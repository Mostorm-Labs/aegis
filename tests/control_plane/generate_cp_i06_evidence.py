from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Mapping

from tests.control_plane.cp_i02_fixtures import (
    escalation_record,
    expected_state,
    make_request,
    occurrence_record,
    terminal_facts,
)
from tools.aegis_control.canonical import canonical_digest
from tools.aegis_control.external_ports import DeterministicExternalAdapter
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.operational import (
    AdmissionController,
    ProviderRateLimitController,
    classify_backpressure,
    manual_fallback_guard,
)
from tools.aegis_control.recovery import (
    backup_control_store,
    reconciliation_policy,
    restore_control_store_backup,
    startup_recovery_plan,
    verify_control_store_integrity,
)
from tools.aegis_control.store import ControlStore, StoreConflict
from tools.aegis_control.trust import TrustFactRequest, TrustResolver


PACKAGE_ID = "CP-I06-P31-01"
PACKAGE_REF = "5683e99f5c144ddddad926afd71ad03b6c85ff91"
TASK_ANCHOR = {
    "revision": "7b3244417c5beba4c75d5eafd471083007fa1843",
    "relation": "ancestor",
}
CP_I05_REVISION = TASK_ANCHOR["revision"]
CP_I05_P34_COMMENT = "5490992992"
CP_I05_EVIDENCE_ARTIFACT_ID = "9790980577"

EVIDENCE_FAMILIES = {
    "human-decision.json": "CPV-E-HUMAN-DECISION",
    "recovery-fault-matrix.json": "CPV-E-RECOVERY-FAULT-MATRIX",
    "backup-restore.json": "CPV-E-BACKUP-RESTORE",
    "rate-limit-control.json": "CPV-E-RATE-LIMIT-CONTROL",
    "derived-operational-state.json": "CPV-E-DERIVED-STATE",
}

ZERO_METRIC_KEYS = {
    "unmaterialized_human_acknowledgement_accepted",
    "semantic_retry_from_restart_or_age",
    "unsafe_manual_duplicate_execution",
    "acknowledged_commit_loss_in_supported_primary_fault_model",
    "repair_scope_expansion_accepted",
    "repair_budget_violation_accepted",
    "repair_lineage_gap_accepted",
    "escalation_history_mutated",
    "conflicting_escalation_resolution_accepted",
    "required_reverification_skipped",
    "control_plane_self_issued_gate_verdict",
    "pause_or_backpressure_semantic_mutation",
    "committed_outbox_dropped_by_backpressure",
    "sustained_rate_limit_breach_without_concurrency_reduction",
    "instant_full_rate_limit_recovery",
    "restore_digest_or_revision_mismatch",
}


def _case(name: str, passed: bool, **facts: Any) -> dict[str, Any]:
    return {"case": name, "passed": bool(passed), **facts}


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _exact_ref(object_type: str, object_id: str, *, scheme: str = "sha256") -> dict[str, Any]:
    value = canonical_digest({"type": object_type, "id": object_id}) if scheme == "sha256" else "draft-v1"
    return {
        "object_type": object_type,
        "id": object_id,
        "ref": f"fixture://{object_type.lower()}/{object_id}",
        "identity": {"scheme": scheme, "value": value},
    }


def _stored_occurrence_ref(stored) -> dict[str, Any]:
    return {
        "object_type": "STAGE_OCCURRENCE",
        "id": stored.record["id"],
        "ref": f"control:STAGE_OCCURRENCE:{stored.record['id']}@{stored.record['record_revision']}",
        "identity": {"scheme": "sha256", "value": stored.digest},
    }


def _internal_ref(stored) -> str:
    return f"STAGE_OCCURRENCE:{stored.record['id']}@{stored.record['record_revision']}#{stored.digest}"


def _terminalize(mutation: MutationService, store: ControlStore, occurrence_id: str, lane_id: str):
    current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
    mutation.apply(make_request(
        "TERMINATE_STAGE_OCCURRENCE",
        f"req_terminal_{occurrence_id}",
        lane_id,
        {
            "occurrence_id": occurrence_id,
            "recorded_at": "2026-09-01T09:05:00Z",
            "terminal": terminal_facts(),
        },
        expected_state(
            target_record_revision=current.record["record_revision"],
            target_record_digest=current.digest,
            work_scope_ref=current.record["work_scope_ref"],
        ),
    ))
    return store.read_latest("STAGE_OCCURRENCE", occurrence_id)


def _seed_terminal_root(mutation: MutationService, store: ControlStore, *, occurrence_id: str, lane_id: str):
    record = occurrence_record(occurrence_id, lane_id)
    mutation.apply(make_request(
        "SCHEDULE_STAGE_OCCURRENCE",
        f"req_schedule_{occurrence_id}",
        lane_id,
        {"occurrence": record},
    ))
    return _terminalize(mutation, store, occurrence_id, lane_id)


