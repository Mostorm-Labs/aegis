from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tools.aegis_control import ControlStore, MutationRejected, MutationService, PolicyEvaluator, ProjectionEngine, Scheduler


def _stored_ref(stored) -> str:
    return (
        f"{stored.record['kind']}:{stored.record['id']}"
        f"@{stored.record['record_revision']}#{stored.digest}"
    )


class CpI03ConcurrentSchedulerTests(unittest.TestCase):
    def test_same_projection_candidates_reach_cp_i02_cas_and_exactly_one_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "control.db")
            store = ControlStore(db)
            mutation = MutationService(store)

            first = make_request(
                "SCHEDULE_STAGE_OCCURRENCE",
                "req_i03_concurrent_a",
                "lane_i03_concurrent",
                {"occurrence": occurrence_record("so_i03_concurrent_a", "lane_i03_concurrent")},
            )
            mutation.apply(first)
            current = store.read_latest("STAGE_OCCURRENCE", "so_i03_concurrent_a")
            mutation.apply(make_request(
                "TERMINATE_STAGE_OCCURRENCE",
                "req_i03_concurrent_a_terminal",
                "lane_i03_concurrent",
                {
                    "occurrence_id": "so_i03_concurrent_a",
                    "terminal": terminal_facts(),
                    "recorded_at": None,
                },
                expected_state(
                    active_occurrence_ref=_stored_ref(current),
                    target_record_revision=current.record["record_revision"],
                    target_record_digest=current.digest,
                ),
            ))

            projection = ProjectionEngine(store).project_lane("lane_i03_concurrent")
            policy = PolicyEvaluator().evaluate_next_action(
                next_legal_action=projection.next_legal_action,
                source_primary_owner="aegis-implementation",
                target_primary_owner="aegis-implementation",
                control_autonomy="AUTONOMOUS",
                policy_basis={"current": True, "rollout_authorized": True},
            )
            planner = Scheduler(store, mutation)
            candidates = [
                planner.derive_candidate(
                    projection,
                    policy,
                    occurrence_record(occurrence_id, "lane_i03_concurrent"),
                )
                for occurrence_id in ("so_i03_concurrent_b", "so_i03_concurrent_c")
            ]

            barrier = threading.Barrier(2)
            outcomes: list[tuple[str, str]] = []
            outcome_lock = threading.Lock()

            def submit(candidate) -> None:
                local_store = ControlStore(db)
                local_mutation = MutationService(local_store, before_transaction=lambda: barrier.wait())
                local_scheduler = Scheduler(local_store, local_mutation)
                try:
                    result = local_scheduler.submit_candidate(candidate)
                    outcome = ("APPLIED", result["canonical_records"][0])
                except MutationRejected as exc:
                    outcome = (exc.code, "")
                with outcome_lock:
                    outcomes.append(outcome)

            threads = [threading.Thread(target=submit, args=(candidate,)) for candidate in candidates]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=10)
            self.assertTrue(all(not thread.is_alive() for thread in threads))

            self.assertEqual(1, sum(code == "APPLIED" for code, _ in outcomes))
            self.assertEqual(1, sum(code == "CONTROL_LANE_SCHEDULE_CONFLICT" for code, _ in outcomes))
            self.assertEqual(2, store.read_lane_head("lane_i03_concurrent").version)
            self.assertEqual(2, len(store.read_outbox()))
            successors = [
                store.read_latest("STAGE_OCCURRENCE", occurrence_id)
                for occurrence_id in ("so_i03_concurrent_b", "so_i03_concurrent_c")
            ]
            self.assertEqual(1, sum(record is not None for record in successors))


if __name__ == "__main__":
    unittest.main()
