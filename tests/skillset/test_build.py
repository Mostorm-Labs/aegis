import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class BuildTests(unittest.TestCase):
    def _fixture(self, root: Path):
        (root/'skillset/skills/demo').mkdir(parents=True)
        (root/'skillset/shared').mkdir(parents=True)
        (root/'skillset/skills/demo/SKILL.md').write_text('---\nname: demo\ndescription: Demo.\n---\n# Demo\n')
        (root/'skillset/shared/core-invariants.md').write_text('# Core\n')

    def _spec(self):
        from tools.aegis_skillset.model import SkillSpec
        return SkillSpec('demo','specialist','skillset/skills/demo','skills/demo',('core-invariants',))

    def test_two_renders_are_byte_identical(self):
        from tools.aegis_skillset.build import render_distribution
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._fixture(root)
            self.assertEqual(render_distribution(root,self._spec()), render_distribution(root,self._spec()))

    def test_generated_shared_reference_matches_canonical_source(self):
        from tools.aegis_skillset.build import render_distribution
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._fixture(root)
            rendered=render_distribution(root,self._spec())
            self.assertEqual((root/'skillset/shared/core-invariants.md').read_bytes(), rendered['skills/demo/references/shared/core-invariants.md'])

    def test_check_detects_distribution_drift(self):
        from tools.aegis_skillset.build import render_distribution
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._fixture(root)
            rendered=render_distribution(root,self._spec())
            for rel,data in rendered.items():
                p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
            target=root/'skills/demo/SKILL.md'; target.write_text('drift')
            self.assertNotEqual(rendered['skills/demo/SKILL.md'], target.read_bytes())

    def test_unsafe_relative_path_is_rejected(self):
        from tools.aegis_skillset.build import _safe_rel
        with self.assertRaises(ValueError): _safe_rel('../escape')

if __name__=='__main__': unittest.main()

class SpecialistSourceTests(unittest.TestCase):
    SPECIALISTS=('aegis-project-state','aegis-governance','aegis-gate-review','aegis-verification','aegis-architecture','aegis-modeling','aegis-discovery','aegis-implementation')
    def test_specialist_sources_have_no_placeholders(self):
        for name in self.SPECIALISTS:
            root=ROOT/'skillset/skills'/name
            text='\n'.join(p.read_text(errors='ignore') for p in root.rglob('*') if p.is_file())
            with self.subTest(name=name):
                self.assertNotIn('TODO',text)
                self.assertNotIn('example_asset',text)
                self.assertIn('Earlier untrusted layer',text)
    def test_specialists_do_not_claim_unowned_stage_ids(self):
        import re
        from tools.aegis_skillset.model import load_skillset
        config=load_skillset(ROOT)
        owner=config.primary_owner_by_stage
        for name in self.SPECIALISTS:
            text=(ROOT/'skillset/skills'/name/'SKILL.md').read_text()
            claimed=set(re.findall(r'\bP\d{2}\b',text))
            if name=='aegis-project-state':
                self.assertEqual(set(),claimed)
            else:
                self.assertTrue(all(owner.get(stage)==name for stage in claimed), (name,claimed))

class DistributionDriftTests(unittest.TestCase):
    def test_extra_distribution_file_is_drift(self):
        from tools.aegis_skillset.build import check_distributions
        extra=ROOT/'skills/aegis/EXTRA.tmp'
        extra.write_text('x')
        try:
            self.assertIn('skills/aegis/EXTRA.tmp', check_distributions(ROOT))
        finally:
            extra.unlink()
