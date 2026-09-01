from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

REAL_CLOCK = "REAL_MONOTONIC_WALL_CLOCK"
ACCELERATED_REPLAY = "ACCELERATED_REPLAY"
MONTHLY_NOT_CLAIMED = "NOT_CLAIMED_PRELAUNCH"


class BenchmarkContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class DataShape:
    active_work_scopes: int
    retained_work_scopes: int
    canonical_record_revisions_retained: int
    open_stage_occurrences: int
    recent_completed_occurrence_revisions_per_work_scope_p95: int
    concurrent_active_provider_jobs: int
    concurrent_interactive_app_users: int


@dataclass(frozen=True)
class R0Evidence:
    clock_class: str
    warmup_wall_seconds: float
    measurement_wall_seconds: float
    data_shape: DataShape
    offered_load: Mapping[str, float]
    bursts: Mapping[str, float]
    latency_quantiles_ms: Mapping[str, Mapping[str, float]]
    invariant_failures: int
    accidental_semantic_duplicates: int
    provider_call_inside_open_mutation_transaction: int


@dataclass(frozen=True)
class S0Evidence:
    clock_class: str
    stress_wall_seconds: float
    data_shape: DataShape
    offered_load: Mapping[str, float]
    invariant_failures: int
    accidental_semantic_duplicates: int
    recovery_pressure: str


@dataclass(frozen=True)
class CostEvent:
    hour: int
    unit: str
    classification: str
    count: int


@dataclass(frozen=True)
class SevenDayCostEvidence:
    measurement_class: str
    hourly_slices: Sequence[int]
    raw_events: Sequence[CostEvent]
    reported_overhead_cost: float
    reported_substantive_cost: float
    reported_ratio: float


def reference_data_shape() -> DataShape:
    return DataShape(
        active_work_scopes=10_000,
        retained_work_scopes=100_000,
        canonical_record_revisions_retained=5_000_000,
        open_stage_occurrences=2_000,
        recent_completed_occurrence_revisions_per_work_scope_p95=250,
        concurrent_active_provider_jobs=500,
        concurrent_interactive_app_users=100,
    )


def reference_r0_load() -> dict[str, float]:
    return {
        "control_api_requests_per_second": 50,
        "canonical_mutation_requests_per_second": 20,
        "projection_evaluations_per_second": 200,
        "provider_callback_or_query_events_per_second": 100,
        "outbox_dispatch_attempts_per_second": 50,
    }


def reference_s0_load() -> dict[str, float]:
    return {key: value * 4 for key, value in reference_r0_load().items()}


_DATA_FLOORS = reference_data_shape()
_R0_BURST_FLOORS = {
    "api_200_rps_wall_seconds": 60,
    "mutation_100_rps_wall_seconds": 30,
    "provider_callbacks_per_minute": 1000,
}
_LATENCY_TARGETS = {
    "cached_read_only_query_ms": {"p50": 50, "p95": 200, "p99": 500},
    "simple_canonical_mutation_ms": {"p50": 100, "p95": 250, "p99": 750},
    "cached_projection_up_to_2000_revisions_ms": {"p95": 250},
    "cold_projection_up_to_2000_revisions_ms": {"p95": 2000},
    "scheduler_decision_ms": {"p95": 250},
    "outbox_claim_to_adapter_dispatch_ms": {"p95": 500},
    "terminalization_commit_to_query_visibility_ms": {"p95": 1000},
}


def validate_data_shape(shape: DataShape) -> None:
    for field in shape.__dataclass_fields__:
        actual = getattr(shape, field)
        minimum = getattr(_DATA_FLOORS, field)
        if actual < minimum:
            raise BenchmarkContractError(f"DATA_SHAPE_FLOOR:{field}:{actual}<{minimum}")


def _require_exact_load(actual: Mapping[str, float], expected: Mapping[str, float], code: str) -> None:
    if set(actual) != set(expected):
        raise BenchmarkContractError(f"{code}:KEY_SET")
    for key, value in expected.items():
        if float(actual[key]) != float(value):
            raise BenchmarkContractError(f"{code}:{key}:{actual[key]}!={value}")


def validate_latency_targets(latency_quantiles_ms: Mapping[str, Mapping[str, float]]) -> None:
    for family, thresholds in _LATENCY_TARGETS.items():
        if family not in latency_quantiles_ms:
            raise BenchmarkContractError(f"LATENCY_FAMILY_MISSING:{family}")
        actual = latency_quantiles_ms[family]
        for quantile, maximum in thresholds.items():
            if quantile not in actual:
                raise BenchmarkContractError(f"LATENCY_QUANTILE_MISSING:{family}:{quantile}")
            if float(actual[quantile]) > maximum:
                raise BenchmarkContractError(f"LATENCY_TARGET_MISS:{family}:{quantile}:{actual[quantile]}>{maximum}")


