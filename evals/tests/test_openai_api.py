import tempfile
import unittest
from pathlib import Path

from evals.providers.openai.api import (
    HTTPResult,
    OpenAIHostedSkillAPI,
    SkillRef,
    build_response_payload,
)


class FakeTransport:
    def __init__(self):
        self.multipart_calls = []
        self.json_calls = []

    def post_multipart_file(self, path, field_name, file_path, content_type):
        self.multipart_calls.append((path, field_name, Path(file_path), content_type))
        return HTTPResult(
            body={"id": "skill_123", "default_version": "7", "latest_version": "7"},
            status_code=200,
            latency_ms=12.5,
            retry_count=0,
        )

    def post_json(self, path, payload):
        self.json_calls.append((path, payload))
        return HTTPResult(
            body={
                "id": "resp_123",
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": '{"case_id":"routing-001","status":"READY","earliest_untrusted_layer":"problem","start_stage":"P00","route":["P00"],"authority_classification":[],"defect_classification":null,"gate_verdict":null,"findings":[],"evidence_requirements":[]}'
                            }
                        ],
                    }
                ],
            },
            status_code=200,
            latency_ms=55.0,
            retry_count=1,
        )


class OpenAIHostedSkillAPITests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "id": "routing-001",
            "category": "routing",
            "severity": "critical",
            "input": {
                "prompt": "Help me start this new product.",
                "context": ["No validated problem exists."],
            },
            "expected": {"status": "BLOCKED_AUTHORITY", "secret": "GOLDEN_SENTINEL"},
            "tags": ["SECRET_TAG"],
        }

    def test_create_skill_uploads_zip_as_multipart_and_returns_pinned_ref(self):
        transport = FakeTransport()
        api = OpenAIHostedSkillAPI(transport)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "aegis.zip"
            path.write_bytes(b"zip")
            ref = api.create_skill(path)

        self.assertEqual(ref, SkillRef(skill_id="skill_123", version="7"))
        self.assertEqual(transport.multipart_calls[0][0], "/skills")
        self.assertEqual(transport.multipart_calls[0][1], "files")
        self.assertEqual(transport.multipart_calls[0][3], "application/zip")

    def test_response_payload_pins_skill_and_never_contains_golden_fields(self):
        payload = build_response_payload(
            self.case,
            SkillRef(skill_id="skill_123", version="7"),
            model="gpt-5.6-sol",
            reasoning_effort="medium",
        )
        self.assertEqual(payload["model"], "gpt-5.6-sol")
        self.assertEqual(payload["reasoning"], {"effort": "medium"})
        shell = payload["tools"][0]
        self.assertEqual(shell["type"], "shell")
        self.assertEqual(shell["environment"]["type"], "container_auto")
        self.assertEqual(
            shell["environment"]["skills"],
            [{"type": "skill_reference", "skill_id": "skill_123", "version": "7"}],
        )
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertTrue(payload["text"]["format"]["strict"])
        encoded = repr(payload)
        self.assertNotIn("GOLDEN_SENTINEL", encoded)
        self.assertNotIn("expected", encoded)
        self.assertNotIn("SECRET_TAG", encoded)
        self.assertIn("Use the mounted `aegis` skill", payload["input"])

    def test_create_response_posts_only_safe_payload(self):
        transport = FakeTransport()
        api = OpenAIHostedSkillAPI(transport)
        result = api.create_response(
            self.case,
            SkillRef(skill_id="skill_123", version="7"),
            model="gpt-5.6-sol",
            reasoning_effort="medium",
        )
        self.assertEqual(result.body["id"], "resp_123")
        path, payload = transport.json_calls[0]
        self.assertEqual(path, "/responses")
        self.assertNotIn("GOLDEN_SENTINEL", repr(payload))
        self.assertEqual(result.retry_count, 1)


if __name__ == "__main__":
    unittest.main()
