import unittest

from evals.providers.openai.api import HTTPResult
from evals.providers.openai.response import (
    ProviderResponseError,
    extract_output_text,
    provider_evidence_record,
)


class OpenAIResponseTests(unittest.TestCase):
    def test_extract_output_text_from_completed_response(self):
        body = {
            "id": "resp_123",
            "status": "completed",
            "model": "gpt-5.6-sol",
            "created_at": 123456,
            "usage": {"input_tokens": 10, "output_tokens": 20},
            "output": [
                {"type": "shell_call", "id": "sh_1"},
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": '{"status":"READY"}'},
                    ],
                },
            ],
        }
        self.assertEqual(extract_output_text(body), '{"status":"READY"}')

    def test_incomplete_response_fails_closed(self):
        body = {"id": "resp_1", "status": "incomplete", "output": []}
        with self.assertRaisesRegex(ProviderResponseError, "incomplete"):
            extract_output_text(body)

    def test_missing_output_text_fails_closed(self):
        body = {"id": "resp_1", "status": "completed", "output": [{"type": "shell_call"}]}
        with self.assertRaisesRegex(ProviderResponseError, "output_text"):
            extract_output_text(body)

    def test_provider_evidence_preserves_response_and_transport_metrics(self):
        result = HTTPResult(
            body={
                "id": "resp_123",
                "status": "completed",
                "model": "gpt-5.6-sol",
                "created_at": 123456,
                "usage": {"input_tokens": 10, "output_tokens": 20},
                "output": [],
            },
            status_code=200,
            latency_ms=88.25,
            retry_count=2,
        )
        evidence = provider_evidence_record(
            case_id="routing-001",
            result=result,
            output_text='{"status":"READY"}',
        )
        self.assertEqual(evidence["case_id"], "routing-001")
        self.assertEqual(evidence["response_id"], "resp_123")
        self.assertEqual(evidence["model"], "gpt-5.6-sol")
        self.assertEqual(evidence["latency_ms"], 88.25)
        self.assertEqual(evidence["retry_count"], 2)
        self.assertEqual(evidence["usage"]["output_tokens"], 20)
        self.assertEqual(evidence["response"], result.body)
        self.assertEqual(evidence["output_text"], '{"status":"READY"}')


if __name__ == "__main__":
    unittest.main()
