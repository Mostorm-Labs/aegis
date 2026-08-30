import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "skillset/dogfood/evidence/pd-p34-02-plugin-install-chatgpt-web-20260829.json"
SOURCE_COMMIT = "a27667c89db9563535c8006f5d957f4d66f2efd5"
RELEASE_VERSION = "0.1.0-beta.2"
RELEASE_MANIFEST_REF = "skillset/releases/aegis-0.1.0-beta.2.json"
MARKETPLACE_SOURCE = "https://github.com/Mostorm-Labs/aegis"
EXPECTED_SKILLS = {
    "aegis",
    "aegis-project-state",
    "aegis-discovery",
    "aegis-modeling",
    "aegis-architecture",
    "aegis-verification",
    "aegis-governance",
    "aegis-implementation",
    "aegis-gate-review",
}


class PDP3402RealPluginInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not EVIDENCE.is_file():
            raise AssertionError(
                "PD-P34-02 requires fresh real ChatGPT Plugin installation evidence at "
                f"{EVIDENCE.relative_to(ROOT)}; synthetic evidence must not satisfy this RED"
            )
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_event_is_fresh_complete_and_chatgpt_web(self):
        self.assertEqual(self.evidence.get("schema_version"), "0.1")
        self.assertTrue(self.evidence.get("fresh_platform_event"))
        self.assertTrue(self.evidence.get("complete_catalog_capture"))
        self.assertTrue(self.evidence.get("platform_event_id"))
        self.assertEqual(
            self.evidence.get("surface"),
            {"product": "chatgpt", "surface": "web"},
        )

    def test_plugin_provenance_and_fixed_source_are_real_and_bound(self):
        self.assertTrue(self.evidence.get("plugin_id"))
        self.assertEqual(self.evidence.get("plugin_name"), "aegis")
        self.assertEqual(self.evidence.get("distribution_provenance"), "PLUGIN")
        self.assertEqual(self.evidence.get("marketplace_source"), MARKETPLACE_SOURCE)
        self.assertEqual(self.evidence.get("source_ref"), SOURCE_COMMIT)
        self.assertEqual(self.evidence.get("source_commit"), SOURCE_COMMIT)
        self.assertEqual(self.evidence.get("release_version"), RELEASE_VERSION)
        self.assertEqual(self.evidence.get("release_manifest_ref"), RELEASE_MANIFEST_REF)
        self.assertTrue(self.evidence.get("materialization_ref"))

    def test_initial_install_has_clean_before_snapshot_and_exact_nine_after(self):
        before = self.evidence.get("before_snapshot")
        after = self.evidence.get("after_snapshot")
        self.assertIsInstance(before, dict)
        self.assertIsInstance(after, dict)
        self.assertEqual(before.get("aegis_plugin_distribution_count"), 0)
        self.assertEqual(before.get("installed_aegis_skill_ids"), [])
        self.assertEqual(after.get("aegis_plugin_distribution_count"), 1)
        self.assertEqual(set(after.get("installed_aegis_skill_ids", [])), EXPECTED_SKILLS)
        self.assertEqual(len(after.get("installed_aegis_skill_ids", [])), 9)
        self.assertFalse(after.get("duplicate_aegis_distribution", True))

    def test_catalog_is_full_specialist_and_runtime_accepted(self):
        self.assertEqual(set(self.evidence.get("installed_skill_ids", [])), EXPECTED_SKILLS)
        self.assertEqual(len(self.evidence.get("installed_skill_ids", [])), 9)
        self.assertEqual(self.evidence.get("catalog_state"), "FULL_SPECIALIST")
        self.assertTrue(self.evidence.get("accepted_runtime"))
        self.assertEqual(self.evidence.get("sync_result"), "not-run")
        self.assertEqual(self.evidence.get("same_plugin_id"), "not-applicable")

    def test_component_release_versions_are_coherent_beta2(self):
        versions = self.evidence.get("component_release_versions")
        self.assertIsInstance(versions, dict)
        self.assertEqual(set(versions), EXPECTED_SKILLS)
        self.assertEqual(set(versions.values()), {RELEASE_VERSION})


if __name__ == "__main__":
    unittest.main()
