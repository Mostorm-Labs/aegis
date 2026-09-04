"""Deterministic CP-I02 evidence compiler; it never issues a Gate verdict."""
from __future__ import annotations

import ast
from pathlib import Path
import platform
import sqlite3
import tempfile
import threading
from typing import Any

from tests.control_plane.cp_i02_fixtures import (
    conflicting_request,
    escalation_record,
    expected_state,
    make_request,
    occurrence_record,
    package_record,
    terminal_facts,
)
from tests.control_plane.store_oracle import audit_database
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.store import ControlStore

TASK_ID = "CP-I02-P31-01"
PACKAGE_REF = "68a6eebec569b31a468743fd8cd4c1a21ac75952"
PREDECESSOR_REF = "a996edb00fbbe1f292bba6e3634118e215fe4c14"
PREDECESSOR_P34_COMMENT = "5474322167"
AUTHORITY_REFS = {
    "product": "c628bdc15fdd3d32511a04b6f09055413f2786c3",
    "modeling": "f29c4da3698038e0174e4380707fa618b03c40b2",
    "architecture": "e657f0e74771184b98f8c8e6f8a8581e4858c82d",
    "verification": "db83168e4086e47a7f431acf289006e4f25b8ffd",
}
TEST_COMMANDS = [
    "python3 -m unittest discover -s tests/control_plane -p 'test_cp_i02_*.py' -v",
    "python3 -m unittest discover -s tests/control_plane -v",
    "python3 -m unittest discover -s tests/project_state -v",
    "python3 -m unittest discover -s tests/skillset -v",
]
SCENARIO_BINDINGS = {
    "G01": {"coverage": "EXERCISED_SUBTRACE", "focus": "schedule A, terminalize A, separately schedule successor B"},
    "G02": {"coverage": "EXERCISED", "focus": "same-lane successor race from exact terminal predecessor"},
    "G03": {"coverage": "EXERCISED", "focus": "independent lanes"},
    "G09": {"coverage": "BOUND_SUBSTRATE_ONLY", "focus": "atomicity substrate"},
    "G10": {"coverage": "BOUND_SUBSTRATE_ONLY", "focus": "atomicity substrate"},
    "G11": {"coverage": "BOUND_SUBSTRATE_ONLY", "focus": "atomicity substrate"},
    "G12": {"coverage": "BOUND_SUBSTRATE_ONLY", "focus": "history substrate"},
    "G29": {"coverage": "EXERCISED", "focus": "idempotent replay"},
    "G30": {"coverage": "EXERCISED", "focus": "idempotency conflict"},
    "G34": {"coverage": "STRUCTURAL", "focus": "commit-before-dispatch boundary"},
    "G35": {"coverage": "EXERCISED", "focus": "escalation companion atomicity"},
}

ZERO_METRICS = (
    "illegal_accepted_transitions", "duplicate_canonical_head", "half_committed_transactions",
    "dispatch_before_commit", "same_lane_double_winners", "idempotency_replay_amplification",
    "conflicting_idempotency_accepted_mutations", "duplicate_terminal_revisions",
    "successor_before_terminal", "orphan_schedule_pairs", "orphan_escalation_companions",
)


def _trace(trace_id: str, expected: Any, observed: Any) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "expected": expected,
        "observed": observed,
        "status": "PASS" if expected == observed else "FAIL",
    }


def _ownership(repo_root: Path) -> dict[str, Any]:
    root = repo_root / "tools" / "aegis_control"
    tx_callers, sql_owners, imports = [], set(), set()
    for path in root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "INSERT INTO canonical_records" in text or "UPDATE lane_heads SET version" in text:
            sql_owners.add(path.name)
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "_mutation_transaction":
                tx_callers.append(path.name)
            if path.name in {"store.py", "mutation.py"}:
                if isinstance(node, ast.Import):
                    imports.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module)
    forbidden = {"requests", "httpx", "urllib.request", "socket"}
    findings = []
    if sorted(tx_callers) != ["mutation.py"]:
        findings.append("SECOND_MUTATION_TRANSACTION_CALLER")
    if sql_owners != {"store.py"}:
        findings.append("RAW_CANONICAL_SQL_OUTSIDE_STORE")
    if not forbidden.isdisjoint(imports):
        findings.append("NETWORK_PATH_IN_TRANSACTION_MODULE")
    return {
        "canonical_writers": ["control-mutation"],
        "transaction_callers": sorted(tx_callers),
        "raw_sql_owners": sorted(sql_owners),
        "network_imports": sorted(imports),
        "findings": findings,
        "passed": not findings,
    }


