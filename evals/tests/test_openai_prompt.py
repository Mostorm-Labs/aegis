import json
import unittest

from evals.providers.openai.prompt import (
    PROMPT_TEMPLATE_VERSION,
    build_case_prompt,
    build_strict_result_schema,
    sanitize_case,
)


class OpenAIPromptTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "id": "routing-001",
            "category": "routing",
            "title": "SECRET_TITLE",
            "severity": "critical",
            "origin": "synthetic",
            "input": {
                "prompt": "Decide where this work should start.",
                "context": ["There is no validated requirement."],
            },
            "expected": {
                "status": "BLOCKED_AUTHORITY",
                "start_stage": "P21",
                "required_findings": ["GOLDEN_SENTINEL"],
            },
            "tags": ["SECRET_TAG"],
        }

    def test_sanitize_case_exposes_only_scenario_fields(self):
        sanitized = sanitize_case(self.case)
        self.assertEqual(
            sanitized,
            {
                "case_id": "routing-001",
                "prompt": "Decide where this work should start.",
                "context": ["There is no validated requirement."],
            },
        )
        encoded = json.dumps(sanitized)
        for forbidden in ("expected", "GOLDEN_SENTINEL", "SECRET_TITLE", "SECRET_TAG", "critical"):
            self.assertNotIn(forbidden, encoded)

    def test_prompt_requires_aegis_without_embedding_goldens(self):
        prompt = build_case_prompt(sanitize_case(self.case))
        self.assertIn("Use the mounted `aegis` skill", prompt)
        self.assertIn("routing-001", prompt)
        self.assertIn("Decide where this work should start.", prompt)
        self.assertIn("There is no validated requirement.", prompt)
        self.assertNotIn("GOLDEN_SENTINEL", prompt)
        self.assertNotIn("BLOCKED_AUTHORITY", prompt)
        self.assertTrue(PROMPT_TEMPLATE_VERSION.startswith("openai-hosted-aegis-baseline/"))

    def test_strict_result_schema_is_closed_and_requires_normalized_fields(self):
        schema = build_strict_result_schema()
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["type"], "object")
        self.assertIn("status", schema["required"])
        self.assertIn("route", schema["required"])
        self.assertIn("findings", schema["required"])
        status_enum = schema["properties"]["status"]["enum"]
        self.assertIn("READY", status_enum)
        self.assertIn("BLOCKED_EVIDENCE", status_enum)
        self.assertNotIn("READY_TO_ROUTE", status_enum)
        defect = schema["properties"]["defect_classification"]
        self.assertEqual(defect["type"], ["string", "null"])
        self.assertIn("IMPLEMENTATION_DEFECT", defect["enum"])
        self.assertIn(None, defect["enum"])


if __name__ == "__main__":
    unittest.main()
