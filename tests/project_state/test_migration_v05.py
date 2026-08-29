import json
import tempfile
import unittest
from pathlib import Path

from tools.aegis_state.compute import compute_state
from tools.aegis_state.migrate_v05 import legacy_decision_id, migrate_v04_to_v05
from tools.aegis_state.model import load_manifests, validate_manifests


ROOT = Path(__file__).resolve().parents[2]


def write_v04(root: Path):
    aegis = root / ".aegis"
    aegis.mkdir(parents=True)
    docs = {
        "project.json": {
            "schema_version": "0.4",
            "project": {"id": "demo", "name": "Demo", "profile": "standard", "lifecycle_hint": "verification"},
        },
        "authorities.json": {
            "schema_version": "0.4",
            "authorities": [
                {"id": "auth", "scope": "runtime", "kind": "system_architecture", "version": "v1", "status": "Current", "ref": "docs/a.md", "depends_on": []}
            ],
            "impact_reviews": [],
        },
        "gates.json": {
            "schema_version": "0.4",
            "gates": [
                {"id": "G1", "stage": "P34", "verdict": "BLOCKED_EVIDENCE", "validity": "current", "authority_ids": ["auth"], "evidence_ids": ["ev-gate"]}
            ],
        },
        "evidence.json": {
            "schema_version": "0.4",
            "evidence": [
                {"id": "ev-gate", "type": "gate_review", "ref": "gate://blocked", "status": "available"},
                {"id": "ev-occurrence", "type": "repository_integration", "ref": "git://abc123", "status": "available"},
            ],
        },
        "integrations.json": {
            "schema_version": "0.4",
            "integrations": [
                {
                    "id": "int1",
                    "kind": "pull_request",
                    "ref": "https://example/pr/1",
                    "gate_id": "G1",
                    "status": "integrated",
                    "target_ref": "main",
                    "evidence_ids": ["ev-occurrence"],
                    "integrated_revision": "abc123",
                }
            ],
        },
    }
    for name, data in docs.items():
        (aegis / name).write_text(json.dumps(data), encoding="utf-8")


def normalized_conformance(state):
    return [
        {key: value for key, value in item.items() if key != "gate_decision_id"}
        for item in state.get("integration_conformance", [])
    ]


class MigrationV05Tests(unittest.TestCase):
    def test_legacy_decision_id_is_deterministic(self):
        self.assertEqual("G1::decision::0001", legacy_decision_id("G1"))
        self.assertEqual("gate-x::decision::0001", legacy_decision_id("gate-x"))

    def test_v04_to_v05_migration_preserves_derived_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_v04(root)
            v04 = load_manifests(root)
            self.assertEqual([], validate_manifests(v04))
            v04_state = compute_state(v04)

            v05 = migrate_v04_to_v05(v04)
            self.assertEqual("0.5", v05.schema_version)
            self.assertEqual([], validate_manifests(v05))
            v05_state = compute_state(v05)

            self.assertEqual(v04_state["blocking_gates"], v05_state["blocking_gates"])
            self.assertEqual(v04_state["integration_applicability"], v05_state["integration_applicability"])
            self.assertEqual(v04_state["nonconforming_integrations"], v05_state["nonconforming_integrations"])
            self.assertEqual(v04_state["integration_conformance"], normalized_conformance(v05_state))
            self.assertEqual("G1::decision::0001", v05.integration_items[0]["gate_decision_id"])
            self.assertNotIn("gate_id", v05.integration_items[0])

    def test_migration_is_repeatable_and_does_not_mutate_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_v04(root)
            source = load_manifests(root)
            source_before = json.dumps(
                {
                    "project": source.project,
                    "authorities": source.authorities,
                    "gates": source.gates,
                    "evidence": source.evidence,
                    "integrations": source.integrations,
                },
                sort_keys=True,
            )
            first = migrate_v04_to_v05(source)
            second = migrate_v04_to_v05(source)
            first_json = json.dumps(
                {
                    "project": first.project,
                    "authorities": first.authorities,
                    "gates": first.gates,
                    "evidence": first.evidence,
                    "integrations": first.integrations,
                },
                sort_keys=True,
            )
            second_json = json.dumps(
                {
                    "project": second.project,
                    "authorities": second.authorities,
                    "gates": second.gates,
                    "evidence": second.evidence,
                    "integrations": second.integrations,
                },
                sort_keys=True,
            )
            self.assertEqual(first_json, second_json)
            self.assertEqual(
                source_before,
                json.dumps(
                    {
                        "project": source.project,
                        "authorities": source.authorities,
                        "gates": source.gates,
                        "evidence": source.evidence,
                        "integrations": source.integrations,
                    },
                    sort_keys=True,
                ),
            )

    def test_non_v04_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_v04(root)
            project_path = root / ".aegis" / "project.json"
            project = json.loads(project_path.read_text(encoding="utf-8"))
            project["schema_version"] = "0.3"
            project_path.write_text(json.dumps(project), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "requires schema_version 0.4"):
                migrate_v04_to_v05(load_manifests(root))

    def test_invalid_v04_source_cannot_be_laundered_by_migration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_v04(root)
            gates_path = root / ".aegis" / "gates.json"
            gates = json.loads(gates_path.read_text(encoding="utf-8"))
            gates["gates"][0]["validity"] = "bogus"
            gates_path.write_text(json.dumps(gates), encoding="utf-8")
            source = load_manifests(root)
            self.assertTrue(validate_manifests(source))
            with self.assertRaisesRegex(ValueError, "invalid v0.4 source"):
                migrate_v04_to_v05(source)

    def test_root_pr9_reconciliation_preserves_nonconforming_occurrence(self):
        root_v04 = load_manifests(ROOT)
        self.assertEqual("0.4", root_v04.schema_version)
        migrated = migrate_v04_to_v05(root_v04)

        gate_id = "gate-skill-decomposition-v02-pr9"
        d1 = legacy_decision_id(gate_id)
        d2 = f"{gate_id}::decision::0002"
        migrated.evidence["evidence"].append(
            {
                "id": "ev-pr9-task6-accepted",
                "type": "gate_review",
                "ref": "https://github.com/Mostorm-Labs/aegis/pull/9#issuecomment-5459909250",
                "status": "available",
                "subject_ids": [d2],
            }
        )
        migrated.gates["decisions"].append(
            {
                "id": d2,
                "gate_id": gate_id,
                "verdict": "PASS",
                "evidence_ids": ["ev-pr9-task6-accepted"],
                "supersedes": d1,
            }
        )

        self.assertEqual([], validate_manifests(migrated))
        state = compute_state(migrated)
        self.assertNotIn(gate_id, state["blocking_gates"])
        self.assertIn("int-pr9", state["nonconforming_integrations"])
        pr9_conformance = next(
            item for item in state["integration_conformance"] if item["integration_id"] == "int-pr9"
        )
        self.assertEqual(d1, pr9_conformance["gate_decision_id"])
        self.assertEqual("nonconforming", pr9_conformance["conformance"])
        self.assertIn(
            {"gate_id": gate_id, "decision_id": d2, "verdict": "PASS"},
            state["current_gate_decisions"],
        )


if __name__ == "__main__":
    unittest.main()
