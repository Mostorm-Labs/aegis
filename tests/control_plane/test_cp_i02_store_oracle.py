import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import (
    expected_state,
    make_request,
    occurrence_record,
    terminal_facts,
)
from tests.control_plane.store_oracle import audit_database
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.store import ControlStore


class StoreOracleTests(unittest.TestCase):
    def test_direct_sql_oracle_sees_exact_durable_state_after_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "oracle.db")
            store = ControlStore(db)
            mutation = MutationService(store)
            mutation.apply(
                make_request(
                    "SCHEDULE_STAGE_OCCURRENCE",
                    "req_oracle_schedule",
                    "lane_oracle",
                    {"occurrence": occurrence_record("so_oracle", "lane_oracle")},
                )
            )
            current = store.read_latest("STAGE_OCCURRENCE", "so_oracle")
            mutation.apply(
                make_request(
                    "TERMINATE_STAGE_OCCURRENCE",
                    "req_oracle_terminal",
                    "lane_oracle",
                    {
                        "occurrence_id": "so_oracle",
                        "recorded_at": "2026-08-31T06:40:00Z",
                        "terminal": terminal_facts(),
                    },
                    expected_state(
                        target_record_revision=1,
                        target_record_digest=current.digest,
                    ),
                )
            )
            del mutation, store
            audit = audit_database(db)
            self.assertTrue(audit["passed"])
            self.assertEqual([1, 2], audit["lineages"]["STAGE_OCCURRENCE:so_oracle"]["revisions"])
            self.assertEqual(1, audit["lane_heads"]["lane_oracle"]["version"])
            self.assertEqual(2, len(audit["idempotency"]))
            self.assertEqual(1, len(audit["outbox"]))
            self.assertTrue(all(value == 0 for value in audit["metrics"].values()))


if __name__ == "__main__":
    unittest.main()
