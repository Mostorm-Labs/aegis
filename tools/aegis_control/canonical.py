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
        "control_lane_id", "work_scope_ref", "trusted_basis", "scope", "verification_binding",
        "policy_binding", "task_anchor", "package_digest",
    },
    "ESCALATION": COMMON_FIELDS | {
        "control_lane_id", "work_scope_ref", "raised_from_occurrence_ref", "trusted_basis_digest",
        "category", "owning_layer", "required_decision", "evidence_snapshot_refs",
    },
}
KIND_ID_SCHEME = {
    "STAGE_OCCURRENCE": "stage-occurrence-v0.2",
    "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE": "verification-bound-package-v0.2",
    "ESCALATION": "escalation-v0.2",
}
PRIMARY_OWNER_BY_STAGE = {
    "P00": "aegis-discovery",
    "P01": "aegis-discovery",
    "P02": "aegis-discovery",
    "P03": "aegis-discovery",
    "P10": "aegis-modeling",
    "P11": "aegis-modeling",
    "P12": "aegis-modeling",
    "P13": "aegis-modeling",
    "P14": "aegis-architecture",
    "P15": "aegis-architecture",
    "P16": "aegis-architecture",
    "P17": "aegis-architecture",
    "P18": "aegis-architecture",
    "P20": "aegis-verification",
    "P21": "aegis-governance",
    "P22": "aegis-governance",
    "P23": "aegis-governance",
    "P24": "aegis-governance",
    "P30": "aegis-implementation",
    "P31": "aegis-implementation",
    "P32": "aegis-implementation",
    "P33": "aegis-implementation",
    "P34": "aegis-gate-review",
    "P35": "aegis-gate-review",
    "P36": "aegis-gate-review",
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


def validate_work_scope_ref(value: Mapping[str, Any], *, parent_ref: bool = False) -> None:
    if not isinstance(value, Mapping):
        raise CanonicalValidationError("WorkScopeRef must be an object")
    expected = {"id_scheme", "id"} if parent_ref else {"id_scheme", "id", "child_work_binding"}
    if set(value) != expected:
        raise CanonicalValidationError("WorkScopeRef has invalid fields")
    if value.get("id_scheme") != "control-work-scope-v0.2":
        raise CanonicalValidationError("WorkScopeRef id_scheme mismatch")
    if not isinstance(value.get("id"), str) or not value["id"].startswith("ws_"):
        raise CanonicalValidationError("WorkScopeRef id is required")
    if parent_ref:
        return
    binding = value.get("child_work_binding")
    if binding is None:
        return
    expected_binding = {
        "parent_work_scope_ref", "spawned_by_occurrence_ref", "parent_gate",
        "acceptance_contract_refs",
    }
    if not isinstance(binding, Mapping) or set(binding) != expected_binding:
        raise CanonicalValidationError("ChildWorkBinding has invalid fields")
    validate_work_scope_ref(binding["parent_work_scope_ref"], parent_ref=True)
    if binding["parent_work_scope_ref"]["id"] == value["id"]:
        raise CanonicalValidationError("WorkScopeRef cannot be its own parent")
    validate_canonical_ref(binding["spawned_by_occurrence_ref"])
    if binding["spawned_by_occurrence_ref"].get("object_type") != "STAGE_OCCURRENCE":
        raise CanonicalValidationError("ChildWorkBinding spawn ref must target STAGE_OCCURRENCE")
    if binding.get("parent_gate") not in {"REQUIRED", "NON_BLOCKING"}:
        raise CanonicalValidationError("ChildWorkBinding parent_gate invalid")
    contracts = binding.get("acceptance_contract_refs")
    if not isinstance(contracts, list):
        raise CanonicalValidationError("ChildWorkBinding acceptance contracts must be a list")
    _validate_ref_list(contracts, object_type="CONTRACT", duplicate_message="duplicate acceptance contract ref")


def validate_required_child_acceptance_binding(value: Mapping[str, Any]) -> None:
    expected = {
        "child_work_scope_ref", "barrier_after_occurrence_ref", "child_completion_occurrence_ref",
        "acceptance_contract_refs", "acceptance_fact_refs", "acceptance_basis_digest",
    }
    if not isinstance(value, Mapping) or set(value) != expected:
        raise CanonicalValidationError("RequiredChildAcceptanceBinding has invalid fields")
    validate_work_scope_ref(value["child_work_scope_ref"])
    for field in ("barrier_after_occurrence_ref", "child_completion_occurrence_ref"):
        validate_canonical_ref(value[field])
        if value[field].get("object_type") != "STAGE_OCCURRENCE":
            raise CanonicalValidationError(f"{field} must target STAGE_OCCURRENCE")
    contracts = value["acceptance_contract_refs"]
    facts = value["acceptance_fact_refs"]
    if not isinstance(contracts, list) or not isinstance(facts, list):
        raise CanonicalValidationError("acceptance refs must be arrays")
    _validate_ref_list(contracts, object_type="CONTRACT", duplicate_message="duplicate acceptance contract ref")
    _validate_ref_list(facts, duplicate_message="duplicate acceptance fact ref")
    validate_digest(value["acceptance_basis_digest"])
    digest_payload = {key: item for key, item in value.items() if key != "acceptance_basis_digest"}
    if canonical_digest(digest_payload) != value["acceptance_basis_digest"]:
        raise CanonicalValidationError("acceptance_basis_digest mismatch")


def _validate_ref_list(values: Sequence[Mapping[str, Any]], *, object_type: str | None = None, duplicate_message: str) -> None:
    seen: set[str] = set()
    for ref in values:
        validate_canonical_ref(ref)
        if object_type is not None and ref.get("object_type") != object_type:
            raise CanonicalValidationError(f"CanonicalRef must target {object_type}")
        digest = canonical_digest(ref)
        if digest in seen:
            raise CanonicalValidationError(duplicate_message)
        seen.add(digest)


def _validate_stage_ownership(record: Mapping[str, Any]) -> None:
    stage_span = record.get("stage_span")
    if not isinstance(stage_span, Mapping) or set(stage_span) != {"stages"}:
        raise CanonicalValidationError("StageOccurrence stage_span must contain exactly stages")
    stages = stage_span.get("stages")
    if not isinstance(stages, list) or not stages or any(not isinstance(stage, str) for stage in stages):
        raise CanonicalValidationError("StageOccurrence stages must be a non-empty string list")
    if len(set(stages)) != len(stages):
        raise CanonicalValidationError("StageOccurrence stages must be unique")
    owners = []
    for stage in stages:
        owner = PRIMARY_OWNER_BY_STAGE.get(stage)
        if owner is None:
            raise CanonicalValidationError("StageOccurrence contains unknown stage")
        owners.append(owner)
    if len(set(owners)) != 1:
        raise CanonicalValidationError("StageOccurrence may not cross Primary owners")
    if record.get("primary_owner") != owners[0]:
        raise CanonicalValidationError("StageOccurrence primary_owner does not match stage ownership")



def _canonical_ref_sort_key(ref: Mapping[str, Any]) -> tuple[str, str, str, str]:
    identity = ref["identity"]
    return (
        ref["object_type"],
        ref["id"],
        identity["scheme"],
        identity["value"],
    )


def validate_trusted_basis(value: Mapping[str, Any]) -> None:
    expected = {
        "authority_refs", "contract_refs", "verification_refs",
        "accepted_fact_refs", "basis_digest",
    }
    if not isinstance(value, Mapping) or set(value) != expected:
        raise CanonicalValidationError("TrustedBasis has invalid fields")
    arrays = {
        "authority_refs": ("AUTHORITY",),
        "contract_refs": ("CONTRACT",),
        "verification_refs": ("VERIFICATION_SPEC", "PROOF_OBLIGATION_SET"),
        "accepted_fact_refs": ("GATE_DECISION", "RESULT", "INTEGRATION", "EXTERNAL_DECISION"),
    }
    for field, allowed_types in arrays.items():
        refs = value[field]
        if not isinstance(refs, list):
            raise CanonicalValidationError(f"TrustedBasis {field} must be a list")
        if field == "authority_refs" and not refs:
            raise CanonicalValidationError("TrustedBasis authority_refs must be non-empty")
        seen: set[str] = set()
        for ref in refs:
            validate_canonical_ref(ref)
            if ref["object_type"] not in allowed_types:
                raise CanonicalValidationError(
                    f"TrustedBasis {field} ref must target one of {sorted(allowed_types)}"
                )
            digest = canonical_digest(ref)
            if digest in seen:
                raise CanonicalValidationError(f"TrustedBasis {field} contains duplicate refs")
            seen.add(digest)
        if refs != sorted(refs, key=_canonical_ref_sort_key):
            raise CanonicalValidationError(f"TrustedBasis {field} must be canonically sorted")
    validate_digest(value["basis_digest"])
    payload = {key: item for key, item in value.items() if key != "basis_digest"}
    if canonical_digest(payload) != value["basis_digest"]:
        raise CanonicalValidationError("TrustedBasis basis_digest mismatch")


def validate_verification_binding(value: Mapping[str, Any]) -> None:
    expected = {
        "verification_spec_ref", "obligation_set_ref", "acceptance_oracle_refs",
        "evidence_compilation_contract_ref",
    }
    if not isinstance(value, Mapping) or set(value) != expected:
        raise CanonicalValidationError("verification_binding has invalid fields")
    validate_canonical_ref(value["verification_spec_ref"])
    if value["verification_spec_ref"]["object_type"] != "VERIFICATION_SPEC":
        raise CanonicalValidationError("verification_spec_ref must target VERIFICATION_SPEC")
    obligation_set_ref = value["obligation_set_ref"]
    if obligation_set_ref is not None:
        validate_canonical_ref(obligation_set_ref)
        if obligation_set_ref["object_type"] != "PROOF_OBLIGATION_SET":
            raise CanonicalValidationError("obligation_set_ref must target PROOF_OBLIGATION_SET")
    oracles = value["acceptance_oracle_refs"]
    if not isinstance(oracles, list) or not oracles:
        raise CanonicalValidationError("acceptance_oracle_refs must be a non-empty list")
    _validate_ref_list(
        oracles,
        object_type="CONTRACT",
        duplicate_message="duplicate acceptance oracle ref",
    )
    validate_canonical_ref(value["evidence_compilation_contract_ref"])
    if value["evidence_compilation_contract_ref"]["object_type"] != "CONTRACT":
        raise CanonicalValidationError("evidence_compilation_contract_ref must target CONTRACT")


def _validate_scope(value: Mapping[str, Any]) -> None:
    expected = {"scope_id", "scope_contract_ref"}
    if not isinstance(value, Mapping) or set(value) != expected:
        raise CanonicalValidationError("package scope has invalid fields")
    if not isinstance(value.get("scope_id"), str) or not value["scope_id"]:
        raise CanonicalValidationError("package scope_id is required")
    validate_canonical_ref(value["scope_contract_ref"])
    if value["scope_contract_ref"]["object_type"] != "CONTRACT":
        raise CanonicalValidationError("scope_contract_ref must target CONTRACT")


def _validate_policy_binding(value: Mapping[str, Any]) -> None:
    expected = {"gate_policy_ref", "control_autonomy", "repair_policy", "policy_digest"}
    if not isinstance(value, Mapping) or set(value) != expected:
        raise CanonicalValidationError("PolicyBinding has invalid fields")
    validate_canonical_ref(value["gate_policy_ref"])
    if value["gate_policy_ref"]["object_type"] != "CONTRACT":
        raise CanonicalValidationError("gate_policy_ref must target CONTRACT")
    if value["control_autonomy"] not in {"AUTONOMOUS", "REVIEW_GUARDED", "HUMAN_DECISION"}:
        raise CanonicalValidationError("PolicyBinding control_autonomy invalid")
    repair_policy = value["repair_policy"]
    expected_repair = {
        "allowed_classes", "max_attempts", "require_reverification",
        "require_fresh_independent_review", "escalation_conditions",
    }
    if not isinstance(repair_policy, Mapping) or set(repair_policy) != expected_repair:
        raise CanonicalValidationError("RepairPolicy has invalid fields")
    if not isinstance(repair_policy["allowed_classes"], list):
        raise CanonicalValidationError("RepairPolicy allowed_classes must be a list")
    max_attempts = repair_policy["max_attempts"]
    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts < 0:
        raise CanonicalValidationError("RepairPolicy max_attempts must be an integer >= 0")
    for field in ("require_reverification", "require_fresh_independent_review"):
        if not isinstance(repair_policy[field], bool):
            raise CanonicalValidationError(f"RepairPolicy {field} must be boolean")
    if not isinstance(repair_policy["escalation_conditions"], list):
        raise CanonicalValidationError("RepairPolicy escalation_conditions must be a list")
    validate_digest(value["policy_digest"])
    payload = {key: item for key, item in value.items() if key != "policy_digest"}
    if canonical_digest(payload) != value["policy_digest"]:
        raise CanonicalValidationError("PolicyBinding policy_digest mismatch")


def _validate_task_anchor(value: Mapping[str, Any] | None) -> None:
    if value is None:
        return
    if not isinstance(value, Mapping) or set(value) != {"revision", "relation"}:
        raise CanonicalValidationError("task_anchor requires exactly revision and relation")
    if value.get("relation") != "ancestor":
        raise CanonicalValidationError("task_anchor relation must be ancestor")
    if not isinstance(value.get("revision"), str) or not value["revision"]:
        raise CanonicalValidationError("task_anchor revision is required")


def validate_verification_bound_package(record: Mapping[str, Any]) -> None:
    missing = KIND_FIELDS["VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE"] - set(record)
    if missing:
        raise CanonicalValidationError(
            f"VerificationBoundImplementationPackage missing fields: {sorted(missing)}"
        )
    validate_trusted_basis(record["trusted_basis"])
    _validate_scope(record["scope"])
    validate_verification_binding(record["verification_binding"])
    _validate_policy_binding(record["policy_binding"])
    _validate_task_anchor(record["task_anchor"])
    validate_digest(record["package_digest"])
    if canonical_digest(record, self_digest_field="package_digest") != record["package_digest"]:
        raise CanonicalValidationError("package_digest mismatch")

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
    if kind in {"STAGE_OCCURRENCE", "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "ESCALATION"}:
        if "work_scope_ref" not in record:
            raise CanonicalValidationError("work_scope_ref is required")
        validate_work_scope_ref(record["work_scope_ref"])
    if kind == "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE":
        validate_verification_bound_package(record)
    if kind == "STAGE_OCCURRENCE":
        _validate_stage_ownership(record)
        state = record.get("state")
        if state not in {"OPEN", "TERMINAL"}:
            raise CanonicalValidationError("StageOccurrence state must be OPEN or TERMINAL")
        terminal = record.get("terminal")
        if state == "OPEN" and terminal is not None:
            raise CanonicalValidationError("OPEN StageOccurrence terminal must be null")
        if state == "TERMINAL" and not isinstance(terminal, Mapping):
            raise CanonicalValidationError("TERMINAL StageOccurrence requires terminal facts")
        schedule_basis = record.get("schedule_basis")
        if not isinstance(schedule_basis, Mapping):
            raise CanonicalValidationError("ScheduleBasis must be an object")
        bindings = schedule_basis.get("required_child_acceptance_bindings")
        if not isinstance(bindings, list):
            raise CanonicalValidationError("required_child_acceptance_bindings is required")
        child_ids = []
        for binding in bindings:
            validate_required_child_acceptance_binding(binding)
            child_ids.append(binding["child_work_scope_ref"]["id"])
        if len(set(child_ids)) != len(child_ids):
            raise CanonicalValidationError("duplicate REQUIRED child binding")
        if child_ids != sorted(child_ids):
            raise CanonicalValidationError("REQUIRED child bindings must be sorted by WorkScope id")
        input_refs = record.get("input_refs")
        if not isinstance(input_refs, list):
            raise CanonicalValidationError("input_refs must be a list")
        _validate_ref_list(input_refs, duplicate_message="duplicate input ref")


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
        if record.get("work_scope_ref") != first.get("work_scope_ref"):
            raise CanonicalValidationError("work_scope_ref is immutable across revisions")
    if first["kind"] == "STAGE_OCCURRENCE":
        for record in records[1:]:
            if record.get("schedule_basis") != first.get("schedule_basis"):
                raise CanonicalValidationError("ScheduleBasis is immutable across revisions")
        terminal_indexes = [i for i, r in enumerate(records) if r["state"] == "TERMINAL"]
        if len(terminal_indexes) > 1:
            raise CanonicalValidationError("StageOccurrence may have only one terminal revision")
        if terminal_indexes and terminal_indexes[0] != len(records) - 1:
            raise CanonicalValidationError("no StageOccurrence revision may follow terminal")
