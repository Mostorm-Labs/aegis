from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import occurrence_record
from tools.aegis_control import CanonicalValidationError, validate_record
from tools.aegis_control.canonical import PRIMARY_OWNER_BY_STAGE


ROOT = Path(__file__).resolve().parents[2]


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

    def test_runtime_primary_owner_map_matches_read_only_skillset_oracle(self):
        oracle = json.loads((ROOT / "skillset/ownership.json").read_text(encoding="utf-8"))
        self.assertEqual(oracle["primary_owner_by_stage"], PRIMARY_OWNER_BY_STAGE)

    def test_stage_occurrence_owner_is_derived_from_stage_span(self):
        valid = occurrence_record("so_owner_valid", "lane_owner_valid")
        valid["stage_span"] = {"stages": ["P34"]}
        valid["primary_owner"] = "aegis-gate-review"
        validate_record(valid)

        wrong_owner = occurrence_record("so_owner_wrong", "lane_owner_wrong")
        wrong_owner["stage_span"] = {"stages": ["P34"]}
        wrong_owner["primary_owner"] = "aegis-implementation"
        with self.assertRaises(CanonicalValidationError):
            validate_record(wrong_owner)

        unknown_stage = occurrence_record("so_owner_unknown", "lane_owner_unknown")
        unknown_stage["stage_span"] = {"stages": ["P99"]}
        unknown_stage["primary_owner"] = "aegis-implementation"
        with self.assertRaises(CanonicalValidationError):
            validate_record(unknown_stage)

        cross_primary = occurrence_record("so_owner_cross", "lane_owner_cross")
        cross_primary["stage_span"] = {"stages": ["P33", "P34"]}
        cross_primary["primary_owner"] = "aegis-implementation"
        with self.assertRaises(CanonicalValidationError):
            validate_record(cross_primary)

    def test_child_occurrence_cannot_inherit_parent_owner_when_stage_owner_differs(self):
        child = occurrence_record("so_child_owner", "lane_child_owner")
        child["work_scope_ref"] = {
            "id_scheme": "control-work-scope-v0.2",
            "id": "ws_child_owner",
            "child_work_binding": None,
        }
        child["stage_span"] = {"stages": ["P34"]}
        child["primary_owner"] = "aegis-implementation"
        with self.assertRaises(CanonicalValidationError):
            validate_record(child)


if __name__ == "__main__":
    unittest.main()
