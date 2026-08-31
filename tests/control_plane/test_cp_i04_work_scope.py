from __future__ import annotations

import unittest

from tests.control_plane.cp_i02_fixtures import occurrence_record
from tools.aegis_control import CanonicalValidationError, validate_record


class CpI04WorkScopeContractTests(unittest.TestCase):
    def test_stage_occurrence_accepts_required_work_scope_and_barrier_array(self):
        record = occurrence_record("so_cp_i04_root", "lane_cp_i04_root")
        record["work_scope_ref"] = {
            "id_scheme": "control-work-scope-v0.2",
            "id": "ws_cp_i04_root",
            "child_work_binding": None,
        }
        record["schedule_basis"]["required_child_acceptance_bindings"] = []

        try:
            validate_record(record)
        except CanonicalValidationError as exc:
            self.fail(f"accepted P12/P13 CP-I04 canonical shape was rejected: {exc}")


if __name__ == "__main__":
    unittest.main()
