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
        for kind, status, legal in (("bound", "awaiting_integration", True), ("absent", "awaiting_integration", False), ("bound", "integrated", True), ("absent", "integrated", True), ("bound", "closed_unmerged", True), ("absent", "closed_unmerged", False)):
            cur = copy.deepcopy(base); item = cur.integrations["integrations"][0]; item["status"] = status
            if status != "integrated": item.pop("integrated_revision", None)
            item["gate_decision_binding"] = ({"kind":"bound","gate_decision_id":"gate-eval-framework-pr1::decision::0001"} if kind == "bound" else {"kind":"absent","reason":"no_applicable_integration_gate_decision"})
            errors = validate_manifests(cur, strict_gate_validity=False)
            self.assertEqual(not errors, legal, (kind, status, errors))

    def test_v1_malformed_bindings_are_rejected(self):
        base = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        invalid = (({"kind": "unknown"}, "bound or absent"), ({"kind": "bound"}, "dangling gate decision"), ({"kind": "bound", "gate_decision_id": "missing"}, "dangling gate decision"), ({"kind": "bound", "gate_decision_id": "gate-eval-framework-pr1::decision::0001", "reason": "no_applicable_integration_gate_decision"}, "must not contain absent reason"), ({"kind": "absent"}, "canonical reason"), ({"kind": "absent", "reason": "unknown"}, "canonical reason"), ({"kind": "absent", "reason": "no_applicable_integration_gate_decision", "gate_decision_id": "gate-eval-framework-pr1::decision::0001"}, "must not contain gate_decision_id"), (None, "bound or absent"))
        for binding, needle in invalid:
            cur = copy.deepcopy(base); cur.integrations["integrations"][0]["gate_decision_binding"] = binding
            errors = validate_manifests(cur, strict_gate_validity=False)
            self.assertTrue(any(needle in e for e in errors), (binding, errors))
        cur = copy.deepcopy(base)
        cur.integrations["integrations"][0]["gate_decision_id"] = "gate-eval-framework-pr1::decision::0001"
        self.assertTrue(any("legacy gate_decision_id is forbidden" in e for e in validate_manifests(cur, strict_gate_validity=False)))

    def test_v6_later_pass_preserves_historical_blocked_binding(self):
        previous = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        current = copy.deepcopy(previous)
        current.gates["decisions"].append({"id": "gate-skill-decomposition-v02-pr9::decision::0003", "gate_id": "gate-skill-decomposition-v02-pr9", "verdict": "PASS", "evidence_ids": ["ev-pr9-task6-p34-accepted"], "supersedes": "gate-skill-decomposition-v02-pr9::decision::0002"})
        blocked = next(x for x in previous.integrations["integrations"] if x["id"] == "int-pr9")
        self.assertEqual(blocked["gate_decision_binding"]["gate_decision_id"], "gate-skill-decomposition-v02-pr9::decision::0001")
        self.assertEqual(validate_v06_transition(previous, current), [])

    def test_v3_missing_lookup_never_becomes_absent(self):
        base = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        cur = copy.deepcopy(base); cur.evidence["evidence"][0]["status"] = "missing"
        self.assertTrue(any("uses unavailable evidence" in e for e in validate_manifests(cur, strict_gate_validity=True)))
        self.assertEqual(cur.integrations["integrations"][-1]["gate_decision_binding"]["kind"], "absent")

    def test_v7_migration_zero_inferred_absent(self):
        base = load_manifests(ROOT / "examples/project-state/v0.5-minimal"); migrated = migrate_v05_to_v06(base)
        self.assertEqual(sum(x["gate_decision_binding"]["kind"] == "absent" for x in migrated.integration_items), 0)

    def test_v11_v12_pr82_and_replay_conflict(self):
        base = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        refs = json.dumps(base.evidence)
        self.assertIn("3a2607220cd875dc66857b334dcfbd2c763e7c7d", json.dumps(base.integrations))
        self.assertIn("pullrequestreview-5122113780", refs)
        cur = copy.deepcopy(base); cur.integrations["integrations"][-1]["integrated_revision"] = "conflict"
        self.assertTrue(any("immutable field integrated_revision" in e for e in validate_v06_transition(base, cur)))

    def test_v8_o1_o6_semantic_transition_representatives(self):
        base = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        template = copy.deepcopy(base.integrations["integrations"][0])
        template["id"] = "int-o"
        template["ref"] = "https://example/o"
        template.pop("integrated_revision", None)
        template["status"] = "awaiting_integration"
        for target_status in ("awaiting_integration", "closed_unmerged", "integrated"):
            current = copy.deepcopy(base)
            item = copy.deepcopy(template); item["status"] = target_status
            if target_status == "integrated": item["integrated_revision"] = "abc123"
            current.integrations["integrations"].append(item)
            self.assertEqual(validate_manifests(current, strict_gate_validity=False), [], target_status)
            self.assertEqual(validate_v06_transition(base, current), [], target_status)
        self.assertEqual(validate_v06_transition(base, copy.deepcopy(base)), [])

    def test_v11_pr82_forbidden_variants_fail_closed(self):
        base = load_manifests(ROOT / "examples/project-state/v0.6-minimal")
        index = next(i for i, x in enumerate(base.integrations["integrations"]) if x["id"] == "int-pr82")
        omitted = copy.deepcopy(base); omitted.integrations["integrations"][index].pop("gate_decision_binding")
        self.assertTrue(validate_manifests(omitted, strict_gate_validity=False))
        retroactive = copy.deepcopy(base); retroactive.integrations["integrations"][index]["gate_decision_binding"] = {"kind": "bound", "gate_decision_id": "gate-control-plane-v02-release-pr66::decision::0001"}
        self.assertTrue(any("immutable field gate_decision_binding" in e for e in validate_v06_transition(base, retroactive)))
        lookup_failure = copy.deepcopy(base); lookup_failure.integrations["integrations"][0]["gate_decision_binding"]["gate_decision_id"] = "missing"
        self.assertTrue(any("dangling gate decision" in e for e in validate_manifests(lookup_failure, strict_gate_validity=False)))

if __name__ == "__main__":
    unittest.main()
