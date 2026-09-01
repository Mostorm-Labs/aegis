"""Durable SQLite persistence mechanics for Control Plane CP-I02..CP-I05.

This module owns storage, transaction, CAS, idempotency, outbox, and read-only
lookup mechanics. CP-I05 delivery state is deliberately operational and lives
outside canonical records, lane heads, and semantic idempotency. This module
intentionally owns no lifecycle, Authority, Gate, proof, policy,
child-acceptance, or provider-currentness decisions.
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
CREATE TABLE IF NOT EXISTS delivery_state (
    outbox_id TEXT PRIMARY KEY,
    occurrence_id TEXT NOT NULL,
    provider_correlation_id TEXT,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    first_attempt_at TEXT,
    last_attempt_at TEXT,
    next_attempt_at TEXT,
    provider_state TEXT,
    last_observed_at TEXT,
    diagnostic_state TEXT,
    FOREIGN KEY(outbox_id) REFERENCES outbox(outbox_id) ON DELETE CASCADE
);
"""


class ControlStore:
    """Public read surface plus private canonical mutation transaction factory."""

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
            return _read_latest(conn, kind, record_id)
        finally:
            conn.close()

    def read_exact(
        self,
        kind: str,
        record_id: str,
        record_revision: int,
        *,
        digest: str | None = None,
    ) -> StoredRecord | None:
        conn = self._connect(readonly=True)
        try:
            return _read_exact(conn, kind, record_id, record_revision, digest=digest)
        finally:
            conn.close()

    def read_revisions(self, kind: str, record_id: str) -> list[StoredRecord]:
        conn = self._connect(readonly=True)
        try:
            return _read_revisions(conn, kind, record_id)
        finally:
            conn.close()

    def read_lane_head(self, lane_id: str) -> LaneHead:
        conn = self._connect(readonly=True)
        try:
            return _read_lane_head(conn, lane_id)
        finally:
            conn.close()

    def read_lane_latest_records(self, lane_id: str) -> list[StoredRecord]:
        """Return the latest immutable revision for every canonical lineage in one lane."""
        conn = self._connect(readonly=True)
        try:
            return _read_latest_records(conn, lane_id=lane_id)
        finally:
            conn.close()

    def read_latest_stage_occurrences(self) -> list[StoredRecord]:
        """Read-only global latest occurrence view for WorkScope/child projection."""
        conn = self._connect(readonly=True)
        try:
            return _read_latest_records(conn, kind="STAGE_OCCURRENCE")
        finally:
            conn.close()

    def read_latest_escalations(self) -> list[StoredRecord]:
        conn = self._connect(readonly=True)
        try:
            return _read_latest_records(conn, kind="ESCALATION")
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
            return [_outbox_row(row) for row in rows]
        finally:
            conn.close()

    def read_outbox_entry(self, outbox_id: str) -> Mapping[str, Any] | None:
        """Read one durably committed outbox row for dispatch eligibility."""
        conn = self._connect(readonly=True)
        try:
            row = conn.execute(
                "SELECT outbox_id, occurrence_id, control_lane_id, payload_json "
                "FROM outbox WHERE outbox_id = ?",
                (outbox_id,),
            ).fetchone()
            return _outbox_row(row) if row else None
        finally:
            conn.close()

    def read_delivery_state(self, outbox_id: str) -> Mapping[str, Any] | None:
        """Read CP-I05 operational delivery state; never canonical lifecycle truth."""
        conn = self._connect(readonly=True)
        try:
            row = conn.execute(
                "SELECT outbox_id, occurrence_id, provider_correlation_id, attempt_count, "
                "first_attempt_at, last_attempt_at, next_attempt_at, provider_state, "
                "last_observed_at, diagnostic_state FROM delivery_state WHERE outbox_id = ?",
                (outbox_id,),
            ).fetchone()
            return _delivery_state(row) if row else None
        finally:
            conn.close()

    def record_delivery_attempt(
        self,
        outbox_id: str,
        attempted_at: str,
        *,
        next_attempt_at: str | None = None,
        provider_state: str | None = None,
    ) -> Mapping[str, Any]:
        """Record one transport attempt in the operational delivery table only."""
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            outbox = conn.execute(
                "SELECT occurrence_id FROM outbox WHERE outbox_id = ?", (outbox_id,)
            ).fetchone()
            if outbox is None:
                raise StoreConflict("outbox entry not found")
            conn.execute(
                "INSERT OR IGNORE INTO delivery_state(outbox_id, occurrence_id) VALUES (?, ?)",
                (outbox_id, outbox["occurrence_id"]),
            )
            conn.execute(
                "UPDATE delivery_state SET "
                "attempt_count = attempt_count + 1, "
                "first_attempt_at = COALESCE(first_attempt_at, ?), "
                "last_attempt_at = ?, next_attempt_at = ?, "
                "provider_state = COALESCE(?, provider_state) "
                "WHERE outbox_id = ?",
                (attempted_at, attempted_at, next_attempt_at, provider_state, outbox_id),
            )
            conn.execute("COMMIT")
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()
        state = self.read_delivery_state(outbox_id)
        assert state is not None
        return state

    def record_delivery_correlation(
        self,
        outbox_id: str,
        correlation_id: str,
        *,
        observed_at: str | None = None,
        provider_state: str = "ACCEPTED",
    ) -> Mapping[str, Any]:
        """Bind provider correlation as operational state without canonical mutation."""
        if not correlation_id:
            raise StoreConflict("provider correlation id is required")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            outbox = conn.execute(
                "SELECT occurrence_id FROM outbox WHERE outbox_id = ?", (outbox_id,)
            ).fetchone()
            if outbox is None:
                raise StoreConflict("outbox entry not found")
            conn.execute(
                "INSERT OR IGNORE INTO delivery_state(outbox_id, occurrence_id) VALUES (?, ?)",
                (outbox_id, outbox["occurrence_id"]),
            )
            current = conn.execute(
                "SELECT provider_correlation_id FROM delivery_state WHERE outbox_id = ?", (outbox_id,)
            ).fetchone()
            existing = current["provider_correlation_id"] if current else None
            if existing is not None and existing != correlation_id:
                raise StoreConflict("provider correlation conflict")
            conn.execute(
                "UPDATE delivery_state SET provider_correlation_id = ?, provider_state = ?, "
                "last_observed_at = COALESCE(?, last_observed_at) WHERE outbox_id = ?",
                (correlation_id, provider_state, observed_at, outbox_id),
            )
            conn.execute("COMMIT")
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()
        state = self.read_delivery_state(outbox_id)
        assert state is not None
        return state

    def snapshot_counts(self) -> Mapping[str, int]:
        """Return canonical/semantic counts only; CP-I05 operational state is excluded."""
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
        return _read_latest(self._conn, kind, record_id)

    def read_exact(
        self,
        kind: str,
        record_id: str,
        record_revision: int,
        *,
        digest: str | None = None,
    ) -> StoredRecord | None:
        return _read_exact(self._conn, kind, record_id, record_revision, digest=digest)

    def read_revisions(self, kind: str, record_id: str) -> list[StoredRecord]:
        return _read_revisions(self._conn, kind, record_id)

    def read_lane_head(self, lane_id: str) -> LaneHead:
        return _read_lane_head(self._conn, lane_id)

    def read_lane_latest_records(self, lane_id: str) -> list[StoredRecord]:
        return _read_latest_records(self._conn, lane_id=lane_id)

    def read_latest_stage_occurrences(self) -> list[StoredRecord]:
        return _read_latest_records(self._conn, kind="STAGE_OCCURRENCE")

    def read_latest_escalations(self) -> list[StoredRecord]:
        return _read_latest_records(self._conn, kind="ESCALATION")

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
        return _read_lane_head(self._conn, lane_id)

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


