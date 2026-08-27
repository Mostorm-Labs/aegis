import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REQUIRED_TOKENS=['P00','P18','P20','P24','P30','P36','BLOCKED_AUTHORITY','IMPLEMENTATION_DEFECT','Project-state bootstrap','Code Complete != Gate Complete']
STAGE_SPECIALISTS=(
    'aegis-discovery','aegis-modeling','aegis-architecture','aegis-verification',
    'aegis-governance','aegis-implementation','aegis-gate-review',
)

class CompositeTests(unittest.TestCase):
    def test_canonical_composite_source_exists(self):
        self.assertTrue((ROOT/'skillset/skills/aegis/SKILL.md').is_file())

    def test_generated_composite_preserves_required_semantics(self):
        self.assertTrue((ROOT/'skills/aegis/SKILL.md').is_file())
        text='\n'.join(p.read_text() for p in (ROOT/'skills/aegis').rglob('*.md'))
        for token in REQUIRED_TOKENS:
            with self.subTest(token=token): self.assertIn(token,text)


class CompositionInstructionContractTests(unittest.TestCase):
    def _canonical(self, skill):
        return (ROOT/'skillset/skills'/skill/'SKILL.md').read_text(encoding='utf-8')

    def _generated(self, skill):
        return (ROOT/'skills'/skill/'SKILL.md').read_text(encoding='utf-8')

    def test_shared_handoff_contract_distinguishes_support_and_ownership_edges(self):
        text=(ROOT/'skillset/shared/handoff-contract.md').read_text(encoding='utf-8')
        for token in (
            'support_return',
            'ownership_handoff',
            'Support Edge != Ownership Handoff Edge',
            'final-answer owner',
            'aegis-project-state',
            'Direct Primary-to-Primary substantive chaining is forbidden',
            'specialist-unavailability evidence',
        ):
            with self.subTest(token=token): self.assertIn(token,text)

    def test_router_encodes_multiskill_and_compatibility_ownership_boundary(self):
        for text in (self._canonical('aegis'), self._generated('aegis')):
            for token in (
                'Multi-Skill Mode',
                'final-answer owner',
                'Composite Compatibility Mode',
                'specialist-unavailability evidence',
                'blocked short-circuit',
            ):
                with self.subTest(token=token): self.assertIn(token,text)

    def test_project_state_encodes_direct_owner_and_support_only_modes(self):
        for text in (self._canonical('aegis-project-state'), self._generated('aegis-project-state')):
            for token in (
                'Direct Project State task',
                'final-answer owner',
                'Support mode',
                'support_return',
                'facts only',
                'no stage verdict',
                'terminal blocked result to `aegis`',
            ):
                with self.subTest(token=token): self.assertIn(token,text)

    def test_stage_specialists_encode_unique_primary_and_no_primary_chaining(self):
        for skill in STAGE_SPECIALISTS:
            for source in ('canonical','generated'):
                text=self._canonical(skill) if source=='canonical' else self._generated(skill)
                for token in (
                    'unique Primary Owner',
                    'Project State support',
                    'does not transfer ownership',
                    'Direct Primary-to-Primary substantive chaining is forbidden',
                    'ownership_handoff',
                    'stop substantive execution',
                ):
                    with self.subTest(skill=skill,source=source,token=token): self.assertIn(token,text)

    def test_generated_shared_handoff_contract_matches_v02_tokens(self):
        for skill in ('aegis','aegis-project-state',*STAGE_SPECIALISTS):
            text=(ROOT/'skills'/skill/'references/shared/handoff-contract.md').read_text(encoding='utf-8')
            with self.subTest(skill=skill):
                self.assertIn('support_return',text)
                self.assertIn('ownership_handoff',text)


if __name__=='__main__': unittest.main()
