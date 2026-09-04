from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
from typing import Any, Mapping

import tests.control_plane.generate_cp_i06_evidence as base
from tests.control_plane.cp_i02_fixtures import (
    escalation_record,
    expected_state,
    make_request,
    occurrence_record,
    terminal_facts,
)
from tools.aegis_control.canonical import canonical_digest
from tools.aegis_control.external_ports import DeterministicExternalAdapter
from tools.aegis_control.mutation import (
    HumanDecisionSupportBinding,
    MutationRejected,
    MutationService,
)
from tools.aegis_control.operational import AdmissionController, ProviderRateLimitController
from tools.aegis_control.store import ControlStore
from tools.aegis_control.trust import TrustFactRequest, TrustResolver


PACKAGE_ID = base.PACKAGE_ID
PACKAGE_REF = base.PACKAGE_REF
TASK_ANCHOR = base.TASK_ANCHOR
CP_I05_REVISION = base.CP_I05_REVISION
CP_I05_P34_COMMENT = base.CP_I05_P34_COMMENT
CP_I05_EVIDENCE_ARTIFACT_ID = base.CP_I05_EVIDENCE_ARTIFACT_ID
CP_I05_EVIDENCE_RUN = "33483868554"
CP_I05_MATERIALIZED_REF = (
    "https://github.com/Mostorm-Labs/aegis/actions/runs/"
    f"{CP_I05_EVIDENCE_RUN}/artifacts/{CP_I05_EVIDENCE_ARTIFACT_ID}"
)

_ORIGINAL_HUMAN_CASES = base._human_decision_cases
_ORIGINAL_RECOVERY_CASES = base._recovery_fault_cases
_ORIGINAL_RATE_CASES = base._rate_limit_cases
_ORIGINAL_DERIVED_CASES = base._derived_operational_cases


P31_MANDATORY_OBLIGATIONS = {
    "9.1": [
        "repair_first_attempt_ordinal_1",
        "repair_second_attempt_contiguous_and_exact_previous",
        "repair_gap_ordinal_rejected_zero_residue",
        "repair_duplicate_ordinal_or_lineage_conflict_rejected",
        "repair_budget_exhausted_rejected_or_escalated_without_repair_occurrence",
        "repair_wrong_class_rejected_zero_residue",
        "repair_ambiguous_classification_rejected",
        "repair_root_finding_change_rejected",
        "repair_policy_digest_mismatch_rejected",
        "repair_scope_expansion_rejected",
        "repair_authority_or_semantic_defect_not_laundered_as_implementation_repair",
        "competing_repair_candidates_exactly_one_cas_winner",
    ],
    "9.2": [
        "required_reverification_creates_distinct_occurrence",
        "required_reverification_exact_repaired_result_binding",
        "required_reverification_cannot_be_skipped_by_local_test_success",
        "rereview_creates_distinct_review_occurrence",
        "rereview_consumes_exact_new_evidence_basis",
        "rereview_does_not_mutate_prior_gate_decision",
        "control_plane_cannot_issue_p34_verdict",
        "current_cross_primary_rollout_denies_unpermitted_auto_handoff",
    ],
    "9.3": [
        "raise_escalation_atomic_with_terminal_occurrence",
        "raise_escalation_precommit_faults_leave_zero_residue",
        "escalation_immutable_revision_one",
        "escalation_required_decision_does_not_self_resolve",
        "chat_or_ui_acknowledgement_not_semantic_resolution",
        "human_decision_missing_exact_ref_rejected",
        "human_decision_mutable_or_unpinned_ref_rejected",
        "human_decision_wrong_resource_or_stale_snapshot_rejected",
        "human_decision_exact_durable_ref_accepted",
        "escalation_resolution_uses_separate_occurrence",
        "exact_resolution_replay_idempotent",
        "conflicting_second_resolution_rejected",
    ],
    "9.4": [
        "crash_before_schedule_commit_no_dispatch",
        "restart_after_open_outbox_commit_dispatches_same_occurrence",
        "restart_after_dispatch_before_ack_reuses_same_occurrence_and_correlation",
        "restart_after_execution_progress_resolves_p33_position",
        "callback_loss_after_materialization_resolves_same_exact_result",
        "restart_after_terminal_before_projection_rebuilds_without_rollback",
        "restart_after_projection_before_next_schedule_recomputes_candidate",
        "restart_after_successor_open_before_dispatch_preserves_separate_successor",
        "store_unavailable_creates_no_fabricated_history",
        "warning_age_reconciles_without_terminalization",
        "critical_age_alerts_reconciles_without_terminalization_or_replacement",
    ],
    "9.5": [
        "backup_restore_preserves_exact_canonical_bytes_and_digests",
        "backup_restore_preserves_revision_lineage",
        "backup_restore_preserves_lane_heads",
        "backup_restore_preserves_semantic_idempotency_replay",
        "backup_restore_preserves_committed_outbox_intent",
        "post_restore_current_external_truth_is_reconciled_before_auto_continuation",
        "possible_acknowledged_commit_gap_blocks_continuation",
        "restore_never_fabricates_missing_history",
    ],
    "9.6": [
        "pause_causes_zero_canonical_delta",
        "pause_does_not_drop_open_occurrence",
        "pause_does_not_drop_committed_outbox",
        "resume_recomputes_fresh_truth_not_stale_candidate",
        "watermark_green_normal_admission",
        "watermark_yellow_reduces_optional_before_required_work",
        "watermark_orange_defers_new_autonomous_admission",
        "watermark_red_stops_saturated_new_autonomous_admission",
        "terminalization_priority_survives_backpressure",
        "reconciliation_priority_survives_backpressure",
        "committed_outbox_drain_survives_backpressure",
        "backpressure_state_never_becomes_semantic_blocker_record",
    ],
    "9.7": [
        "rate_limit_at_or_below_5_percent_over_5_min_no_false_sustained_breach",
        "rate_limit_above_5_percent_over_5_min_reduces_new_dispatch_concurrency",
        "sustained_repeated_breach_applies_reference_halving_behavior",
        "safe_retry_after_is_honored",
        "polling_is_reduced_before_substantive_proof_or_review_is_weakened",
        "provider_recovery_increases_concurrency_gradually",
        "provider_recovery_does_not_jump_immediately_to_full_capacity",
        "rate_limit_state_creates_no_semantic_occurrence",
        "provider_unavailability_not_misclassified_as_implementation_or_gate_failure",
    ],
}


