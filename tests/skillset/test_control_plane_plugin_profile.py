import json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class ControlPlanePluginProfileTests(unittest.TestCase):
    def test_native_plugin_is_exact_nine(self):
        manifest=json.loads((ROOT/'plugins/aegis/.codex-plugin/plugin.json').read_text())
        skills=sorted((ROOT/'plugins/aegis/skills').iterdir())
        self.assertEqual(9,len(skills)); self.assertEqual('aegis',manifest['name'])
        self.assertFalse(any(p.name == 'aegis-plugin' for p in skills))
    def test_gate_and_rollout_boundaries_are_preserved(self):
        text=(ROOT/'docs/execution-surface-contract-v0.2.md').read_text()
        self.assertIn('CONTROL_REVIEW',text)
        routing=(ROOT/'tools/aegis_control/openapi.py').read_text()
        self.assertIn('DENIED',routing)

if __name__=='__main__': unittest.main()
