import json
import tempfile
import unittest
from pathlib import Path

from tools.aegis_state.compute import compute_state
from tools.aegis_state.model import load_manifests, validate_manifests


def write_scenario(root: Path, *, schema_version="0.4", gate_verdict="BLOCKED_EVIDENCE", integration_status="integrated"):
    aegis = root / ".aegis"
    aegis.mkdir(parents=True)
    integration = {
        "id": "int1",
        "kind": "pull_request",
        "ref": "https://example/pr/1",
        "gate_id": "G1",
        "status": integration_status,
        "target_ref": "main",
        "evidence_ids": ["ev-occurrence"],
    }
    if integration_status == "integrated":
        integration["integrated_revision"] = "abc123"

    docs = {
        "project.json": {
            "schema_version": schema_version,
            "project": {"id": "demo", "name": "Demo", "profile": "standard", "lifecycle_hint": "verification"},
        },
        "authorities.json": {
            "schema_version": schema_version,
            "authorities": [
                {"id": "auth", "scope": "runtime", "kind": "system_architecture", "version": "v1", "status": "Current", "ref": "docs/a.md", "depends_on": []}
            ],
            "impact_reviews": [],
        },
        "gates.json": {
            "schema_version": schema_version,
            "gates": [
                {"id": "G1", "stage": "P34", "verdict": gate_verdict, "validity": "current", "authority_ids": ["auth"], "evidence_ids": ["ev-gate"]}
            ],
        },
        "evidence.json": {
            "schema_version": schema_version,
            "evidence": [
                {"id": "ev-gate", "type": "gate_evidence", "ref": "ci://gate", "status": "available"},
                {"id": "ev-occurrence", "type": "repository_integration", "ref": "git://abc123", "status": "available"},
            ],
        },
        "integrations.json": {"schema_version": schema_version, "integrations": [integration]},
    }
    for name, data in docs.items():
        (aegis / name).write_text(json.dumps(data), encoding="utf-8")


class OutOfGateIntegrationV04Tests(unittest.TestCase):
    def test_v04_records_blocked_gate_integration_as_nonconforming_without_clearing_blocker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root)
            manifests = load_manifests(root)
            self.assertEqual([], validate_manifests(manifests))

            state = compute_state(manifests)
            self.assertEqual("0.4", state["schema_version"])
            self.assertIn({"integration_id": "int1", "conformance": "nonconforming"}, state["integration_conformance"])
            self.assertEqual(["int1"], state["nonconforming_integrations"])
            self.assertIn("G1", state["blocking_gates"])
            self.assertIn({"integration_id": "int1", "applicability": "current"}, state["integration_applicability"])
            self.assertEqual("verification", state["earliest_untrusted_layer"])
            self.assertEqual("P34", state["recommended_next_stage"])

    def test_v04_pass_backed_integration_is_conforming(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, gate_verdict="PASS")
            manifests = load_manifests(root)
            self.assertEqual([], validate_manifests(manifests))
            state = compute_state(manifests)
            self.assertIn({"integration_id": "int1", "conformance": "conforming"}, state["integration_conformance"])
            self.assertEqual([], state["nonconforming_integrations"])

    def test_v03_preserves_old_rule_and_rejects_blocked_gate_integration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, schema_version="0.3")
            errors = validate_manifests(load_manifests(root))
            self.assertTrue(any("PASS/PASS_WITH_FINDINGS" in error for error in errors), errors)

    def test_v04_awaiting_integration_still_requires_gate_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, integration_status="awaiting_integration")
            errors = validate_manifests(load_manifests(root))
            self.assertTrue(any("requires PASS/PASS_WITH_FINDINGS" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
