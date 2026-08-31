from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, terminal_facts
from tests.control_plane.test_cp_i04_required_child_barrier import (
    canonical_occurrence_ref,
    child_scope,
    exact_ref,
    internal_ref,
    root_scope,
    scoped_occurrence,
)
from tools import aegis_control


NOW = datetime(2026, 8, 31, 19, 5, tzinfo=timezone.utc)
SECRET = b"cp-i04-p36-matrix"
RESOURCE = "child/acceptance"


class ReplaySnapshotAdapter(aegis_control.DeterministicExternalAdapter):
    def __init__(self, *, source_kind="PROJECT_STATE", adapter_id="p36-provider", clock=None):
        super().__init__(
            source_kind=source_kind,
            adapter_id=adapter_id,
            secret=SECRET,
            callback_available=True,
            query_correlation_available=True,
            clock=clock or (lambda: NOW),
        )
        self.forced_snapshot = None

    def resolve(self, resource_key: str):
        if self.forced_snapshot is not None:
            return self.forced_snapshot
        return super().resolve(resource_key)


class CpI04P36MandatoryMatrixTests(unittest.TestCase):
    def _schedule(self, service, record, request_id, *, predecessor_ref=None):
        request = make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            request_id,
            record["control_lane_id"],
            {"occurrence": record},
            expected_state(
                work_scope_ref=record["work_scope_ref"],
                predecessor_occurrence_ref=predecessor_ref,
            ),
        )
        return service.apply(request), request

    def _terminate(self, service, store, occurrence_id, lane_id, scope):
        current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
        service.apply(
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
        return store.read_latest("STAGE_OCCURRENCE", occurrence_id)

    def _resolver(self, adapter, contract):
        return aegis_control.TrustResolver(
            {"PROJECT_STATE": adapter},
            acceptance_contract_sources={
                aegis_control.canonical_digest(contract): aegis_control.TrustFactRequest(
                    "PROJECT_STATE", RESOURCE
                )
            },
        )

    def _materialize_barrier(self, store, service, contract, prefix):
        parent_scope = root_scope(f"ws_{prefix}_parent")
        parent_id = f"so_{prefix}_parent"
        parent_lane = f"lane_{prefix}_parent"
        self._schedule(
            service,
            scoped_occurrence(parent_id, parent_lane, parent_scope),
            f"req_{prefix}_parent",
        )
        parent_open = store.read_latest("STAGE_OCCURRENCE", parent_id)
        child_ws = child_scope(
            f"ws_{prefix}_child",
            parent_scope,
            canonical_occurrence_ref(parent_open),
            contract,
        )
        child_id = f"so_{prefix}_child"
        child_lane = f"lane_{prefix}_child"
        self._schedule(
            service,
            scoped_occurrence(child_id, child_lane, child_ws),
            f"req_{prefix}_child",
        )
        child_terminal = self._terminate(service, store, child_id, child_lane, child_ws)
        parent_terminal = self._terminate(service, store, parent_id, parent_lane, parent_scope)
        return parent_scope, parent_open, parent_terminal, child_ws, child_terminal

    def test_child_spawn_rolls_back_every_actual_precommit_checkpoint(self):
        checkpoints = ("after_canonical", "after_lane", "after_outbox", "after_idempotency")
        for index, checkpoint in enumerate(checkpoints):
            with self.subTest(checkpoint=checkpoint), tempfile.TemporaryDirectory() as tmp:
                store = aegis_control.ControlStore(str(Path(tmp) / "control.db"))
                service = aegis_control.MutationService(store)
                contract = exact_ref("CONTRACT", f"contract-spawn-{index}", "1")
                parent_scope = root_scope(f"ws_spawn_parent_{index}")
                parent_id = f"so_spawn_parent_{index}"
                parent_lane = f"lane_spawn_parent_{index}"
                self._schedule(
                    service,
                    scoped_occurrence(parent_id, parent_lane, parent_scope),
                    f"req_spawn_parent_{index}",
                )
                parent_open = store.read_latest("STAGE_OCCURRENCE", parent_id)
                child_ws = child_scope(
                    f"ws_spawn_child_{index}",
                    parent_scope,
                    canonical_occurrence_ref(parent_open),
                    contract,
                )
                child_id = f"so_spawn_child_{index}"
                child_lane = f"lane_spawn_child_{index}"
                child = scoped_occurrence(child_id, child_lane, child_ws)
                request_id = f"req_spawn_fault_{index}"
                before = dict(store.snapshot_counts())

                def fault(name, expected=checkpoint):
                    if name == expected:
                        raise RuntimeError(f"synthetic {expected}")

                crashing = aegis_control.MutationService(store, fault_injector=fault)
                with self.assertRaisesRegex(RuntimeError, checkpoint):
                    self._schedule(crashing, child, request_id)

                self.assertEqual(before, dict(store.snapshot_counts()))
                self.assertIsNone(store.read_latest("STAGE_OCCURRENCE", child_id))
                self.assertIsNone(store.read_lane_head(child_lane).occurrence_ref)
                self.assertIsNone(store.read_idempotency(request_id))

    def test_historical_replay_d1_does_not_authorize_new_future_d2_continuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = aegis_control.ControlStore(str(Path(tmp) / "control.db"))
            adapter = ReplaySnapshotAdapter()
            contract = exact_ref("CONTRACT", "contract-history-future", "2")
            gate_d1 = exact_ref("GATE_DECISION", "gate-history-d1", "3")
            gate_d2 = exact_ref("GATE_DECISION", "gate-history-d2", "4")
            adapter.set_resource(
                RESOURCE,
                version_scheme="gate-decision",
                version_value="d1",
                resolved_refs=[gate_d1],
                satisfies=True,
            )
            resolver = self._resolver(adapter, contract)
            service = aegis_control.MutationService(store, trust_resolver=resolver)
            parent_scope, _, parent_terminal, _, _ = self._materialize_barrier(
                store, service, contract, "history_future"
            )

            successor = scoped_occurrence("so_history_s", "lane_history_future_parent", parent_scope)
            self._schedule(
                service,
                successor,
                "req_history_s",
                predecessor_ref=internal_ref(parent_terminal),
            )
            successor_open = store.read_latest("STAGE_OCCURRENCE", successor["id"])
            replay_before = aegis_control.ProjectionEngine(store).replay_required_child_acceptance(successor["id"])
            self.assertEqual(gate_d1, replay_before[0]["acceptance_fact_refs"][0])

            adapter.set_resource(
                RESOURCE,
                version_scheme="gate-decision",
                version_value="d2",
                resolved_refs=[gate_d2],
                satisfies=False,
            )
            replay_after = aegis_control.ProjectionEngine(store).replay_required_child_acceptance(successor["id"])
            self.assertEqual(replay_before, replay_after)

            future_child = child_scope(
                "ws_history_future_child_2",
                parent_scope,
                canonical_occurrence_ref(successor_open),
                contract,
            )
            self._schedule(
                service,
                scoped_occurrence("so_history_future_child_2", "lane_history_future_child_2", future_child),
                "req_history_future_child_2",
            )
            self._terminate(
                service,
                store,
                "so_history_future_child_2",
                "lane_history_future_child_2",
                future_child,
            )
            successor_terminal = self._terminate(
                service,
                store,
                successor["id"],
                successor["control_lane_id"],
                parent_scope,
            )
            future = scoped_occurrence("so_history_t", successor["control_lane_id"], parent_scope)
            before = dict(store.snapshot_counts())
            with self.assertRaises(aegis_control.MutationRejected):
                self._schedule(
                    service,
                    future,
                    "req_history_t",
                    predecessor_ref=internal_ref(successor_terminal),
                )
            self.assertEqual(before, dict(store.snapshot_counts()))
            self.assertIsNone(store.read_latest("STAGE_OCCURRENCE", future["id"]))

    def test_missing_exact_acceptance_fact_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = aegis_control.ControlStore(str(Path(tmp) / "control.db"))
            adapter = ReplaySnapshotAdapter()
            contract = exact_ref("CONTRACT", "contract-missing-fact", "5")
            adapter.set_resource(
                RESOURCE,
                version_scheme="gate-decision",
                version_value="d1",
                resolved_refs=[],
                satisfies=True,
            )
            resolver = self._resolver(adapter, contract)
            support = resolver.resolve_child_acceptance(
                root_scope("ws_missing_fact"),
                exact_ref("STAGE_OCCURRENCE", "so_missing_fact", "6"),
                [contract],
            )
            self.assertFalse(support.accepted)
            self.assertEqual((), support.acceptance_fact_refs)

            service = aegis_control.MutationService(store, trust_resolver=resolver)
            parent_scope, _, parent_terminal, _, _ = self._materialize_barrier(
                store, service, contract, "missing_fact"
            )
            successor = scoped_occurrence(
                "so_missing_fact_successor", "lane_missing_fact_parent", parent_scope
            )
            before = dict(store.snapshot_counts())
            with self.assertRaises(aegis_control.MutationRejected):
                self._schedule(
                    service,
                    successor,
                    "req_missing_fact_successor",
                    predecessor_ref=internal_ref(parent_terminal),
                )
            self.assertEqual(before, dict(store.snapshot_counts()))
            self.assertIsNone(store.read_latest("STAGE_OCCURRENCE", successor["id"]))

    def test_mutable_unpinned_acceptance_fact_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = aegis_control.ControlStore(str(Path(tmp) / "control.db"))
            adapter = ReplaySnapshotAdapter()
            contract = exact_ref("CONTRACT", "contract-mutable-fact", "7")
            mutable_fact = exact_ref("GATE_DECISION", "gate-mutable", "8")
            mutable_fact["identity"] = {"scheme": "git-ref", "value": "refs/heads/main"}
            adapter.set_resource(
                RESOURCE,
                version_scheme="gate-decision",
                version_value="d1",
                resolved_refs=[mutable_fact],
                satisfies=True,
            )
            resolver = self._resolver(adapter, contract)
            support = resolver.resolve_child_acceptance(
                root_scope("ws_mutable_fact"),
                exact_ref("STAGE_OCCURRENCE", "so_mutable_fact", "9"),
                [contract],
            )
            self.assertFalse(support.accepted)

            service = aegis_control.MutationService(store, trust_resolver=resolver)
            parent_scope, _, parent_terminal, _, _ = self._materialize_barrier(
                store, service, contract, "mutable_fact"
            )
            successor = scoped_occurrence(
                "so_mutable_fact_successor", "lane_mutable_fact_parent", parent_scope
            )
            before = dict(store.snapshot_counts())
            with self.assertRaises(aegis_control.MutationRejected):
                self._schedule(
                    service,
                    successor,
                    "req_mutable_fact_successor",
                    predecessor_ref=internal_ref(parent_terminal),
                )
            self.assertEqual(before, dict(store.snapshot_counts()))
            self.assertIsNone(store.read_latest("STAGE_OCCURRENCE", successor["id"]))

    def test_acceptance_contract_exact_identity_not_just_id_is_required(self):
        for index, fact_type in enumerate(("GATE_DECISION", "PROOF_EVALUATION", "RESULT")):
            with self.subTest(fact_type=fact_type):
                adapter = ReplaySnapshotAdapter(adapter_id=f"p36-provider-{index}")
                configured_contract = exact_ref("CONTRACT", f"contract-exact-identity-{index}", "a")
                altered_contract = exact_ref("CONTRACT", f"contract-exact-identity-{index}", "b")
                fact = exact_ref(fact_type, f"fact-exact-identity-{index}", "c")
                adapter.set_resource(
                    RESOURCE,
                    version_scheme="acceptance-fact",
                    version_value=f"d{index}",
                    resolved_refs=[fact],
                    satisfies=True,
                )
                resolver = self._resolver(adapter, configured_contract)
                wrong = resolver.resolve_child_acceptance(
                    root_scope(f"ws_wrong_contract_identity_{index}"),
                    exact_ref("STAGE_OCCURRENCE", f"so_wrong_contract_identity_{index}", "d"),
                    [altered_contract],
                )
                self.assertFalse(wrong.accepted)

                exact = resolver.resolve_child_acceptance(
                    root_scope(f"ws_exact_contract_identity_{index}"),
                    exact_ref("STAGE_OCCURRENCE", f"so_exact_contract_identity_{index}", "e"),
                    [configured_contract],
                )
                self.assertTrue(exact.accepted)
                self.assertEqual((fact,), exact.acceptance_fact_refs)

    def test_duplicate_and_contradictory_exact_facts_fail_closed(self):
        duplicate_adapter = ReplaySnapshotAdapter()
        duplicate_contract = exact_ref("CONTRACT", "contract-duplicate", "e")
        fact = exact_ref("GATE_DECISION", "gate-duplicate", "f")
        duplicate_adapter.set_resource(
            RESOURCE,
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[fact, fact],
            satisfies=True,
        )
        duplicate_support = self._resolver(duplicate_adapter, duplicate_contract).resolve_child_acceptance(
            root_scope("ws_duplicate_fact"),
            exact_ref("STAGE_OCCURRENCE", "so_duplicate_fact", "1"),
            [duplicate_contract],
        )
        self.assertFalse(duplicate_support.accepted)

        adapter = ReplaySnapshotAdapter()
        contract_a = exact_ref("CONTRACT", "contract-contradict-a", "2")
        contract_b = exact_ref("CONTRACT", "contract-contradict-b", "3")
        same_fact = exact_ref("GATE_DECISION", "gate-contradict", "4")
        adapter.set_resource(
            "acceptance/a",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[same_fact],
            satisfies=True,
        )
        adapter.set_resource(
            "acceptance/b",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[same_fact],
            satisfies=True,
            conflict=True,
        )
        resolver = aegis_control.TrustResolver(
            {"PROJECT_STATE": adapter},
            acceptance_contract_sources={
                aegis_control.canonical_digest(contract_a): aegis_control.TrustFactRequest(
                    "PROJECT_STATE", "acceptance/a"
                ),
                aegis_control.canonical_digest(contract_b): aegis_control.TrustFactRequest(
                    "PROJECT_STATE", "acceptance/b"
                ),
            },
        )
        support = resolver.resolve_child_acceptance(
            root_scope("ws_contradict_fact"),
            exact_ref("STAGE_OCCURRENCE", "so_contradict_fact", "5"),
            [contract_a, contract_b],
        )
        self.assertFalse(support.accepted)

    def test_snapshot_negative_matrix_is_commit_bound_and_zero_residue(self):
        cases = (
            "payload_tamper",
            "tag_tamper",
            "wrong_adapter",
            "wrong_source",
            "wrong_resource",
            "scheme_drift",
            "value_drift",
            "expired",
        )
        for index, case in enumerate(cases):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                observed = [NOW]
                adapter = ReplaySnapshotAdapter(clock=lambda: observed[0])
                contract = exact_ref("CONTRACT", f"contract-negative-{index}", "6")
                gate = exact_ref("GATE_DECISION", f"gate-negative-{index}", "7")
                adapter.set_resource(
                    RESOURCE,
                    version_scheme="gate-decision",
                    version_value="d1",
                    resolved_refs=[gate],
                    satisfies=True,
                )
                captured = adapter.resolve(RESOURCE)
                store = aegis_control.ControlStore(str(Path(tmp) / "control.db"))
                resolver = self._resolver(adapter, contract)
                service = aegis_control.MutationService(store, trust_resolver=resolver)
                parent_scope, _, parent_terminal, _, _ = self._materialize_barrier(
                    store, service, contract, f"negative_{index}"
                )

                if case == "payload_tamper":
                    prefix, payload, tag = captured.snapshot_token.split(".")
                    replacement = "A" if payload[-1] != "A" else "B"
                    adapter.forced_snapshot = replace(
                        captured,
                        snapshot_token=f"{prefix}.{payload[:-1]}{replacement}.{tag}",
                    )
                elif case == "tag_tamper":
                    replacement = "A" if captured.snapshot_token[-1] != "A" else "B"
                    adapter.forced_snapshot = replace(
                        captured,
                        snapshot_token=captured.snapshot_token[:-1] + replacement,
                    )
                elif case == "wrong_adapter":
                    foreign = ReplaySnapshotAdapter(adapter_id="p36-provider-other")
                    foreign.set_resource(
                        RESOURCE,
                        version_scheme="gate-decision",
                        version_value="d1",
                        resolved_refs=[gate],
                        satisfies=True,
                    )
                    adapter.forced_snapshot = foreign.resolve(RESOURCE)
                elif case == "wrong_source":
                    foreign = ReplaySnapshotAdapter(source_kind="PROOF_PLANE")
                    foreign.set_resource(
                        RESOURCE,
                        version_scheme="gate-decision",
                        version_value="d1",
                        resolved_refs=[gate],
                        satisfies=True,
                    )
                    adapter.forced_snapshot = foreign.resolve(RESOURCE)
                elif case == "wrong_resource":
                    adapter.set_resource(
                        "child/other",
                        version_scheme="gate-decision",
                        version_value="d1",
                        resolved_refs=[gate],
                        satisfies=True,
                    )
                    adapter.forced_snapshot = super(ReplaySnapshotAdapter, adapter).resolve("child/other")
                elif case == "scheme_drift":
                    adapter.set_resource(
                        RESOURCE,
                        version_scheme="gate-decision-v2",
                        version_value="d1",
                        resolved_refs=[gate],
                        satisfies=True,
                    )
                    adapter.forced_snapshot = captured
                elif case == "value_drift":
                    adapter.set_resource(
                        RESOURCE,
                        version_scheme="gate-decision",
                        version_value="d2",
                        resolved_refs=[gate],
                        satisfies=True,
                    )
                    adapter.forced_snapshot = captured
                elif case == "expired":
                    observed[0] = NOW + timedelta(seconds=11)
                    adapter.forced_snapshot = captured

                successor = scoped_occurrence(
                    f"so_negative_successor_{index}",
                    f"lane_negative_{index}_parent",
                    parent_scope,
                )
                before = dict(store.snapshot_counts())
                request_id = f"req_negative_successor_{index}"
                with self.assertRaises(aegis_control.MutationRejected):
                    self._schedule(
                        service,
                        successor,
                        request_id,
                        predecessor_ref=internal_ref(parent_terminal),
                    )
                self.assertEqual(before, dict(store.snapshot_counts()))
                self.assertIsNone(store.read_latest("STAGE_OCCURRENCE", successor["id"]))
                self.assertIsNone(store.read_idempotency(request_id))


if __name__ == "__main__":
    unittest.main()
