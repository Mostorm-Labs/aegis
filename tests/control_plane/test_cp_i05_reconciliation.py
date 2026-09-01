import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import make_request, occurrence_record
from tests.control_plane.cp_i05_fixtures import dispatch_authorization
from tools.aegis_control.dispatch import DispatchService
from tools.aegis_control.execution_surface import DeterministicExecutionSurface
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.recovery import RecoveryCoordinator, ReconciliationBlocked
from tools.aegis_control.store import ControlStore


RESULT_REF = {
    "object_type": "RESULT",
    "id": "result_callback_loss",
    "ref": "github:artifact:callback-loss-result",
    "identity": {"scheme": "sha256", "value": "sha256:" + "2" * 64},
}


class CpI05ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ControlStore(str(Path(self.tmp.name) / "control.db"))
        mutation = MutationService(self.store)
        scheduled = mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_cp_i05_reconcile",
            "lane_cp_i05_reconcile",
            {"occurrence": occurrence_record("so_cp_i05_reconcile", "lane_cp_i05_reconcile")},
        ))
        self.outbox_id = scheduled["outbox_ids"][0]
        self.surface = DeterministicExecutionSurface()
        receipt = DispatchService(
            self.store,
            self.surface,
            authorization_resolver=dispatch_authorization(),
        ).dispatch(
            self.outbox_id,
            attempted_at="2026-09-01T02:20:00Z",
        )
        self.correlation_id = receipt.correlation_id
        self.recovery = RecoveryCoordinator(self.store, self.surface)

    def tearDown(self):
        self.tmp.cleanup()

    def test_callback_loss_is_recovered_by_query_without_canonical_mutation(self):
        self.surface.set_observation(
            self.correlation_id,
            state="MATERIALIZED",
            execution_revision="exec-2",
            materialized_ref=RESULT_REF,
            reviewer_accessible=True,
        )
        before = dict(self.store.snapshot_counts())
        observation = self.recovery.reconcile_outbox(
            self.outbox_id, observed_at="2026-09-01T02:21:00Z"
        )
        self.assertEqual("MATERIALIZED", observation.state)
        self.assertEqual(RESULT_REF, observation.materialized_ref)
        self.assertEqual(1, self.surface.query_count)
        self.assertEqual(before, self.store.snapshot_counts())
        latest = self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_reconcile")
        self.assertEqual("OPEN", latest.record["state"])
        self.assertEqual(1, latest.record["record_revision"])

    def test_missing_correlation_fails_closed_without_query(self):
        mutation = MutationService(self.store)
        scheduled = mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_cp_i05_reconcile_missing",
            "lane_cp_i05_reconcile_missing",
            {"occurrence": occurrence_record("so_cp_i05_reconcile_missing", "lane_cp_i05_reconcile_missing")},
        ))
        fresh_outbox = scheduled["outbox_ids"][0]
        before_queries = self.surface.query_count
        with self.assertRaises(ReconciliationBlocked) as caught:
            self.recovery.reconcile_outbox(
                fresh_outbox, observed_at="2026-09-01T02:21:00Z"
            )
        self.assertEqual("DELIVERY_CORRELATION_MISSING", caught.exception.code)
        self.assertEqual(before_queries, self.surface.query_count)

    def test_unknown_provider_correlation_fails_closed(self):
        recovery = RecoveryCoordinator(self.store, DeterministicExecutionSurface())
        with self.assertRaises(ReconciliationBlocked) as caught:
            recovery.reconcile_outbox(
                self.outbox_id, observed_at="2026-09-01T02:21:00Z"
            )
        self.assertEqual("PROVIDER_CORRELATION_NOT_FOUND", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
