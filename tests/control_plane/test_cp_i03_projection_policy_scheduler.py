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
from tests.control_plane.reference_model import derive_projection as oracle_projection
from tools import aegis_control


class CpI03ProjectionPolicySchedulerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = aegis_control.ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.mutation = aegis_control.MutationService(self.store)

    def _schedule(self, occurrence_id: str, lane_id: str, *, predecessor_ref=None):
        record = occurrence_record(occurrence_id, lane_id)
        request = make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            f"req_{occurrence_id}",
            lane_id,
            {"occurrence": record},
            expected_state(predecessor_occurrence_ref=predecessor_ref),
        )
        return self.mutation.apply(request)

    def _terminate(self, occurrence_id: str, lane_id: str):
        current = self.store.read_latest("STAGE_OCCURRENCE", occurrence_id)
        request = make_request(
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
        return self.mutation.apply(request)

    @staticmethod
    def _stored_ref(stored):
        return (
            f"{stored.record['kind']}:{stored.record['id']}"
            f"@{stored.record['record_revision']}#{stored.digest}"
        )

    def test_public_cp_i03_surface_exists(self):
        required = {
            "ControlProjection",
            "ProjectionEngine",
            "ProjectionCache",
            "PolicyDecision",
            "PolicyEvaluator",
            "ScheduleCandidate",
            "Scheduler",
            "SchedulingDenied",
        }
        self.assertEqual(required - set(dir(aegis_control)), set())

    def test_projection_matches_independent_oracle_for_active_and_terminal_history(self):
        first = self._schedule("so_i03_a", "lane_i03")
        first_open = self.store.read_latest("STAGE_OCCURRENCE", "so_i03_a")
        production = aegis_control.ProjectionEngine(self.store).project_lane("lane_i03")
        expected = oracle_projection([first_open.record])
        self.assertEqual(production.control_cursor.active_occurrence_id, expected["active_occurrence_id"])
        self.assertEqual(production.control_cursor.last_terminal_occurrence_id, expected["last_terminal_occurrence_id"])
        self.assertEqual(production.next_legal_action, "WAIT_FOR_TERMINAL")

        self._terminate("so_i03_a", "lane_i03")
        first_terminal = self.store.read_latest("STAGE_OCCURRENCE", "so_i03_a")
        production = aegis_control.ProjectionEngine(self.store).project_lane("lane_i03")
        expected = oracle_projection([first_terminal.record])
        self.assertEqual(production.control_cursor.active_occurrence_id, expected["active_occurrence_id"])
        self.assertEqual(production.control_cursor.last_terminal_occurrence_id, expected["last_terminal_occurrence_id"])
        self.assertEqual(production.next_legal_action, "SCHEDULE_SUCCESSOR")
        self.assertEqual(first["outbox_ids"], ["out_i03_a"])

    def test_projection_cache_is_disposable_and_never_changes_canonical_history(self):
        self._schedule("so_i03_cache", "lane_cache")
        before = dict(self.store.snapshot_counts())
        cache = aegis_control.ProjectionCache()
        engine = aegis_control.ProjectionEngine(self.store, cache=cache)
        first = engine.project_lane("lane_cache")
        cached = engine.project_lane("lane_cache")
        self.assertEqual(first, cached)
        cache.clear()
        rebuilt = engine.project_lane("lane_cache")
        after = dict(self.store.snapshot_counts())
        self.assertEqual(first, rebuilt)
        self.assertEqual(before, after)

    def test_policy_denies_current_cross_primary_rollout_even_when_semantically_legal(self):
        evaluator = aegis_control.PolicyEvaluator()
        decision = evaluator.evaluate_next_action(
            next_legal_action="SCHEDULE_SUCCESSOR",
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-gate-review",
            control_autonomy="AUTONOMOUS",
            policy_basis={"current": True, "rollout_authorized": False},
        )
        self.assertEqual(decision.mode, "PROHIBITED")
        self.assertIn("CURRENT_CROSS_PRIMARY_ROLLOUT_DENIED", decision.reason_codes)
        self.assertFalse(decision.auto_schedule_authorized)
        self.assertFalse(decision.gate_decision)

    def test_policy_allows_same_owner_case_with_complete_current_basis(self):
        evaluator = aegis_control.PolicyEvaluator()
        decision = evaluator.evaluate_next_action(
            next_legal_action="SCHEDULE_SUCCESSOR",
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-implementation",
            control_autonomy="AUTONOMOUS",
            policy_basis={"current": True, "rollout_authorized": True},
        )
        self.assertEqual(decision.mode, "AUTONOMOUS")
        self.assertTrue(decision.auto_schedule_authorized)

    def test_policy_fails_closed_when_basis_is_missing_or_ambiguous(self):
        evaluator = aegis_control.PolicyEvaluator()
        for basis in (None, {}, {"current": False, "rollout_authorized": True}):
            with self.subTest(basis=basis):
                decision = evaluator.evaluate_next_action(
                    next_legal_action="SCHEDULE_SUCCESSOR",
                    source_primary_owner="aegis-implementation",
                    target_primary_owner="aegis-implementation",
                    control_autonomy="AUTONOMOUS",
                    policy_basis=basis,
                )
                self.assertEqual(decision.mode, "PROHIBITED")
                self.assertFalse(decision.auto_schedule_authorized)

    def test_stale_candidate_cannot_authorize_mutation(self):
        self._schedule("so_i03_stale_a", "lane_stale")
        self._terminate("so_i03_stale_a", "lane_stale")
        engine = aegis_control.ProjectionEngine(self.store)
        projection = engine.project_lane("lane_stale")
        policy = aegis_control.PolicyEvaluator().evaluate_next_action(
            next_legal_action=projection.next_legal_action,
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-implementation",
            control_autonomy="AUTONOMOUS",
            policy_basis={"current": True, "rollout_authorized": True},
        )
        scheduler = aegis_control.Scheduler(self.store, self.mutation)
        candidate = scheduler.derive_candidate(
            projection,
            policy,
            occurrence_record("so_i03_stale_b", "lane_stale"),
        )

        predecessor = self.store.read_latest("STAGE_OCCURRENCE", "so_i03_stale_a")
        self._schedule("so_i03_winner", "lane_stale", predecessor_ref=self._stored_ref(predecessor))

        with self.assertRaises(aegis_control.MutationRejected) as raised:
            scheduler.submit_candidate(candidate)
        self.assertEqual(raised.exception.code, "STALE_SCHEDULER_CANDIDATE")
        self.assertIsNone(self.store.read_latest("STAGE_OCCURRENCE", "so_i03_stale_b"))

    def test_same_state_concurrent_candidates_converge_to_one_cp_i02_cas_winner(self):
        self._schedule("so_i03_race_a", "lane_race")
        self._terminate("so_i03_race_a", "lane_race")
        projection = aegis_control.ProjectionEngine(self.store).project_lane("lane_race")
        policy = aegis_control.PolicyEvaluator().evaluate_next_action(
            next_legal_action=projection.next_legal_action,
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-implementation",
            control_autonomy="AUTONOMOUS",
            policy_basis={"current": True, "rollout_authorized": True},
        )
        scheduler = aegis_control.Scheduler(self.store, self.mutation)
        candidate_a = scheduler.derive_candidate(projection, policy, occurrence_record("so_i03_race_b", "lane_race"))
        candidate_b = scheduler.derive_candidate(projection, policy, occurrence_record("so_i03_race_c", "lane_race"))

        result = scheduler.submit_candidate(candidate_a)
        self.assertEqual(result["status"], "APPLIED")
        with self.assertRaises(aegis_control.MutationRejected):
            scheduler.submit_candidate(candidate_b)

        winners = [
            self.store.read_latest("STAGE_OCCURRENCE", occurrence_id)
            for occurrence_id in ("so_i03_race_b", "so_i03_race_c")
        ]
        self.assertEqual(sum(item is not None for item in winners), 1)

    def test_pause_and_lease_like_state_do_not_create_canonical_history(self):
        before = dict(self.store.snapshot_counts())
        scheduler = aegis_control.Scheduler(self.store, self.mutation)
        scheduler.pause("lane_ops")
        scheduler.acquire_lease_hint("lane_ops", "worker-1")
        scheduler.release_lease_hint("lane_ops", "worker-1")
        scheduler.resume("lane_ops")
        after = dict(self.store.snapshot_counts())
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
