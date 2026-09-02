from __future__ import annotations

import threading
import time
import unittest

# P36 evidence: S0 must preserve the offered-load window while recoverable backlog drains later.


class CpI09S0AdmissionTests(unittest.TestCase):
    def test_recoverable_s0_backlog_does_not_throttle_offered_load(self):
        from tests.control_plane.cp_i09_benchmark import ScheduledFamily

        abort = threading.Event()

        def slow_operation(_seq):
            time.sleep(0.25)
            return {}

        family = ScheduledFamily(
            name="s0-load-probe",
            rate=8,
            duration=1,
            operation=slow_operation,
            workers=1,
            abort_event=abort,
            backlog_seconds=0.1,
            admission_timeout_seconds=0.01,
            recoverable_backlog=True,
        )
        started = time.monotonic()
        family.schedule_until(started)
        offered = family.snapshot()

        self.assertFalse(abort.is_set())
        self.assertIsNone(offered["scheduling_blocker"])
        self.assertEqual(offered["planned_count"], offered["scheduled_count"])
        self.assertLess(offered["schedule_window_overrun_seconds"], 0.1)
        self.assertGreater(offered["pending_count"], 0)

        family.wait()
        recovered = family.snapshot()
        self.assertEqual(recovered["planned_count"], recovered["completed_count"])
        self.assertEqual(0, recovered["failed_count"])
        self.assertEqual(0, recovered["pending_count"])


if __name__ == "__main__":
    unittest.main()
