from __future__ import annotations

from dataclasses import dataclass

DAY = 24 * 60 * 60
_CANONICAL_NO_AUTO_DELETE = frozenset({
    "STAGE_OCCURRENCE", "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "ESCALATION", "SEMANTIC_IDEMPOTENCY",
})


class RetentionError(RuntimeError):
    pass


@dataclass(frozen=True)
class RetentionPolicy:
    policy_id: str
    record_class: str
    window_seconds: int | None
    expiry_action: str


@dataclass(frozen=True)
class RetentionDecision:
    action: str
    policy: str


_DEFAULT_POLICIES = {
    "STAGE_OCCURRENCE": RetentionPolicy("CANONICAL_HISTORY_LIFETIME", "STAGE_OCCURRENCE", None, "NO_AUTO_DELETE"),
    "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE": RetentionPolicy("CANONICAL_HISTORY_LIFETIME", "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", None, "NO_AUTO_DELETE"),
    "ESCALATION": RetentionPolicy("CANONICAL_HISTORY_LIFETIME", "ESCALATION", None, "NO_AUTO_DELETE"),
    "SEMANTIC_IDEMPOTENCY": RetentionPolicy("CANONICAL_HISTORY_LIFETIME", "SEMANTIC_IDEMPOTENCY", None, "NO_AUTO_DELETE"),
    "PENDING_OUTBOX": RetentionPolicy("UNTIL_RECONCILED", "PENDING_OUTBOX", None, "KEEP"),
    "UNRESOLVED_DELIVERY": RetentionPolicy("UNTIL_RECONCILED", "UNRESOLVED_DELIVERY", None, "KEEP"),
    "COMPLETED_DELIVERY_METADATA": RetentionPolicy("30_DAYS_HOT", "COMPLETED_DELIVERY_METADATA", 30 * DAY, "COMPACT_OPERATIONAL"),
    "HIGH_CARDINALITY_TRACE": RetentionPolicy("14_DAYS_TRACE", "HIGH_CARDINALITY_TRACE", 14 * DAY, "EXPIRE_OPERATIONAL"),
    "STRUCTURED_OPERATIONAL_LOG": RetentionPolicy("30_DAYS_LOG", "STRUCTURED_OPERATIONAL_LOG", 30 * DAY, "EXPIRE_OPERATIONAL"),
    "HIGH_RESOLUTION_METRIC": RetentionPolicy("90_DAYS_HIGH_RES_METRIC", "HIGH_RESOLUTION_METRIC", 90 * DAY, "EXPIRE_OPERATIONAL"),
    "AGGREGATED_SLO_COST_METRIC": RetentionPolicy("AT_LEAST_13_MONTHS", "AGGREGATED_SLO_COST_METRIC", None, "KEEP"),
}


def retention_policy(record_class: str) -> RetentionPolicy:
    return _DEFAULT_POLICIES.get(record_class, RetentionPolicy("UNSPECIFIED_FAIL_SAFE_KEEP", record_class, None, "KEEP"))


def evaluate_retention_at(
    record_class: str,
    *,
    recorded_at_seconds: int,
    current_time_seconds: int,
    policy: RetentionPolicy,
) -> RetentionDecision:
    if policy.record_class != record_class:
        raise RetentionError("RETENTION_POLICY_CLASS_MISMATCH")
    if not isinstance(recorded_at_seconds, int) or isinstance(recorded_at_seconds, bool):
        raise RetentionError("INVALID_RECORDED_TIME")
    if not isinstance(current_time_seconds, int) or isinstance(current_time_seconds, bool):
        raise RetentionError("INVALID_CURRENT_TIME")
    if current_time_seconds < recorded_at_seconds:
        raise RetentionError("CURRENT_TIME_PRECEDES_RECORDED_TIME")
    if policy.window_seconds is not None and (
        not isinstance(policy.window_seconds, int)
        or isinstance(policy.window_seconds, bool)
        or policy.window_seconds < 0
    ):
        raise RetentionError("INVALID_RETENTION_WINDOW")
    if policy.window_seconds is None:
        return RetentionDecision(policy.expiry_action, policy.policy_id)
    age_seconds = current_time_seconds - recorded_at_seconds
    action = policy.expiry_action if age_seconds >= policy.window_seconds else "KEEP"
    return RetentionDecision(action, policy.policy_id)


def evaluate_retention(record_class: str, *, age_seconds: int) -> RetentionDecision:
    if not isinstance(age_seconds, int) or isinstance(age_seconds, bool) or age_seconds < 0:
        raise RetentionError("INVALID_AGE_SECONDS")
    return evaluate_retention_at(
        record_class,
        recorded_at_seconds=0,
        current_time_seconds=age_seconds,
        policy=retention_policy(record_class),
    )
