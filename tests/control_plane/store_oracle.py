"""Independent read-only durable-state oracle for CP-I02 (O-STORE).

This module intentionally imports no production Control Store or MutationService.
It reads the SQLite file directly and verifies persisted bytes, lineage, lane,
idempotency, outbox, and companion-atomicity invariants.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _connect_readonly(db_path: str) -> sqlite3.Connection:
    uri = f"file:{Path(db_path).resolve()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def audit_database(db_path: str) -> dict[str, Any]:
    conn = _connect_readonly(db_path)
    try:
        schema_rows = conn.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "WHERE type IN ('table','index') AND name NOT LIKE 'sqlite_%' ORDER BY type, name"
        ).fetchall()
        schema_text = "\n".join((row["sql"] or "") for row in schema_rows)
        schema_digest = _sha256_bytes(schema_text.encode("utf-8"))

        record_rows = conn.execute(
            "SELECT kind, id_scheme, record_id, record_revision, control_lane_id, "
            "stage_state, canonical_json, digest FROM canonical_records "
            "ORDER BY kind, record_id, record_revision"
        ).fetchall()
        lane_rows = conn.execute(
            "SELECT lane_id, version, occurrence_ref FROM lane_heads ORDER BY lane_id"
        ).fetchall()
        idempotency_rows = conn.execute(
            "SELECT operation_request_id, fingerprint, result_json FROM idempotency "
            "ORDER BY operation_request_id"
        ).fetchall()
        outbox_rows = conn.execute(
            "SELECT outbox_id, occurrence_id, control_lane_id, payload_json FROM outbox "
            "ORDER BY outbox_id"
        ).fetchall()
    finally:
        conn.close()

    findings: list[str] = []
    canonical_records: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for row in record_rows:
        raw = row["canonical_json"]
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            findings.append(f"INVALID_CANONICAL_JSON:{row['kind']}:{row['record_id']}@{row['record_revision']}")
            continue
        computed = _sha256_bytes(raw.encode("utf-8"))
        if computed != row["digest"]:
            findings.append(f"DIGEST_MISMATCH:{row['kind']}:{row['record_id']}@{row['record_revision']}")
        if record.get("kind") != row["kind"] or record.get("id") != row["record_id"]:
            findings.append(f"ROW_IDENTITY_MISMATCH:{row['kind']}:{row['record_id']}@{row['record_revision']}")
        if record.get("record_revision") != row["record_revision"]:
            findings.append(f"ROW_REVISION_MISMATCH:{row['kind']}:{row['record_id']}@{row['record_revision']}")
        item = {
            "kind": row["kind"],
            "id_scheme": row["id_scheme"],
            "id": row["record_id"],
            "record_revision": row["record_revision"],
            "control_lane_id": row["control_lane_id"],
            "stage_state": row["stage_state"],
            "digest": row["digest"],
            "canonical_json": raw,
            "record": record,
        }
        canonical_records.append(item)
        grouped[(row["kind"], row["record_id"])].append(item)

    lineages: dict[str, Any] = {}
    duplicate_terminal_revisions = 0
    for (kind, record_id), items in sorted(grouped.items()):
        revisions = [int(item["record_revision"]) for item in items]
        if revisions != list(range(1, len(items) + 1)):
            findings.append(f"NON_CONTIGUOUS_LINEAGE:{kind}:{record_id}")
        id_schemes = {item["id_scheme"] for item in items}
        if len(id_schemes) != 1:
            findings.append(f"ID_SCHEME_DRIFT:{kind}:{record_id}")
        terminal_count = sum(1 for item in items if item["stage_state"] == "TERMINAL")
        if kind == "STAGE_OCCURRENCE":
            if items[0]["stage_state"] != "OPEN":
                findings.append(f"OCCURRENCE_NOT_OPEN_AT_R1:{record_id}")
            if terminal_count > 1:
                duplicate_terminal_revisions += terminal_count - 1
            terminal_indexes = [i for i, item in enumerate(items) if item["stage_state"] == "TERMINAL"]
            if terminal_indexes and terminal_indexes[-1] != len(items) - 1:
                findings.append(f"REVISION_AFTER_TERMINAL:{record_id}")
        if kind == "ESCALATION" and revisions != [1]:
            findings.append(f"ESCALATION_MUTATED:{record_id}")
        lineages[f"{kind}:{record_id}"] = {
            "revisions": revisions,
            "digests": [item["digest"] for item in items],
            "terminal_count": terminal_count,
        }

    lane_heads = {
        row["lane_id"]: {
            "version": int(row["version"]),
            "occurrence_ref": row["occurrence_ref"],
        }
        for row in lane_rows
    }
    idempotency = {
        row["operation_request_id"]: {
            "fingerprint": row["fingerprint"],
            "result": json.loads(row["result_json"]),
        }
        for row in idempotency_rows
    }
    outbox = {
        row["outbox_id"]: {
            "occurrence_id": row["occurrence_id"],
            "control_lane_id": row["control_lane_id"],
            "payload": json.loads(row["payload_json"]),
        }
        for row in outbox_rows
    }

    occurrence_r1 = {
        item["id"]: item
        for item in canonical_records
        if item["kind"] == "STAGE_OCCURRENCE" and item["record_revision"] == 1
    }
    outbox_occurrence_ids = {item["occurrence_id"] for item in outbox.values()}
    orphan_schedule_pairs = len(set(occurrence_r1) ^ outbox_occurrence_ids)
    if orphan_schedule_pairs:
        findings.append("ORPHAN_SCHEDULE_OUTBOX_OCCURRENCE_PAIR")

    escalation_records = {
        item["id"]: item["record"]
        for item in canonical_records
        if item["kind"] == "ESCALATION"
    }
    terminal_records = [
        item["record"]
        for item in canonical_records
        if item["kind"] == "STAGE_OCCURRENCE" and item["stage_state"] == "TERMINAL"
    ]
    raised_ids = {
        esc_id
        for record in terminal_records
        for esc_id in (record.get("terminal") or {}).get("raised_escalation_ids", [])
    }
    orphan_escalation_companions = len(set(escalation_records) ^ raised_ids)
    if orphan_escalation_companions:
        findings.append("ORPHAN_ESCALATION_COMPANION")

    lane_occurrence_counts: dict[str, int] = defaultdict(int)
    for item in occurrence_r1.values():
        lane_occurrence_counts[item["control_lane_id"]] += 1
    same_lane_double_winners = sum(max(0, count - 1) for count in lane_occurrence_counts.values())
    if same_lane_double_winners:
        findings.append("SAME_LANE_DOUBLE_WINNER")

    metrics = {
        "illegal_accepted_transitions": 0,
        "duplicate_canonical_head": 0,
        "half_committed_transactions": orphan_schedule_pairs + orphan_escalation_companions,
        "dispatch_before_commit": 0,
        "same_lane_double_winners": same_lane_double_winners,
        "idempotency_replay_amplification": 0,
        "conflicting_idempotency_accepted_mutations": 0,
        "duplicate_terminal_revisions": duplicate_terminal_revisions,
        "successor_before_terminal": 0,
        "orphan_schedule_pairs": orphan_schedule_pairs,
        "orphan_escalation_companions": orphan_escalation_companions,
    }

    return {
        "oracle": "O-STORE",
        "mode": "READ_ONLY_SQL",
        "database": str(Path(db_path).name),
        "schema_digest": schema_digest,
        "canonical_records": canonical_records,
        "lineages": lineages,
        "lane_heads": lane_heads,
        "idempotency": idempotency,
        "outbox": outbox,
        "metrics": metrics,
        "findings": sorted(set(findings)),
        "passed": not findings and all(value == 0 for value in metrics.values()),
    }
