import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.generate_cp_i05_evidence import build_evidence_bundle


class CpI05EvidenceTests(unittest.TestCase):
    def test_exact_evidence_families_cases_and_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            result_revision = "f" * 40
            package_ref = "d1e76563385bd03747aef2ee396855ec26496679"
            manifest = build_evidence_bundle(
                result_revision=result_revision,
                package_ref=package_ref,
                output_dir=output,
            )

            expected_files = {
                "dispatch-fault-matrix.json",
                "resume-corpus.json",
                "delivery-policy.json",
                "reconciliation-policy.json",
                "evidence-manifest.json",
            }
            self.assertEqual(expected_files, {path.name for path in output.glob("*.json")})
            self.assertEqual("CP-I05-P31-01", manifest["package_id"])
            self.assertEqual(package_ref, manifest["package_ref"])
            self.assertEqual(result_revision, manifest["result_revision"])
            self.assertEqual(
                "a3fd350c350bec9220a1c6e283de88c14dfbcd2a",
                manifest["task_anchor"]["revision"],
            )
            self.assertEqual("ancestor", manifest["task_anchor"]["relation"])
            self.assertEqual("5486917398", manifest["source_cp_i04_p34_comment"])
            self.assertFalse(manifest["claims"]["p34_gate_pass"])
            self.assertFalse(manifest["claims"]["cp_i06_plus"])
            self.assertEqual("DENIED", manifest["claims"]["current_cross_primary_rollout"])
            self.assertTrue(all(value == 0 for value in manifest["metrics"].values()))

            declared = {entry["file"]: entry for entry in manifest["evidence_files"]}
            self.assertEqual(expected_files - {"evidence-manifest.json"}, set(declared))
            for filename, entry in declared.items():
                data = (output / filename).read_bytes()
                self.assertEqual("sha256:" + hashlib.sha256(data).hexdigest(), entry["digest"])

            dispatch = json.loads((output / "dispatch-fault-matrix.json").read_text())
            self.assertEqual(
                {
                    "committed_outbox_dispatch",
                    "duplicate_transport_same_occurrence",
                    "missing_outbox_no_dispatch",
                    "unauthorized_dispatch_no_provider_request",
                    "provider_ack_not_completion",
                    "callback_loss_query_recovery",
                    "exact_result_materialization_required",
                    "exact_result_materialization_bound",
                },
                {case["case"] for case in dispatch["cases"]},
            )
            for case in dispatch["cases"]:
                self.assertIn("pass", case)
                self.assertTrue(case["pass"])

            resume = json.loads((output / "resume-corpus.json").read_text())
            self.assertEqual(
                {
                    "EXACT_CURSOR",
                    "DESCENDANT_CURSOR",
                    "ANCHOR_DESCENDANT_WITHOUT_CURSOR",
                    "DIVERGED",
                },
                {case["state"] for case in resume["cases"]},
            )
            self.assertTrue(all(not case["replay_completed_work"] for case in resume["cases"]))
            diverged = next(case for case in resume["cases"] if case["state"] == "DIVERGED")
            self.assertEqual("BLOCKED_EXECUTION_DIVERGENCE", diverged["blocker"])

            delivery = json.loads((output / "delivery-policy.json").read_text())
            self.assertEqual([1, 2, 4, 8, 16, 30, 60, 300], delivery["retry_delays_seconds"])
            self.assertFalse(delivery["boundary_cases"]["before_boundary"])
            self.assertTrue(delivery["boundary_cases"]["attempt_12"])
            self.assertTrue(delivery["boundary_cases"]["minute_30"])
            self.assertEqual(0, delivery["semantic_replacement_occurrences"])

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


if __name__ == "__main__":
    unittest.main()
