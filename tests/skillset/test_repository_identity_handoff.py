import json
import tempfile
import unittest
from pathlib import Path

from tools.aegis_skillset.package import validate_repository_identity


ROOT = Path(__file__).resolve().parents[2]


class RepositoryIdentityHandoffTests(unittest.TestCase):
    def _read(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def _load(self, name: str) -> dict:
        return json.loads((ROOT / "skillset/dogfood" / name).read_text(encoding="utf-8"))

    def test_repository_identity_proof_is_complete(self):
        proof = self._load("repository-identity-v0.2.json")
        self.assertEqual(proof["repository"], {"provider": "github", "full_name": "Mostorm-Labs/aegis"})
        self.assertEqual(proof["mandatory_pass"], "10/10")
        self.assertEqual(len(proof["scenarios"]), 10)
        self.assertEqual([case["scenario_id"] for case in proof["scenarios"]], [f"RI-S{i:02d}" for i in range(1, 11)])
        self.assertEqual(proof["scenarios"][0]["expected"], "CONTINUE_TO_ANCHOR_PREFLIGHT")
        self.assertEqual(proof["scenarios"][1]["expected"], "ISOLATE_DECLARED_REPOSITORY")
        self.assertEqual(proof["scenarios"][2]["expected"], "BLOCKED_REPOSITORY_IDENTITY")
        self.assertFalse(proof["scenarios"][8]["p33_classification_performed"])
        self.assertEqual(proof["scenarios"][9]["stage"], "P36")
        self.assertTrue(all(case["expected_mutated_repositories"] == [] for case in proof["scenarios"]))
        self.assertEqual(proof["safety_metrics"]["wrong_repository_authored_mutations"], 0)
        self.assertEqual(proof["safety_metrics"]["p33_repository_preflight_order_violations"], 0)

    def test_negative_proof_rejects_all_mutants_without_false_acceptance(self):
        negative = self._load("repository-identity-negative-v0.2.json")
        self.assertEqual(negative["mandatory_pass"], "6/6")
        self.assertEqual(len(negative["mutants"]), 6)
        self.assertEqual(negative["negative_false_acceptance"], 0)
        self.assertTrue(all(case["expected"] == "BLOCKED_REPOSITORY_IDENTITY" for case in negative["mutants"]))

    def test_repository_validator_fails_closed_for_identity_mutants(self):
        valid = {"provider": "github", "full_name": "Mostorm-Labs/aegis"}
        self.assertEqual(validate_repository_identity(valid), valid)
        mutants = (
            {},
            {"provider": "gitlab", "full_name": "Mostorm-Labs/aegis"},
            {"provider": "github", "full_name": "other/repo"},
            {"provider": "github"},
        )
        for mutant in mutants:
            with self.subTest(mutant=mutant):
                with self.assertRaisesRegex(ValueError, "BLOCKED_REPOSITORY_IDENTITY"):
                    validate_repository_identity(mutant)

    def test_repository_identity_preflight_is_before_anchor_and_cursor(self):
        handoff = (ROOT / "skillset/shared/handoff-contract.md").read_text(encoding="utf-8")
        implementation = (ROOT / "skillset/skills/aegis-implementation/SKILL.md").read_text(encoding="utf-8")
        self.assertLess(handoff.find("Repository identity is resolved"), handoff.find("task_anchor"))
        self.assertLess(implementation.find("repository.provider/full_name"), implementation.find("task_anchor"))
        for path in (
            "skillset/shared/handoff-contract.md",
            "skillset/skills/aegis-implementation/SKILL.md",
            "skillset/skills/aegis-implementation/references/implementation-control.md",
            "skillset/skills/aegis-gate-review/SKILL.md",
            "skillset/skills/aegis-gate-review/references/gate-review.md",
        ):
            self.assertIn("BLOCKED_REPOSITORY_IDENTITY", self._read(path))


if __name__ == "__main__":
    unittest.main()
