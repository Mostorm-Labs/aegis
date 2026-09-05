import importlib
import importlib.util
import unittest

from tools.aegis_control.canonical import canonical_digest, canonical_dumps


class ProofDomainSpecTests(unittest.TestCase):
    def _module(self, name):
        try:
            spec = importlib.util.find_spec(name)
        except ModuleNotFoundError:
            spec = None
        if spec is None:
            self.fail(f"required VP-I01 module is missing: {name}")
        return importlib.import_module(name)

    def _verification_spec(self, mode="REVIEW_DECLARED"):
        requirement_ids = ["REQ-1"]
        return {
            "schema_version": "0.1",
            "id": "vs-vp-i01",
            "scope": "aegis/verification-productization",
            "version": "v0.1",
            "authority_refs": ["authority://vp-i01"],
            "coverage_basis": {
                "authority_ref": "authority://vp-i01",
                "authority_version": "v0.1",
                "authority_digest": canonical_digest({"authority": "vp-i01"}),
                "source_ref": "git:674e01737621621b8131e35f83313fb0154a9f6d",
                "mode": mode,
                "requirements": [{"id": "REQ-1", "ref": "requirement://REQ-1"}],
                "requirement_set_digest": canonical_digest(requirement_ids),
            },
            "claims": [
                {
                    "id": "ECV-C02",
                    "statement": "Floating accepted dependencies never cross P32 unresolved.",
                    "requirement_refs": ["REQ-1"],
                    "proof_contract_id": "PC-ECV-C02",
                }
            ],
            "proof_contracts": [
                {
                    "id": "PC-ECV-C02",
                    "claim_id": "ECV-C02",
                    "mode": "EXPLICIT",
                    "profile_ref": {"id": "REFERENCE", "version": "v0.1"},
                    "resolved_obligations": [
                        {
                            "kind": "INVARIANT",
                            "source_key": "invariant:exact-dependency",
                            "evaluation_mode": "DETERMINISTIC",
                            "required_evidence_types": ["PREFLIGHT_RESULT"],
                            "pass_condition": "floating dependency is rejected before P32",
                        }
                    ],
                }
            ],
            "extensions": {},
        }

    def test_proof_codec_reuses_control_plane_canonicalization(self):
        domain = self._module("tools.aegis_proof.domain")
        value = {"b": 2, "a": 1}
        self.assertEqual(domain.ProofCodec.canonicalize(value), canonical_dumps(value))
        self.assertEqual(domain.ProofCodec.digest(value), canonical_digest(value))

    def test_evidence_input_identity_is_exact_and_producer_bound(self):
        domain = self._module("tools.aegis_proof.domain")
        digest = canonical_digest({"evidence": 1})
        identity = domain.EvidenceInputIdentity.from_materialized_artifact(
            evidence_id="ev-1",
            ref="artifact://123",
            digest=digest,
            producer_class="DETERMINISTIC_COLLECTOR",
        )
        self.assertEqual(
            identity,
            {
                "evidence_id": "ev-1",
                "ref": "artifact://123",
                "digest": digest,
                "producer_class": "DETERMINISTIC_COLLECTOR",
            },
        )
        with self.assertRaises(domain.ProofValidationError):
            domain.EvidenceInputIdentity.from_materialized_artifact(
                evidence_id="ev-1",
                ref="artifact://123",
                digest="not-a-digest",
                producer_class="DETERMINISTIC_COLLECTOR",
            )

    def test_validator_rejects_claim_reference_outside_coverage_basis(self):
        spec_module = self._module("tools.aegis_proof.spec")
        candidate = self._verification_spec()
        candidate["claims"][0]["requirement_refs"] = ["REQ-MISSING"]
        result = spec_module.VerificationSpecValidator.validate(candidate)
        self.assertFalse(result.valid)
        self.assertIn("CLAIM_REQUIREMENT_OUTSIDE_COVERAGE_BASIS", {f.code for f in result.findings})

    def test_review_declared_generates_exactly_one_coverage_completeness_obligation(self):
        spec_module = self._module("tools.aegis_proof.spec")
        obligations_module = self._module("tools.aegis_proof.obligations")
        candidate = self._verification_spec("REVIEW_DECLARED")
        validation = spec_module.VerificationSpecValidator.validate(candidate)
        self.assertTrue(validation.valid, validation.findings)
        result = obligations_module.ObligationGenerator.generate(candidate, generator_version="0.1")
        coverage = [o for o in result.obligations if o["subject"]["kind"] == "COVERAGE_BASIS"]
        self.assertEqual(len(coverage), 1)
        self.assertEqual(coverage[0]["kind"], "COVERAGE_COMPLETENESS")
        self.assertEqual(coverage[0]["source_key"], "coverage-completeness")
        self.assertEqual(coverage[0]["evaluation_mode"], "REVIEW_REQUIRED")
        self.assertNotIn("status", coverage[0])
        self.assertEqual(result.obligation_count, len(result.obligations))

    def test_exact_set_does_not_generate_coverage_completeness_obligation(self):
        obligations_module = self._module("tools.aegis_proof.obligations")
        result = obligations_module.ObligationGenerator.generate(
            self._verification_spec("EXACT_SET"), generator_version="0.1"
        )
        self.assertFalse(any(o["kind"] == "COVERAGE_COMPLETENESS" for o in result.obligations))

    def test_obligation_identity_is_deterministic_for_same_semantic_key(self):
        domain = self._module("tools.aegis_proof.domain")
        key = domain.ObligationIdentityCodec.semantic_key(
            verification_spec_digest=canonical_digest(self._verification_spec()),
            subject_kind="CLAIM",
            subject_id="ECV-C02|PC-ECV-C02",
            obligation_kind="INVARIANT",
            source_key="invariant:exact-dependency",
        )
        first = domain.ObligationIdentityCodec.id_from_key(key)
        second = domain.ObligationIdentityCodec.id_from_key(dict(key))
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("obl_"))


if __name__ == "__main__":
    unittest.main()
