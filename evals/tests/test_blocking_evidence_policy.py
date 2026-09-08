from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class BlockingEvidencePolicyTests(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_core_invariant_requires_necessity_before_blocking(self):
        text = self._read("skills/aegis-verification/references/shared/core-invariants.md")
        self.assertIn("Blocking Evidence Necessity Invariant", text)
        self.assertIn("Missing Evidence != Automatically Gate Blocked", text)
        self.assertIn("high-impact failure mode", text)
        self.assertIn("credible independent detection coverage", text)
        self.assertIn("residual proof gap", text)

    def test_p20_is_failure_mode_first_and_uses_lowest_cost_credible_evidence(self):
        text = self._read("skills/aegis-verification/references/verification.md")
        self.assertIn("Failure-Mode-First", text)
        self.assertIn("high-impact failure mode", text)
        self.assertIn("credible independent detection coverage", text)
        self.assertIn("residual proof gap", text)
        self.assertIn("lowest-cost credible evidence", text)
        self.assertIn("local and CI", text)
        self.assertIn("shared oracle", text)

    def test_p34_treats_evidence_gap_as_proof_capability_gap(self):
        text = self._read("skills/aegis-gate-review/references/gate-review.md")
        self.assertIn("proof-capability gap", text)
        self.assertIn("named artifact", text)
        self.assertIn("does not by itself establish `EVIDENCE_GAP`", text)
        self.assertIn("alternate credible evidence", text)

    def test_skill_entrypoints_apply_policy_to_default_decisions(self):
        verification = self._read("skills/aegis-verification/SKILL.md")
        gate_review = self._read("skills/aegis-gate-review/SKILL.md")
        self.assertIn("Start from failure modes, not artifact lists", verification)
        self.assertIn("Residual Proof Gap", verification)
        self.assertIn("A missing named artifact is not automatically an `EVIDENCE_GAP`", gate_review)
        self.assertIn("residual proof gap", gate_review)

    def test_plugin_materialization_matches_canonical_policy_files(self):
        mirrored_paths = [
            "aegis-verification/SKILL.md",
            "aegis-verification/references/shared/core-invariants.md",
            "aegis-verification/references/verification.md",
            "aegis-gate-review/SKILL.md",
            "aegis-gate-review/references/gate-review.md",
        ]
        for relative_path in mirrored_paths:
            with self.subTest(path=relative_path):
                canonical = self._read(f"skills/{relative_path}")
                plugin = self._read(f"plugins/aegis/skills/{relative_path}")
                self.assertEqual(canonical, plugin)


if __name__ == "__main__":
    unittest.main()
