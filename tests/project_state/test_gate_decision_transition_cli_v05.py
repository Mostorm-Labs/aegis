import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
D1 = "G1::decision::0001"
D2 = "G1::decision::0002"


def write_snapshot(root: Path, decisions):
    aegis = root / ".aegis"
    aegis.mkdir(parents=True)
    docs = {
        "project.json": {
            "schema_version": "0.5",
            "project": {"id": "demo", "name": "Demo", "profile": "standard", "lifecycle_hint": "verification"},
        },
        "authorities.json": {
            "schema_version": "0.5",
            "authorities": [
                {"id": "auth", "scope": "runtime", "kind": "system_architecture", "version": "v1", "status": "Current", "ref": "docs/a.md", "depends_on": []}
            ],
            "impact_reviews": [],
        },
        "gates.json": {
            "schema_version": "0.5",
            "gates": [{"id": "G1", "stage": "P34", "authority_ids": ["auth"]}],
            "decisions": decisions,
        },
        "evidence.json": {
            "schema_version": "0.5",
            "evidence": [
                {"id": "ev-old", "type": "gate_review", "ref": "gate://old", "status": "available"},
                {"id": "ev-new", "type": "gate_review", "ref": "gate://new", "status": "available"},
            ],
        },
        "integrations.json": {"schema_version": "0.5", "integrations": []},
    }
    for name, data in docs.items():
        (aegis / name).write_text(json.dumps(data), encoding="utf-8")


def blocked_decision(verdict="BLOCKED_EVIDENCE", evidence_ids=None):
    return {
        "id": D1,
        "gate_id": "G1",
        "verdict": verdict,
        "evidence_ids": ["ev-old"] if evidence_ids is None else list(evidence_ids),
    }


def pass_decision():
    return {
        "id": D2,
        "gate_id": "G1",
        "verdict": "PASS",
        "evidence_ids": ["ev-new"],
        "supersedes": D1,
    }


def run_transition(previous: Path, current: Path):
    return subprocess.run(
        [sys.executable, "-m", "tools.aegis_state.cli", "transition-check", str(previous), str(current)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


class GateDecisionTransitionCLIV05Tests(unittest.TestCase):
    def test_transition_cli_rejects_in_place_verdict_rewrite_and_routes_p21(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            previous = base / "previous"
            current = base / "current"
            write_snapshot(previous, [blocked_decision()])
            write_snapshot(current, [blocked_decision(verdict="PASS")])
            proc = run_transition(previous, current)
            self.assertNotEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("BLOCKED_AUTHORITY", proc.stdout)
            self.assertIn("P21", proc.stdout)
            self.assertIn("immutable gate decision", proc.stdout)

    def test_transition_cli_rejects_in_place_evidence_rewrite(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            previous = base / "previous"
            current = base / "current"
            write_snapshot(previous, [blocked_decision()])
            write_snapshot(current, [blocked_decision(evidence_ids=["ev-new"])])
            proc = run_transition(previous, current)
            self.assertNotEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("immutable gate decision", proc.stdout)

    def test_transition_cli_rejects_decision_deletion(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            previous = base / "previous"
            current = base / "current"
            write_snapshot(previous, [blocked_decision()])
            write_snapshot(current, [])
            proc = run_transition(previous, current)
            self.assertNotEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("removed immutable gate decision", proc.stdout)

    def test_transition_cli_accepts_append_only_re_review(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            previous = base / "previous"
            current = base / "current"
            write_snapshot(previous, [blocked_decision()])
            write_snapshot(current, [blocked_decision(), pass_decision()])
            proc = run_transition(previous, current)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("TRANSITION_OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