def validate_r0(evidence: R0Evidence, *, require_latency_targets: bool = True) -> None:
    if evidence.clock_class != REAL_CLOCK:
        raise BenchmarkContractError("R0_REAL_WALL_CLOCK_REQUIRED")
    if evidence.warmup_wall_seconds < 600:
        raise BenchmarkContractError("R0_WARMUP_WALL_CLOCK_SHORTFALL")
    if evidence.measurement_wall_seconds < 1800:
        raise BenchmarkContractError("R0_MEASUREMENT_WALL_CLOCK_SHORTFALL")
    validate_data_shape(evidence.data_shape)
    _require_exact_load(evidence.offered_load, reference_r0_load(), "R0_OFFERED_LOAD_MISMATCH")
    for key, minimum in _R0_BURST_FLOORS.items():
        if float(evidence.bursts.get(key, -1)) < minimum:
            raise BenchmarkContractError(f"R0_BURST_MISSING:{key}")
    if evidence.invariant_failures:
        raise BenchmarkContractError("R0_INVARIANT_FAILURE")
    if evidence.accidental_semantic_duplicates:
        raise BenchmarkContractError("R0_SEMANTIC_DUPLICATE")
    if evidence.provider_call_inside_open_mutation_transaction:
        raise BenchmarkContractError("PROVIDER_CALL_INSIDE_OPEN_MUTATION_TRANSACTION")
    if require_latency_targets:
        validate_latency_targets(evidence.latency_quantiles_ms)


def validate_s0(evidence: S0Evidence) -> None:
    if evidence.clock_class != REAL_CLOCK:
        raise BenchmarkContractError("S0_REAL_WALL_CLOCK_REQUIRED")
    if evidence.stress_wall_seconds < 900:
        raise BenchmarkContractError("S0_STRESS_WALL_CLOCK_SHORTFALL")
    validate_data_shape(evidence.data_shape)
    _require_exact_load(evidence.offered_load, reference_s0_load(), "S0_OFFERED_LOAD_MISMATCH")
    if evidence.invariant_failures:
        raise BenchmarkContractError("S0_INVARIANT_FAILURE")
    if evidence.accidental_semantic_duplicates:
        raise BenchmarkContractError("S0_SEMANTIC_DUPLICATE")
    if evidence.recovery_pressure not in {"GREEN"}:
        raise BenchmarkContractError("S0_BACKLOG_NOT_RECOVERED_BELOW_YELLOW")


def validate_w7d(evidence: SevenDayCostEvidence) -> dict[str, float]:
    if evidence.measurement_class != ACCELERATED_REPLAY:
        raise BenchmarkContractError("W7D_ACCELERATED_REPLAY_REQUIRED")
    if tuple(evidence.hourly_slices) != tuple(range(168)):
        raise BenchmarkContractError("W7D_EXACT_168_HOURLY_SLICES_REQUIRED")
    if not evidence.raw_events:
        raise BenchmarkContractError("W7D_RAW_COST_EVENTS_REQUIRED")
    overhead = 0.0
    substantive = 0.0
    hours_seen: set[int] = set()
    for event in evidence.raw_events:
        if event.hour not in range(168):
            raise BenchmarkContractError("W7D_COST_EVENT_HOUR_OUT_OF_RANGE")
        if event.unit not in {"PIU", "PRU", "PAU"}:
            raise BenchmarkContractError("W7D_UNKNOWN_COST_UNIT")
        if event.classification not in {"OVERHEAD", "SUBSTANTIVE"}:
            raise BenchmarkContractError("W7D_UNKNOWN_COST_CLASSIFICATION")
        if not isinstance(event.count, int) or isinstance(event.count, bool) or event.count < 0:
            raise BenchmarkContractError("W7D_INVALID_COST_COUNT")
        hours_seen.add(event.hour)
        if event.classification == "OVERHEAD":
            overhead += float(event.count)
        else:
            substantive += float(event.count)
    if hours_seen != set(range(168)):
        raise BenchmarkContractError("W7D_RAW_EVENT_HOUR_COVERAGE_INCOMPLETE")
    if substantive <= 0:
        raise BenchmarkContractError("W7D_SUBSTANTIVE_COST_ZERO")
    ratio = overhead / substantive
    if abs(evidence.reported_overhead_cost - overhead) > 1e-9:
        raise BenchmarkContractError("W7D_OVERHEAD_RECOMPUTE_MISMATCH")
    if abs(evidence.reported_substantive_cost - substantive) > 1e-9:
        raise BenchmarkContractError("W7D_SUBSTANTIVE_RECOMPUTE_MISMATCH")
    if abs(evidence.reported_ratio - ratio) > 1e-12:
        raise BenchmarkContractError("W7D_RATIO_RECOMPUTE_MISMATCH")
    if ratio > 0.10:
        raise BenchmarkContractError("W7D_COST_RATIO_TARGET_MISS")
    return {"overhead_cost": overhead, "substantive_cost": substantive, "independent_ratio": ratio}


def validate_monthly_availability_claim(value: str) -> str:
    if value != MONTHLY_NOT_CLAIMED:
        raise BenchmarkContractError("MONTHLY_AVAILABILITY_CANNOT_BE_CLAIMED_PRELAUNCH")
    return value
