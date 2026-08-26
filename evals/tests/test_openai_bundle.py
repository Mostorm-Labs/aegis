import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from evals.providers.openai.bundle import build_skill_bundle


class OpenAISkillBundleTests(unittest.TestCase):
    def test_build_skill_bundle_is_deterministic_and_single_root(self):
        root = Path(__file__).resolve().parents[2]
        skill_dir = root / "skills" / "aegis"
        with tempfile.TemporaryDirectory() as td:
            first = Path(td) / "first.zip"
            second = Path(td) / "second.zip"
            a = build_skill_bundle(skill_dir, first)
            b = build_skill_bundle(skill_dir, second)

            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(a.sha256, b.sha256)
            self.assertEqual(a.sha256, hashlib.sha256(first.read_bytes()).hexdigest())
            self.assertEqual(a.top_level, "aegis")

            with zipfile.ZipFile(first) as zf:
                names = zf.namelist()
            self.assertIn("aegis/SKILL.md", names)
            self.assertTrue(any(name.startswith("aegis/references/") for name in names))
            self.assertFalse(any("__pycache__" in name for name in names))
            self.assertFalse(any(name.endswith(".DS_Store") for name in names))
            self.assertTrue(all(name.startswith("aegis/") for name in names))


if __name__ == "__main__":
    unittest.main()
