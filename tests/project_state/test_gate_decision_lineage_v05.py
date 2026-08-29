import json
import tempfile
import unittest
from pathlib import Path

from tools.aegis_state.compute import compute_state
from tools.aegis_state.model import load_manifests, validate_manifests


D1 = "G1::decision::0001"
D2 = "G1::decision::0002"


def decision(decision_id, verdict, *, gate_id="G1", evidence_ids=None, supersedes=None):
    item = {
        "id": decision_id,
        "gate_id": gate_id,
        "verdict": verdict,
        "evidence_ids": list(evidence_ids or ["ev-block"]),
    }
    if supersedes is not None:
        item["supersedes"] = supersedes
    return item


def write_v05(
    root: Path,
    *,
    decisions=None,
    integrations=None,
    gates=None,
    evidence=None,
):
    aegis = root / ".aegis"
    aegis.mkdir(parents=True)
    decisions = list(decisions or [decision(D1, "BLOCKED_EVIDENCE")])
    gates = list(
        gates
        or [
            {
                "id": "G1",
                "stage": "P34",
                "authority_ids": ["auth"],
            }
        ]
    )
    evidence = list(
        evidence
        or [
            {"id": "ev-block", "type": "gate_review", "ref": "gate://blocked", "status": "available"},
            {"id": "ev-pass", "type": "gate_review", "ref": "gate://pass", "status": "available"},
            {"id": "ev-occurrence", "type": "repository_integration", "ref": "git://abc123", "status": "available"},
        ]
    )
    if integrations is None:
        integrations = [
            {
                "id": "int1",
                "kind": "pull_request",
                "ref": "https://example/pr/1",
                "gate_decision_id": D1,
                "status": "integrated",
                "target_ref": "main",
                "evidence_ids": ["ev-occurrence"],
                "integrated_revision": "abc123",
            }
        ]

    docs = {
        "project.json": {
            "schema_version": "0.5",
            "project": {"id": "demo", "name": "Demo", "profile": "standard", "lifecycle_hint": "verification"},
        },
        "authorities.json": {
            "schema_version": "0.5",
            "authorities": [
                {
                    "id": "auth",
                    "scope": "runtime",
                    "kind": "system_architecture",
                    "version": "v1",
                    "status": "Current",
                    "ref": "docs/a.md",
                    "depends_on": [],
                }
            ],
            "impact_reviews": [],
        },
        "gates.json": {"schema_version": "0.5", "gates": gates, "decisions": decisions},
        "evidence.json": {"schema_version": "0.5", "evidence": evidence},
        "integrations.json": {"schema_version": "0.5", "integrations": list(integrations)},
    }
    for name, data in docs.items():
        (aegis / name).write_text(json.dumps(data), encoding="utf-8")


def errors_for(*, decisions=None, integrations=None, gates=None, evidence=None):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        write_v05(root, decisions=decisions, integrations=integrations, gates=gates, evidence=evidence)
        return validate_manifests(load_manifests(root))


