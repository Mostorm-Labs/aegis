"""Reviewer-resolvable P20 V1-V14 evidence index for Project State v0.6."""
import unittest
import copy
import json
from pathlib import Path
from tools.aegis_state.model import load_manifests, validate_manifests
from tools.aegis_state.transition_v06 import validate_v06_transition
from tools.aegis_state.migrate_v06 import migrate_v05_to_v06

ROOT = Path(__file__).resolve().parents[2]

class P20EvidenceMapTests(unittest.TestCase):
    def test_v1_v14_evidence_surfaces_exist(self):
        self.assertTrue((ROOT / "tests/project_state/test_v06_binding.py").exists())
        self.assertTrue((ROOT / "examples/project-state/v0.6-minimal/.aegis/evidence.json").exists())
        self.assertTrue((ROOT / "examples/project-state/v0.6-minimal/.aegis/integrations.json").exists())
        self.assertTrue((ROOT / "skills/aegis-project-state/references/project-state.md").exists())
        self.assertTrue((ROOT / "skillset/skills/aegis-project-state/references/project-state.md").exists())

    def test_pr82_reviewer_refs_are_canonical(self):
        text = (ROOT / "examples/project-state/v0.6-minimal/.aegis/evidence.json").read_text()
        self.assertIn("#pullrequestreview-5122113780", text)
        self.assertIn("#issuecomment-5553423707", text)

    def test_v1_v2_binding_status_matrix(self):
        base = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        for kind, status, legal in (("bound", "awaiting_integration", True), ("absent", "awaiting_integration", False), ("bound", "integrated", True), ("absent", "integrated", True), ("absent", "closed_unmerged", False)):
            cur = copy.deepcopy(base); item = cur.integrations["integrations"][0]; item["status"] = status
            if status == "awaiting_integration": item.pop("integrated_revision", None)
            item["gate_decision_binding"] = ({"kind":"bound","gate_decision_id":"gate-eval-framework-pr1::decision::0001"} if kind == "bound" else {"kind":"absent","reason":"no_applicable_integration_gate_decision"})
            errors = validate_manifests(cur, strict_gate_validity=False)
            self.assertEqual(not errors, legal, (kind, status, errors))

    def test_v3_missing_lookup_never_becomes_absent(self):
        base = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        cur = copy.deepcopy(base); cur.evidence["evidence"][0]["status"] = "missing"
        self.assertTrue(any("uses unavailable evidence" in e for e in validate_manifests(cur, strict_gate_validity=True)))
        self.assertEqual(cur.integrations["integrations"][-1]["gate_decision_binding"]["kind"], "absent")

    def test_v7_migration_zero_inferred_absent(self):
        base = load_manifests(ROOT); migrated = migrate_v05_to_v06(base)
        self.assertEqual(sum(x["gate_decision_binding"]["kind"] == "absent" for x in migrated.integration_items), 0)

    def test_v11_v12_pr82_and_replay_conflict(self):
        base = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        refs = json.dumps(base.evidence)
        self.assertIn("3a2607220cd875dc66857b334dcfbd2c763e7c7d", json.dumps(base.integrations))
        self.assertIn("pullrequestreview-5122113780", refs)
        cur = copy.deepcopy(base); cur.integrations["integrations"][-1]["integrated_revision"] = "conflict"
        self.assertTrue(any("immutable field integrated_revision" in e for e in validate_v06_transition(base, cur)))

if __name__ == "__main__":
    unittest.main()
