from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path


class CpI09FixtureTests(unittest.TestCase):
    def test_insert_record_uses_current_canonical_text_contract(self):
        from tests.control_plane.cp_i02_fixtures import package_record
        from tests.control_plane.cp_i09_fixture import _insert_record
        from tools.aegis_control.canonical import canonical_dumps
        from tools.aegis_control.store import ControlStore

        record = package_record(package_id="pkg_fixture_probe", lane_id="lane_fixture_probe")
        self.assertIsInstance(canonical_dumps(record), str)

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "fixture.sqlite"
            ControlStore(str(db_path))
            conn = sqlite3.connect(str(db_path))
            try:
                _insert_record(conn, record)
                conn.commit()
                row = conn.execute(
                    "SELECT canonical_json FROM canonical_records WHERE kind=? AND record_id=? AND record_revision=?",
                    (record["kind"], record["id"], record["record_revision"]),
                ).fetchone()
            finally:
                conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(canonical_dumps(record), row[0])


if __name__ == "__main__":
    unittest.main()
