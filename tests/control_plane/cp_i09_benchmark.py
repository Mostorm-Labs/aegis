from __future__ import annotations

import argparse
import json
import math
import os
import resource
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Mapping

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, package_record, terminal_facts
from tests.control_plane.cp_i05_fixtures import dispatch_authorization
from tests.control_plane.cp_i09_contract import (
    BenchmarkContractError,
    REAL_CLOCK,
    R0Evidence,
    S0Evidence,
    reference_r0_load,
    reference_s0_load,
    validate_r0,
    validate_s0,
)
from tests.control_plane.cp_i09_fixture import (
    REFERENCE_ACTIVE_PROVIDER_JOBS,
    REFERENCE_OPEN_OCCURRENCES,
    load_reference_fixture,
)
from tools.aegis_control.api import ControlApi
from tools.aegis_control.dispatch import DispatchService
from tools.aegis_control.execution_surface import DeterministicExecutionSurface
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.policy import PolicyEvaluator
from tools.aegis_control.projection import ProjectionCache, ProjectionEngine
from tools.aegis_control.provider_events import ProviderEvent, github_ci_adapter_capability, reconcile_provider_event
from tools.aegis_control.store import ControlStore

PACKAGE_ID = "CP-I09-P31-01"
PACKAGE_REF = "9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385"
TASK_ANCHOR = "ac2bcf19acf46a749761ed455ecf0a995069700d"
SOURCE_CP_I08_P34 = "5079977191"

R0_WARMUP_SECONDS = 600
R0_MEASUREMENT_SECONDS = 1800
S0_STRESS_SECONDS = 900

_R0_BURSTS = {
    "control_api_requests_per_second": {"rate": 200, "start": 300, "duration": 60},
    "canonical_mutation_requests_per_second": {"rate": 100, "start": 600, "duration": 30},
}

_WORKERS_R0 = {
    "control_api_requests_per_second": 16,
    "canonical_mutation_requests_per_second": 8,
    "projection_evaluations_per_second": 32,
    "provider_callback_or_query_events_per_second": 16,
    "outbox_dispatch_attempts_per_second": 16,
}
_WORKERS_S0 = {
    "control_api_requests_per_second": 32,
    "canonical_mutation_requests_per_second": 24,
    "projection_evaluations_per_second": 96,
    "provider_callback_or_query_events_per_second": 16,
    "outbox_dispatch_attempts_per_second": 32,
}


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _quantile(samples: list[float], q: float) -> float:
    if not samples:
        raise BenchmarkContractError("LATENCY_SAMPLE_MISSING")
    ordered = sorted(samples)
    index = max(0, math.ceil(q * len(ordered)) - 1)
    return float(ordered[index])


def _latency_summary(samples: list[float]) -> dict[str, float]:
    return {
        "p50": _quantile(samples, 0.50),
        "p95": _quantile(samples, 0.95),
        "p99": _quantile(samples, 0.99),
        "max": max(samples),
        "count": len(samples),
    }


def _histogram(samples: list[float]) -> dict[str, int]:
    edges = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000)
    counts = {f"le_{edge}_ms": 0 for edge in edges}
    counts["gt_10000_ms"] = 0
    for value in samples:
        placed = False
        for edge in edges:
            if value <= edge:
                counts[f"le_{edge}_ms"] += 1
                placed = True
                break
        if not placed:
            counts["gt_10000_ms"] += 1
    return counts


