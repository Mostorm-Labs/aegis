import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "skillset/dogfood/pd-p34-04-valid-upgrade-v0.1.json"
EVIDENCE = ROOT / "skillset/dogfood/evidence/pd-p34-04-valid-upgrade-chatgpt-web-20260830.json"
RELEASE_B_MANIFEST = ROOT / "skillset/releases/aegis-0.1.0-beta.2.json"

PLUGIN_ID = "aegis"
RELEASE_A_VERSION = "0.1.0-beta.1.1"
RELEASE_A_SOURCE = "edf9511679e68943b4120edb6889f970a02b74d2"
RELEASE_A_VERIFY_RUN = 33289426094
RELEASE_B_VERSION = "0.1.0-beta.2"
RELEASE_B_SOURCE = "a27667c89db9563535c8006f5d957f4d66f2efd5"
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


class PDP3404PluginValidUpgradeTests(unittest.TestCase):
    def _load(self, path: Path):
        self.assertTrue(path.is_file(), f"PD-P34-04 required artifact missing: {path.relative_to(ROOT)}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_upgrade_manifest_pins_two_distinct_coherent_releases(self):
        manifest = self._load(MANIFEST)
        self.assertEqual(manifest.get("schema_version"), "0.1")
        self.assertEqual(manifest.get("case_id"), "PD-P34-04")
        self.assertEqual(manifest.get("plugin_id"), PLUGIN_ID)

        release_a = manifest.get("release_a") or {}
        release_b = manifest.get("release_b") or {}
        self.assertEqual(release_a.get("release_version"), RELEASE_A_VERSION)
        self.assertEqual(release_a.get("source_commit"), RELEASE_A_SOURCE)
        self.assertEqual(release_a.get("verification_run_id"), RELEASE_A_VERIFY_RUN)
        self.assertEqual(release_b.get("release_version"), RELEASE_B_VERSION)
        self.assertEqual(release_b.get("source_commit"), RELEASE_B_SOURCE)
        self.assertNotEqual(release_a.get("source_commit"), release_b.get("source_commit"))
        self.assertNotEqual(release_a.get("release_version"), release_b.get("release_version"))
        self.assertEqual(set(manifest.get("expected_skill_ids") or []), EXPECTED_SKILLS)

        release_b_manifest = self._load(RELEASE_B_MANIFEST)
        self.assertEqual(release_b_manifest.get("release_version"), RELEASE_B_VERSION)
        self.assertEqual(
            {entry["name"] for entry in release_b_manifest["plugin"]["skills"]},
            EXPECTED_SKILLS,
        )
        expected_digests = {entry["name"]: entry["tree_sha256"] for entry in release_b_manifest["plugin"]["skills"]}
        self.assertEqual(manifest.get("release_a_tree_sha256"), expected_digests)
        self.assertEqual(manifest.get("release_b_tree_sha256"), expected_digests)

    def test_real_chatgpt_sync_is_atomic_same_plugin_and_exact_nine(self):
        evidence = self._load(EVIDENCE)
        self.assertEqual(evidence.get("schema_version"), "0.1")
        self.assertEqual(evidence.get("case_id"), "PD-P34-04")
        self.assertTrue(evidence.get("fresh_platform_event"))
        self.assertTrue(evidence.get("complete_upgrade_capture"))
        self.assertTrue(evidence.get("platform_event_id"))
        self.assertEqual(evidence.get("surface"), {"product": "chatgpt", "surface": "web"})
        self.assertEqual(evidence.get("distribution_provenance"), "PLUGIN")
        self.assertEqual(evidence.get("plugin_id"), PLUGIN_ID)
        self.assertEqual(evidence.get("sync_result"), "success")
        self.assertIs(evidence.get("same_plugin_id"), True)
        self.assertIs(evidence.get("accepted_mixed_revision_state"), False)
        self.assertIs(evidence.get("accepted_partial_catalog_state"), False)
        self.assertTrue(evidence.get("materialization_ref"))

        before = evidence.get("before_snapshot") or {}
        after = evidence.get("after_snapshot") or {}
        self.assertEqual(before.get("source_commit"), RELEASE_A_SOURCE)
        self.assertEqual(before.get("release_version"), RELEASE_A_VERSION)
        self.assertEqual(after.get("source_commit"), RELEASE_B_SOURCE)
        self.assertEqual(after.get("release_version"), RELEASE_B_VERSION)

        for snapshot, version in ((before, RELEASE_A_VERSION), (after, RELEASE_B_VERSION)):
            self.assertEqual(snapshot.get("plugin_id"), PLUGIN_ID)
            self.assertEqual(snapshot.get("catalog_state"), "FULL_SPECIALIST")
            self.assertEqual(set(snapshot.get("installed_skill_ids") or []), EXPECTED_SKILLS)
            self.assertEqual(snapshot.get("aegis_plugin_distribution_count"), 1)
            self.assertIs(snapshot.get("duplicate_aegis_distribution"), False)
            components = snapshot.get("component_release_versions") or {}
            self.assertEqual(set(components), EXPECTED_SKILLS)
            self.assertTrue(all(value == version for value in components.values()))

        if "workspace_policy" in before or "workspace_policy" in after:
            self.assertEqual(before.get("workspace_policy"), after.get("workspace_policy"))


if __name__ == "__main__":
    unittest.main()
