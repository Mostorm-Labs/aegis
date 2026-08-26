import json
import unittest
from pathlib import Path

from evals.scripts.aegis_eval.score import score_case, summarize_scores


ROOT = Path(__file__).resolve().parents[2]


def load_cases():
    cases = []
    for path in sorted((ROOT / "evals" / "cases").glob("*.json")):
        cases.extend(json.loads(path.read_text(encoding="utf-8")))
    return cases


def oracle_result(case):
    expected = case["expected"]
    route = []
    if expected.get("start_stage"):
        route.append(expected["start_stage"])
    for stage in expected.get("required_stages") or []:
        if stage not in route:
            route.append(stage)
    return {
        "case_id": case["id"],
        "status": expected.get("status"),
        "earliest_untrusted_layer": expected.get("earliest_untrusted_layer"),
        "start_stage": expected.get("start_stage"),
        "route": route,
        "authority_classification": expected.get("authority_classification") or [],
        "defect_classification": expected.get("defect_classification"),
        "gate_verdict": expected.get("gate_verdict"),
        "findings": [],
        "evidence_requirements": [],
    }


class FullCorpusContractTests(unittest.TestCase):
    def test_current_corpus_can_score_perfectly_from_oracle_fields(self):
        cases = load_cases()
        self.assertGreaterEqual(len(cases), 30)
        scores = [score_case(case, oracle_result(case)) for case in cases]
        self.assertTrue(all(item["exact_score"] == 1.0 for item in scores))
        self.assertTrue(all(not item["critical_errors"] for item in scores))
        summary = summarize_scores(scores)
        self.assertEqual(summary["overall_weighted_score"], 1.0)
        self.assertTrue(summary["candidate_release_gate_pass"])


if __name__ == "__main__":
    unittest.main()
