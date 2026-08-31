"""Independent REVIEW_DECLARED obligation completeness oracle (O-COMPLETE)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


BASE_SOURCE = "docs/control-plane-productization-verification-v0.2.md"
REPAIR_SOURCE = "docs/control-plane-productization-verification-v0.2-p21-repair.md"


@dataclass(frozen=True)
class CompletenessResult:
    ok: bool
    errors: tuple[dict[str, str], ...]

    @property
    def error_codes(self) -> set[str]:
        return {error["code"] for error in self.errors}


def expected_obligations() -> tuple[dict[str, str], ...]:
    obligations = []
    for index in range(1, 20):
        claim_id = f"CPV-C{index:02d}"
        source = BASE_SOURCE if index <= 14 else REPAIR_SOURCE
        obligations.append({"id": f"CPV-O-{claim_id}", "kind": "CLAIM", "source_key": f"{source}#{claim_id}"})
    obligations.append({"id": "CPV-O-COVERAGE-COMPLETENESS", "kind": "COVERAGE_COMPLETENESS", "source_key": f"{BASE_SOURCE}#CoverageBasis.mode=REVIEW_DECLARED"})
    return tuple(obligations)


def validate_obligation_set(supplied: Iterable[Mapping[str, str]], evaluated_ids: set[str] | None) -> CompletenessResult:
    expected = {item["id"]: item for item in expected_obligations()}
    items = [dict(item) for item in supplied]
    errors: list[dict[str, str]] = []
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        identifier = item.get("id", "")
        if identifier in seen:
            duplicates.add(identifier)
        seen.add(identifier)
    for identifier in sorted(duplicates):
        errors.append({"code": "DUPLICATE_OBLIGATION", "id": identifier})
    supplied_ids = {item.get("id", "") for item in items}
    for identifier in sorted(set(expected) - supplied_ids):
        code = "MISSING_COVERAGE_COMPLETENESS" if identifier == "CPV-O-COVERAGE-COMPLETENESS" else "MISSING_OBLIGATION"
        errors.append({"code": code, "id": identifier})
    for identifier in sorted(supplied_ids - set(expected)):
        errors.append({"code": "EXTRA_OBLIGATION", "id": identifier})
    for item in items:
        identifier = item.get("id", "")
        if identifier in expected and item.get("source_key") != expected[identifier]["source_key"]:
            errors.append({"code": "SOURCE_KEY_MISMATCH", "id": identifier})
        if identifier in expected and item.get("kind") != expected[identifier]["kind"]:
            errors.append({"code": "OBLIGATION_KIND_MISMATCH", "id": identifier})
    coverage_count = sum(item.get("kind") == "COVERAGE_COMPLETENESS" for item in items)
    if coverage_count != 1 and not any(e["code"] == "MISSING_COVERAGE_COMPLETENESS" for e in errors):
        errors.append({"code": "COVERAGE_COMPLETENESS_CARDINALITY", "id": str(coverage_count)})
    if evaluated_ids is not None and evaluated_ids != set(expected):
        errors.append({"code": "EVALUATION_SET_MISMATCH", "id": "evaluation-set"})
    return CompletenessResult(ok=not errors, errors=tuple(errors))
