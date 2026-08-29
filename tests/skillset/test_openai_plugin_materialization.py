import json
import re
import unittest
from pathlib import Path

from tools.aegis_skillset.package import tree_sha256


ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = ROOT / ".agents/plugins/marketplace.json"
PLUGIN_ROOT = ROOT / "plugins/aegis"
PLUGIN_MANIFEST = PLUGIN_ROOT / ".codex-plugin/plugin.json"
PLUGIN_SKILLS = PLUGIN_ROOT / "skills"
DISTRIBUTION = ROOT / "skillset/distribution.json"
RELEASE_MANIFEST = ROOT / "skillset/releases/aegis-0.1.0-beta.1.json"
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\."
    r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class OpenAIPluginMaterializationTests(unittest.TestCase):
    def test_repo_marketplace_materializes_one_native_aegis_plugin(self):
        self.assertTrue(
            MARKETPLACE.is_file(),
            "PD-P34-01 requires .agents/plugins/marketplace.json",
        )
        payload = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("name"), "mostorm-labs-aegis")
        self.assertEqual(
            payload.get("interface"),
            {"displayName": "Mostorm Labs Aegis"},
        )
        plugins = payload.get("plugins")
        self.assertIsInstance(plugins, list)
        self.assertEqual(len(plugins), 1)
        entry = plugins[0]
        self.assertEqual(entry.get("name"), "aegis")
        self.assertEqual(
            entry.get("source"),
            {"source": "local", "path": "./plugins/aegis"},
        )
        self.assertEqual(
            entry.get("policy"),
            {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        )
        self.assertEqual(entry.get("category"), "Productivity")

    def test_native_plugin_manifest_is_skills_only_and_release_bound(self):
        self.assertTrue(
            PLUGIN_MANIFEST.is_file(),
            "PD-P34-01 requires plugins/aegis/.codex-plugin/plugin.json",
        )
        plugin = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        release = json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(plugin.get("name"), "aegis")
        self.assertEqual(plugin.get("version"), release.get("release_version"))
        self.assertRegex(plugin.get("version", ""), SEMVER_RE)
        self.assertIsInstance(plugin.get("description"), str)
        self.assertTrue(plugin["description"].strip())
        self.assertIsInstance(plugin.get("author"), dict)
        self.assertTrue(plugin["author"].get("name", "").strip())
        self.assertEqual(plugin.get("skills"), "./skills/")
        self.assertNotIn("apps", plugin)
        self.assertNotIn("mcpServers", plugin)
        self.assertNotIn("hooks", plugin)

        interface = plugin.get("interface")
        self.assertIsInstance(interface, dict)
        for field in (
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
        ):
            self.assertIsInstance(interface.get(field), str)
            self.assertTrue(interface[field].strip(), field)
        self.assertIsInstance(interface.get("capabilities"), list)
        self.assertTrue(interface["capabilities"])
        self.assertTrue(all(isinstance(x, str) and x.strip() for x in interface["capabilities"]))
        self.assertIsInstance(interface.get("defaultPrompt"), list)
        self.assertTrue(interface["defaultPrompt"])
        self.assertLessEqual(len(interface["defaultPrompt"]), 3)
        self.assertTrue(all(isinstance(x, str) and x.strip() for x in interface["defaultPrompt"]))

    def test_plugin_contains_exact_nine_canonical_skill_trees(self):
        distribution = json.loads(DISTRIBUTION.read_text(encoding="utf-8"))
        expected = distribution["plugin"]["skills"]
        self.assertEqual(len(expected), 9)
        self.assertEqual(distribution["plugin"].get("required_apps"), [])
        self.assertEqual(distribution["plugin"].get("optional_apps"), [])
        self.assertTrue(
            PLUGIN_SKILLS.is_dir(),
            "PD-P34-01 requires plugins/aegis/skills",
        )

        actual = sorted(
            path.name
            for path in PLUGIN_SKILLS.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        )
        self.assertEqual(actual, sorted(expected))

        for skill_name in expected:
            canonical = ROOT / "skills" / skill_name
            materialized = PLUGIN_SKILLS / skill_name
            self.assertTrue(materialized.is_dir(), skill_name)
            self.assertEqual(
                tree_sha256(materialized),
                tree_sha256(canonical),
                f"Plugin materialization drift for {skill_name}",
            )


if __name__ == "__main__":
    unittest.main()
