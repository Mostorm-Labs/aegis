"""Independent verifier helpers for M16-M20 qualification."""

from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import hmac
import json
from typing import Mapping

from tools.aegis_control.canonical import canonical_json_bytes


@dataclass(frozen=True)
class SnapshotVerification:
    ok: bool
    reason: str
    payload: dict[str, str] | None = None


def _b64url_encode(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def _b64url_decode(data: bytes) -> bytes:
    return base64.urlsafe_b64decode(data + b"=" * (-len(data) % 4))


def issue_snapshot_token(payload: Mapping[str, str], key: bytes) -> bytes:
    payload_bytes = canonical_json_bytes(dict(payload))
    signature = hmac.new(key, payload_bytes, hashlib.sha256).hexdigest().encode("ascii")
    return _b64url_encode(payload_bytes) + b"." + signature


def verify_snapshot_token(token: bytes, key: bytes, expected_binding: Mapping[str, str]) -> SnapshotVerification:
    try:
        encoded, supplied_signature = token.split(b".", 1)
        raw_payload = _b64url_decode(encoded)
        expected_signature = hmac.new(key, raw_payload, hashlib.sha256).hexdigest().encode("ascii")
        if not hmac.compare_digest(supplied_signature, expected_signature):
            return SnapshotVerification(False, "INVALID_INTEGRITY")
        payload = json.loads(raw_payload.decode("utf-8"))
        if canonical_json_bytes(payload) != raw_payload:
            return SnapshotVerification(False, "NON_CANONICAL_PAYLOAD")
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return SnapshotVerification(False, "MALFORMED_TOKEN")
    for field in ("adapter", "source_kind", "resource_id", "resource_version"):
        if payload.get(field) != expected_binding.get(field):
            return SnapshotVerification(False, "BINDING_MISMATCH", payload)
    return SnapshotVerification(True, "OK", payload)


def mutate_snapshot_payload_without_resigning(token: bytes, field: str, value: str) -> bytes:
    encoded, signature = token.split(b".", 1)
    payload = json.loads(_b64url_decode(encoded).decode("utf-8"))
    payload[field] = value
    mutated_payload = canonical_json_bytes(payload)
    return _b64url_encode(mutated_payload) + b"." + signature


def supports_autonomous_trust_sensitive_provider(*, supports_callback: bool, supports_durable_query: bool, supports_correlation: bool) -> bool:
    return bool(supports_callback and supports_durable_query and supports_correlation)


def sha256_prefixed(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def verify_full_representation(full_bytes: bytes, transported_bytes: bytes, expected_full_digest: str) -> bool:
    return transported_bytes == full_bytes and sha256_prefixed(full_bytes) == expected_full_digest
