import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.verification_productization.ecv0_fixtures import historical_release_source_is_coherent
from tools.aegis_skillset.package import render_release_manifest


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.2.0-beta.2"
TAG = f"v{VERSION}"


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _make_historical_repo(base: Path, *, coherent: bool) -> tuple[Path, str]:
    root = base / "repo"
    root.mkdir()
    skill = root / "skills/aegis/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# Aegis fixture\n", encoding="utf-8")

    distribution = root / "skillset/distribution.json"
    distribution.parent.mkdir(parents=True)
    distribution.write_text(
        json.dumps(
            {
                "plugin": {"skills": ["aegis"]},
                "standalone": {"skills": ["aegis"]},
            },
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    release = root / f"skillset/releases/aegis-{VERSION}.json"
    release.parent.mkdir(parents=True)
    release.write_text(
        json.dumps(render_release_manifest(root, VERSION), sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    if not coherent:
        skill.write_text("# Aegis fixture\nmanifest drift\n", encoding="utf-8")

    _git(root, "init")
    _git(root, "config", "user.email", "fixture@example.invalid")
    _git(root, "config", "user.name", "Aegis Fixture")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "historical release fixture")
    source = _git(root, "rev-parse", "HEAD")
    _git(root, "tag", TAG)
    return root, source


class ControlPlaneV02ReleaseCandidateTests(unittest.TestCase):
    def test_public_release_identity_resolves_exact_historical_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository, source = _make_historical_repo(Path(tmp), coherent=True)
            self.assertTrue(
                historical_release_source_is_coherent(
                    repository,
                    tag=TAG,
                    expected_source=source,
                    version=VERSION,
                )
            )

    def test_public_release_identity_rejects_unresolvable_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository, source = _make_historical_repo(Path(tmp), coherent=True)
            self.assertFalse(
                historical_release_source_is_coherent(
                    repository,
                    tag=f"{TAG}-missing",
                    expected_source=source,
                    version=VERSION,
                )
            )

    def test_public_release_identity_rejects_wrong_publication_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository, source = _make_historical_repo(Path(tmp), coherent=True)
            marker = repository / "later.txt"
            marker.write_text("later candidate\n", encoding="utf-8")
            _git(repository, "add", "later.txt")
            _git(repository, "commit", "-m", "later candidate")
            wrong_source = _git(repository, "rev-parse", "HEAD")
            self.assertNotEqual(source, wrong_source)
            self.assertFalse(
                historical_release_source_is_coherent(
                    repository,
                    tag=TAG,
                    expected_source=wrong_source,
                    version=VERSION,
                )
            )

    def test_public_release_identity_rejects_historical_manifest_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository, source = _make_historical_repo(Path(tmp), coherent=False)
            self.assertFalse(
                historical_release_source_is_coherent(
                    repository,
                    tag=TAG,
                    expected_source=source,
                    version=VERSION,
                )
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
