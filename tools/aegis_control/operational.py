"""Operational-only degraded mode controls for Control Plane CP-I06.

These types decide *when* work may be attempted. They do not author canonical
StageOccurrence, package, Escalation, Authority, Proof, Gate, or Integration
truth. In particular, pause, backpressure, and provider rate-limit state never
create semantic retries or replacement occurrences.
"""
from __future__ import annotations

from dataclasses import dataclass


BACKPRESSURE_LEVELS = ("GREEN", "YELLOW", "ORANGE", "RED")


def classify_backpressure(utilization: float) -> str:
    """Classify P18 capacity watermarks using a normalized utilization ratio."""
    if isinstance(utilization, bool) or not isinstance(utilization, (int, float)):
        raise ValueError("utilization must be numeric")
    value = float(utilization)
    if value < 0:
        raise ValueError("utilization must be non-negative")
    if value < 0.70:
        return "GREEN"
    if value < 0.85:
        return "YELLOW"
    if value < 0.95:
        return "ORANGE"
    return "RED"


@dataclass(frozen=True)
class AdmissionDecision:
    level: str
    admit: bool
    reason: str
    recovery_priority: bool
    requires_fresh_recompute: bool
    semantic_mutation: bool = False


class AdmissionController:
    """In-memory operational admission/pause state; never lifecycle truth."""

    def __init__(self) -> None:
        self._paused = False
        self._fresh_recompute_after_resume = False

    @property
    def paused(self) -> bool:
        return self._paused

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        if self._paused:
            self._fresh_recompute_after_resume = True
        self._paused = False

    def evaluate(
        self,
        *,
        utilization: float,
        autonomous: bool,
        recovery: bool = False,
    ) -> AdmissionDecision:
        level = classify_backpressure(utilization)
        if recovery:
            return AdmissionDecision(
                level,
                True,
                "RECOVERY_OR_COMMITTED_WORK_PRIORITY",
                True,
                self._consume_recompute_flag(),
            )
        if self._paused:
            return AdmissionDecision(
                level,
                False,
                "OPERATOR_PAUSED",
                False,
                False,
            )
        recompute = self._consume_recompute_flag()
        if autonomous and level == "RED":
            return AdmissionDecision(
                level,
                False,
                "STOP_NEW_AUTONOMOUS_ADMISSION",
                False,
                recompute,
            )
        if autonomous and level == "ORANGE":
            return AdmissionDecision(
                level,
                False,
                "DEFER_NEW_AUTONOMOUS_ADMISSION",
                False,
                recompute,
            )
        if autonomous and level == "YELLOW":
            return AdmissionDecision(
                level,
                True,
                "REDUCE_OPTIONAL_OR_SPECULATIVE_WORK",
                False,
                recompute,
            )
        return AdmissionDecision(level, True, "ADMIT", False, recompute)

    def _consume_recompute_flag(self) -> bool:
        value = self._fresh_recompute_after_resume
        self._fresh_recompute_after_resume = False
        return value


@dataclass(frozen=True)
class RateLimitState:
    concurrency: int
    retry_after_seconds: int | None
    breached: bool
    recovering: bool
    semantic_retry: bool = False
    reduce_polling_before_proof_or_review: bool = True


class ProviderRateLimitController:
    """P18 >5%/5m provider-pressure controller with gradual recovery."""

    def __init__(self, *, baseline_concurrency: int, minimum_concurrency: int = 1) -> None:
        if baseline_concurrency < 1 or minimum_concurrency < 1:
            raise ValueError("concurrency must be positive")
        if minimum_concurrency > baseline_concurrency:
            raise ValueError("minimum concurrency cannot exceed baseline")
        self._baseline = int(baseline_concurrency)
        self._minimum = int(minimum_concurrency)
        self._current = int(baseline_concurrency)

    @property
    def concurrency(self) -> int:
        return self._current

    def observe(
        self,
        *,
        window_seconds: int,
        request_count: int,
        rate_limited_count: int,
        retry_after_seconds: int | None = None,
    ) -> RateLimitState:
        if window_seconds < 0 or request_count < 0 or rate_limited_count < 0:
            raise ValueError("rate-limit observations must be non-negative")
        if rate_limited_count > request_count:
            raise ValueError("rate_limited_count cannot exceed request_count")
        if retry_after_seconds is not None and retry_after_seconds < 0:
            raise ValueError("retry_after_seconds must be non-negative")

        ratio = (rate_limited_count / request_count) if request_count else 0.0
        breached = window_seconds >= 300 and request_count > 0 and ratio > 0.05
        recovering = False
        if breached:
            self._current = max(self._minimum, self._current // 2)
        elif window_seconds >= 300 and self._current < self._baseline:
            # Recover by half the remaining headroom, with at least one slot.
            # This is monotonic and deliberately cannot jump straight to baseline.
            remaining = self._baseline - self._current
            step = max(1, remaining // 2)
            self._current = min(self._baseline, self._current + step)
            recovering = self._current < self._baseline

        return RateLimitState(
            concurrency=self._current,
            retry_after_seconds=retry_after_seconds,
            breached=breached,
            recovering=recovering,
        )
