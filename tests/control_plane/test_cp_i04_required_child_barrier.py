from __future__ import annotations

from datetime import datetime, timezone
import inspect
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tools import aegis_control


NOW = datetime(2026, 8, 31, 16, 4, tzinfo=timezone.utc)


def exact_ref(object_type: str, object_id: str, digit: str):
    return {
        "object_type": object_type,
        "id": object_id,
        "ref": f"test:{object_type}:{object_id}",
        "identity": {"scheme": "sha256", "value": "sha256:" + digit * 64},
    }


def root_scope(scope_id: str):
    return {
        "id_scheme": "control-work-scope-v0.2",
        "id": scope_id,
        "child_work_binding": None,
    }


def child_scope(scope_id: str, parent_scope: dict, spawned_by: dict, contract_ref: dict, *, gate="REQUIRED"):
    return {
        "id_scheme": "control-work-scope-v0.2",
        "id": scope_id,
        "child_work_binding": {
            "parent_work_scope_ref": {
                "id_scheme": parent_scope["id_scheme"],
                "id": parent_scope["id"],
            },
            "spawned_by_occurrence_ref": spawned_by,
            "parent_gate": gate,
            "acceptance_contract_refs": [contract_ref],
        },
    }


def scoped_occurrence(occurrence_id: str, lane_id: str, scope: dict):
    record = occurrence_record(occurrence_id, lane_id)
    record["work_scope_ref"] = scope
    record["schedule_basis"]["required_child_acceptance_bindings"] = []
    return record


def internal_ref(stored):
    return (
        f"{stored.record['kind']}:{stored.record['id']}"
        f"@{stored.record['record_revision']}#{stored.digest}"
    )


def canonical_occurrence_ref(stored):
    return {
        "object_type": "STAGE_OCCURRENCE",
        "id": stored.record["id"],
        "ref": f"control:STAGE_OCCURRENCE:{stored.record['id']}@{stored.record['record_revision']}",
        "identity": {"scheme": "sha256", "value": stored.digest},
    }


