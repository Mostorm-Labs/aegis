"""Durable SQLite persistence mechanics for Control Plane CP-I02.

This module owns storage, transaction, CAS, idempotency, and outbox mechanics.
It intentionally owns no lifecycle, Authority, Gate, proof, or policy decisions.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator, Mapping

from .canonical import canonical_digest, canonical_dumps, validate_record


class StoreConflict(RuntimeError):
    pass


@dataclass(frozen=True)
class StoredRecord:
    record: Mapping[str, Any]
    digest: str
    canonical_json: str


@dataclass(frozen=True)
class LaneHead:
    lane_id: str
    version: int
    occurrence_ref: str | None


_SCHEMA = """
CREATE TABLE IF NOT EXISTS canonical_records (
    kind TEXT NOT NULL,
    id_scheme TEXT NOT NULL,
    record_id TEXT NOT NULL,
    record_revision INTEGER NOT NULL,
    control_lane_id TEXT,
    stage_state TEXT,
    canonical_json TEXT NOT NULL,
    digest TEXT NOT NULL,
    PRIMARY KEY (kind, record_id, record_revision)
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_stage_occurrence_terminal
ON canonical_records(record_id)
WHERE kind = 'STAGE_OCCURRENCE' AND stage_state = 'TERMINAL';
CREATE TABLE IF NOT EXISTS lane_heads (
    lane_id TEXT PRIMARY KEY,
    version INTEGER NOT NULL,
    occurrence_ref TEXT
);
CREATE TABLE IF NOT EXISTS idempotency (
    operation_request_id TEXT PRIMARY KEY,
    fingerprint TEXT NOT NULL,
    result_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox (
    outbox_id TEXT PRIMARY KEY,
    occurrence_id TEXT NOT NULL,
    control_lane_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    UNIQUE(occurrence_id)
);
"""


class ControlStore:
    """Public read surface plus private mutation transaction factory."""

    def __init__(self, db_path: str, *, timeout: float = 10.0):
        self.db_path = str(Path(db_path))
        self.timeout = timeout
        self._initialize()

    def _connect(self, *, readonly: bool = False) -> sqlite3.Connection:
        if readonly:
            uri = f"file:{Path(self.db_path).resolve()}?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=self.timeout, isolation_level=None)
        else:
            conn = sqlite3.connect(self.db_path, timeout=self.timeout, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    def _initialize(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.executescript(_SCHEMA)
        finally:
            conn.close()

    @contextmanager
    def _mutation_transaction(self) -> Iterator["_MutationTransaction"]:
        conn = self._connect()
        tx = _MutationTransaction(conn)
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield tx
            conn.execute("COMMIT")
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def read_latest(self, kind: str, record_id: str) -> StoredRecord | None:
        conn = self._connect(readonly=True)
        try:
            row = conn.execute(
                "SELECT canonical_json, digest FROM canonical_records "
                "WHERE kind = ? AND record_id = ? ORDER BY record_revision DESC LIMIT 1",
                (kind, record_id),
            ).fetchone()
            return _stored(row) if row else None
        finally:
            conn.close()

    def read_revisions(self, kind: str, record_id: str) -> list[StoredRecord]:
        conn = self._connect(readonly=True)
        try:
            rows = conn.execute(
                "SELECT canonical_json, digest FROM canonical_records "
                "WHERE kind = ? AND record_id = ? ORDER BY record_revision",
                (kind, record_id),
            ).fetchall()
            return [_stored(row) for row in rows]
        finally:
            conn.close()

    def read_lane_head(self, lane_id: str) -> LaneHead:
        conn = self._connect(readonly=True)
        try:
            row = conn.execute(
                "SELECT version, occurrence_ref FROM lane_heads WHERE lane_id = ?",
                (lane_id,),
            ).fetchone()
            if not row:
                return LaneHead(lane_id, 0, None)
            return LaneHead(lane_id, int(row["version"]), row["occurrence_ref"])
        finally:
            conn.close()

    def read_idempotency(self, request_id: str) -> tuple[str, Mapping[str, Any]] | None:
        conn = self._connect(readonly=True)
        try:
            row = conn.execute(
                "SELECT fingerprint, result_json FROM idempotency WHERE operation_request_id = ?",
                (request_id,),
            ).fetchone()
            if not row:
                return None
            return row["fingerprint"], json.loads(row["result_json"])
        finally:
            conn.close()

    def read_outbox(self) -> list[Mapping[str, Any]]:
        conn = self._connect(readonly=True)
        try:
            rows = conn.execute(
                "SELECT outbox_id, occurrence_id, control_lane_id, payload_json "
                "FROM outbox ORDER BY outbox_id"
            ).fetchall()
            return [
                {
                    "outbox_id": row["outbox_id"],
                    "occurrence_id": row["occurrence_id"],
                    "control_lane_id": row["control_lane_id"],
                    "payload": json.loads(row["payload_json"]),
                }
                for row in rows
            ]
        finally:
            conn.close()

    def snapshot_counts(self) -> Mapping[str, int]:
        conn = self._connect(readonly=True)
        try:
            return {
                table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for table in ("canonical_records", "lane_heads", "idempotency", "outbox")
            }
        finally:
            conn.close()


class _MutationTransaction:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def read_latest(self, kind: str, record_id: str) -> StoredRecord | None:
        row = self._conn.execute(
            "SELECT canonical_json, digest FROM canonical_records "
            "WHERE kind = ? AND record_id = ? ORDER BY record_revision DESC LIMIT 1",
            (kind, record_id),
        ).fetchone()
        return _stored(row) if row else None

    def read_idempotency(self, request_id: str) -> tuple[str, Mapping[str, Any]] | None:
        row = self._conn.execute(
            "SELECT fingerprint, result_json FROM idempotency WHERE operation_request_id = ?",
            (request_id,),
        ).fetchone()
        if not row:
            return None
        return row["fingerprint"], json.loads(row["result_json"])

    def append_canonical(self, record: Mapping[str, Any]) -> StoredRecord:
        validate_record(record)
        text = canonical_dumps(record)
        digest = canonical_digest(record)
        try:
            self._conn.execute(
                "INSERT INTO canonical_records "
                "(kind, id_scheme, record_id, record_revision, control_lane_id, stage_state, canonical_json, digest) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["kind"], record["id_scheme"], record["id"], record["record_revision"],
                    record.get("control_lane_id"), record.get("state"), text, digest,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise StoreConflict(str(exc)) from exc
        return StoredRecord(dict(record), digest, text)

    def compare_and_advance_lane(self, lane_id: str, expected_ref: str | None, next_ref: str) -> LaneHead:
        self._conn.execute(
            "INSERT OR IGNORE INTO lane_heads(lane_id, version, occurrence_ref) VALUES (?, 0, NULL)",
            (lane_id,),
        )
        cur = self._conn.execute(
            "UPDATE lane_heads SET version = version + 1, occurrence_ref = ? "
            "WHERE lane_id = ? AND occurrence_ref IS ?",
            (next_ref, lane_id, expected_ref),
        )
        if cur.rowcount != 1:
            raise StoreConflict("lane compare-and-advance failed")
        row = self._conn.execute(
            "SELECT version, occurrence_ref FROM lane_heads WHERE lane_id = ?", (lane_id,)
        ).fetchone()
        return LaneHead(lane_id, int(row["version"]), row["occurrence_ref"])

    def append_idempotency(self, request_id: str, fingerprint: str, result: Mapping[str, Any]) -> None:
        try:
            self._conn.execute(
                "INSERT INTO idempotency(operation_request_id, fingerprint, result_json) VALUES (?, ?, ?)",
                (request_id, fingerprint, canonical_dumps(result)),
            )
        except sqlite3.IntegrityError as exc:
            raise StoreConflict(str(exc)) from exc

    def append_outbox(self, outbox_id: str, occurrence_id: str, lane_id: str, payload: Mapping[str, Any]) -> None:
        try:
            self._conn.execute(
                "INSERT INTO outbox(outbox_id, occurrence_id, control_lane_id, payload_json) VALUES (?, ?, ?, ?)",
                (outbox_id, occurrence_id, lane_id, canonical_dumps(payload)),
            )
        except sqlite3.IntegrityError as exc:
            raise StoreConflict(str(exc)) from exc


def _stored(row: sqlite3.Row) -> StoredRecord:
    text = row["canonical_json"]
    return StoredRecord(json.loads(text), row["digest"], text)
