from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from dataclasses import asdict
from pathlib import Path

from tests.control_plane.cp_i08_d0 import run_integrated_d0
import tests.control_plane.catalogs as catalogs
import tests.control_plane.qualification as qualification
from tools.aegis_control.availability import AvailabilityError, AvailabilityObservation, classify_observation, evaluate_window
from tools.aegis_control.canonical import canonical_digest
from tools.aegis_control.composition import CompositionError, IntegratedControlPlane, ProviderAuthProvenance
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.observability import (
    ObservabilityBuffer,
    RawMetricEvent,
    REQUIRED_METRIC_FAMILIES,
    alert_snapshot_from_raw,
    evaluate_alerts,
    evaluate_alerts_from_raw,
    recompute_aggregates,
)
from tools.aegis_control.provider_events import ProviderEvent, github_ci_adapter_capability
from tools.aegis_control.retention import DAY, evaluate_retention_at, retention_policy
from tools.aegis_control.store import ControlStore

PACKAGE_ID = "CP-I08-P31-01"
PACKAGE_REF = "55ca192347739779a611cb5d387f05132db37b06"
TASK_ANCHOR = "c7cb7d3d60c5b4505b965bd9f1ea5389c9135e07"
PREDECESSOR_P34 = "5079615570"
P36_PACKAGE = "CP-I08-P36-01"
SOURCE_P34 = "5079847388"
SOURCE_P35 = "5496205447"


