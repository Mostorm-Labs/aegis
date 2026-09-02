from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from tests.control_plane.cp_i09_contract import (
    ACCELERATED_REPLAY,
    BenchmarkContractError,
    CostEvent,
    MONTHLY_NOT_CLAIMED,
    REAL_CLOCK,
    SevenDayCostEvidence,
    validate_latency_targets,
    validate_w7d,
)

PACKAGE_ID = "CP-I09-P31-01"
PACKAGE_REF = "9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385"
TASK_ANCHOR = "ac2bcf19acf46a749761ed455ecf0a995069700d"
SOURCE_CP_I08_P34 = "5079977191"

R0_FILES = (
    "r0-workload-manifest.json",
    "r0-raw-timeseries.json",
    "r0-latency-histograms.json",
    "r0-performance.json",
)
S0_FILES = (
    "s0-workload-manifest.json",
    "s0-raw-timeseries.json",
    "s0-stress.json",
)
W7D_FILES = (
    "w7d-workload-manifest.json",
    "w7d-hourly-slices.json",
    "w7d-raw-cost-events.json",
    "w7d-cost-model.json",
    "w7d-cost.json",
)


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _copy_exact(source: Path, target: Path, files: tuple[str, ...]) -> None:
    actual = {path.name for path in source.glob("*.json")}
    expected = set(files)
    if actual != expected:
        raise SystemExit(f"unexpected CP-I09 split artifact set at {source}: {sorted(actual)}")
    for name in files:
        shutil.copyfile(source / name, target / name)


def _family_load_violation(workload: dict) -> int:
    measurement = workload.get("measurement", {})
    families = measurement.get("families", {})
    if not families:
        return 1
    for family in families.values():
        if family.get("scheduled_count") != family.get("planned_count"):
            return 1
        if int(family.get("completed_count", -1)) + int(family.get("failed_count", -1)) != int(family.get("scheduled_count", -2)):
            return 1
        if int(family.get("failed_count", 1)) != 0:
            return 1
        if float(family.get("schedule_window_overrun_seconds", 9999.0)) > 1.0:
            return 1
    return 0


def _latency_target_miss(r0: dict) -> int:
    try:
        validate_latency_targets(r0.get("latency_quantiles_ms", {}))
    except BenchmarkContractError:
        return 1
    return 0


def _recompute_cost(root: Path) -> tuple[int, float]:
    workload = _read(root / "w7d-workload-manifest.json")
    hourly = _read(root / "w7d-hourly-slices.json")
    raw = _read(root / "w7d-raw-cost-events.json")
    result = _read(root / "w7d-cost.json")
    rows = raw.get("rows", [])
    events = tuple(
        CostEvent(
            hour=int(row["hour"]),
            unit=row["unit"],
            classification=row["classification"],
            count=int(row["count"]),
        )
        for row in rows
    )
    evidence = SevenDayCostEvidence(
        measurement_class=workload.get("measurement_class"),
        hourly_slices=tuple(int(row["hour"]) for row in hourly.get("rows", [])),
        raw_events=events,
        reported_overhead_cost=float(result.get("reported_overhead_cost", -1)),
        reported_substantive_cost=float(result.get("reported_substantive_provider_cost", -1)),
        reported_ratio=float(result.get("reported_ratio", -1)),
    )
    try:
        recomputed = validate_w7d(evidence)
    except (BenchmarkContractError, KeyError, TypeError, ValueError):
        return 1, -1.0
    return 0, float(recomputed["independent_ratio"])


