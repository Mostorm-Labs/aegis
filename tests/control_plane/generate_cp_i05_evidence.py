from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any, Mapping

from tests.control_plane.cp_i02_fixtures import (
    expected_state,
    make_request,
    occurrence_record,
    terminal_facts,
)
from tools.aegis_control.dispatch import DispatchRejected, DispatchService
from tools.aegis_control.execution_surface import DeterministicExecutionSurface, classify_resume
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.recovery import (
    RecoveryCoordinator,
    delivery_is_uncertain,
    dispatch_retry_delay_seconds,
    reconciliation_policy,
)
from tools.aegis_control.store import ControlStore


PACKAGE_ID = "CP-I05-P31-01"
TASK_ANCHOR = "a3fd350c350bec9220a1c6e283de88c14dfbcd2a"
SOURCE_CP_I04_P34_COMMENT = "5486917398"

AUTHORITY_REFS = {
    "product": "c628bdc15fdd3d32511a04b6f09055413f2786c3",
    "modeling": "f29c4da3698038e0174e4380707fa618b03c40b2",
    "architecture": "e657f0e74771184b98f8c8e6f8a8581e4858c82d",
    "verification": "db83168e4086e47a7f431acf289006e4f25b8ffd",
}

RESULT_REF = {
    "object_type": "RESULT",
    "id": "result_cp_i05_evidence",
    "ref": "github:artifact:cp-i05-evidence-result",
    "identity": {"scheme": "sha256", "value": "sha256:" + "5" * 64},
}

ZERO_METRICS = {
    "dispatch_before_commit": 0,
    "worker_direct_canonical_writes": 0,
    "semantic_occurrence_amplification_from_duplicate_transport": 0,
    "duplicate_terminal_revision": 0,
    "age_only_terminalization": 0,
    "unreviewable_result_accepted_as_complete": 0,
    "valid_descendant_resume_replayed_completed_work": 0,
    "diverged_resume_accepted": 0,
    "unauthorized_cross_primary_provider_request": 0,
}


def _write_json(path: Path, payload: Mapping[str, Any]) -> str:
    data = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.write_bytes(data)
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _new_store(tmp: str, name: str) -> ControlStore:
    return ControlStore(str(Path(tmp) / f"{name}.db"))


def _schedule(store: ControlStore, *, occurrence_id: str, lane_id: str, request_id: str) -> tuple[MutationService, str]:
    mutation = MutationService(store)
    result = mutation.apply(
        make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            request_id,
            lane_id,
            {"occurrence": occurrence_record(occurrence_id, lane_id)},
        )
    )
    return mutation, result["outbox_ids"][0]


