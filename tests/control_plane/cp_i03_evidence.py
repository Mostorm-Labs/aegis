"""Deterministic CP-I03 evidence compiler. It never issues a Gate verdict."""
from __future__ import annotations

import ast
from pathlib import Path
import platform
import sqlite3
import tempfile
import threading
from typing import Any

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tests.control_plane.reference_model import derive_projection as oracle_projection
from tools.aegis_control import (
    ControlStore,
    MutationRejected,
    MutationService,
    PolicyEvaluator,
    ProjectionCache,
    ProjectionEngine,
    Scheduler,
    SchedulingDenied,
)

TASK_ID = "CP-I03-P31-01"
PACKAGE_REF = "5be737ae11b226cde222044d31099224c23af81e"
CP_I02_ACCEPTED_REF = "f820132ab6fb9b2af7754773477fe69af513e83c"
CP_I02_P34_COMMENT = "5475361166"
AUTHORITY_REFS = {
    "product": "c628bdc15fdd3d32511a04b6f09055413f2786c3",
    "modeling": "f29c4da3698038e0174e4380707fa618b03c40b2",
    "architecture": "e657f0e74771184b98f8c8e6f8a8581e4858c82d",
    "verification": "db83168e4086e47a7f431acf289006e4f25b8ffd",
    "implementation_plan": "87cbb166411795261ec5f6e7034a89435e053451",
}
TEST_COMMANDS = [
    "python3 -m unittest discover -s tests/control_plane -p 'test_cp_i03_*.py' -v",
    "python3 -m unittest discover -s tests/control_plane -v",
    "python3 -m unittest discover -s tests/project_state -v",
    "python3 -m unittest discover -s tests/skillset -v",
]


def _stored_ref(stored) -> str:
    return (
        f"{stored.record['kind']}:{stored.record['id']}"
        f"@{stored.record['record_revision']}#{stored.digest}"
    )


def _autonomous_occurrence(occurrence_id: str, lane_id: str):
    record = occurrence_record(occurrence_id, lane_id)
    record["policy_binding"] = {"control_autonomy": "AUTONOMOUS"}
    return record


def _schedule(service: MutationService, request_id: str, lane: str, occurrence_id: str, predecessor_ref=None):
    return service.apply(make_request(
        "SCHEDULE_STAGE_OCCURRENCE",
        request_id,
        lane,
        {"occurrence": occurrence_record(occurrence_id, lane)},
        expected_state(predecessor_occurrence_ref=predecessor_ref),
    ))


def _terminate(service: MutationService, store: ControlStore, request_id: str, lane: str, occurrence_id: str):
    current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
    return service.apply(make_request(
        "TERMINATE_STAGE_OCCURRENCE",
        request_id,
        lane,
        {"occurrence_id": occurrence_id, "terminal": terminal_facts(), "recorded_at": None},
        expected_state(
            active_occurrence_ref=_stored_ref(current),
            target_record_revision=current.record["record_revision"],
            target_record_digest=current.digest,
        ),
    ))


def _completed_projection(store: ControlStore, mutation: MutationService, lane: str, occurrence_id: str):
    _schedule(mutation, f"req_{occurrence_id}", lane, occurrence_id)
    _terminate(mutation, store, f"req_{occurrence_id}_terminal", lane, occurrence_id)
    return ProjectionEngine(store).project_lane(lane)