def compile_evidence(
    *,
    result_revision: str,
    workflow_run: str,
    r0_dir: Path,
    s0_dir: Path,
    w7d_dir: Path,
    output_dir: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    _copy_exact(r0_dir, output_dir, R0_FILES)
    _copy_exact(s0_dir, output_dir, S0_FILES)
    _copy_exact(w7d_dir, output_dir, W7D_FILES)

    r0_workload = _read(output_dir / "r0-workload-manifest.json")
    r0 = _read(output_dir / "r0-performance.json")
    s0_workload = _read(output_dir / "s0-workload-manifest.json")
    s0 = _read(output_dir / "s0-stress.json")
    w7d_workload = _read(output_dir / "w7d-workload-manifest.json")
    w7d = _read(output_dir / "w7d-cost.json")

    for label, payload in (("r0", r0), ("s0", s0), ("w7d", w7d)):
        if payload.get("result_revision") != result_revision:
            raise SystemExit(f"CP-I09 {label} result revision mismatch")
    if r0_workload.get("package_ref") != PACKAGE_REF or s0.get("package_ref") != PACKAGE_REF or w7d_workload.get("package_ref") != PACKAGE_REF:
        raise SystemExit("CP-I09 split artifact package provenance mismatch")
    if r0_workload.get("task_anchor") != {"revision": TASK_ANCHOR, "relation": "ancestor"} or s0.get("task_anchor") != {"revision": TASK_ANCHOR, "relation": "ancestor"} or w7d_workload.get("task_anchor") != {"revision": TASK_ANCHOR, "relation": "ancestor"}:
        raise SystemExit("CP-I09 task-anchor provenance mismatch")

    cost_recompute_mismatch, independent_ratio = _recompute_cost(output_dir)
    r0_families = r0_workload.get("measurement", {}).get("families", {})
    s0_families = s0.get("families", {})

    r0_failed_ops = sum(int(value.get("failed_count", 1)) for value in r0_families.values()) if r0_families else 1
    s0_failed_ops = sum(int(value.get("failed_count", 1)) for value in s0_families.values()) if s0_families else 1
    observed_bursts = r0.get("observed_bursts", {})
    r0_burst_missing = int(
        observed_bursts.get("api_200_rps_wall_seconds", 0) < 60
        or observed_bursts.get("mutation_100_rps_wall_seconds", 0) < 30
        or observed_bursts.get("provider_callbacks_per_minute", 0) < 1000
    )

    metrics = {
        "r0_invariant_failures": r0_failed_ops,
        "r0_accidental_semantic_duplicates": int(r0.get("accidental_semantic_duplicates", 1)),
        "r0_wall_clock_shortfall": int(r0.get("clock_class") != REAL_CLOCK or float(r0.get("warmup_wall_seconds", 0)) < 600 or float(r0.get("measurement_wall_seconds", 0)) < 1800),
        "r0_required_load_or_burst_missing": int(_family_load_violation(r0_workload) or r0_burst_missing),
        "r0_latency_target_miss": _latency_target_miss(r0),
        "s0_invariant_failures": s0_failed_ops,
        "s0_accidental_semantic_duplicates": int(s0.get("accidental_semantic_duplicates", 1)),
        "s0_wall_clock_shortfall": int(s0.get("clock_class") != REAL_CLOCK or float(s0.get("stress_wall_seconds", 0)) < 900),
        "s0_offered_load_identity_mismatch": _family_load_violation(s0_workload),
        "s0_unrecovered_backlog": int(s0.get("recovery_pressure") != "GREEN"),
        "provider_call_inside_open_mutation_transaction": int(r0.get("provider_call_inside_open_mutation_transaction", 1)),
        "cost_hourly_slice_identity_mismatch": int(w7d_workload.get("logical_window_hours") != 168 or w7d_workload.get("hourly_slices") != 168),
        "cost_raw_recompute_mismatch": cost_recompute_mismatch,
        "cost_ratio_target_miss": int(independent_ratio < 0 or independent_ratio > 0.10),
        "accelerated_time_used_for_latency_claim": int(r0.get("clock_class") != REAL_CLOCK or s0.get("clock_class") != REAL_CLOCK or w7d.get("measurement_class") != ACCELERATED_REPLAY),
        "monthly_availability_fabricated": 0,
        "current_cross_primary_rollout_expanded": 0,
    }

    claims = {
        "p34_gate_pass": False,
        "evidence_compiler_gate_authority": False,
        "current_cross_primary_rollout": "DENIED",
        "monthly_availability_attainment": MONTHLY_NOT_CLAIMED,
    }
    passed = bool(r0.get("passed")) and bool(s0.get("passed")) and bool(w7d.get("passed")) and not any(metrics.values())

    handoff = {
        "schema_version": "0.2",
        "kind": "CPV-E-ENGINEERING-HANDOFF",
        "package_id": PACKAGE_ID,
        "package_ref": PACKAGE_REF,
        "result_revision": result_revision,
        "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
        "source_cp_i08_p34_review": SOURCE_CP_I08_P34,
        "r0": {"passed": bool(r0.get("passed")), "clock_class": r0.get("clock_class"), "warmup_wall_seconds": r0.get("warmup_wall_seconds"), "measurement_wall_seconds": r0.get("measurement_wall_seconds")},
        "s0": {"passed": bool(s0.get("passed")), "clock_class": s0.get("clock_class"), "stress_wall_seconds": s0.get("stress_wall_seconds"), "recovery_pressure": s0.get("recovery_pressure")},
        "w7d": {"passed": bool(w7d.get("passed")), "measurement_class": w7d.get("measurement_class"), "logical_hours": w7d_workload.get("logical_window_hours"), "independent_ratio": independent_ratio},
        "monthly_availability_attainment": MONTHLY_NOT_CLAIMED,
        "current_cross_primary_rollout": "DENIED",
        "next_review_surface": "CONTROL_REVIEW",
        "next_stage": "P34 Gate Review — CP-I09",
        "p34_gate_pass": False,
        "passed": passed,
    }
    _write(output_dir / "engineering-handoff.json", handoff)

    evidence_files = [*R0_FILES, *S0_FILES, *W7D_FILES, "engineering-handoff.json"]
    file_hashes = {name: _sha(output_dir / name) for name in evidence_files}
    manifest = {
        "schema_version": "0.2",
        "kind": "CP-I09-EVIDENCE-MANIFEST",
        "package_id": PACKAGE_ID,
        "package_ref": PACKAGE_REF,
        "result_revision": result_revision,
        "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
        "source_cp_i08_p34_review": SOURCE_CP_I08_P34,
        "workflow_run": workflow_run,
        "r0": {"clock_class": r0.get("clock_class"), "warmup_wall_seconds": r0.get("warmup_wall_seconds"), "measurement_wall_seconds": r0.get("measurement_wall_seconds"), "passed": bool(r0.get("passed"))},
        "s0": {"clock_class": s0.get("clock_class"), "stress_wall_seconds": s0.get("stress_wall_seconds"), "offered_load_multiplier": 4, "recovery_below_yellow": s0.get("recovery_pressure") == "GREEN", "passed": bool(s0.get("passed"))},
        "w7d": {"measurement_class": w7d.get("measurement_class"), "logical_hours": 168, "independent_ratio": independent_ratio, "passed": bool(w7d.get("passed"))},
        "metrics": metrics,
        "claims": claims,
        "files": file_hashes,
        "passed": passed,
    }
    _write(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--workflow-run", required=True)
    parser.add_argument("--r0-dir", required=True)
    parser.add_argument("--s0-dir", required=True)
    parser.add_argument("--w7d-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    manifest = compile_evidence(
        result_revision=args.result_revision,
        workflow_run=args.workflow_run,
        r0_dir=Path(args.r0_dir),
        s0_dir=Path(args.s0_dir),
        w7d_dir=Path(args.w7d_dir),
        output_dir=Path(args.output_dir),
    )
    return 0 if manifest["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
