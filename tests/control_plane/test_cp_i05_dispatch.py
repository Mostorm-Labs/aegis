import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import make_request, occurrence_record
from tests.control_plane.cp_i05_fixtures import dispatch_authorization
from tools.aegis_control.dispatch import DispatchRejected, DispatchService
from tools.aegis_control.execution_surface import DeterministicExecutionSurface
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.store import ControlStore


class CpI05DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.mutation = MutationService(self.store)
        scheduled = self.mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_cp_i05_dispatch",
            "lane_cp_i05_dispatch",
            {"occurrence": occurrence_record("so_cp_i05_dispatch", "lane_cp_i05_dispatch")},
        ))
        self.outbox_id = scheduled["outbox_ids"][0]
        self.surface = DeterministicExecutionSurface()
        self.dispatch = DispatchService(
            self.store,
            self.surface,
            authorization_resolver=dispatch_authorization(),
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_dispatch_consumes_only_committed_outbox_and_changes_no_canonical_state(self):
        before = dict(self.store.snapshot_counts())
        receipt = self.dispatch.dispatch(
            self.outbox_id,
            attempted_at="2026-09-01T02:10:00Z",
        )
        self.assertTrue(receipt.acknowledged)
        self.assertEqual("so_cp_i05_dispatch", receipt.occurrence_id)
        self.assertTrue(receipt.authorization_basis_digest.startswith("sha256:"))
        self.assertEqual(before, self.store.snapshot_counts())
        delivery = self.store.read_delivery_state(self.outbox_id)
        self.assertEqual(1, delivery["attempt_count"])
        self.assertEqual(receipt.correlation_id, delivery["provider_correlation_id"])

    def test_duplicate_transport_keeps_one_semantic_execution_identity(self):
        first = self.dispatch.dispatch(
            self.outbox_id, attempted_at="2026-09-01T02:10:00Z"
        )
        second = self.dispatch.dispatch(
            self.outbox_id, attempted_at="2026-09-01T02:10:01Z"
        )
        self.assertEqual(first.correlation_id, second.correlation_id)
        self.assertEqual(1, self.surface.unique_execution_count)
        self.assertEqual(1, len(self.store.read_revisions("STAGE_OCCURRENCE", "so_cp_i05_dispatch")))

    def test_unauthorized_dispatch_never_calls_provider(self):
        denied = DispatchService(
            self.store,
            self.surface,
            authorization_resolver=dispatch_authorization(satisfies=False),
        )
        before = dict(self.store.snapshot_counts())
        with self.assertRaises(DispatchRejected) as caught:
            denied.dispatch(self.outbox_id, attempted_at="2026-09-01T02:10:00Z")
        self.assertEqual("DISPATCH_NOT_AUTHORIZED", caught.exception.code)
        self.assertEqual(0, self.surface.provider_request_count)
        self.assertEqual(before, self.store.snapshot_counts())

    def test_missing_outbox_cannot_dispatch(self):
        with self.assertRaises(DispatchRejected) as caught:
            self.dispatch.dispatch("out_missing", attempted_at="2026-09-01T02:10:00Z")
        self.assertEqual("OUTBOX_NOT_FOUND", caught.exception.code)
        self.assertEqual(0, self.surface.provider_request_count)


if __name__ == "__main__":
    unittest.main()
