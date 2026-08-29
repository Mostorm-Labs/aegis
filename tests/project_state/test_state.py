import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.project_state.helpers import manifests, write_project
from tools.aegis_state.compute import compute_state
from tools.aegis_state.model import load_manifests


class StateTests(unittest.TestCase):
    def test_recompute_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_project(root)
            manifests_obj = load_manifests(root)
            a = compute_state(manifests_obj)
            b = compute_state(manifests_obj)
            self.assertEqual(a, b)
            self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_evidence_only_gate_problem_routes_to_p34(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            project, authorities, gates, evidence = manifests()
            gates["gates"][0]["validity"] = "stale"
            evidence["evidence"][0]["status"] = "missing"
            write_project(root, project, authorities, gates, evidence)
            state = compute_state(load_manifests(root))
            self.assertIn("G1", state["stale_gates"])
            self.assertEqual(state["earliest_untrusted_layer"], "verification")
            self.assertEqual(state["recommended_next_stage"], "P34")

    def test_cli_check_detects_state_drift(self):
        repo_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_project(root, state={"schema_version":"0.1","manifest_digest":"wrong"})
            proc = subprocess.run([sys.executable,"-m","tools.aegis_state.cli","check",str(root)], cwd=repo_root, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 3, proc.stdout + proc.stderr)
            self.assertIn("STATE_DRIFT", proc.stdout)

    def test_cli_recompute_write_then_check_passes(self):
        repo_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_project(root)
            write_proc = subprocess.run([sys.executable,"-m","tools.aegis_state.cli","recompute",str(root),"--write"], cwd=repo_root, text=True, capture_output=True)
            self.assertEqual(write_proc.returncode, 0, write_proc.stdout + write_proc.stderr)
            check_proc = subprocess.run([sys.executable,"-m","tools.aegis_state.cli","check",str(root)], cwd=repo_root, text=True, capture_output=True)
            self.assertEqual(check_proc.returncode, 0, check_proc.stdout + check_proc.stderr)
            self.assertIn("STATE_OK", check_proc.stdout)

    def test_cli_migrate_v05_then_check_passes(self):
        repo_root = Path(__file__).resolve().parents[2]
        source = repo_root / "examples" / "project-state" / "minimal"
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated"
            migrate_proc = subprocess.run(
                [sys.executable, "-m", "tools.aegis_state.cli", "migrate-v05", str(source), str(destination)],
                cwd=repo_root,
                text=True,
                capture_output=True,
            )
            self.assertEqual(migrate_proc.returncode, 0, migrate_proc.stdout + migrate_proc.stderr)
            self.assertIn("MIGRATED_V05", migrate_proc.stdout)

            check_proc = subprocess.run(
                [sys.executable, "-m", "tools.aegis_state.cli", "check", str(destination)],
                cwd=repo_root,
                text=True,
                capture_output=True,
            )
            self.assertEqual(check_proc.returncode, 0, check_proc.stdout + check_proc.stderr)
            self.assertIn("STATE_OK", check_proc.stdout)
            state = json.loads((destination / ".aegis" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual("0.5", state["schema_version"])
            self.assertEqual("0.5", state["generator_version"])


if __name__ == "__main__":
    unittest.main()
