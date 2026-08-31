"""Typed deterministic external read ports used by CP-I04 verification.

The fake adapter models provider-owned truth for deterministic tests. It never
writes canonical Control Plane state and it never creates Gate/Proof truth.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping, Sequence

from .canonical import validate_canonical_ref
from .snapshot import SnapshotVerification, SourceSnapshotTokenCodec, format_time


@dataclass(frozen=True)
class ProviderCapability:
    callback_available: bool
    query_correlation_available: bool

    @property
    def full_autonomous_trust_capable(self) -> bool:
        return bool(self.query_correlation_available)


@dataclass(frozen=True)
class SourceSnapshot:
    source_kind: str
    adapter_id: str
    resource_key: str
    version_scheme: str
    version_value: str
    snapshot_token: str
    observed_at: str
    resolved_refs: tuple[Mapping[str, Any], ...]
    satisfies: bool
    ambiguous: bool
    conflict: bool


@dataclass(frozen=True)
class _ResourceState:
    version_scheme: str
    version_value: str
    resolved_refs: tuple[Mapping[str, Any], ...]
    satisfies: bool
    ambiguous: bool
    conflict: bool


class DeterministicExternalAdapter:
    """Deterministic queryable fake for one externally owned source kind."""

    def __init__(
        self,
        *,
        source_kind: str,
        adapter_id: str,
        secret: bytes,
        callback_available: bool,
        query_correlation_available: bool,
        clock: Callable[[], datetime] | None = None,
        snapshot_ttl_seconds: int = 10,
    ):
        if not source_kind or not adapter_id:
            raise ValueError("source_kind and adapter_id are required")
        self.source_kind = source_kind
        self.adapter_id = adapter_id
        self.capability = ProviderCapability(callback_available, query_correlation_available)
        self._codec = SourceSnapshotTokenCodec(secret)
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._snapshot_ttl_seconds = snapshot_ttl_seconds
        self._resources: dict[str, _ResourceState] = {}

    def set_resource(
        self,
        resource_key: str,
        *,
        version_scheme: str,
        version_value: str,
        resolved_refs: Sequence[Mapping[str, Any]],
        satisfies: bool,
        ambiguous: bool = False,
        conflict: bool = False,
    ) -> None:
        if not resource_key or not version_scheme or not version_value:
            raise ValueError("resource/version binding is required")
        refs = []
        for ref in resolved_refs:
            validate_canonical_ref(ref)
            refs.append(deepcopy(dict(ref)))
        self._resources[resource_key] = _ResourceState(
            version_scheme=version_scheme,
            version_value=version_value,
            resolved_refs=tuple(refs),
            satisfies=bool(satisfies),
            ambiguous=bool(ambiguous),
            conflict=bool(conflict),
        )

    def resolve(self, resource_key: str) -> SourceSnapshot:
        state = self._resources.get(resource_key)
        if state is None:
            raise KeyError(resource_key)
        observed = self._clock()
        if observed.tzinfo is None:
            observed = observed.replace(tzinfo=timezone.utc)
        expires = observed + timedelta(seconds=self._snapshot_ttl_seconds)
        payload = {
            "v": 1,
            "source_kind": self.source_kind,
            "adapter_id": self.adapter_id,
            "resource_key": resource_key,
            "version_scheme": state.version_scheme,
            "version_value": state.version_value,
            "observed_at": format_time(observed),
            "expires_at": format_time(expires),
        }
        token = self._codec.issue(payload)
        return SourceSnapshot(
            source_kind=self.source_kind,
            adapter_id=self.adapter_id,
            resource_key=resource_key,
            version_scheme=state.version_scheme,
            version_value=state.version_value,
            snapshot_token=token,
            observed_at=payload["observed_at"],
            resolved_refs=tuple(deepcopy(list(state.resolved_refs))),
            satisfies=state.satisfies,
            ambiguous=state.ambiguous,
            conflict=state.conflict,
        )

    def verify_snapshot(
        self,
        token: str,
        *,
        expected_resource_key: str,
    ) -> SnapshotVerification:
        state = self._resources.get(expected_resource_key)
        if state is None:
            return SnapshotVerification(False, "SNAPSHOT_RESOURCE_NOT_FOUND")
        return self._codec.verify(
            token,
            expected_source_kind=self.source_kind,
            expected_adapter_id=self.adapter_id,
            expected_resource_key=expected_resource_key,
            current_version_value=state.version_value,
            now=self._clock(),
        )
