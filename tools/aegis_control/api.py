from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping


SUPPORTED_PROTOCOL_VERSION = "v1"
REFERENCE_SUPPORTED_REQUEST_BYTES = 1024 * 1024
FORBIDDEN_SECRET_KEYS = {
    "access_token", "refresh_token", "oauth_token", "api_token", "api_key",
    "password", "client_secret", "signing_secret", "authorization", "bearer_token",
}


class ApiRequestError(RuntimeError):
    def __init__(self, code: str, detail: Any = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}: {detail}")


def enforce_envelope_size(raw: bytes, *, max_bytes: int = REFERENCE_SUPPORTED_REQUEST_BYTES) -> bytes:
    if not isinstance(raw, (bytes, bytearray)):
        raise ApiRequestError("INVALID_TRANSPORT_BODY")
    actual = len(raw)
    if actual > max_bytes:
        raise ApiRequestError("REQUEST_TOO_LARGE", {"actual_bytes": actual, "max_bytes": max_bytes})
    return bytes(raw)


def _scan_secret_keys(value: Any, *, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in FORBIDDEN_SECRET_KEYS:
                raise ApiRequestError("SECRET_MATERIAL_IN_SEMANTIC_PAYLOAD", {"path": ".".join(path + (str(key),))})
            _scan_secret_keys(child, path=path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_secret_keys(child, path=path + (str(index),))


def validate_transport_semantic_payload(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ApiRequestError("INVALID_OPERATION_ENVELOPE")
    _scan_secret_keys(value)
    return value


@dataclass(frozen=True)
class ApiResponse:
    status: int
    body: Mapping[str, Any]


class ControlApi:
    def __init__(self, *, mutation_service, query_service=None, max_request_bytes: int = REFERENCE_SUPPORTED_REQUEST_BYTES):
        self._mutation_service = mutation_service
        self._query_service = query_service
        self._max_request_bytes = max_request_bytes

    def handle(self, *, method: str, path: str, headers: Mapping[str, str], body: bytes = b"") -> ApiResponse:
        method = method.upper()
        version = headers.get("X-Aegis-Protocol-Version")
        if version != SUPPORTED_PROTOCOL_VERSION:
            raise ApiRequestError("UNSUPPORTED_PROTOCOL_VERSION", {"received": version, "expected": SUPPORTED_PROTOCOL_VERSION})
        if method == "PATCH" and path.startswith("/v1/"):
            raise ApiRequestError("FORBIDDEN_CANONICAL_MUTATION_ROUTE", path)
        if method == "POST" and path == "/v1/operations":
            return self._submit_operation(headers, body)
        if method == "GET" and path.startswith("/v1/"):
            if self._query_service is None:
                raise ApiRequestError("QUERY_SERVICE_UNAVAILABLE")
            result = self._query_service(path)
            return ApiResponse(status=200, body={"data": result, "semantic_truth": False})
        raise ApiRequestError("ROUTE_NOT_FOUND", {"method": method, "path": path})

    def _submit_operation(self, headers: Mapping[str, str], body: bytes) -> ApiResponse:
        content_type = headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise ApiRequestError("UNSUPPORTED_CONTENT_TYPE")
        raw = enforce_envelope_size(body, max_bytes=self._max_request_bytes)
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ApiRequestError("INVALID_UTF8") from exc
        try:
            request = json.loads(text)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ApiRequestError("INVALID_JSON") from exc
        validate_transport_semantic_payload(request)
        operation_request_id = request.get("operation_request_id") if isinstance(request, Mapping) else None
        idempotency_key = headers.get("Idempotency-Key")
        if not isinstance(operation_request_id, str) or not operation_request_id:
            raise ApiRequestError("OPERATION_REQUEST_ID_REQUIRED")
        if idempotency_key != operation_request_id:
            raise ApiRequestError("IDEMPOTENCY_KEY_MISMATCH")
        result = self._mutation_service.apply(request)
        return ApiResponse(status=200, body={"result": result})