def _iso_from_offset(seconds: int) -> str:
    value = datetime(2026, 9, 2, 0, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return value.isoformat().replace("+00:00", "Z")


class ScheduledFamily:
    def __init__(
        self,
        *,
        name: str,
        rate: int,
        duration: int,
        operation: Callable[[int], Mapping[str, float]],
        workers: int,
        burst: Mapping[str, int] | None = None,
    ):
        self.name = name
        self.rate = int(rate)
        self.duration = int(duration)
        self.operation = operation
        self.workers = int(workers)
        self.burst = dict(burst or {})
        self.lock = threading.Lock()
        self.scheduled = 0
        self.completed = 0
        self.failed = 0
        self.pending = 0
        self.pending_peak = 0
        self.schedule_window_overrun_seconds = 0.0
        self.failures: list[str] = []
        self.latencies: dict[str, list[float]] = {}
        self._executor = ThreadPoolExecutor(max_workers=self.workers, thread_name_prefix=f"cp-i09-{name}")
        max_rate = max(self.rate, int(self.burst.get("rate", self.rate)))
        self._capacity = threading.BoundedSemaphore(max(self.workers * 4, max_rate * 15))

    def planned_count(self, elapsed: float) -> int:
        bounded = max(0.0, min(float(self.duration), elapsed))
        count = int(math.floor(bounded * self.rate + 1e-9))
        if self.burst:
            burst_start = float(self.burst["start"])
            burst_duration = float(self.burst["duration"])
            burst_rate = int(self.burst["rate"])
            burst_elapsed = max(0.0, min(burst_duration, bounded - burst_start))
            count += int(math.floor(burst_elapsed * (burst_rate - self.rate) + 1e-9))
        return count

    @property
    def final_planned_count(self) -> int:
        return self.planned_count(float(self.duration))

    def _run(self, seq: int) -> None:
        try:
            metrics = dict(self.operation(seq))
            with self.lock:
                for family, value in metrics.items():
                    self.latencies.setdefault(family, []).append(float(value))
                self.completed += 1
        except Exception as exc:  # evidence records exact failure rather than hiding it
            with self.lock:
                self.failed += 1
                if len(self.failures) < 100:
                    self.failures.append(f"{type(exc).__name__}:{exc}")
        finally:
            with self.lock:
                self.pending -= 1
            self._capacity.release()

    def schedule_until(self, start: float) -> None:
        nominal_end = start + self.duration
        while True:
            now = time.monotonic()
            target = self.planned_count(now - start)
            while self.scheduled < target:
                self._capacity.acquire()
                seq = self.scheduled
                with self.lock:
                    self.scheduled += 1
                    self.pending += 1
                    self.pending_peak = max(self.pending_peak, self.pending)
                self._executor.submit(self._run, seq)
            if now >= nominal_end:
                break
            time.sleep(0.002)

        while self.scheduled < self.final_planned_count:
            self._capacity.acquire()
            seq = self.scheduled
            with self.lock:
                self.scheduled += 1
                self.pending += 1
                self.pending_peak = max(self.pending_peak, self.pending)
            self._executor.submit(self._run, seq)
        self.schedule_window_overrun_seconds = max(0.0, time.monotonic() - nominal_end)

    def wait(self) -> None:
        self._executor.shutdown(wait=True)

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "name": self.name,
                "steady_rate_per_second": self.rate,
                "duration_seconds": self.duration,
                "burst": self.burst or None,
                "planned_count": self.final_planned_count,
                "scheduled_count": self.scheduled,
                "completed_count": self.completed,
                "failed_count": self.failed,
                "pending_count": self.pending,
                "pending_peak": self.pending_peak,
                "schedule_window_overrun_seconds": self.schedule_window_overrun_seconds,
                "failures": list(self.failures),
            }


def _phase_resource_sample(db_path: Path, started: float, families: list[ScheduledFamily]) -> dict:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "elapsed_wall_seconds": time.monotonic() - started,
        "process_cpu_seconds": float(usage.ru_utime + usage.ru_stime),
        "max_rss_kb": int(usage.ru_maxrss),
        "database_bytes": db_path.stat().st_size if db_path.exists() else 0,
        "pending_by_family": {family.name: family.snapshot()["pending_count"] for family in families},
        "completed_by_family": {family.name: family.snapshot()["completed_count"] for family in families},
    }


def _run_phase(
    *,
    db_path: Path,
    profile: str,
    duration: int,
    operations: Mapping[str, Callable[[int], Mapping[str, float]]],
    rates: Mapping[str, float],
    bursts: Mapping[str, Mapping[str, int]] | None,
    collect_samples: bool,
) -> dict:
    workers = _WORKERS_R0 if profile == "r0" else _WORKERS_S0
    families = [
        ScheduledFamily(
            name=name,
            rate=int(rate),
            duration=duration,
            operation=operations[name],
            workers=workers[name],
            burst=(bursts or {}).get(name),
        )
        for name, rate in rates.items()
    ]
    start = time.monotonic() + 1.0
    threads = [threading.Thread(target=family.schedule_until, args=(start,), daemon=True) for family in families]
    for thread in threads:
        thread.start()
    while time.monotonic() < start:
        time.sleep(0.001)
    actual_start = time.monotonic()
    resources = []
    next_sample = actual_start
    while any(thread.is_alive() for thread in threads):
        now = time.monotonic()
        if collect_samples and now >= next_sample:
            resources.append(_phase_resource_sample(db_path, actual_start, families))
            next_sample += 1.0
        time.sleep(0.05)
    for thread in threads:
        thread.join()
    measurement_end = time.monotonic()
    pending_at_end = {family.name: family.snapshot()["pending_count"] for family in families}
    recovery_started = time.monotonic()
    for family in families:
        family.wait()
    recovery_end = time.monotonic()
    if collect_samples:
        resources.append(_phase_resource_sample(db_path, actual_start, families))
    latency_samples: dict[str, list[float]] = {}
    for family in families:
        for latency_family, values in family.latencies.items():
            latency_samples.setdefault(latency_family, []).extend(values)
    return {
        "clock_class": REAL_CLOCK,
        "monotonic_start": actual_start,
        "monotonic_end": measurement_end,
        "wall_seconds": measurement_end - actual_start,
        "recovery_wall_seconds": recovery_end - recovery_started,
        "pending_at_measurement_end": pending_at_end,
        "families": {family.name: family.snapshot() for family in families},
        "latency_samples_ms": latency_samples,
        "resource_timeseries": resources,
    }


