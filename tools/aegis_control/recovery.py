"""Reconciliation/recovery boundary for Control Plane CP-I05.

Age, callback loss, and delivery uncertainty are operational diagnostics. This
module does not author semantic failure or replacement StageOccurrences.
"""
from __future__ import annotations

from dataclasses import dataclass


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
