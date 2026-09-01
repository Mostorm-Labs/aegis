from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tests.control_plane.cp_i05_fixtures import (
    PACKAGE_ID,
    RESULT_REF,
    TASK_ANCHOR,
    configured_mutation,
    dispatch_authorization,
    navigation,
    result_trust,
    seed_surface,
)
from tools.aegis_control.dispatch import DispatchRejected, DispatchService
from tools.aegis_control.execution_surface import DeterministicExecutionSurface
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.recovery import RecoveryCoordinator
from tools.aegis_control.store import ControlStore
from tools.aegis_control.trust import TrustResolver


def _time(seconds: int) -> str:
    value = datetime(2026, 9, 1, 2, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return value.isoformat().replace("+00:00", "Z")


class CpI05P36RepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _store(self, name: str) -> ControlStore:
        return ControlStore(str(Path(self.tmp.name) / f"{name}.db"))

    def _schedule(self, mutation, occurrence_id, lane_id, *, stage="P32", owner="aegis-implementation"):
        record = occurrence_record(occurrence_id, lane_id)
        record["stage_span"] = {"stages": [stage]}
        record["primary_owner"] = owner
        return mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            f"req_{occurrence_id}_schedule",
            lane_id,
            {"occurrence": record},
        ))

    def _progress_request(self, store, occurrence_id, lane_id, checkpoint, request_id):
        current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
        return make_request(
            "RECORD_EXECUTION_PROGRESS",
            request_id,
            lane_id,
            {
                "occurrence_id": occurrence_id,
                "recorded_at": _time(10),
                "execution_navigation": checkpoint,
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        )

    def _terminate(self, mutation, store, occurrence_id, lane_id, refs, request_id):
        current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
        terminal = terminal_facts()
        terminal["produced_refs"] = list(refs)
        return mutation.apply(make_request(
            "TERMINATE_STAGE_OCCURRENCE",
            request_id,
            lane_id,
            {
                "occurrence_id": occurrence_id,
                "recorded_at": _time(20),
                "terminal": terminal,
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        ))

    def test_b1_flat_navigation_is_rejected_with_zero_residue(self):
        store = self._store("b1-flat")
        mutation = MutationService(store)
        self._schedule(mutation, "so_b1_flat", "lane_b1_flat")
        before = dict(store.snapshot_counts())
        flat = {
            "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
            "classification": "EXACT_CURSOR",
            "accepted_revision": "exec-flat",
            "completed_through": ["implementation"],
            "next_action": "review",
        }
        with self.assertRaises(MutationRejected) as caught:
            mutation.apply(self._progress_request(
                store, "so_b1_flat", "lane_b1_flat", flat, "req_b1_flat_progress"
            ))
        self.assertEqual("INVALID_EXECUTION_NAVIGATION", caught.exception.code)
        self.assertEqual(before, store.snapshot_counts())

    def test_b1_exact_checkpoint_replays_exact_request_and_preserves_start_facts(self):
        store = self._store("b1-exact")
        surface = DeterministicExecutionSurface()
        seed_surface(
            surface,
            occurrence_id="so_b1_exact",
            execution_ref="exec://b1-exact",
            revision="exec-r1",
        )
        mutation = configured_mutation(store, surface)
        self._schedule(mutation, "so_b1_exact", "lane_b1_exact")
        before_record = deepcopy(store.read_latest("STAGE_OCCURRENCE", "so_b1_exact").record)
        checkpoint = navigation("exec://b1-exact", "exec-r1")
        request = self._progress_request(
            store, "so_b1_exact", "lane_b1_exact", checkpoint, "req_b1_exact_progress"
        )
        first = mutation.apply(request)
        replay = mutation.apply(request)
        self.assertEqual(first, replay)
        latest = store.read_latest("STAGE_OCCURRENCE", "so_b1_exact").record
        self.assertEqual(2, latest["record_revision"])
        self.assertEqual(checkpoint, latest["execution_navigation"])
        for field in (
            "control_lane_id", "work_scope_ref", "stage_span", "primary_owner",
            "trusted_basis", "policy_binding", "schedule_basis", "input_refs", "repair_context",
        ):
            self.assertEqual(before_record[field], latest[field], field)

        surface.set_execution_revision("exec://b1-exact", "exec-r2", ancestor_revision="exec-r1")
        before = dict(store.snapshot_counts())
        with self.assertRaises(MutationRejected) as caught:
            mutation.apply(self._progress_request(
                store,
                "so_b1_exact",
                "lane_b1_exact",
                navigation("exec://b1-exact", "exec-r1"),
                "req_b1_stale_position",
            ))
        self.assertEqual("EXECUTION_NAVIGATION_DIVERGENCE", caught.exception.code)
        self.assertEqual(before, store.snapshot_counts())

    def test_b1_wrong_task_anchor_fails_closed(self):
        store = self._store("b1-anchor")
        surface = DeterministicExecutionSurface()
        seed_surface(surface, occurrence_id="so_b1_anchor", execution_ref="exec://b1-anchor")
        mutation = configured_mutation(store, surface)
        self._schedule(mutation, "so_b1_anchor", "lane_b1_anchor")
        bad = navigation("exec://b1-anchor", "exec-r1")
        bad["task_anchor"] = {"revision": "0" * 40, "relation": "ancestor"}
        before = dict(store.snapshot_counts())
        with self.assertRaises(MutationRejected) as caught:
            mutation.apply(self._progress_request(
                store, "so_b1_anchor", "lane_b1_anchor", bad, "req_b1_wrong_anchor"
            ))
        self.assertEqual("EXECUTION_NAVIGATION_DIVERGENCE", caught.exception.code)
        self.assertEqual(before, store.snapshot_counts())

    def test_b2_result_requires_exact_resolution_and_matching_lineage(self):
        store = self._store("b2-exact")
        surface = DeterministicExecutionSurface()
        seed_surface(surface, occurrence_id="so_b2_exact", execution_ref="exec://b2-exact")
        mutation = configured_mutation(
            store,
            surface,
            result_resolver=result_trust(occurrence_id="so_b2_exact"),
        )
        self._schedule(mutation, "so_b2_exact", "lane_b2_exact")
        mutation.apply(self._progress_request(
            store,
            "so_b2_exact",
            "lane_b2_exact",
            navigation("exec://b2-exact", "exec-r1"),
            "req_b2_exact_progress",
        ))
        self.assertEqual(
            "APPLIED",
            self._terminate(
                mutation, store, "so_b2_exact", "lane_b2_exact", [RESULT_REF], "req_b2_exact_terminal"
            )["status"],
        )

        store = self._store("b2-unresolvable")
        surface = DeterministicExecutionSurface()
        seed_surface(surface, occurrence_id="so_b2_unresolvable", execution_ref="exec://b2-unresolvable")
        mutation = configured_mutation(store, surface, result_resolver=TrustResolver({}))
        self._schedule(mutation, "so_b2_unresolvable", "lane_b2_unresolvable")
        mutation.apply(self._progress_request(
            store,
            "so_b2_unresolvable",
            "lane_b2_unresolvable",
            navigation("exec://b2-unresolvable", "exec-r1"),
            "req_b2_unresolvable_progress",
        ))
        before = dict(store.snapshot_counts())
        with self.assertRaises(MutationRejected) as caught:
            self._terminate(
                mutation,
                store,
                "so_b2_unresolvable",
                "lane_b2_unresolvable",
                [RESULT_REF],
                "req_b2_unresolvable_terminal",
            )
        self.assertEqual("RESULT_MATERIALIZATION_UNRESOLVABLE", caught.exception.code)
        self.assertEqual(before, store.snapshot_counts())

        store = self._store("b2-lineage")
        surface = DeterministicExecutionSurface()
        seed_surface(surface, occurrence_id="so_b2_lineage", execution_ref="exec://b2-lineage")
        mutation = configured_mutation(
            store,
            surface,
            result_resolver=result_trust(occurrence_id="another-occurrence"),
        )
        self._schedule(mutation, "so_b2_lineage", "lane_b2_lineage")
        mutation.apply(self._progress_request(
            store,
            "so_b2_lineage",
            "lane_b2_lineage",
            navigation("exec://b2-lineage", "exec-r1"),
            "req_b2_lineage_progress",
        ))
        with self.assertRaises(MutationRejected) as caught:
            self._terminate(
                mutation, store, "so_b2_lineage", "lane_b2_lineage", [RESULT_REF], "req_b2_lineage_terminal"
            )
        self.assertEqual("RESULT_MATERIALIZATION_LINEAGE_MISMATCH", caught.exception.code)

    def test_b2_mutable_result_identity_fails_closed(self):
        mutable_ref = deepcopy(RESULT_REF)
        mutable_ref["identity"] = {"scheme": "branch", "value": "main"}
        store = self._store("b2-unpinned")
        surface = DeterministicExecutionSurface()
        seed_surface(surface, occurrence_id="so_b2_unpinned", execution_ref="exec://b2-unpinned")
        mutation = configured_mutation(store, surface, result_resolver=TrustResolver({}))
        self._schedule(mutation, "so_b2_unpinned", "lane_b2_unpinned")
        mutation.apply(self._progress_request(
            store,
            "so_b2_unpinned",
            "lane_b2_unpinned",
            navigation("exec://b2-unpinned", "exec-r1"),
            "req_b2_unpinned_progress",
        ))
        with self.assertRaises(MutationRejected) as caught:
            self._terminate(
                mutation, store, "so_b2_unpinned", "lane_b2_unpinned", [mutable_ref], "req_b2_unpinned_terminal"
            )
        self.assertEqual("RESULT_MATERIALIZATION_UNPINNED", caught.exception.code)

    def test_b3_current_authorization_cannot_be_spoofed_by_caller(self):
        store = self._store("b3-current")
        scheduled = self._schedule(MutationService(store), "so_b3_current", "lane_b3_current")
        surface = DeterministicExecutionSurface()
        service = DispatchService(
            store, surface, authorization_resolver=dispatch_authorization()
        )
        receipt = service.dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        self.assertTrue(receipt.authorization_basis_digest.startswith("sha256:"))

        store = self._store("b3-cross")
        scheduled = self._schedule(
            MutationService(store),
            "so_b3_cross",
            "lane_b3_cross",
            stage="P34",
            owner="aegis-gate-review",
        )
        surface = DeterministicExecutionSurface()
        service = DispatchService(
            store, surface, authorization_resolver=dispatch_authorization()
        )
        before = dict(store.snapshot_counts())
        with self.assertRaises(DispatchRejected) as caught:
            service.dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        self.assertEqual("CURRENT_CROSS_PRIMARY_ROLLOUT_DENIED", caught.exception.code)
        self.assertEqual(0, surface.provider_request_count)
        self.assertEqual(before, store.snapshot_counts())

        store = self._store("b3-noncurrent")
        scheduled = self._schedule(MutationService(store), "so_b3_noncurrent", "lane_b3_noncurrent")
        surface = DeterministicExecutionSurface()
        service = DispatchService(
            store,
            surface,
            authorization_resolver=dispatch_authorization(satisfies=False),
        )
        with self.assertRaises(DispatchRejected) as caught:
            service.dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        self.assertEqual("DISPATCH_NOT_AUTHORIZED", caught.exception.code)
        self.assertEqual(0, surface.provider_request_count)

    def test_b4_retry_uncertainty_ack_loss_and_reconciliation_are_wired(self):
        store = self._store("b4-retry")
        scheduled = self._schedule(MutationService(store), "so_b4_retry", "lane_b4_retry")
        outbox_id = scheduled["outbox_ids"][0]
        surface = DeterministicExecutionSurface()
        service = DispatchService(store, surface, authorization_resolver=dispatch_authorization())
        service.dispatch(outbox_id, attempted_at=_time(0))
        with self.assertRaises(DispatchRejected) as caught:
            service.dispatch(outbox_id, attempted_at=_time(0))
        self.assertEqual("RETRY_NOT_YET_ELIGIBLE", caught.exception.code)
        for second in [1, 3, 7, 15, 31, 61, 121, 421, 721, 1021, 1321]:
            service.dispatch(outbox_id, attempted_at=_time(second))
        state = store.read_delivery_state(outbox_id)
        self.assertEqual(12, state["attempt_count"])
        self.assertEqual("DELIVERY_UNCERTAIN", state["diagnostic_state"])
        self.assertEqual(1, len(store.read_revisions("STAGE_OCCURRENCE", "so_b4_retry")))

        store = self._store("b4-restart")
        surface = DeterministicExecutionSurface()
        mutation = configured_mutation(
            store,
            surface,
            result_resolver=result_trust(occurrence_id="so_b4_restart"),
        )
        scheduled = self._schedule(mutation, "so_b4_restart", "lane_b4_restart")
        outbox_id = scheduled["outbox_ids"][0]

        class WorkerCrash(RuntimeError):
            pass

        def crash(checkpoint):
            if checkpoint == "after_provider_dispatch":
                raise WorkerCrash

        crashing = DispatchService(
            store,
            surface,
            authorization_resolver=dispatch_authorization(),
            fault_injector=crash,
        )
        with self.assertRaises(WorkerCrash):
            crashing.dispatch(outbox_id, attempted_at=_time(0))
        self.assertEqual(1, surface.unique_execution_count)
        self.assertIsNone(store.read_delivery_state(outbox_id)["provider_correlation_id"])

        restarted = DispatchService(
            store, surface, authorization_resolver=dispatch_authorization()
        )
        receipt = restarted.dispatch(outbox_id, attempted_at=_time(1))
        self.assertEqual(1, surface.unique_execution_count)
        self.assertEqual(receipt.correlation_id, store.read_delivery_state(outbox_id)["provider_correlation_id"])

        surface.set_observation(
            receipt.correlation_id,
            state="RUNNING",
            execution_ref="exec://b4-restart",
            execution_revision="exec-r1",
            completed_through=["implementation"],
            next_action="review",
        )
        recovery = RecoveryCoordinator(
            store,
            surface,
            mutation=mutation,
            task_anchor_revision=TASK_ANCHOR,
            execution_surface_name="CODE_EXECUTION",
        )
        self.assertEqual("RUNNING", recovery.reconcile_outbox(
            outbox_id, observed_at=_time(31)
        ).state)
        self.assertEqual(2, store.read_latest("STAGE_OCCURRENCE", "so_b4_restart").record["record_revision"])

        surface.set_observation(
            receipt.correlation_id,
            state="MATERIALIZED",
            execution_ref="exec://b4-restart",
            execution_revision="exec-r1",
            completed_through=["implementation"],
            next_action="review",
            materialized_ref=RESULT_REF,
        )
        self.assertEqual("MATERIALIZED", recovery.reconcile_outbox(
            outbox_id, observed_at=_time(61)
        ).state)
        latest = store.read_latest("STAGE_OCCURRENCE", "so_b4_restart")
        self.assertEqual("TERMINAL", latest.record["state"])
        terminal_revision = latest.record["record_revision"]
        recovery.reconcile_outbox(outbox_id, observed_at=_time(91), event_hint=True)
        self.assertEqual(
            terminal_revision,
            store.read_latest("STAGE_OCCURRENCE", "so_b4_restart").record["record_revision"],
        )
        self.assertEqual(
            1,
            sum(
                item.record["state"] == "TERMINAL"
                for item in store.read_revisions("STAGE_OCCURRENCE", "so_b4_restart")
            ),
        )


if __name__ == "__main__":
    unittest.main()
