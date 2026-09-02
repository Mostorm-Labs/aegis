from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch


class CpI09HarnessTests(unittest.TestCase):
    def test_scheduler_fails_closed_when_offered_load_backlog_capacity_exhausts(self):
        from tests.control_plane.cp_i09_benchmark import ScheduledFamily

        abort = threading.Event()

        def slow_operation(_seq):
            time.sleep(0.2)
            return {}

        family = ScheduledFamily(
            name="load-probe",
            rate=20,
            duration=1,
            operation=slow_operation,
            workers=1,
            abort_event=abort,
            backlog_seconds=0.1,
            admission_timeout_seconds=0.01,
        )
        started = time.monotonic()
        family.schedule_until(started)
        family.wait()
        snapshot = family.snapshot()

        self.assertTrue(abort.is_set())
        self.assertEqual("OFFERED_LOAD_BACKLOG_CAPACITY_EXHAUSTED", snapshot["scheduling_blocker"])
        self.assertLess(snapshot["scheduled_count"], snapshot["planned_count"])

    def test_distinct_outboxes_can_enter_dispatch_concurrently(self):
        from tests.control_plane.cp_i09_benchmark import _build_operations
        from tools.aegis_control.execution_surface import DispatchReceipt
        from tools.aegis_control.store import ControlStore

        with tempfile.TemporaryDirectory() as tmp:
            operations, _runtime = _build_operations(
                ControlStore(str(Path(tmp) / "control.sqlite")),
                profile="s0",
            )
            dispatch_op = operations["outbox_dispatch_attempts_per_second"]
            entered = threading.Barrier(2)

            def overlapping_dispatch(_self, _outbox_id, *, attempted_at):
                self.assertTrue(attempted_at)
                entered.wait(timeout=1.0)
                time.sleep(0.02)
                return DispatchReceipt("synthetic-occurrence", "synthetic-correlation", True)

            with patch("tools.aegis_control.dispatch.DispatchService.dispatch", new=overlapping_dispatch):
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [executor.submit(dispatch_op, seq) for seq in (0, 1)]
                    for future in futures:
                        future.result(timeout=2.0)

    def test_w7d_generator_materializes_exact_168_hour_raw_recomputable_workload(self):
        from tests.control_plane.cp_i09_cost import build_cost_evidence

        workload, hourly, raw, model, result = build_cost_evidence(result_revision="r" * 40)
        self.assertEqual("ACCELERATED_REPLAY", workload["measurement_class"])
        self.assertEqual(168, workload["logical_window_hours"])
        self.assertEqual(list(range(168)), [row["hour"] for row in hourly["rows"]])
        self.assertEqual(168 * 6, len(raw["rows"]))
        self.assertEqual("CP-I09-REFERENCE-NORMALIZED-V1", model["cost_model_id"])
        self.assertAlmostEqual(0.07, result["independent_recompute"]["independent_ratio"])
        self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
