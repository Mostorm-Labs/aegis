from __future__ import annotations

from dataclasses import dataclass

DAY = 24 * 60 * 60
_CANONICAL_NO_AUTO_DELETE = frozenset({
    "STAGE_OCCURRENCE", "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "ESCALATION", "SEMANTIC_IDEMPOTENCY",
})


@dataclass(frozen=True)
class RetentionDecision:
    action: str
    policy: str


def evaluate_retention(record_class: str, *, age_seconds: int) -> RetentionDecision:
    if record_class in _CANONICAL_NO_AUTO_DELETE:
        return RetentionDecision("NO_AUTO_DELETE", "CANONICAL_HISTORY_LIFETIME")
    if record_class in {"PENDING_OUTBOX", "UNRESOLVED_DELIVERY"}:
        return RetentionDecision("KEEP", "UNTIL_RECONCILED")
    if record_class == "COMPLETED_DELIVERY_METADATA":
        return RetentionDecision("COMPACT_OPERATIONAL" if age_seconds >= 30 * DAY else "KEEP", "30_DAYS_HOT")
    windows = {
        "HIGH_CARDINALITY_TRACE": 14 * DAY,
        "STRUCTURED_OPERATIONAL_LOG": 30 * DAY,
        "HIGH_RESOLUTION_METRIC": 90 * DAY,
    }
    if record_class in windows:
        return RetentionDecision("EXPIRE_OPERATIONAL" if age_seconds >= windows[record_class] else "KEEP", f"{windows[record_class]}_SECONDS")
    if record_class == "AGGREGATED_SLO_COST_METRIC":
        return RetentionDecision("KEEP", "AT_LEAST_13_MONTHS")
    return RetentionDecision("KEEP", "UNSPECIFIED_FAIL_SAFE_KEEP")