def _repair_policy(max_attempts: int = 2) -> dict[str, Any]:
    base = {
        "gate_policy_ref": _exact_ref("CONTRACT", "gate-policy"),
        "control_autonomy": "REVIEW_GUARDED",
        "repair_policy": {
            "allowed_classes": ["IMPLEMENTATION_DEFECT"],
            "max_attempts": max_attempts,
            "require_reverification": True,
            "require_fresh_independent_review": True,
            "escalation_conditions": ["REPAIR_BUDGET_EXHAUSTED"],
        },
    }
    return {**base, "policy_digest": canonical_digest(base)}


def _repair_record(
    occurrence_id: str,
    lane_id: str,
    root_terminal,
    finding_ref: Mapping[str, Any],
    *,
    ordinal: int,
    previous=None,
    max_attempts: int = 2,
    work_scope_ref: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    record = occurrence_record(occurrence_id, lane_id)
    policy = _repair_policy(max_attempts)
    record["policy_binding"] = policy
    record["schedule_basis"] = {"reason_code": "REPAIR", "required_child_acceptance_bindings": []}
    record["repair_context"] = {
        "finding_ref": deepcopy(dict(finding_ref)),
        "root_occurrence_ref": _stored_occurrence_ref(root_terminal),
        "previous_attempt_occurrence_ref": _stored_occurrence_ref(previous) if previous else None,
        "attempt_ordinal": ordinal,
        "repair_policy_digest": policy["policy_digest"],
    }
    if work_scope_ref is not None:
        record["work_scope_ref"] = deepcopy(dict(work_scope_ref))
    return record


def _schedule_repair(
    mutation: MutationService,
    root_terminal,
    finding_ref: Mapping[str, Any],
    occurrence_id: str,
    *,
    ordinal: int,
    previous=None,
    predecessor=None,
    max_attempts: int = 2,
    work_scope_ref: Mapping[str, Any] | None = None,
):
    lane_id = root_terminal.record["control_lane_id"]
    record = _repair_record(
        occurrence_id,
        lane_id,
        root_terminal,
        finding_ref,
        ordinal=ordinal,
        previous=previous,
        max_attempts=max_attempts,
        work_scope_ref=work_scope_ref,
    )
    predecessor = predecessor or root_terminal
    return mutation.apply(make_request(
        "SCHEDULE_REPAIR_OCCURRENCE",
        f"req_{occurrence_id}",
        lane_id,
        {"occurrence": record, "repair_class": "IMPLEMENTATION_DEFECT"},
        expected_state(
            predecessor_occurrence_ref=_internal_ref(predecessor),
            work_scope_ref=record["work_scope_ref"],
        ),
    ))


def _human_fixture(tmp: str, *, resolver_inputs: list[Mapping[str, Any]], configured_decision=None):
    store = ControlStore(str(Path(tmp) / "human.db"))
    decision = configured_decision or _exact_ref("EXTERNAL_DECISION", "decision_cp_i06")
    clock = lambda: datetime(2026, 9, 1, 9, 30, tzinfo=timezone.utc)
    adapter = DeterministicExternalAdapter(
        source_kind="HUMAN_DECISION",
        adapter_id="fixture-human",
        secret=b"cp-i06-human-secret",
        callback_available=True,
        query_correlation_available=True,
        clock=clock,
    )
    adapter.set_resource(
        "escalation/esc_cp_i06",
        version_scheme="native-immutable-id",
        version_value="decision-v1",
        resolved_refs=[decision],
        satisfies=True,
    )
    trust = TrustResolver({"HUMAN_DECISION": adapter})
    mapping = {}
    if configured_decision is not None and configured_decision.get("identity", {}).get("scheme") == "sha256":
        mapping[canonical_digest(configured_decision)] = TrustFactRequest("HUMAN_DECISION", "escalation/esc_cp_i06")
    elif configured_decision is None:
        mapping[canonical_digest(decision)] = TrustFactRequest("HUMAN_DECISION", "escalation/esc_cp_i06")
    mutation = MutationService(store, trust_resolver=trust, human_decision_sources=mapping)

    source = occurrence_record("so_source", "lane_human")
    mutation.apply(make_request("SCHEDULE_STAGE_OCCURRENCE", "req_source_schedule", "lane_human", {"occurrence": source}))
    current = store.read_latest("STAGE_OCCURRENCE", "so_source")
    escalation = escalation_record("esc_cp_i06", "so_source", "lane_human")
    escalation["raised_from_occurrence_ref"] = _stored_occurrence_ref(current)
    terminal = terminal_facts(
        outcome="ESCALATED",
        status="BLOCKED_UNRESOLVED_DECISION",
        raised=["esc_cp_i06"],
    )
    mutation.apply(make_request(
        "RAISE_ESCALATION",
        "req_raise_escalation",
        "lane_human",
        {
            "occurrence_id": "so_source",
            "recorded_at": "2026-09-01T09:20:00Z",
            "escalation": escalation,
            "terminal": terminal,
        },
        expected_state(
            target_record_revision=1,
            target_record_digest=current.digest,
            work_scope_ref=current.record["work_scope_ref"],
        ),
    ))
    source_terminal = store.read_latest("STAGE_OCCURRENCE", "so_source")
    resolver = occurrence_record("so_resolve", "lane_human")
    resolver["stage_span"] = {"stages": ["P21"]}
    resolver["primary_owner"] = "aegis-governance"
    resolver["schedule_basis"] = {"reason_code": "NEXT_LEGAL_STAGE", "required_child_acceptance_bindings": []}
    resolver["input_refs"] = [deepcopy(dict(ref)) for ref in resolver_inputs]
    mutation.apply(make_request(
        "SCHEDULE_STAGE_OCCURRENCE",
        "req_resolver_schedule",
        "lane_human",
        {"occurrence": resolver},
        expected_state(
            predecessor_occurrence_ref=_internal_ref(source_terminal),
            work_scope_ref=resolver["work_scope_ref"],
        ),
    ))
    return store, mutation, adapter, decision


def _resolution_request(store: ControlStore, decision_ref: Any, request_id: str = "req_resolve"):
    current = store.read_latest("STAGE_OCCURRENCE", "so_resolve")
    terminal = terminal_facts()
    terminal["resolved_escalation_ids"] = ["esc_cp_i06"]
    return make_request(
        "RECORD_ESCALATION_RESOLUTION",
        request_id,
        "lane_human",
        {
            "occurrence_id": "so_resolve",
            "recorded_at": "2026-09-01T09:31:00Z",
            "escalation_id": "esc_cp_i06",
            "decision_ref": decision_ref,
            "terminal": terminal,
        },
        expected_state(
            target_record_revision=current.record["record_revision"],
            target_record_digest=current.digest,
            work_scope_ref=current.record["work_scope_ref"],
        ),
    )


def _human_decision_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp:
        decision = _exact_ref("EXTERNAL_DECISION", "decision_cp_i06")
        store, mutation, _, _ = _human_fixture(tmp, resolver_inputs=[decision], configured_decision=decision)
        before_escalation = store.read_latest("ESCALATION", "esc_cp_i06")
        request = _resolution_request(store, decision)
        result = mutation.apply(request)
        after_escalation = store.read_latest("ESCALATION", "esc_cp_i06")
        resolved = store.read_latest("STAGE_OCCURRENCE", "so_resolve")
        cases.append(_case(
            "exact_durable_decision_accepted",
            result["status"] == "APPLIED" and resolved.record["state"] == "TERMINAL",
            result_status=result["status"],
        ))
        cases.append(_case(
            "escalation_immutable_after_resolution",
            before_escalation.digest == after_escalation.digest
            and before_escalation.record["record_revision"] == after_escalation.record["record_revision"] == 1,
            before_digest=before_escalation.digest,
            after_digest=after_escalation.digest,
        ))
        replay = mutation.apply(request)
        cases.append(_case(
            "exact_resolution_replay_idempotent",
            replay == result and len(store.read_revisions("STAGE_OCCURRENCE", "so_resolve")) == 2,
            revision_count=len(store.read_revisions("STAGE_OCCURRENCE", "so_resolve")),
        ))
        conflict_code = None
        try:
            mutation.apply(_resolution_request(store, _exact_ref("EXTERNAL_DECISION", "other"), "req_conflict"))
        except MutationRejected as exc:
            conflict_code = exc.code
        cases.append(_case(
            "conflicting_second_resolution_rejected",
            conflict_code in {"OCCURRENCE_ALREADY_TERMINAL", "ESCALATION_RESOLUTION_CONFLICT"},
            rejection=conflict_code,
        ))

    invalids = [
        ("missing_decision_rejected", None),
        ("chat_ack_rejected", "approved"),
        ("boolean_ack_rejected", True),
    ]
    for name, invalid in invalids:
        with tempfile.TemporaryDirectory() as tmp:
            store, mutation, _, _ = _human_fixture(tmp, resolver_inputs=[])
            before = dict(store.snapshot_counts())
            code = None
            try:
                mutation.apply(_resolution_request(store, invalid))
            except MutationRejected as exc:
                code = exc.code
            cases.append(_case(
                name,
                code == "HUMAN_DECISION_EXACT_REF_REQUIRED" and before == store.snapshot_counts(),
                rejection=code,
                zero_residue=before == store.snapshot_counts(),
            ))

    with tempfile.TemporaryDirectory() as tmp:
        mutable = _exact_ref("EXTERNAL_DECISION", "decision_cp_i06", scheme="semantic-version")
        store, mutation, _, _ = _human_fixture(tmp, resolver_inputs=[mutable], configured_decision=mutable)
        code = None
        try:
            mutation.apply(_resolution_request(store, mutable))
        except MutationRejected as exc:
            code = exc.code
        cases.append(_case(
            "mutable_unpinned_decision_rejected",
            code == "HUMAN_DECISION_EXACT_REF_REQUIRED",
            rejection=code,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        decision = _exact_ref("EXTERNAL_DECISION", "decision_cp_i06")
        store, mutation, adapter, _ = _human_fixture(tmp, resolver_inputs=[decision], configured_decision=decision)
        adapter.set_resource(
            "escalation/esc_cp_i06",
            version_scheme="native-immutable-id",
            version_value="decision-v2",
            resolved_refs=[_exact_ref("EXTERNAL_DECISION", "decision_replacement")],
            satisfies=True,
        )
        code = None
        try:
            mutation.apply(_resolution_request(store, decision))
        except MutationRejected as exc:
            code = exc.code
        cases.append(_case(
            "stale_decision_rejected",
            code == "HUMAN_DECISION_IDENTITY_MISMATCH",
            rejection=code,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        wrong = _exact_ref("EXTERNAL_DECISION", "wrong")
        store, mutation, _, _ = _human_fixture(tmp, resolver_inputs=[wrong])
        code = None
        try:
            mutation.apply(_resolution_request(store, wrong))
        except MutationRejected as exc:
            code = exc.code
        cases.append(_case(
            "wrong_unmaterialized_decision_rejected",
            code == "HUMAN_DECISION_UNRESOLVABLE",
            rejection=code,
        ))
    return cases


def _recovery_fault_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "restart.db"
        store = ControlStore(str(db))
        mutation = MutationService(store)
        scheduled = mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_restart",
            "lane_restart",
            {"occurrence": occurrence_record("so_restart", "lane_restart")},
        ))
        outbox_id = scheduled["outbox_ids"][0]
        before_counts = dict(store.snapshot_counts())
        before_digest = store.read_latest("STAGE_OCCURRENCE", "so_restart").digest
        before_lane = store.read_lane_head("lane_restart")
        before_idempotency = store.read_idempotency("req_restart")
        reopened = ControlStore(str(db))
        preserved = (
            reopened.snapshot_counts() == before_counts
            and reopened.read_latest("STAGE_OCCURRENCE", "so_restart").digest == before_digest
            and reopened.read_lane_head("lane_restart") == before_lane
            and reopened.read_idempotency("req_restart") == before_idempotency
            and reopened.read_outbox()[0]["outbox_id"] == outbox_id
        )
        cases.append(_case(
            "process_replacement_preserves_acknowledged_commit",
            preserved,
            before_counts=before_counts,
            after_counts=dict(reopened.snapshot_counts()),
            occurrence_digest=before_digest,
        ))
        plan = startup_recovery_plan(reopened, observed_at="2026-09-01T10:00:00Z")
        same = (
            len(plan) == 1
            and plan[0].occurrence_id == "so_restart"
            and plan[0].outbox_id == outbox_id
            and plan[0].action == "DISPATCH_COMMITTED_OUTBOX"
            and not plan[0].semantic_retry
            and not plan[0].replacement_occurrence
            and not plan[0].canonical_mutation
        )
        cases.append(_case(
            "restart_reuses_committed_outbox_same_occurrence",
            same,
            plan=plan[0].__dict__ if plan else None,
        ))
        reopened.record_delivery_correlation(
            outbox_id,
            "corr_restart",
            observed_at="2026-09-01T10:00:05Z",
            provider_state="RUNNING",
        )
        correlated = startup_recovery_plan(reopened, observed_at="2026-09-01T10:01:00Z")
        same_correlated = (
            len(correlated) == 1
            and correlated[0].occurrence_id == "so_restart"
            and correlated[0].action == "RECONCILE_EXISTING_OCCURRENCE"
            and not correlated[0].semantic_retry
            and not correlated[0].replacement_occurrence
        )
        cases.append(_case(
            "restart_with_correlation_reconciles_same_occurrence",
            same_correlated,
            plan=correlated[0].__dict__ if correlated else None,
        ))

    warning = reconciliation_policy(15 * 60)
    critical = reconciliation_policy(2 * 60 * 60)
    cases.append(_case(
        "warning_age_is_diagnostic_only",
        not warning.semantic_terminalization,
        interval_seconds=warning.interval_seconds,
        operator_alert=warning.operator_alert,
    ))
    cases.append(_case(
        "critical_age_is_diagnostic_only",
        not critical.semantic_terminalization and critical.operator_alert,
        interval_seconds=critical.interval_seconds,
        operator_alert=critical.operator_alert,
    ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "repair.db"))
        finding = _exact_ref("FINDING", "finding_cp_i06")
        mutation = MutationService(
            store,
            finding_classifications={canonical_digest(finding): "IMPLEMENTATION_DEFECT"},
        )
        root = _seed_terminal_root(mutation, store, occurrence_id="so_root", lane_id="lane_repair")
        first = _schedule_repair(mutation, root, finding, "so_repair_1", ordinal=1)
        first_open = store.read_latest("STAGE_OCCURRENCE", "so_repair_1")
        first_terminal = _terminalize(mutation, store, "so_repair_1", "lane_repair")
        second = _schedule_repair(
            mutation,
            root,
            finding,
            "so_repair_2",
            ordinal=2,
            previous=first_terminal,
            predecessor=first_terminal,
        )
        second_open = store.read_latest("STAGE_OCCURRENCE", "so_repair_2")
        cases.append(_case(
            "repair_attempts_are_new_contiguous_occurrences",
            first["status"] == second["status"] == "APPLIED"
            and first_open.record["repair_context"]["attempt_ordinal"] == 1
            and second_open.record["repair_context"]["attempt_ordinal"] == 2
            and first_open.record["id"] != second_open.record["id"],
            first_id=first_open.record["id"],
            second_id=second_open.record["id"],
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "gap.db"))
        finding = _exact_ref("FINDING", "finding_gap")
        mutation = MutationService(store, finding_classifications={canonical_digest(finding): "IMPLEMENTATION_DEFECT"})
        root = _seed_terminal_root(mutation, store, occurrence_id="so_root_gap", lane_id="lane_gap")
        before = dict(store.snapshot_counts())
        code = None
        try:
            _schedule_repair(mutation, root, finding, "so_gap", ordinal=2)
        except MutationRejected as exc:
            code = exc.code
        cases.append(_case(
            "repair_lineage_gap_rejected",
            code == "REPAIR_ATTEMPT_ORDINAL_GAP" and before == store.snapshot_counts(),
            rejection=code,
            zero_residue=before == store.snapshot_counts(),
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "budget.db"))
        finding = _exact_ref("FINDING", "finding_budget")
        mutation = MutationService(store, finding_classifications={canonical_digest(finding): "IMPLEMENTATION_DEFECT"})
        root = _seed_terminal_root(mutation, store, occurrence_id="so_root_budget", lane_id="lane_budget")
        _schedule_repair(mutation, root, finding, "so_budget_1", ordinal=1, max_attempts=1)
        terminal = _terminalize(mutation, store, "so_budget_1", "lane_budget")
        before = dict(store.snapshot_counts())
        code = None
        try:
            _schedule_repair(
                mutation,
                root,
                finding,
                "so_budget_2",
                ordinal=2,
                previous=terminal,
                predecessor=terminal,
                max_attempts=1,
            )
        except MutationRejected as exc:
            code = exc.code
        cases.append(_case(
            "repair_budget_exhaustion_rejected",
            code == "REPAIR_BUDGET_EXHAUSTED" and before == store.snapshot_counts(),
            rejection=code,
            zero_residue=before == store.snapshot_counts(),
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "scope.db"))
        finding = _exact_ref("FINDING", "finding_scope")
        mutation = MutationService(store, finding_classifications={canonical_digest(finding): "IMPLEMENTATION_DEFECT"})
        root = _seed_terminal_root(mutation, store, occurrence_id="so_root_scope", lane_id="lane_scope")
        expanded = deepcopy(root.record["work_scope_ref"])
        expanded["id"] = "ws_scope_expanded"
        before = dict(store.snapshot_counts())
        code = None
        try:
            _schedule_repair(
                mutation,
                root,
                finding,
                "so_scope_repair",
                ordinal=1,
                work_scope_ref=expanded,
            )
        except MutationRejected as exc:
            code = exc.code
        cases.append(_case(
            "repair_scope_expansion_rejected",
            code == "REPAIR_SCOPE_EXPANSION" and before == store.snapshot_counts(),
            rejection=code,
            zero_residue=before == store.snapshot_counts(),
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "review-loop.db"))
        finding = _exact_ref("FINDING", "finding_review")
        mutation = MutationService(store, finding_classifications={canonical_digest(finding): "IMPLEMENTATION_DEFECT"})
        root = _seed_terminal_root(mutation, store, occurrence_id="so_root_review", lane_id="lane_review")
        _schedule_repair(mutation, root, finding, "so_repair_review", ordinal=1)
        repair_terminal = _terminalize(mutation, store, "so_repair_review", "lane_review")
        result_ref = _exact_ref("RESULT", "repair-result")
        evidence_ref = _exact_ref("EVIDENCE", "reverify-evidence")

        direct = occurrence_record("so_direct_rereview", "lane_review")
        direct["stage_span"] = {"stages": ["P34"]}
        direct["primary_owner"] = "aegis-gate-review"
        direct["schedule_basis"] = {"reason_code": "REREVIEW", "required_child_acceptance_bindings": []}
        direct["input_refs"] = [result_ref, evidence_ref]
        before = dict(store.snapshot_counts())
        direct_code = None
        try:
            mutation.apply(make_request(
                "SCHEDULE_REREVIEW_OCCURRENCE",
                "req_direct_rereview",
                "lane_review",
                {"occurrence": direct},
                expected_state(
                    predecessor_occurrence_ref=_internal_ref(repair_terminal),
                    work_scope_ref=direct["work_scope_ref"],
                ),
            ))
        except MutationRejected as exc:
            direct_code = exc.code
        cases.append(_case(
            "required_reverification_skip_rejected",
            direct_code == "REQUIRED_REVERIFICATION_NOT_COMPLETED" and before == store.snapshot_counts(),
            rejection=direct_code,
            zero_residue=before == store.snapshot_counts(),
        ))

        reverify = occurrence_record("so_reverify", "lane_review")
        reverify["stage_span"] = {"stages": ["P20"]}
        reverify["primary_owner"] = "aegis-verification"
        reverify["schedule_basis"] = {"reason_code": "REVERIFY", "required_child_acceptance_bindings": []}
        reverify["input_refs"] = [result_ref]
        rv = mutation.apply(make_request(
            "SCHEDULE_REVERIFICATION_OCCURRENCE",
            "req_reverify",
            "lane_review",
            {"occurrence": reverify},
            expected_state(
                predecessor_occurrence_ref=_internal_ref(repair_terminal),
                work_scope_ref=reverify["work_scope_ref"],
            ),
        ))
        reverify_open = store.read_latest("STAGE_OCCURRENCE", "so_reverify")
        cases.append(_case(
            "reverification_is_separate_occurrence",
            rv["status"] == "APPLIED"
            and rv["outbox_ids"] == []
            and reverify_open.record["id"] != repair_terminal.record["id"]
            and reverify_open.record["schedule_basis"]["reason_code"] == "REVERIFY",
            occurrence_id=reverify_open.record["id"],
            outbox_ids=rv["outbox_ids"],
        ))
        reverify_terminal = _terminalize(mutation, store, "so_reverify", "lane_review")
        rereview = occurrence_record("so_rereview", "lane_review")
        rereview["stage_span"] = {"stages": ["P34"]}
        rereview["primary_owner"] = "aegis-gate-review"
        rereview["schedule_basis"] = {"reason_code": "REREVIEW", "required_child_acceptance_bindings": []}
        rereview["input_refs"] = [result_ref, evidence_ref]
        rr = mutation.apply(make_request(
            "SCHEDULE_REREVIEW_OCCURRENCE",
            "req_rereview",
            "lane_review",
            {"occurrence": rereview},
            expected_state(
                predecessor_occurrence_ref=_internal_ref(reverify_terminal),
                work_scope_ref=rereview["work_scope_ref"],
            ),
        ))
        stored_rr = store.read_latest("STAGE_OCCURRENCE", "so_rereview")
        cases.append(_case(
            "rereview_is_separate_external_gate_occurrence",
            rr["status"] == "APPLIED"
            and rr["outbox_ids"] == []
            and stored_rr.record["primary_owner"] == "aegis-gate-review"
            and "gate_decision" not in stored_rr.record,
            occurrence_id=stored_rr.record["id"],
            outbox_ids=rr["outbox_ids"],
            primary_owner=stored_rr.record["primary_owner"],
        ))
    return cases


def _backup_restore_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        store = ControlStore(str(root / "source.db"))
        mutation = MutationService(store)
        scheduled = mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_backup",
            "lane_backup",
            {"occurrence": occurrence_record("so_backup", "lane_backup")},
        ))
        outbox_id = scheduled["outbox_ids"][0]
        store.record_delivery_attempt(
            outbox_id,
            "2026-09-01T10:00:00Z",
            next_attempt_at="2026-09-01T10:00:01Z",
        )
        source_record = store.read_latest("STAGE_OCCURRENCE", "so_backup")
        source_revisions = [item.digest for item in store.read_revisions("STAGE_OCCURRENCE", "so_backup")]
        source_lane = store.read_lane_head("lane_backup")
        source_idempotency = store.read_idempotency("req_backup")
        source_outbox = store.read_outbox()
        source_delivery = store.read_delivery_state(outbox_id)
        source_counts = dict(store.snapshot_counts())
        backup = root / "backup.db"
        metadata = backup_control_store(store, str(backup))
        restored = restore_control_store_backup(str(backup), str(root / "restored.db"))
        exact = (
            metadata["integrity_check"] == "ok"
            and verify_control_store_integrity(restored) == "ok"
            and restored.snapshot_counts() == source_counts
            and restored.read_latest("STAGE_OCCURRENCE", "so_backup").digest == source_record.digest
            and [item.digest for item in restored.read_revisions("STAGE_OCCURRENCE", "so_backup")] == source_revisions
            and restored.read_lane_head("lane_backup") == source_lane
            and restored.read_idempotency("req_backup") == source_idempotency
            and restored.read_outbox() == source_outbox
            and restored.read_delivery_state(outbox_id) == source_delivery
        )
        cases.append(_case(
            "verified_backup_restore_preserves_exact_state",
            exact,
            source_digest=source_record.digest,
            restored_digest=restored.read_latest("STAGE_OCCURRENCE", "so_backup").digest,
            source_counts=source_counts,
            restored_counts=dict(restored.snapshot_counts()),
            claimed_fault_model="supported_primary_fault_model_only",
            regional_disaster_recovery_claimed=False,
        ))
        corrupt = root / "corrupt.db"
        backup_control_store(store, str(corrupt))
        corrupt.write_bytes(b"not-a-sqlite-database")
        destination = root / "fabricated.db"
        blocked = False
        try:
            restore_control_store_backup(str(corrupt), str(destination))
        except StoreConflict:
            blocked = True
        cases.append(_case(
            "corrupt_backup_fails_closed",
            blocked and not destination.exists(),
            rejected=blocked,
            fabricated_destination=destination.exists(),
        ))
    return cases


def _rate_limit_cases() -> list[dict[str, Any]]:
    controller = ProviderRateLimitController(baseline_concurrency=100)
    below = controller.observe(window_seconds=300, request_count=100, rate_limited_count=5)
    breached = controller.observe(
        window_seconds=300,
        request_count=100,
        rate_limited_count=6,
        retry_after_seconds=120,
    )
    recovered = controller.observe(window_seconds=300, request_count=100, rate_limited_count=0)
    no_retry = ProviderRateLimitController(baseline_concurrency=8).observe(
        window_seconds=300,
        request_count=20,
        rate_limited_count=2,
    )
    return [
        _case(
            "exact_five_percent_does_not_reduce_concurrency",
            below.concurrency == 100 and not below.breached,
            concurrency=below.concurrency,
        ),
        _case(
            "sustained_over_five_percent_halves_concurrency",
            breached.concurrency == 50 and breached.breached,
            concurrency=breached.concurrency,
        ),
        _case(
            "safe_retry_after_is_retained",
            breached.retry_after_seconds == 120,
            retry_after_seconds=breached.retry_after_seconds,
        ),
        _case(
            "recovery_is_gradual_not_instant",
            50 < recovered.concurrency < 100,
            concurrency=recovered.concurrency,
        ),
        _case(
            "rate_limit_control_never_requests_semantic_retry",
            not no_retry.semantic_retry and no_retry.reduce_polling_before_proof_or_review,
            semantic_retry=no_retry.semantic_retry,
            reduce_polling_before_proof_or_review=no_retry.reduce_polling_before_proof_or_review,
        ),
    ]


def _derived_operational_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    levels = {
        "0.69": classify_backpressure(0.69),
        "0.70": classify_backpressure(0.70),
        "0.85": classify_backpressure(0.85),
        "0.95": classify_backpressure(0.95),
    }
    cases.append(_case(
        "backpressure_watermarks_match_p18",
        levels == {"0.69": "GREEN", "0.70": "YELLOW", "0.85": "ORANGE", "0.95": "RED"},
        levels=levels,
    ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "operational.db"))
        mutation = MutationService(store)
        scheduled = mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_operational",
            "lane_operational",
            {"occurrence": occurrence_record("so_operational", "lane_operational")},
        ))
        outbox_id = scheduled["outbox_ids"][0]
        before_counts = dict(store.snapshot_counts())
        before_outbox = deepcopy(store.read_outbox())
        controller = AdmissionController()
        controller.pause()
        paused = controller.evaluate(utilization=0.20, autonomous=True)
        cases.append(_case(
            "pause_changes_no_canonical_history",
            not paused.admit and before_counts == store.snapshot_counts(),
            reason=paused.reason,
            before=before_counts,
            after=dict(store.snapshot_counts()),
        ))
        controller.resume()
        resumed = controller.evaluate(utilization=0.20, autonomous=True)
        cases.append(_case(
            "resume_requires_fresh_recompute",
            resumed.admit and resumed.requires_fresh_recompute,
            requires_fresh_recompute=resumed.requires_fresh_recompute,
        ))
        orange = controller.evaluate(utilization=0.90, autonomous=True)
        red = controller.evaluate(utilization=0.99, autonomous=True)
        recovery = controller.evaluate(utilization=0.99, autonomous=False, recovery=True)
        cases.append(_case(
            "orange_defers_new_autonomous_admission",
            not orange.admit and orange.reason == "DEFER_NEW_AUTONOMOUS_ADMISSION",
            reason=orange.reason,
        ))
        cases.append(_case(
            "red_stops_new_autonomous_admission",
            not red.admit and red.reason == "STOP_NEW_AUTONOMOUS_ADMISSION",
            reason=red.reason,
        ))
        cases.append(_case(
            "red_preserves_committed_recovery",
            recovery.admit and recovery.recovery_priority,
            reason=recovery.reason,
        ))
        manual = manual_fallback_guard(active_controlled_work=True)
        cases.append(_case(
            "manual_duplicate_fallback_is_denied",
            not manual.allowed and not manual.semantic_retry and not manual.replacement_occurrence,
            reason=manual.reason,
        ))
        cases.append(_case(
            "committed_outbox_is_not_dropped_by_backpressure",
            store.read_outbox() == before_outbox
            and store.read_outbox()[0]["outbox_id"] == outbox_id
            and store.snapshot_counts() == before_counts,
            before_outbox=before_outbox,
            after_outbox=store.read_outbox(),
        ))
    return cases


