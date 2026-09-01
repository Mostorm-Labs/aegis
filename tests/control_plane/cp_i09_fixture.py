from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import occurrence_record, terminal_facts
from tools.aegis_control.canonical import canonical_digest, canonical_dumps
from tools.aegis_control.store import ControlStore


REFERENCE_HISTORY_REVISIONS = 5_000_000
REFERENCE_RETAINED_SCOPES = 100_000
REFERENCE_OPEN_OCCURRENCES = 2_000
REFERENCE_ACTIVE_PROVIDER_JOBS = 500
REFERENCE_INTERACTIVE_USERS = 100
RECENT_COMPLETED_SCOPE_SAMPLE = 100
RECENT_COMPLETED_REVISIONS = 250
PROJECTION_LANE_REVISIONS = 2_000


def _insert_record(conn: sqlite3.Connection, record: dict, *, stage_state: str | None = None) -> str:
    digest = canonical_digest(record)
    conn.execute(
        "INSERT INTO canonical_records(kind,id_scheme,record_id,record_revision,control_lane_id,stage_state,canonical_json,digest) VALUES(?,?,?,?,?,?,?,?)",
        (
            record["kind"],
            record.get("id_scheme", "UUID"),
            record["id"],
            record["record_revision"],
            record.get("control_lane_id"),
            stage_state,
            canonical_dumps(record).decode("utf-8"),
            digest,
        ),
    )
    return digest


def _percentile95(values: list[int]) -> int:
    ordered = sorted(values)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return ordered[index]


