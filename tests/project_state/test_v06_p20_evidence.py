"""Reviewer-resolvable P20 V1-V14 evidence index for Project State v0.6."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class P20EvidenceMapTests(unittest.TestCase):
    def test_v1_v14_evidence_surfaces_exist(self):
        self.assertTrue((ROOT / "tests/project_state/test_v06_binding.py").exists())
        self.assertTrue((ROOT / "examples/project-state/v0.6-minimal/.aegis/evidence.json").exists())
        self.assertTrue((ROOT / "examples/project-state/v0.6-minimal/.aegis/integrations.json").exists())
        self.assertTrue((ROOT / "skills/aegis-project-state/references/project-state.md").exists())
        self.assertTrue((ROOT / "skillset/skills/aegis-project-state/references/project-state.md").exists())

    def test_pr82_reviewer_refs_are_canonical(self):
        text = (ROOT / "examples/project-state/v0.6-minimal/.aegis/evidence.json").read_text()
        self.assertIn("#pullrequestreview-5122113780", text)
        self.assertIn("#issuecomment-5553423707", text)

if __name__ == "__main__":
    unittest.main()
