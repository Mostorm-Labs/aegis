"""Deterministic CP-I01 evidence-manifest builder."""

from __future__ import annotations

import platform
from typing import Iterable

import catalogs
import completeness_oracle
import qualification
from tools.aegis_control.canonical import canonical_digest


TASK_ID = "CP-I01-P31-01"
P20_BASE_REF = "db83168e4086e47a7f431acf289006e4f25b8ffd"
P20_REPAIR_BLOB = "5bed0ce054ead0902bc8c72601814b2f63525067"

_CANONICAL_GOLDEN_VECTORS = {
    "ordered_object": {"z": 1, "a": "雪"},
    "numbers": [0, 1, -1, 1.5, 1e-6, 1e-7, 1e20, 1e21],
    "strings": ['quote"', "slash\\", "line\n"],
}


def build_manifest(result_revision: str, package_ref: str, commands: Iterable[str]) -> dict[str, object]:
    qualification_result = qualification.run_qualification()
    obligations = completeness_oracle.expected_obligations()
    completeness = completeness_oracle.validate_obligation_set(obligations, {o["id"] for o in obligations})
    if not completeness.ok:
        raise AssertionError(f"accepted obligation set failed completeness: {completeness.errors}")
    return {
        "schema_version": "cp-i01-evidence-v0.1",
        "task_id": TASK_ID,
        "result_revision": result_revision,
        "package_ref": package_ref,
        "p20_sources": {"verification_head": P20_BASE_REF, "repair_blob": P20_REPAIR_BLOB},
        "commands": list(commands),
        "python_runtime": platform.python_version(),
        "fixture_catalog_digest": catalogs.fixture_catalog_digest(),
        "mutant_catalog_digest": catalogs.mutant_catalog_digest(),
        "canonical_golden_vector_digest": canonical_digest(_CANONICAL_GOLDEN_VECTORS),
        "deterministic_seed_list": [],
        "qualification": qualification_result,
        "completeness": {"coverage_mode": "REVIEW_DECLARED", "obligation_total": len(obligations), "result": "PASS"},
        "snapshot_mutant_provenance": qualification.snapshot_mutant_provenance(),
        "m20_provenance": qualification.m20_provenance(),
        "evidence_families": ["CPV-E-SPEC", "CPV-E-COMPLETENESS", "CPV-E-VERIFIER-QUALIFICATION", "CPV-E-OBLIGATIONS"],
        "claims_not_made": ["CPV-E-D0-CONFORMANCE", "P34_GATE_PASS"],
    }
