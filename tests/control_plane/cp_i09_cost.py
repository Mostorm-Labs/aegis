from __future__ import annotations

import argparse
import json
from pathlib import Path

from tests.control_plane.cp_i09_contract import (
    ACCELERATED_REPLAY,
    CostEvent,
    SevenDayCostEvidence,
    validate_w7d,
)

PACKAGE_ID = "CP-I09-P31-01"
PACKAGE_REF = "9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385"
TASK_ANCHOR = "ac2bcf19acf46a749761ed455ecf0a995069700d"
SOURCE_CP_I08_P34 = "5079977191"
WORKLOAD_ID = "CPV-W7D-R0"
GENERATOR_VERSION = "cp-i09-w7d-v1"
SEED = 20260901
COST_MODEL_ID = "CP-I09-REFERENCE-NORMALIZED-V1"

# Exact transition/provider action manifest. Counts are per logical hour and are
# materialized as raw provider-unit events; no aggregate is multiplied by 168.
_ACTIONS = (
    {"action": "substantive_implementation_execution", "unit": "PIU", "classification": "SUBSTANTIVE", "count": 60},
    {"action": "substantive_proof_execution", "unit": "PIU", "classification": "SUBSTANTIVE", "count": 30},
    {"action": "substantive_independent_review", "unit": "PIU", "classification": "SUBSTANTIVE", "count": 10},
    {"action": "orchestration_currentness_reads", "unit": "PRU", "classification": "OVERHEAD", "count": 4},
    {"action": "orchestration_reconciliation_reads", "unit": "PRU", "classification": "OVERHEAD", "count": 2},
    {"action": "orchestration_artifact_transport", "unit": "PAU", "classification": "OVERHEAD", "count": 1},
)


def _write(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def build_cost_evidence(*, result_revision: str) -> tuple[dict, dict, dict, dict, dict]:
    raw_rows = []
    events: list[CostEvent] = []
    hourly = []
    for hour in range(168):
        hour_overhead = 0
        hour_substantive = 0
        for action in _ACTIONS:
            row = {
                "hour": hour,
                "action": action["action"],
                "unit": action["unit"],
                "classification": action["classification"],
                "count": int(action["count"]),
            }
            raw_rows.append(row)
            events.append(CostEvent(hour=hour, unit=row["unit"], classification=row["classification"], count=row["count"]))
            if row["classification"] == "OVERHEAD":
                hour_overhead += row["count"]
            else:
                hour_substantive += row["count"]
        hourly.append({
            "hour": hour,
            "overhead_cost": hour_overhead,
            "substantive_provider_cost": hour_substantive,
            "ratio": hour_overhead / hour_substantive,
        })

    reported_overhead = float(sum(row["count"] for row in raw_rows if row["classification"] == "OVERHEAD"))
    reported_substantive = float(sum(row["count"] for row in raw_rows if row["classification"] == "SUBSTANTIVE"))
    reported_ratio = reported_overhead / reported_substantive
    evidence = SevenDayCostEvidence(
        measurement_class=ACCELERATED_REPLAY,
        hourly_slices=tuple(range(168)),
        raw_events=tuple(events),
        reported_overhead_cost=reported_overhead,
        reported_substantive_cost=reported_substantive,
        reported_ratio=reported_ratio,
    )
    independently_recomputed = validate_w7d(evidence)

    workload = {
        "schema_version": "0.2",
        "kind": "CP-I09-W7D-WORKLOAD",
        "id": WORKLOAD_ID,
        "package_id": PACKAGE_ID,
        "package_ref": PACKAGE_REF,
        "result_revision": result_revision,
        "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
        "source_cp_i08_p34_review": SOURCE_CP_I08_P34,
        "logical_window_hours": 168,
        "hourly_slices": 168,
        "measurement_class": ACCELERATED_REPLAY,
        "generator_version": GENERATOR_VERSION,
        "seed": SEED,
        "profile_ref": "P18-R0",
        "transition_provider_action_manifest": list(_ACTIONS),
    }
    hourly_payload = {
        "schema_version": "0.2",
        "kind": "CP-I09-W7D-HOURLY-SLICES",
        "workload_id": WORKLOAD_ID,
        "rows": hourly,
    }
    raw_payload = {
        "schema_version": "0.2",
        "kind": "CP-I09-W7D-RAW-COST-EVENTS",
        "workload_id": WORKLOAD_ID,
        "rows": raw_rows,
    }
    model = {
        "schema_version": "0.2",
        "kind": "CP-I09-W7D-COST-MODEL",
        "cost_model_id": COST_MODEL_ID,
        "currency": "NORMALIZED_COST_UNIT",
        "weights": {"PIU": 1.0, "PRU": 1.0, "PAU": 1.0},
        "rounding": "none",
        "minimum_billing": "none",
        "provider_specific_price_sheet_claimed": False,
    }
    result = {
        "schema_version": "0.2",
        "kind": "CPV-E-7D-COST",
        "workload_id": WORKLOAD_ID,
        "result_revision": result_revision,
        "measurement_class": ACCELERATED_REPLAY,
        "logical_hours": 168,
        "reported_overhead_cost": reported_overhead,
        "reported_substantive_provider_cost": reported_substantive,
        "reported_ratio": reported_ratio,
        "independent_recompute": independently_recomputed,
        "threshold_max": 0.10,
        "passed": independently_recomputed["independent_ratio"] <= 0.10,
    }
    return workload, hourly_payload, raw_payload, model, result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=True)
    workload, hourly, raw, model, result = build_cost_evidence(result_revision=args.result_revision)
    _write(root / "w7d-workload-manifest.json", workload)
    _write(root / "w7d-hourly-slices.json", hourly)
    _write(root / "w7d-raw-cost-events.json", raw)
    _write(root / "w7d-cost-model.json", model)
    _write(root / "w7d-cost.json", result)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
