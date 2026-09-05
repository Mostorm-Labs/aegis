import unittest

from tools.aegis_proof.evidence import EvidenceCompiler, EvidencePlan, EvidenceRequirement
from tools.aegis_proof.ports import ObservationBatch, ObservationRecord


class EvidenceCompilerTests(unittest.TestCase):
    def _plan(self):
        return EvidencePlan((EvidenceRequirement("test.summary", "pytest-json", True),))

    def _batches(self, secondary="manual", secondary_skip=25):
        return (
            ObservationBatch("pytest-json", True, (
                ObservationRecord("test.summary", "DETERMINISTIC_COLLECTOR", "pytest-json", "result@1", {"pass": 445, "skip": 23}),
            )),
            ObservationBatch(secondary, True, (
                ObservationRecord("test.summary", "REVIEWER", secondary, "result@1", {"pass": 445, "skip": secondary_skip}),
            )),
        )

    def _assert_authoritative_oracle(self, compiler, *, secondary="manual", secondary_skip=25):
        artifact = compiler.compile(plan=self._plan(), batches=self._batches(secondary, secondary_skip))
        self.assertEqual(artifact["facts"]["test.summary"], {"pass": 445, "skip": 23})
        self.assertTrue(artifact["complete"])
        return artifact

    def test_EC_S01_authoritative_structured_source_wins(self):
        artifact = self._assert_authoritative_oracle(EvidenceCompiler())
        self.assertEqual(artifact["conflicts"][0]["producer_id"], "manual")

    def test_EC_S14_handoff_totals_are_non_authoritative(self):
        artifact = self._assert_authoritative_oracle(EvidenceCompiler(), secondary="handoff", secondary_skip=99)
        self.assertEqual(artifact["facts"]["test.summary"]["skip"], 23)

    def test_P34_B2_conflicting_authoritative_batches_fail_closed(self):
        batches = (
            ObservationBatch("pytest-json", True, (
                ObservationRecord("test.summary", "DETERMINISTIC_COLLECTOR", "pytest-json", "result@1", {"pass": 445, "skip": 23}),
            )),
            ObservationBatch("pytest-json", True, (
                ObservationRecord("test.summary", "DETERMINISTIC_COLLECTOR", "pytest-json", "result@1", {"pass": 445, "skip": 24}),
            )),
        )
        artifact = EvidenceCompiler().compile(plan=self._plan(), batches=batches)
        self.assertFalse(artifact["complete"])
        self.assertIn("test.summary", artifact["missing_required"])
        self.assertNotIn("test.summary", artifact["facts"])
        self.assertTrue(any(item.get("authoritative") for item in artifact["conflicts"]))

    def test_EC_M01_manual_override_mutant_is_killed(self):
        class ManualOverrideMutant(EvidenceCompiler):
            def compile(self, *, plan, batches):
                artifact = super().compile(plan=plan, batches=batches)
                manual = next(batch for batch in batches if batch.producer_id == "manual")
                artifact = dict(artifact)
                artifact["facts"] = dict(artifact["facts"])
                artifact["facts"]["test.summary"] = manual.observations[0].value
                return artifact

        with self.assertRaises(AssertionError):
            self._assert_authoritative_oracle(ManualOverrideMutant())
        self._assert_authoritative_oracle(EvidenceCompiler())

    def test_EC_M14_handoff_override_mutant_is_killed(self):
        class HandoffOverrideMutant(EvidenceCompiler):
            def compile(self, *, plan, batches):
                artifact = super().compile(plan=plan, batches=batches)
                handoff = next(batch for batch in batches if batch.producer_id == "handoff")
                artifact = dict(artifact)
                artifact["facts"] = {"test.summary": handoff.observations[0].value}
                return artifact

        with self.assertRaises(AssertionError):
            self._assert_authoritative_oracle(HandoffOverrideMutant(), secondary="handoff", secondary_skip=99)
        self._assert_authoritative_oracle(EvidenceCompiler(), secondary="handoff", secondary_skip=99)

    def _assert_incomplete_producer_oracle(self, compiler):
        artifact = compiler.compile(
            plan=self._plan(),
            batches=(ObservationBatch("pytest-json", False, ()),),
        )
        self.assertFalse(artifact["complete"])
        self.assertIn("test.summary", artifact["missing_required"])
        self.assertNotEqual(artifact.get("facts", {}).get("test.summary"), {"fail": 0})

    def test_EC_M17_zero_failure_mutant_is_killed(self):
        class ZeroFailureMutant(EvidenceCompiler):
            def compile(self, *, plan, batches):
                artifact = dict(super().compile(plan=plan, batches=batches))
                artifact["facts"] = dict(artifact["facts"])
                artifact["facts"]["test.summary"] = {"fail": 0}
                artifact["missing_required"] = []
                artifact["complete"] = True
                return artifact

        with self.assertRaises(AssertionError):
            self._assert_incomplete_producer_oracle(ZeroFailureMutant())
        self._assert_incomplete_producer_oracle(EvidenceCompiler())


if __name__ == "__main__":
    unittest.main()
