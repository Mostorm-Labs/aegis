"""Canonical JSON and structural validation primitives for Control Plane v0.2.

The canonical encoder implements the RFC 8785/JCS behaviors required by the
accepted Control Plane schemas: UTF-8 JSON, UTF-16 property ordering,
I-JSON-safe numbers, deterministic ECMAScript-style number spelling, and
SHA-256 digests. It deliberately contains no Control Plane runtime flow.
"""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
import math
import re
from typing import Any, Mapping, Sequence


DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
MAX_SAFE_INTEGER = 9_007_199_254_740_991

CANONICAL_REF_OBJECT_TYPES = {
    "AUTHORITY", "CONTRACT", "STAGE_OCCURRENCE", "VERIFICATION_SPEC",
    "PROOF_OBLIGATION_SET", "IMPLEMENTATION_PACKAGE", "RESULT", "EVIDENCE",
    "PROOF_EVALUATION", "GATE_DECISION", "INTEGRATION", "FINDING",
    "EXECUTION_CURSOR", "EXTERNAL_DECISION",
}

COMMON_FIELDS = {
    "schema_version", "kind", "id_scheme", "id", "record_revision",
    "recorded_at", "extensions",
}

KIND_FIELDS = {
    "STAGE_OCCURRENCE": COMMON_FIELDS | {
        "control_lane_id", "work_scope_ref", "stage_span", "primary_owner", "state",
        "trusted_basis", "policy_binding", "schedule_basis", "input_refs",
        "repair_context", "execution_navigation", "terminal",
    },
    "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE": COMMON_FIELDS | {
        "control_lane_id", "trusted_basis", "scope", "verification_binding",
        "policy_binding", "task_anchor", "package_digest",
    },
    "ESCALATION": COMMON_FIELDS | {
        "control_lane_id", "raised_from_occurrence_ref", "trusted_basis_digest",
        "category", "owning_layer", "required_decision", "evidence_snapshot_refs",
    },
}

KIND_ID_SCHEME = {
    "STAGE_OCCURRENCE": "stage-occurrence-v0.2",
    "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE": "verification-bound-package-v0.2",
    "ESCALATION": "escalation-v0.2",
}


class CanonicalValidationError(ValueError):
    """Raised when a value cannot participate in canonical Control Plane truth."""


def _validate_string(value: str) -> None:
    for char in value:
        code = ord(char)
        if 0xD800 <= code <= 0xDFFF:
            raise CanonicalValidationError("lone surrogate is not valid I-JSON text")


def _utf16_sort_key(value: str) -> bytes:
    _validate_string(value)
    return value.encode("utf-16-be")


def _normalize_exponent(text: str) -> str:
    mantissa, exponent = text.lower().split("e", 1)
    sign = "+" if not exponent.startswith("-") else "-"
    digits = exponent.lstrip("+-").lstrip("0") or "0"
    if "." in mantissa:
        mantissa = mantissa.rstrip("0").rstrip(".")
    return f"{mantissa}e+{digits}" if sign == "+" else f"{mantissa}e-{digits}"


def _format_float(value: float) -> str:
    if not math.isfinite(value):
        raise CanonicalValidationError("non-finite JSON numbers are forbidden")
    if value == 0.0:
        return "0"
    absolute = abs(value)
    shortest = repr(value).lower()
    if 1e-6 <= absolute < 1e21:
        fixed = format(Decimal(shortest), "f")
        if "." in fixed:
            fixed = fixed.rstrip("0").rstrip(".")
        return fixed
    if "e" not in shortest:
        shortest = format(value, ".15e")
    return _normalize_exponent(shortest)


def _encode(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise CanonicalValidationError("integer exceeds I-JSON safe integer range")
        return str(value)
    if isinstance(value, float):
        return _format_float(value)
    if isinstance(value, str):
        _validate_string(value)
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_encode(item) for item in value) + "]"
    if isinstance(value, Mapping):
        for key in value:
            if not isinstance(key, str):
                raise CanonicalValidationError("canonical JSON object keys must be strings")
            _validate_string(key)
        parts = []
        for key in sorted(value.keys(), key=_utf16_sort_key):
            parts.append(f"{_encode(key)}:{_encode(value[key])}")
        return "{" + ",".join(parts) + "}"
    raise CanonicalValidationError(f"unsupported canonical JSON type: {type(value).__name__}")


def canonical_dumps(value: Any) -> str:
    return _encode(value)


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_dumps(value).encode("utf-8")


