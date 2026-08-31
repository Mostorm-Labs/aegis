from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_REF = "28e89118b68b3cf3eab1cf94ab65a20271e32c80"
ACCEPTED_CP_I03 = "f6820374d29772dfe1069f3502b6e4f80795fd80"
CP_I03_P34 = "5480775507"


class CpI04EvidenceTests(unittest.TestCase):
    def test_generator_materializes_exact_cp_i04_evidence_without_gate_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "cp-i04"
            result_revision = "1" * 40
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tests/control_plane/cp_i04_p36_evidence.py"),
                    "--result-revision",
                    result_revision,
                    "--package-ref",
                    PACKAGE_REF,
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
            )
            manifest = json.loads((output / "evidence-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("CP-I04-P31-01", manifest["task_id"])
            self.assertEqual(PACKAGE_REF, manifest["package_ref"])
            self.assertEqual(result_revision, manifest["result_revision"])
            self.assertEqual(ACCEPTED_CP_I03, manifest["accepted_cp_i03"]["revision"])
            self.assertEqual(CP_I03_P34, manifest["accepted_cp_i03"]["p34_comment"])
            self.assertEqual("CP-I04-P36-02", manifest["repair"]["repair_package_id"])
            self.assertTrue(
                {
                    "CPV-E-TRUST-CURRENTNESS",
                    "CPV-E-HISTORICAL-REPLAY",
                    "CPV-E-SNAPSHOT-INTEGRITY",
                    "CPV-E-ASYNC-PROVIDER-CAPABILITY",
                    "CPV-E-CANONICAL-CONFORMANCE",
                    "CP-I04-P36-REPAIR-CLOSURE",
                }.issubset(set(manifest["evidence"]))
            )
            self.assertTrue(all(value == 0 for value in manifest["metrics"].values()))
            self.assertEqual(0, manifest["metrics"]["missing_exact_acceptance_fact_accepted"])
            self.assertEqual(0, manifest["metrics"]["mutable_unpinned_trust_ref_accepted"])
            self.assertEqual(0, manifest["metrics"]["wrong_acceptance_contract_identity_accepted"])
            self.assertFalse(manifest["claims"]["p34_gate_pass"])
            self.assertFalse(manifest["claims"]["CP_I05_plus"])
            self.assertEqual("DENIED", manifest["claims"]["current_cross_primary_rollout"])
            for filename, digest in manifest["file_digests"].items():
                self.assertTrue((output / filename).is_file())
                self.assertRegex(digest, r"^sha256:[0-9a-f]{64}$")

    def test_evidence_families_carry_required_zero_residue_and_replay_facts(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "cp-i04"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tests/control_plane/cp_i04_p36_evidence.py"),
                    "--result-revision",
                    "2" * 40,
                    "--package-ref",
                    PACKAGE_REF,
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
            )
            canonical = json.loads((output / "canonical-conformance.json").read_text(encoding="utf-8"))
            historical = json.loads((output / "historical-replay.json").read_text(encoding="utf-8"))
            currentness = json.loads((output / "trust-currentness.json").read_text(encoding="utf-8"))
            snapshot = json.loads((output / "snapshot-integrity.json").read_text(encoding="utf-8"))
            provider = json.loads((output / "async-provider-capability.json").read_text(encoding="utf-8"))
            repair = json.loads((output / "p36-repair-closure.json").read_text(encoding="utf-8"))

            self.assertTrue(canonical["passed"])
            self.assertTrue(canonical["child_spawn_atomicity"]["zero_residue"])
            self.assertTrue(canonical["barrier_cross_atomicity"]["zero_residue"])
            self.assertTrue(canonical["required_child_denial"]["zero_residue"])
            self.assertEqual(["mutation.py"], canonical["single_writer"]["transaction_callers"])
            self.assertEqual(["store.py"], canonical["single_writer"]["raw_canonical_sql_owners"])

            self.assertTrue(historical["passed"])
            self.assertEqual(historical["pinned_fact_before"], historical["pinned_fact_after"])
            self.assertNotEqual(historical["pinned_fact_after"], historical["current_fact_after"])

            self.assertTrue(currentness["passed"])
            self.assertTrue(currentness["stale_between_resolve_and_commit"]["zero_residue"])
            self.assertTrue(currentness["ambiguous_trust"]["zero_residue"])

            self.assertTrue(snapshot["passed"])
            self.assertFalse(snapshot["tampered_payload"]["accepted"])
            self.assertFalse(snapshot["wrong_source"]["accepted"])
            self.assertFalse(snapshot["wrong_resource"]["accepted"])
            self.assertFalse(snapshot["wrong_version"]["accepted"])

            self.assertTrue(provider["passed"])
            self.assertFalse(provider["callback_only"]["full_autonomous_trust_capable"])
            self.assertTrue(provider["queryable"]["full_autonomous_trust_capable"])

            self.assertTrue(repair["passed"])
            self.assertFalse(repair["missing_exact_acceptance_fact"]["accepted"])
            self.assertFalse(repair["mutable_unpinned_trust_ref"]["accepted"])
            self.assertTrue(all(not value for value in repair["wrong_acceptance_contract_identity"].values()))
            self.assertTrue(all(repair["exact_configured_contract_identity"].values()))


if __name__ == "__main__":
    unittest.main()
