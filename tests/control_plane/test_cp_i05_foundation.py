import importlib.util
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record
from tests.control_plane.cp_i05_fixtures import configured_mutation, navigation, seed_surface
from tools.aegis_control.execution_surface import DeterministicExecutionSurface
from tools.aegis_control.store import ControlStore


class CpI05FoundationRedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ControlStore(str(Path(self.tmp.name) / "control.db"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_cp_i05_runtime_modules_exist(self):
        for module_name in (
            "tools.aegis_control.dispatch",
            "tools.aegis_control.execution_surface",
            "tools.aegis_control.recovery",
        ):
            with self.subTest(module=module_name):
                self.assertIsNotNone(importlib.util.find_spec(module_name))

    def test_store_exposes_noncanonical_delivery_state(self):
        self.assertTrue(hasattr(self.store, "read_delivery_state"))
        self.assertTrue(hasattr(self.store, "record_delivery_attempt"))
        self.assertTrue(hasattr(self.store, "record_delivery_correlation"))
        self.assertTrue(hasattr(self.store, "record_delivery_diagnostic"))

    def test_record_execution_progress_is_supported_with_reconciled_p12_snapshot(self):
        surface = DeterministicExecutionSurface()
        seed_surface(
            surface,
            occurrence_id="so_cp_i05",
            execution_ref="exec://cp-i05",
            revision="abc123",
            completed_through=("step-1",),
            next_action="step-2",
        )
        mutation = configured_mutation(self.store, surface)
        mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_cp_i05_schedule",
            "lane_cp_i05",
            {"occurrence": occurrence_record("so_cp_i05", "lane_cp_i05")},
        ))
        current = self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05")
        checkpoint = navigation("exec://cp-i05", "abc123", next_action="step-2")
        request = make_request(
            "RECORD_EXECUTION_PROGRESS",
            "req_cp_i05_progress",
            "lane_cp_i05",
            {
                "occurrence_id": "so_cp_i05",
                "recorded_at": "2026-09-01T01:15:00Z",
                "execution_navigation": checkpoint,
            },
            expected_state(
                target_record_revision=1,
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        )
        result = mutation.apply(request)
        self.assertEqual("APPLIED", result["status"])
        revisions = self.store.read_revisions("STAGE_OCCURRENCE", "so_cp_i05")
        self.assertEqual(2, len(revisions))
        self.assertEqual("OPEN", revisions[-1].record["state"])
        self.assertEqual(checkpoint, revisions[-1].record["execution_navigation"])


if __name__ == "__main__":
    unittest.main()
