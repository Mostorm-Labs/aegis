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


if __name__ == '__main__':
    unittest.main()
