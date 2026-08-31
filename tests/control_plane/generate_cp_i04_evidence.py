"""Deterministic CP-I04 evidence compiler. It never issues a Gate verdict."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.control_plane.cp_i02_fixtures import (
    expected_state,
    make_request,
    package_record,
    terminal_facts,
)
from tests.control_plane.cp_i03_evidence import (
    AUTHORITY_REFS,
    CP_I02_ACCEPTED_REF,
    CP_I02_P34_COMMENT,
    compile_evidence as compile_cp_i03_evidence,
)
from tests.control_plane.test_cp_i04_required_child_barrier import (
    canonical_occurrence_ref,
    child_scope,
    exact_ref,
    internal_ref,
    root_scope,
    scoped_occurrence,
)
from tools import aegis_control


TASK_ID = "CP-I04-P31-01"
PACKAGE_REF = "28e89118b68b3cf3eab1cf94ab65a20271e32c80"
TASK_ANCHOR = "f6820374d29772dfe1069f3502b6e4f80795fd80"
CP_I03_P34_COMMENT = "5480775507"
PR_NUMBER = 34
NOW = datetime(2026, 8, 31, 16, 12, tzinfo=timezone.utc)
TEST_COMMANDS = [
    "python3 -m unittest discover -s tests/control_plane -p 'test_cp_i04_*.py' -v",
    "python3 -m unittest discover -s tests/control_plane -v",
    "python3 -m unittest discover -s tests/project_state -v",
    "python3 -m unittest discover -s tests/skillset -v",
]
TEST_IDENTITIES = [
    "test_cp_i04_snapshot_trust.CpI04SnapshotTrustTests",
    "test_cp_i04_child_acceptance.CpI04ChildAcceptanceResolverTests",
    "test_cp_i04_required_child_barrier.CpI04RequiredChildBarrierTests",
    "test_cp_i04_barrier_matrix.CpI04BarrierMatrixTests",
    "test_cp_i04_work_scope.CpI04WorkScopeContractTests",
    "test_cp_i04_evidence.CpI04EvidenceTests",
]
QUALIFICATION_IDENTITIES = {
    "G36": "SourceSnapshotToken integrity and exact binding",
    "G37": "provider-version/currentness revalidation before commit",
    "G38": "trust ambiguity/conflict fail-closed zero-residue",
    "G39": "async provider durable query/correlation capability",
    "M16": "snapshot payload tamper with original integrity tag",
    "M17": "wrong adapter/source-kind snapshot binding",
    "M18": "wrong resource/provider-version snapshot binding",
    "M19": "callback-only provider falsely treated as full autonomous",
}


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot(store: aegis_control.ControlStore) -> tuple[dict, int]:
    return dict(store.snapshot_counts()), len(store.read_outbox())


def _adapter(
    *,
    adapter_id: str,
    source_kind: str = "PROJECT_STATE",
    query_correlation: bool = True,
    clock=None,
):
    return aegis_control.DeterministicExternalAdapter(
        source_kind=source_kind,
        adapter_id=adapter_id,
        secret=b"cp-i04-evidence-secret",
        callback_available=True,
        query_correlation_available=query_correlation,
        clock=clock or (lambda: NOW),
    )


def _resolver(adapter, contract_ref: dict, resource_key: str):
    return aegis_control.TrustResolver(
        {"PROJECT_STATE": adapter},
        acceptance_contract_sources={
            contract_ref["id"]: aegis_control.TrustFactRequest("PROJECT_STATE", resource_key)
        },
    )


def _schedule(service, record: dict, request_id: str, *, predecessor_ref=None, package_ref=None):
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


def _terminate(service, store, occurrence_id: str, lane_id: str, scope: dict):
    current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
    service.apply(
        make_request(
            "TERMINATE_STAGE_OCCURRENCE",
            f"req_term_{occurrence_id}",
            lane_id,
            {
                "occurrence_id": occurrence_id,
                "terminal": terminal_facts(),
                "recorded_at": None,
            },
            expected_state(
                work_scope_ref=scope,
                active_occurrence_ref=internal_ref(current),
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
            ),
        )
    )
    return store.read_latest("STAGE_OCCURRENCE", occurrence_id)


def _materialize_parent_child(
    store,
    service,
    contract_ref: dict,
    *,
    prefix: str,
):
    parent_scope = root_scope(f"ws_{prefix}_parent")
    parent_id = f"so_{prefix}_parent"
    parent_lane = f"lane_{prefix}_parent"
    _schedule(service, scoped_occurrence(parent_id, parent_lane, parent_scope), f"req_{prefix}_parent")
    parent_open = store.read_latest("STAGE_OCCURRENCE", parent_id)
    child_ws = child_scope(
        f"ws_{prefix}_child",
        parent_scope,
        canonical_occurrence_ref(parent_open),
        contract_ref,
    )
    child_id = f"so_{prefix}_child"
    child_lane = f"lane_{prefix}_child"
    _schedule(service, scoped_occurrence(child_id, child_lane, child_ws), f"req_{prefix}_child")
    child_terminal = _terminate(service, store, child_id, child_lane, child_ws)
    parent_terminal = _terminate(service, store, parent_id, parent_lane, parent_scope)
    return {
        "parent_scope": parent_scope,
        "parent_open": parent_open,
        "parent_terminal": parent_terminal,
        "parent_lane": parent_lane,
        "child_scope": child_ws,
        "child_terminal": child_terminal,
    }


def _snapshot_integrity() -> dict:
    adapter = _adapter(adapter_id="project-state-snapshot")
    gate_v1 = exact_ref("GATE_DECISION", "gate-snapshot-v1", "1")
    adapter.set_resource(
        "gate/main",
        version_scheme="git-commit+blob",
        version_value="v1",
        resolved_refs=[gate_v1],
        satisfies=True,
    )
    snapshot = adapter.resolve("gate/main")
    valid = adapter.verify_snapshot(snapshot.snapshot_token, expected_resource_key="gate/main")

    prefix, payload, tag = snapshot.snapshot_token.split(".")
    payload_replacement = "A" if payload[-1] != "A" else "B"
    tampered_payload_token = f"{prefix}.{payload[:-1]}{payload_replacement}.{tag}"
    tampered_payload = adapter.verify_snapshot(
        tampered_payload_token,
        expected_resource_key="gate/main",
    )

    tag_replacement = "A" if tag[-1] != "A" else "B"
    tampered_tag = adapter.verify_snapshot(
        f"{prefix}.{payload}.{tag[:-1]}{tag_replacement}",
        expected_resource_key="gate/main",
    )

    wrong_adapter = _adapter(adapter_id="project-state-snapshot-wrong")
    wrong_adapter.set_resource(
        "gate/main",
        version_scheme="git-commit+blob",
        version_value="v1",
        resolved_refs=[gate_v1],
        satisfies=True,
    )
    wrong_adapter_result = wrong_adapter.verify_snapshot(
        snapshot.snapshot_token,
        expected_resource_key="gate/main",
    )

    wrong_source_adapter = _adapter(
        adapter_id="project-state-snapshot",
        source_kind="PROOF_PLANE",
    )
    wrong_source_adapter.set_resource(
        "gate/main",
        version_scheme="git-commit+blob",
        version_value="v1",
        resolved_refs=[gate_v1],
        satisfies=True,
    )
    wrong_source = wrong_source_adapter.verify_snapshot(
        snapshot.snapshot_token,
        expected_resource_key="gate/main",
    )

    adapter.set_resource(
        "gate/other",
        version_scheme="git-commit+blob",
        version_value="v1",
        resolved_refs=[exact_ref("GATE_DECISION", "gate-other", "2")],
        satisfies=True,
    )
    wrong_resource = adapter.verify_snapshot(
        snapshot.snapshot_token,
        expected_resource_key="gate/other",
    )

    adapter.set_resource(
        "gate/main",
        version_scheme="git-commit+blob",
        version_value="v2",
        resolved_refs=[exact_ref("GATE_DECISION", "gate-snapshot-v2", "3")],
        satisfies=True,
    )
    wrong_version = adapter.verify_snapshot(
        snapshot.snapshot_token,
        expected_resource_key="gate/main",
    )

    observed = [NOW]
    expiring = _adapter(adapter_id="project-state-expiring", clock=lambda: observed[0])
    expiring.set_resource(
        "gate/expiring",
        version_scheme="gate-version",
        version_value="e1",
        resolved_refs=[exact_ref("GATE_DECISION", "gate-expiring", "4")],
        satisfies=True,
    )
    expiring_snapshot = expiring.resolve("gate/expiring")
    observed[0] = NOW + timedelta(seconds=11)
    expired = expiring.verify_snapshot(
        expiring_snapshot.snapshot_token,
        expected_resource_key="gate/expiring",
    )

    metrics = {
        "tampered_snapshot_accepted": 0
        if not tampered_payload.valid and not tampered_tag.valid
        else 1,
        "cross_adapter_or_source_snapshot_accepted": 0
        if not wrong_adapter_result.valid and not wrong_source.valid
        else 1,
        "cross_resource_or_version_snapshot_accepted": 0
        if not wrong_resource.valid and not wrong_version.valid
        else 1,
    }
    passed = (
        valid.valid
        and not expired.valid
        and all(value == 0 for value in metrics.values())
    )
    return {
        "evidence_family": "CPV-E-SNAPSHOT-INTEGRITY",
        "oracle": "O-SNAPSHOT independent token/binding checker",
        "valid_snapshot": {"accepted": valid.valid, "code": valid.code},
        "tampered_payload": {"accepted": tampered_payload.valid, "code": tampered_payload.code},
        "tampered_tag": {"accepted": tampered_tag.valid, "code": tampered_tag.code},
        "wrong_adapter": {"accepted": wrong_adapter_result.valid, "code": wrong_adapter_result.code},
        "wrong_source": {"accepted": wrong_source.valid, "code": wrong_source.code},
        "wrong_resource": {"accepted": wrong_resource.valid, "code": wrong_resource.code},
        "wrong_version": {"accepted": wrong_version.valid, "code": wrong_version.code},
        "expired": {"accepted": expired.valid, "code": expired.code},
        "metrics": metrics,
        "passed": passed,
    }


def _async_provider_capability() -> dict:
    callback_only = _adapter(
        adapter_id="project-state-callback-only",
        query_correlation=False,
    )
    queryable = _adapter(
        adapter_id="project-state-queryable",
        query_correlation=True,
    )
    metric = 0 if not callback_only.capability.full_autonomous_trust_capable else 1
    return {
        "evidence_family": "CPV-E-ASYNC-PROVIDER-CAPABILITY",
        "oracle": "O-PROVIDER + O-CONTRACT",
        "callback_only": {
            "callback_available": callback_only.capability.callback_available,
            "query_correlation_available": callback_only.capability.query_correlation_available,
            "full_autonomous_trust_capable": callback_only.capability.full_autonomous_trust_capable,
        },
        "queryable": {
            "callback_available": queryable.capability.callback_available,
            "query_correlation_available": queryable.capability.query_correlation_available,
            "full_autonomous_trust_capable": queryable.capability.full_autonomous_trust_capable,
        },
        "metrics": {"callback_only_provider_fully_autonomous": metric},
        "passed": metric == 0 and queryable.capability.full_autonomous_trust_capable,
    }


def _trust_currentness() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        store = aegis_control.ControlStore(str(Path(tmp) / "trust-currentness.db"))
        adapter = _adapter(adapter_id="project-state-currentness")
        contract = exact_ref("CONTRACT", "contract-currentness", "5")
        gate_d1 = exact_ref("GATE_DECISION", "gate-currentness-d1", "6")
        gate_d2 = exact_ref("GATE_DECISION", "gate-currentness-d2", "7")
        adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[gate_d1],
            satisfies=True,
        )
        resolver = _resolver(adapter, contract, "child/acceptance")
        base_service = aegis_control.MutationService(store, trust_resolver=resolver)
        materialized = _materialize_parent_child(
            store,
            base_service,
            contract,
            prefix="currentness",
        )
        successor = scoped_occurrence(
            "so_currentness_successor",
            materialized["parent_lane"],
            materialized["parent_scope"],
        )

        def drift(name):
            if name == "after_child_acceptance_resolution":
                adapter.set_resource(
                    "child/acceptance",
                    version_scheme="gate-decision",
                    version_value="d2",
                    resolved_refs=[gate_d2],
                    satisfies=True,
                )

        stale_service = aegis_control.MutationService(
            store,
            trust_resolver=resolver,
            fault_injector=drift,
        )
        before_stale = _snapshot(store)
        stale_code = None
        try:
            _schedule(
                stale_service,
                successor,
                "req_currentness_stale",
                predecessor_ref=internal_ref(materialized["parent_terminal"]),
            )
        except aegis_control.MutationRejected as exc:
            stale_code = exc.code
        after_stale = _snapshot(store)
        stale_zero = (
            before_stale == after_stale
            and store.read_latest("STAGE_OCCURRENCE", successor["id"]) is None
        )

        adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d2",
            resolved_refs=[gate_d2],
            satisfies=True,
            ambiguous=True,
        )
        before_ambiguous = _snapshot(store)
        ambiguous_code = None
        try:
            _schedule(
                base_service,
                successor,
                "req_currentness_ambiguous",
                predecessor_ref=internal_ref(materialized["parent_terminal"]),
            )
        except aegis_control.MutationRejected as exc:
            ambiguous_code = exc.code
        after_ambiguous = _snapshot(store)
        ambiguous_zero = before_ambiguous == after_ambiguous

        adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d2",
            resolved_refs=[gate_d2],
            satisfies=True,
            ambiguous=False,
            conflict=True,
        )
        before_conflict = _snapshot(store)
        conflict_code = None
        try:
            _schedule(
                base_service,
                successor,
                "req_currentness_conflict",
                predecessor_ref=internal_ref(materialized["parent_terminal"]),
            )
        except aegis_control.MutationRejected as exc:
            conflict_code = exc.code
        after_conflict = _snapshot(store)
        conflict_zero = before_conflict == after_conflict

        metrics = {
            "stale_success_commits": 0 if stale_zero and stale_code is not None else 1,
            "ambiguous_trust_success": 0
            if ambiguous_zero
            and conflict_zero
            and ambiguous_code == "CHILD_ACCEPTANCE_BASIS_AMBIGUOUS"
            and conflict_code == "CHILD_ACCEPTANCE_BASIS_CONFLICT"
            else 1,
        }
        return {
            "evidence_family": "CPV-E-TRUST-CURRENTNESS",
            "oracle": "O-AUTH + O-PROVIDER commit-bound freshness/ambiguity checker",
            "stale_between_resolve_and_commit": {
                "rejection_code": stale_code,
                "zero_residue": stale_zero,
            },
            "ambiguous_trust": {
                "rejection_code": ambiguous_code,
                "zero_residue": ambiguous_zero,
            },
            "conflicting_trust": {
                "rejection_code": conflict_code,
                "zero_residue": conflict_zero,
            },
            "metrics": metrics,
            "passed": all(value == 0 for value in metrics.values()),
        }


def _historical_replay() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        store = aegis_control.ControlStore(str(Path(tmp) / "historical.db"))
        adapter = _adapter(adapter_id="project-state-history")
        contract = exact_ref("CONTRACT", "contract-history", "8")
        gate_d1 = exact_ref("GATE_DECISION", "gate-history-d1", "9")
        gate_d2 = exact_ref("GATE_DECISION", "gate-history-d2", "a")
        adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[gate_d1],
            satisfies=True,
        )
        resolver = _resolver(adapter, contract, "child/acceptance")
        service = aegis_control.MutationService(store, trust_resolver=resolver)
        materialized = _materialize_parent_child(
            store,
            service,
            contract,
            prefix="history",
        )
        successor = scoped_occurrence(
            "so_history_successor",
            materialized["parent_lane"],
            materialized["parent_scope"],
        )
        _schedule(
            service,
            successor,
            "req_history_successor",
            predecessor_ref=internal_ref(materialized["parent_terminal"]),
        )
        engine = aegis_control.ProjectionEngine(store)
        replay_before = engine.replay_required_child_acceptance(successor["id"])
        pinned_before = replay_before[0]["acceptance_fact_refs"][0]

        adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d2",
            resolved_refs=[gate_d2],
            satisfies=False,
        )
        replay_after = engine.replay_required_child_acceptance(successor["id"])
        pinned_after = replay_after[0]["acceptance_fact_refs"][0]
        current_after = adapter.resolve("child/acceptance").resolved_refs[0]
        mismatch = 0 if replay_before == replay_after and pinned_after != current_after else 1
        return {
            "evidence_family": "CPV-E-HISTORICAL-REPLAY",
            "oracle": "O-CRM + O-AUTH exact ref/digest replay checker",
            "successor_occurrence_id": successor["id"],
            "pinned_fact_before": pinned_before,
            "pinned_fact_after": pinned_after,
            "current_fact_after": current_after,
            "historical_tuple_before": replay_before,
            "historical_tuple_after": replay_after,
            "current_provider_satisfies_after": False,
            "metrics": {"historical_replay_mismatch": mismatch},
            "passed": mismatch == 0,
        }


def _canonical_conformance(repo_root: Path) -> dict:
    predecessor = compile_cp_i03_evidence(repo_root)["canonical_conformance"]

    with tempfile.TemporaryDirectory() as tmp:
        store = aegis_control.ControlStore(str(Path(tmp) / "canonical.db"))
        adapter = _adapter(adapter_id="project-state-canonical")
        contract = exact_ref("CONTRACT", "contract-canonical", "b")
        gate = exact_ref("GATE_DECISION", "gate-canonical", "c")
        adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[gate],
            satisfies=False,
        )
        resolver = _resolver(adapter, contract, "child/acceptance")
        service = aegis_control.MutationService(store, trust_resolver=resolver)

        parent_scope = root_scope("ws_atomic_parent")
        _schedule(
            service,
            scoped_occurrence("so_atomic_parent", "lane_atomic_parent", parent_scope),
            "req_atomic_parent",
        )
        parent_open = store.read_latest("STAGE_OCCURRENCE", "so_atomic_parent")
        child_ws = child_scope(
            "ws_atomic_child",
            parent_scope,
            canonical_occurrence_ref(parent_open),
            contract,
        )
        child_occurrence = scoped_occurrence("so_atomic_child", "lane_atomic_child", child_ws)
        before_spawn = _snapshot(store)

        def child_crash(name):
            if name == "after_lane":
                raise RuntimeError("synthetic child spawn crash")

        crashing_spawn = aegis_control.MutationService(
            store,
            trust_resolver=resolver,
            fault_injector=child_crash,
        )
        spawn_failed = False
        try:
            _schedule(crashing_spawn, child_occurrence, "req_atomic_child_crash")
        except RuntimeError as exc:
            spawn_failed = str(exc) == "synthetic child spawn crash"
        after_spawn = _snapshot(store)
        child_spawn_zero = (
            spawn_failed
            and before_spawn == after_spawn
            and store.read_latest("STAGE_OCCURRENCE", child_occurrence["id"]) is None
            and store.read_lane_head("lane_atomic_child").occurrence_ref is None
        )

        _schedule(service, child_occurrence, "req_atomic_child")
        child_terminal = _terminate(service, store, "so_atomic_child", "lane_atomic_child", child_ws)
        parent_terminal = _terminate(service, store, "so_atomic_parent", "lane_atomic_parent", parent_scope)
        successor = scoped_occurrence("so_atomic_successor", "lane_atomic_parent", parent_scope)

        before_denial = _snapshot(store)
        denial_code = None
        try:
            _schedule(
                service,
                successor,
                "req_atomic_denied",
                predecessor_ref=internal_ref(parent_terminal),
            )
        except aegis_control.MutationRejected as exc:
            denial_code = exc.code
        after_denial = _snapshot(store)
        denial_zero = (
            before_denial == after_denial
            and denial_code == "REQUIRED_CHILD_WORK_NOT_ACCEPTED"
            and store.read_latest("STAGE_OCCURRENCE", successor["id"]) is None
        )

        adapter.set_resource(
            "child/acceptance",
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[gate],
            satisfies=True,
        )
        before_cross = _snapshot(store)

        def barrier_crash(name):
            if name == "after_canonical":
                raise RuntimeError("synthetic barrier crossing crash")

        crashing_barrier = aegis_control.MutationService(
            store,
            trust_resolver=resolver,
            fault_injector=barrier_crash,
        )
        barrier_failed = False
        try:
            _schedule(
                crashing_barrier,
                successor,
                "req_atomic_barrier_crash",
                predecessor_ref=internal_ref(parent_terminal),
            )
        except RuntimeError as exc:
            barrier_failed = str(exc) == "synthetic barrier crossing crash"
        after_cross = _snapshot(store)
        barrier_zero = (
            barrier_failed
            and before_cross == after_cross
            and store.read_latest("STAGE_OCCURRENCE", successor["id"]) is None
        )

        accepted, _ = _schedule(
            service,
            successor,
            "req_atomic_successor",
            predecessor_ref=internal_ref(parent_terminal),
        )
        stored_successor = store.read_latest("STAGE_OCCURRENCE", successor["id"])
        bindings = stored_successor.record["schedule_basis"]["required_child_acceptance_bindings"]
        exact_binding = (
            accepted["status"] == "APPLIED"
            and len(bindings) == 1
            and bindings[0]["child_work_scope_ref"] == child_ws
            and canonical_occurrence_ref(child_terminal) in stored_successor.record["input_refs"]
            and gate in stored_successor.record["input_refs"]
            and "barrier_consumed" not in stored_successor.canonical_json
        )

        conflict_scope = root_scope("ws_lane_conflict")
        _schedule(
            service,
            scoped_occurrence("so_lane_conflict_a", "lane_conflict_a", conflict_scope),
            "req_lane_conflict_a",
        )
        before_lane_conflict = _snapshot(store)
        lane_conflict_code = None
        try:
            _schedule(
                service,
                scoped_occurrence("so_lane_conflict_b", "lane_conflict_b", conflict_scope),
                "req_lane_conflict_b",
            )
        except aegis_control.MutationRejected as exc:
            lane_conflict_code = exc.code
        lane_conflict_zero = before_lane_conflict == _snapshot(store)

        package = package_record("pkg_scope_bound", "lane_pkg_scope")
        service.apply(
            make_request(
                "MATERIALIZE_IMPLEMENTATION_PACKAGE",
                "req_pkg_scope_bound_evidence",
                "lane_pkg_scope",
                {"package": package},
            )
        )
        stored_package = store.read_latest(
            "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE",
            "pkg_scope_bound",
        )
        mismatched = scoped_occurrence(
            "so_pkg_scope_mismatch_evidence",
            "lane_other_scope",
            root_scope("ws_other_scope_evidence"),
        )
        before_package_mismatch = _snapshot(store)
        package_mismatch_code = None
        try:
            _schedule(
                service,
                mismatched,
                "req_pkg_scope_mismatch_evidence",
                package_ref=internal_ref(stored_package),
            )
        except aegis_control.MutationRejected as exc:
            package_mismatch_code = exc.code
        package_mismatch_zero = before_package_mismatch == _snapshot(store)

        second_writer = 0 if predecessor["single_writer"]["passed"] else 1
        metrics = {
            "unbound_required_successor": 0 if exact_binding else 1,
            "required_child_barrier_bypass": 0 if denial_zero else 1,
            "child_spawn_half_commit": 0 if child_spawn_zero else 1,
            "barrier_cross_half_commit": 0 if barrier_zero else 1,
            "second_canonical_writer": second_writer,
        }
        return {
            "evidence_family": "CPV-E-CANONICAL-CONFORMANCE",
            "extension": "CP-I04 WorkScope child spawn / REQUIRED barrier atomicity",
            "accepted_cp_i02_anchor": CP_I02_ACCEPTED_REF,
            "accepted_cp_i03_anchor": TASK_ANCHOR,
            "single_writer": predecessor["single_writer"],
            "scheduler_cas_race": predecessor["scheduler_cas_race"],
            "child_spawn_atomicity": {
                "fault_checkpoint": "after_lane",
                "zero_residue": child_spawn_zero,
            },
            "required_child_denial": {
                "rejection_code": denial_code,
                "zero_residue": denial_zero,
            },
            "barrier_cross_atomicity": {
                "fault_checkpoint": "after_canonical",
                "zero_residue": barrier_zero,
            },
            "accepted_successor_binding": {
                "binding_count": len(bindings),
                "exact_binding": exact_binding,
            },
            "work_scope_lane_conflict": {
                "rejection_code": lane_conflict_code,
                "zero_residue": lane_conflict_zero,
            },
            "package_work_scope_mismatch": {
                "rejection_code": package_mismatch_code,
                "zero_residue": package_mismatch_zero,
            },
            "metrics": metrics,
            "passed": (
                predecessor["single_writer"]["passed"]
                and predecessor["scheduler_cas_race"]["passed"]
                and lane_conflict_code == "WORK_SCOPE_LANE_CONFLICT"
                and lane_conflict_zero
                and package_mismatch_code == "PACKAGE_WORK_SCOPE_MISMATCH"
                and package_mismatch_zero
                and all(value == 0 for value in metrics.values())
            ),
        }


def generate(output_dir: Path, result_revision: str, package_ref: str = PACKAGE_REF) -> dict:
    repo_root = Path(__file__).resolve().parents[2]
    predecessor = compile_cp_i03_evidence(repo_root)
    families = {
        "CPV-E-TRUST-CURRENTNESS": _trust_currentness(),
        "CPV-E-HISTORICAL-REPLAY": _historical_replay(),
        "CPV-E-SNAPSHOT-INTEGRITY": _snapshot_integrity(),
        "CPV-E-ASYNC-PROVIDER-CAPABILITY": _async_provider_capability(),
        "CPV-E-CANONICAL-CONFORMANCE": _canonical_conformance(repo_root),
    }
    for family_id, family in families.items():
        if not family["passed"]:
            raise RuntimeError(f"CP-I04 evidence family failed: {family_id}")

    metrics = {
        "stale_success_commits": families["CPV-E-TRUST-CURRENTNESS"]["metrics"]["stale_success_commits"],
        "historical_replay_mismatch": families["CPV-E-HISTORICAL-REPLAY"]["metrics"]["historical_replay_mismatch"],
        "unbound_required_successor": families["CPV-E-CANONICAL-CONFORMANCE"]["metrics"]["unbound_required_successor"],
        "required_child_barrier_bypass": families["CPV-E-CANONICAL-CONFORMANCE"]["metrics"]["required_child_barrier_bypass"],
        "child_spawn_half_commit": families["CPV-E-CANONICAL-CONFORMANCE"]["metrics"]["child_spawn_half_commit"],
        "barrier_cross_half_commit": families["CPV-E-CANONICAL-CONFORMANCE"]["metrics"]["barrier_cross_half_commit"],
        "tampered_snapshot_accepted": families["CPV-E-SNAPSHOT-INTEGRITY"]["metrics"]["tampered_snapshot_accepted"],
        "cross_adapter_or_source_snapshot_accepted": families["CPV-E-SNAPSHOT-INTEGRITY"]["metrics"]["cross_adapter_or_source_snapshot_accepted"],
        "cross_resource_or_version_snapshot_accepted": families["CPV-E-SNAPSHOT-INTEGRITY"]["metrics"]["cross_resource_or_version_snapshot_accepted"],
        "ambiguous_trust_success": families["CPV-E-TRUST-CURRENTNESS"]["metrics"]["ambiguous_trust_success"],
        "callback_only_provider_fully_autonomous": families["CPV-E-ASYNC-PROVIDER-CAPABILITY"]["metrics"]["callback_only_provider_fully_autonomous"],
        "second_canonical_writer": families["CPV-E-CANONICAL-CONFORMANCE"]["metrics"]["second_canonical_writer"],
    }
    if any(metrics.values()):
        raise RuntimeError("CP-I04 zero-tolerance metric failure")

    paths = {
        "CPV-E-TRUST-CURRENTNESS": output_dir / "trust-currentness.json",
        "CPV-E-HISTORICAL-REPLAY": output_dir / "historical-replay.json",
        "CPV-E-SNAPSHOT-INTEGRITY": output_dir / "snapshot-integrity.json",
        "CPV-E-ASYNC-PROVIDER-CAPABILITY": output_dir / "async-provider-capability.json",
        "CPV-E-CANONICAL-CONFORMANCE": output_dir / "canonical-conformance.json",
    }
    for family_id, path in paths.items():
        _write_json(path, families[family_id])

    file_digests = {path.name: _sha256(path) for path in paths.values()}
    payload_digest = "sha256:" + hashlib.sha256(
        "\n".join(f"{name}={digest}" for name, digest in sorted(file_digests.items())).encode("utf-8")
    ).hexdigest()
    artifact_name = f"cp-i04-evidence-{result_revision}"
    manifest = {
        "evidence_bundle": "CP-I04",
        "task_id": TASK_ID,
        "package_ref": package_ref,
        "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
        "result_revision": result_revision,
        "pr": PR_NUMBER,
        "accepted_cp_i03": {
            "revision": TASK_ANCHOR,
            "p34_comment": CP_I03_P34_COMMENT,
            "disposition": "PASS / ACCEPTED_FOR_DOWNSTREAM",
        },
        "accepted_cp_i02": {
            "revision": CP_I02_ACCEPTED_REF,
            "p34_comment": CP_I02_P34_COMMENT,
            "disposition": "PASS / ACCEPTED_FOR_DOWNSTREAM",
        },
        "authority_refs": AUTHORITY_REFS,
        "runtime": predecessor["runtime"],
        "test_commands": TEST_COMMANDS,
        "test_identities": TEST_IDENTITIES,
        "oracle_identities": {
            "O-CRM": "independent canonical semantic/reference model",
            "O-STORE": "direct durable store / reopen / count oracle",
            "O-PROVIDER": "deterministic external provider capability/currentness oracle",
            "O-SNAPSHOT": "independent snapshot integrity and binding checker",
            "O-AUTH": "exact external Authority/Gate/Proof acceptance-ref checker",
            "O-CONTRACT": "platform/provider capability contract checker",
        },
        "qualification_identities": QUALIFICATION_IDENTITIES,
        "fake_adapters": [
            {
                "implementation": "DeterministicExternalAdapter",
                "source_kind": "PROJECT_STATE",
                "clock": "injected deterministic UTC clock",
                "integrity": "adapter-owned deterministic snapshot tag",
                "currentness": "exact resource version + freshness verification",
            }
        ],
        "evidence": {family_id: path.name for family_id, path in paths.items()},
        "metrics": metrics,
        "file_digests": file_digests,
        "artifact": {
            "name": artifact_name,
            "payload_digest": payload_digest,
            "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
            "workflow_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "workflow_job": os.environ.get("GITHUB_JOB"),
            "github_artifact_id": None,
            "github_artifact_digest": None,
            "binding_note": "GitHub assigns artifact id/digest after upload; durable P32 return binds those values externally without self-digest recursion.",
        },
        "claims": {
            "cp_i04_bounded_conformance": True,
            "current_cross_primary_rollout": "DENIED",
            "p34_gate_pass": False,
            "CP_I05_plus": False,
            "provider_dispatch": False,
            "reconciliation_loop": False,
            "real_production_credentials": False,
        },
        "gate_authority": "Evidence compiler has no authority to issue P34 PASS or ACCEPTED_FOR_DOWNSTREAM",
    }
    _write_json(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--package-ref", default=PACKAGE_REF)
    parser.add_argument("--output-dir", default="artifacts/cp-i04")
    args = parser.parse_args()
    generate(Path(args.output_dir), args.result_revision, args.package_ref)


if __name__ == "__main__":
    main()
