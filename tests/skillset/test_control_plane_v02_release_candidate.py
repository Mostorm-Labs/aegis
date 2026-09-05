import io
import json
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.2.0-beta.1"
TAG = f"v{VERSION}"
HISTORICAL_SOURCE = "3253abced7a17d66d8754fa84d7953408aae49d4"


class ControlPlaneV02ReleaseCandidateTests(unittest.TestCase):
    def _resolve_historical_source(self) -> str:
        proc = subprocess.run(
            ["git", "rev-parse", f"refs/tags/{TAG}^{{commit}}"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(
            0,
            proc.returncode,
            f"historical release tag {TAG} must be reviewer-resolvable: {proc.stderr.strip()}",
        )
        resolved = proc.stdout.strip()
        self.assertEqual(
            HISTORICAL_SOURCE,
            resolved,
            "historical beta.1 release tag must resolve to the frozen publication source",
        )
        return resolved

    def _extract_historical_source(self, destination: Path) -> None:
        source = self._resolve_historical_source()
        proc = subprocess.run(
            ["git", "archive", source],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(
            0,
            proc.returncode,
            f"historical beta.1 source must be archivable: {proc.stderr.decode('utf-8', errors='replace').strip()}",
        )
        with tarfile.open(fileobj=io.BytesIO(proc.stdout), mode="r:") as archive:
            archive.extractall(destination, filter="data")

    def _install_current_checker(self, historical_root: Path) -> None:
        shutil.copy2(
            ROOT / "scripts/build_aegis_distributions.py",
            historical_root / "scripts/build_aegis_distributions.py",
        )
        target = historical_root / "tools/aegis_skillset"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(ROOT / "tools/aegis_skillset", target)

    def test_public_release_identity_is_bound_to_historical_source(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            historical_root = Path(temporary_directory)
            self._extract_historical_source(historical_root)
            self._install_current_checker(historical_root)

            check = subprocess.run(
                [
                    "python3",
                    "scripts/build_aegis_distributions.py",
                    "--check",
                    "--version",
                    VERSION,
                ],
                cwd=historical_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(
                0,
                check.returncode,
                f"historical beta.1 release source must satisfy its frozen manifest: {check.stdout}{check.stderr}",
            )

            plugin = json.loads(
                (historical_root / "plugins/aegis/.codex-plugin/plugin.json").read_text(
                    encoding="utf-8"
                )
            )
            release_path = historical_root / f"skillset/releases/aegis-{VERSION}.json"
            self.assertTrue(release_path.is_file(), "beta.1 release manifest must exist historically")
            release = json.loads(release_path.read_text(encoding="utf-8"))

            self.assertEqual(VERSION, plugin["version"])
            self.assertEqual(VERSION, release["release_version"])
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
