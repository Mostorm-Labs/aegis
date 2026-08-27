import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DistributionValidationTests(unittest.TestCase):
    def test_all_generated_distributions_validate(self):
        try:
            from tools.aegis_skillset.distribution import validate_generated_skills
        except ModuleNotFoundError:
            self.fail('distribution validator not implemented')
        self.assertEqual([], validate_generated_skills(ROOT))

    def test_missing_agents_metadata_is_rejected(self):
        try:
            from tools.aegis_skillset.distribution import validate_generated_skills
        except ModuleNotFoundError:
            self.fail('distribution validator not implemented')
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            shutil.copytree(ROOT / 'skillset', tmp / 'skillset')
            shutil.copytree(ROOT / 'skills', tmp / 'skills')
            (tmp / 'skills/aegis-modeling/agents/openai.yaml').unlink()
            errors = validate_generated_skills(tmp)
            self.assertTrue(any('agents/openai.yaml' in e for e in errors), errors)

    def test_frontmatter_name_mismatch_is_rejected(self):
        try:
            from tools.aegis_skillset.distribution import validate_generated_skills
        except ModuleNotFoundError:
            self.fail('distribution validator not implemented')
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            shutil.copytree(ROOT / 'skillset', tmp / 'skillset')
            shutil.copytree(ROOT / 'skills', tmp / 'skills')
            path = tmp / 'skills/aegis-modeling/SKILL.md'
            path.write_text(path.read_text().replace('name: aegis-modeling', 'name: wrong-name', 1))
            errors = validate_generated_skills(tmp)
            self.assertTrue(any('frontmatter name' in e for e in errors), errors)

    def test_missing_relative_reference_is_rejected(self):
        try:
            from tools.aegis_skillset.distribution import validate_generated_skills
        except ModuleNotFoundError:
            self.fail('distribution validator not implemented')
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            shutil.copytree(ROOT / 'skillset', tmp / 'skillset')
            shutil.copytree(ROOT / 'skills', tmp / 'skills')
            path = tmp / 'skills/aegis-modeling/SKILL.md'
            path.write_text(path.read_text() + '\nRead [missing](references/missing.md).\n')
            errors = validate_generated_skills(tmp)
            self.assertTrue(any('missing reference' in e for e in errors), errors)

    def test_placeholder_is_rejected(self):
        try:
            from tools.aegis_skillset.distribution import validate_generated_skills
        except ModuleNotFoundError:
            self.fail('distribution validator not implemented')
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            shutil.copytree(ROOT / 'skillset', tmp / 'skillset')
            shutil.copytree(ROOT / 'skills', tmp / 'skills')
            path = tmp / 'skills/aegis-modeling/SKILL.md'
            path.write_text(path.read_text() + '\nTODO: later\n')
            errors = validate_generated_skills(tmp)
            self.assertTrue(any('placeholder' in e for e in errors), errors)


if __name__ == '__main__':
    unittest.main()