def _evidence_document(evidence_family: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "0.2",
        "evidence_family": evidence_family,
        "cases": cases,
        "passed": all(case["passed"] for case in cases),
    }


def _metrics(documents: Mapping[str, Mapping[str, Any]]) -> dict[str, int]:
    by_name = {
        case["case"]: case
        for document in documents.values()
        for case in document["cases"]
    }
    metric_pass_requirements = {
        "unmaterialized_human_acknowledgement_accepted": [
            "missing_decision_rejected", "chat_ack_rejected", "boolean_ack_rejected",
            "mutable_unpinned_decision_rejected", "stale_decision_rejected",
            "wrong_unmaterialized_decision_rejected",
        ],
        "semantic_retry_from_restart_or_age": [
            "restart_reuses_committed_outbox_same_occurrence",
            "restart_with_correlation_reconciles_same_occurrence",
            "warning_age_is_diagnostic_only",
            "critical_age_is_diagnostic_only",
        ],
        "unsafe_manual_duplicate_execution": ["manual_duplicate_fallback_is_denied"],
        "acknowledged_commit_loss_in_supported_primary_fault_model": [
            "process_replacement_preserves_acknowledged_commit",
            "verified_backup_restore_preserves_exact_state",
        ],
        "repair_scope_expansion_accepted": ["repair_scope_expansion_rejected"],
        "repair_budget_violation_accepted": ["repair_budget_exhaustion_rejected"],
        "repair_lineage_gap_accepted": ["repair_lineage_gap_rejected"],
        "escalation_history_mutated": ["escalation_immutable_after_resolution"],
        "conflicting_escalation_resolution_accepted": ["conflicting_second_resolution_rejected"],
        "required_reverification_skipped": [
            "required_reverification_skip_rejected",
            "reverification_is_separate_occurrence",
        ],
        "control_plane_self_issued_gate_verdict": ["rereview_is_separate_external_gate_occurrence"],
        "pause_or_backpressure_semantic_mutation": [
            "pause_changes_no_canonical_history",
            "orange_defers_new_autonomous_admission",
            "red_stops_new_autonomous_admission",
        ],
        "committed_outbox_dropped_by_backpressure": ["committed_outbox_is_not_dropped_by_backpressure"],
        "sustained_rate_limit_breach_without_concurrency_reduction": [
            "sustained_over_five_percent_halves_concurrency"
        ],
        "instant_full_rate_limit_recovery": ["recovery_is_gradual_not_instant"],
        "restore_digest_or_revision_mismatch": [
            "verified_backup_restore_preserves_exact_state",
            "corrupt_backup_fails_closed",
        ],
    }
    metrics: dict[str, int] = {}
    for metric, required_cases in metric_pass_requirements.items():
        metrics[metric] = sum(1 for name in required_cases if not by_name.get(name, {}).get("passed", False))
    if set(metrics) != ZERO_METRIC_KEYS:
        raise RuntimeError("CP-I06 metric contract mismatch")
    return metrics


