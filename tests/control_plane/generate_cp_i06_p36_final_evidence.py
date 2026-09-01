from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any

import tests.control_plane.generate_cp_i06_evidence as base
import tests.control_plane.generate_cp_i06_p36_evidence as p36
from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.recovery import backup_control_store, restore_control_store_backup
from tools.aegis_control.store import ControlStore


PACKAGE_ID = p36.PACKAGE_ID
PACKAGE_REF = p36.PACKAGE_REF
TASK_ANCHOR = p36.TASK_ANCHOR
CP_I05_REVISION = p36.CP_I05_REVISION
CP_I05_P34_COMMENT = p36.CP_I05_P34_COMMENT
CP_I05_EVIDENCE_ARTIFACT_ID = p36.CP_I05_EVIDENCE_ARTIFACT_ID
CP_I05_MATERIALIZED_REF = p36.CP_I05_MATERIALIZED_REF
P31_MANDATORY_OBLIGATIONS = p36.P31_MANDATORY_OBLIGATIONS

_ORIGINAL_BACKUP_CASES = base._backup_restore_cases
_ORIGINAL_COVERAGE_MAP = p36._coverage_map

# Exact case IDs independently observed in CP-I05 artifact 9790980577 /
# dispatch-fault-matrix.json during P36 reviewer-side verification. This catalog
# exists only to prevent a coverage map from naming a predecessor case that does
# not exist. It does not rewrite predecessor evidence as CP-I06 truth.
CP_I05_DISPATCH_CASE_IDS = {
    "committed_outbox_dispatch",
    "transient_or_uncommitted_schedule_no_dispatch",
    "schedule_crash_after_canonical",
    "schedule_crash_after_lane",
    "schedule_crash_after_outbox",
    "schedule_crash_after_idempotency",
    "operational_delivery_metadata_no_canonical_change",
    "duplicate_transport_same_occurrence",
    "provider_ack_lost_then_restart_same_execution",
    "unauthorized_cross_primary_no_provider_request",
    "noncurrent_authorization_no_provider_request",
    "provider_ack_not_completion",
    "callback_loss_query_recovery",
    "delivery_uncertain_boundary_no_replacement_occurrence",
    "provider_running_to_materialized_exact_result",
    "duplicate_callback_no_duplicate_terminal_revision",
    "worker_restart_reuses_durable_correlation",
}


def _acknowledged_gap_case() -> dict[str, Any]:
    """Prove a structurally valid but stale backup cannot continue past an acknowledged gap."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        live = ControlStore(str(root / "live.db"))
        mutation = MutationService(live)
        record = occurrence_record("so_gap_root", "lane_gap_restore")
        mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_gap_root",
            "lane_gap_restore",
            {"occurrence": record},
        ))

        # Backup while revision 1 is OPEN. This is structurally valid but will
        # become stale after the next acknowledged canonical commit.
        backup_path = root / "stale-valid-backup.db"
        backup_control_store(live, str(backup_path))

        acknowledged_terminal = base._terminalize(
            mutation,
            live,
            "so_gap_root",
            "lane_gap_restore",
        )
        acknowledged_ref = base._internal_ref(acknowledged_terminal)

        restored = restore_control_store_backup(
            str(backup_path),
            str(root / "restored-stale.db"),
        )
        restored_mutation = MutationService(restored)
        restored_root = restored.read_latest("STAGE_OCCURRENCE", "so_gap_root")
        successor = occurrence_record("so_after_gap", "lane_gap_restore")
        before = dict(restored.snapshot_counts())
        code = None
        try:
            restored_mutation.apply(make_request(
                "SCHEDULE_STAGE_OCCURRENCE",
                "req_after_gap",
                "lane_gap_restore",
                {"occurrence": successor},
                expected_state(
                    predecessor_occurrence_ref=acknowledged_ref,
                    work_scope_ref=successor["work_scope_ref"],
                ),
            ))
        except MutationRejected as exc:
            code = exc.code

        return base._case(
            "stale_valid_backup_missing_acknowledged_terminal_blocks_continuation",
            code == "CONTROL_LANE_SCHEDULE_CONFLICT"
            and restored_root.record["state"] == "OPEN"
            and before == restored.snapshot_counts(),
            rejection=code,
            acknowledged_terminal_ref=acknowledged_ref,
            restored_record_revision=restored_root.record["record_revision"],
            restored_state=restored_root.record["state"],
            zero_residue=before == restored.snapshot_counts(),
        )


def _backup_cases() -> list[dict[str, Any]]:
    return [*_ORIGINAL_BACKUP_CASES(), _acknowledged_gap_case()]


def _coverage_map() -> dict[str, Any]:
    coverage = _ORIGINAL_COVERAGE_MAP()
    entry = {
        "mode": "DIRECT_CP_I06",
        "case_id": (
            "CPV-E-BACKUP-RESTORE::"
            "stale_valid_backup_missing_acknowledged_terminal_blocks_continuation"
        ),
        "rationale": (
            "P36 directly executes a valid backup taken before a later acknowledged "
            "terminal commit; restoring that stale snapshot and presenting the later "
            "exact predecessor fails closed with zero residue."
        ),
    }
    coverage["obligations"]["possible_acknowledged_commit_gap_blocks_continuation"] = entry

    for obligation, item in coverage["obligations"].items():
        if item["mode"] != "INHERITED_EXACT_PREDECESSOR":
            continue
        if item.get("evidence_file") != "dispatch-fault-matrix.json":
            raise RuntimeError(f"unexpected inherited CP-I05 evidence file for {obligation}")
        if item.get("case_id") not in CP_I05_DISPATCH_CASE_IDS:
            raise RuntimeError(
                f"unknown inherited CP-I05 dispatch case for {obligation}: {item.get('case_id')}"
            )
    coverage["passed"] = True
    return coverage


def generate(output_dir: Path, *, result_revision: str) -> dict[str, Any]:
    base._backup_restore_cases = _backup_cases
    p36._coverage_map = _coverage_map
    manifest = p36.generate(output_dir, result_revision=result_revision)
    manifest["p36_repair"]["inherited_case_catalog_validated"] = True
    manifest["p36_repair"]["acknowledged_gap_direct_case"] = (
        "stale_valid_backup_missing_acknowledged_terminal_blocks_continuation"
    )
    base._write_json(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--output-dir", default="artifacts/cp-i06")
    args = parser.parse_args()
    manifest = generate(Path(args.output_dir), result_revision=args.result_revision)
    if not manifest["passed"]:
        raise SystemExit("CP-I06 P36 final evidence bundle did not satisfy repair/reverification contract")


if __name__ == "__main__":
    main()
