from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .model import load_skillset
from .routing import evaluate_terminal_trace
from .distribution import evaluate_catalog_snapshot

REQUIRED_CASE_IDS = (
    "09-01-direct-specialist",
    "09-01-ambiguous-router",
    "09-01-upstream-blocker-reroute",
    "09-01-composite-fallback",
)
VALID_CATALOG_MODES = {"full_specialist", "composite_only"}


@dataclass(frozen=True)
class InstalledPlatformCaseResult:
    case_id: str
    verdict: str
    violations: tuple[str, ...]
    evidence_gaps: tuple[str, ...]
    evidence_ref: str | None
    catalog_state: str | None = None


@dataclass(frozen=True)
class InstalledPlatformGateEvaluation:
    verdict: str
    cases: tuple[InstalledPlatformCaseResult, ...]
    errors: tuple[str, ...]


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_evidence_path(root: Path, ref: str) -> Path:
    path = Path(ref)
    return path if path.is_absolute() else root / path


def _load_case(root: Path, source: dict) -> tuple[dict | None, str | None]:
    rel = source.get("path")
    case_id = source.get("id")
    if not rel or not case_id:
        return None, "case source requires path and id"
    path = root / rel
    if not path.is_file():
        return None, f"case source missing: {rel}"
    try:
        corpus = _load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"case source unreadable: {rel}: {exc}"
    if not isinstance(corpus, list):
        return None, f"case source must be a list: {rel}"
    matches = [case for case in corpus if case.get("id") == case_id]
    if len(matches) != 1:
        return None, f"case source id must resolve exactly once: {rel}#{case_id}"
    return matches[0], None


