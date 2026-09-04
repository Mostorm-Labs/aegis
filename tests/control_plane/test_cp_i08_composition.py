from __future__ import annotations

import tempfile
import unittest

from tools.aegis_control.mutation import MutationService
from tools.aegis_control.provider_events import ProviderEvent, github_ci_adapter_capability
from tools.aegis_control.store import ControlStore


class _GoodWorkerPort:
    def claim_ready_outbox(self, *, limit: int): return []
    def record_delivery_attempt(self, *, outbox_id: str, metadata): return None
    def request_reconciliation(self, *, occurrence_id: str): return None
    def submit_provider_observation(self, *, observation): return None
    def query_platform_capability(self, *, provider_class: str): return {"provider_class": provider_class}


class _BadWorkerPort(_GoodWorkerPort):
    def append_canonical(self, record): return record


class CpI08CompositionRedTests(unittest.TestCase):
    def test_composition_binds_exact_mutation_service_and_no_second_writer(self):
        from tools.aegis_control.composition import IntegratedControlPlane
        with tempfile.TemporaryDirectory() as td:
            mutation = MutationService(ControlStore(f"{td}/control.db"))
            composition = IntegratedControlPlane(mutation_service=mutation, worker_port=_GoodWorkerPort())
            self.assertIs(mutation, composition.mutation_service)
            self.assertIs(mutation, composition.api_mutation_service)
            self.assertEqual("control-mutation", composition.canonical_writer_identity)

    def test_worker_with_canonical_write_surface_is_rejected(self):
        from tools.aegis_control.composition import CompositionError, IntegratedControlPlane
        with tempfile.TemporaryDirectory() as td:
            mutation = MutationService(ControlStore(f"{td}/control.db"))
            with self.assertRaises(CompositionError) as ctx:
                IntegratedControlPlane(mutation_service=mutation, worker_port=_BadWorkerPort())
            self.assertEqual("WORKER_SECOND_WRITER_CAPABILITY", ctx.exception.code)

    def test_post_auth_provider_provenance_is_required_before_query(self):
        from tools.aegis_control.composition import CompositionError, IntegratedControlPlane, ProviderAuthProvenance
        calls = []
        with tempfile.TemporaryDirectory() as td:
            composition = IntegratedControlPlane(mutation_service=MutationService(ControlStore(f"{td}/control.db")), worker_port=_GoodWorkerPort())
            event = ProviderEvent("evt-1", "github", "workflow_run", "run-1", "2026-09-01T00:00:00Z", True, {"conclusion": "failure"})
            with self.assertRaises(CompositionError) as ctx:
                composition.reconcile_provider_event(
                    event,
                    github_ci_adapter_capability(),
                    auth=ProviderAuthProvenance(signature_verified=True, verifier_id="", source_id="github-webhook"),
                    query=lambda key: calls.append(key) or {"resource": key},
                )
            self.assertEqual("PROVIDER_AUTH_PROVENANCE_REQUIRED", ctx.exception.code)
            self.assertEqual([], calls)


if __name__ == "__main__": unittest.main()
