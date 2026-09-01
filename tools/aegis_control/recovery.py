"""Reconciliation/recovery boundary for Control Plane CP-I05.

Age, callback loss, and delivery uncertainty are operational diagnostics. This
module does not author semantic failure or replacement StageOccurrences.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .execution_surface import ProviderObservation
from .store import ControlStore, StoreConflict


class ReconciliationBlocked(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class ReconciliationPolicy:
    interval_seconds: int
    operator_alert: bool
    semantic_terminalization: bool = False


def dispatch_retry_delay_seconds(attempt_count: int) -> int:
    if attempt_count < 1:
        raise ValueError("attempt_count must be positive")
    schedule = (1, 2, 4, 8, 16, 30, 60)
    if attempt_count <= len(schedule):
        return schedule[attempt_count - 1]
    return 300


def delivery_is_uncertain(*, attempt_count: int, elapsed_seconds: int) -> bool:
    if attempt_count < 0 or elapsed_seconds < 0:
        raise ValueError("attempt_count and elapsed_seconds must be non-negative")
    return attempt_count >= 12 or elapsed_seconds >= 1800


def reconciliation_policy(age_seconds: int) -> ReconciliationPolicy:
    if age_seconds < 0:
        raise ValueError("age_seconds must be non-negative")
    if age_seconds < 300:
        return ReconciliationPolicy(30, False)
    if age_seconds < 1800:
        return ReconciliationPolicy(120, False)
    if age_seconds < 7200:
        return ReconciliationPolicy(300, False)
    return ReconciliationPolicy(900, True)


class RecoveryCoordinator:
    """Query provider truth by durable correlation without semantic side effects."""

    def __init__(self, store: ControlStore, execution_surface: Any):
        self._store = store
        self._execution_surface = execution_surface

    def reconcile_outbox(self, outbox_id: str, *, observed_at: str) -> ProviderObservation:
        outbox = self._store.read_outbox_entry(outbox_id)
        if outbox is None:
            raise ReconciliationBlocked("OUTBOX_NOT_FOUND")
        delivery = self._store.read_delivery_state(outbox_id)
        if delivery is None or not delivery.get("provider_correlation_id"):
            raise ReconciliationBlocked("DELIVERY_CORRELATION_MISSING")
        correlation_id = delivery["provider_correlation_id"]
        try:
            observation = self._execution_surface.query(correlation_id)
        except KeyError as exc:
            raise ReconciliationBlocked("PROVIDER_CORRELATION_NOT_FOUND") from exc
        if not isinstance(observation, ProviderObservation):
            raise ReconciliationBlocked("PROVIDER_OBSERVATION_INVALID")
        if observation.occurrence_id != outbox["occurrence_id"]:
            raise ReconciliationBlocked("PROVIDER_CORRELATION_MISMATCH")
        try:
            self._store.record_delivery_correlation(
                outbox_id,
                correlation_id,
                observed_at=observed_at,
                provider_state=observation.state,
            )
        except StoreConflict as exc:
            raise ReconciliationBlocked("DELIVERY_STATE_CONFLICT") from exc
        return observation
