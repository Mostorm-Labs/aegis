import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.aegis_state.migrate_v06 import migrate_v05_to_v06
from tools.aegis_state.model import load_manifests, validate_manifests
from tools.aegis_state.transition_v06 import validate_v06_transition
from tools.aegis_state.compute import compute_state


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

    def test_v06_current_blocked_decision_remains_actionable(self):
        manifests = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        state = compute_state(manifests)
        self.assertIn("gate-openai-real-baseline::decision::0001", [x["decision_id"] for x in state["current_gate_decisions"]])
        self.assertIn("gate-openai-real-baseline", state["blocking_gates"])
        self.assertIn("gate-openai-real-baseline::decision::0001", state["blocking_gate_decisions"])

    def test_v05_to_v06_transition_preserves_immutable_history(self):
        previous = load_manifests(ROOT / "examples/project-state/v0.5-minimal")
        current = migrate_v05_to_v06(previous)
        self.assertEqual(validate_v06_transition(previous, current), [])

    def test_v06_transition_rejects_gate_and_decision_rewrites(self):
        previous = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        current = copy.deepcopy(previous)
        current.gates["gates"][0]["stage"] = "P21"
        current.gates["decisions"][0]["verdict"] = "BLOCKED_EVIDENCE"
        errors = validate_v06_transition(previous, current)
        self.assertTrue(any("immutable gate contract" in e for e in errors))
        self.assertTrue(any("immutable gate decision" in e for e in errors))

    def test_missing_or_failed_evidence_is_not_absent(self):
        manifests = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        current = copy.deepcopy(manifests)
        for evidence in current.evidence["evidence"]:
            if evidence["id"] == "ev-pr82-occurrence-basis":
                evidence["status"] = "missing"
        errors = validate_manifests(current, strict_gate_validity=True)
        self.assertTrue(any("uses unavailable evidence" in e for e in errors))
        self.assertEqual(current.integrations["integrations"][0]["gate_decision_binding"]["kind"], "bound")
        self.assertEqual(current.integrations["integrations"][-1]["gate_decision_binding"]["kind"], "absent")

    def test_later_pass_does_not_rewrite_historical_absent_binding(self):
        previous = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        current = copy.deepcopy(previous)
        current.gates["decisions"].append({
            "id": "gate-project-state-v02-pr7::decision::0002",
            "gate_id": "gate-project-state-v02-pr7",
            "verdict": "PASS",
            "evidence_ids": ["ev-pr7-p34"],
            "supersedes": "gate-project-state-v02-pr7::decision::0001",
        })
        self.assertEqual(previous.integrations["integrations"][-1]["gate_decision_binding"]["kind"], "absent")
        self.assertEqual(current.integrations["integrations"][-1]["gate_decision_binding"]["kind"], "absent")
        self.assertEqual(validate_v06_transition(previous, current), [])


if __name__ == "__main__":
    unittest.main()
