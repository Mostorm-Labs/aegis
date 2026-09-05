import unittest

from tools.aegis_proof.evaluation import ProofEvaluator
from tools.aegis_proof.review import IndependentCompletenessChecker, ReviewBundleAdapter, ReviewContractDiffer, ReviewDelta


def verification_spec():
    return {
        "id": "vs",
        "version": "v0.1",
        "coverage_basis": {"mode": "EXACT_SET", "requirement_set_digest": "sha256:" + "0" * 64},
        "claims": [{"id": "C1", "proof_contract_id": "PC1"}],
        "proof_contracts": [{"id": "PC1", "claim_id": "C1", "resolved_obligations": [
            {"kind": "INVARIANT", "source_key": "one", "evaluation_mode": "DETERMINISTIC", "required_evidence_types": ["TEST"], "pass_condition": "pass"},
            {"kind": "PROBE", "source_key": "two", "evaluation_mode": "DETERMINISTIC", "required_evidence_types": ["TEST"], "pass_condition": "pass"},
        ]}],
    }


class EvaluationReviewTests(unittest.TestCase):
    def test_EC_S04_undeclared_gate_field_routes_upstream(self):
        delta = ReviewContractDiffer().classify(
            requested_requirement={"field": "new_gate_critical_field"},
            verification_spec={"declared_review_fields": ["known"]},
            package={"declared_review_fields": ["known"]},
        )
        self.assertEqual(delta, ReviewDelta.UNDECLARED)

    def test_EC_S15_independent_completeness_detects_omission(self):
        spec = verification_spec()
        checker = IndependentCompletenessChecker()
        expected = checker.expected_ids(verification_spec=spec)
        result = checker.check(verification_spec=spec, actual_obligation_set={"obligation_ids": [expected[0]]})
        self.assertFalse(result.complete)
        self.assertEqual(len(result.missing_ids), 1)

    def test_EC_S16_unresolved_result_is_not_review_ready(self):
        checker = IndependentCompletenessChecker()
        complete = checker.check(verification_spec=verification_spec(), actual_obligation_set={"obligation_ids": list(checker.expected_ids(verification_spec=verification_spec()))})
        bundle = ReviewBundleAdapter().build(
            package_ref={"ref": "pkg://1", "reviewer_resolvable": True},
            result_ref={"ref": "result://missing", "reviewer_resolvable": False},
            evidence_input_refs=[{"ref": "evidence://1", "reviewer_resolvable": True}],
            proof_evaluation_ref={"ref": "eval://1", "reviewer_resolvable": True},
            completeness=complete,
        )
        self.assertFalse(bundle["review_ready"])
        self.assertEqual(bundle["blocker"], "BLOCKED_EVIDENCE")

    def test_EC_M04_undeclared_requirement_cannot_be_p32_repair(self):
        delta = ReviewContractDiffer().classify(
            requested_requirement={"field": "new_gate_critical_field"},
            verification_spec={"declared_review_fields": []},
            package={"declared_review_fields": []},
        )
        self.assertNotEqual(delta.value, "P32_REPAIR")

    def test_EC_M13_evaluator_cannot_emit_gate_pass(self):
        result = ProofEvaluator().evaluate(
            verification_spec={},
            obligation_set={"obligations": [{"id": "o1", "evaluation_mode": "DETERMINISTIC"}]},
            evidence_input_refs=[{"obligation_id": "o1", "status": "SATISFIED"}],
            evaluator_version="0.1",
        )
        serialized = repr(result.proof_evaluation) + repr(result.verification_summary)
        self.assertNotIn("P34", serialized)
        self.assertNotIn("GATE_PASS", serialized)

    def test_EC_M15_completeness_does_not_call_generator(self):
        import tools.aegis_proof.obligations as obligations
        original = obligations.ObligationGenerator.generate
        try:
            obligations.ObligationGenerator.generate = staticmethod(lambda *a, **k: (_ for _ in ()).throw(AssertionError("generator called")))
            checker = IndependentCompletenessChecker()
            expected = checker.expected_ids(verification_spec=verification_spec())
            result = checker.check(verification_spec=verification_spec(), actual_obligation_set={"obligation_ids": list(expected)})
            self.assertTrue(result.complete)
        finally:
            obligations.ObligationGenerator.generate = original


if __name__ == "__main__":
    unittest.main()