def canonical_digest(value: Any, *, self_digest_field: str | None = None) -> str:
    target = value
    if self_digest_field is not None:
        if not isinstance(value, Mapping):
            raise CanonicalValidationError("self digest exclusion requires an object")
        target = {key: item for key, item in value.items() if key != self_digest_field}
    digest = hashlib.sha256(canonical_json_bytes(target)).hexdigest()
    return f"sha256:{digest}"


def validate_digest(value: str) -> None:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise CanonicalValidationError("digest must be sha256:<64 lowercase hex>")


def validate_canonical_ref(ref: Mapping[str, Any]) -> None:
    if not isinstance(ref, Mapping):
        raise CanonicalValidationError("CanonicalRef must be an object")
    expected = {"object_type", "id", "ref", "identity"}
    unknown = set(ref) - expected
    missing = expected - set(ref)
    if missing:
        raise CanonicalValidationError(f"CanonicalRef missing fields: {sorted(missing)}")
    if unknown:
        raise CanonicalValidationError(f"CanonicalRef unknown fields: {sorted(unknown)}")
    if ref["object_type"] not in CANONICAL_REF_OBJECT_TYPES:
        raise CanonicalValidationError("CanonicalRef has unknown object_type")
    if not isinstance(ref["id"], str) or not ref["id"]:
        raise CanonicalValidationError("CanonicalRef id is required")
    if not isinstance(ref["ref"], str) or not ref["ref"]:
        raise CanonicalValidationError("CanonicalRef ref is required")
    identity = ref["identity"]
    if not isinstance(identity, Mapping) or set(identity) != {"scheme", "value"}:
        raise CanonicalValidationError("CanonicalRef identity requires exactly scheme and value")
    if not all(isinstance(identity[key], str) and identity[key] for key in ("scheme", "value")):
        raise CanonicalValidationError("CanonicalRef identity scheme/value must be non-empty strings")


def validate_record(record: Mapping[str, Any]) -> None:
    if not isinstance(record, Mapping):
        raise CanonicalValidationError("canonical record must be an object")
    kind = record.get("kind")
    if kind not in KIND_FIELDS:
        raise CanonicalValidationError(f"unknown canonical record kind: {kind}")
    allowed = KIND_FIELDS[kind]
    unknown = set(record) - allowed
    missing = COMMON_FIELDS - set(record)
    if unknown:
        raise CanonicalValidationError(f"unknown top-level canonical fields: {sorted(unknown)}")
    if missing:
        raise CanonicalValidationError(f"missing required canonical fields: {sorted(missing)}")
    if record.get("schema_version") != "0.2":
        raise CanonicalValidationError("schema_version must equal 0.2")
    if record.get("id_scheme") != KIND_ID_SCHEME[kind]:
        raise CanonicalValidationError("id_scheme does not match kind")
    if not isinstance(record.get("id"), str) or not record["id"]:
        raise CanonicalValidationError("record id is required")
    revision = record.get("record_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise CanonicalValidationError("record_revision must be a positive integer")
    if not isinstance(record.get("recorded_at"), str) or not record["recorded_at"]:
        raise CanonicalValidationError("recorded_at is required")
    if not isinstance(record.get("extensions"), Mapping):
        raise CanonicalValidationError("extensions must be an object")
    if kind == "STAGE_OCCURRENCE":
        state = record.get("state")
        if state not in {"OPEN", "TERMINAL"}:
            raise CanonicalValidationError("StageOccurrence state must be OPEN or TERMINAL")
        terminal = record.get("terminal")
        if state == "OPEN" and terminal is not None:
            raise CanonicalValidationError("OPEN StageOccurrence terminal must be null")
        if state == "TERMINAL" and not isinstance(terminal, Mapping):
            raise CanonicalValidationError("TERMINAL StageOccurrence requires terminal facts")


def validate_revision_lineage(records: Sequence[Mapping[str, Any]]) -> None:
    if not records:
        raise CanonicalValidationError("lineage must not be empty")
    for record in records:
        validate_record(record)
    first = records[0]
    for index, record in enumerate(records, start=1):
        if record["kind"] != first["kind"] or record["id"] != first["id"] or record["id_scheme"] != first["id_scheme"]:
            raise CanonicalValidationError("lineage identity must remain stable")
        if record["record_revision"] != index:
            raise CanonicalValidationError("record_revision lineage must be contiguous from 1")
    if first["kind"] == "STAGE_OCCURRENCE":
        terminal_indexes = [i for i, r in enumerate(records) if r["state"] == "TERMINAL"]
        if len(terminal_indexes) > 1:
            raise CanonicalValidationError("StageOccurrence may have only one terminal revision")
        if terminal_indexes and terminal_indexes[0] != len(records) - 1:
            raise CanonicalValidationError("no StageOccurrence revision may follow terminal")