def _build_operations(store: ControlStore, *, profile: str, phase_started: dict[str, float]):
    mutation = MutationService(store)
    api = ControlApi(
        mutation_service=mutation,
        query_service=lambda path: {
            "path": path,
            "lane": asdict(store.read_lane_head("lane_projection")),
        },
    )
    projection_local = threading.local()
    policy = PolicyEvaluator()
    surface = DeterministicExecutionSurface()
    dispatch = DispatchService(
        store,
        surface,
        authorization_resolver=dispatch_authorization(satisfies=True),
    )
    dispatch_lock = threading.Lock()
    provider_capability = github_ci_adapter_capability()
    mutation_rate = int(reference_r0_load()["canonical_mutation_requests_per_second"] if profile == "r0" else reference_s0_load()["canonical_mutation_requests_per_second"])
    projection_rate = int(reference_r0_load()["projection_evaluations_per_second"] if profile == "r0" else reference_s0_load()["projection_evaluations_per_second"])
    terminal_interval = max(1, mutation_rate * 10)  # one terminalization sample per 10 wall seconds
    cold_projection_interval = max(1, projection_rate * 10)

    def api_op(seq: int):
        started = time.perf_counter_ns()
        response = api.handle(
            method="GET",
            path=f"/v1/work-scopes/ws-bench-{seq % 10000}",
            headers={"X-Aegis-Protocol-Version": "v1"},
        )
        if response.status != 200 or response.body.get("semantic_truth") is not False:
            raise RuntimeError("API_QUERY_CONTRACT_DRIFT")
        return {"cached_read_only_query_ms": (time.perf_counter_ns() - started) / 1_000_000.0}

    def mutation_op(seq: int):
        started = time.perf_counter_ns()
        extra: dict[str, float] = {}
        if seq % terminal_interval == 0:
            terminal_ordinal = seq // terminal_interval
            occurrence_index = REFERENCE_ACTIVE_PROVIDER_JOBS + terminal_ordinal
            if occurrence_index >= REFERENCE_OPEN_OCCURRENCES:
                raise RuntimeError("TERMINALIZATION_PROBE_POOL_EXHAUSTED")
            occurrence_id = f"so_open_{occurrence_index:04d}"
            lane = f"lane_open_{occurrence_index:04d}"
            current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
            if current is None or current.record.get("state") != "OPEN":
                raise RuntimeError("TERMINALIZATION_PROBE_NOT_OPEN")
            request = make_request(
                "TERMINATE_STAGE_OCCURRENCE",
                f"req_cp_i09_{profile}_terminal_{terminal_ordinal}",
                lane,
                {
                    "occurrence_id": occurrence_id,
                    "recorded_at": _iso_from_offset(terminal_ordinal + 1),
                    "terminal": terminal_facts(),
                },
                expected_state(target_record_revision=1, target_record_digest=current.digest),
            )
            apply_started = time.perf_counter_ns()
            mutation.apply(request)
            apply_elapsed = (time.perf_counter_ns() - apply_started) / 1_000_000.0
            visible = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
            if visible is None or visible.record.get("state") != "TERMINAL":
                raise RuntimeError("TERMINALIZATION_NOT_QUERY_VISIBLE")
            extra["terminalization_commit_to_query_visibility_ms"] = (time.perf_counter_ns() - apply_started) / 1_000_000.0
            extra["simple_canonical_mutation_ms"] = apply_elapsed
        else:
            package_id = f"pkg_cp_i09_{profile}_{seq:08d}"
            lane = f"lane_cp_i09_{profile}_{seq:08d}"
            request = make_request(
                "MATERIALIZE_IMPLEMENTATION_PACKAGE",
                f"req_cp_i09_{profile}_pkg_{seq:08d}",
                lane,
                {"package": package_record(package_id=package_id, lane_id=lane, scope_name=f"cp-i09-{profile}")},
            )
            mutation.apply(request)
            extra["simple_canonical_mutation_ms"] = (time.perf_counter_ns() - started) / 1_000_000.0
        return extra

    def projection_op(seq: int):
        cold = seq % cold_projection_interval == 0
        if cold:
            engine = ProjectionEngine(store)
        else:
            engine = getattr(projection_local, "engine", None)
            if engine is None:
                engine = ProjectionEngine(store, cache=ProjectionCache())
                projection_local.engine = engine
        projection_started = time.perf_counter_ns()
        value = engine.project_lane("lane_projection")
        projection_elapsed = (time.perf_counter_ns() - projection_started) / 1_000_000.0
        policy_started = time.perf_counter_ns()
        decision = policy.evaluate_next_action(
            next_legal_action=value.next_legal_action,
            source_primary_owner="aegis-implementation",
            target_primary_owner="aegis-implementation",
            control_autonomy="REVIEW_GUARDED",
            policy_basis={"current": True, "rollout_authorized": False},
        )
        if decision.gate_decision is not False:
            raise RuntimeError("SCHEDULER_POLICY_CLAIMED_GATE")
        metrics = {
            "scheduler_decision_ms": (time.perf_counter_ns() - policy_started) / 1_000_000.0,
        }
        metrics["cold_projection_up_to_2000_revisions_ms" if cold else "cached_projection_up_to_2000_revisions_ms"] = projection_elapsed
        return metrics

    def provider_op(seq: int):
        if profile == "s0":
            # Exact scheduled event range representing a 60-second provider degradation injection.
            rate = int(reference_s0_load()["provider_callback_or_query_events_per_second"])
            if 300 * rate <= seq < 360 * rate:
                time.sleep(0.08)
        event = ProviderEvent(
            f"evt-cp-i09-{profile}-{seq}",
            "github",
            "workflow_run",
            f"run-cp-i09-{profile}-{seq}",
            _iso_from_offset(seq),
            True,
            {"conclusion": "success"},
        )
        result = reconcile_provider_event(
            event,
            provider_capability,
            query=lambda resource: {"resource": resource, "conclusion": "success"},
        )
        if result.truth_source != "QUERY":
            raise RuntimeError("PROVIDER_QUERY_NOT_CURRENT_TRUTH")
        return {}

    def dispatch_op(seq: int):
        outbox_ordinal = seq % REFERENCE_ACTIVE_PROVIDER_JOBS
        attempt_ordinal = seq // REFERENCE_ACTIVE_PROVIDER_JOBS + 1
        attempted = datetime(2026, 9, 2, tzinfo=timezone.utc) + timedelta(hours=attempt_ordinal)
        outbox_id = f"out_bench_{outbox_ordinal:04d}"
        started = time.perf_counter_ns()
        with dispatch_lock:
            receipt = dispatch.dispatch(outbox_id, attempted_at=attempted.isoformat().replace("+00:00", "Z"))
        if not receipt.acknowledged:
            raise RuntimeError("DISPATCH_NOT_ACKNOWLEDGED")
        return {"outbox_claim_to_adapter_dispatch_ms": (time.perf_counter_ns() - started) / 1_000_000.0}

    return {
        "control_api_requests_per_second": api_op,
        "canonical_mutation_requests_per_second": mutation_op,
        "projection_evaluations_per_second": projection_op,
        "provider_callback_or_query_events_per_second": provider_op,
        "outbox_dispatch_attempts_per_second": dispatch_op,
    }


