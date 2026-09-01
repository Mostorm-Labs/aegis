import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.augment_cp_i05_p36_evidence import augment_evidence_bundle
from tests.control_plane.generate_cp_i05_evidence import build_evidence_bundle


EXPECTED_DISPATCH_CASES = {
    "committed_outbox_dispatch",
    "transient_or_uncommitted_schedule_no_dispatch",
    "schedule_crash_after_canonical",
    "schedule_crash_after_lane",
    "schedule_crash_after_outbox",
    "schedule_crash_after_idempotency",
    "operational_delivery_metadata_no_canonical_change",
    "duplicate_transport_same_occurrence",
    "provider_ack_lost_then_restart_same_execution",
    "unauthorized_cross_primary_no_provider_request",
    "noncurrent_authorization_no_provider_request",
    "provider_ack_not_completion",
    "callback_loss_query_recovery",
    "delivery_uncertain_boundary_no_replacement_occurrence",
    "provider_running_to_materialized_exact_result",
    "duplicate_callback_no_duplicate_terminal_revision",
    "worker_restart_reuses_durable_correlation",
}
EXPECTED_RESULT_CASES = {
    "exact_result_resolved",
    "missing_result",
    "inaccessible_result",
    "local_only_unreviewable_result",
    "mutable_unpinned_result",
    "result_identity_mismatch",
    "ambiguous_result_resolution",
    "occurrence_lineage_mismatch",
    "package_lineage_mismatch",
    "task_anchor_lineage_mismatch",
}
EXPECTED_PROGRESS_CASES = {
    "exact_checkpoint_applied",
    "execution_navigation_only_delta",
    "exact_idempotent_progress_replay",
    "unreconciled_descendant_checkpoint_rejected",
    "flat_or_unknown_navigation_rejected",
    "wrong_task_anchor_rejected",
    "stale_revision_digest_zero_residue",
    "competing_checkpoints_one_winner",
}
EXPECTED_EDGE_CASES = {
    "configured_boundary_no_progress_still_requires_exact_result",
    "thirty_minute_uncertainty_persists_without_replacement_occurrence",
}
EXPECTED_METRICS = {
    "age_only_terminalization",
    "dispatch_before_commit",
    "diverged_resume_accepted",
    "duplicate_terminal_revision",
    "semantic_occurrence_amplification_from_duplicate_transport",
    "unauthorized_cross_primary_provider_request",
    "unreviewable_result_accepted_as_complete",
    "valid_descendant_resume_replayed_completed_work",
    "worker_direct_canonical_writes",
}


