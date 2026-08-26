import json
import unittest

from evals.scripts.aegis_eval.normalize import normalize_raw_result


class NormalizeTests(unittest.TestCase):
    def test_normalizes_ready_to_route_alias_to_ready(self):
        raw = json.dumps({
            "case_id": "routing-001",
            "status": "READY_TO_ROUTE",
            "earliest_untrusted_layer": "problem",
            "start_stage": "P00",
            "route": ["P00"],
            "authority_classification": [],
            "defect_classification": None,
            "gate_verdict": None,
            "findings": [],
            "evidence_requirements": [],
        })
        result = normalize_raw_result("routing-001", raw)
        self.assertEqual(result["status"], "READY")

    def test_extracts_json_from_fenced_block(self):
        raw = '''Analysis text
```json
{"status":"BLOCKED_EVIDENCE","start_stage":"P34","route":["P34"]}
```
'''
        result = normalize_raw_result("gate-002", raw)
        self.assertEqual(result["case_id"], "gate-002")
        self.assertEqual(result["status"], "BLOCKED_EVIDENCE")
        self.assertEqual(result["start_stage"], "P34")
        self.assertEqual(result["route"], ["P34"])

    def test_rejects_unstructured_text(self):
        with self.assertRaises(ValueError):
            normalize_raw_result("routing-001", "I think P00 is right")


if __name__ == "__main__":
    unittest.main()
