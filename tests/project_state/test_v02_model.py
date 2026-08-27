import json
import tempfile
import unittest
from pathlib import Path

from tools.aegis_state.model import load_manifests, validate_manifests


def write_v02(root: Path, integrations):
    d = root / ".aegis"
    d.mkdir(parents=True)
    docs = {
        "project.json": {"schema_version":"0.3","project":{"id":"demo","name":"Demo","profile":"standard"}},
        "authorities.json": {"schema_version":"0.3","authorities":[{"id":"auth","scope":"runtime","kind":"system_architecture","version":"v1","status":"Current","ref":"docs/a.md","depends_on":[]}],"impact_reviews":[]},
        "gates.json": {"schema_version":"0.3","gates":[{"id":"G1","stage":"P34","verdict":"PASS","validity":"current","authority_ids":["auth"],"evidence_ids":["ev"]}]},
        "evidence.json": {"schema_version":"0.3","evidence":[{"id":"ev","type":"ci","ref":"ci://g1","status":"available"}]},
        "integrations.json": {"schema_version":"0.3","integrations":integrations},
    }
    for name, data in docs.items():
        (d / name).write_text(json.dumps(data), encoding="utf-8")


class V02ModelTests(unittest.TestCase):
    def test_v02_loader_exposes_integrations_and_validates(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_v02(root, [{"id":"int1","kind":"pull_request","ref":"https://example/pr/1","gate_id":"G1","status":"awaiting_integration","target_ref":"main","evidence_ids":["ev"]}])
            manifests = load_manifests(root)
            self.assertTrue(hasattr(manifests, "integration_items"))
            self.assertEqual(validate_manifests(manifests), [])

    def test_integrated_requires_revision(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_v02(root, [{"id":"int1","kind":"pull_request","ref":"https://example/pr/1","gate_id":"G1","status":"integrated","target_ref":"main","evidence_ids":["ev"]}])
            errors = validate_manifests(load_manifests(root))
            self.assertTrue(any("integrated_revision" in e for e in errors), errors)


class V02IntegrationValidationTests(unittest.TestCase):
    def _errors(self, integrations, *, gate_verdict="PASS", evidence_status="available"):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_v02(root, integrations)
            gates_path = root / ".aegis" / "gates.json"
            gates = json.loads(gates_path.read_text())
            gates["gates"][0]["verdict"] = gate_verdict
            gates_path.write_text(json.dumps(gates), encoding="utf-8")
            evidence_path = root / ".aegis" / "evidence.json"
            evidence = json.loads(evidence_path.read_text())
            evidence["evidence"][0]["status"] = evidence_status
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            return validate_manifests(load_manifests(root))

    def test_duplicate_integration_id_is_rejected(self):
        item = {"id":"int1","kind":"pull_request","ref":"https://example/pr/1","gate_id":"G1","status":"awaiting_integration","target_ref":"main","evidence_ids":["ev"]}
        errors = self._errors([item, dict(item)])
        self.assertTrue(any("duplicate integration id" in e for e in errors), errors)

    def test_dangling_integration_gate_is_rejected(self):
        item = {"id":"int1","kind":"pull_request","ref":"https://example/pr/1","gate_id":"missing","status":"awaiting_integration","target_ref":"main","evidence_ids":["ev"]}
        errors = self._errors([item])
        self.assertTrue(any("dangling gate id" in e for e in errors), errors)

    def test_dangling_integration_evidence_is_rejected(self):
        item = {"id":"int1","kind":"pull_request","ref":"https://example/pr/1","gate_id":"G1","status":"awaiting_integration","target_ref":"main","evidence_ids":["missing"]}
        errors = self._errors([item])
        self.assertTrue(any("dangling evidence id" in e for e in errors), errors)

    def test_awaiting_integration_rejects_blocked_gate(self):
        item = {"id":"int1","kind":"pull_request","ref":"https://example/pr/1","gate_id":"G1","status":"awaiting_integration","target_ref":"main","evidence_ids":["ev"]}
        errors = self._errors([item], gate_verdict="BLOCKED_IMPLEMENTATION")
        self.assertTrue(any("requires PASS/PASS_WITH_FINDINGS" in e for e in errors), errors)

    def test_integration_rejects_unavailable_evidence(self):
        item = {"id":"int1","kind":"pull_request","ref":"https://example/pr/1","gate_id":"G1","status":"awaiting_integration","target_ref":"main","evidence_ids":["ev"]}
        errors = self._errors([item], evidence_status="missing")
        self.assertTrue(any("uses unavailable evidence" in e for e in errors), errors)


class V02EffectiveGateValidityTests(unittest.TestCase):
    def test_awaiting_integration_rejects_gate_with_computed_stale_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            item = {"id":"int1","kind":"pull_request","ref":"https://example/pr/1","gate_id":"G1","status":"awaiting_integration","target_ref":"main","evidence_ids":["ev"]}
            write_v02(root, [item])
            auth_path = root / ".aegis" / "authorities.json"
            authorities = json.loads(auth_path.read_text())
            authorities["authorities"] = [
                {"id":"schema-v1","scope":"document","kind":"semantic_schema","version":"v1","status":"Superseded","ref":"docs/schema-v1.md","depends_on":[]},
                {"id":"schema-v2","scope":"document","kind":"semantic_schema","version":"v2","status":"Current","ref":"docs/schema-v2.md","depends_on":[],"supersedes":"schema-v1","change_class":"breaking"},
                {"id":"auth","scope":"runtime","kind":"system_architecture","version":"v1","status":"Current","ref":"docs/a.md","depends_on":["schema-v1"]},
            ]
            auth_path.write_text(json.dumps(authorities), encoding="utf-8")
            errors = validate_manifests(load_manifests(root))
            self.assertTrue(any("requires current-valid gate G1" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
