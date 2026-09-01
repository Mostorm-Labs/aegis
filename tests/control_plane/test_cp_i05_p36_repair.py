from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tools.aegis_control.canonical import canonical_digest
import tools.aegis_control.dispatch as dispatch_module
import tools.aegis_control.execution_surface as execution_surface_module
from tools.aegis_control.external_ports import DeterministicExternalAdapter
from tools.aegis_control.mutation import MutationRejected, MutationService
import tools.aegis_control.recovery as recovery_module
from tools.aegis_control.store import ControlStore
import tools.aegis_control.trust as trust_module


TASK_ANCHOR = "a3fd350c350bec9220a1c6e283de88c14dfbcd2a"
PACKAGE_ID = "CP-I05-P31-01"
RESULT_REF = {
    "object_type": "RESULT",
    "id": "result_cp_i05_p36",
    "ref": "github:artifact:cp-i05-p36-result",
    "identity": {"scheme": "sha256", "value": "sha256:" + "7" * 64},
}
POLICY_REF = {
    "object_type": "CONTRACT",
    "id": "contract_cp_i05_dispatch_current",
    "ref": "control:dispatch-policy:current",
    "identity": {"scheme": "sha256", "value": "sha256:" + "8" * 64},
}


def _time(seconds: int) -> str:
    value = datetime(2026, 9, 1, 2, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return value.isoformat().replace("+00:00", "Z")


def _navigation(execution_ref: str, revision: str, *, anchor: str = TASK_ANCHOR, next_action: str = "review"):
    return {
        "execution_surface": "CODE_EXECUTION",
        "task_anchor": {"revision": anchor, "relation": "ancestor"},
        "execution_cursor": {
            "execution_ref": execution_ref,
            "revision": revision,
            "completed_through": ["implementation"],
            "next_action": next_action,
        },
    }


def _policy_trust(*, satisfies: bool = True) -> trust_module.TrustResolver:
    adapter = DeterministicExternalAdapter(
        source_kind="control-policy",
        adapter_id="cp-i05-policy",
        secret=b"cp-i05-policy-secret",
        callback_available=False,
        query_correlation_available=True,
    )
    adapter.set_resource(
        "dispatch-current",
        version_scheme="sha256",
        version_value=POLICY_REF["identity"]["value"],
        resolved_refs=[POLICY_REF],
        satisfies=satisfies,
    )
    return trust_module.TrustResolver({"control-policy": adapter})


class CpI05P36RepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _store(self, name: str) -> ControlStore:
        return ControlStore(str(Path(self.tmp.name) / f"{name}.db"))

    def _position_resolver(self, surface, *, anchor: str = TASK_ANCHOR):
        cls = getattr(execution_surface_module, "ExecutionPositionResolver", None)
        self.assertIsNotNone(cls, "CP-I05 must expose the P33 execution-position validation boundary")
        return cls(
            authorized_task_anchor=anchor,
            current_revision=surface.current_revision,
            is_ancestor=surface.is_ancestor,
        )

    def _result_trust(self, *, occurrence_id: str, result_ref=RESULT_REF, ambiguous: bool = False, satisfies: bool = True):
        request_cls = getattr(trust_module, "ResultMaterializationRequest", None)
        self.assertIsNotNone(request_cls, "CP-I05 must expose exact RESULT materialization lineage binding")
        adapter = DeterministicExternalAdapter(
            source_kind="result-store",
            adapter_id="cp-i05-result",
            secret=b"cp-i05-result-secret",
            callback_available=False,
            query_correlation_available=True,
        )
        adapter.set_resource(
            "result-current",
            version_scheme=result_ref["identity"]["scheme"],
            version_value=result_ref["identity"]["value"],
            resolved_refs=[result_ref],
            satisfies=satisfies,
            ambiguous=ambiguous,
        )
        request = request_cls(
            source_kind="result-store",
            resource_key="result-current",
            occurrence_id=occurrence_id,
            package_id=PACKAGE_ID,
            task_anchor_revision=TASK_ANCHOR,
        )
        try:
            return trust_module.TrustResolver(
                {"result-store": adapter},
                result_sources={canonical_digest(result_ref): request},
            )
        except TypeError as exc:
            self.fail(f"TrustResolver must accept exact result_sources: {exc}")

    def _configured_mutation(self, store, surface, *, occurrence_id: str, result_trust=None):
        try:
            return MutationService(
                store,
                trust_resolver=result_trust,
                execution_position_resolver=self._position_resolver(surface),
                implementation_package_id=PACKAGE_ID,
                task_anchor_revision=TASK_ANCHOR,
            )
        except TypeError as exc:
            self.fail(f"MutationService must enforce CP-I05 execution/result boundaries: {exc}")

    def _schedule(self, mutation: MutationService, occurrence_id: str, lane_id: str, *, stage: str = "P32", owner: str = "aegis-implementation"):
        occurrence = occurrence_record(occurrence_id, lane_id)
        occurrence["stage_span"] = {"stages": [stage]}
        occurrence["primary_owner"] = owner
        return mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            f"req_{occurrence_id}_schedule",
            lane_id,
            {"occurrence": occurrence},
        ))

    def _progress(self, mutation: MutationService, store: ControlStore, occurrence_id: str, lane_id: str, navigation, *, request_id: str):
        current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
        return mutation.apply(make_request(
            "RECORD_EXECUTION_PROGRESS",
            request_id,
            lane_id,
            {
                "occurrence_id": occurrence_id,
                "recorded_at": _time(10),
                "execution_navigation": navigation,
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        ))

    def _terminate(self, mutation: MutationService, store: ControlStore, occurrence_id: str, lane_id: str, produced_refs, *, request_id: str):
        current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
        terminal = terminal_facts()
        terminal["produced_refs"] = list(produced_refs)
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

    def test_b1_flat_navigation_shape_is_rejected_with_zero_residue(self):
        store = self._store("b1-flat")
        mutation = MutationService(store)
        self._schedule(mutation, "so_b1_flat", "lane_b1_flat")
        current = store.read_latest("STAGE_OCCURRENCE", "so_b1_flat")
        before = dict(store.snapshot_counts())
        flat = {
            "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
            "classification": "EXACT_CURSOR",
            "accepted_revision": "exec-flat",
            "completed_through": ["implementation"],
            "next_action": "review",
        }
        with self.assertRaises(MutationRejected) as caught:
            self._progress(mutation, store, "so_b1_flat", "lane_b1_flat", flat, request_id="req_b1_flat_progress")
        self.assertEqual("INVALID_EXECUTION_NAVIGATION", caught.exception.code)
        self.assertEqual(before, store.snapshot_counts())
        self.assertEqual(current.digest, store.read_latest("STAGE_OCCURRENCE", "so_b1_flat").digest)

    def test_b1_exact_navigation_requires_reconciled_position_and_preserves_frozen_facts(self):
        store = self._store("b1-exact")
        surface = execution_surface_module.DeterministicExecutionSurface()
        surface.seed_execution(
            occurrence_id="so_b1_exact",
            correlation_id="corr_b1_exact",
            execution_ref="exec://b1-exact",
            revision="exec-r1",
            state="RUNNING",
            completed_through=["implementation"],
            next_action="review",
        )
        mutation = self._configured_mutation(store, surface, occurrence_id="so_b1_exact")
        self._schedule(mutation, "so_b1_exact", "lane_b1_exact")
        before_record = deepcopy(store.read_latest("STAGE_OCCURRENCE", "so_b1_exact").record)
        navigation = _navigation("exec://b1-exact", "exec-r1")
        first = self._progress(mutation, store, "so_b1_exact", "lane_b1_exact", navigation, request_id="req_b1_exact_progress")
        replay = self._progress(mutation, store, "so_b1_exact", "lane_b1_exact", navigation, request_id="req_b1_exact_progress")
        self.assertEqual(first, replay)
        latest = store.read_latest("STAGE_OCCURRENCE", "so_b1_exact").record
        self.assertEqual(2, latest["record_revision"])
        self.assertEqual(navigation, latest["execution_navigation"])
        for field in (
            "control_lane_id", "work_scope_ref", "stage_span", "primary_owner", "trusted_basis",
            "policy_binding", "schedule_basis", "input_refs", "repair_context",
        ):
            self.assertEqual(before_record[field], latest[field], field)

        surface.set_execution_revision("exec://b1-exact", "exec-r2", ancestor_revision="exec-r1")
        stale = _navigation("exec://b1-exact", "exec-r1")
        before = dict(store.snapshot_counts())
        with self.assertRaises(MutationRejected) as caught:
            self._progress(mutation, store, "so_b1_exact", "lane_b1_exact", stale, request_id="req_b1_stale_position")
        self.assertEqual("EXECUTION_NAVIGATION_DIVERGENCE", caught.exception.code)
        self.assertEqual(before, store.snapshot_counts())

    def test_b1_wrong_task_anchor_fails_closed(self):
        store = self._store("b1-anchor")
        surface = execution_surface_module.DeterministicExecutionSurface()
        surface.seed_execution(
            occurrence_id="so_b1_anchor",
            correlation_id="corr_b1_anchor",
            execution_ref="exec://b1-anchor",
            revision="exec-r1",
            state="RUNNING",
            completed_through=[],
            next_action="implementation",
        )
        mutation = self._configured_mutation(store, surface, occurrence_id="so_b1_anchor")
        self._schedule(mutation, "so_b1_anchor", "lane_b1_anchor")
        before = dict(store.snapshot_counts())
        with self.assertRaises(MutationRejected) as caught:
            self._progress(
                mutation,
                store,
                "so_b1_anchor",
                "lane_b1_anchor",
                _navigation("exec://b1-anchor", "exec-r1", anchor="0" * 40),
                request_id="req_b1_wrong_anchor",
            )
        self.assertEqual("EXECUTION_NAVIGATION_DIVERGENCE", caught.exception.code)
        self.assertEqual(before, store.snapshot_counts())

    def test_b2_unresolvable_result_cannot_complete_but_exact_result_can(self):
        # Negative: a structurally valid RESULT without an independently resolvable source is insufficient.
        store = self._store("b2-negative")
        surface = execution_surface_module.DeterministicExecutionSurface()
        surface.seed_execution(
            occurrence_id="so_b2_negative",
            correlation_id="corr_b2_negative",
            execution_ref="exec://b2-negative",
            revision="exec-r1",
            state="RUNNING",
            completed_through=["implementation"],
            next_action="review",
        )
        mutation = self._configured_mutation(store, surface, occurrence_id="so_b2_negative", result_trust=trust_module.TrustResolver({}))
        self._schedule(mutation, "so_b2_negative", "lane_b2_negative")
        self._progress(mutation, store, "so_b2_negative", "lane_b2_negative", _navigation("exec://b2-negative", "exec-r1"), request_id="req_b2_negative_progress")
        before = dict(store.snapshot_counts())
        with self.assertRaises(MutationRejected) as caught:
            self._terminate(mutation, store, "so_b2_negative", "lane_b2_negative", [RESULT_REF], request_id="req_b2_negative_terminal")
        self.assertEqual("RESULT_MATERIALIZATION_UNRESOLVABLE", caught.exception.code)
        self.assertEqual(before, store.snapshot_counts())
        self.assertEqual("OPEN", store.read_latest("STAGE_OCCURRENCE", "so_b2_negative").record["state"])

        # Positive: the same exact RESULT succeeds when the reviewer-resolvable source and lineage match.
        store = self._store("b2-positive")
        surface = execution_surface_module.DeterministicExecutionSurface()
        surface.seed_execution(
            occurrence_id="so_b2_positive",
            correlation_id="corr_b2_positive",
            execution_ref="exec://b2-positive",
            revision="exec-r1",
            state="RUNNING",
            completed_through=["implementation"],
            next_action="review",
        )
        result_trust = self._result_trust(occurrence_id="so_b2_positive")
        mutation = self._configured_mutation(store, surface, occurrence_id="so_b2_positive", result_trust=result_trust)
        self._schedule(mutation, "so_b2_positive", "lane_b2_positive")
        self._progress(mutation, store, "so_b2_positive", "lane_b2_positive", _navigation("exec://b2-positive", "exec-r1"), request_id="req_b2_positive_progress")
        result = self._terminate(mutation, store, "so_b2_positive", "lane_b2_positive", [RESULT_REF], request_id="req_b2_positive_terminal")
        self.assertEqual("APPLIED", result["status"])
        self.assertEqual("TERMINAL", store.read_latest("STAGE_OCCURRENCE", "so_b2_positive").record["state"])

    def test_b2_result_lineage_mismatch_and_unpinned_identity_fail_closed(self):
        # Lineage mismatch.
        store = self._store("b2-lineage")
        surface = execution_surface_module.DeterministicExecutionSurface()
        surface.seed_execution(
            occurrence_id="so_b2_lineage",
            correlation_id="corr_b2_lineage",
            execution_ref="exec://b2-lineage",
            revision="exec-r1",
            state="RUNNING",
            completed_through=["implementation"],
            next_action="review",
        )
        result_trust = self._result_trust(occurrence_id="some_other_occurrence")
        mutation = self._configured_mutation(store, surface, occurrence_id="so_b2_lineage", result_trust=result_trust)
        self._schedule(mutation, "so_b2_lineage", "lane_b2_lineage")
        self._progress(mutation, store, "so_b2_lineage", "lane_b2_lineage", _navigation("exec://b2-lineage", "exec-r1"), request_id="req_b2_lineage_progress")
        before = dict(store.snapshot_counts())
        with self.assertRaises(MutationRejected) as caught:
            self._terminate(mutation, store, "so_b2_lineage", "lane_b2_lineage", [RESULT_REF], request_id="req_b2_lineage_terminal")
        self.assertEqual("RESULT_MATERIALIZATION_LINEAGE_MISMATCH", caught.exception.code)
        self.assertEqual(before, store.snapshot_counts())

        # Mutable/unproven identity.
        mutable_ref = deepcopy(RESULT_REF)
        mutable_ref["identity"] = {"scheme": "branch", "value": "main"}
        store = self._store("b2-unpinned")
        surface = execution_surface_module.DeterministicExecutionSurface()
        surface.seed_execution(
            occurrence_id="so_b2_unpinned",
            correlation_id="corr_b2_unpinned",
            execution_ref="exec://b2-unpinned",
            revision="exec-r1",
            state="RUNNING",
            completed_through=["implementation"],
            next_action="review",
        )
        mutation = self._configured_mutation(store, surface, occurrence_id="so_b2_unpinned", result_trust=trust_module.TrustResolver({}))
        self._schedule(mutation, "so_b2_unpinned", "lane_b2_unpinned")
        self._progress(mutation, store, "so_b2_unpinned", "lane_b2_unpinned", _navigation("exec://b2-unpinned", "exec-r1"), request_id="req_b2_unpinned_progress")
        with self.assertRaises(MutationRejected) as caught:
            self._terminate(mutation, store, "so_b2_unpinned", "lane_b2_unpinned", [mutable_ref], request_id="req_b2_unpinned_terminal")
        self.assertEqual("RESULT_MATERIALIZATION_UNPINNED", caught.exception.code)

    def test_b3_dispatch_uses_current_exact_authorization_not_caller_boolean(self):
        resolver_cls = getattr(dispatch_module, "DispatchAuthorizationResolver", None)
        self.assertIsNotNone(resolver_cls, "dispatch must resolve Current authorization internally")
        request = trust_module.TrustFactRequest("control-policy", "dispatch-current")

        store = self._store("b3-authorized")
        mutation = MutationService(store)
        scheduled = self._schedule(mutation, "so_b3_authorized", "lane_b3_authorized")
        surface = execution_surface_module.DeterministicExecutionSurface()
        auth = resolver_cls(_policy_trust(), request, source_primary_owner="aegis-implementation")
        service = dispatch_module.DispatchService(store, surface, authorization_resolver=auth)
        receipt = service.dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        self.assertTrue(receipt.acknowledged)
        self.assertTrue(receipt.authorization_basis_digest.startswith("sha256:"))

        # A currently denied cross-Primary path cannot be forced by a caller flag because no such flag exists.
        store = self._store("b3-cross-primary")
        mutation = MutationService(store)
        scheduled = self._schedule(
            mutation,
            "so_b3_cross_primary",
            "lane_b3_cross_primary",
            stage="P34",
            owner="aegis-gate-review",
        )
        surface = execution_surface_module.DeterministicExecutionSurface()
        auth = resolver_cls(_policy_trust(), request, source_primary_owner="aegis-implementation")
        service = dispatch_module.DispatchService(store, surface, authorization_resolver=auth)
        before = dict(store.snapshot_counts())
        with self.assertRaises(dispatch_module.DispatchRejected) as caught:
            service.dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        self.assertEqual("CURRENT_CROSS_PRIMARY_ROLLOUT_DENIED", caught.exception.code)
        self.assertEqual(0, surface.provider_request_count)
        self.assertEqual(before, store.snapshot_counts())

        # A non-Current/denied source also fails closed.
        store = self._store("b3-noncurrent")
        mutation = MutationService(store)
        scheduled = self._schedule(mutation, "so_b3_noncurrent", "lane_b3_noncurrent")
        surface = execution_surface_module.DeterministicExecutionSurface()
        auth = resolver_cls(_policy_trust(satisfies=False), request, source_primary_owner="aegis-implementation")
        service = dispatch_module.DispatchService(store, surface, authorization_resolver=auth)
        with self.assertRaises(dispatch_module.DispatchRejected) as caught:
            service.dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        self.assertEqual("DISPATCH_NOT_AUTHORIZED", caught.exception.code)
        self.assertEqual(0, surface.provider_request_count)

    def test_b4_retry_eligibility_and_delivery_uncertainty_are_wired(self):
        resolver_cls = getattr(dispatch_module, "DispatchAuthorizationResolver", None)
        self.assertIsNotNone(resolver_cls)
        auth = resolver_cls(
            _policy_trust(),
            trust_module.TrustFactRequest("control-policy", "dispatch-current"),
            source_primary_owner="aegis-implementation",
        )
        store = self._store("b4-retry")
        mutation = MutationService(store)
        scheduled = self._schedule(mutation, "so_b4_retry", "lane_b4_retry")
        outbox_id = scheduled["outbox_ids"][0]
        surface = execution_surface_module.DeterministicExecutionSurface()
        service = dispatch_module.DispatchService(store, surface, authorization_resolver=auth)
        service.dispatch(outbox_id, attempted_at=_time(0))
        with self.assertRaises(dispatch_module.DispatchRejected) as caught:
            service.dispatch(outbox_id, attempted_at=_time(0))
        self.assertEqual("RETRY_NOT_YET_ELIGIBLE", caught.exception.code)
        self.assertEqual(1, surface.provider_request_count)

        times = [1, 3, 7, 15, 31, 61, 121, 421, 721, 1021, 1321]
        for second in times:
            service.dispatch(outbox_id, attempted_at=_time(second))
        state = store.read_delivery_state(outbox_id)
        self.assertEqual(12, state["attempt_count"])
        self.assertEqual("DELIVERY_UNCERTAIN", state["diagnostic_state"])
        self.assertEqual(1, len(store.read_revisions("STAGE_OCCURRENCE", "so_b4_retry")))

    def test_b4_provider_ack_loss_restart_and_query_reconciliation_reuse_one_execution(self):
        resolver_cls = getattr(dispatch_module, "DispatchAuthorizationResolver", None)
        self.assertIsNotNone(resolver_cls)
        auth = resolver_cls(
            _policy_trust(),
            trust_module.TrustFactRequest("control-policy", "dispatch-current"),
            source_primary_owner="aegis-implementation",
        )
        store = self._store("b4-restart")
        surface = execution_surface_module.DeterministicExecutionSurface()
        result_trust = self._result_trust(occurrence_id="so_b4_restart")
        mutation = self._configured_mutation(store, surface, occurrence_id="so_b4_restart", result_trust=result_trust)
        scheduled = self._schedule(mutation, "so_b4_restart", "lane_b4_restart")
        outbox_id = scheduled["outbox_ids"][0]

        class WorkerCrash(RuntimeError):
            pass

        def crash(checkpoint):
            if checkpoint == "after_provider_dispatch":
                raise WorkerCrash("simulated local acknowledgement loss")

        try:
            crashing = dispatch_module.DispatchService(store, surface, authorization_resolver=auth, fault_injector=crash)
        except TypeError as exc:
            self.fail(f"DispatchService must expose deterministic crash checkpoint: {exc}")
        with self.assertRaises(WorkerCrash):
            crashing.dispatch(outbox_id, attempted_at=_time(0))
        self.assertEqual(1, surface.unique_execution_count)
        self.assertIsNone(store.read_delivery_state(outbox_id)["provider_correlation_id"])

        restarted = dispatch_module.DispatchService(store, surface, authorization_resolver=auth)
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
        recovery = recovery_module.RecoveryCoordinator(
            store,
            surface,
            mutation=mutation,
            task_anchor_revision=TASK_ANCHOR,
            execution_surface_name="CODE_EXECUTION",
        )
        running = recovery.reconcile_outbox(outbox_id, observed_at=_time(31))
        self.assertEqual("RUNNING", running.state)
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
        materialized = recovery.reconcile_outbox(outbox_id, observed_at=_time(61))
        self.assertEqual("MATERIALIZED", materialized.state)
        latest = store.read_latest("STAGE_OCCURRENCE", "so_b4_restart")
        self.assertEqual("TERMINAL", latest.record["state"])
        terminal_revision = latest.record["record_revision"]

        # Duplicate callback/query wakeups cannot append another terminal revision.
        recovery.reconcile_outbox(outbox_id, observed_at=_time(91), event_hint=True)
        latest = store.read_latest("STAGE_OCCURRENCE", "so_b4_restart")
        self.assertEqual(terminal_revision, latest.record["record_revision"])
        self.assertEqual(1, sum(1 for item in store.read_revisions("STAGE_OCCURRENCE", "so_b4_restart") if item.record["state"] == "TERMINAL"))


if __name__ == "__main__":
    unittest.main()