def _schedule(
    service: MutationService,
    request_id: str,
    lane: str,
    occurrence: str,
    expected=None,
):
    return service.apply(make_request(
        "SCHEDULE_STAGE_OCCURRENCE",
        request_id,
        lane,
        {"occurrence": occurrence_record(occurrence, lane)},
        expected,
    ))


def compile_evidence(repo_root: Path) -> dict[str, Any]:
    traces: list[dict[str, Any]] = []
    audits: dict[str, Any] = {}
    crash_rows: list[dict[str, Any]] = []
    metrics = {name: 0 for name in ZERO_METRICS}

    with tempfile.TemporaryDirectory(prefix="cp-i02-evidence-") as tmp:
        root = Path(tmp)

        # Package lineage and semantic idempotency.
        db = str(root / "package.db")
        store = ControlStore(db)
        mutation = MutationService(store)
        req = make_request(
            "MATERIALIZE_IMPLEMENTATION_PACKAGE", "req_ev_pkg_1", "lane_pkg",
            {"package": package_record("pkg_evidence")},
        )
        first = mutation.apply(req)
        before = dict(store.snapshot_counts())
        replay = mutation.apply(req)
        after = dict(store.snapshot_counts())
        traces.append(_trace(
            "G29-idempotent-replay",
            {"same_result": True, "counts_equal": True},
            {"same_result": replay == first, "counts_equal": before == after},
        ))
        if replay != first or before != after:
            metrics["idempotency_replay_amplification"] += 1

        before = dict(store.snapshot_counts())
        code = None
        try:
            mutation.apply(conflicting_request(req))
            metrics["conflicting_idempotency_accepted_mutations"] += 1
        except MutationRejected as exc:
            code = exc.code
        after = dict(store.snapshot_counts())
        traces.append(_trace(
            "G30-idempotency-conflict",
            {"code": "OPERATION_IDEMPOTENCY_CONFLICT", "counts_equal": True},
            {"code": code, "counts_equal": before == after},
        ))
        current = store.read_latest("VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "pkg_evidence")
        mutation.apply(make_request(
            "REVISE_IMPLEMENTATION_PACKAGE", "req_ev_pkg_2", "lane_pkg",
            {"package": package_record("pkg_evidence", revision=2, scope_name="cp-i02-r2")},
            expected_state(target_record_revision=1, target_record_digest=current.digest),
        ))
        audits["package_lineage"] = audit_database(db)

        # G01: schedule A, terminalize A without an implicit successor, then
        # separately schedule B from the exact terminal predecessor.
        db = str(root / "lifecycle.db")
        store = ControlStore(db)
        mutation = MutationService(store)
        _schedule(mutation, "req_ev_g01_schedule_a", "lane_g01", "so_g01_a")
        current = store.read_latest("STAGE_OCCURRENCE", "so_g01_a")
        outbox_before_terminal = len(store.read_outbox())
        terminal_result = mutation.apply(make_request(
            "TERMINATE_STAGE_OCCURRENCE", "req_ev_g01_terminal_a", "lane_g01",
            {
                "occurrence_id": "so_g01_a",
                "recorded_at": "2026-08-31T07:00:00Z",
                "terminal": terminal_facts(),
            },
            expected_state(target_record_revision=1, target_record_digest=current.digest),
        ))
        terminal_ref = terminal_result["canonical_records"][0]
        interim_audit = audit_database(db)
        terminal_observed = {
            "a_revisions": interim_audit["lineages"]["STAGE_OCCURRENCE:so_g01_a"]["revisions"],
            "occurrence_lineages": sum(k.startswith("STAGE_OCCURRENCE:") for k in interim_audit["lineages"]),
            "outbox_delta": len(store.read_outbox()) - outbox_before_terminal,
        }
        terminal_expected = {"a_revisions": [1, 2], "occurrence_lineages": 1, "outbox_delta": 0}
        traces.append(_trace("G01-terminal-boundary", terminal_expected, terminal_observed))
        if terminal_observed != terminal_expected:
            metrics["successor_before_terminal"] += 1

        successor = _schedule(
            mutation,
            "req_ev_g01_schedule_b",
            "lane_g01",
            "so_g01_b",
            expected_state(predecessor_occurrence_ref=terminal_ref),
        )
        audit = audit_database(db)
        successor_observed = {
            "predecessor_ref": terminal_ref,
            "a_revisions": audit["lineages"]["STAGE_OCCURRENCE:so_g01_a"]["revisions"],
            "b_revisions": audit["lineages"]["STAGE_OCCURRENCE:so_g01_b"]["revisions"],
            "lane_version": audit["lane_heads"]["lane_g01"]["version"],
            "lane_head": audit["lane_heads"]["lane_g01"]["occurrence_ref"],
            "successor_ref": successor["canonical_records"][0],
            "outbox": len(audit["outbox"]),
            "active_occurrences": audit["open_occurrences_by_lane"].get("lane_g01", []),
            "same_lane_double_winners": audit["metrics"]["same_lane_double_winners"],
        }
        successor_expected = {
            "predecessor_ref": terminal_ref,
            "a_revisions": [1, 2],
            "b_revisions": [1],
            "lane_version": 2,
            "lane_head": successor["canonical_records"][0],
            "successor_ref": successor["canonical_records"][0],
            "outbox": 2,
            "active_occurrences": ["so_g01_b"],
            "same_lane_double_winners": 0,
        }
        traces.append(_trace("G01-separate-successor", successor_expected, successor_observed))
        if successor_observed != successor_expected:
            metrics["illegal_accepted_transitions"] += 1
        audits["g01_lifecycle"] = audit

        # G01 negative subtrace: an OPEN r1 ref becomes stale after A is
        # terminalized and cannot authorize successor B. The rejected attempt
        # must leave no canonical/idempotency/outbox residue.
        db = str(root / "lifecycle-stale.db")
        store = ControlStore(db)
        mutation = MutationService(store)
        stale_open = _schedule(
            mutation, "req_ev_g01_stale_schedule_a", "lane_g01_stale", "so_g01_stale_a"
        )["canonical_records"][0]
        current = store.read_latest("STAGE_OCCURRENCE", "so_g01_stale_a")
        mutation.apply(make_request(
            "TERMINATE_STAGE_OCCURRENCE", "req_ev_g01_stale_terminal_a", "lane_g01_stale",
            {
                "occurrence_id": "so_g01_stale_a",
                "recorded_at": "2026-08-31T07:01:00Z",
                "terminal": terminal_facts(),
            },
            expected_state(target_record_revision=1, target_record_digest=current.digest),
        ))
        before = dict(store.snapshot_counts())
        stale_code = None
        try:
            _schedule(
                mutation,
                "req_ev_g01_stale_schedule_b",
                "lane_g01_stale",
                "so_g01_stale_b",
                expected_state(predecessor_occurrence_ref=stale_open),
            )
            metrics["illegal_accepted_transitions"] += 1
        except MutationRejected as exc:
            stale_code = exc.code
        after = dict(store.snapshot_counts())
        stale_audit = audit_database(db)
        stale_observed = {
            "code": stale_code,
            "counts_equal": before == after,
            "successor_exists": "STAGE_OCCURRENCE:so_g01_stale_b" in stale_audit["lineages"],
            "lane_version": stale_audit["lane_heads"]["lane_g01_stale"]["version"],
        }
        stale_expected = {
            "code": "CONTROL_LANE_SCHEDULE_CONFLICT",
            "counts_equal": True,
            "successor_exists": False,
            "lane_version": 1,
        }
        traces.append(_trace("G01-stale-predecessor-zero-residue", stale_expected, stale_observed))
        if stale_observed != stale_expected:
            metrics["illegal_accepted_transitions"] += 1
        audits["g01_stale_predecessor"] = stale_audit

        # G02: two writers start from the same exact TERMINAL predecessor. The
        # first successor wins the lane CAS; the loser leaves no residue.
        db = str(root / "race.db")
        store = ControlStore(db)
        mutation = MutationService(store)
        _schedule(mutation, "req_ev_race_base", "lane_race", "so_race_base")
        current = store.read_latest("STAGE_OCCURRENCE", "so_race_base")
        race_terminal = mutation.apply(make_request(
            "TERMINATE_STAGE_OCCURRENCE", "req_ev_race_base_terminal", "lane_race",
            {
                "occurrence_id": "so_race_base",
                "recorded_at": "2026-08-31T07:02:00Z",
                "terminal": terminal_facts(),
            },
            expected_state(target_record_revision=1, target_record_digest=current.digest),
        ))
        predecessor_ref = race_terminal["canonical_records"][0]
        barrier = threading.Barrier(2)
        outcomes: list[str] = []
        lock = threading.Lock()

        def writer(index: int) -> None:
            service = MutationService(ControlStore(db), before_transaction=lambda: barrier.wait())
            try:
                _schedule(
                    service,
                    f"req_ev_race_successor_{index}",
                    "lane_race",
                    f"so_race_successor_{index}",
                    expected_state(predecessor_occurrence_ref=predecessor_ref),
                )
                outcome = "APPLIED"
            except MutationRejected as exc:
                outcome = exc.code
            with lock:
                outcomes.append(outcome)

        threads = [threading.Thread(target=writer, args=(i,)) for i in (1, 2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(10)
        audit = audit_database(db)
        observed = {
            "predecessor_ref": predecessor_ref,
            "applied": outcomes.count("APPLIED"),
            "conflicts": outcomes.count("CONTROL_LANE_SCHEDULE_CONFLICT"),
            "occurrences": sum(k.startswith("STAGE_OCCURRENCE:") for k in audit["lineages"]),
            "outbox": len(audit["outbox"]),
            "idempotency": len(audit["idempotency"]),
            "lane_version": audit["lane_heads"]["lane_race"]["version"],
            "active_occurrences": len(audit["open_occurrences_by_lane"].get("lane_race", [])),
            "same_lane_double_winners": audit["metrics"]["same_lane_double_winners"],
        }
        expected = {
            "predecessor_ref": predecessor_ref,
            "applied": 1,
            "conflicts": 1,
            "occurrences": 2,
            "outbox": 2,
            "idempotency": 3,
            "lane_version": 2,
            "active_occurrences": 1,
            "same_lane_double_winners": 0,
        }
        traces.append(_trace("G02-established-predecessor-race", expected, observed))
        if observed != expected:
            metrics["same_lane_double_winners"] += 1
        audits["g02_same_lane"] = audit

        # G03: independent lanes both commit.
        db = str(root / "independent.db")
        store = ControlStore(db)
        mutation = MutationService(store)
        _schedule(mutation, "req_ev_lane_a", "lane_a", "so_a")
        _schedule(mutation, "req_ev_lane_b", "lane_b", "so_b")
        audit = audit_database(db)
        observed = {"lane_heads": len(audit["lane_heads"]), "outbox": len(audit["outbox"])}
        traces.append(_trace("G03-independent-lanes", {"lane_heads": 2, "outbox": 2}, observed))
        if observed != {"lane_heads": 2, "outbox": 2}:
            metrics["illegal_accepted_transitions"] += 1
        audits["g03_independent_lanes"] = audit

        # Schedule crash matrix + reopen durability.
        for checkpoint in ("after_canonical", "after_lane", "after_outbox", "after_idempotency"):
            db = str(root / f"crash-{checkpoint}.db")
            store = ControlStore(db)

            def inject(name: str, target: str = checkpoint):
                if name == target:
                    raise RuntimeError(target)

            try:
                _schedule(
                    MutationService(store, fault_injector=inject),
                    f"req_{checkpoint}",
                    "lane_crash",
                    "so_crash",
                )
                outcome = "UNEXPECTED_COMMIT"
            except RuntimeError:
                outcome = "ROLLED_BACK"
            audit = audit_database(db)
            counts = {
                "canonical_records": len(audit["canonical_records"]),
                "lane_heads": len(audit["lane_heads"]),
                "idempotency": len(audit["idempotency"]),
                "outbox": len(audit["outbox"]),
            }
            if outcome != "ROLLED_BACK" or any(counts.values()):
                metrics["half_committed_transactions"] += 1
            crash_rows.append({
                "transaction": "SCHEDULE_STAGE_OCCURRENCE",
                "failure_point": checkpoint,
                "expected": "ROLLBACK_ALL",
                "expected_counts": {
                    "canonical_records": 0,
                    "lane_heads": 0,
                    "idempotency": 0,
                    "outbox": 0,
                },
                "observed": outcome,
                "post_reopen_counts": counts,
            })

        db = str(root / "reopen.db")
        _schedule(MutationService(ControlStore(db)), "req_reopen", "lane_reopen", "so_reopen")
        audit = audit_database(db)
        reopen = {
            "canonical_records": len(audit["canonical_records"]),
            "lane_heads": len(audit["lane_heads"]),
            "idempotency": len(audit["idempotency"]),
            "outbox": len(audit["outbox"]),
        }
        crash_rows.append({
            "transaction": "SCHEDULE_STAGE_OCCURRENCE",
            "failure_point": "AFTER_COMMIT_REOPEN",
            "expected": "FULL_COMMITTED_SET",
            "observed": reopen,
        })
        audits["commit_reopen"] = audit

        # G35: escalation and terminal revision are atomic companions.
        db = str(root / "escalation.db")
        store = ControlStore(db)
        mutation = MutationService(store)
        _schedule(mutation, "req_esc_schedule", "lane_esc", "so_esc")
        current = store.read_latest("STAGE_OCCURRENCE", "so_esc")
        request = make_request(
            "RAISE_ESCALATION", "req_esc_raise", "lane_esc",
            {
                "occurrence_id": "so_esc",
                "recorded_at": "2026-08-31T07:10:00Z",
                "escalation": escalation_record("esc_evidence", "so_esc", "lane_esc"),
                "terminal": terminal_facts(
                    "ESCALATED",
                    "BLOCKED_UNRESOLVED_DECISION",
                    raised=["esc_evidence"],
                    earliest="P21",
                ),
            },
            expected_state(target_record_revision=1, target_record_digest=current.digest),
        )
        mutation.apply(request)
        audit = audit_database(db)
        observed = {
            "escalation_revisions": audit["lineages"]["ESCALATION:esc_evidence"]["revisions"],
            "occurrence_revisions": audit["lineages"]["STAGE_OCCURRENCE:so_esc"]["revisions"],
            "orphan_companions": audit["metrics"]["orphan_escalation_companions"],
        }
        traces.append(_trace(
            "G35-escalation-companion",
            {"escalation_revisions": [1], "occurrence_revisions": [1, 2], "orphan_companions": 0},
            observed,
        ))
        audits["g35_escalation"] = audit

        # Escalation companion rollback matrix: the pre-existing scheduled OPEN
        # occurrence remains durable, but neither the escalation nor terminal
        # companion nor raise-idempotency result may survive a failed raise.
        for checkpoint in ("after_escalation", "after_terminal", "after_idempotency"):
            db = str(root / f"escalation-crash-{checkpoint}.db")
            store = ControlStore(db)
            mutation = MutationService(store)
            _schedule(mutation, f"req_esc_base_{checkpoint}", "lane_esc_crash", "so_esc_crash")
            current = store.read_latest("STAGE_OCCURRENCE", "so_esc_crash")
            baseline = dict(store.snapshot_counts())
            request = make_request(
                "RAISE_ESCALATION", f"req_esc_crash_{checkpoint}", "lane_esc_crash",
                {
                    "occurrence_id": "so_esc_crash",
                    "recorded_at": "2026-08-31T07:11:00Z",
                    "escalation": escalation_record("esc_crash", "so_esc_crash", "lane_esc_crash"),
                    "terminal": terminal_facts(
                        "ESCALATED",
                        "BLOCKED_UNRESOLVED_DECISION",
                        raised=["esc_crash"],
                        earliest="P21",
                    ),
                },
                expected_state(target_record_revision=1, target_record_digest=current.digest),
            )

            def inject_escalation(name: str, target: str = checkpoint):
                if name == target:
                    raise RuntimeError(target)

            try:
                MutationService(store, fault_injector=inject_escalation).apply(request)
                outcome = "UNEXPECTED_COMMIT"
            except RuntimeError:
                outcome = "ROLLED_BACK"
            audit = audit_database(db)
            counts = {
                "canonical_records": len(audit["canonical_records"]),
                "lane_heads": len(audit["lane_heads"]),
                "idempotency": len(audit["idempotency"]),
                "outbox": len(audit["outbox"]),
            }
            if outcome != "ROLLED_BACK" or counts != baseline:
                metrics["half_committed_transactions"] += 1
            crash_rows.append({
                "transaction": "RAISE_ESCALATION",
                "failure_point": checkpoint,
                "expected": "ROLLBACK_TO_PREEXISTING_OPEN_BASELINE",
                "expected_counts": baseline,
                "observed": outcome,
                "post_reopen_counts": counts,
            })

        # Unsupported later-slice operation must be zero mutation. CP-I05 now
        # supports RECORD_EXECUTION_PROGRESS, so retain the CP-I02 invariant by
        # probing an operation that is still owned by the later CP-I06 slice.
        db = str(root / "unsupported.db")
        store = ControlStore(db)
        before = dict(store.snapshot_counts())
        code = None
        try:
            MutationService(store).apply(make_request(
                "SCHEDULE_REPAIR_OCCURRENCE",
                "req_unsupported",
                "lane_unsupported",
                {"checkpoint": 1},
            ))
            metrics["illegal_accepted_transitions"] += 1
        except MutationRejected as exc:
            code = exc.code
        after = dict(store.snapshot_counts())
        traces.append(_trace(
            "CP-I02-unsupported-operation",
            {"code": "UNSUPPORTED_OPERATION_IN_CP_I02", "counts_equal": True},
            {"code": code, "counts_equal": before == after},
        ))
        if before != after:
            metrics["illegal_accepted_transitions"] += 1
        audits["unsupported_operation"] = audit_database(db)

    ownership = _ownership(repo_root)
    traces.append(_trace(
        "G34-commit-before-dispatch-structure",
        {"canonical_writers": ["control-mutation"], "network": False},
        {
            "canonical_writers": ownership["canonical_writers"],
            "network": bool(set(ownership["network_imports"]) & {"requests", "httpx", "urllib.request", "socket"}),
        },
    ))
    if not ownership["passed"]:
        metrics["illegal_accepted_transitions"] += len(ownership["findings"])

    for audit in audits.values():
        for key in (
            "duplicate_canonical_head",
            "half_committed_transactions",
            "same_lane_double_winners",
            "duplicate_terminal_revisions",
            "orphan_schedule_pairs",
            "orphan_escalation_companions",
        ):
            metrics[key] += int(audit["metrics"].get(key, 0))
        if not audit["passed"]:
            metrics["illegal_accepted_transitions"] += len(audit["findings"])

    canonical_pass = all(value == 0 for value in metrics.values()) and all(
        trace["status"] == "PASS" for trace in traces
    )
    crash_pass = all(
        row["observed"] == {
            "canonical_records": 1,
            "lane_heads": 1,
            "idempotency": 1,
            "outbox": 1,
        }
        if row["failure_point"] == "AFTER_COMMIT_REOPEN"
        else row["observed"] == "ROLLED_BACK" and row["post_reopen_counts"] == row["expected_counts"]
        for row in crash_rows
    )
    return {
        "canonical_conformance": {
            "evidence_family": "CPV-E-CANONICAL-CONFORMANCE",
            "scenario_bindings": SCENARIO_BINDINGS,
            "traces": traces,
            "ownership": ownership,
            "metrics": metrics,
            "passed": canonical_pass,
        },
        "store_audit": {
            "evidence_family": "CPV-E-STORE-AUDIT",
            "oracle": "O-STORE",
            "audits": audits,
            "passed": all(audit["passed"] for audit in audits.values()),
        },
        "trace_corpus": {
            "corpus": "CP-I02 raw canonical trace corpus",
            "scenario_bindings": SCENARIO_BINDINGS,
            "traces": traces,
        },
        "crash_matrix": {
            "matrix": "CP-I02 transaction/crash matrix",
            "rows": crash_rows,
            "passed": crash_pass,
        },
        "runtime": {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version},
    }
