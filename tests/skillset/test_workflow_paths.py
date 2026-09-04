import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/skillset.yml'
REQUIRED_V02_PATHS = (
    'docs/skill-decomposition-v0.2.md',
    'docs/skill-decomposition-dogfood-v0.2.md',
    'docs/superpowers/specs/*multi-skill-composition*.md',
    'docs/superpowers/plans/*multi-skill-composition*.md',
)
EXACT_EVIDENCE_EXPR = '${{ github.event.pull_request.head.sha || github.sha }}'


class SkillsetWorkflowPathTests(unittest.TestCase):
    def _event_paths(self, event: str) -> str:
        text = WORKFLOW.read_text(encoding='utf-8')
        if event == 'push':
            match = re.search(r'(?ms)^  push:\n    paths:\n(?P<body>.*?)(?=^  pull_request:)', text)
        else:
            match = re.search(r'(?ms)^  pull_request:\n    paths:\n(?P<body>.*?)(?=^\nconcurrency:)', text)
        self.assertIsNotNone(match, f'{event} paths block missing')
        return match.group('body')

    def test_push_paths_cover_v02_composition_authority(self):
        paths = self._event_paths('push')
        for required in REQUIRED_V02_PATHS:
            with self.subTest(path=required):
                self.assertIn(f'"{required}"', paths)

    def test_pull_request_paths_cover_v02_composition_authority(self):
        paths = self._event_paths('pull_request')
        for required in REQUIRED_V02_PATHS:
            with self.subTest(path=required):
                self.assertIn(f'"{required}"', paths)

    def test_workflow_builds_and_uploads_plugin_distribution(self):
        workflow = WORKFLOW.read_text(encoding='utf-8')
        required = (
            'python3 -m tools.aegis_skillset.cli distribution-check .',
            'python3 scripts/build_aegis_distributions.py --check',
            'python3 scripts/build_aegis_distributions.py --package-dir /tmp/aegis-plugin-dist',
            'actions/upload-artifact@v4',
            'name: aegis-distributions-0.1.0-task6.1',
        )
        for needle in required:
            with self.subTest(needle=needle):
                self.assertIn(needle, workflow)

    def test_workflow_uploads_user_facing_nine_skill_installation_kit(self):
        workflow = WORKFLOW.read_text(encoding='utf-8')
        required = (
            'name: Upload Aegis Skill installation kit',
            'name: aegis-skill-installation-kit-0.1.0-task6.1',
            'path: /tmp/aegis-plugin-dist/aegis-skills-0.1.0-task6.1/',
            'if-no-files-found: error',
        )
        for needle in required:
            with self.subTest(needle=needle):
                self.assertIn(needle, workflow)

    def test_workflow_uses_published_history_and_exact_head_candidate_parity(self):
        workflow = WORKFLOW.read_text(encoding='utf-8')
        for needle in (
            'scripts/build_aegis_distributions.py --published-history --version 0.1.0-beta.3 --check',
            'scripts/build_openai_plugin_materialization.py --published-history --release-version 0.1.0-beta.3 --check',
            f'AEGIS_EVIDENCE_REVISION: {EXACT_EVIDENCE_EXPR}',
            f'ref: {EXACT_EVIDENCE_EXPR}',
            'run: test "$(git rev-parse HEAD)" = "$AEGIS_EVIDENCE_REVISION"',
            'scripts/build_candidate_plugin_parity.py --output /tmp/aegis-candidate-plugin-parity.json',
            f'name: aegis-candidate-plugin-parity-{EXACT_EVIDENCE_EXPR}',
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, workflow)
        self.assertNotIn('name: aegis-candidate-plugin-parity-${{ github.sha }}', workflow)
        self.assertNotIn('aegis-skill-installation-kit-0.1.0-beta.3-candidate', workflow)


if __name__ == '__main__':
    unittest.main()