def load_reference_fixture(db_path: str | Path) -> dict:
    db_path = str(db_path)
    ControlStore(db_path)  # materialize the production schema before benchmark-only bulk preload.
    conn = sqlite3.connect(db_path, timeout=60.0)
    conn.execute("PRAGMA synchronous=OFF")
    conn.execute("PRAGMA temp_store=MEMORY")

    # Volume preload: 100k retained WorkScopes x 50 retained package revisions = 5M rows.
    # This benchmark-only loader never ships with production modules and never participates in semantic mutation.
    conn.executescript(
        """
        CREATE TEMP TABLE IF NOT EXISTS bench_digits(d INTEGER PRIMARY KEY);
        DELETE FROM bench_digits;
        INSERT INTO bench_digits(d) VALUES(0),(1),(2),(3),(4),(5),(6),(7),(8),(9);
        """
    )
    conn.execute("BEGIN")
    conn.execute(
        """
        WITH nums AS (
          SELECT
            a.d + 10*b.d + 100*c.d + 1000*d.d + 10000*e.d + 100000*f.d + 1000000*g.d AS n
          FROM bench_digits a
          CROSS JOIN bench_digits b
          CROSS JOIN bench_digits c
          CROSS JOIN bench_digits d
          CROSS JOIN bench_digits e
          CROSS JOIN bench_digits f
          CROSS JOIN bench_digits g
        )
        INSERT INTO canonical_records(
          kind,id_scheme,record_id,record_revision,control_lane_id,stage_state,canonical_json,digest
        )
        SELECT
          'VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE',
          'UUID',
          'vip_bench_' || printf('%06d', CAST(n / 50 AS INTEGER)),
          (n % 50) + 1,
          'lane_bench_' || printf('%06d', CAST(n / 50 AS INTEGER)),
          NULL,
          printf(
            '{"kind":"VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE","id_scheme":"UUID","id":"vip_bench_%06d","record_revision":%d,"control_lane_id":"lane_bench_%06d","work_scope_ref":{"id":"ws_bench_%06d"},"benchmark_volume_preload":true}',
            CAST(n / 50 AS INTEGER), (n % 50) + 1, CAST(n / 50 AS INTEGER), CAST(n / 50 AS INTEGER)
          ),
          'sha256:' || printf('%064x', n + 1)
        FROM nums
        WHERE n < ?
        """,
        (REFERENCE_HISTORY_REVISIONS,),
    )

    # 10k lane heads make the active-scope floor concrete in the production lane-head table.
    conn.executemany(
        "INSERT OR IGNORE INTO lane_heads(lane_id,version,occurrence_ref) VALUES(?,0,NULL)",
        ((f"lane_bench_{i:06d}",) for i in range(10_000)),
    )

    # Dedicated <=2k-revision projection WorkScope. Forty package lineages x 50 revisions.
    for package_index in range(40):
        for revision in range(1, 51):
            record = {
                "kind": "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE",
                "id_scheme": "UUID",
                "id": f"vip_projection_{package_index:03d}",
                "record_revision": revision,
                "control_lane_id": "lane_projection",
                "work_scope_ref": {"id": "ws_projection"},
                "benchmark_volume_preload": True,
            }
            _insert_record(conn, record)
    conn.execute("INSERT OR IGNORE INTO lane_heads(lane_id,version,occurrence_ref) VALUES('lane_projection',0,NULL)")

    # 2k live OPEN occurrences, each on its own lane. First 500 also own committed outbox entries.
    open_refs: list[tuple[str, str, str]] = []
    for i in range(REFERENCE_OPEN_OCCURRENCES):
        lane = f"lane_open_{i:04d}"
        occurrence = occurrence_record(f"so_open_{i:04d}", lane)
        digest = _insert_record(conn, occurrence, stage_state="OPEN")
        ref = f"STAGE_OCCURRENCE:{occurrence['id']}@1#{digest}"
        conn.execute(
            "INSERT OR REPLACE INTO lane_heads(lane_id,version,occurrence_ref) VALUES(?,?,?)",
            (lane, 1, ref),
        )
        open_refs.append((occurrence["id"], lane, ref))

    for i, (occurrence_id, lane, ref) in enumerate(open_refs[:REFERENCE_ACTIVE_PROVIDER_JOBS]):
        outbox_id = f"out_bench_{i:04d}"
        payload = json.dumps(
            {"occurrence_ref": ref, "control_lane_id": lane, "operation_request_id": f"req_bench_dispatch_{i:04d}"},
            sort_keys=True,
            separators=(",", ":"),
        )
        conn.execute(
            "INSERT INTO outbox(outbox_id,occurrence_id,control_lane_id,payload_json,status,created_at,acked_at) VALUES(?,?,?,?,?,?,NULL)",
            (outbox_id, occurrence_id, lane, payload, "READY", "2026-09-01T00:00:00Z"),
        )

    # Explicit p95=250 recent completed StageOccurrence-revision sample.
    recent_counts: list[int] = []
    for scope_index in range(RECENT_COMPLETED_SCOPE_SAMPLE):
        lane = f"lane_recent_{scope_index:03d}"
        occurrence_id = f"so_recent_{scope_index:03d}"
        for revision in range(1, RECENT_COMPLETED_REVISIONS + 1):
            record = occurrence_record(occurrence_id, lane)
            record["record_revision"] = revision
            if revision == RECENT_COMPLETED_REVISIONS:
                record["state"] = "TERMINAL"
                record["terminal"] = terminal_facts()
                stage_state = "TERMINAL"
            else:
                stage_state = "OPEN"
            _insert_record(conn, record, stage_state=stage_state)
        recent_counts.append(RECENT_COMPLETED_REVISIONS)

    conn.commit()

    canonical_rows = conn.execute("SELECT COUNT(*) FROM canonical_records").fetchone()[0]
    retained_scopes = conn.execute(
        "SELECT COUNT(DISTINCT record_id) FROM canonical_records WHERE kind='VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE' AND record_id LIKE 'vip_bench_%'"
    ).fetchone()[0]
    open_occurrences = conn.execute(
        "SELECT COUNT(*) FROM canonical_records WHERE kind='STAGE_OCCURRENCE' AND stage_state='OPEN' AND record_id LIKE 'so_open_%'"
    ).fetchone()[0]
    provider_jobs = conn.execute("SELECT COUNT(*) FROM outbox WHERE outbox_id LIKE 'out_bench_%'").fetchone()[0]
    active_lanes = conn.execute("SELECT COUNT(*) FROM lane_heads").fetchone()[0]
    projection_revisions = conn.execute(
        "SELECT COUNT(*) FROM canonical_records WHERE control_lane_id='lane_projection'"
    ).fetchone()[0]
    conn.close()

    return {
        "db_path": db_path,
        "fixture_load_mode": "BENCHMARK_ONLY_PRODUCTION_SCHEMA_PRELOAD",
        "canonical_record_revisions_retained": canonical_rows,
        "retained_work_scopes": retained_scopes,
        "active_work_scopes": active_lanes,
        "open_stage_occurrences": open_occurrences,
        "recent_completed_occurrence_revisions_per_work_scope_p95": _percentile95(recent_counts),
        "recent_completed_scope_sample_size": len(recent_counts),
        "concurrent_active_provider_jobs": provider_jobs,
        "concurrent_interactive_app_users": REFERENCE_INTERACTIVE_USERS,
        "projection_lane_revisions": projection_revisions,
        "benchmark_volume_preload_rows_are_not_semantic_mutation_evidence": True,
    }