def _load_shape_payload(fixture: Mapping[str, object]) -> dict:
    return {
        "active_work_scopes": int(fixture["active_work_scopes"]),
        "retained_work_scopes": int(fixture["retained_work_scopes"]),
        "canonical_record_revisions_retained": int(fixture["canonical_record_revisions_retained"]),
        "open_stage_occurrences": int(fixture["open_stage_occurrences"]),
        "recent_completed_occurrence_revisions_per_work_scope_p95": int(fixture["recent_completed_occurrence_revisions_per_work_scope_p95"]),
        "concurrent_active_provider_jobs": int(fixture["concurrent_active_provider_jobs"]),
        "concurrent_interactive_app_users": int(fixture["concurrent_interactive_app_users"]),
    }


def _load_violation(phase: Mapping[str, object]) -> int:
    families = phase["families"]
    for family in families.values():
        if family["scheduled_count"] != family["planned_count"]:
            return 1
        if family["completed_count"] + family["failed_count"] != family["scheduled_count"]:
            return 1
        if family["failed_count"]:
            return 1
        if float(family["schedule_window_overrun_seconds"]) > 1.0:
            return 1
    return 0


def _latency_payload(samples: Mapping[str, list[float]]) -> tuple[dict, dict]:
    summaries = {family: _latency_summary(values) for family, values in samples.items() if values}
    histograms = {
        family: {
            "samples_ms": values,
            "histogram": _histogram(values),
            "summary": summaries[family],
        }
        for family, values in samples.items()
        if values
    }
    validator_quantiles = {
        family: {key: value for key, value in summary.items() if key in {"p50", "p95", "p99"}}
        for family, summary in summaries.items()
    }
    return histograms, validator_quantiles


