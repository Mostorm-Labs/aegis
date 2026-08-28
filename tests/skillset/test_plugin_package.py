import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.aegis_skillset.model import load_skillset
from tools.aegis_skillset.package import build_source_bundles, render_release_manifest, tree_sha256

ROOT = Path(__file__).resolve().parents[2]


class PluginPackageTests(unittest.TestCase):
    def test_release_manifest_pins_manifest_order_and_shared_aegis_digest(self):
        manifest = render_release_manifest(ROOT, "0.1.0-task6.1")
        names = [x["name"] for x in manifest["plugin"]["skills"]]
        self.assertEqual(names, [s.name for s in load_skillset(ROOT).skills])
        self.assertEqual([x["name"] for x in manifest["standalone"]["skills"]], ["aegis"])
        self.assertEqual(manifest["plugin"]["skills"][0]["tree_sha256"], manifest["standalone"]["skills"][0]["tree_sha256"])

    def test_source_bundles_have_expected_layout_and_are_reproducible(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            p1, s1 = build_source_bundles(ROOT, "0.1.0-task6.1", out)
            first = (p1.read_bytes(), s1.read_bytes())
            p2, s2 = build_source_bundles(ROOT, "0.1.0-task6.1", out)
            self.assertEqual(first, (p2.read_bytes(), s2.read_bytes()))
            with zipfile.ZipFile(p1) as z:
                names = z.namelist()
                self.assertIn("aegis-plugin-0.1.0-task6.1/release.json", names)
                self.assertEqual({n.split('/')[2] for n in names if n.startswith("aegis-plugin-0.1.0-task6.1/skills/") and n.count('/') >= 3}, {s.name for s in load_skillset(ROOT).skills})
            with zipfile.ZipFile(s1) as z:
                self.assertIn("aegis-standalone-0.1.0-task6.1/release.json", z.namelist())
                self.assertTrue(all("/aegis/" in n or n.endswith("/aegis") or n.endswith("/release.json") for n in z.namelist()))


if __name__ == "__main__":
    unittest.main()