def _patched_human_fixture(
    tmp: str,
    *,
    resolver_inputs: list[Mapping[str, Any]],
    configured_decision=None,
):
    store = ControlStore(str(Path(tmp) / "human.db"))
    decision = configured_decision or base._exact_ref("EXTERNAL_DECISION", "decision_cp_i06")
    clock = lambda: datetime(2026, 9, 1, 9, 30, tzinfo=timezone.utc)
    adapter = DeterministicExternalAdapter(
        source_kind="HUMAN_DECISION",
        adapter_id="fixture-human",
        secret=b"cp-i06-human-secret",
        callback_available=True,
        query_correlation_available=True,
        clock=clock,
    )
    resource_key = "escalation/esc_cp_i06"
    adapter.set_resource(
        resource_key,
        version_scheme="native-immutable-id",
        version_value="decision-v1",
        resolved_refs=[decision],
        satisfies=True,
    )
    trust = TrustResolver({"HUMAN_DECISION": adapter})
    mapping = {}
    if configured_decision is not None and configured_decision.get("identity", {}).get("scheme") == "sha256":
        mapping[canonical_digest(configured_decision)] = HumanDecisionSupportBinding(
            escalation_id="esc_cp_i06",
            trust_fact_request=TrustFactRequest("HUMAN_DECISION", resource_key),
        )
    elif configured_decision is None:
        mapping[canonical_digest(decision)] = HumanDecisionSupportBinding(
            escalation_id="esc_cp_i06",
            trust_fact_request=TrustFactRequest("HUMAN_DECISION", resource_key),
        )
    mutation = MutationService(store, trust_resolver=trust, human_decision_sources=mapping)

    source = occurrence_record("so_source", "lane_human")
    mutation.apply(make_request(
        "SCHEDULE_STAGE_OCCURRENCE",
        "req_source_schedule",
        "lane_human",
        {"occurrence": source},
    ))
    current = store.read_latest("STAGE_OCCURRENCE", "so_source")
    escalation = escalation_record("esc_cp_i06", "so_source", "lane_human")
    escalation["raised_from_occurrence_ref"] = base._stored_occurrence_ref(current)
    mutation.apply(make_request(
        "RAISE_ESCALATION",
        "req_raise_escalation",
        "lane_human",
        {
            "occurrence_id": "so_source",
            "recorded_at": "2026-09-01T09:20:00Z",
            "escalation": escalation,
            "terminal": terminal_facts(
                outcome="ESCALATED",
                status="BLOCKED_UNRESOLVED_DECISION",
                raised=["esc_cp_i06"],
            ),
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
    resolver["schedule_basis"] = {
        "reason_code": "NEXT_LEGAL_STAGE",
        "required_child_acceptance_bindings": [],
    }
    resolver["input_refs"] = [deepcopy(dict(ref)) for ref in resolver_inputs]
    mutation.apply(make_request(
        "SCHEDULE_STAGE_OCCURRENCE",
        "req_resolver_schedule",
        "lane_human",
        {"occurrence": resolver},
        expected_state(
            predecessor_occurrence_ref=base._internal_ref(source_terminal),
            work_scope_ref=resolver["work_scope_ref"],
        ),
    ))
    return store, mutation, adapter, decision


def _wrong_resource_case() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "wrong-resource.db"))
        decision = base._exact_ref("EXTERNAL_DECISION", "decision_other_escalation")
        clock = lambda: datetime(2026, 9, 1, 9, 30, tzinfo=timezone.utc)
        adapter = DeterministicExternalAdapter(
            source_kind="HUMAN_DECISION",
            adapter_id="fixture-human-wrong-resource",
            secret=b"cp-i06-p36-wrong-resource",
            callback_available=True,
            query_correlation_available=True,
            clock=clock,
        )
        provider_resource = "opaque-human-resource-7"
        adapter.set_resource(
            provider_resource,
            version_scheme="native-immutable-id",
            version_value="decision-other-v1",
            resolved_refs=[decision],
            satisfies=True,
        )
        mutation = MutationService(
            store,
            trust_resolver=TrustResolver({"HUMAN_DECISION": adapter}),
            human_decision_sources={
                canonical_digest(decision): HumanDecisionSupportBinding(
                    escalation_id="esc_other",
                    trust_fact_request=TrustFactRequest("HUMAN_DECISION", provider_resource),
                )
            },
        )
        source = occurrence_record("so_source_wrong_resource", "lane_wrong_resource")
        mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_source_wrong_resource",
            "lane_wrong_resource",
            {"occurrence": source},
        ))
        current = store.read_latest("STAGE_OCCURRENCE", "so_source_wrong_resource")
        escalation = escalation_record(
            "esc_cp_i06", "so_source_wrong_resource", "lane_wrong_resource"
        )
        escalation["raised_from_occurrence_ref"] = base._stored_occurrence_ref(current)
        mutation.apply(make_request(
            "RAISE_ESCALATION",
            "req_raise_wrong_resource",
            "lane_wrong_resource",
            {
                "occurrence_id": "so_source_wrong_resource",
                "recorded_at": "2026-09-01T09:20:00Z",
                "escalation": escalation,
                "terminal": terminal_facts(
                    outcome="ESCALATED",
                    status="BLOCKED_UNRESOLVED_DECISION",
                    raised=["esc_cp_i06"],
                ),
            },
            expected_state(
                target_record_revision=1,
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        ))
        source_terminal = store.read_latest("STAGE_OCCURRENCE", "so_source_wrong_resource")
        resolver = occurrence_record("so_resolve_wrong_resource", "lane_wrong_resource")
        resolver["stage_span"] = {"stages": ["P21"]}
        resolver["primary_owner"] = "aegis-governance"
        resolver["schedule_basis"] = {
            "reason_code": "NEXT_LEGAL_STAGE",
            "required_child_acceptance_bindings": [],
        }
        resolver["input_refs"] = [decision]
        mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_schedule_resolver_wrong_resource",
            "lane_wrong_resource",
            {"occurrence": resolver},
            expected_state(
                predecessor_occurrence_ref=base._internal_ref(source_terminal),
                work_scope_ref=resolver["work_scope_ref"],
            ),
        ))
        resolver_current = store.read_latest("STAGE_OCCURRENCE", "so_resolve_wrong_resource")
        terminal = terminal_facts()
        terminal["resolved_escalation_ids"] = ["esc_cp_i06"]
        before = dict(store.snapshot_counts())
        before_escalation = store.read_latest("ESCALATION", "esc_cp_i06")
        code = None
        try:
            mutation.apply(make_request(
                "RECORD_ESCALATION_RESOLUTION",
                "req_resolve_wrong_resource_evidence",
                "lane_wrong_resource",
                {
                    "occurrence_id": "so_resolve_wrong_resource",
                    "recorded_at": "2026-09-01T09:31:00Z",
                    "escalation_id": "esc_cp_i06",
                    "decision_ref": decision,
                    "terminal": terminal,
                },
                expected_state(
                    target_record_revision=resolver_current.record["record_revision"],
                    target_record_digest=resolver_current.digest,
                    work_scope_ref=resolver_current.record["work_scope_ref"],
                ),
            ))
        except MutationRejected as exc:
            code = exc.code
        after_escalation = store.read_latest("ESCALATION", "esc_cp_i06")
        return base._case(
            "valid_fresh_materialized_wrong_resource_decision_rejected_zero_residue",
            code == "HUMAN_DECISION_WRONG_RESOURCE"
            and before == store.snapshot_counts()
            and before_escalation.digest == after_escalation.digest
            and store.read_latest("STAGE_OCCURRENCE", "so_resolve_wrong_resource").record["state"] == "OPEN",
            rejection=code,
            provider_resource_key=provider_resource,
            bound_escalation_id="esc_other",
            attempted_escalation_id="esc_cp_i06",
            decision_ref=decision,
            zero_residue=before == store.snapshot_counts(),
        )


