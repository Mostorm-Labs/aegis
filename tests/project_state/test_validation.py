import tempfile
import unittest
from pathlib import Path

from tests.project_state.helpers import manifests, write_project
from tools.aegis_state.model import load_manifests, validate_manifests


class ValidationTests(unittest.TestCase):
    def validate(self, authorities=None, gates=None, evidence=None):
        with tempfile.TemporaryDirectory() as td:
            project, base_auth, base_gates, base_ev = manifests()
            write_project(Path(td), project, authorities or base_auth, gates or base_gates, evidence or base_ev)
            return validate_manifests(load_manifests(Path(td)))

    def test_duplicate_current_scope_kind_is_rejected(self):
        _, authorities, _, _ = manifests()
        authorities["authorities"].append({"id":"arch-v2","scope":"runtime","kind":"system_architecture","version":"v2","status":"Current","ref":"docs/arch-v2.md","depends_on":[]})
        errors = self.validate(authorities=authorities)
        self.assertTrue(any("multiple Current authorities" in e for e in errors), errors)

    def test_dangling_authority_dependency_is_rejected(self):
        _, authorities, _, _ = manifests()
        authorities["authorities"][1]["depends_on"] = ["missing"]
        errors = self.validate(authorities=authorities)
        self.assertTrue(any("dangling authority dependency" in e for e in errors), errors)

    def test_dependency_cycle_is_rejected(self):
        _, authorities, _, _ = manifests()
        authorities["authorities"][0]["depends_on"] = ["arch-v1"]
        errors = self.validate(authorities=authorities)
        self.assertTrue(any("authority dependency cycle" in e for e in errors), errors)

    def test_supersession_cycle_is_rejected(self):
        _, authorities, _, _ = manifests()
        authorities["authorities"][0]["status"] = "Superseded"
        authorities["authorities"][0]["supersedes"] = "arch-v1"
        authorities["authorities"][1]["status"] = "Superseded"
        authorities["authorities"][1]["supersedes"] = "schema-v1"
        errors = self.validate(authorities=authorities)
        self.assertTrue(any("supersession cycle" in e for e in errors), errors)

    def test_pass_gate_without_evidence_is_rejected(self):
        _, _, gates, _ = manifests()
        gates["gates"][0]["evidence_ids"] = []
        errors = self.validate(gates=gates)
        self.assertTrue(any("PASS gate G1 requires evidence" in e for e in errors), errors)

    def test_current_pass_gate_on_superseded_authority_is_rejected(self):
        _, authorities, _, _ = manifests()
        authorities["authorities"][1]["status"] = "Superseded"
        errors = self.validate(authorities=authorities)
        self.assertTrue(any("current PASS gate G1 depends on non-current authority" in e for e in errors), errors)

    def test_current_pass_gate_on_unavailable_evidence_is_rejected(self):
        _, _, _, evidence = manifests()
        evidence["evidence"][0]["status"] = "missing"
        errors = self.validate(evidence=evidence)
        self.assertTrue(any("current PASS gate G1 uses unavailable evidence" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
