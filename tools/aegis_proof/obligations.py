"""Deterministic ProofObligation generation from an exact validated VerificationSpec."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .domain import ObligationIdentityCodec, ProofCodec, ProofValidationError
from .spec import VerificationSpecValidator


@dataclass(frozen=True)
class ObligationSet:
    verification_spec_digest: str
    coverage_basis_digest: str
    generator: Mapping[str, str]
    obligations: tuple[Mapping[str, Any], ...]
    obligation_ids: tuple[str, ...]
    obligation_set_digest: str
    obligation_count: int


class ObligationGenerator:
    @staticmethod
    def generate(
        spec: Mapping[str, Any], *, generator_version: str, generator_name: str = "aegis-proof"
    ) -> ObligationSet:
        validation = VerificationSpecValidator.validate(spec)
        if not validation.valid:
            codes = ",".join(f.code for f in validation.findings)
            raise ProofValidationError(f"VerificationSpec is invalid: {codes}")
        if not isinstance(generator_version, str) or not generator_version:
            raise ProofValidationError("generator_version is required")

        spec_digest = ProofCodec.digest(spec)
        coverage = spec["coverage_basis"]
        coverage_digest = coverage["requirement_set_digest"]
        contract_by_id = {contract["id"]: contract for contract in spec["proof_contracts"]}
        obligations: list[dict[str, Any]] = []

        for claim in spec["claims"]:
            contract = contract_by_id[claim["proof_contract_id"]]
            for descriptor in contract["resolved_obligations"]:
                subject_id = f"{claim['id']}|{contract['id']}"
                key = ObligationIdentityCodec.semantic_key(
                    verification_spec_digest=spec_digest,
                    subject_kind="CLAIM",
                    subject_id=subject_id,
                    obligation_kind=descriptor["kind"],
                    source_key=descriptor["source_key"],
                )
                obligations.append(
                    {
                        "id": ObligationIdentityCodec.id_from_key(key),
                        "id_scheme": ObligationIdentityCodec.ID_SCHEME,
                        "verification_spec": {
                            "id": spec["id"],
                            "version": spec["version"],
                            "digest": spec_digest,
                        },
                        "subject": {
                            "kind": "CLAIM",
                            "claim_id": claim["id"],
                            "proof_contract_id": contract["id"],
                        },
                        "kind": descriptor["kind"],
                        "source_key": descriptor["source_key"],
                        "evaluation_mode": descriptor["evaluation_mode"],
                        "required_evidence_types": list(descriptor["required_evidence_types"]),
                        "pass_condition": descriptor["pass_condition"],
                    }
                )

        if coverage["mode"] == "REVIEW_DECLARED":
            key = ObligationIdentityCodec.semantic_key(
                verification_spec_digest=spec_digest,
                subject_kind="COVERAGE_BASIS",
                subject_id=coverage_digest,
                obligation_kind="COVERAGE_COMPLETENESS",
                source_key="coverage-completeness",
            )
            obligations.append(
                {
                    "id": ObligationIdentityCodec.id_from_key(key),
                    "id_scheme": ObligationIdentityCodec.ID_SCHEME,
                    "verification_spec": {
                        "id": spec["id"],
                        "version": spec["version"],
                        "digest": spec_digest,
                    },
                    "subject": {
                        "kind": "COVERAGE_BASIS",
                        "coverage_basis_digest": coverage_digest,
                    },
                    "kind": "COVERAGE_COMPLETENESS",
                    "source_key": "coverage-completeness",
                    "evaluation_mode": "REVIEW_REQUIRED",
                    "required_evidence_types": ["REVIEWER"],
                    "pass_condition": (
                        "CONTROL_REVIEW confirms the declared Requirement universe faithfully "
                        "represents the pinned upstream Authority scope"
                    ),
                }
            )

        obligations.sort(key=lambda item: item["id"])
        obligation_ids = tuple(item["id"] for item in obligations)
        generator = {"name": generator_name, "version": generator_version}
        envelope = {
            "verification_spec_digest": spec_digest,
            "coverage_basis_digest": coverage_digest,
            "generator": generator,
            "obligation_ids": list(obligation_ids),
            "obligation_count": len(obligation_ids),
        }
        return ObligationSet(
            verification_spec_digest=spec_digest,
            coverage_basis_digest=coverage_digest,
            generator=generator,
            obligations=tuple(obligations),
            obligation_ids=obligation_ids,
            obligation_set_digest=ProofCodec.digest(envelope),
            obligation_count=len(obligation_ids),
        )
