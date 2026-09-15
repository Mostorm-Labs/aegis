import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "scripts/aegis_execution_package.py"
SKILL = ROOT / "skillset/skills/aegis-implementation/SKILL.md"
REF = ROOT / "skillset/skills/aegis-implementation/references/repo-local-execution-authority.md"


class RepoLocalExecutionAuthorityTests(unittest.TestCase):
    def descriptor(self, root: Path):
        rev = "1" * 40
        return {
            "package": {
                "schema_version": "0.1", "task_id": "GT-G2-00-A6", "stage": "P32", "stage_owner": "aegis-implementation",
                "execution_authority_mode": "repo_materialized",
                "repository": {"provider": "github", "full_name": "Mostorm-Labs/axiom", "canonical_branch": "main"},
                "execution_ref": "codex/gt-g2-a6-incremental-runtime-coordination",
                "task_anchor": {"revision": rev, "relation": "ancestor"}, "resume_cursor": None,
                "continue_until_terminal_state": True, "return_surface": "CONTROL_REVIEW"
            },
            "authority_lock": {"authority_id": "A6", "authority_version": "v1", "authority_state": "Current", "source": {"provider": "notion", "source_id": "page", "source_revision": "rev", "content_hash": "sha256:abc"}, "frozen_statements": ["canonical publication is atomic"], "superseded_by": None},
            "verification_lock": {"verification_spec": "P20", "obligations": [{"id": "R08", "requirement": "observers never see mixed generations", "oracle": {"executable": "observer_atomicity"}, "acceptance": "only complete Gold or Gnew", "evidence_required": ["test-result"]}]},
            "execution_contract": {"required_changes": ["publication transaction"], "forbidden_changes": [], "authorized_mutation_scope": ["runtime"], "preserve_completed_work": [], "required_verification": ["R08"], "blocking_evidence": ["R08"], "corroborative_evidence": [], "terminal_success": {"all_of": ["R08 green", "durable result"]}, "terminal_blockers": ["AUTHORITY_CONFLICT", "VERIFICATION_DESIGN_DEFECT", "TASK_PACKAGE_DEFECT", "PACKAGE_SCOPE_DIVERGENCE"], "continue_until_terminal_state": True, "implementation_design_preflight": {"continue_without_control_return_when_resolved": True}, "oracle_precondition": {"red_required": True, "expected_failure": "mixed generation visible", "observation_seam": "canonical observer"}, "return_contract": {"success_status": "READY_FOR_CONTROL_REVIEW", "return_surface": "CONTROL_REVIEW"}},
            "implementation_context": "Current flow\nA -> B -> C\n\nFirst incomplete action\nBind publication owner.\n",
            "evidence_contract": {"blocking": ["R08"], "corroborative": []}
        }

    def run_tool(self, *args, cwd=None):
        return subprocess.run(["python3", str(TOOL), *map(str, args)], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_materialize_validate_and_thin_handoff(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            descriptor = root / "descriptor.json"
            descriptor.write_text(json.dumps(self.descriptor(root)), encoding="utf-8")
            result = self.run_tool("materialize", descriptor, "--root", root)
            self.assertEqual(result.returncode, 0, result.stderr)
            package = root / ".aegis/packages/GT-G2-00-A6/package.json"
            self.assertTrue(package.is_file())
            expected = {"package.json", "authority.lock.json", "verification.lock.json", "execution-contract.json", "implementation-context.md", "evidence-contract.json"}
            self.assertEqual({p.name for p in package.parent.iterdir()}, expected)
            result = self.run_tool("validate", package)
            self.assertEqual(result.returncode, 0, result.stderr)
            handoff = self.run_tool("render-handoff", package, "--materialization-ref", "deadbeef")
            self.assertEqual(handoff.returncode, 0, handoff.stderr)
            self.assertLess(len(handoff.stdout.splitlines()), 30)
            self.assertIn("continue_until_terminal_state: true", handoff.stdout)
            self.assertNotIn("canonical publication is atomic", handoff.stdout)

    def test_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); descriptor = root / "descriptor.json"
            descriptor.write_text(json.dumps(self.descriptor(root)), encoding="utf-8")
            self.assertEqual(self.run_tool("materialize", descriptor, "--root", root).returncode, 0)
            package = root / ".aegis/packages/GT-G2-00-A6/package.json"
            lock = package.parent / "authority.lock.json"
            lock.write_text(lock.read_text() + " ", encoding="utf-8")
            result = self.run_tool("validate", package)
            self.assertEqual(result.returncode, 2)
            self.assertIn("HASH_MISMATCH", result.stderr)

    def test_legacy_remote_package_remains_valid(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); package = root / "package.json"
            package.write_text(json.dumps({"schema_version": "0.1", "task_id": "legacy", "stage": "P32", "stage_owner": "aegis-implementation", "repository": {"provider": "github", "full_name": "Mostorm-Labs/axtp"}, "execution_ref": "main", "task_anchor": {"revision": "1" * 40, "relation": "ancestor"}, "resume_cursor": None, "package_ref": "notion://legacy", "continue_until_terminal_state": True, "return_surface": "CONTROL_REVIEW"}), encoding="utf-8")
            result = self.run_tool("validate", package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("mode=remote", result.stdout)

    def test_contract_text_keeps_preflight_internal_and_gate_independent(self):
        text = SKILL.read_text(encoding="utf-8") + REF.read_text(encoding="utf-8")
        for token in ("ImplementationDesignPreflight", "RED Oracle Preflight", "READY_FOR_CONTROL_REVIEW", "Implementation Producer != Final Gate Reviewer", "progressive"):
            self.assertIn(token, text)
        self.assertIn("not a new P-stage", text)


if __name__ == "__main__":
    unittest.main()
