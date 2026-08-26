import json
import io
import os
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from evals.providers.openai.api import HTTPResult, SkillRef
from evals.providers.openai.driver import main, run_case


class FakeAPI:
    def __init__(self):
        self.calls = []

    def create_response(self, case, skill, *, model, reasoning_effort):
        self.calls.append((case, skill, model, reasoning_effort))
        return HTTPResult(
            body={
                "id": "resp_abc",
                "status": "completed",
                "model": model,
                "created_at": 123,
                "usage": {"input_tokens": 12, "output_tokens": 8},
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {
                                        "case_id": "WRONG",
                                        "status": "READY",
                                        "earliest_untrusted_layer": "problem",
                                        "start_stage": "P00",
                                        "route": ["P00"],
                                        "authority_classification": [],
                                        "defect_classification": None,
                                        "gate_verdict": None,
                                        "findings": ["Start at the earliest untrusted layer."],
                                        "evidence_requirements": [],
                                    }
                                ),
                            }
                        ],
                    }
                ],
            },
            status_code=200,
            latency_ms=42.0,
            retry_count=1,
        )


class OpenAIDriverTests(unittest.TestCase):
    def test_run_case_preserves_provider_evidence_and_forces_case_identity(self):
        case = {
            "id": "routing-001",
            "category": "routing",
            "severity": "critical",
            "input": {"prompt": "Help me start.", "context": ["No problem statement."]},
            "expected": {"secret": "GOLDEN_SENTINEL"},
            "tags": ["SECRET_TAG"],
        }
        api = FakeAPI()
        with tempfile.TemporaryDirectory() as td:
            output = run_case(
                case,
                api=api,
                skill=SkillRef("skill_123", "7"),
                evidence_dir=Path(td),
                model="gpt-5.6-sol",
                reasoning_effort="medium",
            )
            parsed = json.loads(output)
            evidence_path = Path(td) / "routing-001.json"
            evidence = json.loads(evidence_path.read_text())

        self.assertEqual(parsed["case_id"], "routing-001")
        self.assertEqual(parsed["status"], "READY")
        self.assertEqual(evidence["response_id"], "resp_abc")
        self.assertEqual(evidence["skill_id"], "skill_123")
        self.assertEqual(evidence["skill_version"], "7")
        self.assertEqual(evidence["scenario"]["case_id"], "routing-001")
        encoded = json.dumps(evidence)
        self.assertNotIn("GOLDEN_SENTINEL", encoded)
        self.assertNotIn("SECRET_TAG", encoded)
        self.assertNotIn("expected", encoded)

        sent_case = api.calls[0][0]
        self.assertEqual(set(sent_case), {"id", "input"})
        self.assertNotIn("expected", sent_case)
        self.assertEqual(api.calls[0][1], SkillRef("skill_123", "7"))

    def test_main_missing_api_key_returns_blocked_environment(self):
        stdin = io.StringIO(json.dumps({"id": "routing-001", "input": {"prompt": "x", "context": []}}))
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("sys.stdin", stdin), mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            code = main(["--skill-id", "skill_123", "--skill-version", "7", "--evidence-dir", "/tmp/aegis-provider-evidence"])
        self.assertEqual(code, 3)
        self.assertIn("BLOCKED_ENVIRONMENT", stderr.getvalue())
        self.assertEqual(stdout.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
