from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .api import ControlApi
from .mutation import MutationService
from .provider_events import AdapterCapability, ProviderEvent, ReconciledObservation, reconcile_provider_event


class CompositionError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class ProviderAuthProvenance:
    signature_verified: bool
    verifier_id: str
    source_id: str


_FORBIDDEN_WORKER_SURFACE = {
    "append_canonical", "_mutation_transaction", "advance_lane", "compare_and_advance_lane",
    "set_terminal", "terminate_occurrence", "set_gate_verdict", "record_gate_verdict",
}


class IntegratedControlPlane:
    def __init__(self, *, mutation_service: MutationService, worker_port, query_service=None):
        if not isinstance(mutation_service, MutationService):
            raise CompositionError("MUTATION_SERVICE_REQUIRED")
        for name in _FORBIDDEN_WORKER_SURFACE:
            if hasattr(worker_port, name):
                raise CompositionError("WORKER_SECOND_WRITER_CAPABILITY")
        self._mutation_service = mutation_service
        self.worker_port = worker_port
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

    def reconcile_provider_event(self, event: ProviderEvent, capability: AdapterCapability, *, auth: ProviderAuthProvenance, query: Callable[[str], Mapping]) -> ReconciledObservation:
        if not auth.signature_verified or not auth.verifier_id or not auth.source_id:
            raise CompositionError("PROVIDER_AUTH_PROVENANCE_REQUIRED")
        if event.signature_verified is not True or event.signature_verified != auth.signature_verified:
            raise CompositionError("PROVIDER_AUTH_PROVENANCE_MISMATCH")
        return reconcile_provider_event(event, capability, query=query)
