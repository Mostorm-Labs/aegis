import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V02 = ROOT / 'skillset/dogfood/installed-platform-v0.2.json'


def collect_keys(value):
    keys = set()
    if isinstance(value, dict):
        keys.update(value)
        for child in value.values():
            keys.update(collect_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(collect_keys(child))
    return keys


class HistoricalReinterpretationV02Tests(unittest.TestCase):
    def _load(self):
        self.assertTrue(V02.is_file(), 'v0.2 historical reinterpretation artifact missing')
        return json.loads(V02.read_text(encoding='utf-8'))

    def test_v02_links_immutable_v01_history(self):
        data = self._load()
        self.assertEqual('0.2', data['schema_version'])
        self.assertEqual('skillset/dogfood/installed-platform-v0.1.json', data['historical_source'])
        self.assertEqual('f48391cf93cd5b2543f8f23c1e0256e7dac6e5cc', data['historical_source_blob_sha'])
        self.assertEqual('terminal_trace_v0.2', data['oracle'])
        self.assertTrue(data['historical_source_immutable'])

    def test_v02_does_not_use_first_skill_acceptance_fields(self):
        data = self._load()
        forbidden = {'expected_skill', 'expected_initial_skill', 'actual_initial_skill', 'actual_first_skill'}
        self.assertTrue(forbidden.isdisjoint(collect_keys(data)))

    def test_each_case_has_v02_policy_basis(self):
        data = self._load()
        self.assertEqual(4, len(data['cases']))
        for case in data['cases']:
            policy = case['policy']
            valid_basis = bool(
                policy.get('required_primary_owner')
                or policy.get('routing_only_reason')
                or policy.get('short_circuit')
                or policy.get('requested_primary_owner')
            )
            with self.subTest(case=case['id']):
                self.assertTrue(valid_basis)
                self.assertTrue(case['evidence_refs'])

    def test_incomplete_historical_cases_fail_closed(self):
        data = self._load()
        for case in data['cases']:
            with self.subTest(case=case['id']):
                self.assertEqual('BLOCKED_EVIDENCE', case['interpretation_status'])
                self.assertTrue(case['evidence_gaps'])
                self.assertTrue(case['rerun_required'])


if __name__ == '__main__':
    unittest.main()
