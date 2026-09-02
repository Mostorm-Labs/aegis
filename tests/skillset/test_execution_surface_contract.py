import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ExecutionSurfaceContractTests(unittest.TestCase):
    def _read(self, path):
        return (ROOT / path).read_text(encoding='utf-8')

    def test_shared_handoff_contract_defines_surface_handoff(self):
        text = self._read('skillset/shared/handoff-contract.md')
        for required in ('surface_handoff', 'Surface Handoff != Ownership Handoff', 'stage_owner', 'from_surface', 'to_surface', 'package_ref'):
            self.assertIn(required, text)
        self.assertIn('does not transfer ownership', text.lower())

    def test_codex_surface_handoff_requires_standard_execution_prefix(self):
        prefix = (
            '请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，'
            '按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；'
            '若状态冲突则 fail closed。'
        )
        handoff = self._read('skillset/shared/handoff-contract.md')
        implementation = self._read('skillset/skills/aegis-implementation/SKILL.md')
        authority = self._read('docs/execution-surface-contract-v0.2.md')
        for text in (handoff, implementation, authority):
            self.assertIn(prefix, text)
        self.assertIn('preferred_executor: codex', handoff)

    def test_implementation_skill_routes_planning_and_code_surfaces(self):
        text = self._read('skillset/skills/aegis-implementation/SKILL.md')
        for required in ('CONTROL_REASONING', 'CODE_EXECUTION', 'P30', 'P31', 'P32', 'P33', 'package_ref'):
            self.assertIn(required, text)
        self.assertIn('surface handoff', text.lower())
        self.assertIn('does not transfer', text.lower())

    def test_gate_review_skill_routes_review_and_reverification_surfaces(self):
        text = self._read('skillset/skills/aegis-gate-review/SKILL.md')
        for required in ('CONTROL_REVIEW', 'CODE_REVERIFY', 'P34', 'P35', 'P36'):
            self.assertIn(required, text)
        self.assertIn('after', text.lower())
        self.assertIn('classif', text.lower())

    def test_shared_handoff_requires_materialized_review_evidence(self):
        text = self._read('skillset/shared/handoff-contract.md')
        self.assertIn('materialized_ref', text)
        self.assertIn('reviewer-accessible', text.lower())
        self.assertIn('local-only', text.lower())

    def test_implementation_requires_materialization_before_control_review(self):
        text = self._read('skillset/skills/aegis-implementation/SKILL.md')
        self.assertIn('materialized_ref', text)
        self.assertIn('reviewer-accessible', text.lower())
        self.assertIn('local-only', text.lower())
        self.assertIn('CONTROL_REVIEW', text)

    def test_authority_requires_evidence_materialization_boundary(self):
        text = self._read('docs/execution-surface-contract-v0.1.md')
        self.assertIn('materialized_ref', text)
        self.assertIn('reviewer-accessible', text.lower())
        self.assertIn('local-only', text.lower())
        self.assertIn('BLOCKED_EVIDENCE', text)

    def test_gate_review_resolves_materialized_ref_before_executor_claim(self):
        text = self._read('skillset/skills/aegis-gate-review/SKILL.md')
        self.assertIn('materialized_ref', text)
        self.assertIn('reviewer-accessible', text.lower())
        self.assertIn('before', text.lower())
        self.assertIn('agent claims are not evidence', text.lower())


if __name__ == '__main__':
    unittest.main()
