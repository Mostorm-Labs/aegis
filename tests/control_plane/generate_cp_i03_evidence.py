from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.control_plane.cp_i02_fixtures import occurrence_record
from tests.control_plane.cp_i03_evidence import (
    AUTHORITY_REFS,
    CP_I02_ACCEPTED_REF,
    CP_I02_P34_COMMENT,
    PACKAGE_REF,
    TASK_ID,
    TEST_COMMANDS,
    _autonomous_occurrence,
    _completed_projection,
    compile_evidence,
)
from tools.aegis_control import (
    ControlStore,
    MutationRejected,
    MutationService,
    PolicyEvaluator,
    Scheduler,
    SchedulingDenied,
)

REPAIR_LINEAGE = {
    "original_blocker_id": "CP-I03-P34-B1",
    "source_p34_comment": "5476589682",
    "source_p35_comment": "5476782049",
    "source_p36_comment": "5477531093",
    "rereview_blocker_id": "CP-I03-P34-B2",
    "source_p34_rereview_comment": "5479230527",
    "source_p35_b2_comment": "5480059914",
}


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot(store: ControlStore) -> tuple[dict, int]:
    return dict(store.snapshot_counts()), len(store.read_outbox())


def _submit_policy_rejection_case(
    *,
    case_id: str,
    fresh_policy_basis: dict,
    expected_code: str,
) -> tuple[str | None, bool]:
    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / f"{case_id}.db"))
        mutation = MutationService(store)
        lane = f"lane_{case_id}"
        predecessor_id = f"so_{case_id}_a"
        candidate_id = f"so_{case_id}_b"
        projection = _completed_projection(store, mutation, lane, predecessor_id)
        allowed_basis = {"current": True, "rollout_authorized": True, "revision": "v1"}
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
            policy_basis_resolver=lambda candidate: dict(fresh_policy_basis),
        )
        candidate = scheduler.derive_candidate(
            projection,
            allowed,
            _autonomous_occurrence(candidate_id, lane),
        )
        before = _snapshot(store)
        rejection_code = None
        try:
            scheduler.submit_candidate(candidate)
        except MutationRejected as exc:
            rejection_code = exc.code
        after = _snapshot(store)
        zero_residue = before == after and store.read_latest("STAGE_OCCURRENCE", candidate_id) is None
        return rejection_code, zero_residue and rejection_code == expected_code


def _policy_rejection_zero_residue() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "pinned-mismatch.db"))
        mutation = MutationService(store)
        lane = "lane_policy_binding"
        projection = _completed_projection(store, mutation, lane, "so_policy_binding_a")
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
        before = _snapshot(store)
        pinned_code = None
        try:
            scheduler.derive_candidate(
                projection,
                allowed,
                occurrence_record("so_policy_binding_b", lane),
            )
        except SchedulingDenied as exc:
            pinned_code = exc.code
        after = _snapshot(store)
        pinned_zero = (
            before == after
            and pinned_code == "CANDIDATE_POLICY_BINDING_MISMATCH"
            and store.read_latest("STAGE_OCCURRENCE", "so_policy_binding_b") is None
        )

    cases = {
        "allow_to_deny": (
            {"current": True, "rollout_authorized": False, "revision": "v1"},
            "POLICY_REVALIDATION_DENIED",
        ),
        "changed_policy_digest": (
            {"current": True, "rollout_authorized": True, "revision": "v2"},
            "STALE_POLICY_AUTHORIZATION",
        ),
        "stale_current_basis": (
            {"current": False, "rollout_authorized": True, "revision": "v1"},
            "POLICY_REVALIDATION_DENIED",
        ),
        "ambiguous_current_basis": (
            {"current": True},
            "POLICY_REVALIDATION_DENIED",
        ),
    }
    rejection_codes = {"pinned_policy_mismatch": pinned_code}
    zero_residue = {"pinned_policy_mismatch": pinned_zero}
    for case_id, (fresh_basis, expected_code) in cases.items():
        observed_code, passed = _submit_policy_rejection_case(
            case_id=case_id,
            fresh_policy_basis=fresh_basis,
            expected_code=expected_code,
        )
        rejection_codes[case_id] = observed_code
        zero_residue[case_id] = passed

    metrics = {
        "pinned_policy_mismatch_commits": 0 if zero_residue["pinned_policy_mismatch"] else 1,
        "stale_policy_authorization": 0
        if all(
            zero_residue[key]
            for key in ("allow_to_deny", "changed_policy_digest", "stale_current_basis")
        )
        else 1,
        "ambiguous_policy_authorization": 0 if zero_residue["ambiguous_current_basis"] else 1,
    }
    return {
        "rejection_codes": rejection_codes,
        "zero_residue": zero_residue,
        "metrics": metrics,
        "passed": all(zero_residue.values()) and all(value == 0 for value in metrics.values()),
    }


