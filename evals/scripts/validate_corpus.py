#!/usr/bin/env python3
"""Validate the Aegis v0.1 seed evaluation corpus using only stdlib."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = ROOT / "evals" / "cases"

EXPECTED_COUNTS = {
    "routing": 10,
    "authority": 8,
    "defect": 6,
    "gate": 6,
}

ALLOWED_CATEGORIES = set(EXPECTED_COUNTS)
ALLOWED_SEVERITIES = {"normal", "high", "critical"}
ALLOWED_ORIGINS = {"synthetic", "dogfood", "incident"}
ALLOWED_DEFECTS = {
    "IMPLEMENTATION_DEFECT",
    "SPEC_DEFECT",
    "AUTHORITY_CONFLICT",
    "MISSING_CONTRACT",
    "TEST_DEFECT",
    "EVIDENCE_GAP",
    "ENVIRONMENT_DEFECT",
    "DEPENDENCY_BLOCKER",
    "UNRESOLVED_DECISION",
}
ALLOWED_GATE_VERDICTS = {
    "PASS",
    "PASS_WITH_FINDINGS",
    "BLOCKED_IMPLEMENTATION",
    "BLOCKED_AUTHORITY",
    "BLOCKED_EVIDENCE",
    "BLOCKED_ENVIRONMENT",
}
ALLOWED_STAGES = {
    "P00", "P01", "P02", "P03",
    "P10", "P11", "P12", "P13", "P14", "P15", "P16", "P17", "P18",
    "P20", "P21", "P22", "P23", "P24",
    "P30", "P31", "P32", "P33", "P34", "P35", "P36",
}
ID_RE = re.compile(r"^(routing|authority|defect|gate)-([0-9]{3})$")

REQUIRED_CASE_KEYS = {
    "id", "category", "title", "severity", "origin", "input", "expected", "tags"
}
REQUIRED_INPUT_KEYS = {"prompt", "context"}
REQUIRED_EXPECTED_KEYS = {
    "status",
    "earliest_untrusted_layer",
    "start_stage",
    "required_stages",
    "forbidden_stages",
    "required_findings",
    "forbidden_findings",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_string_list(errors: list[str], case_id: str, field: str, value: object) -> None:
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        fail(errors, f"{case_id}: {field} must be a list of strings")


def validate_case(errors: list[str], case: object, source: Path) -> str | None:
    if not isinstance(case, dict):
        fail(errors, f"{source}: case entry must be an object")
        return None

    missing = REQUIRED_CASE_KEYS - case.keys()
    if missing:
        fail(errors, f"{source}: case missing keys {sorted(missing)}")
        return None

    case_id = case.get("id")
    if not isinstance(case_id, str) or not ID_RE.match(case_id):
        fail(errors, f"{source}: invalid id {case_id!r}")
        return None

    category = case.get("category")
    if category not in ALLOWED_CATEGORIES:
        fail(errors, f"{case_id}: invalid category {category!r}")
    elif not case_id.startswith(f"{category}-"):
        fail(errors, f"{case_id}: id prefix does not match category {category}")

    if case.get("severity") not in ALLOWED_SEVERITIES:
        fail(errors, f"{case_id}: invalid severity {case.get('severity')!r}")
    if case.get("origin") not in ALLOWED_ORIGINS:
        fail(errors, f"{case_id}: invalid origin {case.get('origin')!r}")
    if not isinstance(case.get("title"), str) or len(case["title"].strip()) < 3:
        fail(errors, f"{case_id}: title must be a non-empty string")

    input_obj = case.get("input")
    if not isinstance(input_obj, dict):
        fail(errors, f"{case_id}: input must be an object")
    else:
        missing_input = REQUIRED_INPUT_KEYS - input_obj.keys()
        if missing_input:
            fail(errors, f"{case_id}: input missing keys {sorted(missing_input)}")
        if not isinstance(input_obj.get("prompt"), str) or len(input_obj.get("prompt", "").strip()) < 3:
            fail(errors, f"{case_id}: input.prompt must be a non-empty string")
        validate_string_list(errors, case_id, "input.context", input_obj.get("context"))

    expected = case.get("expected")
    if not isinstance(expected, dict):
        fail(errors, f"{case_id}: expected must be an object")
    else:
        missing_expected = REQUIRED_EXPECTED_KEYS - expected.keys()
        if missing_expected:
            fail(errors, f"{case_id}: expected missing keys {sorted(missing_expected)}")

        start_stage = expected.get("start_stage")
        if start_stage is not None and start_stage not in ALLOWED_STAGES:
            fail(errors, f"{case_id}: invalid start_stage {start_stage!r}")

        for field in ("required_stages", "forbidden_stages"):
            value = expected.get(field)
            validate_string_list(errors, case_id, f"expected.{field}", value)
            if isinstance(value, list):
                invalid = [stage for stage in value if stage not in ALLOWED_STAGES]
                if invalid:
                    fail(errors, f"{case_id}: invalid stages in {field}: {invalid}")

        for field in (
            "authority_classification",
            "required_findings",
            "forbidden_findings",
        ):
            if field in expected:
                validate_string_list(errors, case_id, f"expected.{field}", expected.get(field))

        defect = expected.get("defect_classification")
        if defect is not None and defect not in ALLOWED_DEFECTS:
            fail(errors, f"{case_id}: invalid defect_classification {defect!r}")

        gate = expected.get("gate_verdict")
        if gate is not None and gate not in ALLOWED_GATE_VERDICTS:
            fail(errors, f"{case_id}: invalid gate_verdict {gate!r}")
        if category == "gate" and gate is None:
            fail(errors, f"{case_id}: gate cases must define gate_verdict")
        if category == "defect" and defect is None:
            fail(errors, f"{case_id}: defect cases must define defect_classification")

    validate_string_list(errors, case_id, "tags", case.get("tags"))
    return case_id


def main() -> int:
    errors: list[str] = []
    seen_ids: set[str] = set()
    counts: Counter[str] = Counter()

    files = sorted(CASES_DIR.glob("*.json"))
    if not files:
        print(f"ERROR: no case files found under {CASES_DIR}", file=sys.stderr)
        return 1

    total = 0
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(errors, f"{path}: cannot parse JSON: {exc}")
            continue

        if not isinstance(payload, list):
            fail(errors, f"{path}: top-level JSON value must be an array")
            continue

        for case in payload:
            total += 1
            case_id = validate_case(errors, case, path)
            if case_id is None:
                continue
            if case_id in seen_ids:
                fail(errors, f"duplicate case id: {case_id}")
            seen_ids.add(case_id)
            if isinstance(case, dict) and case.get("category") in ALLOWED_CATEGORIES:
                counts[case["category"]] += 1

    if total != sum(EXPECTED_COUNTS.values()):
        fail(errors, f"expected 30 cases, found {total}")

    for category, expected_count in EXPECTED_COUNTS.items():
        actual = counts[category]
        if actual != expected_count:
            fail(errors, f"{category}: expected {expected_count} cases, found {actual}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAILED: {len(errors)} validation error(s)", file=sys.stderr)
        return 1

    summary = ", ".join(f"{name}={counts[name]}" for name in sorted(EXPECTED_COUNTS))
    print(f"PASS: {total} cases validated ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
