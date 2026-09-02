from __future__ import annotations

import unittest
from pathlib import Path


class CpI09WorkflowContractTests(unittest.TestCase):
    def test_workflow_has_exact_long_window_evidence_topology(self):
        text = Path(".github/workflows/control-plane-cp-i09.yml").read_text(encoding="utf-8")

        for job in (
            "contract-regression:",
            "r0-real-wall-clock:",
            "s0-real-wall-clock:",
            "cost-168h-accelerated:",
            "combine-and-verify:",
        ):
            self.assertIn(job, text)

        self.assertGreaterEqual(
            text.count('ref: ${{ github.event.pull_request.head.sha || github.sha }}'),
            5,
        )
        self.assertIn("--profile r0", text)
        self.assertIn("--profile s0", text)
        self.assertIn("tests.control_plane.cp_i09_cost", text)
        self.assertIn("tests.control_plane.generate_cp_i09_evidence", text)
        self.assertIn("actions/upload-artifact@v4", text)
        self.assertIn("actions/download-artifact@v4", text)
        self.assertIn("cp-i09-r0-${{ github.event.pull_request.head.sha || github.sha }}", text)
        self.assertIn("cp-i09-s0-${{ github.event.pull_request.head.sha || github.sha }}", text)
        self.assertIn("cp-i09-w7d-${{ github.event.pull_request.head.sha || github.sha }}", text)
        self.assertIn("cp-i09-evidence-${{ github.event.pull_request.head.sha || github.sha }}", text)

        self.assertNotIn("monthly_availability_attainment: PASS", text)
        self.assertNotIn("p34_gate_pass: true", text)


if __name__ == "__main__":
    unittest.main()
