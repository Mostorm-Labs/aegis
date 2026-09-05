import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.2.0-beta.1"
TAG = f"v{VERSION}"
HISTORICAL_SOURCE = "3253abced7a17d66d8754fa84d7953408aae49d4"


class ControlPlaneV02ReleaseCandidateTests(unittest.TestCase):
    def test_public_release_identity_is_bound_to_historical_source(self):
        workflow = (ROOT / ".github/workflows/skillset.yml").read_text(encoding="utf-8")

        self.assertIn("Check Control Plane v0.2 published source binding", workflow)
        self.assertIn(f"refs/tags/{TAG}", workflow)
        self.assertIn(HISTORICAL_SOURCE, workflow)
        self.assertIn(f"git archive refs/tags/{TAG}", workflow)
        self.assertIn('historical_root="$(mktemp -d)"', workflow)
        self.assertIn('cd "$historical_root"', workflow)
        self.assertIn(
            f"python3 scripts/build_aegis_distributions.py --check --version {VERSION}",
            workflow,
        )
        self.assertNotIn(
            "Check Aegis development release manifest",
            workflow,
            "a non-release candidate must not be coupled to a historical development manifest",
        )

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
