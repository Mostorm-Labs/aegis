import importlib.util
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.store import ControlStore


class CpI05FoundationRedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.mutation = MutationService(self.store)

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

    def test_record_execution_progress_is_supported(self):
        schedule = make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_cp_i05_schedule",
            "lane_cp_i05",
            {"occurrence": occurrence_record("so_cp_i05", "lane_cp_i05")},
        )
        self.mutation.apply(schedule)
        current = self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05")
        request = make_request(
            "RECORD_EXECUTION_PROGRESS",
            "req_cp_i05_progress",
            "lane_cp_i05",
            {
                "occurrence_id": "so_cp_i05",
                "recorded_at": "2026-09-01T01:15:00Z",
                "execution_navigation": {
                    "task_anchor": {"revision": "a3fd350c350bec9220a1c6e283de88c14dfbcd2a", "relation": "ancestor"},
                    "classification": "EXACT_CURSOR",
                    "accepted_revision": "abc123",
                    "completed_through": ["step-1"],
                    "next_action": "step-2",
                },
            },
            expected_state(
                target_record_revision=1,
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        )
        try:
            result = self.mutation.apply(request)
        except MutationRejected as exc:
            result = {"status": "REJECTED", "code": exc.code}
        self.assertEqual("APPLIED", result["status"])
        revisions = self.store.read_revisions("STAGE_OCCURRENCE", "so_cp_i05")
        self.assertEqual(2, len(revisions))
        self.assertEqual("OPEN", revisions[-1].record["state"])
        self.assertEqual(request["payload"]["execution_navigation"], revisions[-1].record["execution_navigation"])


if __name__ == "__main__":
    unittest.main()
