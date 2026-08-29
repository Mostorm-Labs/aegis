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

    def test_authority_makes_anchor_and_known_cursor_conditionally_mandatory(self):
        authority = self._read("docs/execution-surface-contract-v0.2.md")
        shared = self._read("skillset/shared/handoff-contract.md")
        implementation = self._read("skillset/skills/aegis-implementation/SKILL.md")

        for text in (authority, shared):
            self.assertIn(
                "MUST include a non-null `task_anchor`",
                text,
            )
            self.assertIn(
                "MUST include a non-null `resume_cursor`",
                text,
            )

        self.assertIn("nullable at the schema level", implementation)
        self.assertIn("MUST carry a non-null `resume_cursor`", implementation)

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

    def test_behavioral_dogfood_covers_all_p33_reconciliation_outcomes(self):
        path = ROOT / "skillset/dogfood/execution-anchor-resume-cursor-v0.2.json"
        self.assertTrue(path.is_file(), "missing expanded P33 reconciliation dogfood")
        corpus = json.loads(path.read_text(encoding="utf-8"))
        scenarios = {case["reconciliation_class"]: case for case in corpus["scenarios"]}

        self.assertEqual(
            set(scenarios),
            {
                "EXACT_CURSOR",
                "DESCENDANT_CURSOR",
                "ANCHOR_DESCENDANT_WITHOUT_CURSOR",
                "DIVERGED",
            },
        )

        exact = scenarios["EXACT_CURSOR"]
        self.assertEqual(
            exact["observed"]["revision"], exact["resume_cursor"]["revision"]
        )
        self.assertEqual(exact["decision"], "P33_RESUME")
        self.assertFalse(exact["replay_completed_work"])

        descendant = scenarios["DESCENDANT_CURSOR"]
        self.assertEqual(descendant["observed"]["relation_to_cursor"], "descendant")
        self.assertEqual(descendant["decision"], "P33_RESUME")
        self.assertFalse(descendant["replay_completed_work"])

        anchor_only = scenarios["ANCHOR_DESCENDANT_WITHOUT_CURSOR"]
        self.assertIsNone(anchor_only["resume_cursor"])
        self.assertEqual(anchor_only["observed"]["relation_to_anchor"], "descendant")
        self.assertEqual(anchor_only["decision"], "P33_RESUME")
        self.assertTrue(anchor_only["establish_resume_cursor"])
        self.assertFalse(anchor_only["replay_completed_work"])

        diverged = scenarios["DIVERGED"]
        self.assertEqual(diverged["observed"]["relation_to_anchor"], "unrelated")
        self.assertEqual(diverged["observed"]["relation_to_cursor"], "unrelated")
        self.assertEqual(diverged["decision"], "BLOCKED_EXECUTION_DIVERGENCE")
        self.assertFalse(diverged["continue_execution"])

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