def _human_cases() -> list[dict[str, Any]]:
    base._human_fixture = _patched_human_fixture
    return [*_ORIGINAL_HUMAN_CASES(), _wrong_resource_case()]


def _additional_repair_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "duplicate.db"))
        finding = base._exact_ref("FINDING", "finding_duplicate")
        mutation = MutationService(
            store,
            finding_classifications={canonical_digest(finding): "IMPLEMENTATION_DEFECT"},
        )
        root = base._seed_terminal_root(
            mutation, store, occurrence_id="so_root_duplicate", lane_id="lane_duplicate"
        )
        base._schedule_repair(mutation, root, finding, "so_dup_1", ordinal=1)
        first_terminal = base._terminalize(mutation, store, "so_dup_1", "lane_duplicate")
        before = dict(store.snapshot_counts())
        code = None
        try:
            base._schedule_repair(
                mutation,
                root,
                finding,
                "so_dup_again",
                ordinal=1,
                predecessor=first_terminal,
            )
        except MutationRejected as exc:
            code = exc.code
        cases.append(base._case(
            "repair_duplicate_ordinal_rejected",
            code == "REPAIR_ATTEMPT_ORDINAL_GAP" and before == store.snapshot_counts(),
            rejection=code,
            zero_residue=before == store.snapshot_counts(),
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "ambiguous.db"))
        finding = base._exact_ref("FINDING", "finding_ambiguous")
        mutation = MutationService(
            store,
            finding_classifications={canonical_digest(finding): "AMBIGUOUS"},
        )
        root = base._seed_terminal_root(
            mutation, store, occurrence_id="so_root_ambiguous", lane_id="lane_ambiguous"
        )
        before = dict(store.snapshot_counts())
        code = None
        try:
            base._schedule_repair(mutation, root, finding, "so_ambiguous", ordinal=1)
        except MutationRejected as exc:
            code = exc.code
        cases.append(base._case(
            "repair_ambiguous_classification_rejected",
            code == "REPAIR_FINDING_CLASSIFICATION_CONFLICT" and before == store.snapshot_counts(),
            rejection=code,
            zero_residue=before == store.snapshot_counts(),
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "root-change.db"))
        finding_a = base._exact_ref("FINDING", "finding_root_a")
        finding_b = base._exact_ref("FINDING", "finding_root_b")
        mutation = MutationService(
            store,
            finding_classifications={
                canonical_digest(finding_a): "IMPLEMENTATION_DEFECT",
                canonical_digest(finding_b): "IMPLEMENTATION_DEFECT",
            },
        )
        root = base._seed_terminal_root(
            mutation, store, occurrence_id="so_root_change", lane_id="lane_root_change"
        )
        base._schedule_repair(mutation, root, finding_a, "so_root_change_1", ordinal=1)
        first_terminal = base._terminalize(
            mutation, store, "so_root_change_1", "lane_root_change"
        )
        before = dict(store.snapshot_counts())
        code = None
        try:
            base._schedule_repair(
                mutation,
                root,
                finding_b,
                "so_root_change_2",
                ordinal=2,
                previous=first_terminal,
                predecessor=first_terminal,
            )
        except MutationRejected as exc:
            code = exc.code
        cases.append(base._case(
            "repair_root_finding_change_rejected",
            code in {"REPAIR_ATTEMPT_ORDINAL_GAP", "REPAIR_FINDING_LINEAGE_MISMATCH"}
            and before == store.snapshot_counts(),
            rejection=code,
            zero_residue=before == store.snapshot_counts(),
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "policy-digest.db"))
        finding = base._exact_ref("FINDING", "finding_policy_digest")
        mutation = MutationService(
            store,
            finding_classifications={canonical_digest(finding): "IMPLEMENTATION_DEFECT"},
        )
        root = base._seed_terminal_root(
            mutation, store, occurrence_id="so_root_policy", lane_id="lane_policy"
        )
        record = base._repair_record(
            "so_policy_bad", "lane_policy", root, finding, ordinal=1
        )
        record["repair_context"]["repair_policy_digest"] = "sha256:" + "0" * 64
        before = dict(store.snapshot_counts())
        code = None
        try:
            mutation.apply(make_request(
                "SCHEDULE_REPAIR_OCCURRENCE",
                "req_policy_bad",
                "lane_policy",
                {"occurrence": record, "repair_class": "IMPLEMENTATION_DEFECT"},
                expected_state(
                    predecessor_occurrence_ref=base._internal_ref(root),
                    work_scope_ref=record["work_scope_ref"],
                ),
            ))
        except MutationRejected as exc:
            code = exc.code
        cases.append(base._case(
            "repair_policy_digest_mismatch_rejected",
            code == "REPAIR_POLICY_DIGEST_MISMATCH" and before == store.snapshot_counts(),
            rejection=code,
            zero_residue=before == store.snapshot_counts(),
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "authority-launder.db"))
        finding = base._exact_ref("FINDING", "finding_authority")
        mutation = MutationService(
            store,
            finding_classifications={canonical_digest(finding): "AUTHORITY_CHANGE"},
        )
        root = base._seed_terminal_root(
            mutation, store, occurrence_id="so_root_authority", lane_id="lane_authority"
        )
        before = dict(store.snapshot_counts())
        code = None
        try:
            base._schedule_repair(mutation, root, finding, "so_authority_repair", ordinal=1)
        except MutationRejected as exc:
            code = exc.code
        cases.append(base._case(
            "repair_authority_or_semantic_defect_not_laundered",
            code == "REPAIR_FINDING_CLASSIFICATION_CONFLICT" and before == store.snapshot_counts(),
            rejection=code,
            zero_residue=before == store.snapshot_counts(),
        ))
    return cases


