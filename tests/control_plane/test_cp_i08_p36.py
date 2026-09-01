from __future__ import annotations

import tempfile
import unittest

from tools.aegis_control.mutation import MutationService
from tools.aegis_control.provider_events import ProviderEvent, github_ci_adapter_capability
from tools.aegis_control.store import ControlStore

DAY = 24 * 60 * 60


class _LeakyStoreWorkerPort:
    def __init__(self, store):
        self.store = store
    def claim_ready_outbox(self, *, limit: int): return []
    def record_delivery_attempt(self, *, outbox_id: str, metadata): return None
    def request_reconciliation(self, *, occurrence_id: str): return None
    def submit_provider_observation(self, *, observation): return None
    def query_platform_capability(self, *, provider_class: str): return {"provider_class": provider_class}


class _LeakyMutationWorkerPort(_LeakyStoreWorkerPort):
    def __init__(self, mutation_service):
        self.mutation_service = mutation_service


class _SafeWorkerPort:
    def claim_ready_outbox(self, *, limit: int): return [limit]
    def record_delivery_attempt(self, *, outbox_id: str, metadata): return (outbox_id, metadata)
    def request_reconciliation(self, *, occurrence_id: str): return occurrence_id
    def submit_provider_observation(self, *, observation): return observation
    def query_platform_capability(self, *, provider_class: str): return {"provider_class": provider_class}


class CpI08P36RepairRedTests(unittest.TestCase):
    def test_worker_port_with_nested_store_or_mutation_service_is_rejected(self):
        from tools.aegis_control.composition import CompositionError, IntegratedControlPlane
        with tempfile.TemporaryDirectory() as td:
            store = ControlStore(f"{td}/control.db")
            mutation = MutationService(store)
            for worker in (_LeakyStoreWorkerPort(store), _LeakyMutationWorkerPort(mutation)):
                with self.assertRaises(CompositionError) as ctx:
                    IntegratedControlPlane(mutation_service=mutation, worker_port=worker)
                self.assertEqual("WORKER_SECOND_WRITER_CAPABILITY", ctx.exception.code)

    def test_worker_facing_proxy_exposes_only_five_operational_methods(self):
        from tools.aegis_control.composition import IntegratedControlPlane
        with tempfile.TemporaryDirectory() as td:
            mutation = MutationService(ControlStore(f"{td}/control.db"))
            composition = IntegratedControlPlane(mutation_service=mutation, worker_port=_SafeWorkerPort())
            public = {name for name in dir(composition.worker_port) if not name.startswith("_")}
            self.assertEqual({
                "claim_ready_outbox", "record_delivery_attempt", "request_reconciliation",
                "submit_provider_observation", "query_platform_capability",
            }, public)
            for leaked in ("store", "mutation_service", "append_canonical", "_mutation_transaction"):
                self.assertFalse(hasattr(composition.worker_port, leaked), leaked)

    def test_integrated_reconciliation_result_preserves_exact_provider_auth_provenance(self):
        from tools.aegis_control.composition import IntegratedControlPlane, ProviderAuthProvenance
        with tempfile.TemporaryDirectory() as td:
            composition = IntegratedControlPlane(
                mutation_service=MutationService(ControlStore(f"{td}/control.db")),
                worker_port=_SafeWorkerPort(),
            )
            auth = ProviderAuthProvenance(True, "github-webhook-hmac-v1", "github-actions-webhook")
            event = ProviderEvent("evt-p36", "github", "workflow_run", "run-p36", "2026-09-01T00:00:00Z", True, {})
            result = composition.reconcile_provider_event(
                event,
                github_ci_adapter_capability(),
                auth=auth,
                query=lambda key: {"resource": key, "status": "completed"},
            )
            self.assertEqual(auth, result.auth_provenance)
            self.assertEqual("GITHUB_REPOSITORY_CI", result.provider_class)
            self.assertEqual("QUERY", result.truth_source)

    def test_availability_window_requires_nonempty_window_id_and_preserves_it(self):
        from tools.aegis_control.availability import AvailabilityError, AvailabilityObservation, evaluate_window
        rows = [AvailabilityObservation("probe-1", "CONTROL_API_AVAILABILITY", "SUCCESS", synthetic_probe=True)]
        with self.assertRaises(AvailabilityError):
            evaluate_window(rows, required_probe_intervals=1, complete_window=True, window_id="")
        result = evaluate_window(rows, required_probe_intervals=1, complete_window=True, window_id="window-2026-09-01T00:00Z/PT1M")
        self.assertEqual("window-2026-09-01T00:00Z/PT1M", result.window_id)

    def test_retention_expiry_uses_explicit_recorded_now_and_policy_window(self):
        from tools.aegis_control.retention import retention_policy, evaluate_retention_at
        policy = retention_policy("HIGH_CARDINALITY_TRACE")
        before = evaluate_retention_at(
            "HIGH_CARDINALITY_TRACE",
            recorded_at_seconds=100,
            current_time_seconds=100 + 14 * DAY - 1,
            policy=policy,
        )
        at = evaluate_retention_at(
            "HIGH_CARDINALITY_TRACE",
            recorded_at_seconds=100,
            current_time_seconds=100 + 14 * DAY,
            policy=policy,
        )
        self.assertEqual("KEEP", before.action)
        self.assertEqual("EXPIRE_OPERATIONAL", at.action)
        self.assertEqual(14 * DAY, policy.window_seconds)
        self.assertEqual("HIGH_CARDINALITY_TRACE", policy.record_class)

    def test_raw_alert_events_recompute_same_alerts_without_semantic_mutation(self):
        from tools.aegis_control.observability import RawMetricEvent, evaluate_alerts, evaluate_alerts_from_raw, alert_snapshot_from_raw
        rows = [
            RawMetricEvent(1, "2026-09-01T00:00:00Z", "oldest_ready_outbox_seconds", "corr-alert-1", 301.0, "seconds", {}),
            RawMetricEvent(2, "2026-09-01T00:00:01Z", "reconciliation_lag_seconds", "corr-alert-2", 901.0, "seconds", {}),
        ]
        snapshot = alert_snapshot_from_raw(rows)
        direct = evaluate_alerts(snapshot)
        recomputed = evaluate_alerts_from_raw(rows)
        self.assertEqual(direct, recomputed)
        self.assertEqual({"OUTBOX_AGE_URGENT", "RECONCILIATION_LAG_URGENT"}, {a.rule_id for a in recomputed})
        self.assertTrue(all(a.semantic_truth is False for a in recomputed))


if __name__ == "__main__": unittest.main()
