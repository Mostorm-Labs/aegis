"""Opaque SourceSnapshotToken issue/verify primitives for CP-I04.

Tokens are operational validation guards. They are not Authority, Evidence,
Gate, Integration, or semantic lifecycle truth.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
from typing import Any, Mapping

from .canonical import canonical_json_bytes


_TOKEN_FIELDS = {
    "v",
    "source_kind",
    "adapter_id",
    "resource_key",
    "version_scheme",
    "version_value",
    "observed_at",
    "expires_at",
}


@dataclass(frozen=True)
class SnapshotVerification:
    valid: bool
    code: str
    payload: Mapping[str, Any] | None = None


class SourceSnapshotTokenCodec:
    """Issue and verify `sst1.<payload>.<integrity-tag>` tokens."""

    def __init__(self, secret: bytes):
        if not isinstance(secret, bytes) or not secret:
            raise ValueError("snapshot token secret must be non-empty bytes")
        self._secret = bytes(secret)

    @staticmethod
    def _encode_part(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    @staticmethod
    def _decode_part(value: str) -> bytes:
        if not isinstance(value, str) or not value:
            raise ValueError("empty base64url part")
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode((value + padding).encode("ascii"))

    def issue(self, payload: Mapping[str, Any]) -> str:
        value = dict(payload)
        if set(value) != _TOKEN_FIELDS or value.get("v") != 1:
            raise ValueError("invalid SourceSnapshotToken payload")
        payload_part = self._encode_part(canonical_json_bytes(value))
        signed = f"sst1.{payload_part}".encode("ascii")
        tag_part = self._encode_part(hmac.new(self._secret, signed, hashlib.sha256).digest())
        return f"sst1.{payload_part}.{tag_part}"

    def verify(
        self,
        token: str,
        *,
        expected_source_kind: str,
        expected_adapter_id: str,
        expected_resource_key: str,
        current_version_scheme: str | None = None,
        current_version_value: str | None = None,
        now: datetime | None = None,
    ) -> SnapshotVerification:
        try:
            prefix, payload_part, tag_part = token.split(".")
            if prefix != "sst1":
                return SnapshotVerification(False, "SNAPSHOT_TOKEN_FORMAT")
            signed = f"sst1.{payload_part}".encode("ascii")
            supplied_tag = self._decode_part(tag_part)
            expected_tag = hmac.new(self._secret, signed, hashlib.sha256).digest()
            if not hmac.compare_digest(supplied_tag, expected_tag):
                return SnapshotVerification(False, "SNAPSHOT_INTEGRITY_INVALID")
            payload = json.loads(self._decode_part(payload_part).decode("utf-8"))
        except (AttributeError, UnicodeDecodeError, ValueError, json.JSONDecodeError):
            return SnapshotVerification(False, "SNAPSHOT_TOKEN_FORMAT")

        if not isinstance(payload, Mapping) or set(payload) != _TOKEN_FIELDS or payload.get("v") != 1:
            return SnapshotVerification(False, "SNAPSHOT_PAYLOAD_INVALID")
        if payload.get("source_kind") != expected_source_kind:
            return SnapshotVerification(False, "SNAPSHOT_SOURCE_KIND_MISMATCH", payload)
        if payload.get("adapter_id") != expected_adapter_id:
            return SnapshotVerification(False, "SNAPSHOT_ADAPTER_MISMATCH", payload)
        if payload.get("resource_key") != expected_resource_key:
            return SnapshotVerification(False, "SNAPSHOT_RESOURCE_MISMATCH", payload)
        if current_version_scheme is not None and payload.get("version_scheme") != current_version_scheme:
            return SnapshotVerification(False, "SNAPSHOT_VERSION_STALE", payload)
        if current_version_value is not None and payload.get("version_value") != current_version_value:
            return SnapshotVerification(False, "SNAPSHOT_VERSION_STALE", payload)

        expires_at = payload.get("expires_at")
        if expires_at is not None:
            try:
                deadline = _parse_time(expires_at)
                observed_now = now or datetime.now(timezone.utc)
                if observed_now.tzinfo is None:
                    observed_now = observed_now.replace(tzinfo=timezone.utc)
                if observed_now > deadline:
                    return SnapshotVerification(False, "SNAPSHOT_EXPIRED", payload)
            except (TypeError, ValueError):
                return SnapshotVerification(False, "SNAPSHOT_PAYLOAD_INVALID", payload)
        return SnapshotVerification(True, "SNAPSHOT_VALID", payload)


def _parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp required")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_time(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
