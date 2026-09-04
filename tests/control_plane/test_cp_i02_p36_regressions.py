import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import (
    expected_state,
    make_request,
    occurrence_record,
    terminal_facts,
)
from tests.control_plane.store_oracle import audit_database
from tools.aegis_control.canonical import canonical_digest, canonical_dumps
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.store import ControlStore


class P36ContinuationRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _db(self, name):
        return str(Path(self.tmp.name) / name)

    @staticmethod
    def _schedule(service, request_id, lane_id, occurrence_id, predecessor_ref=None):
        return service.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            request_id,
            lane_id,
            {"occurrence": occurrence_record(occurrence_id, lane_id)},
            expected_state(predecessor_occurrence_ref=predecessor_ref),
        ))

    @staticmethod
    def _terminate(service, store, request_id, lane_id, occurrence_id):
        current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
        return service.apply(make_request(
            "TERMINATE_STAGE_OCCURRENCE",
            request_id,
            lane_id,
            {
                "occurrence_id": occurrence_id,
                "recorded_at": "2026-08-31T07:30:00Z",
                "terminal": terminal_facts(),
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
            ),
        ))

    def test_legal_terminal_predecessor_schedules_successor_and_advances_lane(self):
        db = self._db("continuation.db")
        store = ControlStore(db)
        service = MutationService(store)

        first = self._schedule(service, "req_p36_a", "lane_p36", "so_p36_a")
        self.assertEqual(1, first["lane_head"]["version"])
        terminal = self._terminate(service, store, "req_p36_a_terminal", "lane_p36", "so_p36_a")
        predecessor_ref = terminal["canonical_records"][0]
        outbox_before = len(store.read_outbox())

        second = self._schedule(
            service,
            "req_p36_b",
            "lane_p36",
            "so_p36_b",
            predecessor_ref=predecessor_ref,
        )

        self.assertEqual("APPLIED", second["status"])
        self.assertEqual(2, second["lane_head"]["version"])
        self.assertIn("STAGE_OCCURRENCE:so_p36_b@1#", second["lane_head"]["occurrence_ref"])
        self.assertEqual(2, len(store.read_outbox()))
        self.assertEqual(outbox_before + 1, len(store.read_outbox()))
        self.assertEqual("TERMINAL", store.read_latest("STAGE_OCCURRENCE", "so_p36_a").record["state"])
        self.assertEqual("OPEN", store.read_latest("STAGE_OCCURRENCE", "so_p36_b").record["state"])

    def test_stale_or_still_open_predecessor_fails_with_zero_residue(self):
        for mode in ("stale", "open"):
            with self.subTest(mode=mode):
                db = self._db(f"{mode}.db")
                store = ControlStore(db)
                service = MutationService(store)
                first = self._schedule(service, f"req_{mode}_a", f"lane_{mode}", f"so_{mode}_a")
                open_ref = first["canonical_records"][0]
                if mode == "stale":
                    terminal = self._terminate(
                        service, store, f"req_{mode}_terminal", f"lane_{mode}", f"so_{mode}_a"
                    )
                    predecessor_ref = open_ref
                    self.assertNotEqual(open_ref, terminal["canonical_records"][0])
                else:
                    predecessor_ref = open_ref

                before = dict(store.snapshot_counts())
                with self.assertRaisesRegex(MutationRejected, "CONTROL_LANE_SCHEDULE_CONFLICT"):
                    self._schedule(
                        service,
                        f"req_{mode}_b",
                        f"lane_{mode}",
                        f"so_{mode}_b",
                        predecessor_ref=predecessor_ref,
                    )
                self.assertEqual(before, store.snapshot_counts())
                self.assertIsNone(store.read_latest("STAGE_OCCURRENCE", f"so_{mode}_b"))

    def test_race_from_terminal_predecessor_has_exactly_one_successor(self):
        db = self._db("race-established.db")
        store = ControlStore(db)
        service = MutationService(store)
        self._schedule(service, "req_race_base", "lane_race_p36", "so_race_base")
        terminal = self._terminate(
            service, store, "req_race_base_terminal", "lane_race_p36", "so_race_base"
        )
        predecessor_ref = terminal["canonical_records"][0]

        barrier = threading.Barrier(2)
        outcomes = []
        lock = threading.Lock()

        def run(index):
            candidate = MutationService(ControlStore(db), before_transaction=lambda: barrier.wait())
            try:
                result = self._schedule(
                    candidate,
                    f"req_race_successor_{index}",
                    "lane_race_p36",
                    f"so_race_successor_{index}",
                    predecessor_ref=predecessor_ref,
                )
                outcome = ("APPLIED", result)
            except MutationRejected as exc:
                outcome = (exc.code, None)
            with lock:
                outcomes.append(outcome)

        threads = [threading.Thread(target=run, args=(index,)) for index in (1, 2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(10)
            self.assertFalse(thread.is_alive())

        self.assertEqual(1, sum(code == "APPLIED" for code, _ in outcomes))
        self.assertEqual(1, sum(code == "CONTROL_LANE_SCHEDULE_CONFLICT" for code, _ in outcomes))
        reopened = ControlStore(db)
        successor_rows = sum(
            len(reopened.read_revisions("STAGE_OCCURRENCE", f"so_race_successor_{index}"))
            for index in (1, 2)
        )
        self.assertEqual(1, successor_rows)
        self.assertEqual(2, reopened.read_lane_head("lane_race_p36").version)
        self.assertEqual(2, len(reopened.read_outbox()))
        self.assertEqual(3, reopened.snapshot_counts()["idempotency"])

    def test_store_oracle_accepts_terminal_then_open_successor_history(self):
        db = self._db("oracle-continuation.db")
        store = ControlStore(db)
        service = MutationService(store)
        self._schedule(service, "req_oracle_a", "lane_oracle_p36", "so_oracle_a")
        terminal = self._terminate(
            service, store, "req_oracle_a_terminal", "lane_oracle_p36", "so_oracle_a"
        )
        self._schedule(
            service,
            "req_oracle_b",
            "lane_oracle_p36",
            "so_oracle_b",
            predecessor_ref=terminal["canonical_records"][0],
        )

        audit = audit_database(db)
        self.assertTrue(audit["passed"], audit["findings"])
        self.assertEqual(0, audit["metrics"]["same_lane_double_winners"])
        self.assertEqual([1, 2], audit["lineages"]["STAGE_OCCURRENCE:so_oracle_a"]["revisions"])
        self.assertEqual([1], audit["lineages"]["STAGE_OCCURRENCE:so_oracle_b"]["revisions"])
        self.assertEqual(2, audit["lane_heads"]["lane_oracle_p36"]["version"])

    def test_store_oracle_flags_true_two_open_same_lane_corruption(self):
        db = self._db("oracle-double-winner.db")
        store = ControlStore(db)
        service = MutationService(store)
        self._schedule(service, "req_oracle_good", "lane_oracle_bad", "so_oracle_good")

        injected = occurrence_record("so_oracle_injected", "lane_oracle_bad")
        canonical_json = canonical_dumps(injected)
        digest = canonical_digest(injected)
        injected_ref = f"STAGE_OCCURRENCE:so_oracle_injected@1#{digest}"
        outbox_payload = {
            "occurrence_ref": injected_ref,
            "control_lane_id": "lane_oracle_bad",
            "operation_request_id": "req_oracle_injected",
        }
        conn = sqlite3.connect(db)
        try:
            conn.execute(
                "INSERT INTO canonical_records "
                "(kind, id_scheme, record_id, record_revision, control_lane_id, stage_state, canonical_json, digest) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    injected["kind"],
                    injected["id_scheme"],
                    injected["id"],
                    injected["record_revision"],
                    injected["control_lane_id"],
                    injected["state"],
                    canonical_json,
                    digest,
                ),
            )
            conn.execute(
                "INSERT INTO outbox(outbox_id, occurrence_id, control_lane_id, payload_json) VALUES (?, ?, ?, ?)",
                (
                    "out_oracle_injected",
                    injected["id"],
                    injected["control_lane_id"],
                    canonical_dumps(outbox_payload),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        audit = audit_database(db)
        self.assertFalse(audit["passed"])
        self.assertEqual(1, audit["metrics"]["same_lane_double_winners"])
        self.assertIn("SAME_LANE_DOUBLE_WINNER", audit["findings"])
        self.assertEqual(
            ["so_oracle_good", "so_oracle_injected"],
            audit["open_occurrences_by_lane"]["lane_oracle_bad"],
        )
        self.assertEqual(0, audit["metrics"]["orphan_schedule_pairs"])


if __name__ == "__main__":
    unittest.main()
