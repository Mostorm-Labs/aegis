import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "skillset/dogfood/pd-p34-04-valid-upgrade-v0.1.json"
EVIDENCE = ROOT / "skillset/dogfood/evidence/pd-p34-04-valid-upgrade-chatgpt-web-20260830.json"
RELEASE_B_MANIFEST = ROOT / "skillset/releases/aegis-0.1.0-beta.2.json"

PLUGIN_NAME = "aegis"
UPGRADE_CHANNEL = "aegis/pd-p34-04-valid-upgrade-channel"
RELEASE_A_VERSION = "0.1.0-beta.1.1"
RELEASE_A_SOURCE = "edf9511679e68943b4120edb6889f970a02b74d2"
RELEASE_A_VERIFY_RUN = 33289426094
RELEASE_B_VERSION = "0.1.0-beta.2"
RELEASE_B_SOURCE = "9ea469a56ae829defdac476b21c25704023200ed"
RELEASE_B_VERIFY_RUN = 33289965920
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
HISTORICAL_COMPONENT_TREE_SHA256 = {
    "aegis": "8599a15d24ccd80c534cc5838425592f666184f8edcf577366b96a48197c42dd",
    "aegis-project-state": "66639e270cf547f03fa78d1a2e518a4efc58780cadac778bb690f56e6a42b8c6",
    "aegis-discovery": "2e89921aee11008c8c4db7500c80f243a149a2465fec3281d1d0146905b73721",
    "aegis-modeling": "5c842d382244c638b4227185683629e856f010b4d73cea71c1208a288e5635ab",
    "aegis-architecture": "d3d0fca798af19a9fed9a32d23bdf172b5bee06dfde7226ab3473d860cff26ba",
    "aegis-verification": "b461f31350a2cd73eacd434bdd0849775b75ed7696481143496db1ee22ef5ce8",
    "aegis-governance": "bbc320caee94c1ee615ba9ba79795a3bae683ca58c4fb9f41841efa886d2b8c5",
    "aegis-implementation": "58554a6191327a31c101f8e07f938fad89105e271334cda5e649e222aa064c86",
    "aegis-gate-review": "b593a93bee619d72bfcbd81abf21ca60e4d465d308ed488a9de4443d7f7a8af5",
}


class PDP3404PluginValidUpgradeTests(unittest.TestCase):
    def _load(self, path: Path):
        self.assertTrue(path.is_file(), f"PD-P34-04 required artifact missing: {path.relative_to(ROOT)}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_upgrade_manifest_pins_two_distinct_coherent_releases_on_one_movable_channel(self):
        manifest = self._load(MANIFEST)
        self.assertEqual(manifest.get("schema_version"), "0.1")
        self.assertEqual(manifest.get("case_id"), "PD-P34-04")
        self.assertEqual(manifest.get("plugin_name"), PLUGIN_NAME)
        self.assertEqual(manifest.get("marketplace_ref_type"), "branch")
        self.assertEqual(manifest.get("marketplace_ref"), UPGRADE_CHANNEL)

        release_a = manifest.get("release_a") or {}
        release_b = manifest.get("release_b") or {}
        self.assertEqual(release_a.get("release_version"), RELEASE_A_VERSION)
        self.assertEqual(release_a.get("source_commit"), RELEASE_A_SOURCE)
        self.assertEqual(release_a.get("verification_run_id"), RELEASE_A_VERIFY_RUN)
        self.assertEqual(release_b.get("release_version"), RELEASE_B_VERSION)
        self.assertEqual(release_b.get("source_commit"), RELEASE_B_SOURCE)
        self.assertEqual(release_b.get("verification_run_id"), RELEASE_B_VERIFY_RUN)
        self.assertNotEqual(release_a.get("source_commit"), release_b.get("source_commit"))
        self.assertNotEqual(release_a.get("release_version"), release_b.get("release_version"))
        self.assertEqual(set(manifest.get("expected_skill_ids") or []), EXPECTED_SKILLS)

        # Historical platform evidence is bound to immutable source commits. Its
        # component digests must not float when the current beta.2 candidate evolves.
        self.assertEqual(manifest.get("release_a_tree_sha256"), HISTORICAL_COMPONENT_TREE_SHA256)
        self.assertEqual(manifest.get("release_b_tree_sha256"), HISTORICAL_COMPONENT_TREE_SHA256)

        release_b_manifest = self._load(RELEASE_B_MANIFEST)
        self.assertEqual(release_b_manifest.get("release_version"), RELEASE_B_VERSION)
        self.assertEqual(
            {entry["name"] for entry in release_b_manifest["plugin"]["skills"]},
            EXPECTED_SKILLS,
        )

    def test_real_chatgpt_sync_is_atomic_same_platform_plugin_and_exact_nine(self):
        evidence = self._load(EVIDENCE)
        self.assertEqual(evidence.get("schema_version"), "0.1")
        self.assertEqual(evidence.get("case_id"), "PD-P34-04")
        self.assertTrue(evidence.get("fresh_platform_event"))
        self.assertTrue(evidence.get("complete_upgrade_capture"))
        self.assertTrue(evidence.get("platform_event_id"))
        self.assertEqual(evidence.get("surface"), {"product": "chatgpt", "surface": "web"})
        self.assertEqual(evidence.get("distribution_provenance"), "PLUGIN")
        self.assertEqual(evidence.get("plugin_name"), PLUGIN_NAME)
        self.assertEqual(evidence.get("marketplace_ref_type"), "branch")
        self.assertEqual(evidence.get("marketplace_ref"), UPGRADE_CHANNEL)
        self.assertEqual(evidence.get("upgrade_mechanism"), "marketplace_sync")
        self.assertEqual(evidence.get("sync_result"), "success")
        self.assertIs(evidence.get("same_plugin_id"), True)
        self.assertIs(evidence.get("plugin_deleted_between_snapshots"), False)
        self.assertIs(evidence.get("marketplace_deleted_between_snapshots"), False)
        self.assertIs(evidence.get("accepted_mixed_revision_state"), False)
        self.assertIs(evidence.get("accepted_partial_catalog_state"), False)
        self.assertTrue(evidence.get("materialization_ref"))

        platform_plugin_id = evidence.get("platform_plugin_id")
        self.assertIsInstance(platform_plugin_id, str)
        self.assertTrue(platform_plugin_id.strip())

        latest_sync = evidence.get("latest_sync") or {}
        self.assertEqual(latest_sync.get("added"), 0)
        self.assertEqual(latest_sync.get("updated"), 1)
        self.assertEqual(latest_sync.get("failed"), 0)

        before = evidence.get("before_snapshot") or {}
        after = evidence.get("after_snapshot") or {}
        self.assertEqual(before.get("source_commit"), RELEASE_A_SOURCE)
        self.assertEqual(before.get("release_version"), RELEASE_A_VERSION)
        self.assertEqual(after.get("source_commit"), RELEASE_B_SOURCE)
        self.assertEqual(after.get("release_version"), RELEASE_B_VERSION)
        self.assertEqual(before.get("platform_plugin_id"), platform_plugin_id)
        self.assertEqual(after.get("platform_plugin_id"), platform_plugin_id)

        for snapshot, version in ((before, RELEASE_A_VERSION), (after, RELEASE_B_VERSION)):
            self.assertEqual(snapshot.get("plugin_name"), PLUGIN_NAME)
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
