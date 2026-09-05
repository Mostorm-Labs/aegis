import unittest

from tools.aegis_proof.evidence import EvidenceCompiler, EvidencePlan, EvidenceRequirement
from tools.aegis_proof.ports import ObservationBatch, ObservationRecord


class EvidenceCompilerTests(unittest.TestCase):
    def _plan(self):
        return EvidencePlan((EvidenceRequirement("test.summary", "pytest-json", True),))

    def test_EC_S01_authoritative_structured_source_wins(self):
        batches = (
            ObservationBatch("pytest-json", True, (
                ObservationRecord("test.summary", "DETERMINISTIC_COLLECTOR", "pytest-json", "result@1", {"pass": 445, "skip": 23}),
            )),
            ObservationBatch("manual", True, (
                ObservationRecord("test.summary", "REVIEWER", "manual", "result@1", {"pass": 445, "skip": 25}),
            )),
        )
        artifact = EvidenceCompiler().compile(plan=self._plan(), batches=batches)
        self.assertEqual(artifact["facts"]["test.summary"], {"pass": 445, "skip": 23})
        self.assertEqual(artifact["conflicts"][0]["producer_id"], "manual")

    def test_EC_S14_handoff_totals_are_non_authoritative(self):
        batches = (
            ObservationBatch("pytest-json", True, (
                ObservationRecord("test.summary", "DETERMINISTIC_COLLECTOR", "pytest-json", "result@1", {"pass": 10, "skip": 2}),
            )),
            ObservationBatch("handoff", True, (
                ObservationRecord("test.summary", "REVIEWER", "handoff", "result@1", {"pass": 10, "skip": 99}),
            )),
        )
        artifact = EvidenceCompiler().compile(plan=self._plan(), batches=batches)
        self.assertEqual(artifact["facts"]["test.summary"]["skip"], 2)

    def test_EC_M01_manual_override_mutant_is_detected(self):
        class ManualOverrideMutant(EvidenceCompiler):
            def compile(self, *, plan, batches):
                artifact = super().compile(plan=plan, batches=batches)
                for batch in batches:
                    if batch.producer_id == "manual":
                        artifact = dict(artifact)
                        artifact["facts"] = dict(artifact["facts"])
                        artifact["facts"]["test.summary"] = batch.observations[0].value
                return artifact
        batches = (
            ObservationBatch("pytest-json", True, (ObservationRecord("test.summary", "DETERMINISTIC_COLLECTOR", "pytest-json", "r", {"pass": 445, "skip": 23}),)),
            ObservationBatch("manual", True, (ObservationRecord("test.summary", "REVIEWER", "manual", "r", {"pass": 445, "skip": 25}),)),
        )
        self.assertNotEqual(ManualOverrideMutant().compile(plan=self._plan(), batches=batches)["facts"]["test.summary"], {"pass": 445, "skip": 23})

    def test_EC_M14_handoff_override_mutant_is_detected(self):
        class HandoffOverrideMutant(EvidenceCompiler):
            def compile(self, *, plan, batches):
                artifact = super().compile(plan=plan, batches=batches)
                handoff = next(b for b in batches if b.producer_id == "handoff")
                artifact = dict(artifact)
                artifact["facts"] = {"test.summary": handoff.observations[0].value}
                return artifact
        batches = (
            ObservationBatch("pytest-json", True, (ObservationRecord("test.summary", "DETERMINISTIC_COLLECTOR", "pytest-json", "r", {"pass": 10, "skip": 2}),)),
            ObservationBatch("handoff", True, (ObservationRecord("test.summary", "REVIEWER", "handoff", "r", {"pass": 10, "skip": 99}),)),
        )
        self.assertEqual(HandoffOverrideMutant().compile(plan=self._plan(), batches=batches)["facts"]["test.summary"]["skip"], 99)

    def test_EC_M17_incomplete_producer_is_not_zero_failures(self):
        batch = ObservationBatch("pytest-json", False, ())
        artifact = EvidenceCompiler().compile(plan=self._plan(), batches=(batch,))
        self.assertIn("test.summary", artifact["missing_required"])
        self.assertNotEqual(artifact.get("facts", {}).get("test.summary"), {"fail": 0})


if __name__ == "__main__":
    unittest.main()