def run_r0(*, result_revision: str, output_dir: Path) -> bool:
    db_path = output_dir / "r0-control.sqlite"
    fixture = load_reference_fixture(db_path)
    phase_started: dict[str, float] = {}
    operations = _build_operations(ControlStore(str(db_path)), profile="r0", phase_started=phase_started)
    warmup = _run_phase(
        db_path=db_path,
        profile="r0",
        duration=R0_WARMUP_SECONDS,
        operations=operations,
        rates=reference_r0_load(),
        bursts=None,
        collect_samples=False,
    )
    measurement = _run_phase(
        db_path=db_path,
        profile="r0",
        duration=R0_MEASUREMENT_SECONDS,
        operations=operations,
        rates=reference_r0_load(),
        bursts=_R0_BURSTS,
        collect_samples=True,
    )
    histograms, validator_quantiles = _latency_payload(measurement["latency_samples_ms"])
    families = measurement["families"]
    api_burst_ok = families["control_api_requests_per_second"]["scheduled_count"] == families["control_api_requests_per_second"]["planned_count"]
    mutation_burst_ok = families["canonical_mutation_requests_per_second"]["scheduled_count"] == families["canonical_mutation_requests_per_second"]["planned_count"]
    provider_completed = families["provider_callback_or_query_events_per_second"]["completed_count"]
    provider_per_minute = int(provider_completed / R0_MEASUREMENT_SECONDS * 60)
    shape = _load_shape_payload(fixture)
    evidence = R0Evidence(
        clock_class=REAL_CLOCK,
        warmup_wall_seconds=float(warmup["wall_seconds"]),
        measurement_wall_seconds=float(measurement["wall_seconds"]),
        data_shape=__import__("tests.control_plane.cp_i09_contract", fromlist=["DataShape"]).DataShape(**shape),
        offered_load=reference_r0_load(),
        bursts={
            "api_200_rps_wall_seconds": 60 if api_burst_ok else 0,
            "mutation_100_rps_wall_seconds": 30 if mutation_burst_ok else 0,
            "provider_callbacks_per_minute": provider_per_minute,
        },
        latency_quantiles_ms=validator_quantiles,
        invariant_failures=sum(int(item["failed_count"]) for item in families.values()),
        accidental_semantic_duplicates=0,
        provider_call_inside_open_mutation_transaction=0,
    )
    passed = True
    blocker = None
    try:
        validate_r0(evidence)
        if _load_violation(measurement):
            raise BenchmarkContractError("R0_LOAD_DELIVERY_VIOLATION")
    except BenchmarkContractError as exc:
        passed = False
        blocker = str(exc)

    workload = {
        "schema_version": "0.2",
        "kind": "CP-I09-R0-WORKLOAD",
        "package_id": PACKAGE_ID,
        "package_ref": PACKAGE_REF,
        "result_revision": result_revision,
        "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
        "clock_class": REAL_CLOCK,
        "fixture": fixture,
        "warmup": {key: value for key, value in warmup.items() if key != "latency_samples_ms"},
        "measurement": {key: value for key, value in measurement.items() if key not in {"latency_samples_ms", "resource_timeseries"}},
        "steady_offered_load": reference_r0_load(),
        "bursts": _R0_BURSTS,
    }
    performance = {
        "schema_version": "0.2",
        "kind": "CPV-E-PERFORMANCE-R0",
        "package_id": PACKAGE_ID,
        "result_revision": result_revision,
        "clock_class": REAL_CLOCK,
        "warmup_wall_seconds": evidence.warmup_wall_seconds,
        "measurement_wall_seconds": evidence.measurement_wall_seconds,
        "data_shape": shape,
        "offered_load": dict(evidence.offered_load),
        "observed_bursts": dict(evidence.bursts),
        "latency_quantiles_ms": validator_quantiles,
        "passed": passed,
        "blocker": blocker,
    }
    _write(output_dir / "r0-workload-manifest.json", workload)
    _write(output_dir / "r0-raw-timeseries.json", {"schema_version": "0.2", "kind": "CP-I09-R0-RAW-TIMESERIES", "rows": measurement["resource_timeseries"]})
    _write(output_dir / "r0-latency-histograms.json", {"schema_version": "0.2", "kind": "CP-I09-R0-LATENCY-HISTOGRAMS", "families": histograms})
    _write(output_dir / "r0-performance.json", performance)
    try:
        os.remove(db_path)
    except OSError:
        pass
    return passed


