import json
import tempfile
import unittest
from pathlib import Path

from evals.scripts.aegis_eval.adapters import RecordedAdapter
from evals.scripts.aegis_eval.runner import evaluate_cases


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "id": "routing-001",
            "category": "routing",
            "severity": "high",
            "expected": {
                "status": "READY",
                "earliest_untrusted_layer": "problem",
                "start_stage": "P00",
                "required_stages": ["P00"],
                "forbidden_stages": ["P32"],
                "authority_classification": [],
                "defect_classification": None,
                "gate_verdict": None,
            },
        }
        self.result = {
            "status": "READY_TO_ROUTE",
            "earliest_untrusted_layer": "problem",
            "start_stage": "P00",
            "route": ["P00"],
            "authority_classification": [],
            "defect_classification": None,
            "gate_verdict": None,
            "findings": ["problem not validated"],
            "evidence_requirements": [],
        }

    def test_recorded_adapter_pipeline_writes_evidence_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            recorded = root / "recorded.json"
            recorded.write_text(json.dumps({"routing-001": self.result}), encoding="utf-8")
            out = root / "out"
            summary = evaluate_cases([self.case], RecordedAdapter(recorded), out)

            self.assertEqual(summary["overall_weighted_score"], 1.0)
            self.assertTrue(summary["deterministic_gate_pass"])
            self.assertEqual(summary["behavioral_gate_status"], "BLOCKED_EVIDENCE")
            self.assertTrue((out / "raw" / "routing-001.txt").exists())
            self.assertTrue((out / "normalized" / "routing-001.json").exists())
            self.assertTrue((out / "summary.json").exists())
            self.assertTrue((out / "report.md").exists())

    def test_semantic_pass_flag_cannot_promote_without_evidence_contract(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            recorded = root / "recorded.json"
            recorded.write_text(json.dumps({"routing-001": self.result}), encoding="utf-8")
            with self.assertRaises(ValueError):
                evaluate_cases(
                    [self.case],
                    RecordedAdapter(recorded),
                    root / "out",
                    semantic_evidence_status="PASS",
                )

    def test_recorded_adapter_requires_every_case(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            recorded = root / "recorded.json"
            recorded.write_text("{}", encoding="utf-8")
            with self.assertRaises(KeyError):
                evaluate_cases([self.case], RecordedAdapter(recorded), root / "out")


if __name__ == "__main__":
    unittest.main()
