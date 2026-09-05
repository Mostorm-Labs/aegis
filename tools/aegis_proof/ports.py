from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Protocol

@dataclass(frozen=True)
class ObservationRecord:
    fact_key: str
    producer_class: str
    producer_id: str
    subject_ref: str
    value: Any
    provider_run_ref: str | None = None

@dataclass(frozen=True)
class ObservationBatch:
    producer_id: str
    complete: bool
    observations: tuple[ObservationRecord, ...]

@dataclass(frozen=True)
class ImmutableArtifactLocator:
    provider: str
    native_id: str
    ref: str
    digest: str
    reviewer_resolvable: bool

class ArtifactStorePort(Protocol):
    def materialize(self, data: bytes, *, media_type: str, metadata: Mapping[str, Any]) -> ImmutableArtifactLocator: ...
    def resolve(self, locator: ImmutableArtifactLocator) -> bytes: ...

class ExactRefResolverPort(Protocol):
    def resolve(self, ref: Mapping[str, Any]) -> Mapping[str, Any]: ...

class ResultMaterializationPort(Protocol):
    def resolve_result(self, result_ref: Mapping[str, Any]) -> Mapping[str, Any]: ...
