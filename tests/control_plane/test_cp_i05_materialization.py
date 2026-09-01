import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.store import ControlStore


RESULT_REF = {
    "object_type": "RESULT",
    "id": "result_cp_i05",
    "ref": "github:artifact:cp-i05-result",
    "identity": {"scheme": "sha256", "value": "sha256:" + "1" * 64},
}


class CpI05MaterializationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.mutation = MutationService(self.store)
        self.mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_cp_i05_materialize",
            "lane_cp_i05_materialize",
            {"occurrence": occurrence_record("so_cp_i05_materialize", "lane_cp_i05_materialize")},
        ))

    def tearDown(self):
        self.tmp.cleanup()

    def _progress(self, *, result_ref, reviewer_accessible):
        current = self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_materialize")
        navigation = {
            "task_anchor": {"revision": "a3fd350c350bec9220a1c6e283de88c14dfbcd2a", "relation": "ancestor"},
            "classification": "EXACT_CURSOR",
            "accepted_revision": "exec-cursor-1",
            "completed_through": ["implementation"],
            "next_action": "review",
            "materialization_required": True,
            "result_ref": result_ref,
            "reviewer_accessible": reviewer_accessible,
        }
        return self.mutation.apply(make_request(
            "RECORD_EXECUTION_PROGRESS",
            "req_cp_i05_materialization_progress",
            "lane_cp_i05_materialize",
            {
                "occurrence_id": "so_cp_i05_materialize",
                "recorded_at": "2026-09-01T02:15:00Z",
                "execution_navigation": navigation,
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        ))

    def _terminate(self, produced_refs):
        current = self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_materialize")
        terminal = terminal_facts()
        terminal["produced_refs"] = list(produced_refs)
        return self.mutation.apply(make_request(
            "TERMINATE_STAGE_OCCURRENCE",
            "req_cp_i05_materialization_terminal",
            "lane_cp_i05_materialize",
            {
                "occurrence_id": "so_cp_i05_materialize",
                "recorded_at": "2026-09-01T02:16:00Z",
                "terminal": terminal,
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        ))

    def test_review_ready_completion_requires_reviewer_accessible_exact_result(self):
        self._progress(result_ref=None, reviewer_accessible=False)
        with self.assertRaises(MutationRejected) as caught:
            self._terminate([])
        self.assertEqual("RESULT_MATERIALIZATION_REQUIRED", caught.exception.code)
        self.assertEqual("OPEN", self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_materialize").record["state"])

    def test_exact_result_must_be_bound_into_terminal_produced_refs(self):
        self._progress(result_ref=RESULT_REF, reviewer_accessible=True)
        with self.assertRaises(MutationRejected) as caught:
            self._terminate([])
        self.assertEqual("RESULT_MATERIALIZATION_MISMATCH", caught.exception.code)

    def test_exact_reviewer_accessible_result_allows_completion(self):
        self._progress(result_ref=RESULT_REF, reviewer_accessible=True)
        result = self._terminate([RESULT_REF])
        self.assertEqual("APPLIED", result["status"])
        latest = self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_materialize")
        self.assertEqual("TERMINAL", latest.record["state"])
        self.assertEqual([RESULT_REF], latest.record["terminal"]["produced_refs"])


if __name__ == "__main__":
    unittest.main()
