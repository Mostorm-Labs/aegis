import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_STAGES = {
    'P00','P01','P02','P03',
    'P10','P11','P12','P13','P14','P15','P16','P17','P18',
    'P20','P21','P22','P23','P24',
    'P30','P31','P32','P33','P34','P35','P36',
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
