from __future__ import annotations

import json
import mimetypes
import time
import uuid
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HTTPResult:
    body: dict
    status_code: int
    latency_ms: float
    retry_count: int


class ProviderError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, body: str = "", retry_count: int = 0):
        super().__init__(message)
        self.status_code = status_code
        self.body = body
        self.retry_count = retry_count


class ProviderEnvironmentError(ProviderError):
    pass


class ProviderRequestError(ProviderError):
    pass


class OpenAIHTTPTransport:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 120.0,
        max_retries: int = 2,
        retry_base_seconds: float = 1.0,
        sleep_fn=time.sleep,
        opener=urllib.request.urlopen,
    ):
        if not api_key:
            raise ProviderEnvironmentError("OPENAI_API_KEY is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_base_seconds = retry_base_seconds
        self.sleep_fn = sleep_fn
        self.opener = opener

    def post_json(self, path: str, payload: dict) -> HTTPResult:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return self._request(
            path,
            data=data,
            content_type="application/json",
        )

    def post_multipart_file(
        self,
        path: str,
        field_name: str,
        file_path: str | Path,
        content_type: str | None = None,
    ) -> HTTPResult:
        file_path = Path(file_path)
        if not file_path.is_file():
            raise ValueError(f"multipart file does not exist: {file_path}")
        boundary = f"aegis-{uuid.uuid4().hex}"
        content_type = content_type or mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        chunks = [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="{field_name}"; '
                f'filename="{file_path.name}"\r\n'
            ).encode(),
            f"Content-Type: {content_type}\r\n\r\n".encode(),
            file_path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
        return self._request(
            path,
            data=b"".join(chunks),
            content_type=f"multipart/form-data; boundary={boundary}",
        )

    def _request(self, path: str, *, data: bytes, content_type: str) -> HTTPResult:
        url = f"{self.base_url}/{path.lstrip('/')}"
        last_error: ProviderError | None = None
        started = time.monotonic()

        for attempt in range(self.max_retries + 1):
            request = urllib.request.Request(
                url,
                data=data,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": content_type,
                    "Accept": "application/json",
                },
            )
            try:
                with self.opener(request, timeout=self.timeout_seconds) as response:
                    raw = response.read().decode("utf-8")
                    body = json.loads(raw) if raw else {}
                    return HTTPResult(
                        body=body,
                        status_code=getattr(response, "status", 200),
                        latency_ms=(time.monotonic() - started) * 1000.0,
                        retry_count=attempt,
                    )
            except urllib.error.HTTPError as exc:
                raw = exc.read().decode("utf-8", errors="replace")
                status = exc.code
                if status in (401, 403):
                    raise ProviderEnvironmentError(
                        f"OpenAI API access denied with HTTP {status}",
                        status_code=status,
                        body=raw,
                        retry_count=attempt,
                    ) from exc
                retryable = status == 429 or status >= 500
                last_error = ProviderRequestError(
                    f"OpenAI API request failed with HTTP {status}",
                    status_code=status,
                    body=raw,
                    retry_count=attempt,
                )
                if not retryable or attempt >= self.max_retries:
                    raise last_error from exc
            except urllib.error.URLError as exc:
                last_error = ProviderRequestError(
                    f"OpenAI API request failed: {exc.reason}",
                    retry_count=attempt,
                )
                if attempt >= self.max_retries:
                    raise last_error from exc

            self.sleep_fn(self.retry_base_seconds * (2**attempt))

        assert last_error is not None
        raise last_error
