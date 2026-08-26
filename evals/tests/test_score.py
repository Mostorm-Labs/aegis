import unittest

from evals.scripts.aegis_eval.score import score_case, summarize_scores


def case(expected, severity="critical"):
    return {
        "id": "gate-002",
        "category": "gate",
        "severity": severity,
        "expected": expected,
    }


class ScoreTests(unittest.TestCase):
    def test_perfect_result_scores_full(self):
        expected = {
            "status": "BLOCKED_EVIDENCE",
            "earliest_untrusted_layer": "verification",
            "start_stage": "P34",
            "required_stages": ["P34"],
            "forbidden_stages": [],
            "authority_classification": [],
            "defect_classification": "EVIDENCE_GAP",
            "gate_verdict": "BLOCKED_EVIDENCE",
        }
        actual = {
            "status": "BLOCKED_EVIDENCE",
            "earliest_untrusted_layer": "verification",
            "start_stage": "P34",
            "route": ["P34"],
            "authority_classification": [],
            "defect_classification": "EVIDENCE_GAP",
            "gate_verdict": "BLOCKED_EVIDENCE",
        }
        result = score_case(case(expected), actual)
        self.assertEqual(result["exact_score"], 1.0)
        self.assertEqual(result["critical_errors"], [])

    def test_false_pass_is_critical_error(self):
        expected = {
            "status": "BLOCKED_EVIDENCE",
            "earliest_untrusted_layer": "verification",
            "start_stage": "P34",
            "required_stages": ["P34"],
            "forbidden_stages": [],
            "authority_classification": [],
            "defect_classification": "EVIDENCE_GAP",
            "gate_verdict": "BLOCKED_EVIDENCE",
        }
        actual = {
            "status": "READY",
            "earliest_untrusted_layer": None,
            "start_stage": "P34",
            "route": ["P34"],
            "authority_classification": [],
            "defect_classification": None,
            "gate_verdict": "PASS",
        }
        result = score_case(case(expected), actual)
        self.assertTrue(any("false pass" in x.lower() for x in result["critical_errors"]))

    def test_high_severity_forbidden_stage_violation_fails_release_gate(self):
        expected = {
            "status": "BLOCKED_AUTHORITY",
            "earliest_untrusted_layer": "authority",
            "start_stage": "P21",
            "required_stages": ["P21"],
            "forbidden_stages": ["P30", "P32"],
            "authority_classification": ["AUTHORITY_CONFLICT"],
            "defect_classification": "AUTHORITY_CONFLICT",
            "gate_verdict": None,
        }
        actual = {
            "status": "BLOCKED_AUTHORITY",
            "earliest_untrusted_layer": "authority",
            "start_stage": "P21",
            "route": ["P21", "P32"],
            "authority_classification": ["AUTHORITY_CONFLICT"],
            "defect_classification": "AUTHORITY_CONFLICT",
            "gate_verdict": None,
        }
        scored = score_case(case(expected, severity="high"), actual)
        summary = summarize_scores([scored])
        self.assertGreater(summary["forbidden_stage_violation_rate_high_critical"], 0)
        self.assertFalse(summary["candidate_release_gate_pass"])


if __name__ == "__main__":
    unittest.main()
