from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

REQUIRED_METRIC_FAMILIES = frozenset({
    "control_api_latency", "canonical_transaction_latency", "projection_latency",
    "outbox_depth", "outbox_oldest_age", "open_occurrence_age", "reconciliation_latency",
    "provider_call_count", "provider_rate_limit", "conflict_count",
    "zero_tolerance_invariant", "orchestration_cost_component",
})


class ObservabilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class RawMetricEvent:
    sequence: int
    timestamp: str
    family: str
    correlation_id: str
    value: float
    unit: str
    dimensions: Mapping[str, str]


@dataclass(frozen=True)
class Alert:
    rule_id: str
    severity: str
    semantic_truth: bool = False


class ObservabilityBuffer:
    def __init__(self):
        self._events: list[RawMetricEvent] = []

    def record(self, event: RawMetricEvent) -> None:
        if not event.correlation_id:
            raise ObservabilityError("CORRELATION_ID_REQUIRED")
        if not event.family or not event.timestamp or not event.unit:
            raise ObservabilityError("INVALID_RAW_METRIC_EVENT")
        if self._events and event.sequence <= self._events[-1].sequence:
            raise ObservabilityError("NON_MONOTONIC_EVENT_SEQUENCE")
        self._events.append(event)

    def raw_events(self) -> tuple[RawMetricEvent, ...]:
        return tuple(self._events)

    def export_aggregates(self):
        return recompute_aggregates(self._events)


def recompute_aggregates(events: Sequence[RawMetricEvent]) -> dict:
    grouped: dict[tuple[str, str], list[float]] = {}
    for event in events:
        grouped.setdefault((event.family, event.unit), []).append(float(event.value))
    return {
        f"{family}|{unit}": {"count": len(values), "sum": sum(values), "min": min(values), "max": max(values)}
        for (family, unit), values in sorted(grouped.items())
    }


def evaluate_alerts(snapshot: Mapping[str, object]) -> list[Alert]:
    alerts: list[Alert] = []
    if snapshot.get("possible_acknowledged_commit_loss") is True:
        alerts.append(Alert("ACKNOWLEDGED_COMMIT_LOSS_CRITICAL", "CRITICAL"))
    if snapshot.get("stale_snapshot_accepted") is True:
        alerts.append(Alert("STALE_SNAPSHOT_ACCEPTED_CRITICAL", "CRITICAL"))
    if snapshot.get("unauthorized_cross_primary_dispatch") is True:
        alerts.append(Alert("UNAUTHORIZED_CROSS_PRIMARY_CRITICAL", "CRITICAL"))
    if snapshot.get("production_traffic") is True and float(snapshot.get("store_unavailable_seconds", 0) or 0) > 120:
        alerts.append(Alert("STORE_UNAVAILABLE_CRITICAL", "CRITICAL"))
    if float(snapshot.get("oldest_ready_outbox_seconds", 0) or 0) > 300:
        alerts.append(Alert("OUTBOX_AGE_URGENT", "URGENT"))
    if float(snapshot.get("reconciliation_lag_seconds", 0) or 0) > 900:
        alerts.append(Alert("RECONCILIATION_LAG_URGENT", "URGENT"))
    if float(snapshot.get("red_backpressure_seconds", 0) or 0) > 300:
        alerts.append(Alert("RED_BACKPRESSURE_URGENT", "URGENT"))
    if int(snapshot.get("delivery_attempts", 0) or 0) >= 12 or float(snapshot.get("delivery_uncertainty_seconds", 0) or 0) >= 1800:
        alerts.append(Alert("DELIVERY_UNCERTAINTY_URGENT", "URGENT"))
    return alerts