def _progress(
    store: ControlStore,
    mutation: MutationService,
    *,
    occurrence_id: str,
    lane_id: str,
    request_id: str,
    navigation: Mapping[str, Any],
) -> None:
    current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
    assert current is not None
    mutation.apply(
        make_request(
            "RECORD_EXECUTION_PROGRESS",
            request_id,
            lane_id,
            {
                "occurrence_id": occurrence_id,
                "recorded_at": "2026-09-01T02:30:00Z",
                "execution_navigation": dict(navigation),
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        )
    )


def _terminate(
    store: ControlStore,
    mutation: MutationService,
    *,
    occurrence_id: str,
    lane_id: str,
    request_id: str,
    produced_refs: list[Mapping[str, Any]],
) -> Mapping[str, Any]:
    current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
    assert current is not None
    terminal = terminal_facts()
    terminal["produced_refs"] = list(produced_refs)
    return mutation.apply(
        make_request(
            "TERMINATE_STAGE_OCCURRENCE",
            request_id,
            lane_id,
            {
                "occurrence_id": occurrence_id,
                "recorded_at": "2026-09-01T02:31:00Z",
                "terminal": terminal,
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        )
    )


def _dispatch_fault_matrix() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as tmp:
        # Committed outbox is the only dispatch input; delivery metadata stays non-canonical.
        store = _new_store(tmp, "committed")
        _, outbox_id = _schedule(
            store,
            occurrence_id="so_ev_committed",
            lane_id="lane_ev_committed",
            request_id="req_ev_committed",
        )
        surface = DeterministicExecutionSurface()
        service = DispatchService(store, surface)
        before = dict(store.snapshot_counts())
        receipt = service.dispatch(outbox_id, dispatch_authorized=True, attempted_at="2026-09-01T02:32:00Z")
        after = dict(store.snapshot_counts())
        latest = store.read_latest("STAGE_OCCURRENCE", "so_ev_committed")
        delivery = store.read_delivery_state(outbox_id)
        passed = bool(
            receipt.acknowledged
            and before == after
            and latest is not None
            and latest.record["state"] == "OPEN"
            and latest.record["record_revision"] == 1
            and delivery is not None
            and delivery["provider_correlation_id"] == receipt.correlation_id
        )
        cases.append({
            "case": "committed_outbox_dispatch",
            "pass": passed,
            "outbox_id": outbox_id,
            "canonical_before": before,
            "canonical_after": after,
            "provider_correlation_id": receipt.correlation_id,
            "occurrence_state": latest.record["state"] if latest else None,
        })

        # At-least-once delivery preserves one semantic occurrence/execution identity.
        store = _new_store(tmp, "duplicate")
        _, outbox_id = _schedule(
            store,
            occurrence_id="so_ev_duplicate",
            lane_id="lane_ev_duplicate",
            request_id="req_ev_duplicate",
        )
        surface = DeterministicExecutionSurface()
        service = DispatchService(store, surface)
        first = service.dispatch(outbox_id, dispatch_authorized=True, attempted_at="2026-09-01T02:33:00Z")
        second = service.dispatch(outbox_id, dispatch_authorized=True, attempted_at="2026-09-01T02:33:01Z")
        revisions = store.read_revisions("STAGE_OCCURRENCE", "so_ev_duplicate")
        passed = first.correlation_id == second.correlation_id and surface.unique_execution_count == 1 and len(revisions) == 1
        cases.append({
            "case": "duplicate_transport_same_occurrence",
            "pass": passed,
            "first_correlation_id": first.correlation_id,
            "second_correlation_id": second.correlation_id,
            "provider_requests": surface.provider_request_count,
            "unique_execution_count": surface.unique_execution_count,
            "semantic_occurrence_revisions": len(revisions),
        })

        # A non-existent/transient outbox identity cannot dispatch.
        store = _new_store(tmp, "missing")
        surface = DeterministicExecutionSurface()
        service = DispatchService(store, surface)
        code = None
        try:
            service.dispatch("out_missing", dispatch_authorized=True, attempted_at="2026-09-01T02:34:00Z")
        except DispatchRejected as exc:
            code = exc.code
        passed = code == "OUTBOX_NOT_FOUND" and surface.provider_request_count == 0
        cases.append({
            "case": "missing_outbox_no_dispatch",
            "pass": passed,
            "rejection_code": code,
            "provider_requests": surface.provider_request_count,
        })

        # Current rollout/policy denial is checked before provider invocation.
        store = _new_store(tmp, "unauthorized")
        _, outbox_id = _schedule(
            store,
            occurrence_id="so_ev_unauthorized",
            lane_id="lane_ev_unauthorized",
            request_id="req_ev_unauthorized",
        )
        surface = DeterministicExecutionSurface()
        service = DispatchService(store, surface)
        before = dict(store.snapshot_counts())
        code = None
        try:
            service.dispatch(outbox_id, dispatch_authorized=False, attempted_at="2026-09-01T02:35:00Z")
        except DispatchRejected as exc:
            code = exc.code
        after = dict(store.snapshot_counts())
        passed = code == "DISPATCH_NOT_AUTHORIZED" and surface.provider_request_count == 0 and before == after
        cases.append({
            "case": "unauthorized_dispatch_no_provider_request",
            "pass": passed,
            "rejection_code": code,
            "provider_requests": surface.provider_request_count,
            "canonical_before": before,
            "canonical_after": after,
        })

        # Provider acknowledgement is transport state only, not semantic completion.
        store = _new_store(tmp, "ack")
        _, outbox_id = _schedule(
            store,
            occurrence_id="so_ev_ack",
            lane_id="lane_ev_ack",
            request_id="req_ev_ack",
        )
        surface = DeterministicExecutionSurface()
        receipt = DispatchService(store, surface).dispatch(
            outbox_id, dispatch_authorized=True, attempted_at="2026-09-01T02:36:00Z"
        )
        latest = store.read_latest("STAGE_OCCURRENCE", "so_ev_ack")
        passed = bool(receipt.acknowledged and latest is not None and latest.record["state"] == "OPEN" and latest.record["record_revision"] == 1)
        cases.append({
            "case": "provider_ack_not_completion",
            "pass": passed,
            "acknowledged": receipt.acknowledged,
            "occurrence_state": latest.record["state"] if latest else None,
            "occurrence_revision": latest.record["record_revision"] if latest else None,
        })

        # Callback loss is recovered by query/correlation without canonical mutation.
        store = _new_store(tmp, "callback")
        _, outbox_id = _schedule(
            store,
            occurrence_id="so_ev_callback",
            lane_id="lane_ev_callback",
            request_id="req_ev_callback",
        )
        surface = DeterministicExecutionSurface()
        receipt = DispatchService(store, surface).dispatch(
            outbox_id, dispatch_authorized=True, attempted_at="2026-09-01T02:37:00Z"
        )
        surface.set_observation(
            receipt.correlation_id,
            state="MATERIALIZED",
            execution_revision="exec-evidence-1",
            materialized_ref=RESULT_REF,
            reviewer_accessible=True,
        )
        before = dict(store.snapshot_counts())
        observation = RecoveryCoordinator(store, surface).reconcile_outbox(
            outbox_id, observed_at="2026-09-01T02:38:00Z"
        )
        after = dict(store.snapshot_counts())
        latest = store.read_latest("STAGE_OCCURRENCE", "so_ev_callback")
        passed = bool(
            observation.state == "MATERIALIZED"
            and observation.materialized_ref == RESULT_REF
            and observation.reviewer_accessible
            and surface.query_count == 1
            and before == after
            and latest is not None
            and latest.record["state"] == "OPEN"
        )
        cases.append({
            "case": "callback_loss_query_recovery",
            "pass": passed,
            "provider_query_count": surface.query_count,
            "provider_state": observation.state,
            "reviewer_accessible": observation.reviewer_accessible,
            "canonical_before": before,
            "canonical_after": after,
            "occurrence_state": latest.record["state"] if latest else None,
        })

        # Review-ready completion fails closed when exact result materialization is absent.
        store = _new_store(tmp, "materialization_required")
        mutation, _ = _schedule(
            store,
            occurrence_id="so_ev_mat_required",
            lane_id="lane_ev_mat_required",
            request_id="req_ev_mat_required_schedule",
        )
        _progress(
            store,
            mutation,
            occurrence_id="so_ev_mat_required",
            lane_id="lane_ev_mat_required",
            request_id="req_ev_mat_required_progress",
            navigation={
                "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
                "classification": "EXACT_CURSOR",
                "accepted_revision": "exec-evidence-2",
                "completed_through": ["implementation"],
                "next_action": "review",
                "materialization_required": True,
                "result_ref": None,
                "reviewer_accessible": False,
            },
        )
        before = dict(store.snapshot_counts())
        code = None
        try:
            _terminate(
                store,
                mutation,
                occurrence_id="so_ev_mat_required",
                lane_id="lane_ev_mat_required",
                request_id="req_ev_mat_required_terminal",
                produced_refs=[],
            )
        except MutationRejected as exc:
            code = exc.code
        after = dict(store.snapshot_counts())
        latest = store.read_latest("STAGE_OCCURRENCE", "so_ev_mat_required")
        passed = bool(code == "RESULT_MATERIALIZATION_REQUIRED" and before == after and latest is not None and latest.record["state"] == "OPEN")
        cases.append({
            "case": "exact_result_materialization_required",
            "pass": passed,
            "rejection_code": code,
            "canonical_before": before,
            "canonical_after": after,
            "occurrence_state": latest.record["state"] if latest else None,
        })

        # An exact reviewer-accessible RESULT bound into produced_refs permits completion.
        store = _new_store(tmp, "materialization_bound")
        mutation, _ = _schedule(
            store,
            occurrence_id="so_ev_mat_bound",
            lane_id="lane_ev_mat_bound",
            request_id="req_ev_mat_bound_schedule",
        )
        _progress(
            store,
            mutation,
            occurrence_id="so_ev_mat_bound",
            lane_id="lane_ev_mat_bound",
            request_id="req_ev_mat_bound_progress",
            navigation={
                "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
                "classification": "EXACT_CURSOR",
                "accepted_revision": "exec-evidence-3",
                "completed_through": ["implementation"],
                "next_action": "review",
                "materialization_required": True,
                "result_ref": RESULT_REF,
                "reviewer_accessible": True,
            },
        )
        result = _terminate(
            store,
            mutation,
            occurrence_id="so_ev_mat_bound",
            lane_id="lane_ev_mat_bound",
            request_id="req_ev_mat_bound_terminal",
            produced_refs=[RESULT_REF],
        )
        latest = store.read_latest("STAGE_OCCURRENCE", "so_ev_mat_bound")
        terminal_refs = latest.record["terminal"]["produced_refs"] if latest else []
        passed = bool(result["status"] == "APPLIED" and latest is not None and latest.record["state"] == "TERMINAL" and terminal_refs == [RESULT_REF])
        cases.append({
            "case": "exact_result_materialization_bound",
            "pass": passed,
            "mutation_status": result["status"],
            "occurrence_state": latest.record["state"] if latest else None,
            "produced_refs": terminal_refs,
        })

    if not all(case["pass"] for case in cases):
        raise AssertionError("CP-I05 dispatch/materialization evidence contains a failed case")
    return {
        "evidence_family": "CPV-E-DISPATCH-FAULT-MATRIX",
        "cases": cases,
    }


def _resume_corpus() -> dict[str, Any]:
    scenarios = [
        (
            "EXACT_CURSOR",
            classify_resume(
                task_anchor_revision="A",
                resume_cursor={"revision": "C", "completed_through": ["P32.1"], "next_action": "P32.2"},
                observed_revision="C",
                is_ancestor=lambda a, b: a == b,
            ),
        ),
        (
            "DESCENDANT_CURSOR",
            classify_resume(
                task_anchor_revision="A",
                resume_cursor={"revision": "C", "completed_through": ["P32.1"], "next_action": "reconcile delta"},
                observed_revision="D",
                is_ancestor=lambda a, b: (a, b) in {("C", "D"), ("A", "D")},
            ),
        ),
        (
            "ANCHOR_DESCENDANT_WITHOUT_CURSOR",
            classify_resume(
                task_anchor_revision="A",
                resume_cursor=None,
                observed_revision="D",
                is_ancestor=lambda a, b: (a, b) == ("A", "D"),
            ),
        ),
        (
            "DIVERGED",
            classify_resume(
                task_anchor_revision="A",
                resume_cursor={"revision": "C", "completed_through": [], "next_action": "continue"},
                observed_revision="X",
                is_ancestor=lambda a, b: False,
            ),
        ),
    ]
    cases = [
        {
            "state": result.state,
            "expected_state": expected,
            "pass": result.state == expected,
            "accepted_revision": result.accepted_revision,
            "completed_through": list(result.completed_through),
            "next_action": result.next_action,
            "replay_completed_work": result.replay_completed_work,
            "blocker": result.blocker,
        }
        for expected, result in scenarios
    ]
    expected_states = {"EXACT_CURSOR", "DESCENDANT_CURSOR", "ANCHOR_DESCENDANT_WITHOUT_CURSOR", "DIVERGED"}
    observed_states = {case["state"] for case in cases}
    diverged = next(case for case in cases if case["state"] == "DIVERGED")
    if observed_states != expected_states or any(case["replay_completed_work"] for case in cases) or diverged["blocker"] != "BLOCKED_EXECUTION_DIVERGENCE":
        raise AssertionError("CP-I05 resume corpus does not satisfy the exact P33 contract")
    return {
        "evidence_family": "CPV-E-RESUME-CORPUS",
        "cases": cases,
    }


def _delivery_policy() -> dict[str, Any]:
    retry_delays = [dispatch_retry_delay_seconds(i) for i in range(1, 9)]
    boundary_cases = {
        "before_boundary": delivery_is_uncertain(attempt_count=11, elapsed_seconds=1799),
        "attempt_12": delivery_is_uncertain(attempt_count=12, elapsed_seconds=1),
        "minute_30": delivery_is_uncertain(attempt_count=1, elapsed_seconds=1800),
    }
    if retry_delays != [1, 2, 4, 8, 16, 30, 60, 300] or boundary_cases != {
        "before_boundary": False,
        "attempt_12": True,
        "minute_30": True,
    }:
        raise AssertionError("CP-I05 delivery policy drifted from P18")
    return {
        "evidence_family": "CPV-E-DELIVERY-POLICY",
        "retry_delays_seconds": retry_delays,
        "uncertainty_rule": "attempt_count >= 12 OR elapsed_seconds >= 1800",
        "boundary_cases": boundary_cases,
        "semantic_replacement_occurrences": 0,
    }


def _reconciliation_policy_evidence() -> dict[str, Any]:
    ages = [0, 299, 300, 1799, 1800, 7199, 7200]
    cases = []
    for age in ages:
        policy = reconciliation_policy(age)
        cases.append({
            "age_seconds": age,
            "interval_seconds": policy.interval_seconds,
            "operator_alert": policy.operator_alert,
            "semantic_terminalization": policy.semantic_terminalization,
        })
    expected = [
        [0, 30, False],
        [299, 30, False],
        [300, 120, False],
        [1799, 120, False],
        [1800, 300, False],
        [7199, 300, False],
        [7200, 900, True],
    ]
    observed = [[c["age_seconds"], c["interval_seconds"], c["operator_alert"]] for c in cases]
    if observed != expected or any(c["semantic_terminalization"] for c in cases):
        raise AssertionError("CP-I05 reconciliation policy drifted from P18")
    return {
        "evidence_family": "CPV-E-RECONCILIATION-POLICY",
        "cases": cases,
    }


def build_evidence_bundle(*, result_revision: str, package_ref: str, output_dir: Path) -> dict[str, Any]:
    if len(result_revision) != 40 or any(ch not in "0123456789abcdef" for ch in result_revision):
        raise ValueError("result_revision must be an exact lowercase 40-hex git revision")
    if package_ref != "d1e76563385bd03747aef2ee396855ec26496679":
        raise ValueError("unexpected CP-I05 package ref")

    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = [
        ("dispatch-fault-matrix.json", "CPV-E-DISPATCH-FAULT-MATRIX", _dispatch_fault_matrix()),
        ("resume-corpus.json", "CPV-E-RESUME-CORPUS", _resume_corpus()),
        ("delivery-policy.json", "CPV-E-DELIVERY-POLICY", _delivery_policy()),
        ("reconciliation-policy.json", "CPV-E-RECONCILIATION-POLICY", _reconciliation_policy_evidence()),
    ]

    evidence_files = []
    for filename, family, payload in payloads:
        digest = _write_json(output_dir / filename, payload)
        evidence_files.append({"family": family, "file": filename, "digest": digest})

    manifest = {
        "schema_version": "aegis-cp-i05-evidence-v1",
        "package_id": PACKAGE_ID,
        "package_ref": package_ref,
        "result_revision": result_revision,
        "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
        "source_cp_i04_p34_comment": SOURCE_CP_I04_P34_COMMENT,
        "authority_refs": AUTHORITY_REFS,
        "evidence_files": evidence_files,
        "metrics": dict(ZERO_METRICS),
        "claims": {
            "p34_gate_pass": False,
            "cp_i06_plus": False,
            "current_cross_primary_rollout": "DENIED",
            "evidence_compiler_gate_authority": False,
        },
    }
    _write_json(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--package-ref", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    manifest = build_evidence_bundle(
        result_revision=args.result_revision,
        package_ref=args.package_ref,
        output_dir=args.output_dir,
    )
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
