from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Mapping

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tests.control_plane.cp_i05_fixtures import configured_mutation, dispatch_authorization, seed_surface
from tools.aegis_control.dispatch import DispatchService
from tools.aegis_control.execution_surface import DeterministicExecutionSurface
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.recovery import RecoveryCoordinator
from tools.aegis_control.store import ControlStore


EVIDENCE_FILE = "p36-edge-closure.json"
EVIDENCE_FAMILY = "CP-I05-P36-EDGE-CLOSURE"
EXPECTED_REPAIR_PACKAGE = "CP-I05-P36-01"


def _time(seconds: int) -> str:
    value = datetime(2026, 9, 1, 2, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return value.isoformat().replace("+00:00", "Z")


def _write(path: Path, payload: Mapping[str, Any]) -> str:
    data = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.write_bytes(data)
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _direct_terminal_requires_result() -> Mapping[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "terminal-bypass.db"))
        surface = DeterministicExecutionSurface()
        seed_surface(
            surface,
            occurrence_id="so_edge_terminal_bypass",
            execution_ref="exec://edge-terminal-bypass",
        )
        mutation = configured_mutation(store, surface)
        mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_edge_terminal_bypass_schedule",
            "lane_edge_terminal_bypass",
            {"occurrence": occurrence_record("so_edge_terminal_bypass", "lane_edge_terminal_bypass")},
        ))
        current = store.read_latest("STAGE_OCCURRENCE", "so_edge_terminal_bypass")
        terminal = terminal_facts()
        terminal["produced_refs"] = []
        before = dict(store.snapshot_counts())
        code = None
        try:
            mutation.apply(make_request(
                "TERMINATE_STAGE_OCCURRENCE",
                "req_edge_terminal_bypass_terminal",
                "lane_edge_terminal_bypass",
                {
                    "occurrence_id": "so_edge_terminal_bypass",
                    "recorded_at": _time(20),
                    "terminal": terminal,
                },
                expected_state(
                    target_record_revision=current.record["record_revision"],
                    target_record_digest=current.digest,
                    work_scope_ref=current.record["work_scope_ref"],
                ),
            ))
        except MutationRejected as exc:
            code = exc.code
        after = dict(store.snapshot_counts())
        latest = store.read_latest("STAGE_OCCURRENCE", "so_edge_terminal_bypass")
        return {
            "case": "configured_boundary_no_progress_still_requires_exact_result",
            "pass": code == "RESULT_MATERIALIZATION_REQUIRED"
            and before == after
            and latest.record["state"] == "OPEN",
            "rejection": code,
            "before": before,
            "after": after,
            "zero_residue": before == after,
            "final_state": latest.record["state"],
        }


def _time_uncertainty_persists() -> Mapping[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "time-uncertainty.db"))
        mutation = MutationService(store)
        scheduled = mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_edge_time_uncertainty_schedule",
            "lane_edge_time_uncertainty",
            {"occurrence": occurrence_record("so_edge_time_uncertainty", "lane_edge_time_uncertainty")},
        ))
        outbox_id = scheduled["outbox_ids"][0]
        surface = DeterministicExecutionSurface()
        DispatchService(
            store,
            surface,
            authorization_resolver=dispatch_authorization(),
        ).dispatch(outbox_id, attempted_at=_time(0))
        before = dict(store.snapshot_counts())
        RecoveryCoordinator(store, surface).reconcile_outbox(
            outbox_id,
            observed_at=_time(1800),
        )
        after = dict(store.snapshot_counts())
        state = store.read_delivery_state(outbox_id)
        occurrence_count = len(store.read_revisions("STAGE_OCCURRENCE", "so_edge_time_uncertainty"))
        return {
            "case": "thirty_minute_uncertainty_persists_without_replacement_occurrence",
            "pass": state["diagnostic_state"] == "DELIVERY_UNCERTAIN"
            and state["attempt_count"] == 1
            and occurrence_count == 1
            and before == after,
            "diagnostic_state": state["diagnostic_state"],
            "attempt_count": state["attempt_count"],
            "semantic_occurrence_count": occurrence_count,
            "before": before,
            "after": after,
            "canonical_unchanged": before == after,
        }


def augment_evidence_bundle(*, output_dir: Path) -> Mapping[str, Any]:
    manifest_path = output_dir / "evidence-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("repair_package_id") != EXPECTED_REPAIR_PACKAGE:
        raise AssertionError("unexpected CP-I05 repair package lineage")

    cases = [_direct_terminal_requires_result(), _time_uncertainty_persists()]
    names = [case["case"] for case in cases]
    if len(names) != len(set(names)) or not all(case["pass"] for case in cases):
        raise AssertionError("CP-I05 P36 edge closure contains a failing/duplicate case")
    payload = {
        "evidence_family": EVIDENCE_FAMILY,
        "repair_package_id": EXPECTED_REPAIR_PACKAGE,
        "repair_lineage": dict(manifest["repair_lineage"]),
        "result_revision": manifest["result_revision"],
        "cases": cases,
        "passed": True,
    }
    digest = _write(output_dir / EVIDENCE_FILE, payload)

    entries = [entry for entry in manifest["evidence_files"] if entry["file"] != EVIDENCE_FILE]
    entries.append({
        "file": EVIDENCE_FILE,
        "evidence_family": EVIDENCE_FAMILY,
        "digest": digest,
        "passed": True,
    })
    manifest["evidence_files"] = sorted(entries, key=lambda item: item["file"])
    manifest["passed"] = bool(manifest["passed"] and payload["passed"])
    _write(manifest_path, manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    manifest = augment_evidence_bundle(output_dir=Path(args.output_dir))
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
