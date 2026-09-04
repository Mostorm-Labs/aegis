import json
import unittest
from pathlib import Path

from tools.aegis_skillset.package import render_release_manifest


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.2.0-beta.1"
TAG = f"v{VERSION}"


class ControlPlaneV02ReleaseCandidateTests(unittest.TestCase):
    def test_public_release_identity_is_coherent(self):
        plugin = json.loads(
            (ROOT / "plugins/aegis/.codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        release_path = ROOT / f"skillset/releases/aegis-{VERSION}.json"
        self.assertTrue(release_path.is_file(), "beta.1 release manifest must exist")
        release = json.loads(release_path.read_text(encoding="utf-8"))

        self.assertEqual(VERSION, plugin["version"])
        self.assertEqual(VERSION, release["release_version"])
        self.assertEqual(render_release_manifest(ROOT, VERSION), release)

        names = [entry["name"] for entry in release["plugin"]["skills"]]
        self.assertEqual(9, len(names))
        self.assertEqual(9, len(set(names)))
        self.assertEqual("aegis", release["plugin"]["id"])

    def test_current_docs_point_to_v02_release(self):
        notes = ROOT / f"docs/releases/{TAG}.md"
        guide = ROOT / "docs/installation-and-usage-v0.2.md"
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertTrue(notes.is_file())
        self.assertTrue(guide.is_file())
        self.assertIn(TAG, notes.read_text(encoding="utf-8"))
        self.assertIn(TAG, guide.read_text(encoding="utf-8"))
        self.assertIn(TAG, readme)
        self.assertIn("docs/installation-and-usage-v0.2.md", readme)

    def test_historical_v01_release_files_remain_present(self):
        for version in ("0.1.0-beta.1", "0.1.0-beta.2", "0.1.0-beta.3"):
            self.assertTrue((ROOT / f"skillset/releases/aegis-{version}.json").is_file())
            self.assertTrue((ROOT / f"docs/releases/v{version}.md").is_file())


if __name__ == "__main__":
    unittest.main()
