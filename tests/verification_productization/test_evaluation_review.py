import hashlib
import json
import unittest

from tools.aegis_proof.evaluation import EvaluationResult, ProofEvaluator
from tools.aegis_proof.review import IndependentCompletenessChecker, ReviewBundleAdapter, ReviewContractDiffer, ReviewDelta


def verification_spec():
    return {
        "id": "vs",
        "version": "v0.1",
        "coverage_basis": {"mode": "EXACT_SET", "requirement_set_digest": "sha256:" + "0" * 64},
        "claims": [{"id": "C1", "proof_contract_id": "PC1"}],
        "proof_contracts": [{"id": "PC1", "claim_id": "C1", "resolved_obligations": [
            {"kind": "INVARIANT", "source_key": "one", "evaluation_mode": "DETERMINISTIC", "required_evidence_types": ["TEST"], "pass_condition": "pass"},
            {"kind": "PROBE", "source_key": "two", "evaluation_mode": "DETERMINISTIC", "required_evidence_types": ["TEST"], "pass_condition": "probe passes"},
        ]}],
    }


def deterministic_obligation():
    return {
        "id": "o1",
        "subject": {"kind": "CLAIM", "claim_id": "C1", "proof_contract_id": "PC1"},
        "kind": "INVARIANT",
        "source_key": "one",
        "evaluation_mode": "DETERMINISTIC",
        "required_evidence_types": ["TEST"],
        "pass_condition": "pass",
    }


def review_required_obligation():
    return {
        "id": "review-1",
        "subject": {"kind": "COVERAGE_BASIS", "coverage_basis_digest": "sha256:" + "0" * 64},
        "kind": "COVERAGE_COMPLETENESS",
        "source_key": "coverage-completeness",
        "evaluation_mode": "REVIEW_REQUIRED",
        "required_evidence_types": ["REVIEWER"],
        "pass_condition": "CONTROL_REVIEW confirms coverage",
    }