def _ownership_rollout() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "rollout.db"))
        mutation = MutationService(store)
        projection = _completed_projection(store, mutation, "lane_rollout", "so_rollout_a")
        decision = PolicyEvaluator().evaluate_next_action(
            next_legal_action=projection.next_legal_action,
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-gate-review",
            control_autonomy="AUTONOMOUS",
            policy_basis={"current": True, "rollout_authorized": True},
        )
        before = dict(store.snapshot_counts())
        denied = False
        try:
            Scheduler(store, mutation).derive_candidate(
                projection,
                decision,
                occurrence_record("so_rollout_b", "lane_rollout"),
            )
        except SchedulingDenied as exc:
            denied = exc.code == "POLICY_DENIED_AUTO_SCHEDULE"
        after = dict(store.snapshot_counts())

        current_basis = {"current": True, "rollout_authorized": True}
        same_owner_allowed = PolicyEvaluator().evaluate_next_action(
            next_legal_action=projection.next_legal_action,
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-implementation",
            control_autonomy="AUTONOMOUS",
            policy_basis=current_basis,
        )
        binding_before = dict(store.snapshot_counts())
        binding_denied = False
        try:
            Scheduler(
                store,
                mutation,
                policy_basis_resolver=lambda candidate: dict(current_basis),
            ).derive_candidate(
                projection,
                same_owner_allowed,
                occurrence_record("so_rollout_binding_mismatch", "lane_rollout"),
            )
        except SchedulingDenied as exc:
            binding_denied = exc.code == "CANDIDATE_POLICY_BINDING_MISMATCH"
        binding_after = dict(store.snapshot_counts())

        missing_basis = PolicyEvaluator().evaluate_next_action(
            next_legal_action=projection.next_legal_action,
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-implementation",
            control_autonomy="AUTONOMOUS",
            policy_basis=None,
        )
        metrics = {
            "unauthorized_auto_schedules": 0 if denied and before == after else 1,
            "unofficial_gate_decisions_accepted": 0 if not decision.gate_decision and not missing_basis.gate_decision else 1,
            "pinned_policy_mismatch_commits": 0 if binding_denied and binding_before == binding_after else 1,
        }
        return {
            "evidence_family": "CPV-E-OWNERSHIP-ROLLOUT",
            "current_cross_primary_rollout": decision.mode,
            "reason_codes": list(decision.reason_codes),
            "missing_policy_basis_mode": missing_basis.mode,
            "pinned_policy_mismatch_denied": binding_denied,
            "canonical_counts_before_denied_candidate": before,
            "canonical_counts_after_denied_candidate": after,
            "metrics": metrics,
            "passed": decision.mode == "PROHIBITED" and all(value == 0 for value in metrics.values()),
        }


