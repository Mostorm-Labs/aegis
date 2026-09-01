from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


class CpI08EvidenceRedTests(unittest.TestCase):
    def test_exact_eight_file_bundle_and_zero_tolerance_manifest(self):
        from tests.control_plane.generate_cp_i08_evidence import materialize_evidence

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = materialize_evidence(result_revision="f" * 40, output_dir=root, workflow_run="test-run")
            expected = {
                "d0-conformance.json",
                "verifier-qualification.json",
                "retention-replay.json",
                "observability-cost.json",
                "operational-retention.json",
                "alerting-conformance.json",
                "availability-evaluator-qualification.json",
                "evidence-manifest.json",
            }
            self.assertEqual(expected, {p.name for p in root.glob("*.json")})
            self.assertTrue(manifest["passed"])
            self.assertEqual(44, manifest["d0"]["golden_passed"])
            self.assertEqual(20, manifest["qualification"]["detected"])
            self.assertEqual(0, manifest["qualification"]["false_acceptance"])
            self.assertTrue(all(value == 0 for value in manifest["metrics"].values()))
            self.assertFalse(manifest["claims"]["p34_gate_pass"])
            self.assertFalse(manifest["claims"]["cp_i09_plus"])
            self.assertFalse(manifest["claims"]["monthly_availability_attainment"])
            for path in root.glob("*.json"):
                json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__": unittest.main()