def generate(output_dir: Path, result_revision: str, package_ref: str = PACKAGE_REF) -> dict:
    repo_root = Path(__file__).resolve().parents[2]
    compiled = compile_evidence(repo_root)
    rejection = _policy_rejection_zero_residue()
    canonical = compiled["canonical_conformance"]
    canonical["extension"] = "CP-I03 scheduler / CP-I02 CAS + commit-bound policy rejection integration"
    canonical["policy_rejection_zero_residue"] = rejection
    canonical["metrics"] = {**canonical["metrics"], **rejection["metrics"]}
    canonical["passed"] = (
        canonical["passed"]
        and rejection["passed"]
        and all(value == 0 for value in canonical["metrics"].values())
    )

    metrics = compiled["zero_tolerance_metrics"]
    metrics["pinned_policy_mismatch_commits"] = max(
        metrics["pinned_policy_mismatch_commits"],
        rejection["metrics"]["pinned_policy_mismatch_commits"],
    )
    metrics["stale_policy_authorization"] = max(
        metrics["stale_policy_authorization"],
        rejection["metrics"]["stale_policy_authorization"],
    )
    metrics["ambiguous_policy_authorization"] = rejection["metrics"]["ambiguous_policy_authorization"]

    for key in ("ownership_rollout", "derived_state", "canonical_conformance"):
        if not compiled[key]["passed"]:
            raise RuntimeError(f"CP-I03 evidence family failed: {key}")
    if any(metrics.values()):
        raise RuntimeError("CP-I03 zero-tolerance metric failure")

    files = {
        "ownership_rollout": output_dir / "ownership-rollout.json",
        "derived_state": output_dir / "derived-state.json",
        "canonical_conformance": output_dir / "canonical-conformance.json",
    }
    for key, path in files.items():
        _write_json(path, compiled[key])

    manifest = {
        "evidence_bundle": "CP-I03",
        "task_id": TASK_ID,
        "package_ref": package_ref,
        "result_revision": result_revision,
        "repair_lineage": dict(REPAIR_LINEAGE),
        "accepted_cp_i02": {
            "revision": CP_I02_ACCEPTED_REF,
            "p34_comment": CP_I02_P34_COMMENT,
            "disposition": "PASS / ACCEPTED_FOR_DOWNSTREAM",
        },
        "authority_refs": AUTHORITY_REFS,
        "runtime": compiled["runtime"],
        "test_commands": TEST_COMMANDS,
        "oracle_identities": {
            "projection": "O-CRM independent expected semantic state",
            "canonical_writer": "static single-writer ownership probe",
            "scheduler_concurrency": "CP-I02 lane CAS / compare-and-append",
            "policy_rejection": "submit_candidate commit-bound fail-closed zero-residue probes",
        },
        "evidence": {
            "CPV-E-OWNERSHIP-ROLLOUT": files["ownership_rollout"].name,
            "CPV-E-DERIVED-STATE": files["derived_state"].name,
            "CPV-E-CANONICAL-CONFORMANCE": files["canonical_conformance"].name,
        },
        "metrics": metrics,
        "file_digests": {path.name: _sha256(path) for path in files.values()},
        "claims": {
            "cp_i03_bounded_conformance": True,
            "current_cross_primary_rollout": "DENIED",
            "p34_gate_pass": False,
            "complete_CPV_E_D0_CONFORMANCE": False,
            "dispatch_or_provider_integration": False,
            "provider_currentness_proof": False,
            "CP_I04_plus": False,
            "R0": False,
            "S0": False,
            "seven_day_cost": False,
            "monthly_availability": False,
        },
        "gate_authority": "Evidence compiler has no authority to issue P34 PASS",
    }
    _write_json(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--package-ref", default=PACKAGE_REF)
    parser.add_argument("--output-dir", default="artifacts/cp-i03")
    args = parser.parse_args()
    generate(Path(args.output_dir), args.result_revision, args.package_ref)


if __name__ == "__main__":
    main()
