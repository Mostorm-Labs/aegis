"""Read-only external trust aggregation for CP-I04."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence

from .canonical import canonical_digest, validate_canonical_ref, validate_digest
from .external_ports import DeterministicExternalAdapter, SourceSnapshot


_GIT_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_SEMVER_RE = re.compile(
    r"^(?:0|[1-9][0-9]*)\."
    r"(?:0|[1-9][0-9]*)\."
    r"(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def _validate_exact_trust_ref(ref: Mapping[str, Any]) -> None:
    """Fail closed unless a CanonicalRef carries an exact trust-boundary identity.

    Generic CanonicalRef structure deliberately remains broader. CP-I04 authorization
    only accepts identity schemes whose exactness can be established locally from the
    accepted P12 contract. Native/governed schemes require an owning provider contract
    that can prove immutability; this bounded fake-adapter slice does not invent one.
    """

    validate_canonical_ref(ref)
    identity = ref["identity"]
    scheme = identity["scheme"]
    value = identity["value"]
    if scheme == "sha256":
        validate_digest(value)
        return
    if scheme == "git-sha":
        if not _GIT_SHA_RE.fullmatch(value):
            raise ValueError("git-sha trust identity must pin an exact commit/object id")
        return
    if scheme == "semantic-version":
        if not _SEMVER_RE.fullmatch(value):
            raise ValueError("semantic-version trust identity must pin an exact version")
        return
    raise ValueError("trust-boundary identity scheme is not proven exact/immutable")


@dataclass(frozen=True)
class TrustFactRequest:
    source_kind: str
    resource_key: str


@dataclass(frozen=True)
class TrustResolution:
    valid: bool
    code: str
    snapshots: tuple[SourceSnapshot, ...] = ()
    resolved_refs: tuple[Mapping[str, Any], ...] = ()


@dataclass(frozen=True)
class ChildAcceptanceSupport:
    accepted: bool
    code: str
    child_work_scope_ref: Mapping[str, Any]
    child_completion_occurrence_ref: Mapping[str, Any]
    acceptance_contract_refs: tuple[Mapping[str, Any], ...]
    acceptance_fact_refs: tuple[Mapping[str, Any], ...]
    acceptance_basis_digest: str
    snapshot_resolution: TrustResolution


class TrustResolver:
    """Aggregate provider-owned facts without creating a local durable verdict."""

    def __init__(
        self,
        adapters: Mapping[str, DeterministicExternalAdapter],
        *,
        acceptance_contract_sources: Mapping[str, TrustFactRequest] | None = None,
    ):
        self._adapters = dict(adapters)
        # Keys are canonical digests of the exact CONTRACT CanonicalRef. A stable
        # semantic contract id alone is intentionally insufficient to authorize.
        self._acceptance_contract_sources = dict(acceptance_contract_sources or {})

    def resolve_for_projection(self, requests: Sequence[TrustFactRequest]) -> TrustResolution:
        return self._resolve(requests)

    def resolve_for_mutation(self, requests: Sequence[TrustFactRequest]) -> TrustResolution:
        return self._resolve(requests)

    def resolve_child_acceptance(
        self,
        child_work_scope_ref: Mapping[str, Any],
        child_completion_occurrence_ref: Mapping[str, Any],
        acceptance_contract_refs: Sequence[Mapping[str, Any]],
    ) -> ChildAcceptanceSupport:
        try:
            validate_canonical_ref(child_completion_occurrence_ref)
            contracts = []
            requests = []
            seen_contract_ids: set[str] = set()
            seen_contract_keys: set[str] = set()
            for contract in acceptance_contract_refs:
                _validate_exact_trust_ref(contract)
                if contract.get("object_type") != "CONTRACT":
                    raise ValueError("acceptance contract ref must target CONTRACT")
                contract_id = contract.get("id")
                contract_key = canonical_digest(contract)
                if contract_id in seen_contract_ids or contract_key in seen_contract_keys:
                    return self._child_support(
                        False,
                        "CHILD_ACCEPTANCE_BASIS_AMBIGUOUS",
                        child_work_scope_ref,
                        child_completion_occurrence_ref,
                        acceptance_contract_refs,
                        TrustResolution(False, "TRUST_FACT_DUPLICATE"),
                    )
                seen_contract_ids.add(contract_id)
                seen_contract_keys.add(contract_key)
                request = self._acceptance_contract_sources.get(contract_key)
                if request is None:
                    return self._child_support(
                        False,
                        "REQUIRED_CHILD_WORK_NOT_ACCEPTED",
                        child_work_scope_ref,
                        child_completion_occurrence_ref,
                        acceptance_contract_refs,
                        TrustResolution(False, "TRUST_CONTRACT_BINDING_MISSING"),
                    )
                contracts.append(deepcopy(dict(contract)))
                requests.append(request)
        except (TypeError, ValueError):
            return self._child_support(
                False,
                "CHILD_ACCEPTANCE_BASIS_AMBIGUOUS",
                child_work_scope_ref,
                child_completion_occurrence_ref,
                acceptance_contract_refs,
                TrustResolution(False, "TRUST_BASIS_AMBIGUOUS"),
            )

        resolution = self.resolve_for_mutation(requests)
        if not resolution.valid:
            code = (
                "CHILD_ACCEPTANCE_BASIS_AMBIGUOUS"
                if resolution.code in {"TRUST_BASIS_AMBIGUOUS", "TRUST_FACT_DUPLICATE"}
                else "CHILD_ACCEPTANCE_BASIS_CONFLICT"
                if resolution.code == "TRUST_BASIS_CONFLICT"
                else "REQUIRED_CHILD_WORK_NOT_ACCEPTED"
            )
            return self._child_support(
                False,
                code,
                child_work_scope_ref,
                child_completion_occurrence_ref,
                contracts,
                resolution,
            )

        try:
            if len(resolution.snapshots) != len(contracts):
                raise ValueError("acceptance contract resolution cardinality mismatch")
            for snapshot in resolution.snapshots:
                if not snapshot.resolved_refs:
                    return self._child_support(
                        False,
                        "REQUIRED_CHILD_WORK_NOT_ACCEPTED",
                        child_work_scope_ref,
                        child_completion_occurrence_ref,
                        contracts,
                        TrustResolution(False, "TRUST_ACCEPTANCE_FACT_MISSING"),
                    )
                for ref in snapshot.resolved_refs:
                    _validate_exact_trust_ref(ref)
        except (TypeError, ValueError):
            return self._child_support(
                False,
                "CHILD_ACCEPTANCE_BASIS_AMBIGUOUS",
                child_work_scope_ref,
                child_completion_occurrence_ref,
                contracts,
                TrustResolution(False, "TRUST_BASIS_AMBIGUOUS"),
            )

        return self._child_support(
            True,
            "CHILD_ACCEPTED_FOR_PARENT",
            child_work_scope_ref,
            child_completion_occurrence_ref,
            contracts,
            resolution,
        )

    def _child_support(
        self,
        accepted: bool,
        code: str,
        child_work_scope_ref: Mapping[str, Any],
        child_completion_occurrence_ref: Mapping[str, Any],
        acceptance_contract_refs: Sequence[Mapping[str, Any]],
        resolution: TrustResolution,
    ) -> ChildAcceptanceSupport:
        facts = tuple(deepcopy(list(resolution.resolved_refs))) if resolution.valid else ()
        contracts = tuple(deepcopy([dict(ref) for ref in acceptance_contract_refs]))
        payload = {
            "child_work_scope_ref": deepcopy(dict(child_work_scope_ref)),
            "child_completion_occurrence_ref": deepcopy(dict(child_completion_occurrence_ref)),
            "acceptance_contract_refs": list(contracts),
            "acceptance_fact_refs": list(facts),
        }
        return ChildAcceptanceSupport(
            accepted=accepted,
            code=code,
            child_work_scope_ref=deepcopy(dict(child_work_scope_ref)),
            child_completion_occurrence_ref=deepcopy(dict(child_completion_occurrence_ref)),
            acceptance_contract_refs=contracts,
            acceptance_fact_refs=facts,
            acceptance_basis_digest=canonical_digest(payload),
            snapshot_resolution=resolution,
        )

    def _resolve(self, requests: Sequence[TrustFactRequest]) -> TrustResolution:
        snapshots: list[SourceSnapshot] = []
        refs: list[Mapping[str, Any]] = []
        seen_ref_digests: set[str] = set()
        for request in requests:
            adapter = self._adapters.get(request.source_kind)
            if adapter is None:
                return TrustResolution(False, "TRUST_SOURCE_MISSING")
            try:
                snapshot = adapter.resolve(request.resource_key)
            except KeyError:
                return TrustResolution(False, "TRUST_RESOURCE_MISSING")
            verification = adapter.verify_snapshot(
                snapshot.snapshot_token,
                expected_resource_key=request.resource_key,
            )
            if not verification.valid:
                return TrustResolution(False, verification.code)
            if snapshot.ambiguous:
                return TrustResolution(False, "TRUST_BASIS_AMBIGUOUS")
            if snapshot.conflict:
                return TrustResolution(False, "TRUST_BASIS_CONFLICT")
            if not snapshot.satisfies:
                return TrustResolution(False, "TRUST_BASIS_DENIED")
            snapshots.append(snapshot)
            for ref in snapshot.resolved_refs:
                digest = canonical_digest(ref)
                if digest in seen_ref_digests:
                    return TrustResolution(False, "TRUST_FACT_DUPLICATE")
                seen_ref_digests.add(digest)
                refs.append(deepcopy(dict(ref)))
        return TrustResolution(True, "TRUST_VALID", tuple(snapshots), tuple(refs))

    def verify_freshness(self, resolution: TrustResolution) -> TrustResolution:
        if not resolution.valid:
            return resolution
        for snapshot in resolution.snapshots:
            adapter = self._adapters.get(snapshot.source_kind)
            if adapter is None:
                return TrustResolution(False, "TRUST_SOURCE_MISSING")
            verification = adapter.verify_snapshot(
                snapshot.snapshot_token,
                expected_resource_key=snapshot.resource_key,
            )
            if not verification.valid:
                return TrustResolution(False, verification.code)
        return resolution