def _read_latest(conn: sqlite3.Connection, kind: str, record_id: str) -> StoredRecord | None:
    row = conn.execute(
        "SELECT canonical_json, digest FROM canonical_records "
        "WHERE kind = ? AND record_id = ? ORDER BY record_revision DESC LIMIT 1",
        (kind, record_id),
    ).fetchone()
    return _stored(row) if row else None


def _read_exact(
    conn: sqlite3.Connection,
    kind: str,
    record_id: str,
    record_revision: int,
    *,
    digest: str | None = None,
) -> StoredRecord | None:
    row = conn.execute(
        "SELECT canonical_json, digest FROM canonical_records "
        "WHERE kind = ? AND record_id = ? AND record_revision = ?",
        (kind, record_id, record_revision),
    ).fetchone()
    if not row:
        return None
    stored = _stored(row)
    if digest is not None and stored.digest != digest:
        return None
    return stored


def _read_revisions(conn: sqlite3.Connection, kind: str, record_id: str) -> list[StoredRecord]:
    rows = conn.execute(
        "SELECT canonical_json, digest FROM canonical_records "
        "WHERE kind = ? AND record_id = ? ORDER BY record_revision",
        (kind, record_id),
    ).fetchall()
    return [_stored(row) for row in rows]


def _read_lane_head(conn: sqlite3.Connection, lane_id: str) -> LaneHead:
    row = conn.execute(
        "SELECT version, occurrence_ref FROM lane_heads WHERE lane_id = ?", (lane_id,)
    ).fetchone()
    if not row:
        return LaneHead(lane_id, 0, None)
    return LaneHead(lane_id, int(row["version"]), row["occurrence_ref"])


