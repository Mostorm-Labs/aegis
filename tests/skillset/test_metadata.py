import json
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_STAGES = {
    'P00','P01','P02','P03',
    'P10','P11','P12','P13','P14','P15','P16','P17','P18',
    'P20','P21','P22','P23','P24',
    'P30','P31','P32','P33','P34','P35','P36',
}
EXPECTED_SURFACES = ('CONTROL_REASONING','CODE_EXECUTION','CONTROL_REVIEW','CODE_REVERIFY')
EXPECTED_OPENAI_PROFILE = {
    'CONTROL_REASONING': 'chatgpt',
    'CODE_EXECUTION': 'codex',
    'CONTROL_REVIEW': 'chatgpt',
    'CODE_REVERIFY': 'codex',
}
EXPECTED_SURFACE_BY_STAGE = {
    'P30':'CONTROL_REASONING','P31':'CONTROL_REASONING',
    'P32':'CODE_EXECUTION','P33':'CODE_EXECUTION',
    'P34':'CONTROL_REVIEW','P35':'CONTROL_REVIEW',
    'P36':'CODE_REVERIFY',
}

class MetadataTests(unittest.TestCase):
    def _load(self):
        self.assertTrue((ROOT / 'tools/aegis_skillset/model.py').is_file(), 'skillset model must exist')
        from tools.aegis_skillset.model import load_skillset, validate_skillset
        return load_skillset, validate_skillset

    def test_every_stage_has_exactly_one_primary_owner(self):
        load_skillset, validate_skillset = self._load()
        config = load_skillset(ROOT)
        self.assertEqual([], validate_skillset(config))
        self.assertEqual(EXPECTED_STAGES, set(config.primary_owner_by_stage))

    def test_manifest_does_not_duplicate_stage_ownership(self):
        self.assertTrue((ROOT / 'skillset/manifest.json').is_file(), 'manifest must exist')
        raw = json.loads((ROOT / 'skillset/manifest.json').read_text())
        self.assertTrue(all('stages' not in skill for skill in raw['skills']))

    def test_only_aegis_owns_ambiguity_routing(self):
        load_skillset, _ = self._load()
        config = load_skillset(ROOT)
        self.assertEqual('aegis', config.ambiguity_router)

    def test_v02_composition_metadata_is_frozen(self):
        load_skillset, _ = self._load()
        config = load_skillset(ROOT)
        self.assertEqual(('aegis-project-state',), getattr(config, 'supporting_skills', None))
        self.assertEqual('aegis', getattr(config, 'compatibility_owner', None))
        self.assertIs(True, getattr(config, 'compatibility_requires_unavailable_evidence', None))

    def test_execution_surface_contract_is_frozen(self):
        load_skillset, _ = self._load()
        config = load_skillset(ROOT)
        self.assertEqual(EXPECTED_SURFACES, config.semantic_surfaces)
        self.assertEqual('openai', config.default_executor_profile)
        self.assertEqual(EXPECTED_OPENAI_PROFILE, config.executor_profiles['openai'])
        self.assertEqual(EXPECTED_SURFACE_BY_STAGE, config.execution_surface_by_stage)
        self.assertIs(False, config.surface_handoff_transfers_ownership)

if __name__ == '__main__':
    unittest.main()

class MetadataNegativeTests(unittest.TestCase):
    def test_unknown_stage_owner_is_rejected(self):
        from tools.aegis_skillset.model import load_skillset, validate_skillset
        config = load_skillset(ROOT)
        config.primary_owner_by_stage['P34'] = 'aegis-unknown'
        self.assertTrue(any('unknown stage owner' in e for e in validate_skillset(config)))

    def test_missing_stage_is_rejected(self):
        from tools.aegis_skillset.model import load_skillset, validate_skillset
        config = load_skillset(ROOT)
        del config.primary_owner_by_stage['P36']
        self.assertTrue(any('missing stage ownership' in e for e in validate_skillset(config)))

    def test_unknown_supporting_skill_is_rejected(self):
        config = replace(self._config(), supporting_skills=('aegis-project-state', 'aegis-unknown'))
        self.assertTrue(any('unknown supporting skill' in e for e in self._validate(config)))

    def test_non_aegis_compatibility_owner_is_rejected(self):
        config = replace(self._config(), compatibility_owner='aegis-gate-review')
        self.assertTrue(any('compatibility owner must be aegis' in e for e in self._validate(config)))

    def test_compatibility_without_unavailability_evidence_is_rejected(self):
        config = replace(self._config(), compatibility_requires_unavailable_evidence=False)
        self.assertTrue(any('compatibility requires unavailable evidence' in e for e in self._validate(config)))

    def test_unknown_execution_surface_is_rejected(self):
        mapping = dict(self._config().execution_surface_by_stage)
        mapping['P32'] = 'UNKNOWN_SURFACE'
        config = replace(self._config(), execution_surface_by_stage=mapping)
        self.assertTrue(any('unknown execution surface' in e for e in self._validate(config)))

    def test_missing_execution_stage_is_rejected(self):
        mapping = dict(self._config().execution_surface_by_stage)
        del mapping['P36']
        config = replace(self._config(), execution_surface_by_stage=mapping)
        self.assertTrue(any('missing execution surface stage' in e for e in self._validate(config)))

    def test_surface_handoff_cannot_transfer_ownership(self):
        config = replace(self._config(), surface_handoff_transfers_ownership=True)
        self.assertTrue(any('surface handoff must not transfer ownership' in e for e in self._validate(config)))

    def _config(self):
        from tools.aegis_skillset.model import load_skillset
        return load_skillset(ROOT)

    def _validate(self, config):
        from tools.aegis_skillset.model import validate_skillset
        return validate_skillset(config)
