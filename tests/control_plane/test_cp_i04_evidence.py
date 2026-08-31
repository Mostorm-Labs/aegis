from __future__ import annotations

import hashlib
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
SOURCE_REVISION = "3cb0aa61f69459048f228dc5c979e679d97daf43"
EXPECTED_EVIDENCE_FAMILIES = {
    "CPV-E-TRUST-CURRENTNESS",
    "CPV-E-HISTORICAL-REPLAY",
    "CPV-E-SNAPSHOT-INTEGRITY",
    "CPV-E-ASYNC-PROVIDER-CAPABILITY",
    "CPV-E-CANONICAL-CONFORMANCE",
    "CP-I04-P36-REPAIR-CLOSURE",
    "CP-I04-P36-MANDATORY-MATRIX",
}
EXPECTED_ZERO_METRICS = {
    "stale_success_commits",
    "historical_replay_mismatch",
    "unbound_required_successor",
    "required_child_barrier_bypass",
    "child_spawn_half_commit",
    "barrier_cross_half_commit",
    "tampered_snapshot_accepted",
    "cross_adapter_or_source_snapshot_accepted",
    "cross_resource_or_version_snapshot_accepted",
    "ambiguous_trust_success",
    "callback_only_provider_fully_autonomous",
    "second_canonical_writer",
    "missing_exact_acceptance_fact_accepted",
    "mutable_unpinned_trust_ref_accepted",
    "wrong_acceptance_contract_identity_accepted",
}
EXPECTED_SPAWN_CASES = {
    "after_canonical",
    "after_lane",
    "after_outbox",
    "after_idempotency",
}
EXPECTED_SNAPSHOT_CASES = {
    "payload_tamper",
    "tag_tamper",
    "wrong_adapter",
    "wrong_source",
    "wrong_resource",
    "version_scheme_drift",
    "version_value_drift",
    "expiry",
}
EXPECTED_REPAIR_MUTATION_CASES = {
    "missing_exact_acceptance_fact",
    "mutable_unpinned_trust_ref",
}
EXPECTED_N3_TYPES = {"GATE_DECISION", "PROOF_EVALUATION", "RESULT"}
STATE_FIELDS = {
    "canonical_counts",
    "outbox_count",
    "idempotency_present",
    "occurrence_present",
    "lane_head_ref",
}


