from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.control_plane.cp_i03_evidence import (
    AUTHORITY_REFS,
    CP_I02_ACCEPTED_REF,
    CP_I02_P34_COMMENT,
    PACKAGE_REF,
    TASK_ID,
    TEST_COMMANDS,
    compile_evidence,
)


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def generate(output_dir: Path, result_revision: str, package_ref: str = PACKAGE_REF) -> dict:
    repo_root = Path(__file__).resolve().parents[2]
    compiled = compile_evidence(repo_root)
    for key in ("ownership_rollout", "derived_state", "canonical_conformance"):
        if not compiled[key]["passed"]:
            raise RuntimeError(f"CP-I03 evidence family failed: {key}")
    if any(compiled["zero_tolerance_metrics"].values()):
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
        },
        "evidence": {
            "CPV-E-OWNERSHIP-ROLLOUT": files["ownership_rollout"].name,
            "CPV-E-DERIVED-STATE": files["derived_state"].name,
            "CPV-E-CANONICAL-CONFORMANCE": files["canonical_conformance"].name,
        },
        "metrics": compiled["zero_tolerance_metrics"],
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
