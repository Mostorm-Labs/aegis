#!/usr/bin/env python3
"""Validate the Aegis seed corpus while allowing durable dogfood/incident growth."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = ROOT / "evals" / "cases"

SEED_COUNTS = {"routing": 10, "authority": 8, "defect": 6, "gate": 6}
ALLOWED_CATEGORIES = set(SEED_COUNTS)
ALLOWED_SEVERITIES = {"normal", "high", "critical"}
ALLOWED_ORIGINS = {"synthetic", "dogfood", "incident"}
ALLOWED_DEFECTS = {
    "IMPLEMENTATION_DEFECT", "SPEC_DEFECT", "AUTHORITY_CONFLICT", "MISSING_CONTRACT",
    "TEST_DEFECT", "EVIDENCE_GAP", "ENVIRONMENT_DEFECT", "DEPENDENCY_BLOCKER",
    "UNRESOLVED_DECISION",
}
ALLOWED_GATE_VERDICTS = {
    "PASS", "PASS_WITH_FINDINGS", "BLOCKED_IMPLEMENTATION", "BLOCKED_AUTHORITY",
    "BLOCKED_EVIDENCE", "BLOCKED_ENVIRONMENT",
}
ALLOWED_STAGES = {
    "P00", "P01", "P02", "P03", "P10", "P11", "P12", "P13", "P14", "P15", "P16",
    "P17", "P18", "P20", "P21", "P22", "P23", "P24", "P30", "P31", "P32", "P33",
    "P34", "P35", "P36",
}
ID_RE = re.compile(r"^(routing|authority|defect|gate)-([0-9]{3})$")
REQUIRED_CASE_KEYS = {"id", "category", "title", "severity", "origin", "input", "expected", "tags"}
REQUIRED_EXPECTED_KEYS = {
    "status", "earliest_untrusted_layer", "start_stage", "required_stages", "forbidden_stages",
    "required_findings", "forbidden_findings",
}


def _seed_ids() -> set[str]:
    return {
        f"{category}-{index:03d}"
        for category, count in SEED_COUNTS.items()
        for index in range(1, count + 1)
    }


def _is_string_list(value) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def validate_cases(cases: list[dict]) -> tuple[list[str], dict]:
    errors: list[str] = []
    seen: set[str] = set()
    counts = Counter()

    for case in cases:
        if not isinstance(case, dict):
            errors.append("case entry must be an object")
            continue
        missing = REQUIRED_CASE_KEYS - case.keys()
        if missing:
            errors.append(f"case missing keys {sorted(missing)}")
            continue

        case_id = case.get("id")
        match = ID_RE.match(case_id) if isinstance(case_id, str) else None
        if not match:
            errors.append(f"invalid id {case_id!r}")
            continue
        if case_id in seen:
            errors.append(f"duplicate case id: {case_id}")
        seen.add(case_id)

        category = case.get("category")
        if category not in ALLOWED_CATEGORIES:
            errors.append(f"{case_id}: invalid category {category!r}")
        elif not case_id.startswith(f"{category}-"):
            errors.append(f"{case_id}: id prefix does not match category {category}")
        else:
            counts[category] += 1

        if case.get("severity") not in ALLOWED_SEVERITIES:
            errors.append(f"{case_id}: invalid severity")
        if case.get("origin") not in ALLOWED_ORIGINS:
            errors.append(f"{case_id}: invalid origin")

        input_obj = case.get("input")
        if not isinstance(input_obj, dict) or not isinstance(input_obj.get("prompt"), str) or not _is_string_list(input_obj.get("context")):
            errors.append(f"{case_id}: invalid input contract")

        expected = case.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{case_id}: expected must be an object")
            continue
        missing_expected = REQUIRED_EXPECTED_KEYS - expected.keys()
        if missing_expected:
            errors.append(f"{case_id}: expected missing keys {sorted(missing_expected)}")

        start_stage = expected.get("start_stage")
        if start_stage is not None and start_stage not in ALLOWED_STAGES:
            errors.append(f"{case_id}: invalid start_stage {start_stage!r}")
        for field in ("required_stages", "forbidden_stages"):
            value = expected.get(field)
            if not _is_string_list(value):
                errors.append(f"{case_id}: expected.{field} must be a list of strings")
            elif any(stage not in ALLOWED_STAGES for stage in value):
                errors.append(f"{case_id}: invalid stage in {field}")
        for field in ("authority_classification", "required_findings", "forbidden_findings"):
            if field in expected and not _is_string_list(expected.get(field)):
                errors.append(f"{case_id}: expected.{field} must be a list of strings")

        defect = expected.get("defect_classification")
        if defect is not None and defect not in ALLOWED_DEFECTS:
            errors.append(f"{case_id}: invalid defect_classification {defect!r}")
        gate = expected.get("gate_verdict")
        if gate is not None and gate not in ALLOWED_GATE_VERDICTS:
            errors.append(f"{case_id}: invalid gate_verdict {gate!r}")
        if category == "gate" and gate is None:
            errors.append(f"{case_id}: gate cases must define gate_verdict")
        if category == "defect" and defect is None:
            errors.append(f"{case_id}: defect cases must define defect_classification")
        if not _is_string_list(case.get("tags")):
            errors.append(f"{case_id}: tags must be a list of strings")

    missing_seed = sorted(_seed_ids() - seen)
    for case_id in missing_seed:
        errors.append(f"missing required seed case: {case_id}")

    summary = {"total": len(cases), **{name: counts[name] for name in sorted(SEED_COUNTS)}}
    return errors, summary


def load_cases(cases_dir: Path = CASES_DIR) -> tuple[list[dict], list[str]]:
    cases: list[dict] = []
    errors: list[str] = []
    for path in sorted(cases_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: cannot parse JSON: {exc}")
            continue
        if not isinstance(payload, list):
            errors.append(f"{path}: top-level JSON value must be an array")
            continue
        cases.extend(payload)
    if not cases and not errors:
        errors.append(f"no case files found under {cases_dir}")
    return cases, errors


def main() -> int:
    cases, load_errors = load_cases()
    validation_errors, summary = validate_cases(cases) if cases else ([], {"total": 0})
    errors = load_errors + validation_errors
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAILED: {len(errors)} validation error(s)", file=sys.stderr)
        return 1
    counts = ", ".join(f"{name}={summary[name]}" for name in sorted(SEED_COUNTS))
    print(f"PASS: {summary['total']} cases validated ({counts}; seed=30, extensible=true)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
