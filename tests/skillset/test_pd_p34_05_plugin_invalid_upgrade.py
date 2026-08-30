import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "skillset/dogfood/pd-p34-05-invalid-upgrade-v0.1.json"
EVIDENCE = ROOT / "skillset/dogfood/evidence/pd-p34-05-invalid-upgrade-chatgpt-web-20260830.json"

PLUGIN_NAME = "aegis"
UPGRADE_CHANNEL = "aegis/pd-p34-04-valid-upgrade-channel"
LAST_WORKING_VERSION = "0.1.0-beta.2"
LAST_WORKING_SOURCE = "9ea469a56ae829defdac476b21c25704023200ed"
LAST_WORKING_VERIFY_RUN = 33289965920
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
SAFE_OUTCOMES = {"LAST_WORKING_RETAINED", "BROKEN_CATALOG_BLOCKED"}
BROKEN_STATES = {"PARTIAL_CATALOG", "MIXED_REVISION"}


class PDP3405PluginInvalidUpgradeTests(unittest.TestCase):
    def _load(self, path: Path):
        self.assertTrue(path.is_file(), f"PD-P34-05 required artifact missing: {path.relative_to(ROOT)}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_invalid_fixture_is_pinned_and_distinct_from_last_working_release(self):
        manifest = self._load(MANIFEST)
        self.assertEqual(manifest.get("schema_version"), "0.1")
        self.assertEqual(manifest.get("case_id"), "PD-P34-05")
        self.assertEqual(manifest.get("plugin_name"), PLUGIN_NAME)
        self.assertEqual(manifest.get("marketplace_ref_type"), "branch")
        self.assertEqual(manifest.get("marketplace_ref"), UPGRADE_CHANNEL)

        before = manifest.get("last_working_release") or {}
        self.assertEqual(before.get("release_version"), LAST_WORKING_VERSION)
        self.assertEqual(before.get("source_commit"), LAST_WORKING_SOURCE)
        self.assertEqual(before.get("verification_run_id"), LAST_WORKING_VERIFY_RUN)
        self.assertEqual(set(before.get("expected_skill_ids") or []), EXPECTED_SKILLS)

        invalid = manifest.get("invalid_update_fixture") or {}
        self.assertTrue(invalid.get("source_commit"))
        self.assertNotEqual(invalid.get("source_commit"), LAST_WORKING_SOURCE)
        self.assertTrue(invalid.get("fixture_branch"))
        self.assertTrue(invalid.get("invalidity"))
        self.assertEqual(invalid.get("expected_repository_validation"), "FAIL")
        self.assertTrue(invalid.get("validation_run_id"))
        self.assertTrue(invalid.get("reviewer_accessible_ref"))

    def test_real_invalid_sync_fails_closed_without_compatibility_fallback(self):
        evidence = self._load(EVIDENCE)
        self.assertEqual(evidence.get("schema_version"), "0.1")
        self.assertEqual(evidence.get("case_id"), "PD-P34-05")
        self.assertTrue(evidence.get("fresh_platform_event"))
        self.assertTrue(evidence.get("complete_invalid_upgrade_capture"))
        self.assertTrue(evidence.get("platform_event_id"))
        self.assertEqual(evidence.get("surface"), {"product": "chatgpt", "surface": "web"})
        self.assertEqual(evidence.get("distribution_provenance"), "PLUGIN")
        self.assertEqual(evidence.get("plugin_name"), PLUGIN_NAME)
        self.assertEqual(evidence.get("marketplace_ref_type"), "branch")
        self.assertEqual(evidence.get("marketplace_ref"), UPGRADE_CHANNEL)
        self.assertEqual(evidence.get("upgrade_mechanism"), "marketplace_sync")
        self.assertIs(evidence.get("same_plugin_id"), True)
        self.assertIs(evidence.get("plugin_deleted_between_snapshots"), False)
        self.assertIs(evidence.get("marketplace_deleted_between_snapshots"), False)
        self.assertIs(evidence.get("invalid_candidate_accepted_runtime"), False)
        self.assertIs(evidence.get("compatibility_fallback"), False)
        self.assertTrue(evidence.get("materialization_ref"))

        plugin_id = evidence.get("platform_plugin_id")
        self.assertIsInstance(plugin_id, str)
        self.assertTrue(plugin_id.strip())

        before = evidence.get("before_snapshot") or {}
        self.assertEqual(before.get("source_commit"), LAST_WORKING_SOURCE)
        self.assertEqual(before.get("release_version"), LAST_WORKING_VERSION)
        self.assertEqual(before.get("platform_plugin_id"), plugin_id)
        self.assertEqual(before.get("catalog_state"), "FULL_SPECIALIST")
        self.assertEqual(set(before.get("installed_skill_ids") or []), EXPECTED_SKILLS)
        self.assertEqual(before.get("aegis_plugin_distribution_count"), 1)
        self.assertIs(before.get("duplicate_aegis_distribution"), False)

        outcome = evidence.get("safe_outcome")
        self.assertIn(outcome, SAFE_OUTCOMES)
        after = evidence.get("after_snapshot") or {}
        self.assertEqual(after.get("platform_plugin_id"), plugin_id)
        self.assertEqual(after.get("aegis_plugin_distribution_count"), 1)
        self.assertIs(after.get("duplicate_aegis_distribution"), False)

        if outcome == "LAST_WORKING_RETAINED":
            self.assertEqual(evidence.get("sync_result"), "error")
            self.assertIs(evidence.get("last_working_release_retained"), True)
            self.assertEqual(after.get("source_commit"), LAST_WORKING_SOURCE)
            self.assertEqual(after.get("release_version"), LAST_WORKING_VERSION)
            self.assertEqual(after.get("catalog_state"), "FULL_SPECIALIST")
            self.assertEqual(set(after.get("installed_skill_ids") or []), EXPECTED_SKILLS)
            self.assertIs(after.get("accepted_runtime"), True)
        else:
            self.assertIn(evidence.get("sync_result"), {"success", "error"})
            self.assertIn(after.get("catalog_state"), BROKEN_STATES)
            self.assertIs(after.get("accepted_runtime"), False)
            self.assertNotEqual(after.get("catalog_state"), "COMPOSITE_ONLY")


if __name__ == "__main__":
    unittest.main()
