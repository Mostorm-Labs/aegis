import json
import unittest
from pathlib import Path

from tools.aegis_skillset.dogfood import evaluate_installed_platform_rerun


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "skillset/dogfood/pd-p34-03-plugin-behavioral-parity-v0.1.json"
SOURCE_COMMIT = "a27667c89db9563535c8006f5d957f4d66f2efd5"
RELEASE_VERSION = "0.1.0-beta.2"
PLUGIN_CASES = {
    "09-01-direct-specialist": (
        ROOT / "skillset/dogfood/evidence/pd-p34-03-09-01-direct-specialist-chatgpt-web-20260830.json",
        "Audit Mostorm-Labs/aegis PR #9 against its Gate evidence.",
    ),
    "09-01-ambiguous-router": (
        ROOT / "skillset/dogfood/evidence/pd-p34-03-09-01-ambiguous-router-chatgpt-web-20260830.json",
        "What should this project do next?",
    ),
    "09-01-upstream-blocker-reroute": (
        ROOT / "skillset/dogfood/evidence/pd-p34-03-09-01-upstream-blocker-reroute-chatgpt-web-20260830.json",
        "Design module architecture, but project authority is unresolved.",
    ),
}


class PDP3403PluginBehavioralParityTests(unittest.TestCase):
    def test_three_fresh_plugin_behavior_events_are_bound_and_prompts_unchanged(self):
        for case_id, (path, expected_prompt) in PLUGIN_CASES.items():
            self.assertTrue(
                path.is_file(),
                f"PD-P34-03 requires fresh real Plugin behavior evidence for {case_id}: {path.relative_to(ROOT)}",
            )
            evidence = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(evidence.get("schema_version"), "0.2")
            self.assertEqual(evidence.get("case_id"), case_id)
            self.assertTrue(evidence.get("fresh_platform_event"))
            self.assertTrue(evidence.get("complete_response_captured"))
            self.assertTrue(evidence.get("platform_event_id"))
            self.assertEqual(evidence.get("surface"), {"product": "chatgpt", "surface": "web"})
            self.assertEqual(evidence.get("prompt"), expected_prompt)
            self.assertEqual(evidence.get("distribution_provenance"), "PLUGIN")
            self.assertEqual(evidence.get("plugin_id"), "aegis")
            self.assertEqual(evidence.get("source_commit"), SOURCE_COMMIT)
            self.assertEqual(evidence.get("release_version"), RELEASE_VERSION)
            self.assertEqual(evidence.get("catalog_state"), "FULL_SPECIALIST")
            self.assertTrue(evidence.get("materialization_ref"))

    def test_terminal_trace_oracle_passes_plugin_full_specialist_cases_without_manufacturing_composite(self):
        self.assertTrue(MANIFEST.is_file(), "PD-P34-03 manifest missing")
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        composite = next(item for item in manifest["cases"] if item["id"] == "09-01-composite-fallback")
        self.assertTrue(composite.get("historical_protected_fixture"))
        self.assertTrue(composite.get("plugin_environment_must_not_be_degraded_to_execute"))
        self.assertIn("task6-catalog-composite-only", composite.get("catalog_evidence_ref", ""))

        result = evaluate_installed_platform_rerun(ROOT, MANIFEST)
        self.assertEqual("PASS", result.verdict, result)
        self.assertEqual(4, len(result.cases))
        self.assertTrue(all(case.verdict == "PASS" for case in result.cases), result)
        by_id = {case.case_id: case for case in result.cases}
        for case_id in PLUGIN_CASES:
            self.assertEqual("FULL_SPECIALIST", by_id[case_id].catalog_state)
        self.assertEqual("COMPOSITE_ONLY", by_id["09-01-composite-fallback"].catalog_state)


if __name__ == "__main__":
    unittest.main()
