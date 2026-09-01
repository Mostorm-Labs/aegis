from datetime import datetime, timedelta, timezone
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tests.control_plane.cp_i05_fixtures import configured_mutation, dispatch_authorization, seed_surface
from tools.aegis_control.dispatch import DispatchService
from tools.aegis_control.execution_surface import DeterministicExecutionSurface
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.recovery import RecoveryCoordinator
from tools.aegis_control.store import ControlStore


def _time(seconds: int) -> str:
    value = datetime(2026, 9, 1, 2, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return value.isoformat().replace("+00:00", "Z")


class CpI05P36EdgeCaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _store(self, name: str) -> ControlStore:
        return ControlStore(str(Path(self.tmp.name) / f"{name}.db"))

    def test_configured_execution_boundary_cannot_complete_without_exact_result_even_before_progress(self):
        store = self._store("terminal-bypass")
        surface = DeterministicExecutionSurface()
        seed_surface(
            surface,
            occurrence_id="so_terminal_bypass",
            execution_ref="exec://terminal-bypass",
        )
        mutation = configured_mutation(store, surface)
        mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_terminal_bypass_schedule",
            "lane_terminal_bypass",
            {"occurrence": occurrence_record("so_terminal_bypass", "lane_terminal_bypass")},
        ))
        current = store.read_latest("STAGE_OCCURRENCE", "so_terminal_bypass")
        terminal = terminal_facts()
        terminal["produced_refs"] = []
        before = dict(store.snapshot_counts())
        with self.assertRaises(MutationRejected) as caught:
            mutation.apply(make_request(
                "TERMINATE_STAGE_OCCURRENCE",
                "req_terminal_bypass_terminal",
                "lane_terminal_bypass",
                {
                    "occurrence_id": "so_terminal_bypass",
                    "recorded_at": _time(20),
                    "terminal": terminal,
                },
                expected_state(
                    target_record_revision=current.record["record_revision"],
                    target_record_digest=current.digest,
                    work_scope_ref=current.record["work_scope_ref"],
                ),
            ))
        self.assertEqual("RESULT_MATERIALIZATION_REQUIRED", caught.exception.code)
        self.assertEqual(before, store.snapshot_counts())
        self.assertEqual(
            "OPEN",
            store.read_latest("STAGE_OCCURRENCE", "so_terminal_bypass").record["state"],
        )

    def test_thirty_minute_unresolved_delivery_persists_delivery_uncertain_without_replacement_occurrence(self):
        store = self._store("time-uncertainty")
        mutation = MutationService(store)
        scheduled = mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_time_uncertainty_schedule",
            "lane_time_uncertainty",
            {"occurrence": occurrence_record("so_time_uncertainty", "lane_time_uncertainty")},
        ))
        outbox_id = scheduled["outbox_ids"][0]
        surface = DeterministicExecutionSurface()
        DispatchService(
            store,
            surface,
            authorization_resolver=dispatch_authorization(),
        ).dispatch(outbox_id, attempted_at=_time(0))
        self.assertIsNone(store.read_delivery_state(outbox_id)["diagnostic_state"])

        RecoveryCoordinator(store, surface).reconcile_outbox(
            outbox_id,
            observed_at=_time(1800),
        )
        state = store.read_delivery_state(outbox_id)
        self.assertEqual("DELIVERY_UNCERTAIN", state["diagnostic_state"])
        self.assertEqual(1, state["attempt_count"])
        self.assertEqual(1, len(store.read_revisions("STAGE_OCCURRENCE", "so_time_uncertainty")))


if __name__ == "__main__":
    unittest.main()