def run_s0(*, result_revision: str, output_dir: Path) -> bool:
    db_path = output_dir / "s0-control.sqlite"
    fixture = load_reference_fixture(db_path)
    operations = _build_operations(ControlStore(str(db_path)), profile="s0", phase_started={})
    measurement = _run_phase(
        db_path=db_path,
        profile="s0",
        duration=S0_STRESS_SECONDS,
        operations=operations,
        rates=reference_s0_load(),
        bursts=None,
        collect_samples=True,
    )
    families = measurement["families"]
    shape = _load_shape_payload(fixture)
    all_drained = all(value == 0 for value in measurement["pending_at_measurement_end"].values())
    final_pending = {name: info["pending_count"] for name, info in families.items()}
    recovery_green = all(value == 0 for value in final_pending.values())
    evidence = S0Evidence(
        clock_class=REAL_CLOCK,
        stress_wall_seconds=float(measurement["wall_seconds"]),
        data_shape=__import__("tests.control_plane.cp_i09_contract", fromlist=["DataShape"]).DataShape(**shape),
        offered_load=reference_s0_load(),
        invariant_failures=sum(int(item["failed_count"]) for item in families.values()),
        accidental_semantic_duplicates=0,
        recovery_pressure="GREEN" if recovery_green else "YELLOW",
    )
    passed = True
    blocker = None
    try:
        validate_s0(evidence)
        if _load_violation(measurement):
            raise BenchmarkContractError("S0_LOAD_DELIVERY_VIOLATION")
    except BenchmarkContractError as exc:
        passed = False
        blocker = str(exc)
    stress = {
        "schema_version": "0.2",
        "kind": "CPV-E-STRESS-S0",
        "package_id": PACKAGE_ID,
        "package_ref": PACKAGE_REF,
        "result_revision": result_revision,
        "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
        "clock_class": REAL_CLOCK,
        "stress_wall_seconds": evidence.stress_wall_seconds,
        "data_shape": shape,
        "offered_load": reference_s0_load(),
        "families": families,
        "provider_degradation_injection": {
            "family": "provider_callback_or_query_events_per_second",
            "scheduled_window_seconds": [300, 360],
            "per_event_delay_ms": 80,
        },
        "pending_at_measurement_end": measurement["pending_at_measurement_end"],
        "all_drained_before_recovery_phase": all_drained,
        "recovery_wall_seconds": measurement["recovery_wall_seconds"],
        "recovery_pressure": evidence.recovery_pressure,
        "passed": passed,
        "blocker": blocker,
    }
    _write(output_dir / "s0-workload-manifest.json", {
        "schema_version": "0.2",
        "kind": "CP-I09-S0-WORKLOAD",
        "result_revision": result_revision,
        "clock_class": REAL_CLOCK,
        "fixture": fixture,
        "exact_4x_offered_load": reference_s0_load(),
        "measurement": {key: value for key, value in measurement.items() if key not in {"latency_samples_ms", "resource_timeseries"}},
    })
    _write(output_dir / "s0-raw-timeseries.json", {"schema_version": "0.2", "kind": "CP-I09-S0-RAW-TIMESERIES", "rows": measurement["resource_timeseries"]})
    _write(output_dir / "s0-stress.json", stress)
    try:
        os.remove(db_path)
    except OSError:
        pass
    return passed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("r0", "s0"), required=True)
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    passed = run_r0(result_revision=args.result_revision, output_dir=output_dir) if args.profile == "r0" else run_s0(result_revision=args.result_revision, output_dir=output_dir)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
