from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .api import ControlApi
from .mutation import MutationService
from .provider_events import AdapterCapability, ProviderEvent, reconcile_provider_event
from .store import ControlStore


class CompositionError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class ProviderAuthProvenance:
    signature_verified: bool
    verifier_id: str
    source_id: str


@dataclass(frozen=True)
class IntegratedReconciledObservation:
    event_id: str
    observation: Mapping
    truth_source: str
    auth_provenance: ProviderAuthProvenance
    provider_class: str


_FORBIDDEN_WORKER_SURFACE = {
    "append_canonical", "_mutation_transaction", "advance_lane", "compare_and_advance_lane",
    "set_terminal", "terminate_occurrence", "set_gate_verdict", "record_gate_verdict",
}
_FORBIDDEN_WORKER_CARRIERS = {
    "store", "_store", "control_store", "_control_store", "mutation_service", "_mutation_service",
}
_REQUIRED_WORKER_METHODS = (
    "claim_ready_outbox", "record_delivery_attempt", "request_reconciliation",
    "submit_provider_observation", "query_platform_capability",
)


def _validate_worker_target(worker_port) -> None:
    for name in _REQUIRED_WORKER_METHODS:
        if not callable(getattr(worker_port, name, None)):
            raise CompositionError("WORKER_OPERATIONAL_CAPABILITY_REQUIRED")
    for name in _FORBIDDEN_WORKER_SURFACE | _FORBIDDEN_WORKER_CARRIERS:
        if hasattr(worker_port, name):
            raise CompositionError("WORKER_SECOND_WRITER_CAPABILITY")
    values = vars(worker_port).values() if hasattr(worker_port, "__dict__") else ()
    for value in values:
        if isinstance(value, (MutationService, ControlStore)) or hasattr(value, "_mutation_transaction"):
            raise CompositionError("WORKER_SECOND_WRITER_CAPABILITY")


class RestrictedWorkerPort:
    __slots__ = (
        "__claim_ready_outbox", "__record_delivery_attempt", "__request_reconciliation",
        "__submit_provider_observation", "__query_platform_capability",
    )

    def __init__(self, worker_port):
        _validate_worker_target(worker_port)
        self.__claim_ready_outbox = worker_port.claim_ready_outbox
        self.__record_delivery_attempt = worker_port.record_delivery_attempt
        self.__request_reconciliation = worker_port.request_reconciliation
        self.__submit_provider_observation = worker_port.submit_provider_observation
        self.__query_platform_capability = worker_port.query_platform_capability

    def claim_ready_outbox(self, *, limit: int):
        return self.__claim_ready_outbox(limit=limit)

    def record_delivery_attempt(self, *, outbox_id: str, metadata):
        return self.__record_delivery_attempt(outbox_id=outbox_id, metadata=metadata)

    def request_reconciliation(self, *, occurrence_id: str):
        return self.__request_reconciliation(occurrence_id=occurrence_id)

    def submit_provider_observation(self, *, observation):
        return self.__submit_provider_observation(observation=observation)

    def query_platform_capability(self, *, provider_class: str):
        return self.__query_platform_capability(provider_class=provider_class)


class IntegratedControlPlane:
    def __init__(self, *, mutation_service: MutationService, worker_port, query_service=None):
        if not isinstance(mutation_service, MutationService):
            raise CompositionError("MUTATION_SERVICE_REQUIRED")
        self._mutation_service = mutation_service
        self.worker_port = RestrictedWorkerPort(worker_port)
        self.api = ControlApi(mutation_service=mutation_service, query_service=query_service)

    @property
    def mutation_service(self) -> MutationService:
        return self._mutation_service

    @property
    def api_mutation_service(self) -> MutationService:
        return self.api._mutation_service

    @property
    def canonical_writer_identity(self) -> str:
        return "control-mutation"

    def reconcile_provider_event(self, event: ProviderEvent, capability: AdapterCapability, *, auth: ProviderAuthProvenance, query: Callable[[str], Mapping]) -> IntegratedReconciledObservation:
        if not auth.signature_verified or not auth.verifier_id or not auth.source_id:
            raise CompositionError("PROVIDER_AUTH_PROVENANCE_REQUIRED")
        if event.signature_verified is not True or event.signature_verified != auth.signature_verified:
            raise CompositionError("PROVIDER_AUTH_PROVENANCE_MISMATCH")
        resolved = reconcile_provider_event(event, capability, query=query)
        return IntegratedReconciledObservation(
            event_id=resolved.event_id,
            observation=resolved.observation,
            truth_source=resolved.truth_source,
            auth_provenance=auth,
            provider_class=capability.provider_class,
        )
