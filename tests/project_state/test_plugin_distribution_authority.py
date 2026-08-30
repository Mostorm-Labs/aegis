import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PluginDistributionAuthorityTests(unittest.TestCase):
    def test_plugin_distribution_authority_is_registered_as_proposed(self):
        authorities = json.loads((ROOT / ".aegis/authorities.json").read_text(encoding="utf-8"))
        matches = [item for item in authorities["authorities"] if item.get("id") == "aegis-plugin-distribution-v0.1"]
        self.assertEqual(1, len(matches))
        authority = matches[0]
        self.assertEqual("aegis/plugin-distribution", authority["scope"])
        self.assertEqual("skill_contract", authority["kind"])
        self.assertEqual("v0.1", authority["version"])
        self.assertEqual("Proposed", authority["status"])
        self.assertEqual("docs/plugin-distribution-contract-v0.1.md", authority["ref"])
        self.assertEqual(["aegis-skill-decomposition-v0.2"], authority["depends_on"])

    def test_registration_preserves_pr9_decision_lineage(self):
        state = json.loads((ROOT / ".aegis/state.json").read_text(encoding="utf-8"))
        current = {
            item["gate_id"]: item
            for item in state["current_gate_decisions"]
        }
        pr9 = current["gate-skill-decomposition-v02-pr9"]
        self.assertEqual("gate-skill-decomposition-v02-pr9::decision::0002", pr9["decision_id"])
        self.assertEqual("PASS", pr9["verdict"])
        self.assertNotIn("gate-skill-decomposition-v02-pr9", state["blocking_gates"])
        self.assertIn("int-pr9", state["nonconforming_integrations"])
        conformance = {
            item["integration_id"]: item
            for item in state["integration_conformance"]
        }
        int_pr9 = conformance["int-pr9"]
        self.assertEqual("gate-skill-decomposition-v02-pr9::decision::0001", int_pr9["gate_decision_id"])
        self.assertEqual("nonconforming", int_pr9["conformance"])


if __name__ == "__main__":
    unittest.main()