class CpI04EvidenceTests(unittest.TestCase):
    def _generate(self, output: Path, result_revision: str) -> dict:
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
        return json.loads((output / "evidence-manifest.json").read_text(encoding="utf-8"))

    def _assert_state(self, state: dict) -> None:
        self.assertEqual(STATE_FIELDS, set(state))
        self.assertIsInstance(state["canonical_counts"], dict)
        self.assertIsInstance(state["outbox_count"], int)
        self.assertIsInstance(state["idempotency_present"], bool)
        self.assertIsInstance(state["occurrence_present"], bool)

    def _assert_case_set(self, cases: list[dict], expected: set[str]) -> dict[str, dict]:
        names = [case["case"] for case in cases]
        self.assertEqual(len(names), len(set(names)), "mandatory evidence cases must be unique")
        self.assertEqual(expected, set(names))
        return {case["case"]: case for case in cases}

    def test_generator_materializes_exact_cp_i04_evidence_without_gate_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "cp-i04"
            result_revision = "1" * 40
            manifest = self._generate(output, result_revision)

            self.assertEqual("CP-I04-P31-01", manifest["task_id"])
            self.assertEqual(PACKAGE_REF, manifest["package_ref"])
            self.assertEqual(result_revision, manifest["result_revision"])
            self.assertEqual(ACCEPTED_CP_I03, manifest["accepted_cp_i03"]["revision"])
            self.assertEqual(CP_I03_P34, manifest["accepted_cp_i03"]["p34_comment"])
            self.assertEqual(EXPECTED_EVIDENCE_FAMILIES, set(manifest["evidence"]))

            repair = manifest["repair"]
            self.assertEqual("CP-I04-P36-03", repair["repair_package_id"])
            self.assertEqual("5483456044", repair["source_p34_rereview_comment"])
            self.assertEqual("5483634948", repair["source_p35_comment"])
            self.assertEqual(SOURCE_REVISION, repair["source_revision"])
            self.assertEqual("CP-I04-P36-02", repair["previous_repair"]["repair_package_id"])
            self.assertEqual("5483324780", repair["previous_repair"]["return_comment"])

            self.assertEqual(EXPECTED_ZERO_METRICS, set(manifest["metrics"]))
            self.assertTrue(all(value == 0 for value in manifest["metrics"].values()))
            self.assertFalse(manifest["claims"]["p34_gate_pass"])
            self.assertFalse(manifest["claims"]["CP_I05_plus"])
            self.assertEqual("DENIED", manifest["claims"]["current_cross_primary_rollout"])
            self.assertNotIn("verdict", manifest)

            self.assertEqual(set(manifest["evidence"].values()), set(manifest["file_digests"]))
            for filename, digest in manifest["file_digests"].items():
                path = output / filename
                self.assertTrue(path.is_file())
                self.assertRegex(digest, r"^sha256:[0-9a-f]{64}$")
                actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(digest, actual)

    def test_evidence_families_carry_required_zero_residue_and_replay_facts(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "cp-i04"
            self._generate(output, "2" * 40)
            canonical = json.loads((output / "canonical-conformance.json").read_text(encoding="utf-8"))
            historical = json.loads((output / "historical-replay.json").read_text(encoding="utf-8"))
            currentness = json.loads((output / "trust-currentness.json").read_text(encoding="utf-8"))
            snapshot = json.loads((output / "snapshot-integrity.json").read_text(encoding="utf-8"))
            provider = json.loads((output / "async-provider-capability.json").read_text(encoding="utf-8"))
            repair = json.loads((output / "p36-repair-closure.json").read_text(encoding="utf-8"))
            mandatory = json.loads((output / "p36-mandatory-matrix.json").read_text(encoding="utf-8"))

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

            self.assertTrue(mandatory["passed"])
            self.assertEqual("CP-I04-P36-03", mandatory["repair_package_id"])
            self.assertEqual("5483456044", mandatory["source_p34_rereview_comment"])
            self.assertEqual("5483634948", mandatory["source_p35_comment"])
            self.assertEqual(SOURCE_REVISION, mandatory["source_revision"])

            spawn_cases = self._assert_case_set(
                mandatory["child_spawn_precommit"], EXPECTED_SPAWN_CASES
            )
            for case in spawn_cases.values():
                self.assertEqual(case["case"], case["injected_checkpoint"])
                self.assertIsNotNone(case["rejection"])
                self._assert_state(case["before"])
                self._assert_state(case["after"])
                self.assertTrue(case["child_occurrence_absent"])
                self.assertTrue(case["child_lane_head_absent"])
                self.assertTrue(case["idempotency_residue_absent"])
                self.assertTrue(case["zero_residue"])

            future = mandatory["historical_d1_future_d2"]
            self.assertTrue(future["historical_replay_preserved"])
            self.assertEqual(future["replay_before"], future["replay_after"])
            self.assertFalse(future["provider_current_satisfies"])
            self.assertTrue(future["future_current_evaluated"])
            self.assertTrue(future["future_mutation_rejected"])
            self.assertIsNotNone(future["future_mutation_code"])
            self._assert_state(future["before"])
            self._assert_state(future["after"])
            self.assertTrue(future["successor_absent"])
            self.assertTrue(future["idempotency_residue_absent"])
            self.assertTrue(future["zero_residue"])

            snapshot_cases = self._assert_case_set(
                mandatory["snapshot_negative_matrix"], EXPECTED_SNAPSHOT_CASES
            )
            for case in snapshot_cases.values():
                self.assertFalse(case["snapshot_accepted"])
                self.assertIsNotNone(case["snapshot_code"])
                self.assertTrue(case["mutation_rejected"])
                self.assertIsNotNone(case["mutation_code"])
                self._assert_state(case["before"])
                self._assert_state(case["after"])
                self.assertTrue(case["successor_absent"])
                self.assertTrue(case["idempotency_residue_absent"])
                self.assertTrue(case["zero_residue"])

            mutation_cases = mandatory["repair_mutation_bound"]
            self.assertEqual(EXPECTED_REPAIR_MUTATION_CASES, set(mutation_cases))
            for name, case in mutation_cases.items():
                self.assertEqual(name, case["case"])
                self.assertFalse(case["resolver_accepted"])
                self.assertIsNotNone(case["resolver_code"])
                self.assertTrue(case["mutation_rejected"])
                self.assertIsNotNone(case["mutation_code"])
                self._assert_state(case["before"])
                self._assert_state(case["after"])
                self.assertTrue(case["successor_absent"])
                self.assertTrue(case["idempotency_residue_absent"])
                self.assertTrue(case["zero_residue"])

            n3 = mandatory["n3_contract_identity_controls"]
            self.assertEqual(EXPECTED_N3_TYPES, set(n3["wrong_acceptance_contract_identity"]))
            self.assertEqual(EXPECTED_N3_TYPES, set(n3["exact_configured_contract_identity"]))
            self.assertTrue(all(not value for value in n3["wrong_acceptance_contract_identity"].values()))
            self.assertTrue(all(n3["exact_configured_contract_identity"].values()))


if __name__ == "__main__":
    unittest.main()
