from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class CpI09ProgressTests(unittest.TestCase):
    def test_interrupted_progress_write_preserves_last_valid_snapshot(self):
        from tests.control_plane.cp_i09_progress import write_progress_snapshot

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s0-progress.json"
            path.write_text('{"generation": 1}\n', encoding="utf-8")

            with patch("tests.control_plane.cp_i09_progress.os.replace", side_effect=RuntimeError("simulated interruption")):
                with self.assertRaises(RuntimeError):
                    write_progress_snapshot(path, {"generation": 2})

            self.assertEqual({"generation": 1}, json.loads(path.read_text(encoding="utf-8")))

    def test_progress_snapshot_exposes_required_s0_diagnostics_and_provenance(self):
        from tests.control_plane.cp_i09_progress import build_progress_snapshot

        family = {
            "planned_count": 720000,
            "scheduled_count": 612345,
            "completed_count": 600000,
            "failed_count": 0,
            "pending_count": 12345,
            "pending_peak": 15000,
            "schedule_window_overrun_seconds": 42.5,
            "scheduling_blocker": None,
        }
        payload = build_progress_snapshot(
            profile="s0",
            phase="STRESS",
            elapsed_wall_seconds=901.25,
            result_revision="deadbeef",
            package_id="CP-I09-P31-01",
            package_ref="pkgref",
            task_anchor={"revision": "anchor", "relation": "ancestor"},
            family_snapshots={"projection_evaluations_per_second": family},
            abort_reason=None,
            resource_observation={"max_rss_kb": 123456},
        )

        self.assertEqual("CP-I09-S0-PROGRESS", payload["kind"])
        self.assertEqual("deadbeef", payload.get("result_revision"))
        self.assertEqual("pkgref", payload.get("package_ref"))
        self.assertEqual({"revision": "anchor", "relation": "ancestor"}, payload.get("task_anchor"))
        self.assertEqual("STRESS", payload.get("phase"))
        self.assertEqual(901.25, payload.get("elapsed_wall_seconds"))
        self.assertEqual(family, payload.get("families", {}).get("projection_evaluations_per_second"))
        self.assertEqual({"max_rss_kb": 123456}, payload.get("resource_observation"))
        self.assertIsNone(payload.get("abort_reason"))

    def test_progress_reporter_updates_before_execution_finishes(self):
        import time
        from tests.control_plane import cp_i09_progress

        reporter_type = getattr(cp_i09_progress, "ProgressReporter", None)
        self.assertIsNotNone(reporter_type)
        if reporter_type is None:
            return

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s0-progress.json"
            generation = [0]

            def snapshot(phase):
                generation[0] += 1
                return {"phase": phase, "generation": generation[0]}

            reporter = reporter_type(path, snapshot, interval_seconds=0.01)
            reporter.start("STRESS")
            deadline = time.monotonic() + 1.0
            first = json.loads(path.read_text(encoding="utf-8"))
            while first.get("generation", 0) < 2 and time.monotonic() < deadline:
                time.sleep(0.005)
                first = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("STRESS", first["phase"])
            self.assertGreaterEqual(first["generation"], 2)

            reporter.set_phase("DRAINING")
            second = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("DRAINING", second["phase"])
            reporter.stop("COMPLETE")
            final = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("COMPLETE", final["phase"])

    def test_s0_benchmark_wires_periodic_progress_and_recovery_phase(self):
        source = Path("tests/control_plane/cp_i09_benchmark.py").read_text(encoding="utf-8")
        self.assertIn("ProgressReporter", source)
        self.assertIn('progress_path=output_dir / "s0-progress.json"', source)
        self.assertIn('reporter.set_phase("DRAINING")', source)
        self.assertIn('reporter.stop("EXECUTION_COMPLETE")', source)

    def test_workflow_separates_timeout_diagnostics_from_exact_s0_evidence(self):
        workflow = Path(".github/workflows/control-plane-cp-i09.yml").read_text(encoding="utf-8")
        s0 = workflow.split("s0-real-wall-clock:", 1)[1].split("cost-168h-accelerated:", 1)[0]
        self.assertIn("timeout-minutes: 90", s0)
        for name in ("s0-workload-manifest.json", "s0-raw-timeseries.json", "s0-stress.json"):
            self.assertIn(f"artifacts/s0/{name}", s0)
        self.assertIn("cp-i09-s0-progress-", s0)
        self.assertIn("artifacts/s0/s0-progress.json", s0)
        main_upload = s0.split("name: Upload S0 evidence", 1)[1].split("name: Upload S0 diagnostic progress", 1)[0]
        self.assertNotIn("s0-progress.json", main_upload)


if __name__ == "__main__":
    unittest.main()
