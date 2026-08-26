import io
import json
import unittest
import urllib.error

from evals.providers.openai.http import (
    OpenAIHTTPTransport,
    ProviderEnvironmentError,
)


class FakeResponse:
    def __init__(self, body, status=200):
        self.body = json.dumps(body).encode()
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


class SequenceOpener:
    def __init__(self, items):
        self.items = list(items)
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append((request, timeout))
        item = self.items.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


class OpenAIHTTPTransportTests(unittest.TestCase):
    def test_retryable_429_retries_once_and_reports_retry_count(self):
        error = urllib.error.HTTPError(
            "https://api.openai.com/v1/responses",
            429,
            "rate limited",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"rate limited"}'),
        )
        opener = SequenceOpener([error, FakeResponse({"id": "resp_1"})])
        sleeps = []
        transport = OpenAIHTTPTransport(
            "secret",
            max_retries=2,
            retry_base_seconds=0.25,
            sleep_fn=sleeps.append,
            opener=opener,
        )
        result = transport.post_json("/responses", {"model": "gpt-5.6-sol"})
        self.assertEqual(result.body["id"], "resp_1")
        self.assertEqual(result.retry_count, 1)
        self.assertEqual(sleeps, [0.25])
        self.assertEqual(len(opener.requests), 2)

    def test_401_maps_to_environment_error_without_retry(self):
        error = urllib.error.HTTPError(
            "https://api.openai.com/v1/responses",
            401,
            "unauthorized",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"bad key"}'),
        )
        opener = SequenceOpener([error])
        transport = OpenAIHTTPTransport("secret", opener=opener, sleep_fn=lambda _: None)
        with self.assertRaises(ProviderEnvironmentError) as ctx:
            transport.post_json("/responses", {})
        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(len(opener.requests), 1)

    def test_missing_key_is_environment_error(self):
        with self.assertRaises(ProviderEnvironmentError):
            OpenAIHTTPTransport("")


if __name__ == "__main__":
    unittest.main()
