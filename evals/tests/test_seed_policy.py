import unittest

from evals.scripts.validate_corpus import validate_cases


def make_case(case_id, category, origin="synthetic"):
    return {
        "id": case_id,
        "category": category,
        "title": "valid case",
        "severity": "normal",
        "origin": origin,
        "input": {"prompt": "valid prompt", "context": []},
        "expected": {
            "status": "READY",
            "earliest_untrusted_layer": None,
            "start_stage": "P00" if category == "routing" else "P21",
            "required_stages": [],
            "forbidden_stages": [],
            "authority_classification": [],
            "defect_classification": "IMPLEMENTATION_DEFECT" if category == "defect" else None,
            "gate_verdict": "PASS" if category == "gate" else None,
            "required_findings": [],
            "forbidden_findings": [],
        },
        "tags": [],
    }


class SeedPolicyTests(unittest.TestCase):
    def build_seed(self):
        counts = {"routing": 10, "authority": 8, "defect": 6, "gate": 6}
        cases = []
        for category, count in counts.items():
            for i in range(1, count + 1):
                cases.append(make_case(f"{category}-{i:03d}", category))
        return cases

    def test_allows_additional_dogfood_case_after_seed(self):
        cases = self.build_seed()
        cases.append(make_case("routing-011", "routing", origin="dogfood"))
        errors, summary = validate_cases(cases)
        self.assertEqual(errors, [])
        self.assertEqual(summary["total"], 31)

    def test_missing_seed_id_fails_even_if_count_is_replaced(self):
        cases = self.build_seed()
        cases = [c for c in cases if c["id"] != "routing-003"]
        cases.append(make_case("routing-011", "routing", origin="dogfood"))
        errors, _ = validate_cases(cases)
        self.assertTrue(any("routing-003" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
