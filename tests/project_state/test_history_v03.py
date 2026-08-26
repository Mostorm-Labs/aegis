import json
import tempfile
import unittest
from pathlib import Path

from tools.aegis_state.compute import compute_state
from tools.aegis_state.model import load_manifests, validate_manifests


def write_scenario(root: Path, *, authorities, gate, integration, evidence_status="available"):
    docs = {
        "project.json": {"schema_version":"0.3","project":{"id":"demo","name":"Demo","profile":"standard","lifecycle_hint":"implementation"}},
        "authorities.json": {"schema_version":"0.3","authorities":authorities,"impact_reviews":[]},
        "gates.json": {"schema_version":"0.3","gates":[gate]},
        "evidence.json": {"schema_version":"0.3","evidence":[{"id":"ev","type":"ci","ref":"ci://history","status":evidence_status}]},
        "integrations.json": {"schema_version":"0.3","integrations":[integration]},
    }
    aegis = root / ".aegis"
    aegis.mkdir(parents=True)
    for name, data in docs.items():
        (aegis / name).write_text(json.dumps(data), encoding="utf-8")


def auth(aid, status, scope="runtime", kind="system_architecture"):
    return {"id":aid,"scope":scope,"kind":kind,"version":"v1","status":status,"ref":f"docs/{aid}.md","depends_on":[]}


def gate(gid, verdict, authority_ids, *, validity="current"):
    return {"id":gid,"stage":"P34","verdict":verdict,"validity":validity,"authority_ids":authority_ids,"evidence_ids":["ev"]}


def integration(iid, gid, status, revision=None):
    item = {"id":iid,"kind":"pull_request","ref":f"https://example/{iid}","gate_id":gid,"status":status,"target_ref":"main","evidence_ids":["ev"]}
    if revision is not None:
        item["integrated_revision"] = revision
    return item


class HistoryV03Tests(unittest.TestCase):
    def test_integrated_survives_all_authority_supersession(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, authorities=[auth("auth-old", "Superseded")], gate=gate("G-old", "PASS", ["auth-old"]), integration=integration("int-old", "G-old", "integrated", "abc123"))
            manifests = load_manifests(root)
            self.assertEqual(validate_manifests(manifests), [])
            state = compute_state(manifests)
            self.assertIn({"integration_id":"int-old","applicability":"historical"}, state["integration_applicability"])
            self.assertIn("G-old", state["historical_gates"])
            self.assertNotIn("G-old", state["stale_gates"])

    def test_historical_blocked_gate_cannot_support_integrated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, authorities=[auth("auth-old", "Superseded")], gate=gate("G-old", "BLOCKED_IMPLEMENTATION", ["auth-old"]), integration=integration("int-old", "G-old", "integrated", "abc123"))
            errors = validate_manifests(load_manifests(root))
            self.assertTrue(any("PASS/PASS_WITH_FINDINGS" in e for e in errors), errors)

    def test_awaiting_still_rejects_noncurrent_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, authorities=[auth("auth-old", "Superseded")], gate=gate("G-old", "PASS", ["auth-old"]), integration=integration("int-old", "G-old", "awaiting_integration"))
            errors = validate_manifests(load_manifests(root))
            self.assertTrue(any("current" in e for e in errors), errors)

    def test_historical_gate_is_non_actionable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, authorities=[auth("auth-old", "Superseded")], gate=gate("G-old", "PASS", ["auth-old"]), integration=integration("int-old", "G-old", "closed_unmerged"))
            state = compute_state(load_manifests(root))
            self.assertIn("G-old", state["historical_gates"])
            self.assertNotIn("G-old", state["stale_gates"])
            self.assertIsNone(state["earliest_untrusted_layer"])

    def test_current_stale_gate_remains_actionable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, authorities=[auth("auth-current", "Current")], gate=gate("G-current", "PASS", ["auth-current"]), integration=integration("int-current", "G-current", "closed_unmerged"), evidence_status="missing")
            state = compute_state(load_manifests(root))
            self.assertIn("G-current", state["stale_gates"])
            self.assertEqual(state["earliest_untrusted_layer"], "verification")
            self.assertEqual(state["recommended_next_stage"], "P34")

    def test_mixed_authority_gate_routes_p21(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, authorities=[auth("auth-current", "Current"), auth("auth-old", "Superseded", scope="runtime-old")], gate=gate("G-mixed", "PASS", ["auth-current", "auth-old"]), integration=integration("int-mixed", "G-mixed", "integrated", "abc123"))
            state = compute_state(load_manifests(root))
            self.assertIn("G-mixed", state["needs_review_gates"])
            self.assertEqual(state["earliest_untrusted_layer"], "authority")
            self.assertEqual(state["recommended_next_stage"], "P21")

    def test_integrated_requires_available_occurrence_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, authorities=[auth("auth-current", "Current")], gate=gate("G-current", "PASS", ["auth-current"]), integration=integration("int-current", "G-current", "integrated", "abc123"), evidence_status="missing")
            errors = validate_manifests(load_manifests(root))
            self.assertTrue(any("unavailable evidence" in e for e in errors), errors)

    def test_closed_unmerged_is_completed_history_even_under_current_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, authorities=[auth("auth-current", "Current")], gate=gate("G-current", "PASS", ["auth-current"]), integration=integration("int-closed", "G-current", "closed_unmerged"))
            state = compute_state(load_manifests(root))
            self.assertIn({"integration_id":"int-closed","applicability":"historical"}, state["integration_applicability"])
            self.assertNotIn("int-closed", state["awaiting_integrations"])

    def test_historical_blocked_gate_does_not_reactivate_current_blocker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_scenario(root, authorities=[auth("auth-old", "Superseded")], gate=gate("G-old", "BLOCKED_ENVIRONMENT", ["auth-old"]), integration=integration("int-old", "G-old", "closed_unmerged"))
            state = compute_state(load_manifests(root))
            self.assertNotIn("G-old", state["blocking_gates"])
            self.assertIsNone(state["earliest_untrusted_layer"])


if __name__ == "__main__":
    unittest.main()
