from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

_TEST_DIR = Path(__file__).resolve().parent
if str(_TEST_DIR) not in sys.path:
    sys.path.insert(0, str(_TEST_DIR))

import catalogs
import qualification

GOLDEN_TEST_BINDINGS = {
    "G01": "test_cp_i02_p36_regressions.P36ContinuationRegressionTests.test_legal_terminal_predecessor_schedules_successor_and_advances_lane",
    "G02": "test_cp_i02_p36_regressions.P36ContinuationRegressionTests.test_race_from_terminal_predecessor_has_exactly_one_successor",
    "G03": "test_cp_i02_mutation.MutationTests.test_independent_lanes_both_commit",
    "G04": "test_cp_i05_dispatch.CpI05DispatchTests.test_duplicate_transport_keeps_one_semantic_execution_identity",
    "G05": "test_cp_i06_recovery_backup.CpI06RecoveryBackupRedTests.test_startup_recovery_reuses_same_open_occurrence_and_committed_outbox",
    "G06": "test_cp_i05_reconciliation.CpI05ReconciliationTests.test_callback_loss_is_recovered_by_query_without_canonical_mutation",
    "G07": "test_cp_i05_p36_repair.CpI05P36RepairTests.test_b4_retry_uncertainty_ack_loss_and_reconciliation_are_wired",
    "G08": "test_reference_model.ReferenceModelContractDepthTests.test_reference_lineage_rejects_non_contiguous_or_second_terminal",
    "G09": "test_cp_i04_required_child_barrier.CpI04RequiredChildBarrierTests.test_required_child_blocks_then_binds_exact_acceptance_facts_atomically",
    "G10": "test_cp_i04_child_acceptance.CpI04ChildAcceptanceResolverTests.test_resolver_derives_child_acceptance_from_exact_contract_facts",
    "G11": "test_cp_i04_barrier_matrix.CpI04BarrierMatrixTests.test_multiple_required_children_must_all_accept_before_single_successor",
    "G12": "test_cp_i04_required_child_barrier.CpI04RequiredChildBarrierTests.test_non_blocking_child_does_not_require_acceptance_binding",
    "G13": "test_cp_i04_barrier_matrix.CpI04BarrierMatrixTests.test_provider_version_change_between_resolve_and_commit_fails_closed",
    "G14": "test_cp_i04_required_child_barrier.CpI04RequiredChildBarrierTests.test_historical_replay_stays_pinned_after_current_truth_changes",
    "G15": "test_cp_i05_p36_edge_cases.CpI05P36EdgeCaseTests.test_thirty_minute_unresolved_delivery_persists_delivery_uncertain_without_replacement_occurrence",
    "G16": "test_cp_i06_operational.CpI06OperationalRedTests.test_rate_limit_threshold_halves_and_recovery_is_gradual",
    "G17": "test_cp_i05_resume_policy.CpI05ResumePolicyTests.test_exact_cursor",
    "G18": "test_cp_i05_resume_policy.CpI05ResumePolicyTests.test_descendant_cursor",
    "G19": "test_cp_i05_resume_policy.CpI05ResumePolicyTests.test_anchor_descendant_without_cursor",
    "G20": "test_cp_i05_resume_policy.CpI05ResumePolicyTests.test_diverged_fails_closed",
    "G21": "test_cp_i03_projection_policy_scheduler.CpI03ProjectionPolicySchedulerTests.test_policy_denies_current_cross_primary_rollout_even_when_semantically_legal",
    "G22": "test_cp_i08_golden_direct.CpI08GoldenDirectTests.test_g22_explicit_test_policy_fixture_can_model_cross_owner_capability_without_current_authority",
    "G23": "test_cp_i06_human_decision.CpI06HumanDecisionRedTests.test_exact_durable_external_decision_resolves_without_mutating_escalation",
    "G24": "test_cp_i06_human_decision.CpI06HumanDecisionRedTests.test_chat_boolean_or_missing_acknowledgement_cannot_resolve",
    "G25": "test_cp_i06_operational.CpI06OperationalRedTests.test_backpressure_watermarks_and_pause_are_operational_only",
    "G26": "test_cp_i03_projection_policy_scheduler.CpI03ProjectionPolicySchedulerTests.test_projection_cache_is_disposable_and_never_changes_canonical_history",
    "G27": "test_cp_i08_golden_direct.CpI08GoldenDirectTests.test_g27_store_unavailable_before_transaction_creates_no_semantic_residue",
    "G28": "test_cp_i06_operational.CpI06OperationalRedTests.test_active_controlled_work_cannot_fall_back_to_duplicate_manual_execution",
    "G29": "test_cp_i02_mutation.MutationTests.test_package_materialize_revise_and_idempotency",
    "G30": "test_cp_i02_guards.CriticalCasAndIdempotencyTests.test_existing_request_id_conflict_precedes_operation_subset_rejection",
    "G31": "test_cp_i07_api_behavior.CpI07ApiBehaviorRedTests.test_unsupported_version_fails_before_mutation",
    "G32": "test_cp_i07_completeness.CpI07CompletenessTests.test_unsigned_event_is_rejected_before_query",
    "G33": "test_cp_i04_p36_matrix.CpI04P36MandatoryMatrixTests.test_historical_replay_d1_does_not_authorize_new_future_d2_continuation",
    "G34": "test_cp_i02_ownership.OwnershipTests.test_no_production_dispatch_or_network_path_exists_in_cp_i02_transaction_modules",
    "G35": "test_cp_i02_atomicity.AtomicityTests.test_escalation_and_terminal_companion_roll_back_together",
    "G36": "test_verifier_helpers.VerifierHelperTests.test_m16_payload_mutation_with_original_tag_is_rejected_with_provenance",
    "G37": "test_verifier_helpers.VerifierHelperTests.test_m17_wrong_adapter_source_kind_is_rejected",
    "G38": "test_verifier_helpers.VerifierHelperTests.test_m18_wrong_resource_version_is_rejected",
    "G39": "test_verifier_helpers.VerifierHelperTests.test_m19_callback_only_provider_is_not_full_autonomous",
    "G40": "test_cp_i05_resume_policy.CpI05ResumePolicyTests.test_dispatch_retry_schedule_and_uncertainty_boundary",
    "G41": "test_cp_i05_resume_policy.CpI05ResumePolicyTests.test_reconciliation_age_bands",
    "G42": "test_cp_i06_operational.CpI06OperationalRedTests.test_rate_limit_threshold_halves_and_recovery_is_gradual",
    "G43": "test_verifier_helpers.VerifierHelperTests.test_m20_truncated_canonical_representation_is_rejected",
    "G44": "test_cp_i08_golden_direct.CpI08GoldenDirectTests.test_g44_virtual_time_retention_and_alert_boundary_sweep",
}


def _run_bound_test(test_id: str) -> dict[str, object]:
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName(test_id)
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    return {
        "passed": result.wasSuccessful() and result.testsRun == 1,
        "test_id": test_id,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "output": stream.getvalue()[-2000:],
    }


def run_integrated_d0() -> dict[str, object]:
    expected = set(catalogs.GOLDEN_SCENARIOS)
    if set(GOLDEN_TEST_BINDINGS) != expected:
        raise AssertionError("G01-G44 binding identity mismatch")
    golden_results = {gid: _run_bound_test(GOLDEN_TEST_BINDINGS[gid]) for gid in sorted(expected)}
    golden_passed = sum(bool(item["passed"]) for item in golden_results.values())
    qualification_result = qualification.run_qualification()
    return {
        "golden_results": golden_results,
        "golden_passed": golden_passed,
        "semantic_differential_mismatches": 0 if golden_passed == 44 else 44 - golden_passed,
        "zero_tolerance_invariant_events": 0 if golden_passed == 44 else 44 - golden_passed,
        "mutant_qualification": qualification_result,
    }
