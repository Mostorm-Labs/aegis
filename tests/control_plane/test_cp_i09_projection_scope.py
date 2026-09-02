from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import make_request, occurrence_record
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.projection import ProjectionEngine
from tools.aegis_control.store import ControlStore


class _NoGlobalOccurrenceScanStore(ControlStore):
    def read_latest_stage_occurrences(self):
        raise AssertionError("projection must not scan global latest StageOccurrence history")


class CpI09ProjectionScopeTests(unittest.TestCase):
    def test_projection_reads_only_current_scope_family_not_global_occurrence_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "control.sqlite"
            setup_store = ControlStore(str(db_path))
            mutation = MutationService(setup_store)
            occurrence = occurrence_record("so_projection_probe", "lane_projection_probe")
            mutation.apply(
                make_request(
                    "SCHEDULE_STAGE_OCCURRENCE",
                    "req_projection_probe",
                    "lane_projection_probe",
                    {"occurrence": occurrence},
                )
            )

            projection = ProjectionEngine(_NoGlobalOccurrenceScanStore(str(db_path))).project_lane(
                "lane_projection_probe"
            )

            self.assertEqual("ws_lane_projection_probe", projection.control_cursor.work_scope_ref["id"])
            self.assertEqual("so_projection_probe", projection.control_cursor.active_occurrence_id)
            self.assertEqual((), projection.child_work)

    def test_production_schema_has_scope_family_occurrence_indexes(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "control.sqlite"
            ControlStore(str(db_path))
            conn = sqlite3.connect(str(db_path))
            try:
                rows = conn.execute(
                    "SELECT name, sql FROM sqlite_master "
                    "WHERE type='index' AND tbl_name='canonical_records'"
                ).fetchall()
            finally:
                conn.close()

        indexes = {name: sql or "" for name, sql in rows}
        self.assertIn("ix_stage_occurrence_scope_latest", indexes)
        self.assertIn("$.work_scope_ref.id", indexes["ix_stage_occurrence_scope_latest"])
        self.assertIn("ix_stage_occurrence_parent_scope_latest", indexes)
        self.assertIn(
            "$.work_scope_ref.child_work_binding.parent_work_scope_ref.id",
            indexes["ix_stage_occurrence_parent_scope_latest"],
        )


if __name__ == "__main__":
    unittest.main()
