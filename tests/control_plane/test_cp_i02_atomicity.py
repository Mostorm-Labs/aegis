import tempfile
import threading
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import (
    escalation_record,
    expected_state,
    make_request,
    occurrence_record,
    terminal_facts,
)
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.store import ControlStore


class InjectedFailure(RuntimeError):
    pass


class AtomicityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _db(self, name="atomic.db"):
        return str(Path(self.tmp.name) / name)

    def _schedule_request(self, request_id="req_atomic", lane_id="lane_atomic", occurrence_id="so_atomic"):
        return make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            request_id,
            lane_id,
            {"occurrence": occurrence_record(occurrence_id, lane_id)},
        )

    def test_each_schedule_precommit_failure_rolls_back_all_semantic_rows(self):
        for checkpoint in ("after_canonical", "after_lane", "after_outbox", "after_idempotency"):
            with self.subTest(checkpoint=checkpoint):
                db = self._db(f"{checkpoint}.db")
                store = ControlStore(db)

                def inject(name):
                    if name == checkpoint:
                        raise InjectedFailure(name)

                with self.assertRaises(InjectedFailure):
                    MutationService(store, fault_injector=inject).apply(self._schedule_request())
                reopened = ControlStore(db)
                self.assertEqual(
                    {"canonical_records": 0, "lane_heads": 0, "idempotency": 0, "outbox": 0},
                    reopened.snapshot_counts(),
                )

    def test_uncommitted_schedule_is_invisible_to_separate_reader(self):
        db = self._db("visibility.db")
        writer_store = ControlStore(db)
        reached = threading.Event()
        release = threading.Event()
        errors = []

        def inject(name):
            if name == "after_outbox":
                reached.set()
                if not release.wait(5):
                    raise InjectedFailure("visibility timeout")

        def write():
            try:
                MutationService(writer_store, fault_injector=inject).apply(self._schedule_request())
            except Exception as exc:
                errors.append(exc)

        thread = threading.Thread(target=write)
        thread.start()
        self.assertTrue(reached.wait(5))
        observer = ControlStore(db)
        self.assertEqual(
            {"canonical_records": 0, "lane_heads": 0, "idempotency": 0, "outbox": 0},
            observer.snapshot_counts(),
        )
        release.set()
        thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual([], errors)
        self.assertEqual(
            {"canonical_records": 1, "lane_heads": 1, "idempotency": 1, "outbox": 1},
            ControlStore(db).snapshot_counts(),
        )

    def test_committed_schedule_survives_close_and_reopen_as_complete_set(self):
        db = self._db("reopen.db")
        store = ControlStore(db)
        result = MutationService(store).apply(self._schedule_request())
        self.assertEqual("APPLIED", result["status"])
        del store
        reopened = ControlStore(db)
        self.assertEqual(1, len(reopened.read_revisions("STAGE_OCCURRENCE", "so_atomic")))
        self.assertEqual(1, reopened.read_lane_head("lane_atomic").version)
        self.assertIsNotNone(reopened.read_idempotency("req_atomic"))
        self.assertEqual(1, len(reopened.read_outbox()))

    def test_escalation_and_terminal_companion_roll_back_together(self):
        for checkpoint in ("after_escalation", "after_terminal", "after_idempotency"):
            with self.subTest(checkpoint=checkpoint):
                db = self._db(f"esc-{checkpoint}.db")
                store = ControlStore(db)
                MutationService(store).apply(
                    self._schedule_request("req_esc_schedule", "lane_01", "so_01")
                )
                current = store.read_latest("STAGE_OCCURRENCE", "so_01")
                before = dict(store.snapshot_counts())
                request = make_request(
                    "RAISE_ESCALATION",
                    "req_esc_raise",
                    "lane_01",
                    {
                        "occurrence_id": "so_01",
                        "recorded_at": "2026-08-31T06:32:00Z",
                        "escalation": escalation_record(),
                        "terminal": terminal_facts(
                            "ESCALATED",
                            "BLOCKED_UNRESOLVED_DECISION",
                            raised=["esc_01"],
                            earliest="P21",
                        ),
                    },
                    expected_state(
                        target_record_revision=1,
                        target_record_digest=current.digest,
                    ),
                )

                def inject(name):
                    if name == checkpoint:
                        raise InjectedFailure(name)

                with self.assertRaises(InjectedFailure):
                    MutationService(store, fault_injector=inject).apply(request)
                reopened = ControlStore(db)
                self.assertEqual(before, reopened.snapshot_counts())
                self.assertIsNone(reopened.read_latest("ESCALATION", "esc_01"))
                self.assertEqual("OPEN", reopened.read_latest("STAGE_OCCURRENCE", "so_01").record["state"])
                self.assertIsNone(reopened.read_idempotency("req_esc_raise"))


if __name__ == "__main__":
    unittest.main()
