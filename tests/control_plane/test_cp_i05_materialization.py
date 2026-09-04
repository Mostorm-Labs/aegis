import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tests.control_plane.cp_i05_fixtures import (
    RESULT_REF,
    configured_mutation,
    navigation,
    result_trust,
    seed_surface,
)
from tools.aegis_control.execution_surface import DeterministicExecutionSurface
from tools.aegis_control.mutation import MutationRejected
from tools.aegis_control.store import ControlStore


class CpI05MaterializationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.surface = DeterministicExecutionSurface()
        seed_surface(
            self.surface,
            occurrence_id="so_cp_i05_materialize",
            execution_ref="exec://cp-i05-materialize",
            revision="exec-cursor-1",
        )
        self.mutation = configured_mutation(
            self.store,
            self.surface,
            result_resolver=result_trust(occurrence_id="so_cp_i05_materialize"),
        )
        self.mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_cp_i05_materialize",
            "lane_cp_i05_materialize",
            {"occurrence": occurrence_record("so_cp_i05_materialize", "lane_cp_i05_materialize")},
        ))
        self._progress()

    def tearDown(self):
        self.tmp.cleanup()

    def _progress(self):
        current = self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_materialize")
        return self.mutation.apply(make_request(
            "RECORD_EXECUTION_PROGRESS",
            "req_cp_i05_materialization_progress",
            "lane_cp_i05_materialize",
            {
                "occurrence_id": "so_cp_i05_materialize",
                "recorded_at": "2026-09-01T02:15:00Z",
                "execution_navigation": navigation(
                    "exec://cp-i05-materialize", "exec-cursor-1"
                ),
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        ))

    def _terminate(self, produced_refs, *, request_id="req_cp_i05_materialization_terminal"):
        current = self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_materialize")
        terminal = terminal_facts()
        terminal["produced_refs"] = list(produced_refs)
        return self.mutation.apply(make_request(
            "TERMINATE_STAGE_OCCURRENCE",
            request_id,
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

    def test_review_ready_completion_requires_exact_result_in_produced_refs(self):
        before = dict(self.store.snapshot_counts())
        with self.assertRaises(MutationRejected) as caught:
            self._terminate([])
        self.assertEqual("RESULT_MATERIALIZATION_REQUIRED", caught.exception.code)
        self.assertEqual(before, self.store.snapshot_counts())
        self.assertEqual(
            "OPEN",
            self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_materialize").record["state"],
        )

    def test_exact_reviewer_resolved_result_allows_completion(self):
        result = self._terminate([RESULT_REF])
        self.assertEqual("APPLIED", result["status"])
        latest = self.store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_materialize")
        self.assertEqual("TERMINAL", latest.record["state"])
        self.assertEqual([RESULT_REF], latest.record["terminal"]["produced_refs"])

    def test_unconfigured_result_source_fails_closed(self):
        # A new occurrence with a valid-looking ref but no resolver binding cannot complete.
        store = ControlStore(str(Path(self.tmp.name) / "unconfigured.db"))
        surface = DeterministicExecutionSurface()
        seed_surface(
            surface,
            occurrence_id="so_cp_i05_unconfigured",
            execution_ref="exec://cp-i05-unconfigured",
            revision="exec-r1",
        )
        mutation = configured_mutation(store, surface)
        mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_cp_i05_unconfigured_schedule",
            "lane_cp_i05_unconfigured",
            {"occurrence": occurrence_record("so_cp_i05_unconfigured", "lane_cp_i05_unconfigured")},
        ))
        current = store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_unconfigured")
        mutation.apply(make_request(
            "RECORD_EXECUTION_PROGRESS",
            "req_cp_i05_unconfigured_progress",
            "lane_cp_i05_unconfigured",
            {
                "occurrence_id": "so_cp_i05_unconfigured",
                "recorded_at": "2026-09-01T02:15:00Z",
                "execution_navigation": navigation("exec://cp-i05-unconfigured", "exec-r1"),
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        ))
        current = store.read_latest("STAGE_OCCURRENCE", "so_cp_i05_unconfigured")
        terminal = terminal_facts()
        terminal["produced_refs"] = [RESULT_REF]
        with self.assertRaises(MutationRejected) as caught:
            mutation.apply(make_request(
                "TERMINATE_STAGE_OCCURRENCE",
                "req_cp_i05_unconfigured_terminal",
                "lane_cp_i05_unconfigured",
                {
                    "occurrence_id": "so_cp_i05_unconfigured",
                    "recorded_at": "2026-09-01T02:16:00Z",
                    "terminal": terminal,
                },
                expected_state(
                    target_record_revision=current.record["record_revision"],
                    target_record_digest=current.digest,
                    work_scope_ref=current.record["work_scope_ref"],
                ),
            ))
        self.assertEqual("RESULT_MATERIALIZATION_UNRESOLVABLE", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