class GateDecisionLineageV05Tests(unittest.TestCase):
    def test_re_review_pass_clears_current_blocker_without_rewriting_integration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_v05(
                root,
                decisions=[
                    decision(D1, "BLOCKED_EVIDENCE"),
                    decision(D2, "PASS", evidence_ids=["ev-pass"], supersedes=D1),
                ],
            )
            manifests = load_manifests(root)
            self.assertEqual([], validate_manifests(manifests))
            state = compute_state(manifests)

            self.assertIn(
                {"gate_id": "G1", "decision_id": D2, "verdict": "PASS"},
                state["current_gate_decisions"],
            )
            self.assertNotIn("G1", state["blocking_gates"])
            self.assertNotIn(D1, state["blocking_gate_decisions"])
            self.assertIn(
                {"integration_id": "int1", "gate_decision_id": D1, "conformance": "nonconforming"},
                state["integration_conformance"],
            )
            self.assertEqual(["int1"], state["nonconforming_integrations"])

    def test_initial_blocked_decision_is_the_current_blocker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_v05(root)
            manifests = load_manifests(root)
            self.assertEqual([], validate_manifests(manifests))
            state = compute_state(manifests)
            self.assertEqual(["G1"], state["blocking_gates"])
            self.assertEqual([D1], state["blocking_gate_decisions"])
            self.assertIn(
                {"gate_id": "G1", "decision_id": D1, "verdict": "BLOCKED_EVIDENCE"},
                state["current_gate_decisions"],
            )

    def test_duplicate_decision_id_is_rejected(self):
        errors = errors_for(
            decisions=[
                decision(D1, "BLOCKED_EVIDENCE"),
                decision(D1, "PASS", evidence_ids=["ev-pass"]),
            ]
        )
        self.assertTrue(any("duplicate gate decision id" in error for error in errors), errors)

    def test_gate_without_decision_is_rejected(self):
        errors = errors_for(decisions=[])
        self.assertTrue(any("at least one gate decision" in error for error in errors), errors)

    def test_decision_id_must_match_gate_and_sequence_format(self):
        errors = errors_for(decisions=[decision("wrong-id", "BLOCKED_EVIDENCE")])
        self.assertTrue(any("decision id" in error and "sequence" in error for error in errors), errors)

    def test_sequence_gap_is_rejected(self):
        errors = errors_for(
            decisions=[
                decision(D1, "BLOCKED_EVIDENCE"),
                decision("G1::decision::0003", "PASS", evidence_ids=["ev-pass"], supersedes=D1),
            ]
        )
        self.assertTrue(any("sequence" in error for error in errors), errors)

    def test_dangling_supersedes_is_rejected(self):
        errors = errors_for(
            decisions=[
                decision(D1, "BLOCKED_EVIDENCE", supersedes="G1::decision::0000"),
            ]
        )
        self.assertTrue(any("dangling supersedes" in error for error in errors), errors)

    def test_cross_gate_supersedes_is_rejected(self):
        errors = errors_for(
            gates=[
                {"id": "G1", "stage": "P34", "authority_ids": ["auth"]},
                {"id": "G2", "stage": "P34", "authority_ids": ["auth"]},
            ],
            decisions=[
                decision(D1, "BLOCKED_EVIDENCE"),
                decision("G2::decision::0001", "PASS", gate_id="G2", evidence_ids=["ev-pass"], supersedes=D1),
            ],
        )
        self.assertTrue(any("cross-gate" in error for error in errors), errors)

    def test_decision_cycle_is_rejected(self):
        errors = errors_for(
            decisions=[
                decision(D1, "BLOCKED_EVIDENCE", supersedes=D2),
                decision(D2, "PASS", evidence_ids=["ev-pass"], supersedes=D1),
            ]
        )
        self.assertTrue(any("decision lineage cycle" in error for error in errors), errors)

    def test_two_children_for_one_decision_is_rejected(self):
        errors = errors_for(
            decisions=[
                decision(D1, "BLOCKED_EVIDENCE"),
                decision(D2, "PASS", evidence_ids=["ev-pass"], supersedes=D1),
                decision("G1::decision::0003", "PASS", evidence_ids=["ev-pass"], supersedes=D1),
            ]
        )
        self.assertTrue(any("decision lineage fork" in error for error in errors), errors)

    def test_disconnected_lineage_is_rejected(self):
        errors = errors_for(
            decisions=[
                decision(D1, "BLOCKED_EVIDENCE"),
                decision(D2, "PASS", evidence_ids=["ev-pass"]),
            ]
        )
        self.assertTrue(any("decision lineage" in error for error in errors), errors)

    def test_integration_with_missing_gate_decision_is_rejected(self):
        errors = errors_for(
            integrations=[
                {
                    "id": "int1",
                    "kind": "pull_request",
                    "ref": "https://example/pr/1",
                    "gate_decision_id": "G1::decision::9999",
                    "status": "integrated",
                    "target_ref": "main",
                    "evidence_ids": ["ev-occurrence"],
                    "integrated_revision": "abc123",
                }
            ]
        )
        self.assertTrue(any("dangling gate decision" in error for error in errors), errors)

    def test_awaiting_integration_rejects_superseded_pass_decision(self):
        errors = errors_for(
            decisions=[
                decision(D1, "PASS", evidence_ids=["ev-pass"]),
                decision(D2, "PASS", evidence_ids=["ev-pass"], supersedes=D1),
            ],
            integrations=[
                {
                    "id": "int1",
                    "kind": "pull_request",
                    "ref": "https://example/pr/1",
                    "gate_decision_id": D1,
                    "status": "awaiting_integration",
                    "target_ref": "main",
                    "evidence_ids": ["ev-occurrence"],
                }
            ],
        )
        self.assertTrue(any("requires current PASS/PASS_WITH_FINDINGS gate decision" in error for error in errors), errors)

    def test_awaiting_integration_rejects_current_blocked_decision(self):
        errors = errors_for(
            integrations=[
                {
                    "id": "int1",
                    "kind": "pull_request",
                    "ref": "https://example/pr/1",
                    "gate_decision_id": D1,
                    "status": "awaiting_integration",
                    "target_ref": "main",
                    "evidence_ids": ["ev-occurrence"],
                }
            ]
        )
        self.assertTrue(any("requires current PASS/PASS_WITH_FINDINGS gate decision" in error for error in errors), errors)

    def test_unavailable_historical_decision_evidence_does_not_reactivate_blocker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = [
                {"id": "ev-block", "type": "gate_review", "ref": "gate://blocked", "status": "missing"},
                {"id": "ev-pass", "type": "gate_review", "ref": "gate://pass", "status": "available"},
                {"id": "ev-occurrence", "type": "repository_integration", "ref": "git://abc123", "status": "available"},
            ]
            write_v05(
                root,
                decisions=[
                    decision(D1, "BLOCKED_EVIDENCE"),
                    decision(D2, "PASS", evidence_ids=["ev-pass"], supersedes=D1),
                ],
                evidence=evidence,
            )
            manifests = load_manifests(root)
            self.assertEqual([], validate_manifests(manifests))
            state = compute_state(manifests)
            self.assertNotIn("G1", state["blocking_gates"])
            self.assertNotIn("G1", state["stale_gates"])
            self.assertIn("int1", state["nonconforming_integrations"])

    def test_unavailable_current_decision_evidence_routes_to_p34(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = [
                {"id": "ev-block", "type": "gate_review", "ref": "gate://blocked", "status": "available"},
                {"id": "ev-pass", "type": "gate_review", "ref": "gate://pass", "status": "missing"},
                {"id": "ev-occurrence", "type": "repository_integration", "ref": "git://abc123", "status": "available"},
            ]
            write_v05(
                root,
                decisions=[
                    decision(D1, "BLOCKED_EVIDENCE"),
                    decision(D2, "PASS", evidence_ids=["ev-pass"], supersedes=D1),
                ],
                evidence=evidence,
            )
            manifests = load_manifests(root)
            state = compute_state(manifests)
            self.assertIn("G1", state["stale_gates"])
            self.assertEqual("verification", state["earliest_untrusted_layer"])
            self.assertEqual("P34", state["recommended_next_stage"])


if __name__ == "__main__":
    unittest.main()
