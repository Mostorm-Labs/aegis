import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ExecutionAnchorResumeCursorTests(unittest.TestCase):
    def _read(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def test_shared_handoff_defines_anchor_and_cursor_semantics(self):
        text = self._read("skillset/shared/handoff-contract.md")
        for required in (
            "Task Anchor != Execution Cursor",
            "task_anchor",
            "resume_cursor",
            "historical HEAD equality",
            "BLOCKED_EXECUTION_DIVERGENCE",
        ):
            self.assertIn(required, text)

    def test_implementation_contract_defines_p33_reconciliation_outcomes(self):
        skill = self._read("skillset/skills/aegis-implementation/SKILL.md")
        control = self._read(
            "skillset/skills/aegis-implementation/references/implementation-control.md"
        )
        combined = skill + "\n" + control
        for required in (
            "EXACT_CURSOR",
            "DESCENDANT_CURSOR",
            "ANCHOR_DESCENDANT_WITHOUT_CURSOR",
            "DIVERGED",
            "first incomplete verified step",
            "do not replay",
        ):
            self.assertIn(required, combined)

    def test_v02_authority_forbids_historical_head_equality_only_resume(self):
        text = self._read("docs/execution-surface-contract-v0.2.md")
        self.assertIn("Task Anchor != Execution Cursor", text)
        self.assertIn("historical HEAD equality", text)
        self.assertIn("must not", text)
        self.assertIn("DESCENDANT_CURSOR", text)

    def test_descendant_cursor_dogfood_resumes_without_replay(self):
        trace = json.loads(
            self._read("skillset/dogfood/execution-anchor-resume-cursor-v0.1.json")
        )
        self.assertEqual(trace["scenario_id"], "ES-RC-001")
        self.assertEqual(trace["stage"], "P33")
        self.assertEqual(trace["task_anchor"]["relation"], "ancestor")
        self.assertEqual(trace["observed"]["relation_to_cursor"], "descendant")
        self.assertEqual(trace["decision"], "P33_RESUME")
        self.assertFalse(trace["replay_completed_work"])
        for key in ("task_anchor", "resume_cursor", "observed"):
            revision = trace[key]["revision"]
            self.assertEqual(len(revision), 40)
            int(revision, 16)

    def test_generated_implementation_skill_preserves_resume_contract(self):
        text = self._read("skills/aegis-implementation/SKILL.md")
        for required in (
            "Task Anchor != Execution Cursor",
            "task_anchor",
            "resume_cursor",
            "DESCENDANT_CURSOR",
            "BLOCKED_EXECUTION_DIVERGENCE",
        ):
            self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
