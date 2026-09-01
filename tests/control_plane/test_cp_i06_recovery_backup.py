from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import make_request, occurrence_record
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.recovery import (
    backup_control_store,
    restore_control_store_backup,
    startup_recovery_plan,
    verify_control_store_integrity,
)
from tools.aegis_control.store import ControlStore, StoreConflict


class CpI06RecoveryBackupRedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root / "control.db"
        self.store = ControlStore(str(self.db))
        self.mutation = MutationService(self.store)

    def tearDown(self):
        self.tmp.cleanup()

    def _seed_open(self, occurrence_id="so_restart", lane_id="lane_restart"):
        result = self.mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            f"req_{occurrence_id}",
            lane_id,
            {"occurrence": occurrence_record(occurrence_id, lane_id)},
        ))
        return result["outbox_ids"][0]

    def test_primary_process_replacement_has_zero_acknowledged_commit_loss(self):
        outbox_id = self._seed_open()
        before_counts = dict(self.store.snapshot_counts())
        before_occurrence = self.store.read_latest("STAGE_OCCURRENCE", "so_restart")
        before_lane = self.store.read_lane_head("lane_restart")
        before_idempotency = self.store.read_idempotency("req_so_restart")

        # Simulate loss of all process memory by constructing a fresh store
        # object against the same durable database.
        reopened = ControlStore(str(self.db))
        self.assertEqual(before_counts, reopened.snapshot_counts())
        self.assertEqual(before_occurrence.digest, reopened.read_latest("STAGE_OCCURRENCE", "so_restart").digest)
        self.assertEqual(before_lane, reopened.read_lane_head("lane_restart"))
        self.assertEqual(before_idempotency, reopened.read_idempotency("req_so_restart"))
        self.assertEqual(outbox_id, reopened.read_outbox()[0]["outbox_id"])

    def test_startup_recovery_reuses_same_open_occurrence_and_committed_outbox(self):
        outbox_id = self._seed_open()
        before = dict(self.store.snapshot_counts())

        restarted = ControlStore(str(self.db))
        plan = startup_recovery_plan(restarted, observed_at="2026-09-01T10:00:00Z")
        self.assertEqual(1, len(plan))
        self.assertEqual("so_restart", plan[0].occurrence_id)
        self.assertEqual(outbox_id, plan[0].outbox_id)
        self.assertEqual("DISPATCH_COMMITTED_OUTBOX", plan[0].action)
        self.assertFalse(plan[0].semantic_retry)
        self.assertFalse(plan[0].replacement_occurrence)
        self.assertEqual(before, restarted.snapshot_counts())
        self.assertEqual("OPEN", restarted.read_latest("STAGE_OCCURRENCE", "so_restart").record["state"])

        restarted.record_delivery_correlation(
            outbox_id,
            "corr_restart",
            observed_at="2026-09-01T10:00:05Z",
            provider_state="RUNNING",
        )
        correlated = startup_recovery_plan(restarted, observed_at="2026-09-01T10:01:00Z")
        self.assertEqual("RECONCILE_EXISTING_OCCURRENCE", correlated[0].action)
        self.assertEqual("so_restart", correlated[0].occurrence_id)
        self.assertFalse(correlated[0].semantic_retry)
        self.assertFalse(correlated[0].replacement_occurrence)

    def test_backup_restore_preserves_exact_acknowledged_snapshot(self):
        outbox_id = self._seed_open("so_backup", "lane_backup")
        self.store.record_delivery_attempt(
            outbox_id,
            "2026-09-01T10:00:00Z",
            next_attempt_at="2026-09-01T10:00:01Z",
        )
        canonical = self.store.read_latest("STAGE_OCCURRENCE", "so_backup")
        idempotency = self.store.read_idempotency("req_so_backup")
        counts = dict(self.store.snapshot_counts())

        backup = self.root / "control.backup.db"
        metadata = backup_control_store(self.store, str(backup))
        self.assertEqual("ok", metadata["integrity_check"])
        self.assertTrue(backup.is_file())

        restored_path = self.root / "restored.db"
        restored = restore_control_store_backup(str(backup), str(restored_path))
        self.assertEqual("ok", verify_control_store_integrity(restored))
        self.assertEqual(counts, restored.snapshot_counts())
        self.assertEqual(canonical.digest, restored.read_latest("STAGE_OCCURRENCE", "so_backup").digest)
        self.assertEqual(idempotency, restored.read_idempotency("req_so_backup"))
        self.assertEqual(outbox_id, restored.read_outbox()[0]["outbox_id"])
        self.assertEqual(1, restored.read_delivery_state(outbox_id)["attempt_count"])

    def test_corrupt_backup_fails_closed_without_fabricated_restore(self):
        self._seed_open("so_corrupt", "lane_corrupt")
        backup = self.root / "corrupt.db"
        backup_control_store(self.store, str(backup))
        backup.write_bytes(b"not-a-sqlite-database")
        destination = self.root / "should-not-exist.db"

        with self.assertRaises(StoreConflict):
            restore_control_store_backup(str(backup), str(destination))
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
