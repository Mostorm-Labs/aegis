from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import (
    expected_state,
    make_request,
    occurrence_record,
    terminal_facts,
)
from tools import aegis_control


class CpI03PolicyCurrentnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = aegis_control.ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.mutation = aegis_control.MutationService(self.store)

    @staticmethod
    def _stored_ref(stored):
        return (
            f"{stored.record['kind']}:{stored.record['id']}"
            f"@{stored.record['record_revision']}#{stored.digest}"
        )

    @staticmethod
    def _autonomous_occurrence(occurrence_id: str, lane_id: str):
        record = occurrence_record(occurrence_id, lane_id)
        record["policy_binding"] = {"control_autonomy": "AUTONOMOUS"}
        return record

    def _completed_projection(self, lane_id: str, occurrence_id: str):
        self.mutation.apply(
            make_request(
                "SCHEDULE_STAGE_OCCURRENCE",
                f"req_{occurrence_id}",
                lane_id,
                {"occurrence": occurrence_record(occurrence_id, lane_id)},
                expected_state(),
            )
        )
        current = self.store.read_latest("STAGE_OCCURRENCE", occurrence_id)
        self.mutation.apply(
            make_request(
                "TERMINATE_STAGE_OCCURRENCE",
                f"req_term_{occurrence_id}",
                lane_id,
                {"occurrence_id": occurrence_id, "terminal": terminal_facts(), "recorded_at": None},
                expected_state(
                    active_occurrence_ref=self._stored_ref(current),
                    target_record_revision=current.record["record_revision"],
                    target_record_digest=current.digest,
                ),
            )
        )
        return aegis_control.ProjectionEngine(self.store).project_lane(lane_id)

    def _candidate(self, lane_id: str, occurrence_id: str, fresh_basis: dict):
        projection = self._completed_projection(lane_id, f"{occurrence_id}_predecessor")
        allowed_basis = {"current": True, "rollout_authorized": True, "revision": "v1"}
        policy = aegis_control.PolicyEvaluator().evaluate_next_action(
            next_legal_action=projection.next_legal_action,
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-implementation",
            control_autonomy="AUTONOMOUS",
            policy_basis=allowed_basis,
        )
        scheduler = aegis_control.Scheduler(
            self.store,
            self.mutation,
            policy_basis_resolver=lambda candidate: dict(fresh_basis),
        )
        candidate = scheduler.derive_candidate(
            projection,
            policy,
            self._autonomous_occurrence(occurrence_id, lane_id),
        )
        return scheduler, candidate

    def _assert_submit_rejected_without_residue(self, fresh_basis: dict, occurrence_id: str):
        lane_id = f"lane_{occurrence_id}"
        scheduler, candidate = self._candidate(lane_id, occurrence_id, fresh_basis)
        before_counts = dict(self.store.snapshot_counts())
        before_outbox = len(self.store.read_outbox())

        with self.assertRaises(aegis_control.MutationRejected) as raised:
            scheduler.submit_candidate(candidate)

        self.assertEqual("POLICY_REVALIDATION_DENIED", raised.exception.code)
        self.assertEqual(before_counts, dict(self.store.snapshot_counts()))
        self.assertEqual(before_outbox, len(self.store.read_outbox()))
        self.assertIsNone(self.store.read_latest("STAGE_OCCURRENCE", occurrence_id))

    def test_submit_rejects_stale_current_policy_basis_without_residue(self):
        self._assert_submit_rejected_without_residue(
            {"current": False, "rollout_authorized": True, "revision": "v1"},
            "so_policy_currentness_stale",
        )

    def test_submit_rejects_ambiguous_current_policy_basis_without_residue(self):
        self._assert_submit_rejected_without_residue(
            {"current": True},
            "so_policy_currentness_ambiguous",
        )


if __name__ == "__main__":
    unittest.main()
