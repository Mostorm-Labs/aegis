from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence
from .domain import ObligationIdentityCodec, ProofCodec

class ReviewDelta(str, Enum):
    DECLARED = "DECLARED"
    EXISTING_REVIEW_ONLY = "EXISTING_REVIEW_ONLY"
    UNDECLARED = "UNDECLARED"
    STRUCTURALLY_UNSATISFIABLE = "STRUCTURALLY_UNSATISFIABLE"

@dataclass(frozen=True)
class CompletenessResult:
    complete: bool
    expected_ids: tuple[str, ...]
    actual_ids: tuple[str, ...]
    missing_ids: tuple[str, ...]
    unexpected_ids: tuple[str, ...]

class IndependentCompletenessChecker:
    def expected_ids(self, *, verification_spec: Mapping[str, Any]) -> tuple[str, ...]:
        spec_digest = ProofCodec.digest(verification_spec)
        contracts = {item["id"]: item for item in verification_spec.get("proof_contracts", ())}
        ids = []
        for claim in verification_spec.get("claims", ()):
            contract = contracts.get(claim.get("proof_contract_id"))
            if not contract:
                continue
            for descriptor in contract.get("resolved_obligations", ()):
                key = ObligationIdentityCodec.semantic_key(
                    verification_spec_digest=spec_digest,
                    subject_kind="CLAIM",
                    subject_id=f"{claim['id']}|{contract['id']}",
                    obligation_kind=descriptor["kind"],
                    source_key=descriptor["source_key"],
                )
                ids.append(ObligationIdentityCodec.id_from_key(key))
        coverage = verification_spec.get("coverage_basis", {})
        if coverage.get("mode") == "REVIEW_DECLARED":
            key = ObligationIdentityCodec.semantic_key(
                verification_spec_digest=spec_digest,
                subject_kind="COVERAGE_BASIS",
                subject_id=str(coverage.get("requirement_set_digest")),
                obligation_kind="COVERAGE_COMPLETENESS",
                source_key="coverage-completeness",
            )
            ids.append(ObligationIdentityCodec.id_from_key(key))
        return tuple(sorted(ids))

    def check(self, *, verification_spec: Mapping[str, Any], actual_obligation_set: Mapping[str, Any]) -> CompletenessResult:
        expected = self.expected_ids(verification_spec=verification_spec)
        actual = tuple(sorted(str(i) for i in actual_obligation_set.get("obligation_ids", ())))
        missing = tuple(sorted(set(expected) - set(actual)))
        unexpected = tuple(sorted(set(actual) - set(expected)))
        return CompletenessResult(not missing and not unexpected, expected, actual, missing, unexpected)

class ReviewContractDiffer:
    def classify(self, *, requested_requirement: Mapping[str, Any], verification_spec: Mapping[str, Any], package: Mapping[str, Any]) -> ReviewDelta:
        field = requested_requirement.get("field")
        spec_fields = set(verification_spec.get("declared_review_fields", ()))
        package_fields = set(package.get("declared_review_fields", ()))
        if requested_requirement.get("structurally_unsatisfiable"):
            return ReviewDelta.STRUCTURALLY_UNSATISFIABLE
        if field in spec_fields and field in package_fields:
            return ReviewDelta.DECLARED
        if field in spec_fields and field not in package_fields:
            return ReviewDelta.EXISTING_REVIEW_ONLY
        return ReviewDelta.UNDECLARED

class ReviewBundleAdapter:
    def build(self, *, package_ref: Mapping[str, Any], result_ref: Mapping[str, Any], evidence_input_refs: Sequence[Mapping[str, Any]], proof_evaluation_ref: Mapping[str, Any], completeness: CompletenessResult) -> Mapping[str, Any]:
        refs = [package_ref, result_ref, proof_evaluation_ref, *evidence_input_refs]
        resolvable = all(bool(ref.get("reviewer_resolvable")) and bool(ref.get("ref")) for ref in refs)
        ready = resolvable and completeness.complete
        return {"package_ref": package_ref, "result_ref": result_ref, "evidence_input_refs": list(evidence_input_refs), "proof_evaluation_ref": proof_evaluation_ref, "completeness": completeness, "review_ready": ready, "blocker": None if ready else "BLOCKED_EVIDENCE"}
