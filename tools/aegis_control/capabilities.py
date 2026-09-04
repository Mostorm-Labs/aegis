from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Protocol, runtime_checkable


@dataclass(frozen=True)
class CapabilityProfile:
    process: str
    capabilities: FrozenSet[str]
    credential_refs: FrozenSet[str] = frozenset()


def api_capability_profile() -> CapabilityProfile:
    return CapabilityProfile(
        process="aegis-control-api",
        capabilities=frozenset({
            "CONTROL_QUERY", "CONTROL_MUTATION_VIA_SERVICE", "TRUST_RESOLUTION",
            "PROJECTION", "POLICY", "SCHEDULER", "RECOVERY_COORDINATION",
            "PROVIDER_EVENT_INGRESS",
        }),
    )


def worker_capability_profile() -> CapabilityProfile:
    return CapabilityProfile(
        process="aegis-control-worker",
        capabilities=frozenset({
            "OUTBOX_CLAIM", "DELIVERY_METADATA", "PROVIDER_DELIVERY", "PROVIDER_QUERY",
            "RECONCILIATION_REQUEST", "PROVIDER_OBSERVATION_SUBMIT", "PLATFORM_CAPABILITY_QUERY",
        }),
    )


@runtime_checkable
class WorkerControlPort(Protocol):
    def claim_ready_outbox(self, *, limit: int): ...
    def record_delivery_attempt(self, *, outbox_id: str, metadata): ...
    def request_reconciliation(self, *, occurrence_id: str): ...
    def submit_provider_observation(self, *, observation): ...
    def query_platform_capability(self, *, provider_class: str): ...