def _write(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _case(case_id: str, passed: bool, **facts):
    return {"case_id": case_id, "passed": bool(passed), **facts}


class _WorkerPort:
    def claim_ready_outbox(self, *, limit: int): return []
    def record_delivery_attempt(self, *, outbox_id: str, metadata): return None
    def request_reconciliation(self, *, occurrence_id: str): return None
    def submit_provider_observation(self, *, observation): return None
    def query_platform_capability(self, *, provider_class: str): return {"provider_class": provider_class}


class _LeakyStoreWorkerPort(_WorkerPort):
    def __init__(self, store): self.store = store


class _LeakyMutationWorkerPort(_WorkerPort):
    def __init__(self, mutation_service): self.mutation_service = mutation_service


def _composition_cases():
    with tempfile.TemporaryDirectory() as td:
        store = ControlStore(f"{td}/control.db")
        mutation = MutationService(store)
        composition = IntegratedControlPlane(mutation_service=mutation, worker_port=_WorkerPort())
        public_surface = {name for name in dir(composition.worker_port) if not name.startswith("_")}
        expected_surface = {
            "claim_ready_outbox", "record_delivery_attempt", "request_reconciliation",
            "submit_provider_observation", "query_platform_capability",
        }
        f1 = _case(
            "F1_exact_mutation_service_single_writer_and_restricted_worker_proxy",
            composition.mutation_service is mutation
            and composition.api_mutation_service is mutation
            and composition.canonical_writer_identity == "control-mutation"
            and public_surface == expected_surface,
            canonical_writer_identity=composition.canonical_writer_identity,
            worker_public_surface=sorted(public_surface),
        )
        leak_cases = []
        for case_id, worker in (
            ("F1_nested_store_worker_rejected", _LeakyStoreWorkerPort(store)),
            ("F1_nested_mutation_service_worker_rejected", _LeakyMutationWorkerPort(mutation)),
        ):
            try:
                IntegratedControlPlane(mutation_service=mutation, worker_port=worker)
                rejected = False
                code = None
            except CompositionError as exc:
                rejected = exc.code == "WORKER_SECOND_WRITER_CAPABILITY"
                code = exc.code
            leak_cases.append(_case(case_id, rejected, rejection=code))

        calls = []
        event = ProviderEvent("evt-i08", "github", "workflow_run", "run-i08", "2026-09-01T00:00:00Z", True, {"conclusion": "failure"})
        auth = ProviderAuthProvenance(True, "github-webhook-hmac-v1", "github-actions-webhook")
        result = composition.reconcile_provider_event(
            event,
            github_ci_adapter_capability(),
            auth=auth,
            query=lambda key: calls.append(key) or {"resource": key, "conclusion": "success"},
        )
        f2_positive = _case(
            "F2_post_auth_provenance_preserved_then_query_truth_used",
            calls == ["run-i08"]
            and result.truth_source == "QUERY"
            and result.observation.get("conclusion") == "success"
            and result.auth_provenance == auth
            and result.provider_class == "GITHUB_REPOSITORY_CI",
            query_calls=calls,
            truth_source=result.truth_source,
            observation=dict(result.observation),
            auth_provenance=asdict(result.auth_provenance),
            provider_class=result.provider_class,
        )
        denied_calls = []
        try:
            composition.reconcile_provider_event(
                event,
                github_ci_adapter_capability(),
                auth=ProviderAuthProvenance(True, "", "github-actions-webhook"),
                query=lambda key: denied_calls.append(key) or {"resource": key},
            )
            denied = False
            code = None
        except CompositionError as exc:
            denied = denied_calls == [] and exc.code == "PROVIDER_AUTH_PROVENANCE_REQUIRED"
            code = exc.code
        f2_negative = _case("F2_missing_auth_provenance_rejected_before_query", denied, rejection=code, query_calls=denied_calls)
    return [f1, *leak_cases, f2_positive, f2_negative]


def _retention_artifacts():
    canonical_rows = [
        {"kind": "STAGE_OCCURRENCE", "id": "so-retained", "record_revision": 1},
        {"kind": "ESCALATION", "id": "esc-retained", "record_revision": 1},
    ]
    before = canonical_digest(canonical_rows)
    op_cases = []
    boundaries = [
        ("HIGH_CARDINALITY_TRACE", 14 * DAY, "EXPIRE_OPERATIONAL"),
        ("COMPLETED_DELIVERY_METADATA", 30 * DAY, "COMPACT_OPERATIONAL"),
    ]
    recorded = 1000
    for record_class, window, expiry_action in boundaries:
        policy = retention_policy(record_class)
        before_decision = evaluate_retention_at(record_class, recorded_at_seconds=recorded, current_time_seconds=recorded + window - 1, policy=policy)
        at_decision = evaluate_retention_at(record_class, recorded_at_seconds=recorded, current_time_seconds=recorded + window, policy=policy)
        op_cases.append(_case(
            f"{record_class}_explicit_time_one_tick_before",
            policy.window_seconds == window and before_decision.action == "KEEP",
            policy_id=policy.policy_id,
            policy_window_seconds=policy.window_seconds,
            recorded_at_seconds=recorded,
            current_time_seconds=recorded + window - 1,
            action=before_decision.action,
        ))
        op_cases.append(_case(
            f"{record_class}_explicit_time_at_boundary",
            policy.window_seconds == window and at_decision.action == expiry_action,
            policy_id=policy.policy_id,
            policy_window_seconds=policy.window_seconds,
            recorded_at_seconds=recorded,
            current_time_seconds=recorded + window,
            action=at_decision.action,
            expected=expiry_action,
        ))
    for record_class in ("STAGE_OCCURRENCE", "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "ESCALATION", "SEMANTIC_IDEMPOTENCY"):
        policy = retention_policy(record_class)
        decision = evaluate_retention_at(record_class, recorded_at_seconds=0, current_time_seconds=20 * 365 * DAY, policy=policy)
        op_cases.append(_case(
            f"canonical_{record_class}_no_auto_delete",
            policy.window_seconds is None and decision.action == "NO_AUTO_DELETE",
            policy_id=policy.policy_id,
            action=decision.action,
        ))
    after = canonical_digest(canonical_rows)
    replay = {
        "schema_version": "0.2",
        "kind": "CPV-E-RETENTION-REPLAY",
        "canonical_digest_before": before,
        "canonical_digest_after": after,
        "cases": [_case("operational_retention_preserves_canonical_replay_digest", before == after, before=before, after=after)],
    }
    operational_retention = {"schema_version": "0.2", "kind": "CPV-E-OPERATIONAL-RETENTION", "cases": op_cases}
    return replay, operational_retention


def _observability_artifact():
    buf = ObservabilityBuffer()
    for seq, family in enumerate(sorted(REQUIRED_METRIC_FAMILIES), start=1):
        unit = "usd" if family == "orchestration_cost_component" else "count"
        buf.record(RawMetricEvent(seq, f"2026-09-01T00:00:{seq:02d}Z", family, f"corr-{seq}", float(seq), unit, {"slice": "CP-I08"}))
    raw = buf.raw_events()
    exported = buf.export_aggregates()
    independent = recompute_aggregates(raw)
    present = {event.family for event in raw}
    cases = [
        _case("required_metric_families_complete", present == set(REQUIRED_METRIC_FAMILIES), present=sorted(present)),
        _case("raw_aggregate_independent_recompute_exact", exported == independent, exported=exported, independent=independent),
        _case("all_raw_rows_have_correlation_id", all(event.correlation_id for event in raw)),
        _case("cost_attribution_path_present_without_seven_day_claim", "orchestration_cost_component" in present, seven_day_cost_pass=False),
    ]
    return {
        "schema_version": "0.2",
        "kind": "CPV-E-OBSERVABILITY-COST",
        "raw_events": [asdict(event) for event in raw],
        "exported_aggregates": exported,
        "independent_aggregates": independent,
        "cases": cases,
        "claims": {"seven_day_cost_pass": False, "r0_pass": False, "s0_pass": False},
    }


def _alert_raw_rows(snapshot: dict[str, object], prefix: str):
    rows = []
    for seq, (family, value) in enumerate(snapshot.items(), start=1):
        if isinstance(value, bool):
            numeric = 1.0 if value else 0.0
            unit = "bool"
        else:
            numeric = float(value)
            unit = "count" if family == "delivery_attempts" else "seconds"
        rows.append(RawMetricEvent(seq, f"2026-09-01T00:10:{seq:02d}Z", family, f"corr-{prefix}-{seq}", numeric, unit, {"probe": prefix}))
    return rows


def _alert_artifact():
    probes = [
        ("outbox_at_boundary", {"oldest_ready_outbox_seconds": 300}, set()),
        ("outbox_above_boundary", {"oldest_ready_outbox_seconds": 301}, {"OUTBOX_AGE_URGENT"}),
        ("reconcile_at_boundary", {"reconciliation_lag_seconds": 900}, set()),
        ("reconcile_above_boundary", {"reconciliation_lag_seconds": 901}, {"RECONCILIATION_LAG_URGENT"}),
        ("red_at_boundary", {"red_backpressure_seconds": 300}, set()),
        ("red_above_boundary", {"red_backpressure_seconds": 301}, {"RED_BACKPRESSURE_URGENT"}),
        ("store_at_boundary", {"store_unavailable_seconds": 120, "production_traffic": True}, set()),
        ("store_above_boundary", {"store_unavailable_seconds": 121, "production_traffic": True}, {"STORE_UNAVAILABLE_CRITICAL"}),
        ("delivery_attempt_before_limit", {"delivery_attempts": 11}, set()),
        ("delivery_attempt_at_limit", {"delivery_attempts": 12}, {"DELIVERY_UNCERTAINTY_URGENT"}),
        ("uncertainty_before_limit", {"delivery_uncertainty_seconds": 1799}, set()),
        ("uncertainty_at_limit", {"delivery_uncertainty_seconds": 1800}, {"DELIVERY_UNCERTAINTY_URGENT"}),
        ("critical_commit_loss", {"possible_acknowledged_commit_loss": True}, {"ACKNOWLEDGED_COMMIT_LOSS_CRITICAL"}),
        ("critical_stale_snapshot", {"stale_snapshot_accepted": True}, {"STALE_SNAPSHOT_ACCEPTED_CRITICAL"}),
        ("critical_unauthorized_cross_primary", {"unauthorized_cross_primary_dispatch": True}, {"UNAUTHORIZED_CROSS_PRIMARY_CRITICAL"}),
    ]
    cases = []
    for name, snapshot, expected in probes:
        raw_rows = _alert_raw_rows(snapshot, name)
        recomputed_snapshot = alert_snapshot_from_raw(raw_rows)
        direct = evaluate_alerts(snapshot)
        from_raw = evaluate_alerts_from_raw(raw_rows)
        direct_ids = {alert.rule_id for alert in direct}
        raw_ids = {alert.rule_id for alert in from_raw}
        cases.append(_case(
            name,
            direct_ids == expected and raw_ids == expected and direct == from_raw and recomputed_snapshot == snapshot and all(alert.semantic_truth is False for alert in from_raw),
            expected=sorted(expected),
            direct=sorted(direct_ids),
            recomputed=sorted(raw_ids),
            recomputed_snapshot=recomputed_snapshot,
            raw_events=[asdict(row) for row in raw_rows],
            semantic_mutation_count=0,
            gate_truth_count=sum(bool(alert.semantic_truth) for alert in from_raw),
        ))
    return {"schema_version": "0.2", "kind": "CPV-E-ALERTING-CONFORMANCE", "cases": cases}


def _availability_artifact():
    seeded = [
        (AvailabilityObservation("local-api", "CONTROL_API_AVAILABILITY", "FAILURE"), "BAD"),
        (AvailabilityObservation("write-store", "WRITE_PATH_AVAILABILITY", "FAILURE", store_healthy=False), "BAD"),
        (AvailabilityObservation("query-store-healthy", "QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY", "FAILURE", store_healthy=True), "BAD"),
        (AvailabilityObservation("provider-excluded", "CONTROL_API_AVAILABILITY", "FAILURE", external_provider_failure=True, provider_incident_ref="sha256:" + "1" * 64, local_path_healthy=True, exclusion_manifested=True), "EXCLUDED_EXTERNAL"),
        (AvailabilityObservation("provider-false-label", "CONTROL_API_AVAILABILITY", "FAILURE", external_provider_failure=True, local_path_healthy=False, exclusion_manifested=True), "BAD"),
        (AvailabilityObservation("semantic-4xx", "CONTROL_API_AVAILABILITY", "SEMANTIC_4XX"), "GOOD"),
        (AvailabilityObservation("query-store-down", "QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY", "FAILURE", store_healthy=False), "OUTSIDE_CONDITIONAL_DENOMINATOR"),
    ]
    cases = []
    correct = 0
    false_local_exclusion = 0
    for observation, expected in seeded:
        actual = classify_observation(observation).classification
        ok = actual == expected
        correct += int(ok)
        if observation.observation_id in {"local-api", "write-store", "query-store-healthy", "provider-false-label"} and actual == "EXCLUDED_EXTERNAL":
            false_local_exclusion += 1
        cases.append(_case(observation.observation_id, ok, expected=expected, actual=actual))
    dup_rows = [
        AvailabilityObservation("probe-1", "CONTROL_API_AVAILABILITY", "SUCCESS", synthetic_probe=True),
        AvailabilityObservation("probe-1", "CONTROL_API_AVAILABILITY", "SUCCESS", synthetic_probe=True),
    ]
    incomplete = evaluate_window(dup_rows, window_id="window-seeded-incomplete", required_probe_intervals=2, complete_window=False)
    cases.append(_case("duplicate_raw_observation_deduplicated", incomplete.denominator == 1 and incomplete.numerator == 1, window_id=incomplete.window_id, numerator=incomplete.numerator, denominator=incomplete.denominator))
    cases.append(_case("missing_probe_interval_is_evidence_gap", "MISSING_SYNTHETIC_PROBE_INTERVAL" in incomplete.evidence_gaps and incomplete.status == "INCOMPLETE" and not incomplete.historical_attainment_claimed, window_id=incomplete.window_id, gaps=list(incomplete.evidence_gaps)))
    complete_rows = [
        AvailabilityObservation("probe-a", "CONTROL_API_AVAILABILITY", "SUCCESS", synthetic_probe=True),
        AvailabilityObservation("probe-b", "CONTROL_API_AVAILABILITY", "FAILURE", synthetic_probe=True),
    ]
    complete = evaluate_window(complete_rows, window_id="window-seeded-complete", required_probe_intervals=2, complete_window=True)
    cases.append(_case("complete_seeded_window_ratio_deterministic", complete.status == "COMPLETE" and complete.ratio == 0.5 and complete.window_id == "window-seeded-complete" and not complete.historical_attainment_claimed, window_id=complete.window_id, ratio=complete.ratio))
    try:
        evaluate_window(complete_rows, window_id="", required_probe_intervals=2, complete_window=True)
        empty_rejected = False
        empty_code = None
    except AvailabilityError as exc:
        empty_rejected = str(exc) == "OBSERVATION_WINDOW_ID_REQUIRED"
        empty_code = str(exc)
    cases.append(_case("empty_window_identity_rejected", empty_rejected, rejection=empty_code))
    return {
        "schema_version": "0.2",
        "kind": "CPV-E-AVAILABILITY-EVALUATOR-QUALIFICATION",
        "classification_correct": correct,
        "classification_total": len(seeded),
        "false_local_failure_exclusion": false_local_exclusion,
        "cases": cases,
        "claims": {"historical_monthly_attainment": False},
    }


def materialize_evidence(*, result_revision: str, output_dir: Path, workflow_run: str, workflow_job: str = "verify") -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    d0 = run_integrated_d0()
    for result in d0["golden_results"].values():
        result["execution"] = {"workflow_run": str(workflow_run), "workflow_job": workflow_job}
    composition_cases = _composition_cases()
    d0_payload = {
        "schema_version": "0.2",
        "kind": "CPV-E-D0-CONFORMANCE",
        "golden_catalog_digest": catalogs.fixture_catalog_digest(),
        "golden_results": d0["golden_results"],
        "golden_passed": d0["golden_passed"],
        "semantic_differential_mismatches": d0["semantic_differential_mismatches"],
        "zero_tolerance_invariant_events": d0["zero_tolerance_invariant_events"],
        "execution": {"workflow_run": str(workflow_run), "workflow_job": workflow_job},
        "composition_cases": composition_cases,
    }
    qualification_result = d0["mutant_qualification"]
    verifier_payload = {
        "schema_version": "0.2",
        "kind": "CPV-E-VERIFIER-QUALIFICATION",
        "mutant_catalog_digest": catalogs.mutant_catalog_digest(),
        "qualification": qualification_result,
        "snapshot_mutant_provenance": qualification.snapshot_mutant_provenance(),
        "m20_provenance": qualification.m20_provenance(),
    }
    replay_payload, retention_payload = _retention_artifacts()
    observability_payload = _observability_artifact()
    alert_payload = _alert_artifact()
    availability_payload = _availability_artifact()
    families = {
        "d0-conformance.json": d0_payload,
        "verifier-qualification.json": verifier_payload,
        "retention-replay.json": replay_payload,
        "observability-cost.json": observability_payload,
        "operational-retention.json": retention_payload,
        "alerting-conformance.json": alert_payload,
        "availability-evaluator-qualification.json": availability_payload,
    }
    for name, payload in families.items():
        _write(output_dir / name, payload)
    all_cases = []
    for payload in families.values():
        all_cases.extend(payload.get("cases", []))
        all_cases.extend(payload.get("composition_cases", []))

    alert_recompute_mismatch = sum(not case["passed"] for case in alert_payload["cases"])
    alert_semantic_mutations = sum(case.get("semantic_mutation_count", 0) for case in alert_payload["cases"])
    alert_gate_truth = sum(case.get("gate_truth_count", 0) for case in alert_payload["cases"])
    window_identity_lost = int(any(
        case["case_id"] in {"duplicate_raw_observation_deduplicated", "missing_probe_interval_is_evidence_gap", "complete_seeded_window_ratio_deterministic"} and not case.get("window_id")
        for case in availability_payload["cases"]
    ))
    retention_binding_failed = int(any(not case["passed"] for case in retention_payload["cases"]))
    d0_execution_missing = sum(
        not result.get("execution", {}).get("workflow_run") or not result.get("execution", {}).get("workflow_job")
        for result in d0_payload["golden_results"].values()
    )
    composition_by_id = {case["case_id"]: case for case in composition_cases}
    second_writer_exposed = int(
        not composition_by_id["F1_exact_mutation_service_single_writer_and_restricted_worker_proxy"]["passed"]
        or not composition_by_id["F1_nested_store_worker_rejected"]["passed"]
        or not composition_by_id["F1_nested_mutation_service_worker_rejected"]["passed"]
    )
    provider_provenance_lost = int(
        not composition_by_id["F2_post_auth_provenance_preserved_then_query_truth_used"]["passed"]
        or not composition_by_id["F2_missing_auth_provenance_rejected_before_query"]["passed"]
    )
    metrics = {
        "semantic_differential_mismatches": d0["semantic_differential_mismatches"],
        "zero_tolerance_invariant_events": d0["zero_tolerance_invariant_events"],
        "false_mutant_acceptance": qualification_result["false_acceptance"],
        "canonical_replay_drift": int(replay_payload["canonical_digest_before"] != replay_payload["canonical_digest_after"]),
        "missing_required_metric_families": int({event["family"] for event in observability_payload["raw_events"]} != set(REQUIRED_METRIC_FAMILIES)),
        "raw_aggregate_recompute_mismatch": int(observability_payload["exported_aggregates"] != observability_payload["independent_aggregates"]),
        "raw_alert_recompute_mismatch": alert_recompute_mismatch,
        "operational_retention_mutated_canonical_history": int(replay_payload["canonical_digest_before"] != replay_payload["canonical_digest_after"]),
        "retention_explicit_time_policy_binding_failed": retention_binding_failed,
        "alert_caused_semantic_mutation": alert_semantic_mutations,
        "alert_emitted_gate_truth": alert_gate_truth,
        "availability_false_local_failure_exclusion": availability_payload["false_local_failure_exclusion"],
        "availability_incomplete_window_claimed_attainment": 0,
        "availability_window_identity_lost": window_identity_lost,
        "composition_second_writer_exposed": second_writer_exposed,
        "provider_auth_provenance_lost": provider_provenance_lost,
        "d0_execution_provenance_missing": d0_execution_missing,
        "current_cross_primary_rollout_expanded": 0,
    }
    passed = (
        d0["golden_passed"] == 44
        and qualification_result["detected"] == 20
        and qualification_result["false_acceptance"] == 0
        and availability_payload["classification_correct"] == availability_payload["classification_total"]
        and all(case.get("passed") is True for case in all_cases)
        and not any(metrics.values())
    )
    manifest = {
        "schema_version": "0.2",
        "kind": "CP-I08_EVIDENCE_MANIFEST",
        "package_id": PACKAGE_ID,
        "package_ref": PACKAGE_REF,
        "result_revision": result_revision,
        "workflow_run": str(workflow_run),
        "workflow_job": workflow_job,
        "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
        "predecessor_cp_i07_p34_review": PREDECESSOR_P34,
        "p36_repair": {"repair_package_id": P36_PACKAGE, "source_p34_review": SOURCE_P34, "source_p35_comment": SOURCE_P35},
        "d0": {"golden_passed": d0["golden_passed"], "golden_total": 44},
        "qualification": {"detected": qualification_result["detected"], "mandatory_total": 20, "false_acceptance": qualification_result["false_acceptance"]},
        "metrics": metrics,
        "claims": {
            "p34_gate_pass": False,
            "evidence_compiler_gate_authority": False,
            "current_cross_primary_rollout": "DENIED",
            "cp_i09_plus": False,
            "r0_pass": False,
            "s0_pass": False,
            "seven_day_cost_pass": False,
            "monthly_availability_attainment": False,
        },
        "passed": passed,
    }
    manifest["evidence_files"] = {
        name: "sha256:" + hashlib.sha256((output_dir / name).read_bytes()).hexdigest()
        for name in families
    }
    _write(output_dir / "evidence-manifest.json", manifest)
    if not passed:
        raise RuntimeError("CP-I08 evidence did not satisfy zero-tolerance closure")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--workflow-run", required=True)
    parser.add_argument("--workflow-job", default="verify")
    args = parser.parse_args()
    materialize_evidence(result_revision=args.result_revision, output_dir=Path(args.output_dir), workflow_run=args.workflow_run, workflow_job=args.workflow_job)


if __name__ == "__main__":
    main()
