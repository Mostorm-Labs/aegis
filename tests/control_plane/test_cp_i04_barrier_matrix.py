from __future__ import annotations

from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, package_record, terminal_facts
from tests.control_plane.test_cp_i04_required_child_barrier import (
    canonical_occurrence_ref,
    child_scope,
    exact_ref,
    internal_ref,
    root_scope,
    scoped_occurrence,
)
from tools import aegis_control


NOW = datetime(2026, 8, 31, 16, 8, tzinfo=timezone.utc)


class CpI04BarrierMatrixTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = aegis_control.ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.adapter = aegis_control.DeterministicExternalAdapter(
            source_kind="PROJECT_STATE",
            adapter_id="project-state-matrix",
            secret=b"cp-i04-matrix-secret",
            callback_available=True,
            query_correlation_available=True,
            clock=lambda: NOW,
        )
        self.contract = exact_ref("CONTRACT", "contract-matrix", "1")
        self.gate = exact_ref("GATE_DECISION", "gate-matrix", "2")
        self.adapter.set_resource(
            "matrix/acceptance",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[self.gate],
            satisfies=True,
        )
        self.resolver = aegis_control.TrustResolver(
            {"PROJECT_STATE": self.adapter},
            acceptance_contract_sources={
                aegis_control.canonical_digest(self.contract): aegis_control.TrustFactRequest(
                    "PROJECT_STATE", "matrix/acceptance"
                )
            },
        )
        self.mutation = aegis_control.MutationService(self.store, trust_resolver=self.resolver)

    def _schedule(self, record, request_id, *, predecessor_ref=None, package_ref=None, mutation=None):
        service = mutation or self.mutation
        request = make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            request_id,
            record["control_lane_id"],
            {"occurrence": record},
            expected_state(
                work_scope_ref=record["work_scope_ref"],
                predecessor_occurrence_ref=predecessor_ref,
                package_ref=package_ref,
            ),
        )
        return service.apply(request), request

    def _terminate(self, occurrence_id, lane_id, scope):
        current = self.store.read_latest("STAGE_OCCURRENCE", occurrence_id)
        self.mutation.apply(
            make_request(
                "TERMINATE_STAGE_OCCURRENCE",
                f"req_term_{occurrence_id}",
                lane_id,
                {"occurrence_id": occurrence_id, "terminal": terminal_facts(), "recorded_at": None},
                expected_state(
                    work_scope_ref=scope,
                    active_occurrence_ref=internal_ref(current),
                    target_record_revision=current.record["record_revision"],
                    target_record_digest=current.digest,
                ),
            )
        )
        return self.store.read_latest("STAGE_OCCURRENCE", occurrence_id)

    def _parent_child_terminal(self):
        parent_scope = root_scope("ws_matrix_parent")
        self._schedule(scoped_occurrence("so_matrix_parent", "lane_matrix_parent", parent_scope), "req_matrix_parent")
        parent_open = self.store.read_latest("STAGE_OCCURRENCE", "so_matrix_parent")
        child = child_scope(
            "ws_matrix_child",
            parent_scope,
            canonical_occurrence_ref(parent_open),
            self.contract,
        )
        self._schedule(scoped_occurrence("so_matrix_child", "lane_matrix_child", child), "req_matrix_child")
        child_terminal = self._terminate("so_matrix_child", "lane_matrix_child", child)
        parent_terminal = self._terminate("so_matrix_parent", "lane_matrix_parent", parent_scope)
        return parent_scope, parent_open, child, child_terminal, parent_terminal

    def test_ambiguous_and_conflicting_child_acceptance_leave_zero_residue(self):
        parent_scope, _, _, _, parent_terminal = self._parent_child_terminal()
        successor = scoped_occurrence("so_matrix_successor", "lane_matrix_parent", parent_scope)
        for ambiguous, conflict, expected_code in (
            (True, False, "CHILD_ACCEPTANCE_BASIS_AMBIGUOUS"),
            (False, True, "CHILD_ACCEPTANCE_BASIS_CONFLICT"),
        ):
            with self.subTest(expected_code=expected_code):
                self.adapter.set_resource(
                    "matrix/acceptance",
                    version_scheme="gate-decision",
                    version_value="d1",
                    resolved_refs=[self.gate],
                    satisfies=True,
                    ambiguous=ambiguous,
                    conflict=conflict,
                )
                before = dict(self.store.snapshot_counts())
                before_outbox = len(self.store.read_outbox())
                with self.assertRaises(aegis_control.MutationRejected) as raised:
                    self._schedule(
                        successor,
                        f"req_matrix_{expected_code.lower()}",
                        predecessor_ref=internal_ref(parent_terminal),
                    )
                self.assertEqual(expected_code, raised.exception.code)
                self.assertEqual(before, dict(self.store.snapshot_counts()))
                self.assertEqual(before_outbox, len(self.store.read_outbox()))
                self.assertIsNone(self.store.read_latest("STAGE_OCCURRENCE", successor["id"]))

    def test_provider_version_change_between_resolve_and_commit_fails_closed(self):
        parent_scope, _, _, _, parent_terminal = self._parent_child_terminal()
        successor = scoped_occurrence("so_matrix_stale", "lane_matrix_parent", parent_scope)
        gate_d2 = exact_ref("GATE_DECISION", "gate-matrix-d2", "3")

        def drift(name):
            if name == "after_child_acceptance_resolution":
                self.adapter.set_resource(
                    "matrix/acceptance",
                    version_scheme="gate-decision",
                    version_value="d2",
                    resolved_refs=[gate_d2],
                    satisfies=True,
                )

        stale_mutation = aegis_control.MutationService(
            self.store,
            trust_resolver=self.resolver,
            fault_injector=drift,
        )
        before = dict(self.store.snapshot_counts())
        before_outbox = len(self.store.read_outbox())
        with self.assertRaises(aegis_control.MutationRejected) as raised:
            self._schedule(
                successor,
                "req_matrix_stale",
                predecessor_ref=internal_ref(parent_terminal),
                mutation=stale_mutation,
            )
        self.assertEqual("REQUIRED_CHILD_WORK_NOT_ACCEPTED", raised.exception.code)
        self.assertEqual(before, dict(self.store.snapshot_counts()))
        self.assertEqual(before_outbox, len(self.store.read_outbox()))
        self.assertIsNone(self.store.read_latest("STAGE_OCCURRENCE", successor["id"]))

    def test_multiple_required_children_must_all_accept_before_single_successor(self):
        contract_two = exact_ref("CONTRACT", "contract-matrix-two", "4")
        gate_two = exact_ref("GATE_DECISION", "gate-matrix-two", "5")
        self.adapter.set_resource(
            "matrix/acceptance-two",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[gate_two],
            satisfies=False,
        )
        self.resolver = aegis_control.TrustResolver(
            {"PROJECT_STATE": self.adapter},
            acceptance_contract_sources={
                aegis_control.canonical_digest(self.contract): aegis_control.TrustFactRequest(
                    "PROJECT_STATE", "matrix/acceptance"
                ),
                aegis_control.canonical_digest(contract_two): aegis_control.TrustFactRequest(
                    "PROJECT_STATE", "matrix/acceptance-two"
                ),
            },
        )
        self.mutation = aegis_control.MutationService(self.store, trust_resolver=self.resolver)

        parent_scope = root_scope("ws_multi_parent")
        self._schedule(scoped_occurrence("so_multi_parent", "lane_multi_parent", parent_scope), "req_multi_parent")
        parent_open = self.store.read_latest("STAGE_OCCURRENCE", "so_multi_parent")
        spawn_ref = canonical_occurrence_ref(parent_open)
        child_one = child_scope("ws_multi_child_a", parent_scope, spawn_ref, self.contract)
        child_two = child_scope("ws_multi_child_b", parent_scope, spawn_ref, contract_two)
        self._schedule(scoped_occurrence("so_multi_child_a", "lane_multi_child_a", child_one), "req_multi_child_a")
        self._schedule(scoped_occurrence("so_multi_child_b", "lane_multi_child_b", child_two), "req_multi_child_b")
        self._terminate("so_multi_child_a", "lane_multi_child_a", child_one)
        self._terminate("so_multi_child_b", "lane_multi_child_b", child_two)
        parent_terminal = self._terminate("so_multi_parent", "lane_multi_parent", parent_scope)

        successor = scoped_occurrence("so_multi_successor", "lane_multi_parent", parent_scope)
        before = dict(self.store.snapshot_counts())
        with self.assertRaises(aegis_control.MutationRejected) as raised:
            self._schedule(successor, "req_multi_blocked", predecessor_ref=internal_ref(parent_terminal))
        self.assertEqual("REQUIRED_CHILD_WORK_NOT_ACCEPTED", raised.exception.code)
        self.assertEqual(before, dict(self.store.snapshot_counts()))

        self.adapter.set_resource(
            "matrix/acceptance-two",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[gate_two],
            satisfies=True,
        )
        result, _ = self._schedule(successor, "req_multi_successor", predecessor_ref=internal_ref(parent_terminal))
        self.assertEqual("APPLIED", result["status"])
        stored = self.store.read_latest("STAGE_OCCURRENCE", successor["id"])
        bindings = stored.record["schedule_basis"]["required_child_acceptance_bindings"]
        self.assertEqual(["ws_multi_child_a", "ws_multi_child_b"], [item["child_work_scope_ref"]["id"] for item in bindings])

    def test_package_work_scope_mismatch_fails_before_schedule_residue(self):
        package = package_record("pkg_scope_bound", "lane_pkg_scope")
        self.mutation.apply(
            make_request(
                "MATERIALIZE_IMPLEMENTATION_PACKAGE",
                "req_pkg_scope_bound",
                "lane_pkg_scope",
                {"package": package},
            )
        )
        stored_package = self.store.read_latest("VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "pkg_scope_bound")
        occurrence_scope = root_scope("ws_other_scope")
        occurrence = scoped_occurrence("so_pkg_scope_mismatch", "lane_other_scope", occurrence_scope)
        before = dict(self.store.snapshot_counts())
        with self.assertRaises(aegis_control.MutationRejected) as raised:
            self._schedule(
                occurrence,
                "req_pkg_scope_mismatch",
                package_ref=internal_ref(stored_package),
            )
        self.assertEqual("PACKAGE_WORK_SCOPE_MISMATCH", raised.exception.code)
        self.assertEqual(before, dict(self.store.snapshot_counts()))

    def test_barrier_crossing_replay_is_idempotent_without_duplicate_binding(self):
        parent_scope, _, _, _, parent_terminal = self._parent_child_terminal()
        successor = scoped_occurrence("so_matrix_idempotent", "lane_matrix_parent", parent_scope)
        _, request = self._schedule(
            successor,
            "req_matrix_idempotent",
            predecessor_ref=internal_ref(parent_terminal),
        )
        before = dict(self.store.snapshot_counts())
        first = self.mutation.apply(request)
        second = self.mutation.apply(request)
        self.assertEqual(first, second)
        self.assertEqual(before, dict(self.store.snapshot_counts()))
        stored = self.store.read_latest("STAGE_OCCURRENCE", successor["id"])
        self.assertEqual(1, len(stored.record["schedule_basis"]["required_child_acceptance_bindings"]))

    def test_direct_parent_cycle_is_rejected_with_zero_residue(self):
        parent_scope = root_scope("ws_cycle")
        self._schedule(scoped_occurrence("so_cycle_parent", "lane_cycle_parent", parent_scope), "req_cycle_parent")
        parent_open = self.store.read_latest("STAGE_OCCURRENCE", "so_cycle_parent")
        cyclic = child_scope("ws_cycle", parent_scope, canonical_occurrence_ref(parent_open), self.contract)
        occurrence = scoped_occurrence("so_cycle_child", "lane_cycle_child", cyclic)
        before = dict(self.store.snapshot_counts())
        with self.assertRaises(aegis_control.MutationRejected):
            self._schedule(occurrence, "req_cycle_child")
        self.assertEqual(before, dict(self.store.snapshot_counts()))


if __name__ == "__main__":
    unittest.main()
