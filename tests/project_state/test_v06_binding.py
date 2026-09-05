import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.aegis_state.migrate_v06 import migrate_v05_to_v06
from tools.aegis_state.model import load_manifests, validate_manifests
from tools.aegis_state.transition_v06 import validate_v06_transition


ROOT = Path(__file__).resolve().parents[2]


class V06BindingTests(unittest.TestCase):
    def test_minimal_fixture_validates_and_preserves_absent_or_bound(self):
        manifests = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        self.assertEqual(manifests.schema_version, "0.6")
        self.assertEqual(validate_manifests(manifests), [])
        for item in manifests.integration_items:
            binding = item["gate_decision_binding"]
            self.assertIn(binding["kind"], {"bound", "absent"})

    def test_v05_migration_is_lossless_bound_and_never_infers_absent(self):
        source = load_manifests(ROOT)
        migrated = migrate_v05_to_v06(source)
        self.assertEqual(migrated.schema_version, "0.6")
        self.assertTrue(all(x["gate_decision_binding"]["kind"] == "bound" for x in migrated.integration_items))
        self.assertEqual([x["id"] for x in migrated.integration_items], [x["id"] for x in source.integration_items])

    def test_integrated_binding_identity_is_immutable(self):
        previous = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        current = copy.deepcopy(previous)
        current.integrations["integrations"][0]["gate_decision_binding"] = {"kind": "absent", "reason": "no_applicable_integration_gate_decision"}
        self.assertTrue(any("immutable field gate_decision_binding" in e for e in validate_v06_transition(previous, current)))


if __name__ == "__main__":
    unittest.main()
