import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


class RoutingTests(unittest.TestCase):
    def test_routing_module_exists(self):
        self.assertTrue((ROOT/'tools/aegis_skillset/routing.py').is_file())

    def test_protected_routing_corpus_is_valid(self):
        self.assertTrue((ROOT/'tools/aegis_skillset/routing.py').is_file())
        from tools.aegis_skillset.routing import validate_routing_corpus
        self.assertEqual([], validate_routing_corpus(ROOT))


class TerminalTraceOracleTests(unittest.TestCase):
    def _config(self):
        from tools.aegis_skillset.model import load_skillset
        return load_skillset(ROOT)

    def _evaluate(self, case, trace):
        from tools.aegis_skillset import routing
        evaluator = getattr(routing, 'evaluate_terminal_trace', None)
        self.assertIsNotNone(evaluator, 'terminal-trace evaluator missing')
        return evaluator(case, trace, self._config())

    @staticmethod
    def _gate_case():
        return {
            'required_primary_owner': 'aegis-gate-review',
            'allowed_supporting_skills': ['aegis-project-state'],
            'router_policy': 'only_for_genuine_ambiguity_or_accepted_earlier_blocker',
            'normal_terminal_owner': 'aegis-gate-review',
            'short_circuit': {
                'allowed': True,
                'condition': 'earlier_blocker_conclusively_established',
                'terminal_owner': 'aegis',
            },
        }

    def test_support_first_gate_review_passes(self):
        trace = {
            'terminal': True,
            'mode': 'multi_skill',
            'invocations': [
                {'skill': 'aegis-project-state', 'role': 'support'},
                {'skill': 'aegis-gate-review', 'role': 'primary'},
            ],
            'final_answer_owner': 'aegis-gate-review',
            'genuine_ambiguity': False,
            'earlier_blocker_conclusively_established': False,
            'specialist_availability': {'aegis-gate-review': 'available'},
            'ownership_edges': [],
            'handoff_edges': [],
            'forbidden_downstream_substantive_execution': 0,
            'primary_substantive_result_emitted': True,
        }
        result = self._evaluate(self._gate_case(), trace)
        self.assertEqual('PASS', result.verdict)
        self.assertEqual((), result.violations)
        self.assertEqual((), result.evidence_gaps)

    def test_support_ownership_leak_fails(self):
        trace = {
            'terminal': True,
            'mode': 'multi_skill',
            'invocations': [
                {'skill': 'aegis-project-state', 'role': 'support'},
            ],
            'final_answer_owner': 'aegis-project-state',
            'genuine_ambiguity': False,
            'earlier_blocker_conclusively_established': False,
            'specialist_availability': {'aegis-gate-review': 'available'},
            'ownership_edges': [],
            'handoff_edges': [],
            'forbidden_downstream_substantive_execution': 0,
            'primary_substantive_result_emitted': False,
        }
        result = self._evaluate(self._gate_case(), trace)
        self.assertEqual('FAIL', result.verdict)
        self.assertIn('SUPPORT_OWNERSHIP_LEAK', result.violations)

    def test_router_ownership_leak_fails(self):
        trace = {
            'terminal': True,
            'mode': 'multi_skill',
            'invocations': [
                {'skill': 'aegis', 'role': 'router'},
            ],
            'final_answer_owner': 'aegis',
            'genuine_ambiguity': False,
            'earlier_blocker_conclusively_established': False,
            'specialist_availability': {'aegis-gate-review': 'available'},
            'ownership_edges': [],
            'handoff_edges': [],
            'forbidden_downstream_substantive_execution': 0,
            'primary_substantive_result_emitted': False,
        }
        result = self._evaluate(self._gate_case(), trace)
        self.assertEqual('FAIL', result.verdict)
        self.assertIn('ROUTER_OWNERSHIP_LEAK', result.violations)

    def test_direct_primary_chain_fails(self):
        case = {
            'required_primary_owner': 'aegis-architecture',
            'allowed_supporting_skills': ['aegis-project-state'],
            'router_policy': 'only_for_genuine_ambiguity_or_accepted_earlier_blocker',
            'normal_terminal_owner': 'aegis-architecture',
        }
        trace = {
            'terminal': True,
            'mode': 'multi_skill',
            'invocations': [
                {'skill': 'aegis-architecture', 'role': 'primary'},
                {'skill': 'aegis-verification', 'role': 'primary'},
            ],
            'final_answer_owner': 'aegis-verification',
            'genuine_ambiguity': False,
            'earlier_blocker_conclusively_established': False,
            'specialist_availability': {
                'aegis-architecture': 'available',
                'aegis-verification': 'available',
            },
            'ownership_edges': [['aegis-architecture', 'aegis-verification']],
            'handoff_edges': [],
            'forbidden_downstream_substantive_execution': 0,
            'primary_substantive_result_emitted': True,
        }
        result = self._evaluate(case, trace)
        self.assertEqual('FAIL', result.verdict)
        self.assertIn('DIRECT_PRIMARY_CHAIN', result.violations)

    def test_earlier_blocker_can_skip_requested_primary(self):
        case = {
            'requested_primary_owner': 'aegis-architecture',
            'allowed_supporting_skills': ['aegis-project-state'],
            'router_policy': 'only_for_genuine_ambiguity_or_accepted_earlier_blocker',
            'short_circuit': {
                'allowed': True,
                'condition': 'earlier_blocker_conclusively_established',
                'terminal_owner': 'aegis',
            },
            'must_stop': True,
        }
        trace = {
            'terminal': True,
            'mode': 'multi_skill',
            'invocations': [
                {'skill': 'aegis-project-state', 'role': 'support'},
                {'skill': 'aegis', 'role': 'router'},
            ],
            'final_answer_owner': 'aegis',
            'genuine_ambiguity': False,
            'earlier_blocker_conclusively_established': True,
            'specialist_availability': {'aegis-architecture': 'available'},
            'ownership_edges': [],
            'handoff_edges': [],
            'forbidden_downstream_substantive_execution': 0,
            'primary_substantive_result_emitted': False,
        }
        result = self._evaluate(case, trace)
        self.assertEqual('PASS', result.verdict)

    def test_compatibility_requires_unavailability_evidence(self):
        case = {
            'requested_primary_owner': 'aegis-modeling',
            'compatibility_owner': 'aegis',
            'requires_specialist_unavailable_evidence': True,
            'normal_terminal_owner': 'aegis',
        }
        trace = {
            'terminal': True,
            'mode': 'compatibility',
            'invocations': [
                {'skill': 'aegis', 'role': 'compatibility'},
            ],
            'final_answer_owner': 'aegis',
            'genuine_ambiguity': False,
            'earlier_blocker_conclusively_established': False,
            'specialist_availability': {},
            'ownership_edges': [],
            'handoff_edges': [],
            'forbidden_downstream_substantive_execution': 0,
            'primary_substantive_result_emitted': True,
        }
        result = self._evaluate(case, trace)
        self.assertEqual('BLOCKED_EVIDENCE', result.verdict)
        self.assertIn('specialist availability: aegis-modeling', result.evidence_gaps)

    def test_bounded_router_primary_router_blocker_return_passes(self):
        case = {
            'required_primary_owner': 'aegis-architecture',
            'allowed_supporting_skills': ['aegis-project-state'],
            'router_policy': 'only_for_genuine_ambiguity_or_accepted_earlier_blocker',
            'normal_terminal_owner': 'aegis-architecture',
            'short_circuit': {
                'allowed': True,
                'condition': 'earlier_blocker_conclusively_established',
                'terminal_owner': 'aegis',
            },
        }
        trace = {
            'terminal': True,
            'mode': 'multi_skill',
            'invocations': [
                {'skill': 'aegis', 'role': 'router'},
                {'skill': 'aegis-architecture', 'role': 'primary'},
                {'skill': 'aegis', 'role': 'router'},
            ],
            'final_answer_owner': 'aegis',
            'genuine_ambiguity': False,
            'earlier_blocker_conclusively_established': True,
            'specialist_availability': {'aegis-architecture': 'available'},
            'ownership_edges': [
                ['aegis', 'aegis-architecture'],
                ['aegis-architecture', 'aegis'],
            ],
            'handoff_edges': [['aegis-architecture', 'aegis']],
            'forbidden_downstream_substantive_execution': 0,
            'primary_substantive_result_emitted': False,
        }
        result = self._evaluate(case, trace)
        self.assertEqual('PASS', result.verdict)

    def test_ownership_cycle_fails(self):
        case = {
            'required_primary_owner': 'aegis-architecture',
            'allowed_supporting_skills': ['aegis-project-state'],
            'router_policy': 'only_for_genuine_ambiguity_or_accepted_earlier_blocker',
            'normal_terminal_owner': 'aegis-architecture',
            'short_circuit': {
                'allowed': True,
                'condition': 'earlier_blocker_conclusively_established',
                'terminal_owner': 'aegis',
            },
        }
        trace = {
            'terminal': True,
            'mode': 'multi_skill',
            'invocations': [
                {'skill': 'aegis-architecture', 'role': 'primary'},
                {'skill': 'aegis', 'role': 'router'},
                {'skill': 'aegis-architecture', 'role': 'primary'},
                {'skill': 'aegis', 'role': 'router'},
            ],
            'final_answer_owner': 'aegis',
            'genuine_ambiguity': False,
            'earlier_blocker_conclusively_established': True,
            'specialist_availability': {'aegis-architecture': 'available'},
            'ownership_edges': [
                ['aegis-architecture', 'aegis'],
                ['aegis', 'aegis-architecture'],
                ['aegis-architecture', 'aegis'],
            ],
            'handoff_edges': [
                ['aegis-architecture', 'aegis'],
                ['aegis', 'aegis-architecture'],
            ],
            'forbidden_downstream_substantive_execution': 0,
            'primary_substantive_result_emitted': False,
        }
        result = self._evaluate(case, trace)
        self.assertEqual('FAIL', result.verdict)
        self.assertIn('OWNERSHIP_LOOP', result.violations)


