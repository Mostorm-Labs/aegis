from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path


class CpI09StoreIndexTests(unittest.TestCase):
    def test_control_lane_latest_projection_has_covering_lookup_index(self):
        from tools.aegis_control.store import ControlStore

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "control.sqlite"
            ControlStore(str(db_path))
            conn = sqlite3.connect(str(db_path))
            try:
                indexes = {
                    row[1]: tuple(
                        info[2]
                        for info in conn.execute(f"PRAGMA index_info('{row[1]}')").fetchall()
                    )
                    for row in conn.execute("PRAGMA index_list('canonical_records')").fetchall()
                }
            finally:
                conn.close()

        self.assertIn("ix_canonical_lane_latest", indexes)
        self.assertEqual(
            ("control_lane_id", "kind", "record_id", "record_revision"),
            indexes["ix_canonical_lane_latest"],
        )


if __name__ == "__main__":
    unittest.main()