def generate(output_dir: Path, *, result_revision: str) -> dict[str, Any]:
    documents = {
        "human-decision.json": _evidence_document("CPV-E-HUMAN-DECISION", _human_decision_cases()),
        "recovery-fault-matrix.json": _evidence_document("CPV-E-RECOVERY-FAULT-MATRIX", _recovery_fault_cases()),
        "backup-restore.json": _evidence_document("CPV-E-BACKUP-RESTORE", _backup_restore_cases()),
        "rate-limit-control.json": _evidence_document("CPV-E-RATE-LIMIT-CONTROL", _rate_limit_cases()),
        "derived-operational-state.json": _evidence_document("CPV-E-DERIVED-STATE", _derived_operational_cases()),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, document in documents.items():
        _write_json(output_dir / filename, document)

    metrics = _metrics(documents)
    evidence_files = [
        {
            "file": filename,
            "evidence_family": EVIDENCE_FAMILIES[filename],
            "digest": _sha256(output_dir / filename),
            "passed": document["passed"],
        }
        for filename, document in sorted(documents.items())
    ]
    manifest = {
        "schema_version": "0.2",
        "kind": "CP-I06_EVIDENCE_MANIFEST",
        "package_id": PACKAGE_ID,
        "package_ref": PACKAGE_REF,
        "result_revision": result_revision,
        "task_anchor": TASK_ANCHOR,
        "predecessor": {
            "cp_i05_revision": CP_I05_REVISION,
            "cp_i05_p34_comment": CP_I05_P34_COMMENT,
            "cp_i05_evidence_artifact_id": CP_I05_EVIDENCE_ARTIFACT_ID,
        },
        "evidence_files": evidence_files,
        "metrics": metrics,
        "claims": {
            "p34_gate_pass": False,
            "evidence_compiler_gate_authority": False,
            "cp_i07_plus": False,
            "current_cross_primary_rollout": "DENIED",
            "R0": False,
            "S0": False,
            "seven_day_cost": False,
            "monthly_availability": False,
            "regional_disaster_recovery": False,
        },
        "passed": all(entry["passed"] for entry in evidence_files)
        and all(value == 0 for value in metrics.values()),
    }
    _write_json(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--output-dir", default="artifacts/cp-i06")
    args = parser.parse_args()
    manifest = generate(Path(args.output_dir), result_revision=args.result_revision)
    if not manifest["passed"]:
        raise SystemExit("CP-I06 evidence bundle did not satisfy the zero-tolerance contract")


if __name__ == "__main__":
    main()