class CpI05EvidenceTests(unittest.TestCase):
    def _assert_exact_unique_cases(self, expected, cases):
        names = [case["case"] for case in cases]
        self.assertEqual(expected, set(names))
        self.assertEqual(len(names), len(set(names)), "duplicate mandatory evidence case")
        for case in cases:
            self.assertIs(case.get("pass"), True, case["case"])

    def test_exact_evidence_families_cases_repair_lineage_and_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            result_revision = "f" * 40
            package_ref = "d1e76563385bd03747aef2ee396855ec26496679"
            build_evidence_bundle(
                result_revision=result_revision,
                package_ref=package_ref,
                output_dir=output,
            )
            manifest = augment_evidence_bundle(output_dir=output)

            expected_files = {
                "dispatch-fault-matrix.json",
                "resume-corpus.json",
                "delivery-policy.json",
                "reconciliation-policy.json",
                "p36-edge-closure.json",
                "evidence-manifest.json",
            }
            self.assertEqual(expected_files, {path.name for path in output.glob("*.json")})
            self.assertEqual("CP-I05-P31-01", manifest["package_id"])
            self.assertEqual(package_ref, manifest["package_ref"])
            self.assertEqual("CP-I05-P36-01", manifest["repair_package_id"])
            self.assertEqual(result_revision, manifest["result_revision"])
            self.assertEqual(
                {"revision": "a3fd350c350bec9220a1c6e283de88c14dfbcd2a", "relation": "ancestor"},
                manifest["task_anchor"],
            )
            self.assertEqual("5486917398", manifest["source_cp_i04_p34_comment"])
            expected_repair_lineage = {
                "source_p34_comment": "5488464223",
                "source_p35_classification_comment": "5489296080",
                "source_revision": "033637a5be7cb04bb60f0d8176e48130027b9b93",
            }
            self.assertEqual(expected_repair_lineage, manifest["repair_lineage"])
            self.assertEqual(EXPECTED_METRICS, set(manifest["metrics"]))
            self.assertTrue(all(value == 0 for value in manifest["metrics"].values()))
            self.assertIs(manifest["passed"], True)
            self.assertEqual(
                {
                    "p34_gate_pass": False,
                    "evidence_compiler_gate_authority": False,
                    "cp_i06_plus": False,
                    "current_cross_primary_rollout": "DENIED",
                },
                manifest["claims"],
            )

            declared = {entry["file"]: entry for entry in manifest["evidence_files"]}
            self.assertEqual(expected_files - {"evidence-manifest.json"}, set(declared))
            self.assertEqual(
                {
                    "CPV-E-DISPATCH-FAULT-MATRIX",
                    "CPV-E-RESUME-CORPUS",
                    "CPV-E-DELIVERY-POLICY",
                    "CPV-E-RECONCILIATION-POLICY",
                    "CP-I05-P36-EDGE-CLOSURE",
                },
                {entry["evidence_family"] for entry in declared.values()},
            )
            for filename, entry in declared.items():
                data = (output / filename).read_bytes()
                self.assertEqual("sha256:" + hashlib.sha256(data).hexdigest(), entry["digest"])
                self.assertIs(entry["passed"], True)

            dispatch = json.loads((output / "dispatch-fault-matrix.json").read_text())
            self.assertEqual("CPV-E-DISPATCH-FAULT-MATRIX", dispatch["evidence_family"])
            self.assertEqual("CP-I05-P36-01", dispatch["repair_package_id"])
            self._assert_exact_unique_cases(EXPECTED_DISPATCH_CASES, dispatch["cases"])
            self._assert_exact_unique_cases(EXPECTED_RESULT_CASES, dispatch["result_cases"])
            self._assert_exact_unique_cases(EXPECTED_PROGRESS_CASES, dispatch["progress_cases"])

            for case in dispatch["cases"]:
                if case["case"].startswith("schedule_crash_"):
                    self.assertIs(case["zero_residue"], True)
                    self.assertEqual(0, case["provider_request_count"])
            for case in dispatch["result_cases"]:
                if case["case"] != "exact_result_resolved":
                    self.assertIs(case["zero_residue"], True)
                    self.assertEqual("OPEN", case["final_state"])
            for case in dispatch["progress_cases"]:
                if case["case"] in {
                    "unreconciled_descendant_checkpoint_rejected",
                    "flat_or_unknown_navigation_rejected",
                    "wrong_task_anchor_rejected",
                    "stale_revision_digest_zero_residue",
                }:
                    self.assertIs(case["zero_residue"], True)

            edge = json.loads((output / "p36-edge-closure.json").read_text())
            self.assertEqual("CP-I05-P36-EDGE-CLOSURE", edge["evidence_family"])
            self.assertEqual("CP-I05-P36-01", edge["repair_package_id"])
            self.assertEqual(expected_repair_lineage, edge["repair_lineage"])
            self.assertEqual(result_revision, edge["result_revision"])
            self._assert_exact_unique_cases(EXPECTED_EDGE_CASES, edge["cases"])
            self.assertIs(edge["passed"], True)

            resume = json.loads((output / "resume-corpus.json").read_text())
            states = [case["state"] for case in resume["cases"]]
            self.assertEqual(
                {
                    "EXACT_CURSOR",
                    "DESCENDANT_CURSOR",
                    "ANCHOR_DESCENDANT_WITHOUT_CURSOR",
                    "DIVERGED",
                },
                set(states),
            )
            self.assertEqual(len(states), len(set(states)))
            self.assertTrue(all(case["pass"] for case in resume["cases"]))
            self.assertTrue(all(not case["replay_completed_work"] for case in resume["cases"]))
            diverged = next(case for case in resume["cases"] if case["state"] == "DIVERGED")
            self.assertEqual("BLOCKED_EXECUTION_DIVERGENCE", diverged["blocker"])

            delivery = json.loads((output / "delivery-policy.json").read_text())
            self.assertEqual([1, 2, 4, 8, 16, 30, 60, 300], delivery["retry_delays_seconds"])
            self.assertEqual(
                {"before_boundary": False, "attempt_12": True, "minute_30": True},
                delivery["boundary_cases"],
            )
            self.assertEqual(0, delivery["semantic_replacement_occurrences"])
            self.assertIs(delivery["passed"], True)

            reconciliation = json.loads((output / "reconciliation-policy.json").read_text())
            self.assertEqual(
                [
                    [0, 30, False],
                    [299, 30, False],
                    [300, 120, False],
                    [1799, 120, False],
                    [1800, 300, False],
                    [7199, 300, False],
                    [7200, 900, True],
                ],
                [
                    [case["age_seconds"], case["interval_seconds"], case["operator_alert"]]
                    for case in reconciliation["cases"]
                ],
            )
            self.assertTrue(all(not case["semantic_terminalization"] for case in reconciliation["cases"]))
            self.assertIs(reconciliation["passed"], True)


if __name__ == "__main__":
    unittest.main()
