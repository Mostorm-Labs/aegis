"""Pure proof-domain canonical identity helpers for Verification Productization."""
from __future__ import annotations

from typing import Any, Mapping

from tools.aegis_control.canonical import (
    CanonicalValidationError,
    canonical_digest,
    canonical_dumps,
    validate_digest,
)


class ProofValidationError(ValueError):
    """Raised when accepted Proof Plane semantics cannot be represented exactly."""


class ProofCodec:
    @staticmethod
    def canonicalize(value: Any) -> str:
        try:
            return canonical_dumps(value)
        except CanonicalValidationError as exc:
            raise ProofValidationError(str(exc)) from exc

    @staticmethod
    def digest(value: Any) -> str:
        try:
            return canonical_digest(value)
        except CanonicalValidationError as exc:
            raise ProofValidationError(str(exc)) from exc


class ObligationIdentityCodec:
    ID_SCHEME = "proof-obligation-v0.1"
    SUBJECT_KINDS = {"CLAIM", "COVERAGE_BASIS"}

    @staticmethod
    def semantic_key(
        *,
        verification_spec_digest: str,
        subject_kind: str,
        subject_id: str,
        obligation_kind: str,
        source_key: str,
    ) -> dict[str, str]:
        try:
            validate_digest(verification_spec_digest)
        except CanonicalValidationError as exc:
            raise ProofValidationError(str(exc)) from exc
        if subject_kind not in ObligationIdentityCodec.SUBJECT_KINDS:
            raise ProofValidationError("unknown ProofObligation subject kind")
        for name, value in {
            "subject_id": subject_id,
            "obligation_kind": obligation_kind,
            "source_key": source_key,
        }.items():
            if not isinstance(value, str) or not value:
                raise ProofValidationError(f"{name} must be a non-empty string")
        return {
            "id_scheme": ObligationIdentityCodec.ID_SCHEME,
            "verification_spec_digest": verification_spec_digest,
            "subject_kind": subject_kind,
            "subject_id": subject_id,
            "obligation_kind": obligation_kind,
            "source_key": source_key,
        }

    @staticmethod
    def id_from_key(key: Mapping[str, Any]) -> str:
        expected = {
            "id_scheme",
            "verification_spec_digest",
            "subject_kind",
            "subject_id",
            "obligation_kind",
            "source_key",
        }
        if not isinstance(key, Mapping) or set(key) != expected:
            raise ProofValidationError("invalid ProofObligation semantic key")
        if key.get("id_scheme") != ObligationIdentityCodec.ID_SCHEME:
            raise ProofValidationError("ProofObligation id_scheme mismatch")
        digest = ProofCodec.digest(dict(key)).split(":", 1)[1]
        return f"obl_{digest}"


class EvidenceInputIdentity:
    PRODUCER_CLASSES = {"DETERMINISTIC_COLLECTOR", "EXECUTOR", "REVIEWER", "EXTERNAL"}

    @staticmethod
    def from_materialized_artifact(
        *, evidence_id: str, ref: str, digest: str, producer_class: str
    ) -> dict[str, str]:
        if not isinstance(evidence_id, str) or not evidence_id:
            raise ProofValidationError("evidence_id is required")
        if not isinstance(ref, str) or not ref:
            raise ProofValidationError("reviewer-resolvable evidence ref is required")
        if producer_class not in EvidenceInputIdentity.PRODUCER_CLASSES:
            raise ProofValidationError("unknown evidence producer_class")
        try:
            validate_digest(digest)
        except CanonicalValidationError as exc:
            raise ProofValidationError(str(exc)) from exc
        return {
            "evidence_id": evidence_id,
            "ref": ref,
            "digest": digest,
            "producer_class": producer_class,
        }
