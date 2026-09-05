import tempfile
import unittest
from pathlib import Path

from tests.verification_productization import ecv0_fixtures as fixtures


HISTORICAL_VERSION = "0.2.0-beta.1"
HISTORICAL_TAG = f"v{HISTORICAL_VERSION}"


def _write_shape_only_skillset_workflow(root: Path, source: str) -> None:
    target = root / ".github/workflows/skillset.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            (
                "Check Control Plane v0.2 published source binding",
                f"refs/tags/{HISTORICAL_TAG}",
                source,
                f"git archive refs/tags/{HISTORICAL_TAG}",
                'cd "$historical_root"',
                f"python3 scripts/build_aegis_distributions.py --check --version {HISTORICAL_VERSION}",
            )
        ),
        encoding="utf-8",
    )


def _write_shape_only_release_workflow(root: Path) -> None:
    target = root / ".github/workflows/release.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            (
                'python3 scripts/build_aegis_distributions.py --version "$VERSION" --check',
                "embedded == manifest",
                'hashlib.sha256(data).hexdigest() == entry["zip_sha256"]',
                "sha256sum -c SHA256SUMS",
            )
        ),
        encoding="utf-8",
    )


class ECV0ApplicabilityTests(unittest.TestCase):
    def test_ec_ap01_rejects_shape_only_historical_source_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_source = "f" * 40
            _write_shape_only_skillset_workflow(root, fake_source)

            original_root = fixtures.ROOT
            original_source = fixtures.HISTORICAL_SOURCE
            try:
                fixtures.ROOT = root
                fixtures.HISTORICAL_SOURCE = fake_source
                self.assertFalse(
                    fixtures.run_applicability("EC-AP01"),
                    "EC-AP01 must resolve and execute the historical source, not accept workflow text shape",
                )
            finally:
                fixtures.ROOT = original_root
                fixtures.HISTORICAL_SOURCE = original_source

    def test_ec_ap02_rejects_shape_only_release_mismatch_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_shape_only_release_workflow(root)

            original_root = fixtures.ROOT
            try:
                fixtures.ROOT = root
                self.assertFalse(
                    fixtures.run_applicability("EC-AP02"),
                    "EC-AP02 must execute a release-applicable mismatch and observe rejection",
                )
            finally:
                fixtures.ROOT = original_root


if __name__ == "__main__":
    unittest.main()
