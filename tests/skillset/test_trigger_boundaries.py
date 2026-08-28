import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def frontmatter_description(skill: str) -> str:
    text = (ROOT / 'skillset' / 'skills' / skill / 'SKILL.md').read_text(encoding='utf-8')
    match = re.search(r'^description:\s*(.+)$', text, re.MULTILINE)
    if not match:
        raise AssertionError(f'{skill}: missing frontmatter description')
    return match.group(1).strip().lower()


class TriggerBoundaryTests(unittest.TestCase):
    def test_composite_facade_description_is_router_scoped(self):
        desc = frontmatter_description('aegis')
        self.assertIn('owning lifecycle stage is unknown', desc)
        self.assertIn('what should this project do next', desc)
        self.assertIn('where should we start or resume', desc)
        self.assertIn('explicit handoff from a specialist', desc)
        self.assertIn('single specialist clearly owns the request', desc)
        self.assertIn('only this composite skill is installed', desc)
        for forbidden in (
            'software-development work',
            'earliest untrusted layer',
            'gate',
            'architecture',
            'schema',
            'implementation',
            'evidence',
        ):
            self.assertNotIn(forbidden, desc)

    def test_project_state_description_is_manifest_scoped(self):
        desc = frontmatter_description('aegis-project-state')
        self.assertIn('.aegis', desc)
        self.assertIn('manifest', desc)
        self.assertNotIn('authority/gate/evidence/integration records', desc)
        self.assertNotIn('gate evidence audit', desc)

    def test_direct_specialists_claim_the_protected_requests(self):
        architecture = frontmatter_description('aegis-architecture')
        gate_review = frontmatter_description('aegis-gate-review')
        self.assertIn('design the system architecture', architecture)
        self.assertIn('direct', architecture)
        self.assertIn('gate evidence', gate_review)
        self.assertIn('pr', gate_review)


if __name__ == '__main__':
    unittest.main()