class RoutingCorpusV02Tests(unittest.TestCase):
    def test_v02_routing_cases_do_not_use_expected_skill(self):
        import json
        for name in ('direct-trigger.json', 'ambiguous-routing.json', 'upstream-blocker.json', 'compatibility.json'):
            cases = json.loads((ROOT/'skillset/routing'/name).read_text(encoding='utf-8'))
            for case in cases:
                with self.subTest(file=name, case=case.get('id')):
                    self.assertNotIn('expected_skill', case)
                    self.assertNotIn('expected_initial_skill', case)
                    self.assertNotIn('actual_first_skill', case)

    def test_handoff_corpus_separates_support_and_ownership_edges(self):
        import json
        handoffs = json.loads((ROOT/'skillset/routing/cross-skill-handoff.json').read_text(encoding='utf-8'))
        self.assertNotIn('valid', handoffs)
        self.assertIn('valid_support_returns', handoffs)
        self.assertIn('valid_ownership_handoffs', handoffs)
        self.assertIn('forbidden_primary_chains', handoffs)
        self.assertIn('forbidden_cycles', handoffs)

    def test_old_primary_handoffs_are_now_forbidden_primary_chains(self):
        import json
        handoffs = json.loads((ROOT/'skillset/routing/cross-skill-handoff.json').read_text(encoding='utf-8'))
        edges = {
            tuple(edge)
            for case in handoffs.get('forbidden_primary_chains', [])
            for edge in case.get('edges', [])
        }
        self.assertIn(('aegis-architecture', 'aegis-verification'), edges)
        self.assertIn(('aegis-verification', 'aegis-implementation'), edges)

    def test_composition_trace_regression_corpus_matches_oracle(self):
        import json
        path = ROOT/'skillset/routing/composition-traces.json'
        self.assertTrue(path.is_file(), 'composition trace regression corpus missing')
        from tools.aegis_skillset.model import load_skillset
        from tools.aegis_skillset.routing import evaluate_terminal_trace
        config = load_skillset(ROOT)
        fixtures = json.loads(path.read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(fixtures), 11)
        for fixture in fixtures:
            with self.subTest(case=fixture.get('id')):
                result = evaluate_terminal_trace(fixture['case'], fixture['trace'], config)
                self.assertEqual(fixture['expected_verdict'], result.verdict)
                for violation in fixture.get('expected_violations', []):
                    self.assertIn(violation, result.violations)
                for gap in fixture.get('expected_evidence_gaps', []):
                    self.assertIn(gap, result.evidence_gaps)


if __name__=='__main__': unittest.main()