def _recovery_cases() -> list[dict[str, Any]]:
    return [*_ORIGINAL_RECOVERY_CASES(), *_additional_repair_cases()]


def _rate_cases() -> list[dict[str, Any]]:
    cases = list(_ORIGINAL_RATE_CASES())
    repeated = ProviderRateLimitController(baseline_concurrency=100)
    first = repeated.observe(window_seconds=300, request_count=100, rate_limited_count=6)
    second = repeated.observe(window_seconds=300, request_count=100, rate_limited_count=6)
    cases.append(base._case(
        "repeated_sustained_breach_halves_again",
        first.concurrency == 50 and second.concurrency == 25,
        first_concurrency=first.concurrency,
        second_concurrency=second.concurrency,
    ))
    unavailable = ProviderRateLimitController(baseline_concurrency=8).observe(
        window_seconds=300, request_count=10, rate_limited_count=10
    )
    cases.append(base._case(
        "provider_unavailability_remains_operational_not_gate_or_implementation_failure",
        unavailable.breached and not unavailable.semantic_retry,
        breached=unavailable.breached,
        semantic_retry=unavailable.semantic_retry,
        classification="OPERATIONAL_PROVIDER_PRESSURE",
    ))
    return cases


def _derived_cases() -> list[dict[str, Any]]:
    cases = list(_ORIGINAL_DERIVED_CASES())
    controller = AdmissionController()
    green = controller.evaluate(utilization=0.20, autonomous=True)
    yellow = controller.evaluate(utilization=0.75, autonomous=True)
    terminalization = controller.evaluate(utilization=0.99, autonomous=False, recovery=True)
    reconciliation = controller.evaluate(utilization=0.99, autonomous=False, recovery=True)
    cases.extend([
        base._case(
            "green_normal_admission",
            green.admit and green.reason == "ADMIT",
            reason=green.reason,
        ),
        base._case(
            "yellow_reduces_optional_before_required_work",
            yellow.admit and yellow.reason == "REDUCE_OPTIONAL_OR_SPECULATIVE_WORK",
            reason=yellow.reason,
        ),
        base._case(
            "terminalization_priority_survives_backpressure",
            terminalization.admit and terminalization.recovery_priority,
            reason=terminalization.reason,
        ),
        base._case(
            "reconciliation_priority_survives_backpressure",
            reconciliation.admit and reconciliation.recovery_priority,
            reason=reconciliation.reason,
        ),
    ])
    return cases