def _derived_state() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "derived.db"))
        mutation = MutationService(store)
        projection = _completed_projection(store, mutation, "lane_derived", "so_derived_a")
        terminal = store.read_latest("STAGE_OCCURRENCE", "so_derived_a")
        oracle = oracle_projection([terminal.record])

        cache = ProjectionCache()
        engine = ProjectionEngine(store, cache=cache)
        counts_before_cache = dict(store.snapshot_counts())
        cached_first = engine.project_lane("lane_derived")
        cached_second = engine.project_lane("lane_derived")
        cache.clear()
        rebuilt = engine.project_lane("lane_derived")
        counts_after_cache = dict(store.snapshot_counts())

        allowed_basis = {"current": True, "rollout_authorized": True}
        allowed = PolicyEvaluator().evaluate_next_action(
            next_legal_action=projection.next_legal_action,
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-implementation",
            control_autonomy="AUTONOMOUS",
            policy_basis=allowed_basis,
        )
        scheduler = Scheduler(
            store,
            mutation,
            policy_basis_resolver=lambda candidate: dict(allowed_basis),
        )
        stale_candidate = scheduler.derive_candidate(
            projection,
            allowed,
            _autonomous_occurrence("so_derived_stale", "lane_derived"),
        )
        predecessor = store.read_latest("STAGE_OCCURRENCE", "so_derived_a")
        _schedule(mutation, "req_derived_winner", "lane_derived", "so_derived_winner", _stored_ref(predecessor))
        counts_before_stale = dict(store.snapshot_counts())
        stale_rejected = False
        try:
            scheduler.submit_candidate(stale_candidate)
        except MutationRejected as exc:
            stale_rejected = exc.code == "STALE_SCHEDULER_CANDIDATE"
        counts_after_stale = dict(store.snapshot_counts())

        policy_projection = _completed_projection(store, mutation, "lane_policy_stale", "so_policy_stale_a")
        current_policy_basis = {"current": True, "rollout_authorized": True, "revision": "v1"}
        policy_allowed = PolicyEvaluator().evaluate_next_action(
            next_legal_action=policy_projection.next_legal_action,
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-implementation",
            control_autonomy="AUTONOMOUS",
            policy_basis=current_policy_basis,
        )
        policy_scheduler = Scheduler(
            store,
            mutation,
            policy_basis_resolver=lambda candidate: dict(current_policy_basis),
        )
        policy_candidate = policy_scheduler.derive_candidate(
            policy_projection,
            policy_allowed,
            _autonomous_occurrence("so_policy_stale_b", "lane_policy_stale"),
        )
        counts_before_policy_stale = dict(store.snapshot_counts())
        current_policy_basis["revision"] = "v2"
        stale_policy_rejected = False
        try:
            policy_scheduler.submit_candidate(policy_candidate)
        except MutationRejected as exc:
            stale_policy_rejected = exc.code == "STALE_POLICY_AUTHORIZATION"
        counts_after_policy_stale = dict(store.snapshot_counts())

        counts_before_ops = dict(store.snapshot_counts())
        scheduler.pause("lane_derived")
        scheduler.acquire_lease_hint("lane_derived", "worker-1")
        scheduler.release_lease_hint("lane_derived", "worker-1")
        scheduler.resume("lane_derived")
        counts_after_ops = dict(store.snapshot_counts())

        oracle_match = (
            projection.control_cursor.active_occurrence_id == oracle["active_occurrence_id"]
            and projection.control_cursor.last_terminal_occurrence_id == oracle["last_terminal_occurrence_id"]
        )
        cache_match = cached_first == cached_second == rebuilt
        metrics = {
            "stale_projection_authorization": 0 if stale_rejected and counts_before_stale == counts_after_stale else 1,
            "stale_policy_authorization": 0
            if stale_policy_rejected and counts_before_policy_stale == counts_after_policy_stale else 1,
            "cache_pause_lease_only_canonical_mutations": 0
            if counts_before_cache == counts_after_cache and counts_before_ops == counts_after_ops else 1,
        }
        return {
            "evidence_family": "CPV-E-DERIVED-STATE",
            "oracle": "O-CRM independent expected semantic state",
            "projection_oracle_match": oracle_match,
            "cache_rebuild_match": cache_match,
            "stale_candidate_rejected": stale_rejected,
            "stale_policy_rejected": stale_policy_rejected,
            "metrics": metrics,
            "passed": oracle_match and cache_match and all(value == 0 for value in metrics.values()),
        }


def _writer_ownership(repo_root: Path) -> dict[str, Any]:
    root = repo_root / "tools" / "aegis_control"
    tx_callers: list[str] = []
    raw_sql_owners: set[str] = set()
    for path in root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "INSERT INTO canonical_records" in text or "UPDATE lane_heads SET version" in text:
            raw_sql_owners.add(path.name)
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "_mutation_transaction":
                tx_callers.append(path.name)
    findings = []
    if sorted(tx_callers) != ["mutation.py"]:
        findings.append("SECOND_MUTATION_TRANSACTION_CALLER")
    if raw_sql_owners != {"store.py"}:
        findings.append("RAW_CANONICAL_SQL_OUTSIDE_STORE")
    return {
        "transaction_callers": sorted(tx_callers),
        "raw_canonical_sql_owners": sorted(raw_sql_owners),
        "findings": findings,
        "passed": not findings,
    }


