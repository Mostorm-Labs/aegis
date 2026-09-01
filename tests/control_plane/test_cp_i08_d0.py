from __future__ import annotations

import unittest


class CpI08D0RedTests(unittest.TestCase):
    def test_integrated_d0_covers_exact_g01_g44_and_m01_m20(self):
        from tests.control_plane.cp_i08_d0 import run_integrated_d0
        result = run_integrated_d0()
        self.assertEqual([f"G{i:02d}" for i in range(1, 45)], sorted(result["golden_results"]))
        self.assertTrue(all(item["passed"] for item in result["golden_results"].values()))
        self.assertEqual(44, result["golden_passed"])
        self.assertEqual(0, result["semantic_differential_mismatches"])
        self.assertEqual(0, result["zero_tolerance_invariant_events"])
        self.assertEqual(20, result["mutant_qualification"]["detected"])
        self.assertEqual(0, result["mutant_qualification"]["false_acceptance"])


if __name__ == "__main__": unittest.main()
