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
from tools.aegis_control.availability import AvailabilityObservation, classify_observation, evaluate_window
from tools.aegis_control.canonical import canonical_digest
from tools.aegis_control.composition import CompositionError, IntegratedControlPlane, ProviderAuthProvenance
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.observability import ObservabilityBuffer, RawMetricEvent, REQUIRED_METRIC_FAMILIES, evaluate_alerts, recompute_aggregates
from tools.aegis_control.provider_events import ProviderEvent, github_ci_adapter_capability
from tools.aegis_control.retention import DAY, evaluate_retention
from tools.aegis_control.store import ControlStore

PACKAGE_ID = "CP-I08-P31-01"
PACKAGE_REF = "55ca192347739779a611cb5d387f05132db37b06"
TASK_ANCHOR = "c7cb7d3d60c5b4505b965bd9f1ea5389c9135e07"
PREDECESSOR_P34 = "5079615570"


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


def _composition_cases():
    with tempfile.TemporaryDirectory() as td:
        mutation = MutationService(ControlStore(f"{td}/control.db"))
        composition = IntegratedControlPlane(mutation_service=mutation, worker_port=_WorkerPort())
        f1 = _case("F1_exact_mutation_service_single_writer", composition.mutation_service is mutation and composition.api_mutation_service is mutation and composition.canonical_writer_identity == "control-mutation", canonical_writer_identity=composition.canonical_writer_identity)
        calls = []
        event = ProviderEvent("evt-i08", "github", "workflow_run", "run-i08", "2026-09-01T00:00:00Z", True, {"conclusion": "failure"})
        result = composition.reconcile_provider_event(event, github_ci_adapter_capability(), auth=ProviderAuthProvenance(True, "github-webhook-hmac-v1", "github-actions-webhook"), query=lambda key: calls.append(key) or {"resource": key, "conclusion": "success"})
        f2_positive = _case("F2_post_auth_provenance_preserved_then_query_truth_used", calls == ["run-i08"] and result.truth_source == "QUERY" and result.observation.get("conclusion") == "success", query_calls=calls, truth_source=result.truth_source, observation=dict(result.observation))
        denied_calls = []
        try:
            composition.reconcile_provider_event(event, github_ci_adapter_capability(), auth=ProviderAuthProvenance(True, "", "github-actions-webhook"), query=lambda key: denied_calls.append(key) or {"resource": key})
            denied = False; code = None
        except CompositionError as exc:
            denied = denied_calls == [] and exc.code == "PROVIDER_AUTH_PROVENANCE_REQUIRED"; code = exc.code
        f2_negative = _case("F2_missing_auth_provenance_rejected_before_query", denied, rejection=code, query_calls=denied_calls)
    return [f1, f2_positive, f2_negative]


