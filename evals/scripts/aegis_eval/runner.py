from __future__ import annotations

import json
from pathlib import Path

from .normalize import normalize_raw_result
from .report import render_report
from .score import score_case, summarize_scores


def evaluate_cases(
    cases: list[dict],
    adapter,
    output_dir: str | Path,
    semantic_evidence_status: str = "NOT_EVALUATED",
) -> dict:
    if semantic_evidence_status != "NOT_EVALUATED":
        raise ValueError(
            "semantic evidence promotion is not implemented in v0.1; "
            "a status flag alone cannot promote the Behavioral Gate"
        )

    output_dir = Path(output_dir)
    raw_dir = output_dir / "raw"
    normalized_dir = output_dir / "normalized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)

    scores: list[dict] = []

    for case in cases:
        case_id = case["id"]
        raw = adapter.run(case)
        (raw_dir / f"{case_id}.txt").write_text(raw, encoding="utf-8")

        normalized = normalize_raw_result(case_id, raw)
        (normalized_dir / f"{case_id}.json").write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        scores.append(score_case(case, normalized))

    summary = summarize_scores(scores)
    summary["deterministic_gate_pass"] = summary.pop("candidate_release_gate_pass")
    summary["semantic_evidence_status"] = semantic_evidence_status

    if not summary["deterministic_gate_pass"]:
        summary["behavioral_gate_status"] = "BLOCKED_IMPLEMENTATION"
    else:
        summary["behavioral_gate_status"] = "BLOCKED_EVIDENCE"

    (output_dir / "case-scores.json").write_text(
        json.dumps(scores, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "report.md").write_text(
        render_report(summary, scores, getattr(adapter, "name", adapter.__class__.__name__)),
        encoding="utf-8",
    )
    return summary
