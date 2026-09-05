"""Deterministic VerificationSpec validation without semantic authoring decisions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tools.aegis_control.canonical import CanonicalValidationError, canonical_digest, validate_digest


@dataclass(frozen=True)
class ValidationFinding:
    code: str
    message: str
    path: str


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    findings: tuple[ValidationFinding, ...]


class VerificationSpecValidator:
    SPEC_FIELDS = {
        "schema_version", "id", "scope", "version", "authority_refs",
        "coverage_basis", "claims", "proof_contracts", "extensions",
    }
    COVERAGE_FIELDS = {
        "authority_ref", "authority_version", "authority_digest", "source_ref",
        "mode", "requirements", "requirement_set_digest",
    }
    COVERAGE_MODES = {"EXACT_SET", "REVIEW_DECLARED"}
    CONTRACT_MODES = {"GENERATED", "EXPLICIT", "CUSTOM"}
    OBLIGATION_KINDS = {
        "INVARIANT", "ORACLE", "FIXTURE", "PROBE", "METRIC", "THRESHOLD",
        "EVIDENCE", "CHALLENGE", "QUALIFICATION", "PROVENANCE",
        "COVERAGE_COMPLETENESS",
    }
    EVALUATION_MODES = {"DETERMINISTIC", "REVIEW_REQUIRED"}

    @classmethod
    def validate(cls, spec: Mapping[str, Any]) -> ValidationResult:
        findings: list[ValidationFinding] = []

        def add(code: str, message: str, path: str) -> None:
            findings.append(ValidationFinding(code, message, path))

        if not isinstance(spec, Mapping):
            return ValidationResult(False, (ValidationFinding("SPEC_NOT_OBJECT", "VerificationSpec must be an object", "$"),))
        missing = cls.SPEC_FIELDS - set(spec)
        unknown = set(spec) - cls.SPEC_FIELDS
        if missing:
            add("SPEC_MISSING_FIELDS", f"missing fields: {sorted(missing)}", "$")
        if unknown:
            add("SPEC_UNKNOWN_FIELDS", f"unknown fields: {sorted(unknown)}", "$")
        if spec.get("schema_version") != "0.1":
            add("SPEC_SCHEMA_VERSION", "schema_version must equal 0.1", "schema_version")
        for field in ("id", "scope", "version"):
            if not isinstance(spec.get(field), str) or not spec.get(field):
                add("SPEC_REQUIRED_STRING", f"{field} must be non-empty", field)
        authority_refs = spec.get("authority_refs")
        if not isinstance(authority_refs, list) or not authority_refs:
            add("SPEC_AUTHORITY_REFS", "authority_refs must be a non-empty list", "authority_refs")

        coverage = spec.get("coverage_basis")
        requirement_ids: list[str] = []
        if not isinstance(coverage, Mapping):
            add("COVERAGE_BASIS_NOT_OBJECT", "coverage_basis must be an object", "coverage_basis")
        else:
            missing_cov = cls.COVERAGE_FIELDS - set(coverage)
            unknown_cov = set(coverage) - cls.COVERAGE_FIELDS
            if missing_cov:
                add("COVERAGE_BASIS_MISSING_FIELDS", f"missing fields: {sorted(missing_cov)}", "coverage_basis")
            if unknown_cov:
                add("COVERAGE_BASIS_UNKNOWN_FIELDS", f"unknown fields: {sorted(unknown_cov)}", "coverage_basis")
            if coverage.get("mode") not in cls.COVERAGE_MODES:
                add("COVERAGE_BASIS_MODE", "unknown coverage mode", "coverage_basis.mode")
            for field in ("authority_ref", "source_ref"):
                if not isinstance(coverage.get(field), str) or not coverage.get(field):
                    add("COVERAGE_BASIS_REQUIRED_STRING", f"{field} must be non-empty", f"coverage_basis.{field}")
            authority_version = coverage.get("authority_version")
            if authority_version is not None and not isinstance(authority_version, str):
                add("COVERAGE_BASIS_AUTHORITY_VERSION", "authority_version must be string or null", "coverage_basis.authority_version")
            for field in ("authority_digest", "requirement_set_digest"):
                try:
                    validate_digest(coverage.get(field))
                except CanonicalValidationError:
                    add("COVERAGE_BASIS_DIGEST", f"{field} must be an exact sha256 digest", f"coverage_basis.{field}")
            requirements = coverage.get("requirements")
            if not isinstance(requirements, list):
                add("COVERAGE_BASIS_REQUIREMENTS", "requirements must be a list", "coverage_basis.requirements")
            else:
                for index, requirement in enumerate(requirements):
                    path = f"coverage_basis.requirements[{index}]"
                    if not isinstance(requirement, Mapping) or set(requirement) != {"id", "ref"}:
                        add("COVERAGE_REQUIREMENT_SHAPE", "requirement requires exactly id/ref", path)
                        continue
                    requirement_id = requirement.get("id")
                    if not isinstance(requirement_id, str) or not requirement_id:
                        add("COVERAGE_REQUIREMENT_ID", "requirement id is required", f"{path}.id")
                        continue
                    ref = requirement.get("ref")
                    if ref is not None and (not isinstance(ref, str) or not ref):
                        add("COVERAGE_REQUIREMENT_REF", "requirement ref must be non-empty string or null", f"{path}.ref")
                    requirement_ids.append(requirement_id)
                if len(set(requirement_ids)) != len(requirement_ids):
                    add("COVERAGE_REQUIREMENT_DUPLICATE", "requirement ids must be unique", "coverage_basis.requirements")
                expected_digest = canonical_digest(sorted(requirement_ids))
                if coverage.get("requirement_set_digest") != expected_digest:
                    add("COVERAGE_REQUIREMENT_SET_DIGEST", "requirement_set_digest mismatch", "coverage_basis.requirement_set_digest")

        claims = spec.get("claims")
        contracts = spec.get("proof_contracts")
        claim_by_id: dict[str, Mapping[str, Any]] = {}
        contract_by_id: dict[str, Mapping[str, Any]] = {}
        covered: set[str] = set()

        if not isinstance(claims, list):
            add("CLAIMS_NOT_LIST", "claims must be a list", "claims")
            claims = []
        for index, claim in enumerate(claims):
            path = f"claims[{index}]"
            if not isinstance(claim, Mapping):
                add("CLAIM_NOT_OBJECT", "claim must be an object", path)
                continue
            claim_id = claim.get("id")
            if not isinstance(claim_id, str) or not claim_id:
                add("CLAIM_ID", "claim id is required", f"{path}.id")
                continue
            if claim_id in claim_by_id:
                add("CLAIM_DUPLICATE", "claim ids must be unique", f"{path}.id")
            claim_by_id[claim_id] = claim
            refs = claim.get("requirement_refs")
            if not isinstance(refs, list) or not refs or any(not isinstance(item, str) or not item for item in refs):
                add("CLAIM_REQUIREMENT_REFS", "claim requirement_refs must be a non-empty string list", f"{path}.requirement_refs")
                refs = []
            for requirement_ref in refs:
                if requirement_ref not in set(requirement_ids):
                    add(
                        "CLAIM_REQUIREMENT_OUTSIDE_COVERAGE_BASIS",
                        f"claim references out-of-basis requirement {requirement_ref}",
                        f"{path}.requirement_refs",
                    )
                else:
                    covered.add(requirement_ref)
            if not isinstance(claim.get("proof_contract_id"), str) or not claim.get("proof_contract_id"):
                add("CLAIM_PROOF_CONTRACT", "proof_contract_id is required", f"{path}.proof_contract_id")

        uncovered = sorted(set(requirement_ids) - covered)
        if uncovered:
            add("UNCOVERED_REQUIREMENTS", f"uncovered requirements: {uncovered}", "coverage_basis.requirements")

        if not isinstance(contracts, list):
            add("PROOF_CONTRACTS_NOT_LIST", "proof_contracts must be a list", "proof_contracts")
            contracts = []
        for index, contract in enumerate(contracts):
            path = f"proof_contracts[{index}]"
            if not isinstance(contract, Mapping):
                add("PROOF_CONTRACT_NOT_OBJECT", "ProofContract must be an object", path)
                continue
            contract_id = contract.get("id")
            if not isinstance(contract_id, str) or not contract_id:
                add("PROOF_CONTRACT_ID", "ProofContract id is required", f"{path}.id")
                continue
            if contract_id in contract_by_id:
                add("PROOF_CONTRACT_DUPLICATE", "ProofContract ids must be unique", f"{path}.id")
            contract_by_id[contract_id] = contract
            if contract.get("mode") not in cls.CONTRACT_MODES:
                add("PROOF_CONTRACT_MODE", "unknown ProofContract mode", f"{path}.mode")
            profile_ref = contract.get("profile_ref")
            if profile_ref is not None:
                if not isinstance(profile_ref, Mapping) or set(profile_ref) != {"id", "version"}:
                    add("PROOF_PROFILE_REF", "profile_ref requires exactly id/version", f"{path}.profile_ref")
                elif not all(isinstance(profile_ref.get(k), str) and profile_ref.get(k) for k in ("id", "version")):
                    add("PROOF_PROFILE_REF", "profile id/version must be exact non-empty strings", f"{path}.profile_ref")
            elif contract.get("mode") == "GENERATED":
                add("PROOF_PROFILE_REF", "GENERATED contract requires exact profile_ref", f"{path}.profile_ref")
            resolved = contract.get("resolved_obligations")
            if not isinstance(resolved, list):
                add("PROOF_CONTRACT_RESOLVED_OBLIGATIONS", "resolved_obligations must be a list", f"{path}.resolved_obligations")
                continue
            for obligation_index, obligation in enumerate(resolved):
                opath = f"{path}.resolved_obligations[{obligation_index}]"
                if not isinstance(obligation, Mapping):
                    add("PROOF_OBLIGATION_DESCRIPTOR", "resolved obligation must be an object", opath)
                    continue
                if obligation.get("kind") not in cls.OBLIGATION_KINDS - {"COVERAGE_COMPLETENESS"}:
                    add("PROOF_OBLIGATION_KIND", "unknown or invalid Claim-scoped obligation kind", f"{opath}.kind")
                if obligation.get("evaluation_mode") not in cls.EVALUATION_MODES:
                    add("PROOF_OBLIGATION_EVALUATION_MODE", "unknown evaluation_mode", f"{opath}.evaluation_mode")
                if not isinstance(obligation.get("source_key"), str) or not obligation.get("source_key"):
                    add("PROOF_OBLIGATION_SOURCE_KEY", "source_key is required", f"{opath}.source_key")
                evidence_types = obligation.get("required_evidence_types")
                if not isinstance(evidence_types, list) or any(not isinstance(item, str) or not item for item in evidence_types):
                    add("PROOF_OBLIGATION_EVIDENCE_TYPES", "required_evidence_types must be a string list", f"{opath}.required_evidence_types")
                if not isinstance(obligation.get("pass_condition"), str) or not obligation.get("pass_condition"):
                    add("PROOF_OBLIGATION_PASS_CONDITION", "pass_condition is required", f"{opath}.pass_condition")

        for claim_id, claim in claim_by_id.items():
            contract_id = claim.get("proof_contract_id")
            contract = contract_by_id.get(contract_id)
            if contract is None:
                add("CLAIM_PROOF_CONTRACT_MISSING", f"missing ProofContract {contract_id}", f"claims.{claim_id}.proof_contract_id")
            elif contract.get("claim_id") != claim_id:
                add("CLAIM_PROOF_CONTRACT_MISMATCH", "ProofContract claim_id mismatch", f"proof_contracts.{contract_id}.claim_id")

        return ValidationResult(not findings, tuple(findings))