def _retention_artifacts():
    canonical_rows = [{"kind": "STAGE_OCCURRENCE", "id": "so-retained", "record_revision": 1}, {"kind": "ESCALATION", "id": "esc-retained", "record_revision": 1}]
    before = canonical_digest(canonical_rows)
    operational = [("HIGH_CARDINALITY_TRACE", 14 * DAY - 1, "KEEP"), ("HIGH_CARDINALITY_TRACE", 14 * DAY, "EXPIRE_OPERATIONAL"), ("COMPLETED_DELIVERY_METADATA", 30 * DAY - 1, "KEEP"), ("COMPLETED_DELIVERY_METADATA", 30 * DAY, "COMPACT_OPERATIONAL")]
    op_cases = []
    for cls, age, expected in operational:
        decision = evaluate_retention(cls, age_seconds=age)
        op_cases.append(_case(f"{cls}_{age}", decision.action == expected, record_class=cls, age_seconds=age, action=decision.action, expected=expected))
    for cls in ("STAGE_OCCURRENCE", "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "ESCALATION", "SEMANTIC_IDEMPOTENCY"):
        decision = evaluate_retention(cls, age_seconds=20 * 365 * DAY)
        op_cases.append(_case(f"canonical_{cls}_no_auto_delete", decision.action == "NO_AUTO_DELETE", action=decision.action))
    after = canonical_digest(canonical_rows)
    replay = {"schema_version": "0.2", "kind": "CPV-E-RETENTION-REPLAY", "canonical_digest_before": before, "canonical_digest_after": after, "cases": [_case("operational_retention_preserves_canonical_replay_digest", before == after, before=before, after=after)]}
    operational_retention = {"schema_version": "0.2", "kind": "CPV-E-OPERATIONAL-RETENTION", "cases": op_cases}
    return replay, operational_retention


def _observability_artifact():
    buf = ObservabilityBuffer()
    for seq, family in enumerate(sorted(REQUIRED_METRIC_FAMILIES), start=1):
        unit = "usd" if family == "orchestration_cost_component" else "count"
        buf.record(RawMetricEvent(seq, f"2026-09-01T00:00:{seq:02d}Z", family, f"corr-{seq}", float(seq), unit, {"slice": "CP-I08"}))
    raw = buf.raw_events(); exported = buf.export_aggregates(); independent = recompute_aggregates(raw); present = {event.family for event in raw}
    cases = [_case("required_metric_families_complete", present == set(REQUIRED_METRIC_FAMILIES), present=sorted(present)), _case("raw_aggregate_independent_recompute_exact", exported == independent, exported=exported, independent=independent), _case("all_raw_rows_have_correlation_id", all(event.correlation_id for event in raw)), _case("cost_attribution_path_present_without_seven_day_claim", "orchestration_cost_component" in present, seven_day_cost_pass=False)]
    return {"schema_version": "0.2", "kind": "CPV-E-OBSERVABILITY-COST", "raw_events": [asdict(event) for event in raw], "exported_aggregates": exported, "independent_aggregates": independent, "cases": cases, "claims": {"seven_day_cost_pass": False, "r0_pass": False, "s0_pass": False}}


def _alert_artifact():
    probes = [("outbox_at_boundary", {"oldest_ready_outbox_seconds": 300}, set()), ("outbox_above_boundary", {"oldest_ready_outbox_seconds": 301}, {"OUTBOX_AGE_URGENT"}), ("reconcile_at_boundary", {"reconciliation_lag_seconds": 900}, set()), ("reconcile_above_boundary", {"reconciliation_lag_seconds": 901}, {"RECONCILIATION_LAG_URGENT"}), ("red_at_boundary", {"red_backpressure_seconds": 300}, set()), ("red_above_boundary", {"red_backpressure_seconds": 301}, {"RED_BACKPRESSURE_URGENT"}), ("store_at_boundary", {"store_unavailable_seconds": 120, "production_traffic": True}, set()), ("store_above_boundary", {"store_unavailable_seconds": 121, "production_traffic": True}, {"STORE_UNAVAILABLE_CRITICAL"}), ("delivery_attempt_before_limit", {"delivery_attempts": 11}, set()), ("delivery_attempt_at_limit", {"delivery_attempts": 12}, {"DELIVERY_UNCERTAINTY_URGENT"}), ("uncertainty_before_limit", {"delivery_uncertainty_seconds": 1799}, set()), ("uncertainty_at_limit", {"delivery_uncertainty_seconds": 1800}, {"DELIVERY_UNCERTAINTY_URGENT"}), ("critical_commit_loss", {"possible_acknowledged_commit_loss": True}, {"ACKNOWLEDGED_COMMIT_LOSS_CRITICAL"}), ("critical_stale_snapshot", {"stale_snapshot_accepted": True}, {"STALE_SNAPSHOT_ACCEPTED_CRITICAL"}), ("critical_unauthorized_cross_primary", {"unauthorized_cross_primary_dispatch": True}, {"UNAUTHORIZED_CROSS_PRIMARY_CRITICAL"})]
    cases = []
    for name, snapshot, expected in probes:
        alerts = evaluate_alerts(snapshot); actual = {alert.rule_id for alert in alerts}
        cases.append(_case(name, actual == expected and all(alert.semantic_truth is False for alert in alerts), expected=sorted(expected), actual=sorted(actual)))
    return {"schema_version": "0.2", "kind": "CPV-E-ALERTING-CONFORMANCE", "cases": cases}


def _availability_artifact():
    seeded = [(AvailabilityObservation("local-api", "CONTROL_API_AVAILABILITY", "FAILURE"), "BAD"), (AvailabilityObservation("write-store", "WRITE_PATH_AVAILABILITY", "FAILURE", store_healthy=False), "BAD"), (AvailabilityObservation("query-store-healthy", "QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY", "FAILURE", store_healthy=True), "BAD"), (AvailabilityObservation("provider-excluded", "CONTROL_API_AVAILABILITY", "FAILURE", external_provider_failure=True, provider_incident_ref="sha256:" + "1" * 64, local_path_healthy=True, exclusion_manifested=True), "EXCLUDED_EXTERNAL"), (AvailabilityObservation("provider-false-label", "CONTROL_API_AVAILABILITY", "FAILURE", external_provider_failure=True, local_path_healthy=False, exclusion_manifested=True), "BAD"), (AvailabilityObservation("semantic-4xx", "CONTROL_API_AVAILABILITY", "SEMANTIC_4XX"), "GOOD"), (AvailabilityObservation("query-store-down", "QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY", "FAILURE", store_healthy=False), "OUTSIDE_CONDITIONAL_DENOMINATOR")]
    cases = []; correct = 0; false_local_exclusion = 0
    for observation, expected in seeded:
        actual = classify_observation(observation).classification; ok = actual == expected; correct += int(ok)
        if observation.observation_id in {"local-api", "write-store", "query-store-healthy", "provider-false-label"} and actual == "EXCLUDED_EXTERNAL": false_local_exclusion += 1
        cases.append(_case(observation.observation_id, ok, expected=expected, actual=actual))
    dup_rows = [AvailabilityObservation("probe-1", "CONTROL_API_AVAILABILITY", "SUCCESS", synthetic_probe=True), AvailabilityObservation("probe-1", "CONTROL_API_AVAILABILITY", "SUCCESS", synthetic_probe=True)]
    incomplete = evaluate_window(dup_rows, required_probe_intervals=2, complete_window=False)
    cases.append(_case("duplicate_raw_observation_deduplicated", incomplete.denominator == 1 and incomplete.numerator == 1, numerator=incomplete.numerator, denominator=incomplete.denominator))
    cases.append(_case("missing_probe_interval_is_evidence_gap", "MISSING_SYNTHETIC_PROBE_INTERVAL" in incomplete.evidence_gaps and incomplete.status == "INCOMPLETE" and not incomplete.historical_attainment_claimed, gaps=list(incomplete.evidence_gaps)))
    complete_rows = [AvailabilityObservation("probe-a", "CONTROL_API_AVAILABILITY", "SUCCESS", synthetic_probe=True), AvailabilityObservation("probe-b", "CONTROL_API_AVAILABILITY", "FAILURE", synthetic_probe=True)]
    complete = evaluate_window(complete_rows, required_probe_intervals=2, complete_window=True)
    cases.append(_case("complete_seeded_window_ratio_deterministic", complete.status == "COMPLETE" and complete.ratio == 0.5 and not complete.historical_attainment_claimed, ratio=complete.ratio))
    return {"schema_version": "0.2", "kind": "CPV-E-AVAILABILITY-EVALUATOR-QUALIFICATION", "classification_correct": correct, "classification_total": len(seeded), "false_local_failure_exclusion": false_local_exclusion, "cases": cases, "claims": {"historical_monthly_attainment": False}}


def materialize_evidence(*, result_revision: str, output_dir: Path, workflow_run: str) -> dict:
    output_dir = Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    d0 = run_integrated_d0(); composition_cases = _composition_cases()
    d0_payload = {"schema_version": "0.2", "kind": "CPV-E-D0-CONFORMANCE", "golden_catalog_digest": catalogs.fixture_catalog_digest(), "golden_results": d0["golden_results"], "golden_passed": d0["golden_passed"], "semantic_differential_mismatches": d0["semantic_differential_mismatches"], "zero_tolerance_invariant_events": d0["zero_tolerance_invariant_events"], "composition_cases": composition_cases}
    qualification_result = d0["mutant_qualification"]
    verifier_payload = {"schema_version": "0.2", "kind": "CPV-E-VERIFIER-QUALIFICATION", "mutant_catalog_digest": catalogs.mutant_catalog_digest(), "qualification": qualification_result, "snapshot_mutant_provenance": qualification.snapshot_mutant_provenance(), "m20_provenance": qualification.m20_provenance()}
    replay_payload, retention_payload = _retention_artifacts(); observability_payload = _observability_artifact(); alert_payload = _alert_artifact(); availability_payload = _availability_artifact()
    families = {"d0-conformance.json": d0_payload, "verifier-qualification.json": verifier_payload, "retention-replay.json": replay_payload, "observability-cost.json": observability_payload, "operational-retention.json": retention_payload, "alerting-conformance.json": alert_payload, "availability-evaluator-qualification.json": availability_payload}
    for name, payload in families.items(): _write(output_dir / name, payload)
    all_cases = []
    for payload in families.values(): all_cases.extend(payload.get("cases", [])); all_cases.extend(payload.get("composition_cases", []))
    metrics = {"semantic_differential_mismatches": d0["semantic_differential_mismatches"], "zero_tolerance_invariant_events": d0["zero_tolerance_invariant_events"], "false_mutant_acceptance": qualification_result["false_acceptance"], "canonical_replay_drift": int(replay_payload["canonical_digest_before"] != replay_payload["canonical_digest_after"]), "missing_required_metric_families": int(set(event["family"] for event in observability_payload["raw_events"]) != set(REQUIRED_METRIC_FAMILIES)), "raw_aggregate_recompute_mismatch": int(observability_payload["exported_aggregates"] != observability_payload["independent_aggregates"]), "operational_retention_mutated_canonical_history": int(replay_payload["canonical_digest_before"] != replay_payload["canonical_digest_after"]), "alert_caused_semantic_mutation": int(any(case.get("passed") is not True for case in alert_payload["cases"])), "alert_emitted_gate_truth": 0, "availability_false_local_failure_exclusion": availability_payload["false_local_failure_exclusion"], "availability_incomplete_window_claimed_attainment": 0, "composition_second_writer_exposed": int(not composition_cases[0]["passed"]), "provider_auth_provenance_lost": int(not all(case["passed"] for case in composition_cases[1:])), "current_cross_primary_rollout_expanded": 0}
    passed = d0["golden_passed"] == 44 and qualification_result["detected"] == 20 and qualification_result["false_acceptance"] == 0 and availability_payload["classification_correct"] == availability_payload["classification_total"] and all(case.get("passed") is True for case in all_cases) and not any(metrics.values())
    manifest = {"schema_version": "0.2", "kind": "CP-I08_EVIDENCE_MANIFEST", "package_id": PACKAGE_ID, "package_ref": PACKAGE_REF, "result_revision": result_revision, "workflow_run": str(workflow_run), "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"}, "predecessor_cp_i07_p34_review": PREDECESSOR_P34, "d0": {"golden_passed": d0["golden_passed"], "golden_total": 44}, "qualification": {"detected": qualification_result["detected"], "mandatory_total": 20, "false_acceptance": qualification_result["false_acceptance"]}, "metrics": metrics, "claims": {"p34_gate_pass": False, "evidence_compiler_gate_authority": False, "current_cross_primary_rollout": "DENIED", "cp_i09_plus": False, "r0_pass": False, "s0_pass": False, "seven_day_cost_pass": False, "monthly_availability_attainment": False}, "passed": passed}
    manifest["evidence_files"] = {name: "sha256:" + hashlib.sha256((output_dir / name).read_bytes()).hexdigest() for name in families}
    _write(output_dir / "evidence-manifest.json", manifest)
    if not passed: raise RuntimeError("CP-I08 evidence did not satisfy zero-tolerance closure")
    return manifest


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--result-revision", required=True); parser.add_argument("--output-dir", required=True); parser.add_argument("--workflow-run", required=True); args = parser.parse_args()
    materialize_evidence(result_revision=args.result_revision, output_dir=Path(args.output_dir), workflow_run=args.workflow_run)


if __name__ == "__main__": main()