class CpI04RequiredChildBarrierTests(unittest.TestCase):
    def setUp(self):
        params = inspect.signature(aegis_control.MutationService).parameters
        if "trust_resolver" not in params:
            self.fail("CP-I04 MutationService trust boundary is not implemented")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = aegis_control.ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.adapter = aegis_control.DeterministicExternalAdapter(
            source_kind="PROJECT_STATE",
            adapter_id="project-state-barrier",
            secret=b"cp-i04-barrier-secret",
            callback_available=True,
            query_correlation_available=True,
            clock=lambda: NOW,
        )
        self.contract_ref = exact_ref("CONTRACT", "contract-child-gate", "8")
        self.gate_d1 = exact_ref("GATE_DECISION", "gate-child-d1", "9")
        self.adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[self.gate_d1],
            satisfies=False,
        )
        self.resolver = aegis_control.TrustResolver(
            {"PROJECT_STATE": self.adapter},
            acceptance_contract_sources={
                aegis_control.canonical_digest(self.contract_ref): aegis_control.TrustFactRequest(
                    "PROJECT_STATE", "child/acceptance"
                )
            },
        )
        self.mutation = aegis_control.MutationService(self.store, trust_resolver=self.resolver)

    def _schedule(self, record, request_id, *, predecessor_ref=None):
        return self.mutation.apply(
            make_request(
                "SCHEDULE_STAGE_OCCURRENCE",
                request_id,
                record["control_lane_id"],
                {"occurrence": record},
                expected_state(
                    work_scope_ref=record["work_scope_ref"],
                    predecessor_occurrence_ref=predecessor_ref,
                ),
            )
        )

    def _terminate(self, occurrence_id: str, lane_id: str, scope: dict):
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

    def _materialize_parent_and_child(self, *, gate="REQUIRED"):
        parent_scope = root_scope("ws_parent")
        parent_a = scoped_occurrence("so_parent_a", "lane_parent", parent_scope)
        self._schedule(parent_a, "req_parent_a")
        parent_open = self.store.read_latest("STAGE_OCCURRENCE", "so_parent_a")
        child_ws = child_scope(
            "ws_child",
            parent_scope,
            canonical_occurrence_ref(parent_open),
            self.contract_ref,
            gate=gate,
        )
        child_a = scoped_occurrence("so_child_a", "lane_child", child_ws)
        self._schedule(child_a, "req_child_a")
        child_terminal = self._terminate("so_child_a", "lane_child", child_ws)
        parent_terminal = self._terminate("so_parent_a", "lane_parent", parent_scope)
        return parent_scope, child_ws, parent_open, parent_terminal, child_terminal

    def test_required_child_blocks_then_binds_exact_acceptance_facts_atomically(self):
        parent_scope, child_ws, parent_open, parent_terminal, child_terminal = self._materialize_parent_and_child()
        successor = scoped_occurrence("so_parent_b", "lane_parent", parent_scope)
        before = dict(self.store.snapshot_counts())
        before_outbox = len(self.store.read_outbox())
        with self.assertRaises(aegis_control.MutationRejected) as raised:
            self._schedule(successor, "req_parent_b_blocked", predecessor_ref=internal_ref(parent_terminal))
        self.assertEqual("REQUIRED_CHILD_WORK_NOT_ACCEPTED", raised.exception.code)
        self.assertEqual(before, dict(self.store.snapshot_counts()))
        self.assertEqual(before_outbox, len(self.store.read_outbox()))

        self.adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[self.gate_d1],
            satisfies=True,
        )
        result = self._schedule(successor, "req_parent_b", predecessor_ref=internal_ref(parent_terminal))
        self.assertEqual("APPLIED", result["status"])
        stored = self.store.read_latest("STAGE_OCCURRENCE", "so_parent_b")
        bindings = stored.record["schedule_basis"]["required_child_acceptance_bindings"]
        self.assertEqual(1, len(bindings))
        binding = bindings[0]
        self.assertEqual(child_ws, binding["child_work_scope_ref"])
        self.assertEqual(canonical_occurrence_ref(parent_open), binding["barrier_after_occurrence_ref"])
        self.assertEqual(canonical_occurrence_ref(child_terminal), binding["child_completion_occurrence_ref"])
        self.assertEqual([self.contract_ref], binding["acceptance_contract_refs"])
        self.assertEqual([self.gate_d1], binding["acceptance_fact_refs"])
        self.assertTrue(binding["acceptance_basis_digest"].startswith("sha256:"))
        self.assertIn(canonical_occurrence_ref(child_terminal), stored.record["input_refs"])
        self.assertIn(self.gate_d1, stored.record["input_refs"])
        self.assertNotIn("barrier_consumed", stored.canonical_json)

    def test_non_blocking_child_does_not_require_acceptance_binding(self):
        parent_scope, _, _, parent_terminal, _ = self._materialize_parent_and_child(gate="NON_BLOCKING")
        successor = scoped_occurrence("so_parent_nonblocking", "lane_parent", parent_scope)
        result = self._schedule(successor, "req_parent_nonblocking", predecessor_ref=internal_ref(parent_terminal))
        self.assertEqual("APPLIED", result["status"])
        stored = self.store.read_latest("STAGE_OCCURRENCE", "so_parent_nonblocking")
        self.assertEqual([], stored.record["schedule_basis"]["required_child_acceptance_bindings"])

    def test_same_work_scope_cannot_bind_to_second_lane(self):
        scope = root_scope("ws_unique")
        self._schedule(scoped_occurrence("so_unique_a", "lane_unique_a", scope), "req_unique_a")
        with self.assertRaises(aegis_control.MutationRejected) as raised:
            self._schedule(scoped_occurrence("so_unique_b", "lane_unique_b", scope), "req_unique_b")
        self.assertEqual("WORK_SCOPE_LANE_CONFLICT", raised.exception.code)

    def test_child_spawn_failure_rolls_back_occurrence_lane_and_outbox(self):
        parent_scope = root_scope("ws_fault_parent")
        self._schedule(scoped_occurrence("so_fault_parent", "lane_fault_parent", parent_scope), "req_fault_parent")
        parent_open = self.store.read_latest("STAGE_OCCURRENCE", "so_fault_parent")
        child_ws = child_scope(
            "ws_fault_child",
            parent_scope,
            canonical_occurrence_ref(parent_open),
            self.contract_ref,
        )
        before = dict(self.store.snapshot_counts())

        def fault(name):
            if name == "after_lane":
                raise RuntimeError("synthetic child spawn crash")

        crashing = aegis_control.MutationService(self.store, trust_resolver=self.resolver, fault_injector=fault)
        child = scoped_occurrence("so_fault_child", "lane_fault_child", child_ws)
        with self.assertRaisesRegex(RuntimeError, "synthetic child spawn crash"):
            crashing.apply(
                make_request(
                    "SCHEDULE_STAGE_OCCURRENCE",
                    "req_fault_child",
                    "lane_fault_child",
                    {"occurrence": child},
                    expected_state(work_scope_ref=child_ws),
                )
            )
        self.assertEqual(before, dict(self.store.snapshot_counts()))
        self.assertIsNone(self.store.read_latest("STAGE_OCCURRENCE", "so_fault_child"))
        self.assertIsNone(self.store.read_lane_head("lane_fault_child").occurrence_ref)

    def test_historical_replay_stays_pinned_after_current_truth_changes(self):
        if not hasattr(aegis_control.ProjectionEngine, "replay_required_child_acceptance"):
            self.fail("CP-I04 historical acceptance replay is not implemented")
        parent_scope, _, _, parent_terminal, _ = self._materialize_parent_and_child()
        self.adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[self.gate_d1],
            satisfies=True,
        )
        successor = scoped_occurrence("so_parent_history", "lane_parent", parent_scope)
        self._schedule(successor, "req_parent_history", predecessor_ref=internal_ref(parent_terminal))
        replay_before = aegis_control.ProjectionEngine(self.store).replay_required_child_acceptance("so_parent_history")
        self.assertEqual(self.gate_d1, replay_before[0]["acceptance_fact_refs"][0])

        gate_d2 = exact_ref("GATE_DECISION", "gate-child-d2", "a")
        self.adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d2",
            resolved_refs=[gate_d2],
            satisfies=False,
        )
        replay_after = aegis_control.ProjectionEngine(self.store).replay_required_child_acceptance("so_parent_history")
        self.assertEqual(replay_before, replay_after)
        self.assertEqual(self.gate_d1, replay_after[0]["acceptance_fact_refs"][0])


if __name__ == "__main__":
    unittest.main()