def resolved_evidence(*, obligation_id="o1", pass_condition="pass", passed=True, reviewer_resolvable=True, digest_override=None):
    artifact = {
        "id": "ev-1",
        "producer_class": "DETERMINISTIC_COLLECTOR",
        "subjects": {"claim_ids": ["C1"], "obligation_ids": [obligation_id]},
        "observations": [
            {"obligation_id": obligation_id, "pass_condition": pass_condition, "passed": passed}
        ],
    }
    payload = json.dumps(artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    digest = "sha256:" + hashlib.sha256(payload).hexdigest()
    return {
        "evidence_id": "ev-1",
        "ref": "artifact://ev-1",
        "digest": digest_override or digest,
        "producer_class": "DETERMINISTIC_COLLECTOR",
        "provider": "memory",
        "native_id": "1",
        "reviewer_resolvable": reviewer_resolvable,
        "resolved_artifact": artifact,
    }


class MemoryExactResolver:
    def __init__(self, evidence_ref, artifact, *, reviewer_resolvable=True, resolved_digest=None):
        self._response = {
            "ref": evidence_ref["ref"],
            "digest": resolved_digest or evidence_ref["digest"],
            "provider": evidence_ref["provider"],
            "native_id": evidence_ref["native_id"],
            "reviewer_resolvable": reviewer_resolvable,
            "content": artifact,
        }

    def resolve(self, ref):
        return dict(self._response)


def resolver_binding(**kwargs):
    evidence_ref = dict(resolved_evidence(**kwargs))
    artifact = evidence_ref.pop("resolved_artifact")
    return evidence_ref, MemoryExactResolver(evidence_ref, artifact)


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

    def test_P34_B1_arbitrary_status_mapping_cannot_satisfy(self):
        result = ProofEvaluator().evaluate(
            verification_spec=verification_spec(),
            obligation_set={"obligations": [deterministic_obligation()]},
            evidence_input_refs=[{"obligation_id": "o1", "status": "SATISFIED"}],
            evaluator_version="0.1",
        )
        self.assertEqual(result.proof_evaluation["results"][0]["status"], "UNSATISFIED")

    def test_P34_B1_inline_resolved_artifact_without_exact_resolver_cannot_satisfy(self):
        result = ProofEvaluator().evaluate(
            verification_spec=verification_spec(),
            obligation_set={"obligations": [deterministic_obligation()]},
            evidence_input_refs=[resolved_evidence()],
            evaluator_version="0.1",
        )
        self.assertEqual(result.proof_evaluation["results"][0]["status"], "UNSATISFIED")

    def test_P34_B1_exact_resolver_applies_frozen_pass_condition(self):
        evidence_ref, resolver = resolver_binding()
        evaluator = ProofEvaluator(resolver=resolver)
        result = evaluator.evaluate(
            verification_spec=verification_spec(),
            obligation_set={"obligations": [deterministic_obligation()]},
            evidence_input_refs=[evidence_ref],
            evaluator_version="0.1",
        )
        self.assertEqual(result.proof_evaluation["results"][0]["status"], "SATISFIED")

    def test_P34_B1_digest_mismatch_fails_closed(self):
        evidence_ref, resolver = resolver_binding(digest_override="sha256:" + "f" * 64)
        evaluator = ProofEvaluator(resolver=resolver)
        result = evaluator.evaluate(
            verification_spec=verification_spec(),
            obligation_set={"obligations": [deterministic_obligation()]},
            evidence_input_refs=[evidence_ref],
            evaluator_version="0.1",
        )
        self.assertEqual(result.proof_evaluation["results"][0]["status"], "UNSATISFIED")

    def test_P34_B1_unresolved_or_nonreviewable_evidence_fails_closed(self):
        evidence_ref, resolver = resolver_binding(reviewer_resolvable=False)
        evaluator = ProofEvaluator(resolver=resolver)
        result = evaluator.evaluate(
            verification_spec=verification_spec(),
            obligation_set={"obligations": [deterministic_obligation()]},
            evidence_input_refs=[evidence_ref],
            evaluator_version="0.1",
        )
        self.assertEqual(result.proof_evaluation["results"][0]["status"], "UNSATISFIED")

    def test_P34_B1_review_required_remains_exception(self):
        result = ProofEvaluator().evaluate(
            verification_spec=verification_spec(),
            obligation_set={"obligations": [review_required_obligation()]},
            evidence_input_refs=[],
            evaluator_version="0.1",
        )
        self.assertEqual(result.proof_evaluation["results"][0]["status"], "EXCEPTION")

    def _assert_undeclared_oracle(self, differ):
        delta = differ.classify(
            requested_requirement={"field": "new_gate_critical_field"},
            verification_spec={"declared_review_fields": []},
            package={"declared_review_fields": []},
        )
        self.assertEqual(delta, ReviewDelta.UNDECLARED)

    def test_EC_M04_undeclared_requirement_mutant_is_killed(self):
        class P32RepairMutant:
            def classify(self, **kwargs):
                return "P32_REPAIR"

        with self.assertRaises(AssertionError):
            self._assert_undeclared_oracle(P32RepairMutant())
        self._assert_undeclared_oracle(ReviewContractDiffer())

    def _assert_no_gate_output(self, evaluator, evidence_ref):
        result = evaluator.evaluate(
            verification_spec=verification_spec(),
            obligation_set={"obligations": [deterministic_obligation()]},
            evidence_input_refs=[evidence_ref],
            evaluator_version="0.1",
        )
        serialized = repr(result.proof_evaluation) + repr(result.verification_summary)
        self.assertNotIn("P34", serialized)
        self.assertNotIn("GATE_PASS", serialized)
        self.assertNotIn("gate_verdict", serialized)

    def test_EC_M13_gate_pass_mutant_is_killed(self):
        class GatePassMutant(ProofEvaluator):
            def evaluate(self, **kwargs):
                result = super().evaluate(**kwargs)
                mutated = dict(result.proof_evaluation)
                mutated["gate_verdict"] = "PASS"
                return EvaluationResult(mutated, result.verification_summary)

        evidence_ref, resolver = resolver_binding()
        with self.assertRaises(AssertionError):
            self._assert_no_gate_output(GatePassMutant(resolver=resolver), evidence_ref)
        self._assert_no_gate_output(ProofEvaluator(resolver=resolver), evidence_ref)

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
