"""Read-only external trust aggregation for CP-I04."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .canonical import canonical_digest
from .external_ports import DeterministicExternalAdapter, SourceSnapshot


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


class TrustResolver:
    """Aggregate provider-owned facts without creating a local verdict."""

    def __init__(self, adapters: Mapping[str, DeterministicExternalAdapter]):
        self._adapters = dict(adapters)

    def resolve_for_projection(self, requests: Sequence[TrustFactRequest]) -> TrustResolution:
        return self._resolve(requests)

    def resolve_for_mutation(self, requests: Sequence[TrustFactRequest]) -> TrustResolution:
        return self._resolve(requests)

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
                refs.append(ref)
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