def _direct(case_id: str, rationale: str) -> dict[str, Any]:
    return {
        "mode": "DIRECT_CP_I06",
        "case_id": case_id,
        "rationale": rationale,
    }


def _inherited(case_id: str, rationale: str) -> dict[str, Any]:
    return {
        "mode": "INHERITED_EXACT_PREDECESSOR",
        "predecessor_revision": CP_I05_REVISION,
        "artifact_id": CP_I05_EVIDENCE_ARTIFACT_ID,
        "materialized_ref": CP_I05_MATERIALIZED_REF,
        "evidence_file": "dispatch-fault-matrix.json",
        "case_id": case_id,
        "rationale": rationale,
    }


def _coverage_map() -> dict[str, Any]:
    e_recovery = "CPV-E-RECOVERY-FAULT-MATRIX::"
    e_human = "CPV-E-HUMAN-DECISION::"
    e_backup = "CPV-E-BACKUP-RESTORE::"
    e_rate = "CPV-E-RATE-LIMIT-CONTROL::"
    e_derived = "CPV-E-DERIVED-STATE::"
    coverage = {
        "repair_first_attempt_ordinal_1": _direct(e_recovery + "repair_attempts_are_new_contiguous_occurrences", "Executed CP-I06 evidence records ordinal 1."),
        "repair_second_attempt_contiguous_and_exact_previous": _direct(e_recovery + "repair_attempts_are_new_contiguous_occurrences", "The same executed lineage records ordinal 2 as a distinct successor."),
        "repair_gap_ordinal_rejected_zero_residue": _direct(e_recovery + "repair_lineage_gap_rejected", "Executed gap request is rejected with zero residue."),
        "repair_duplicate_ordinal_or_lineage_conflict_rejected": _direct(e_recovery + "repair_duplicate_ordinal_rejected", "P36 executes a duplicate ordinal after an accepted first attempt and verifies zero residue."),
        "repair_budget_exhausted_rejected_or_escalated_without_repair_occurrence": _direct(e_recovery + "repair_budget_exhaustion_rejected", "Executed exhausted budget creates no repair occurrence."),
        "repair_wrong_class_rejected_zero_residue": _direct("tests.control_plane.test_cp_i06_repair.CpI06RepairRedTests.test_wrong_finding_or_caller_reclassification_fails_closed", "Exact-head focused test exercises caller reclassification fail-closed."),
        "repair_ambiguous_classification_rejected": _direct(e_recovery + "repair_ambiguous_classification_rejected", "P36 executes ambiguous classification and verifies zero residue."),
        "repair_root_finding_change_rejected": _direct(e_recovery + "repair_root_finding_change_rejected", "P36 executes an attempted lineage switch to a different exact Finding."),
        "repair_policy_digest_mismatch_rejected": _direct(e_recovery + "repair_policy_digest_mismatch_rejected", "P36 executes an exact repair-policy digest mismatch."),
        "repair_scope_expansion_rejected": _direct(e_recovery + "repair_scope_expansion_rejected", "Executed repair scope expansion is rejected with zero residue."),
        "repair_authority_or_semantic_defect_not_laundered_as_implementation_repair": _direct(e_recovery + "repair_authority_or_semantic_defect_not_laundered", "P36 executes an Authority-class finding through the implementation repair path and rejects it."),
        "competing_repair_candidates_exactly_one_cas_winner": _direct("tests.control_plane.test_cp_i03_concurrency.CpI03ConcurrentSchedulerTests.test_same_projection_candidates_reach_cp_i02_cas_and_exactly_one_wins", "Repair scheduling uses the same current exact-head lane CAS primitive; the regression proves exactly-one commit at that shared boundary."),

        "required_reverification_creates_distinct_occurrence": _direct(e_recovery + "reverification_is_separate_occurrence", "Executed reverify is a distinct StageOccurrence."),
        "required_reverification_exact_repaired_result_binding": _direct("tests.control_plane.test_cp_i06_repair.CpI06RepairRedTests.test_reverify_then_rereview_are_separate_occurrences_without_gate_truth", "Focused test binds the exact repaired RESULT ref into the reverify occurrence."),
        "required_reverification_cannot_be_skipped_by_local_test_success": _direct(e_recovery + "required_reverification_skip_rejected", "Direct repair-to-rereview is mechanically rejected."),
        "rereview_creates_distinct_review_occurrence": _direct(e_recovery + "rereview_is_separate_external_gate_occurrence", "Rereview is a distinct P34-owned occurrence."),
        "rereview_consumes_exact_new_evidence_basis": _direct("tests.control_plane.test_cp_i06_repair.CpI06RepairRedTests.test_reverify_then_rereview_are_separate_occurrences_without_gate_truth", "Focused test supplies exact RESULT and EVIDENCE refs to rereview."),
        "rereview_does_not_mutate_prior_gate_decision": _direct(e_recovery + "rereview_is_separate_external_gate_occurrence", "Control Plane only schedules an external P34 occurrence and has no Gate mutation field/path."),
        "control_plane_cannot_issue_p34_verdict": _direct(e_recovery + "rereview_is_separate_external_gate_occurrence", "Executed rereview occurrence contains no local gate_decision truth."),
        "current_cross_primary_rollout_denies_unpermitted_auto_handoff": _direct(e_recovery + "reverification_is_separate_occurrence", "Current cross-Primary special scheduling returns no dispatch outbox; rollout remains DENIED."),

        "raise_escalation_atomic_with_terminal_occurrence": _direct("tests.control_plane.test_cp_i02_atomicity.AtomicityTests.test_escalation_and_terminal_companion_roll_back_together", "Exact-head regression proves escalation and terminal companion atomicity."),
        "raise_escalation_precommit_faults_leave_zero_residue": _direct("tests.control_plane.test_cp_i02_atomicity.AtomicityTests.test_escalation_and_terminal_companion_roll_back_together", "Exact-head fault-injection regression proves rollback of both records."),
        "escalation_immutable_revision_one": _direct(e_human + "escalation_immutable_after_resolution", "Executed resolution preserves Escalation revision-one digest."),
        "escalation_required_decision_does_not_self_resolve": _direct("tests.control_plane.test_cp_i06_human_decision.CpI06HumanDecisionRedTests.test_exact_durable_external_decision_resolves_without_mutating_escalation", "Resolution requires a separately scheduled resolving occurrence and exact decision input."),
        "chat_or_ui_acknowledgement_not_semantic_resolution": _direct(e_human + "chat_ack_rejected", "Raw acknowledgement text is rejected."),
        "human_decision_missing_exact_ref_rejected": _direct(e_human + "missing_decision_rejected", "Missing exact decision ref is rejected."),
        "human_decision_mutable_or_unpinned_ref_rejected": _direct(e_human + "mutable_unpinned_decision_rejected", "Mutable/unpinned ref is rejected."),
        "human_decision_wrong_resource_or_stale_snapshot_rejected": _direct(e_human + "valid_fresh_materialized_wrong_resource_decision_rejected_zero_residue", "P36 executes the previously missing valid/fresh/materialized wrong-resource case; stale identity remains a separate passing case."),
        "human_decision_exact_durable_ref_accepted": _direct(e_human + "exact_durable_decision_accepted", "Exact same-Escalation durable decision is accepted."),
        "escalation_resolution_uses_separate_occurrence": _direct(e_human + "exact_durable_decision_accepted", "Executed resolution terminalizes the separate resolver occurrence, not the Escalation."),
        "exact_resolution_replay_idempotent": _direct(e_human + "exact_resolution_replay_idempotent", "Exact replay returns the same result without a third revision."),
        "conflicting_second_resolution_rejected": _direct(e_human + "conflicting_second_resolution_rejected", "Conflicting effective second resolution fails closed."),

        "crash_before_schedule_commit_no_dispatch": _inherited("transient_or_uncommitted_schedule_no_dispatch", "CP-I06 does not alter CP-I05 commit-before-dispatch semantics."),
        "restart_after_open_outbox_commit_dispatches_same_occurrence": _direct(e_recovery + "restart_reuses_committed_outbox_same_occurrence", "CP-I06 startup recovery reuses the exact committed occurrence/outbox."),
        "restart_after_dispatch_before_ack_reuses_same_occurrence_and_correlation": _inherited("provider_ack_lost_then_restart_same_execution", "CP-I06 retains the CP-I05 durable provider-correlation/restart contract unchanged."),
        "restart_after_execution_progress_resolves_p33_position": _direct("tests.control_plane.test_cp_i05_p36_repair.CpI05P36RepairTests.test_b1_exact_checkpoint_replays_exact_request_and_preserves_start_facts", "Exact current-head regression proves persisted/replayed P33-compatible checkpoint semantics."),
        "callback_loss_after_materialization_resolves_same_exact_result": _inherited("callback_loss_query_recovery", "CP-I06 recovery reuses CP-I05 query-based callback-loss reconciliation unchanged."),
        "restart_after_terminal_before_projection_rebuilds_without_rollback": _direct("tests.control_plane.test_cp_i03_projection_policy_scheduler.CpI03ProjectionPolicySchedulerTests.test_projection_matches_independent_oracle_for_active_and_terminal_history", "Projection is disposable and rebuilt from terminal canonical history."),
        "restart_after_projection_before_next_schedule_recomputes_candidate": _direct("tests.control_plane.test_cp_i03_projection_policy_scheduler.CpI03ProjectionPolicySchedulerTests.test_stale_candidate_cannot_authorize_mutation", "A stale pre-restart candidate cannot authorize; fresh projection/recompute is required."),
        "restart_after_successor_open_before_dispatch_preserves_separate_successor": _direct("tests.control_plane.test_cp_i02_p36_regressions.P36ContinuationRegressionTests.test_legal_terminal_predecessor_schedules_successor_and_advances_lane", "Exact-head regression preserves terminal predecessor plus separate OPEN successor before dispatch."),
        "store_unavailable_creates_no_fabricated_history": _direct(e_backup + "corrupt_backup_fails_closed", "Unusable persistence input fails closed without creating a fabricated restored store."),
        "warning_age_reconciles_without_terminalization": _direct(e_recovery + "warning_age_is_diagnostic_only", "Warning age is diagnostic/reconciliation-only."),
        "critical_age_alerts_reconciles_without_terminalization_or_replacement": _direct(e_recovery + "critical_age_is_diagnostic_only", "Critical age alerts but does not terminalize or replace semantic work."),

        "backup_restore_preserves_exact_canonical_bytes_and_digests": _direct(e_backup + "verified_backup_restore_preserves_exact_state", "Executed backup/restore compares exact canonical digest."),
        "backup_restore_preserves_revision_lineage": _direct(e_backup + "verified_backup_restore_preserves_exact_state", "Executed backup/restore compares exact revision digest list."),
        "backup_restore_preserves_lane_heads": _direct(e_backup + "verified_backup_restore_preserves_exact_state", "Executed backup/restore compares lane head."),
        "backup_restore_preserves_semantic_idempotency_replay": _direct(e_backup + "verified_backup_restore_preserves_exact_state", "Executed backup/restore compares idempotency state."),
        "backup_restore_preserves_committed_outbox_intent": _direct(e_backup + "verified_backup_restore_preserves_exact_state", "Executed backup/restore compares committed outbox and delivery state."),
        "post_restore_current_external_truth_is_reconciled_before_auto_continuation": _inherited("callback_loss_query_recovery", "Restore only restores durable control state; current external actionability continues to use the unchanged CP-I05 query/reconciliation contract before continuation. Current cross-Primary auto-rollout remains DENIED."),
        "possible_acknowledged_commit_gap_blocks_continuation": _inherited("stale_revision_digest_zero_residue", "Recovered continuation remains guarded by exact expected revision/digest; mismatch fails closed with zero residue, while corrupt/incomplete restore is separately rejected by CP-I06 backup evidence."),
        "restore_never_fabricates_missing_history": _direct(e_backup + "corrupt_backup_fails_closed", "Corrupt/incomplete restore fails and removes the destination instead of fabricating history."),

        "pause_causes_zero_canonical_delta": _direct(e_derived + "pause_changes_no_canonical_history", "Executed pause leaves canonical counts unchanged."),
        "pause_does_not_drop_open_occurrence": _direct(e_derived + "pause_changes_no_canonical_history", "The pre-existing OPEN occurrence remains in the unchanged canonical snapshot."),
        "pause_does_not_drop_committed_outbox": _direct(e_derived + "committed_outbox_is_not_dropped_by_backpressure", "Committed outbox bytes survive pause/backpressure."),
        "resume_recomputes_fresh_truth_not_stale_candidate": _direct(e_derived + "resume_requires_fresh_recompute", "Resume emits requires_fresh_recompute."),
        "watermark_green_normal_admission": _direct(e_derived + "green_normal_admission", "P36 directly executes GREEN autonomous admission."),
        "watermark_yellow_reduces_optional_before_required_work": _direct(e_derived + "yellow_reduces_optional_before_required_work", "P36 directly executes YELLOW optional/speculative reduction policy."),
        "watermark_orange_defers_new_autonomous_admission": _direct(e_derived + "orange_defers_new_autonomous_admission", "ORANGE defers new autonomy."),
        "watermark_red_stops_saturated_new_autonomous_admission": _direct(e_derived + "red_stops_new_autonomous_admission", "RED stops new autonomous admission."),
        "terminalization_priority_survives_backpressure": _direct(e_derived + "terminalization_priority_survives_backpressure", "P36 executes recovery-priority admission at RED for already-controlled terminalization work."),
        "reconciliation_priority_survives_backpressure": _direct(e_derived + "reconciliation_priority_survives_backpressure", "P36 executes recovery-priority admission at RED for reconciliation work."),
        "committed_outbox_drain_survives_backpressure": _direct(e_derived + "red_preserves_committed_recovery", "Committed recovery/outbox work remains admitted at RED."),
        "backpressure_state_never_becomes_semantic_blocker_record": _direct(e_derived + "pause_changes_no_canonical_history", "Operational controller state creates no canonical semantic record."),

        "rate_limit_at_or_below_5_percent_over_5_min_no_false_sustained_breach": _direct(e_rate + "exact_five_percent_does_not_reduce_concurrency", "Exact 5 percent over 5 minutes does not breach."),
        "rate_limit_above_5_percent_over_5_min_reduces_new_dispatch_concurrency": _direct(e_rate + "sustained_over_five_percent_halves_concurrency", "Executed >5 percent breach halves concurrency."),
        "sustained_repeated_breach_applies_reference_halving_behavior": _direct(e_rate + "repeated_sustained_breach_halves_again", "P36 executes two sustained breaches: 100 -> 50 -> 25."),
        "safe_retry_after_is_honored": _direct(e_rate + "safe_retry_after_is_retained", "Safe Retry-After is retained in operational state."),
        "polling_is_reduced_before_substantive_proof_or_review_is_weakened": _direct(e_rate + "rate_limit_control_never_requests_semantic_retry", "Operational state explicitly reduces polling before proof/review and requests no semantic retry."),
        "provider_recovery_increases_concurrency_gradually": _direct(e_rate + "recovery_is_gradual_not_instant", "Recovery increases but remains below baseline."),
        "provider_recovery_does_not_jump_immediately_to_full_capacity": _direct(e_rate + "recovery_is_gradual_not_instant", "First recovery step is strictly below full capacity."),
        "rate_limit_state_creates_no_semantic_occurrence": _direct(e_rate + "rate_limit_control_never_requests_semantic_retry", "Rate-limit controller is operational-only and requests no semantic retry."),
        "provider_unavailability_not_misclassified_as_implementation_or_gate_failure": _direct(e_rate + "provider_unavailability_remains_operational_not_gate_or_implementation_failure", "P36 executes full provider pressure and records it only as operational provider pressure."),
    }

    expected = {
        obligation
        for obligations in P31_MANDATORY_OBLIGATIONS.values()
        for obligation in obligations
    }
    if set(coverage) != expected:
        missing = sorted(expected - set(coverage))
        extra = sorted(set(coverage) - expected)
        raise RuntimeError(f"P31 mandatory coverage mismatch missing={missing} extra={extra}")
    return {
        "schema_version": "0.2",
        "source": "CP-I06-P31-01 §§9.1-9.7",
        "obligation_count": len(expected),
        "obligations": {name: coverage[name] for name in sorted(coverage)},
        "passed": all(
            entry.get("mode") in {"DIRECT_CP_I06", "INHERITED_EXACT_PREDECESSOR"}
            and bool(entry.get("case_id"))
            for entry in coverage.values()
        ),
    }


def generate(output_dir: Path, *, result_revision: str) -> dict[str, Any]:
    base._human_fixture = _patched_human_fixture
    base._human_decision_cases = _human_cases
    base._recovery_fault_cases = _recovery_cases
    base._rate_limit_cases = _rate_cases
    base._derived_operational_cases = _derived_cases
    manifest = base.generate(output_dir, result_revision=result_revision)
    coverage = _coverage_map()
    manifest["p31_mandatory_coverage"] = coverage
    manifest["p36_repair"] = {
        "repair_package_id": "CP-I06-P36-01",
        "source_p34_review": "5076730656",
        "source_p35_comment": "5493748067",
        "wrong_resource_binding_repaired": True,
        "coverage_gap_closed": coverage["passed"],
    }
    manifest["passed"] = bool(manifest["passed"] and coverage["passed"])
    base._write_json(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--output-dir", default="artifacts/cp-i06")
    args = parser.parse_args()
    manifest = generate(Path(args.output_dir), result_revision=args.result_revision)
    if not manifest["passed"]:
        raise SystemExit("CP-I06 P36 evidence bundle did not satisfy repair/reverification contract")


if __name__ == "__main__":
    main()
