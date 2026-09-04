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

from tests.control_plane.cp_i02_evidence import (
    AUTHORITY_REFS,
    PACKAGE_REF,
    PREDECESSOR_P34_COMMENT,
    PREDECESSOR_REF,
    TASK_ID,
    TEST_COMMANDS,
)
from tests.control_plane.cp_i02_evidence_compat import compile_evidence


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def generate(output_dir: Path, result_revision: str, package_ref: str = PACKAGE_REF) -> dict:
    repo_root = Path(__file__).resolve().parents[2]
    compiled = compile_evidence(repo_root)
    if not compiled["canonical_conformance"]["passed"]:
        raise RuntimeError("CPV-E-CANONICAL-CONFORMANCE did not satisfy zero-tolerance metrics")
    if not compiled["store_audit"]["passed"]:
        raise RuntimeError("CPV-E-STORE-AUDIT failed")
    if not compiled["crash_matrix"]["passed"]:
        raise RuntimeError("transaction/crash matrix failed")

    files = {
        "canonical_conformance": output_dir / "canonical-conformance.json",
        "store_audit": output_dir / "store-audit.json",
        "trace_corpus": output_dir / "trace-corpus.json",
        "crash_matrix": output_dir / "crash-matrix.json",
    }
    for key, path in files.items():
        _write_json(path, compiled[key])

    schema_digests = sorted({
        audit["schema_digest"]
        for audit in compiled["store_audit"]["audits"].values()
    })
    manifest = {
        "evidence_bundle": "CP-I02",
        "task_id": TASK_ID,
        "package_ref": package_ref,
        "result_revision": result_revision,
        "accepted_predecessor": {
            "revision": PREDECESSOR_REF,
            "p34_comment": PREDECESSOR_P34_COMMENT,
            "disposition": "PASS / ACCEPTED_FOR_DOWNSTREAM",
        },
        "authority_refs": AUTHORITY_REFS,
        "runtime": compiled["runtime"],
        "test_commands": TEST_COMMANDS,
        "store_schema_digests": schema_digests,
        "evidence": {
            "CPV-E-CANONICAL-CONFORMANCE": files["canonical_conformance"].name,
            "CPV-E-STORE-AUDIT": files["store_audit"].name,
            "raw_canonical_trace_corpus": files["trace_corpus"].name,
            "transaction_crash_matrix": files["crash_matrix"].name,
        },
        "metrics": compiled["canonical_conformance"]["metrics"],
        "file_digests": {path.name: _sha256(path) for path in files.values()},
        "claims": {
            "cp_i02_bounded_conformance": True,
            "complete_CPV_E_D0_CONFORMANCE": False,
            "complete_CPV_E_DISPATCH_FAULT_MATRIX": False,
            "rollout_policy_proof": False,
            "provider_currentness_proof": False,
            "R0": False,
            "S0": False,
            "seven_day_cost": False,
            "monthly_availability": False,
            "p34_gate_pass": False,
        },
    }
    _write_json(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--package-ref", default=PACKAGE_REF)
    parser.add_argument("--output-dir", default="artifacts/cp-i02")
    args = parser.parse_args()
    generate(Path(args.output_dir), args.result_revision, args.package_ref)


if __name__ == "__main__":
    main()
