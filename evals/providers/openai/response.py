from __future__ import annotations

from .http import HTTPResult


class ProviderResponseError(RuntimeError):
    pass


def extract_output_text(response: dict) -> str:
    status = response.get("status")
    if status != "completed":
        raise ProviderResponseError(f"provider response is {status or 'unknown'}, not completed")

    texts: list[str] = []
    output = response.get("output", [])
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content", [])
            if not isinstance(content, list):
                continue
            for part in content:
                if isinstance(part, dict) and part.get("type") == "output_text":
                    text = part.get("text")
                    if isinstance(text, str) and text:
                        texts.append(text)

    if not texts:
        raise ProviderResponseError("provider response does not contain output_text")
    return "\n".join(texts)


def provider_evidence_record(*, case_id: str, result: HTTPResult, output_text: str) -> dict:
    body = result.body
    return {
        "case_id": case_id,
        "response_id": body.get("id"),
        "provider_status": body.get("status"),
        "model": body.get("model"),
        "created_at": body.get("created_at"),
        "usage": body.get("usage") or {},
        "latency_ms": result.latency_ms,
        "retry_count": result.retry_count,
        "http_status": result.status_code,
        "output_text": output_text,
        "response": body,
    }
