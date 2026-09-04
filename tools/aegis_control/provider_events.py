from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class AdapterCapability:
    provider_class: str
    authenticated_events: bool
    durable_query: bool
    durable_correlation: bool
    autonomous_trust_sensitive: bool


@dataclass(frozen=True)
class ProviderEvent:
    event_id: str
    provider: str
    event_kind: str
    resource_hint: str
    observed_at: str
    signature_verified: bool
    payload_hint: Mapping[str, Any]


@dataclass(frozen=True)
class ReconciledObservation:
    event_id: str
    observation: Mapping[str, Any]
    truth_source: str


def github_ci_adapter_capability() -> AdapterCapability:
    return AdapterCapability(
        provider_class="GITHUB_REPOSITORY_CI",
        authenticated_events=True,
        durable_query=True,
        durable_correlation=True,
        autonomous_trust_sensitive=True,
    )


def validate_adapter_capability(capability: AdapterCapability) -> AdapterCapability:
    if not capability.provider_class:
        raise ValueError("provider_class required")
    if capability.autonomous_trust_sensitive:
        if not capability.authenticated_events:
            raise ValueError("autonomous trust-sensitive adapter requires authenticated events")
        if not capability.durable_query or not capability.durable_correlation:
            raise ValueError("callback-only adapter cannot claim autonomous trust-sensitive capability")
    return capability


def reconcile_by_query(resource_hint: str, capability: AdapterCapability, *, query: Callable[[str], Mapping[str, Any]]) -> ReconciledObservation:
    validate_adapter_capability(capability)
    if not capability.durable_query or not capability.durable_correlation:
        raise ValueError("provider lacks durable query/correlation")
    observation = dict(query(resource_hint))
    if not observation:
        raise ValueError("provider query returned no durable observation")
    return ReconciledObservation(event_id="QUERY_RECOVERY", observation=observation, truth_source="QUERY")


def reconcile_provider_event(event: ProviderEvent, capability: AdapterCapability, *, query: Callable[[str], Mapping[str, Any]]) -> ReconciledObservation:
    validate_adapter_capability(capability)
    if not event.signature_verified:
        raise ValueError("unverified provider event")
    if not capability.durable_query or not capability.durable_correlation:
        raise ValueError("provider event cannot support trust-sensitive reconciliation")
    observation = dict(query(event.resource_hint))
    if not observation:
        raise ValueError("provider query returned no durable observation")
    return ReconciledObservation(event_id=event.event_id, observation=observation, truth_source="QUERY")
