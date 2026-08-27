import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REQUIRED_TOKENS=['P00','P18','P20','P24','P30','P36','BLOCKED_AUTHORITY','IMPLEMENTATION_DEFECT','Project-state bootstrap','Code Complete != Gate Complete']

class CompositeTests(unittest.TestCase):
    def test_canonical_composite_source_exists(self):
        self.assertTrue((ROOT/'skillset/skills/aegis/SKILL.md').is_file())

    def test_generated_composite_preserves_required_semantics(self):
        self.assertTrue((ROOT/'skills/aegis/SKILL.md').is_file())
        text='\n'.join(p.read_text() for p in (ROOT/'skills/aegis').rglob('*.md'))
        for token in REQUIRED_TOKENS:
            with self.subTest(token=token): self.assertIn(token,text)

if __name__=='__main__': unittest.main()
