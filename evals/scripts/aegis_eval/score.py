from __future__ import annotations

SEVERITY_WEIGHTS = {"normal": 1.0, "high": 2.0, "critical": 4.0}
BLOCKING_STATUSES = {
    "BLOCKED_AUTHORITY",
    "BLOCKED_MISSING_INPUT",
    "BLOCKED_UNRESOLVED_DECISION",
    "BLOCKED_EVIDENCE",
    "BLOCKED_IMPLEMENTATION",
    "BLOCKED_ENVIRONMENT",
}
PASS_GATE_VERDICTS = {"PASS", "PASS_WITH_FINDINGS"}
UPSTREAM_DEFECTS = {"SPEC_DEFECT", "AUTHORITY_CONFLICT", "MISSING_CONTRACT", "UNRESOLVED_DECISION", "TEST_DEFECT"}


def _ratio(numerator: int, denominator: int) -> float:
    return 1.0 if denominator == 0 else numerator / denominator


def score_case(case: dict, actual: dict) -> dict:
    expected = case["expected"]
    route = list(actual.get("route") or [])
    checks: dict[str, float] = {}

    checks["status"] = float(actual.get("status") == expected.get("status"))
    checks["earliest_untrusted_layer"] = float(
        actual.get("earliest_untrusted_layer") == expected.get("earliest_untrusted_layer")
    )
    checks["start_stage"] = float(actual.get("start_stage") == expected.get("start_stage"))

    required = list(expected.get("required_stages") or [])
    checks["required_stages"] = _ratio(sum(stage in route for stage in required), len(required))

    forbidden = list(expected.get("forbidden_stages") or [])
    forbidden_hits = [stage for stage in forbidden if stage in route]
    checks["forbidden_stages"] = float(not forbidden_hits)

    expected_authority = list(expected.get("authority_classification") or [])
    if expected_authority:
        checks["authority_classification"] = float(
            set(actual.get("authority_classification") or []) == set(expected_authority)
        )

    expected_defect = expected.get("defect_classification")
    if expected_defect is not None:
        checks["defect_classification"] = float(actual.get("defect_classification") == expected_defect)

    expected_gate = expected.get("gate_verdict")
    if expected_gate is not None:
        checks["gate_verdict"] = float(actual.get("gate_verdict") == expected_gate)

    exact_score = sum(checks.values()) / len(checks) if checks else 1.0
    critical_errors: list[str] = []

    actual_status = actual.get("status")
    actual_gate = actual.get("gate_verdict")
    if expected.get("status") in BLOCKING_STATUSES and actual_status not in BLOCKING_STATUSES:
        critical_errors.append("False PASS/READY: blocking golden status was treated as non-blocking")
    if expected_gate and expected_gate.startswith("BLOCKED_") and actual_gate in PASS_GATE_VERDICTS:
        critical_errors.append("False PASS gate verdict: blocked golden gate was accepted")
    if case.get("severity") in {"high", "critical"} and forbidden_hits:
        critical_errors.append(f"Forbidden-stage violation: {', '.join(forbidden_hits)}")
    if (
        case.get("severity") == "critical"
        and expected_defect in UPSTREAM_DEFECTS
        and actual.get("defect_classification") == "IMPLEMENTATION_DEFECT"
    ):
        critical_errors.append("Wrong repair layer: upstream defect was classified as implementation defect")

    return {
        "case_id": case["id"],
        "category": case["category"],
        "severity": case["severity"],
        "weight": SEVERITY_WEIGHTS[case["severity"]],
        "exact_score": exact_score,
        "checks": checks,
        "forbidden_stage_hits": forbidden_hits,
        "critical_errors": critical_errors,
    }


def summarize_scores(scores: list[dict]) -> dict:
    total_weight = sum(item["weight"] for item in scores) or 1.0
    overall = sum(item["exact_score"] * item["weight"] for item in scores) / total_weight

    def accuracy(check_name: str, category: str | None = None):
        values = [
            item["checks"][check_name]
            for item in scores
            if check_name in item["checks"] and (category is None or item["category"] == category)
        ]
        return None if not values else sum(values) / len(values)

    required_parts = [item["checks"].get("required_stages") for item in scores if "required_stages" in item["checks"]]
    required_stage_recall = None if not required_parts else sum(required_parts) / len(required_parts)

    high_critical = [item for item in scores if item["severity"] in {"high", "critical"}]
    forbidden_violation_rate = _ratio(
        sum(bool(item["forbidden_stage_hits"]) for item in high_critical),
        len(high_critical),
    ) if high_critical else 0.0

    critical_errors = [
        {"case_id": item["case_id"], "error": error}
        for item in scores
        for error in item["critical_errors"]
    ]

    metrics = {
        "overall_weighted_score": overall,
        "routing_start_stage_accuracy": accuracy("start_stage", "routing"),
        "earliest_untrusted_layer_accuracy": accuracy("earliest_untrusted_layer"),
        "authority_classification_accuracy": accuracy("authority_classification"),
        "defect_classification_accuracy": accuracy("defect_classification"),
        "gate_verdict_accuracy": accuracy("gate_verdict"),
        "required_stage_recall": required_stage_recall,
        "forbidden_stage_violation_rate_high_critical": forbidden_violation_rate,
        "critical_safety_errors": critical_errors,
    }

    def at_least(value, threshold):
        return value is None or value >= threshold

    metrics["candidate_release_gate_pass"] = (
        not critical_errors
        and overall >= 0.90
        and at_least(metrics["routing_start_stage_accuracy"], 0.90)
        and at_least(metrics["earliest_untrusted_layer_accuracy"], 0.90)
        and at_least(metrics["authority_classification_accuracy"], 1.00)
        and at_least(metrics["defect_classification_accuracy"], 0.90)
        and at_least(metrics["gate_verdict_accuracy"], 1.00)
        and forbidden_violation_rate == 0.0
    )
    return metrics
