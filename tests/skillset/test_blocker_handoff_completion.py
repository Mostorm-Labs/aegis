import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class BlockerHandoffCompletionTests(unittest.TestCase):
    def test_established_blocker_requires_central_router_terminal_owner(self):
        from tools.aegis_skillset.model import load_skillset
        from tools.aegis_skillset.routing import evaluate_terminal_trace

        case = {
            "requested_primary_owner": "aegis-architecture",
            "allowed_supporting_skills": ["aegis-project-state"],
            "router_policy": "only_for_genuine_ambiguity_or_accepted_earlier_blocker",
            "short_circuit": {
                "allowed": True,
                "condition": "earlier_blocker_conclusively_established",
                "terminal_owner": "aegis",
            },
            "must_stop": True,
        }
        trace = {
            "terminal": True,
            "mode": "multi_skill",
            "invocations": [
                {"skill": "aegis-architecture", "role": "primary"},
            ],
            "final_answer_owner": "aegis-architecture",
            "genuine_ambiguity": False,
            "earlier_blocker_conclusively_established": True,
            "specialist_availability": {"aegis-architecture": "available"},
            "ownership_edges": [],
            "handoff_edges": [["aegis-architecture", "aegis"]],
            "forbidden_downstream_substantive_execution": 0,
            "primary_substantive_result_emitted": False,
        }

        result = evaluate_terminal_trace(case, trace, load_skillset(ROOT))
        self.assertEqual("FAIL", result.verdict)
        self.assertIn("WRONG_FINAL_ANSWER_OWNER", result.violations)

    def test_architecture_skill_makes_blocker_handoff_nonterminal(self):
        for path in (
            ROOT / "skillset/skills/aegis-architecture/SKILL.md",
            ROOT / "skills/aegis-architecture/SKILL.md",
        ):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn("The handoff is not the terminal user answer", text)
                self.assertIn("central `aegis` must own the terminal blocked/routing answer", text)


if __name__ == "__main__":
    unittest.main()