def evaluate_installed_platform_rerun(
    root: Path,
    manifest_path: Path | None = None,
) -> InstalledPlatformGateEvaluation:
    root = Path(root)
    manifest_path = Path(manifest_path or root / "skillset/dogfood/installed-platform-rerun-v0.2.1.json")
    errors: list[str] = []
    results: list[InstalledPlatformCaseResult] = []

    if not manifest_path.is_file():
        return InstalledPlatformGateEvaluation(
            "BLOCKED_EVIDENCE", (), (f"rerun manifest missing: {manifest_path}",)
        )
    try:
        manifest = _load_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return InstalledPlatformGateEvaluation(
            "BLOCKED_EVIDENCE", (), (f"rerun manifest unreadable: {exc}",)
        )

    schema = manifest.get("schema_version")
    if schema not in {"0.2", "0.2.1"}:
        errors.append("rerun manifest schema_version must be 0.2 or 0.2.1")
    if manifest.get("oracle") != "terminal_trace_v0.2":
        errors.append("rerun manifest oracle must be terminal_trace_v0.2")
    cases = manifest.get("cases")
    if not isinstance(cases, list):
        return InstalledPlatformGateEvaluation(
            "BLOCKED_EVIDENCE", (), tuple(errors + ["rerun manifest cases must be a list"])
        )

    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        errors.append("rerun manifest contains duplicate case ids")
    if set(ids) != set(REQUIRED_CASE_IDS):
        errors.append("rerun manifest must contain exactly the four protected Task 6 cases")

    if schema == "0.2.1":
        return _evaluate_v021(root, manifest, tuple(errors))

    config = load_skillset(root)
    for entry in cases:
        case_id = entry.get("id") or "<missing>"
        gaps: list[str] = []
        violations: tuple[str, ...] = ()
        evidence_ref = entry.get("evidence_ref")
        required_catalog_mode = entry.get("required_catalog_mode")
        if required_catalog_mode not in VALID_CATALOG_MODES:
            errors.append(f"{case_id}: invalid required_catalog_mode {required_catalog_mode}")

        case, case_error = _load_case(root, entry.get("case_source") or {})
        if case_error:
            errors.append(f"{case_id}: {case_error}")
            results.append(
                InstalledPlatformCaseResult(
                    case_id,
                    "BLOCKED_EVIDENCE",
                    (),
                    ("canonical routing case",),
                    evidence_ref,
                )
            )
            continue

        if not evidence_ref:
            results.append(
                InstalledPlatformCaseResult(
                    case_id,
                    "BLOCKED_EVIDENCE",
                    (),
                    ("fresh installed-platform evidence",),
                    None,
                )
            )
            continue

        evidence_path = _resolve_evidence_path(root, evidence_ref)
        if not evidence_path.is_file():
            results.append(
                InstalledPlatformCaseResult(
                    case_id,
                    "BLOCKED_EVIDENCE",
                    (),
                    (f"evidence artifact: {evidence_ref}",),
                    evidence_ref,
                )
            )
            continue

        try:
            evidence = _load_json(evidence_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{case_id}: evidence unreadable: {exc}")
            results.append(
                InstalledPlatformCaseResult(
                    case_id,
                    "BLOCKED_EVIDENCE",
                    (),
                    ("readable evidence artifact",),
                    evidence_ref,
                )
            )
            continue

        if evidence.get("schema_version") != "0.2":
            gaps.append("evidence schema_version 0.2")
        if evidence.get("case_id") != case_id:
            gaps.append("matching evidence case_id")
        if evidence.get("fresh_platform_event") is not True:
            gaps.append("fresh platform event")
        if evidence.get("complete_response_captured") is not True:
            gaps.append("complete response capture")
        if not evidence.get("platform_event_id"):
            gaps.append("platform event id")
        environment = evidence.get("environment")
        if not isinstance(environment, dict):
            gaps.append("platform environment")
        elif environment.get("catalog_mode") != required_catalog_mode:
            gaps.append(f"catalog mode: {required_catalog_mode}")

        trace = evidence.get("trace")
        if not isinstance(trace, dict):
            gaps.append("normalized terminal trace")
            oracle_verdict = "BLOCKED_EVIDENCE"
            oracle_gaps: tuple[str, ...] = ()
        else:
            oracle = evaluate_terminal_trace(case, trace, config)
            oracle_verdict = oracle.verdict
            violations = oracle.violations
            oracle_gaps = oracle.evidence_gaps

        combined_gaps = tuple(dict.fromkeys([*gaps, *oracle_gaps]))
        if oracle_verdict == "FAIL":
            verdict = "FAIL"
        elif combined_gaps:
            verdict = "BLOCKED_EVIDENCE"
        else:
            verdict = "PASS"
        results.append(
            InstalledPlatformCaseResult(
                case_id, verdict, violations, combined_gaps, evidence_ref
            )
        )

    if any(result.verdict == "FAIL" for result in results):
        verdict = "FAIL"
    elif (
        not errors
        and len(results) == len(REQUIRED_CASE_IDS)
        and all(result.verdict == "PASS" for result in results)
    ):
        verdict = "PASS"
    else:
        verdict = "BLOCKED_EVIDENCE"
    return InstalledPlatformGateEvaluation(verdict, tuple(results), tuple(errors))


def _evaluate_v021(root: Path, manifest: dict, initial_errors: tuple[str, ...]) -> InstalledPlatformGateEvaluation:
    errors = list(initial_errors)
    results = []
    cases = manifest.get("cases", [])
    ids = [entry.get("id") for entry in cases]
    if len(ids) != len(set(ids)):
        errors.append("rerun manifest contains duplicate case ids")
    if set(ids) != set(REQUIRED_CASE_IDS):
        errors.append("rerun manifest must contain exactly the four protected Task 6 cases")
    config = load_skillset(root)
    required_trace = ("terminal", "invocations", "final_answer_owner", "genuine_ambiguity", "earlier_blocker_conclusively_established", "ownership_edges", "handoff_edges", "forbidden_downstream_substantive_execution", "primary_substantive_result_emitted")
    for entry in cases:
        case_id = entry.get("id") or "<missing>"
        case, case_error = _load_case(root, entry.get("case_source") or {})
        cref, bref = entry.get("catalog_evidence_ref"), entry.get("behavior_evidence_ref")
        if case_error:
            errors.append(f"{case_id}: {case_error}")
            results.append(InstalledPlatformCaseResult(case_id, "BLOCKED_EVIDENCE", (), ("canonical routing case",), bref, None)); continue
        if not cref:
            results.append(InstalledPlatformCaseResult(case_id, "BLOCKED_EVIDENCE", (), ("catalog_evidence_ref",), bref, None)); continue
        cp = _resolve_evidence_path(root, cref)
        if not cp.is_file():
            results.append(InstalledPlatformCaseResult(case_id, "BLOCKED_EVIDENCE", (), (f"catalog evidence artifact: {cref}",), bref, None)); continue
        try: catalog = evaluate_catalog_snapshot(root, _load_json(cp))
        except (OSError, json.JSONDecodeError) as exc:
            results.append(InstalledPlatformCaseResult(case_id, "BLOCKED_EVIDENCE", (), (f"readable catalog evidence: {exc}",), bref, None)); continue
        if catalog.verdict != "PASS":
            results.append(InstalledPlatformCaseResult(case_id, catalog.verdict, (), catalog.evidence_gaps or catalog.errors, bref, catalog.catalog_state)); continue
        if catalog.catalog_state != entry.get("required_catalog_state"):
            results.append(InstalledPlatformCaseResult(case_id, "BLOCKED_ENVIRONMENT", (), ("required catalog state",), bref, catalog.catalog_state)); continue
        if not bref:
            results.append(InstalledPlatformCaseResult(case_id, "BLOCKED_EVIDENCE", (), ("behavior_evidence_ref",), None, catalog.catalog_state)); continue
        bp = _resolve_evidence_path(root, bref)
        if not bp.is_file():
            results.append(InstalledPlatformCaseResult(case_id, "BLOCKED_EVIDENCE", (), (f"behavior evidence artifact: {bref}",), bref, catalog.catalog_state)); continue
        try: behavior = _load_json(bp)
        except (OSError, json.JSONDecodeError) as exc:
            results.append(InstalledPlatformCaseResult(case_id, "BLOCKED_EVIDENCE", (), (f"readable behavior evidence: {exc}",), bref, catalog.catalog_state)); continue
        gaps = []
        if behavior.get("schema_version") != "0.2": gaps.append("behavior evidence schema_version 0.2")
        if behavior.get("case_id") != case_id: gaps.append("matching behavior evidence case_id")
        if behavior.get("fresh_platform_event") is not True: gaps.append("fresh platform event")
        if behavior.get("complete_response_captured") is not True: gaps.append("complete response capture")
        if not behavior.get("platform_event_id"): gaps.append("platform event id")
        trace = behavior.get("trace")
        if not isinstance(trace, dict): gaps.append("normalized terminal trace"); trace = {}
        else:
            for key in required_trace:
                if key not in trace: gaps.append(f"trace.{key}")
            for key, expected in (("mode", catalog.runtime_mode), ("specialist_availability", catalog.specialist_availability)):
                if key in trace and trace[key] != expected: gaps.append(f"trace/catalog {key} conflict")
        if gaps:
            results.append(InstalledPlatformCaseResult(case_id, "BLOCKED_EVIDENCE", (), tuple(gaps), bref, catalog.catalog_state)); continue
        derived = dict(trace); derived["mode"] = catalog.runtime_mode; derived["specialist_availability"] = catalog.specialist_availability
        oracle = evaluate_terminal_trace(case, derived, config)
        verdict = oracle.verdict
        results.append(InstalledPlatformCaseResult(case_id, verdict, oracle.violations, oracle.evidence_gaps, bref, catalog.catalog_state))
    verdict = "FAIL" if any(r.verdict == "FAIL" for r in results) else "BLOCKED_ENVIRONMENT" if any(r.verdict == "BLOCKED_ENVIRONMENT" for r in results) else "BLOCKED_EVIDENCE" if any(r.verdict == "BLOCKED_EVIDENCE" for r in results) else "PASS" if len(results) == len(REQUIRED_CASE_IDS) and not errors else "BLOCKED_EVIDENCE"
    return InstalledPlatformGateEvaluation(verdict, tuple(results), tuple(errors))
