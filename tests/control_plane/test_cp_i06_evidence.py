from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.generate_cp_i06_evidence import (
    CP_I05_EVIDENCE_ARTIFACT_ID,
    CP_I05_P34_COMMENT,
    CP_I05_REVISION,
    PACKAGE_ID,
    PACKAGE_REF,
    TASK_ANCHOR,
    generate,
)


EXPECTED_FILES = {
    "human-decision.json",
    "recovery-fault-matrix.json",
    "backup-restore.json",
    "rate-limit-control.json",
    "derived-operational-state.json",
    "evidence-manifest.json",
}
EXPECTED_FAMILIES = {
    "CPV-E-HUMAN-DECISION",
    "CPV-E-RECOVERY-FAULT-MATRIX",
    "CPV-E-BACKUP-RESTORE",
    "CPV-E-RATE-LIMIT-CONTROL",
    "CPV-E-DERIVED-STATE",
}
EXPECTED_METRICS = {
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
EXPECTED_CASES = {
    "CPV-E-HUMAN-DECISION": {
        "exact_durable_decision_accepted",
        "missing_decision_rejected",
        "chat_ack_rejected",
        "boolean_ack_rejected",
        "mutable_unpinned_decision_rejected",
        "stale_decision_rejected",
        "wrong_unmaterialized_decision_rejected",
        "escalation_immutable_after_resolution",
        "exact_resolution_replay_idempotent",
        "conflicting_second_resolution_rejected",
    },
    "CPV-E-RECOVERY-FAULT-MATRIX": {
        "process_replacement_preserves_acknowledged_commit",
        "restart_reuses_committed_outbox_same_occurrence",
        "restart_with_correlation_reconciles_same_occurrence",
        "warning_age_is_diagnostic_only",
        "critical_age_is_diagnostic_only",
        "repair_attempts_are_new_contiguous_occurrences",
        "repair_lineage_gap_rejected",
        "repair_budget_exhaustion_rejected",
        "repair_scope_expansion_rejected",
        "required_reverification_skip_rejected",
        "reverification_is_separate_occurrence",
        "rereview_is_separate_external_gate_occurrence",
    },
    "CPV-E-BACKUP-RESTORE": {
        "verified_backup_restore_preserves_exact_state",
        "corrupt_backup_fails_closed",
    },
    "CPV-E-RATE-LIMIT-CONTROL": {
        "exact_five_percent_does_not_reduce_concurrency",
        "sustained_over_five_percent_halves_concurrency",
        "safe_retry_after_is_retained",
        "recovery_is_gradual_not_instant",
        "rate_limit_control_never_requests_semantic_retry",
    },
    "CPV-E-DERIVED-STATE": {
        "backpressure_watermarks_match_p18",
        "pause_changes_no_canonical_history",
        "resume_requires_fresh_recompute",
        "orange_defers_new_autonomous_admission",
        "red_stops_new_autonomous_admission",
        "red_preserves_committed_recovery",
        "manual_duplicate_fallback_is_denied",
        "committed_outbox_is_not_dropped_by_backpressure",
    },
}


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class CpI06EvidenceContractTests(unittest.TestCase):
    def test_exact_bundle_families_cases_metrics_provenance_and_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            result_revision = "a" * 40
            manifest = generate(output, result_revision=result_revision)

            self.assertEqual(EXPECTED_FILES, {path.name for path in output.iterdir() if path.is_file()})
            materialized = _load(output / "evidence-manifest.json")
            self.assertEqual(manifest, materialized)

            self.assertEqual("0.2", materialized["schema_version"])
            self.assertEqual("CP-I06_EVIDENCE_MANIFEST", materialized["kind"])
            self.assertEqual(PACKAGE_ID, materialized["package_id"])
            self.assertEqual(PACKAGE_REF, materialized["package_ref"])
            self.assertEqual(result_revision, materialized["result_revision"])
            self.assertEqual(TASK_ANCHOR, materialized["task_anchor"])
            self.assertEqual(
                {
                    "cp_i05_revision": CP_I05_REVISION,
                    "cp_i05_p34_comment": CP_I05_P34_COMMENT,
                    "cp_i05_evidence_artifact_id": CP_I05_EVIDENCE_ARTIFACT_ID,
                },
                materialized["predecessor"],
            )

            evidence_files = materialized["evidence_files"]
            self.assertEqual(5, len(evidence_files))
            self.assertEqual(EXPECTED_FAMILIES, {entry["evidence_family"] for entry in evidence_files})
            self.assertEqual(5, len({entry["file"] for entry in evidence_files}))
            self.assertEqual(5, len({entry["evidence_family"] for entry in evidence_files}))

            for entry in evidence_files:
                path = output / entry["file"]
                self.assertTrue(path.is_file(), entry)
                self.assertEqual(_sha256(path), entry["digest"])
                self.assertTrue(entry["passed"], entry)
                evidence = _load(path)
                self.assertEqual(entry["evidence_family"], evidence["evidence_family"])
                self.assertTrue(evidence["passed"])
                case_names = {case["case"] for case in evidence["cases"]}
                self.assertEqual(EXPECTED_CASES[evidence["evidence_family"]], case_names)
                self.assertEqual(len(case_names), len(evidence["cases"]))
                self.assertTrue(all(case["passed"] for case in evidence["cases"]))

            self.assertEqual(EXPECTED_METRICS, set(materialized["metrics"]))
            self.assertTrue(all(value == 0 for value in materialized["metrics"].values()))
            self.assertEqual(
                {
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
                materialized["claims"],
            )
            self.assertTrue(materialized["passed"])

    def test_manifest_pass_is_derived_from_case_level_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            manifest = generate(output, result_revision="b" * 40)
            self.assertTrue(manifest["passed"])
            for entry in manifest["evidence_files"]:
                evidence = _load(output / entry["file"])
                self.assertEqual(
                    all(case["passed"] for case in evidence["cases"]),
                    evidence["passed"],
                )


if __name__ == "__main__":
    unittest.main()