def _scheduler_cas_race() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "race.db")
        store = ControlStore(db)
        mutation = MutationService(store)
        projection = _completed_projection(store, mutation, "lane_race", "so_race_a")
        current_basis = {"current": True, "rollout_authorized": True}
        allowed = PolicyEvaluator().evaluate_next_action(
            next_legal_action=projection.next_legal_action,
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-implementation",
            control_autonomy="AUTONOMOUS",
            policy_basis=current_basis,
        )
        planner = Scheduler(
            store,
            mutation,
            policy_basis_resolver=lambda candidate: dict(current_basis),
        )
        candidates = [
            planner.derive_candidate(projection, allowed, _autonomous_occurrence(occurrence_id, "lane_race"))
            for occurrence_id in ("so_race_b", "so_race_c")
        ]
        barrier = threading.Barrier(2)
        lock = threading.Lock()
        outcomes: list[str] = []

        def submit(candidate) -> None:
            local_store = ControlStore(db)
            local_scheduler = Scheduler(
                local_store,
                MutationService(local_store, before_transaction=lambda: barrier.wait()),
                policy_basis_resolver=lambda current_candidate: dict(current_basis),
            )
            try:
                local_scheduler.submit_candidate(candidate)
                result = "APPLIED"
            except MutationRejected as exc:
                result = exc.code
            with lock:
                outcomes.append(result)

        threads = [threading.Thread(target=submit, args=(candidate,)) for candidate in candidates]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        if any(thread.is_alive() for thread in threads):
            raise RuntimeError("scheduler CAS evidence race did not terminate")

        winner_count = outcomes.count("APPLIED")
        loser_count = len(outcomes) - winner_count
        successors = [
            store.read_latest("STAGE_OCCURRENCE", occurrence_id)
            for occurrence_id in ("so_race_b", "so_race_c")
        ]
        successor_count = sum(record is not None for record in successors)
        expected_loser = loser_count == 1 and all(
            outcome in {"APPLIED", "CONTROL_LANE_SCHEDULE_CONFLICT"} for outcome in outcomes
        )
        return {
            "outcomes": sorted(outcomes),
            "winner_count": winner_count,
            "loser_count": loser_count,
            "canonical_successor_count": successor_count,
            "lane_version": store.read_lane_head("lane_race").version,
            "outbox_count_including_predecessor": len(store.read_outbox()),
            "passed": winner_count == 1 and expected_loser and successor_count == 1,
        }


def _canonical_conformance(repo_root: Path) -> dict[str, Any]:
    ownership = _writer_ownership(repo_root)
    race = _scheduler_cas_race()
    metrics = {
        "same_lane_double_winners": 0 if race["winner_count"] == 1 and race["canonical_successor_count"] == 1 else 1,
        "scheduler_direct_canonical_writes": 0 if ownership["passed"] else 1,
    }
    return {
        "evidence_family": "CPV-E-CANONICAL-CONFORMANCE",
        "extension": "CP-I03 scheduler / CP-I02 CAS integration",
        "accepted_cp_i02_anchor": CP_I02_ACCEPTED_REF,
        "single_writer": ownership,
        "scheduler_cas_race": race,
        "metrics": metrics,
        "passed": ownership["passed"] and race["passed"] and all(value == 0 for value in metrics.values()),
    }


def compile_evidence(repo_root: Path) -> dict[str, Any]:
    ownership = _ownership_rollout()
    derived = _derived_state()
    canonical = _canonical_conformance(repo_root)
    return {
        "runtime": {
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
        },
        "ownership_rollout": ownership,
        "derived_state": derived,
        "canonical_conformance": canonical,
        "zero_tolerance_metrics": {
            "unauthorized_auto_schedules": ownership["metrics"]["unauthorized_auto_schedules"],
            "unofficial_gate_decisions_accepted": ownership["metrics"]["unofficial_gate_decisions_accepted"],
            "pinned_policy_mismatch_commits": ownership["metrics"]["pinned_policy_mismatch_commits"],
            "stale_projection_authorization": derived["metrics"]["stale_projection_authorization"],
            "stale_policy_authorization": derived["metrics"]["stale_policy_authorization"],
            "cache_pause_lease_only_canonical_mutations": derived["metrics"]["cache_pause_lease_only_canonical_mutations"],
        },
    }
