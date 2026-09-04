"""Narrow compatibility bridge for the historical CP-I02 evidence probe.

CP-I02 intentionally proves that an operation *still owned by a later slice*
fails with zero residue. Its original compiler selected
SCHEDULE_REPAIR_OCCURRENCE as that representative operation. CP-I06 now owns
that operation, so the representative probe must advance to the only P13
operation still deferred: RECOMPUTE_CONTROL_PROJECTION.

This bridge changes only that historical representative trace. It never masks
other CP-I02 evidence failures or changes any zero-tolerance metric.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from tests.control_plane.cp_i02_evidence import compile_evidence as _compile_evidence
from tests.control_plane.cp_i02_fixtures import make_request
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.store import ControlStore


def compile_evidence(repo_root: Path) -> dict:
    compiled = _compile_evidence(repo_root)
    traces = compiled["canonical_conformance"]["traces"]
    matches = [trace for trace in traces if trace.get("trace_id") == "CP-I02-unsupported-operation"]
    if len(matches) != 1:
        raise RuntimeError("CP-I02 unsupported-operation evidence trace is not unique")
    trace = matches[0]

    # If the historical probe already passes, do not reinterpret anything.
    if trace.get("status") == "PASS":
        return compiled

    observed = trace.get("observed") or {}
    if observed.get("code") != "INVALID_REPAIR_SCHEDULE_PAYLOAD" or not observed.get("counts_equal"):
        raise RuntimeError("CP-I02 unsupported-operation trace failed for an unexpected reason")

    with tempfile.TemporaryDirectory(prefix="cp-i02-future-op-") as tmp:
        store = ControlStore(str(Path(tmp) / "unsupported.db"))
        before = dict(store.snapshot_counts())
        code = None
        try:
            MutationService(store).apply(make_request(
                "RECOMPUTE_CONTROL_PROJECTION",
                "req_unsupported_projection",
                "lane_unsupported",
                {"checkpoint": 1},
            ))
        except MutationRejected as exc:
            code = exc.code
        after = dict(store.snapshot_counts())

    expected = {"code": "UNSUPPORTED_OPERATION_IN_CP_I02", "counts_equal": True}
    replacement = {"code": code, "counts_equal": before == after}
    trace["expected"] = expected
    trace["observed"] = replacement
    trace["status"] = "PASS" if replacement == expected else "FAIL"

    metrics = compiled["canonical_conformance"]["metrics"]
    compiled["canonical_conformance"]["passed"] = (
        all(value == 0 for value in metrics.values())
        and all(item.get("status") == "PASS" for item in traces)
    )
    # The legacy compiler shares the trace list today; assign explicitly so the
    # durable raw trace corpus remains correct if that implementation changes.
    compiled["trace_corpus"]["traces"] = traces
    return compiled
