import ast
from pathlib import Path
import unittest

import completeness_oracle as complete


class CompletenessOracleTests(unittest.TestCase):
    def setUp(self):
        self.expected = list(complete.expected_obligations())

    def test_exact_review_declared_set_is_accepted(self):
        result = complete.validate_obligation_set(self.expected, {o["id"] for o in self.expected})
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(len(self.expected), 20)
        self.assertEqual(sum(o["kind"] == "COVERAGE_COMPLETENESS" for o in self.expected), 1)

    def test_omitted_claim_is_rejected(self):
        result = complete.validate_obligation_set(self.expected[:-2] + self.expected[-1:], None)
        self.assertIn("MISSING_OBLIGATION", result.error_codes)

    def test_omitted_coverage_completeness_is_rejected(self):
        supplied = [o for o in self.expected if o["kind"] != "COVERAGE_COMPLETENESS"]
        result = complete.validate_obligation_set(supplied, None)
        self.assertIn("MISSING_COVERAGE_COMPLETENESS", result.error_codes)

    def test_duplicate_obligation_is_rejected(self):
        result = complete.validate_obligation_set(self.expected + [dict(self.expected[0])], None)
        self.assertIn("DUPLICATE_OBLIGATION", result.error_codes)

    def test_extra_unknown_obligation_is_rejected(self):
        supplied = self.expected + [{"id": "CPV-O-UNKNOWN", "kind": "CLAIM", "source_key": "unknown"}]
        result = complete.validate_obligation_set(supplied, None)
        self.assertIn("EXTRA_OBLIGATION", result.error_codes)

    def test_changed_semantic_source_key_is_rejected(self):
        supplied = [dict(o) for o in self.expected]
        supplied[0]["source_key"] = "tampered"
        result = complete.validate_obligation_set(supplied, None)
        self.assertIn("SOURCE_KEY_MISMATCH", result.error_codes)

    def test_strict_subset_or_superset_evaluation_is_rejected(self):
        ids = {o["id"] for o in self.expected}
        subset = set(ids)
        subset.pop()
        self.assertIn("EVALUATION_SET_MISMATCH", complete.validate_obligation_set(self.expected, subset).error_codes)
        superset = set(ids) | {"CPV-O-EXTRA"}
        self.assertIn("EVALUATION_SET_MISMATCH", complete.validate_obligation_set(self.expected, superset).error_codes)

    def test_completeness_oracle_does_not_import_execution_generator(self):
        path = Path(__file__).with_name("completeness_oracle.py")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertFalse([name for name in imported if "obligation_generator" in name])


if __name__ == "__main__":
    unittest.main()
