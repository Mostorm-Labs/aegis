import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.aegis_skillset.model import load_skillset
from tools.aegis_skillset.package import (
    build_skill_installation_kit_archive,
    build_source_bundles,
    render_release_manifest,
    tree_sha256,
)

ROOT = Path(__file__).resolve().parents[2]
RELEASE = "0.1.0-task6.1"


class PluginPackageTests(unittest.TestCase):
    def test_release_manifest_pins_manifest_order_shared_aegis_digest_and_upload_zip_identity(self):
        manifest = render_release_manifest(ROOT, RELEASE)
        names = [x["name"] for x in manifest["plugin"]["skills"]]
        self.assertEqual(names, [s.name for s in load_skillset(ROOT).skills])
        self.assertEqual([x["name"] for x in manifest["standalone"]["skills"]], ["aegis"])
        self.assertEqual(manifest["plugin"]["skills"][0]["tree_sha256"], manifest["standalone"]["skills"][0]["tree_sha256"])
        for entry in manifest["plugin"]["skills"]:
            self.assertEqual(entry.get("zip_filename"), f"{entry['name']}.zip")
            self.assertRegex(entry.get("zip_sha256", ""), r"^[0-9a-f]{64}$")

    def test_source_bundles_have_expected_layout_and_are_reproducible(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            p1, s1 = build_source_bundles(ROOT, RELEASE, out)
            first = (p1.read_bytes(), s1.read_bytes())
            p2, s2 = build_source_bundles(ROOT, RELEASE, out)
            self.assertEqual(first, (p2.read_bytes(), s2.read_bytes()))
            with zipfile.ZipFile(p1) as z:
                names = z.namelist()
                self.assertIn(f"aegis-plugin-{RELEASE}/release.json", names)
                self.assertEqual({n.split('/')[2] for n in names if n.startswith(f"aegis-plugin-{RELEASE}/skills/") and n.count('/') >= 3}, {s.name for s in load_skillset(ROOT).skills})
            with zipfile.ZipFile(s1) as z:
                self.assertIn(f"aegis-standalone-{RELEASE}/release.json", z.namelist())
                self.assertTrue(all("/aegis/" in n or n.endswith("/aegis") or n.endswith("/release.json") for n in z.namelist()))

    def test_package_dir_contains_upload_ready_nine_skill_installation_kit(self):
        expected_skills = [s.name for s in load_skillset(ROOT).skills]
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            command = [
                sys.executable,
                str(ROOT / "scripts/build_aegis_distributions.py"),
                "--package-dir",
                str(out),
            ]
            run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(0, run.returncode, run.stdout + run.stderr)

            kit = out / f"aegis-skills-{RELEASE}"
            self.assertTrue(kit.is_dir(), "package-dir must emit the user-facing installation kit")
            release_path = kit / "release.json"
            self.assertTrue(release_path.is_file())
            release = json.loads(release_path.read_text(encoding="utf-8"))

            zip_paths = sorted(kit.glob("*.zip"))
            self.assertEqual(
                sorted(f"{name}.zip" for name in expected_skills),
                sorted(path.name for path in zip_paths),
            )
            self.assertEqual(len(expected_skills), 9)

            by_name = {entry["name"]: entry for entry in release["plugin"]["skills"]}
            self.assertEqual(set(by_name), set(expected_skills))

            first_bytes = {}
            for skill_name in expected_skills:
                path = kit / f"{skill_name}.zip"
                data = path.read_bytes()
                first_bytes[skill_name] = data
                entry = by_name[skill_name]
                self.assertEqual(entry["zip_filename"], path.name)
                self.assertEqual(entry["zip_sha256"], hashlib.sha256(data).hexdigest())
                self.assertEqual(entry["tree_sha256"], tree_sha256(ROOT / "skills" / skill_name))
                with zipfile.ZipFile(path) as z:
                    names = z.namelist()
                    self.assertIn("SKILL.md", names)
                    self.assertIn("agents/openai.yaml", names)
                    self.assertFalse(any(name.startswith(f"{skill_name}/") for name in names))

            rerun = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(0, rerun.returncode, rerun.stdout + rerun.stderr)
            self.assertEqual(
                first_bytes,
                {name: (kit / f"{name}.zip").read_bytes() for name in expected_skills},
            )

    def test_explicit_release_version_builds_reproducible_installation_archive(self):
        release = "0.1.0-beta.1"
        expected_skills = [s.name for s in load_skillset(ROOT).skills]
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            command = [
                sys.executable,
                str(ROOT / "scripts/build_aegis_distributions.py"),
                "--version",
                release,
                "--installation-kit-archive-dir",
                str(out),
            ]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            archive_path = out / f"aegis-skill-installation-kit-{release}.zip"
            self.assertTrue(archive_path.is_file())
            first_bytes = archive_path.read_bytes()

            with zipfile.ZipFile(archive_path) as z:
                prefix = f"aegis-skills-{release}/"
                names = set(z.namelist())
                self.assertIn(prefix + "release.json", names)
                for skill_name in expected_skills:
                    self.assertIn(prefix + f"{skill_name}.zip", names)
                manifest = json.loads(z.read(prefix + "release.json").decode("utf-8"))
                self.assertEqual(release, manifest["release_version"])

            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(0, second.returncode, second.stdout + second.stderr)
            self.assertEqual(first_bytes, archive_path.read_bytes())
            self.assertEqual(
                first_bytes,
                build_skill_installation_kit_archive(ROOT, release, out).read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
