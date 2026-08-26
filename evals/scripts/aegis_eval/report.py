from __future__ import annotations


def _pct(value):
    return "n/a" if value is None else f"{value * 100:.1f}%"


def render_report(summary: dict, scores: list[dict], adapter_name: str) -> str:
    lines = [
        "# Aegis Evaluation Report",
        "",
        f"- Adapter: `{adapter_name}`",
        f"- Cases: `{len(scores)}`",
        f"- Overall weighted exact score: `{_pct(summary['overall_weighted_score'])}`",
        f"- Deterministic gate: `{'PASS' if summary['deterministic_gate_pass'] else 'BLOCKED'}`",
        f"- Behavioral gate status: `{summary['behavioral_gate_status']}`",
        "",
        "## Metrics",
        "",
        f"- Routing start-stage accuracy: `{_pct(summary.get('routing_start_stage_accuracy'))}`",
        f"- Earliest-untrusted-layer accuracy: `{_pct(summary.get('earliest_untrusted_layer_accuracy'))}`",
        f"- Authority classification accuracy: `{_pct(summary.get('authority_classification_accuracy'))}`",
        f"- Defect classification accuracy: `{_pct(summary.get('defect_classification_accuracy'))}`",
        f"- Gate verdict accuracy: `{_pct(summary.get('gate_verdict_accuracy'))}`",
        f"- Required-stage recall: `{_pct(summary.get('required_stage_recall'))}`",
        f"- High/Critical forbidden-stage violation rate: `{_pct(summary.get('forbidden_stage_violation_rate_high_critical'))}`",
        f"- Critical safety errors: `{len(summary.get('critical_safety_errors', []))}`",
        "",
        "## Gate boundary",
        "",
        "The deterministic scorer does not grade semantic `required_findings` / `forbidden_findings`.",
        "Until a separately auditable semantic evidence contract is implemented, the full behavioral gate remains `BLOCKED_EVIDENCE` even when deterministic checks pass.",
    ]

    if summary.get("critical_safety_errors"):
        lines.extend(["", "## Critical safety errors", ""])
        for item in summary["critical_safety_errors"]:
            lines.append(f"- `{item['case_id']}` — {item['error']}")

    failed = [item for item in scores if item["exact_score"] < 1.0 or item["critical_errors"]]
    if failed:
        lines.extend(["", "## Cases with deterministic findings", ""])
        for item in failed:
            lines.append(f"- `{item['case_id']}` — exact `{_pct(item['exact_score'])}`")

    lines.append("")
    return "\n".join(lines)
