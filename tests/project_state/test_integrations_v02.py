import json
import tempfile
import unittest
from pathlib import Path

from tools.aegis_state.compute import compute_state, manifest_digest
from tools.aegis_state.model import load_manifests


def write_project(root: Path, *, integration_status="awaiting_integration", gate_verdict="PASS", integrated_revision=None):
    d = root / ".aegis"
    d.mkdir(parents=True)
    integration = {"id":"int1","kind":"pull_request","ref":"https://example/pr/1","gate_id":"G1","status":integration_status,"target_ref":"main","evidence_ids":["ev"]}
    if integrated_revision is not None:
        integration["integrated_revision"] = integrated_revision
    docs = {
        "project.json": {"schema_version":"0.2","project":{"id":"demo","name":"Demo","profile":"standard","lifecycle_hint":"implementation"}},
        "authorities.json": {"schema_version":"0.2","authorities":[{"id":"auth","scope":"runtime","kind":"system_architecture","version":"v1","status":"Current","ref":"docs/a.md","depends_on":[]}],"impact_reviews":[]},
        "gates.json": {"schema_version":"0.2","gates":[{"id":"G1","stage":"P34","verdict":gate_verdict,"validity":"current","authority_ids":["auth"],"evidence_ids":["ev"]}]},
        "evidence.json": {"schema_version":"0.2","evidence":[{"id":"ev","type":"ci","ref":"ci://g1","status":"available"}]},
        "integrations.json": {"schema_version":"0.2","integrations":[integration]},
    }
    for name, data in docs.items():
        (d / name).write_text(json.dumps(data), encoding="utf-8")


class IntegrationV02Tests(unittest.TestCase):
    def test_awaiting_integration_routes_to_finishing_handoff(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_project(root)
            state = compute_state(load_manifests(root))
            self.assertEqual(state.get("awaiting_integrations"), ["int1"])
            self.assertEqual(state.get("earliest_untrusted_layer"), "implementation")
            self.assertIsNone(state.get("recommended_next_stage"))
            self.assertEqual(state.get("recommended_handoff"), "superpowers:finishing-a-development-branch")

    def test_integrated_item_is_not_awaiting(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_project(root, integration_status="integrated", integrated_revision="abc123")
            state = compute_state(load_manifests(root))
            self.assertEqual(state.get("awaiting_integrations"), [])

    def test_blocked_gate_outranks_awaiting_integration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_project(root, gate_verdict="BLOCKED_ENVIRONMENT")
            state = compute_state(load_manifests(root))
            self.assertEqual(state.get("earliest_untrusted_layer"), "verification")
            self.assertEqual(state.get("recommended_next_stage"), "P34")

    def test_manifest_digest_changes_with_integration_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_project(root)
            m1 = load_manifests(root)
            d1 = manifest_digest(m1)
            p = root / ".aegis" / "integrations.json"
            data = json.loads(p.read_text())
            data["integrations"][0]["status"] = "closed_unmerged"
            p.write_text(json.dumps(data), encoding="utf-8")
            d2 = manifest_digest(load_manifests(root))
            self.assertNotEqual(d1, d2)


if __name__ == "__main__":
    unittest.main()
