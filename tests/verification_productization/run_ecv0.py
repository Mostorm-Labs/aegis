#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.verification_productization.ecv0_fixtures import (
    APPLICABILITY_IDS,
    MUTANT_IDS,
    SCENARIO_IDS,
    run_applicability,
    run_mutant,
    run_scenario,
)

EXPECTED_APPLICABILITY_IDS = ("EC-AP01", "EC-AP02")


def _source_revision() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git rev-parse HEAD failed")
    return proc.stdout.strip()


def _applicability_contract_is_exact() -> bool:
    return (
        tuple(APPLICABILITY_IDS) == EXPECTED_APPLICABILITY_IDS
        and len(APPLICABILITY_IDS) == len(set(APPLICABILITY_IDS))
    )


def build_report() -> dict:
    scenario_records = [
        {"id": scenario_id, "verdict": "PASS" if run_scenario(scenario_id) else "FAIL"}
        for scenario_id in SCENARIO_IDS
    ]
    mutant_records = [
        {"id": mutant_id, "detected": bool(run_mutant(mutant_id))}
        for mutant_id in MUTANT_IDS
    ]
    applicability_records = [
        {
            "id": applicability_id,
            "verdict": "PASS" if run_applicability(applicability_id) else "FAIL",
        }
        for applicability_id in APPLICABILITY_IDS
    ]
    scenario_pass = sum(1 for item in scenario_records if item["verdict"] == "PASS")
    mutant_detected = sum(1 for item in mutant_records if item["detected"])
    applicability_pass = sum(
        1 for item in applicability_records if item["verdict"] == "PASS"
    )
    return {
        "profile": "ECV0",
        "source_revision": _source_revision(),
        "scenario_records": scenario_records,
        "mutant_records": mutant_records,
        "applicability_records": applicability_records,
        "derived_summary": {
            "scenario_required": len(SCENARIO_IDS),
            "scenario_pass": scenario_pass,
            "mutant_required": len(MUTANT_IDS),
            "mutant_detected": mutant_detected,
            "mutant_false_acceptance": len(MUTANT_IDS) - mutant_detected,
            "applicability_required": len(APPLICABILITY_IDS),
            "applicability_pass": applicability_pass,
            "applicability_fail": len(APPLICABILITY_IDS) - applicability_pass,
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    if not _applicability_contract_is_exact():
        return 1

    report = build_report()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = report["derived_summary"]
    if summary != {
        "scenario_required": 17,
        "scenario_pass": 17,
        "mutant_required": 17,
        "mutant_detected": 17,
        "mutant_false_acceptance": 0,
        "applicability_required": 2,
        "applicability_pass": 2,
        "applicability_fail": 0,
    }:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
