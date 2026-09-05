import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_VERSION = "0.2.0-beta.1"
HISTORICAL_TAG = f"v{HISTORICAL_VERSION}"
HISTORICAL_SOURCE = "3253abced7a17d66d8754fa84d7953408aae49d4"


class ECV0ApplicabilityTests(unittest.TestCase):
    def test_ec_ap01_non_release_candidate_uses_historical_source_binding(self):
        workflow = (ROOT / ".github/workflows/skillset.yml").read_text(encoding="utf-8")

        self.assertNotIn(
            "Check Aegis development release manifest",
            workflow,
            "legacy development snapshot must not gate unrelated non-release candidate bytes",
        )
        self.assertIn("Check Control Plane v0.2 published source binding", workflow)
        self.assertIn(f"refs/tags/{HISTORICAL_TAG}", workflow)
        self.assertIn(HISTORICAL_SOURCE, workflow)
        self.assertIn(f"git archive refs/tags/{HISTORICAL_TAG}", workflow)
        self.assertIn('cd "$historical_root"', workflow)
        self.assertIn(
            f"python3 scripts/build_aegis_distributions.py --version {HISTORICAL_VERSION} --check",
            workflow,
        )

    def test_ec_ap02_active_release_candidate_still_fails_closed_on_mismatch(self):
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")

        self.assertIn(
            'python3 scripts/build_aegis_distributions.py --version "$VERSION" --check',
            workflow,
        )
        self.assertIn("embedded == manifest", workflow)
        self.assertIn("hashlib.sha256(data).hexdigest() == entry[\"zip_sha256\"]", workflow)
        self.assertIn("sha256sum -c SHA256SUMS", workflow)


if __name__ == "__main__":
    unittest.main()