def _read_latest_records(
    conn: sqlite3.Connection,
    *,
    lane_id: str | None = None,
    kind: str | None = None,
) -> list[StoredRecord]:
    where = []
    params: list[Any] = []
    if lane_id is not None:
        where.append("control_lane_id = ?")
        params.append(lane_id)
    if kind is not None:
        where.append("kind = ?")
        params.append(kind)
    predicate = " WHERE " + " AND ".join(where) if where else ""
    rows = conn.execute(
        "SELECT c.canonical_json, c.digest "
        "FROM canonical_records AS c "
        "JOIN ("
        "  SELECT kind, record_id, MAX(record_revision) AS max_revision "
        f"  FROM canonical_records{predicate} "
        "  GROUP BY kind, record_id"
        ") AS latest "
        "ON latest.kind = c.kind "
        "AND latest.record_id = c.record_id "
        "AND latest.max_revision = c.record_revision "
        "ORDER BY c.kind, c.record_id",
        tuple(params),
    ).fetchall()
    return [_stored(row) for row in rows]


def _outbox_row(row: sqlite3.Row) -> Mapping[str, Any]:
    return {
        "outbox_id": row["outbox_id"],
        "occurrence_id": row["occurrence_id"],
        "control_lane_id": row["control_lane_id"],
        "payload": json.loads(row["payload_json"]),
    }


def _delivery_state(row: sqlite3.Row) -> Mapping[str, Any]:
    return {
        "outbox_id": row["outbox_id"],
        "occurrence_id": row["occurrence_id"],
        "provider_correlation_id": row["provider_correlation_id"],
        "attempt_count": int(row["attempt_count"]),
        "first_attempt_at": row["first_attempt_at"],
        "last_attempt_at": row["last_attempt_at"],
        "next_attempt_at": row["next_attempt_at"],
        "provider_state": row["provider_state"],
        "last_observed_at": row["last_observed_at"],
        "diagnostic_state": row["diagnostic_state"],
    }


def _stored(row: sqlite3.Row) -> StoredRecord:
    text = row["canonical_json"]
    return StoredRecord(json.loads(text), row["digest"], text)
