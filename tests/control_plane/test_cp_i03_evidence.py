from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.generate_cp_i03_evidence import PACKAGE_REF, generate


class CpI03EvidenceTests(unittest.TestCase):
    def test_generates_required_durable_evidence_with_zero_tolerance_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "cp-i03"
            revision = "a" * 40
            manifest = generate(output, revision, PACKAGE_REF)

            expected_files = {
                "ownership-rollout.json",
                "derived-state.json",
                "canonical-conformance.json",
                "evidence-manifest.json",
            }
            self.assertEqual(expected_files, {path.name for path in output.iterdir()})
            self.assertEqual(revision, manifest["result_revision"])
            self.assertEqual(PACKAGE_REF, manifest["package_ref"])
            self.assertEqual(
                "f820132ab6fb9b2af7754773477fe69af513e83c",
                manifest["accepted_cp_i02"]["revision"],
            )
            self.assertEqual("5475361166", manifest["accepted_cp_i02"]["p34_comment"])
            self.assertEqual(
                {
                    "original_blocker_id": "CP-I03-P34-B1",
                    "source_p34_comment": "5476589682",
                    "source_p35_comment": "5476782049",
                    "source_p36_comment": "5477531093",
                    "rereview_blocker_id": "CP-I03-P34-B2",
                    "source_p34_rereview_comment": "5479230527",
                    "source_p35_b2_comment": "5480059914",
                },
                manifest["repair_lineage"],
            )
            self.assertEqual(
                {
                    "CPV-E-OWNERSHIP-ROLLOUT",
                    "CPV-E-DERIVED-STATE",
                    "CPV-E-CANONICAL-CONFORMANCE",
                },
                set(manifest["evidence"]),
            )
            self.assertEqual(
                {
                    "unauthorized_auto_schedules": 0,
                    "unofficial_gate_decisions_accepted": 0,
                    "pinned_policy_mismatch_commits": 0,
                    "stale_projection_authorization": 0,
                    "stale_policy_authorization": 0,
                    "ambiguous_policy_authorization": 0,
                    "cache_pause_lease_only_canonical_mutations": 0,
                },
                manifest["metrics"],
            )
            self.assertFalse(manifest["claims"]["p34_gate_pass"])
            self.assertFalse(manifest["claims"]["R0"])
            self.assertFalse(manifest["claims"]["S0"])
            for filename, expected_digest in manifest["file_digests"].items():
                observed = "sha256:" + hashlib.sha256((output / filename).read_bytes()).hexdigest()
                self.assertEqual(expected_digest, observed)

            ownership = json.loads((output / "ownership-rollout.json").read_text(encoding="utf-8"))
            derived = json.loads((output / "derived-state.json").read_text(encoding="utf-8"))
            canonical = json.loads((output / "canonical-conformance.json").read_text(encoding="utf-8"))
            self.assertTrue(ownership["passed"])
            self.assertTrue(derived["passed"])
            self.assertTrue(canonical["passed"])
            self.assertEqual("PROHIBITED", ownership["current_cross_primary_rollout"])
            self.assertTrue(ownership["pinned_policy_mismatch_denied"])
            self.assertTrue(derived["stale_policy_rejected"])
            self.assertEqual(1, canonical["scheduler_cas_race"]["winner_count"])
            self.assertEqual(1, canonical["scheduler_cas_race"]["loser_count"])

            rejection = canonical["policy_rejection_zero_residue"]
            self.assertTrue(rejection["passed"])
            self.assertEqual(
                {
                    "pinned_policy_mismatch": "CANDIDATE_POLICY_BINDING_MISMATCH",
                    "allow_to_deny": "POLICY_REVALIDATION_DENIED",
                    "changed_policy_digest": "STALE_POLICY_AUTHORIZATION",
                    "stale_current_basis": "POLICY_REVALIDATION_DENIED",
                    "ambiguous_current_basis": "POLICY_REVALIDATION_DENIED",
                },
                rejection["rejection_codes"],
            )
            self.assertTrue(all(rejection["zero_residue"].values()))
            self.assertEqual(
                {
                    "pinned_policy_mismatch_commits": 0,
                    "stale_policy_authorization": 0,
                    "ambiguous_policy_authorization": 0,
                },
                rejection["metrics"],
            )

    def test_generator_is_directly_executable_from_repository_root(self):
        repo_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "cp-i03"
            completed = subprocess.run(
                [
                    sys.executable,
                    "tests/control_plane/generate_cp_i03_evidence.py",
                    "--result-revision",
                    "b" * 40,
                    "--package-ref",
                    PACKAGE_REF,
                    "--output-dir",
                    str(output),
                ],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            self.assertTrue((output / "evidence-manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
