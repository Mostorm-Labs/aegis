import json
import re
import unittest
from pathlib import Path

from tools.aegis_skillset.model import load_skillset

ROOT = Path(__file__).resolve().parents[2]
TRACE_PATH = ROOT / "skillset/dogfood/execution-surface-behavioral-v0.1.json"
EXPECTED_CHANGED_FILES = [
    "skillset/dogfood/execution-surface-behavioral-v0.1.json",
    "tests/skillset/test_execution_surface_behavioral_dogfood.py",
]


class ExecutionSurfaceBehavioralDogfoodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_skillset(ROOT)
        cls.trace = json.loads(TRACE_PATH.read_text(encoding="utf-8"))

    def test_surface_handoff_matches_machine_contract(self):
        handoff = self.trace["surface_handoff"]
        config = self.config

        self.assertEqual(self.trace["scenario_id"], "ES-BD-001")
        self.assertEqual(handoff["type"], "surface_handoff")
        self.assertEqual(handoff["stage"], "P32")
        self.assertEqual(handoff["stage_owner"], config.primary_owner_by_stage["P32"])
        self.assertEqual(handoff["from_surface"], config.execution_surface_by_stage["P31"])
        self.assertEqual(handoff["to_surface"], config.execution_surface_by_stage["P32"])
        self.assertEqual(
            handoff["preferred_executor"],
            config.executor_profiles[config.default_executor_profile][handoff["to_surface"]],
        )
        self.assertEqual(handoff["return_surface"], config.execution_surface_by_stage["P34"])
        self.assertFalse(config.surface_handoff_transfers_ownership)

    def test_executor_observation_is_bounded_and_auditable(self):
        observation = self.trace["executor_observation"]
        self.assertEqual(observation["executor"], "codex")
        self.assertEqual(observation["surface"], "CODE_EXECUTION")
        self.assertEqual(observation["status"], "READY_FOR_REVIEW")
        self.assertRegex(observation["starting_revision"], re.compile(r"^[0-9a-f]{40}$"))
        self.assertEqual(observation["changed_files"], EXPECTED_CHANGED_FILES)
        self.assertEqual(
            observation["verification_commands"],
            [
                "python3 -m unittest tests.skillset.test_execution_surface_behavioral_dogfood -v",
                "python3 -m unittest tests.skillset.test_execution_surface_contract tests.skillset.test_metadata -v",
            ],
        )


if __name__ == "__main__":
    unittest.main()
