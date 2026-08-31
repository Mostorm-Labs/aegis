"""P36-02 CP-I04 repair evidence wrapper.

Extends the frozen five-family CP-I04 evidence bundle with explicit N1/N2/N3
repair-closure metrics. It does not issue a Gate verdict.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.control_plane import generate_cp_i04_evidence as base
from tests.control_plane.test_cp_i04_required_child_barrier import exact_ref, root_scope
from tools import aegis_control


REPAIR_PACKAGE_ID = "CP-I04-P36-02"
SOURCE_P35_COMMENT = "5483198734"
SOURCE_P36_COMMENT = "5483129237"
RESOURCE = "p36/repair/acceptance"


def _exact_resolver(adapter, contract_ref: dict, resource_key: str):
    return aegis_control.TrustResolver(
        {"PROJECT_STATE": adapter},
        acceptance_contract_sources={
            aegis_control.canonical_digest(contract_ref): aegis_control.TrustFactRequest(
                "PROJECT_STATE", resource_key
            )
        },
    )


def _adapter(adapter_id: str):
    return aegis_control.DeterministicExternalAdapter(
        source_kind="PROJECT_STATE",
        adapter_id=adapter_id,
        secret=b"cp-i04-p36-repair-evidence",
        callback_available=True,
        query_correlation_available=True,
        clock=lambda: base.NOW,
    )


def _support(resolver, contract, suffix: str):
    return resolver.resolve_child_acceptance(
        root_scope(f"ws_p36_{suffix}"),
        exact_ref("STAGE_OCCURRENCE", f"so_p36_{suffix}", "d"),
        [contract],
    )


def _repair_closure() -> dict:
    missing_adapter = _adapter("p36-missing-fact")
    missing_contract = exact_ref("CONTRACT", "contract-p36-missing", "1")
    missing_adapter.set_resource(
        RESOURCE,
        version_scheme="acceptance-fact",
        version_value="m1",
        resolved_refs=[],
        satisfies=True,
    )
    missing = _support(
        _exact_resolver(missing_adapter, missing_contract, RESOURCE),
        missing_contract,
        "missing",
    )

    mutable_adapter = _adapter("p36-mutable-ref")
    mutable_contract = exact_ref("CONTRACT", "contract-p36-mutable", "2")
    mutable_fact = exact_ref("GATE_DECISION", "gate-p36-mutable", "3")
    mutable_fact["identity"] = {"scheme": "git-ref", "value": "refs/heads/main"}
    mutable_adapter.set_resource(
        RESOURCE,
        version_scheme="acceptance-fact",
        version_value="r1",
        resolved_refs=[mutable_fact],
        satisfies=True,
    )
    mutable = _support(
        _exact_resolver(mutable_adapter, mutable_contract, RESOURCE),
        mutable_contract,
        "mutable",
    )

    wrong_contract_results = {}
    exact_contract_results = {}
    for index, object_type in enumerate(("GATE_DECISION", "PROOF_EVALUATION", "RESULT")):
        adapter = _adapter(f"p36-contract-{index}")
        configured = exact_ref("CONTRACT", f"contract-p36-exact-{index}", "4")
        altered = exact_ref("CONTRACT", f"contract-p36-exact-{index}", "5")
        fact = exact_ref(object_type, f"fact-p36-exact-{index}", "6")
        adapter.set_resource(
            RESOURCE,
            version_scheme="acceptance-fact",
            version_value=f"c{index}",
            resolved_refs=[fact],
            satisfies=True,
        )
        resolver = _exact_resolver(adapter, configured, RESOURCE)
        wrong_contract_results[object_type] = _support(
            resolver, altered, f"wrong_contract_{index}"
        ).accepted
        exact_contract_results[object_type] = _support(
            resolver, configured, f"exact_contract_{index}"
        ).accepted

    metrics = {
        "missing_exact_acceptance_fact_accepted": 1 if missing.accepted else 0,
        "mutable_unpinned_trust_ref_accepted": 1 if mutable.accepted else 0,
        "wrong_acceptance_contract_identity_accepted": 1
        if any(wrong_contract_results.values())
        else 0,
    }
    return {
        "evidence_family": "CP-I04-P36-REPAIR-CLOSURE",
        "repair_package_id": REPAIR_PACKAGE_ID,
        "source_p35_comment": SOURCE_P35_COMMENT,
        "source_p36_comment": SOURCE_P36_COMMENT,
        "oracle": "O-AUTH + exact CanonicalRef/contract-binding checker",
        "missing_exact_acceptance_fact": {
            "accepted": missing.accepted,
            "code": missing.code,
        },
        "mutable_unpinned_trust_ref": {
            "accepted": mutable.accepted,
            "code": mutable.code,
        },
        "wrong_acceptance_contract_identity": wrong_contract_results,
        "exact_configured_contract_identity": exact_contract_results,
        "metrics": metrics,
        "passed": (
            all(value == 0 for value in metrics.values())
            and all(exact_contract_results.values())
        ),
    }


def generate(output_dir: Path, result_revision: str, package_ref: str = base.PACKAGE_REF) -> dict:
    # The original compiler predates N3 and keyed fake contract sources by stable id.
    # Patch only its in-memory fixture resolver so all base evidence executes against
    # the repaired exact-binding production contract without rewriting old evidence history.
    base._resolver = _exact_resolver
    manifest = base.generate(output_dir, result_revision, package_ref)

    repair = _repair_closure()
    if not repair["passed"]:
        raise RuntimeError("CP-I04 P36-02 repair evidence failed")

    repair_path = output_dir / "p36-repair-closure.json"
    base._write_json(repair_path, repair)
    manifest["repair"] = {
        "repair_package_id": REPAIR_PACKAGE_ID,
        "source_p35_comment": SOURCE_P35_COMMENT,
        "source_p36_comment": SOURCE_P36_COMMENT,
    }
    manifest["evidence"]["CP-I04-P36-REPAIR-CLOSURE"] = repair_path.name
    manifest["metrics"].update(repair["metrics"])
    if any(manifest["metrics"].values()):
        raise RuntimeError("CP-I04 P36-02 zero-tolerance metric failure")
    if "test_cp_i04_p36_matrix.CpI04P36MandatoryMatrixTests" not in manifest["test_identities"]:
        manifest["test_identities"].append(
            "test_cp_i04_p36_matrix.CpI04P36MandatoryMatrixTests"
        )

    manifest["file_digests"][repair_path.name] = base._sha256(repair_path)
    payload_digest = "sha256:" + hashlib.sha256(
        "\n".join(
            f"{name}={digest}"
            for name, digest in sorted(manifest["file_digests"].items())
        ).encode("utf-8")
    ).hexdigest()
    manifest["artifact"]["payload_digest"] = payload_digest
    manifest["artifact"]["binding_note"] = (
        "GitHub assigns artifact id/digest after upload; durable P36-02 return binds "
        "those values externally without self-digest recursion."
    )
    base._write_json(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--package-ref", default=base.PACKAGE_REF)
    parser.add_argument("--output-dir", default="artifacts/cp-i04")
    args = parser.parse_args()
    generate(Path(args.output_dir), args.result_revision, args.package_ref)


if __name__ == "__main__":
    main()
