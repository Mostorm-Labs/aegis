import importlib
import importlib.util
import unittest
from unittest.mock import patch

from tools.aegis_control.canonical import (
    CanonicalValidationError,
    canonical_digest,
    validate_record,
)


def exact_ref(object_type, ident):
    return {
        "object_type": object_type,
        "id": ident,
        "ref": f"git:{ident}",
        "identity": {"scheme": "git-sha", "value": "a" * 40},
    }


def trusted_basis():
    value = {
        "authority_refs": [exact_ref("AUTHORITY", "authority-vp")],
        "contract_refs": [exact_ref("CONTRACT", "contract-vp")],
        "verification_refs": [exact_ref("VERIFICATION_SPEC", "spec-vp")],
        "accepted_fact_refs": [],
    }
    value["basis_digest"] = canonical_digest(value)
    return value


def policy_binding():
    value = {
        "gate_policy_ref": exact_ref("CONTRACT", "gate-policy"),
        "control_autonomy": "REVIEW_GUARDED",
        "repair_policy": {
            "allowed_classes": ["IMPLEMENTATION_DEFECT"],
            "max_attempts": 1,
            "require_reverification": True,
            "require_fresh_independent_review": True,
            "escalation_conditions": ["AUTHORITY_CONFLICT"],
        },
    }
    value["policy_digest"] = canonical_digest(value)
    return value


def valid_package():
    record = {
        "schema_version": "0.2",
        "kind": "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE",
        "id_scheme": "verification-bound-package-v0.2",
        "id": "pkg_vp_i01",
        "record_revision": 1,
        "recorded_at": "2026-09-05T00:00:00Z",
        "control_lane_id": "lane_vp_i01",
        "work_scope_ref": {
            "id_scheme": "control-work-scope-v0.2",
            "id": "ws_vp_i01",
            "child_work_binding": None,
        },
        "trusted_basis": trusted_basis(),
        "scope": {
            "scope_id": "VP-I01_EXACT_CONTRACT_AND_PACKAGE_PREFLIGHT",
            "scope_contract_ref": exact_ref("CONTRACT", "scope-vp-i01"),
        },
        "verification_binding": {
            "verification_spec_ref": exact_ref("VERIFICATION_SPEC", "ecv0"),
            "obligation_set_ref": None,
            "acceptance_oracle_refs": [exact_ref("CONTRACT", "O-EC-PREFLIGHT")],
            "evidence_compilation_contract_ref": exact_ref("CONTRACT", "evidence-contract"),
        },
        "policy_binding": policy_binding(),
        "task_anchor": {"revision": "b" * 40, "relation": "ancestor"},
        "extensions": {},
    }
    record["package_digest"] = canonical_digest(record)
    return record


class PackagePreflightTests(unittest.TestCase):
    def _module(self, name):
        try:
            spec = importlib.util.find_spec(name)
        except ModuleNotFoundError:
            spec = None
        if spec is None:
            self.fail(f"required VP-I01 module is missing: {name}")
        return importlib.import_module(name)

    def _floating_projection(self):
        return {
            "verification_spec_ref": {
                "object_type": "VERIFICATION_SPEC",
                "id": "accepted A4",
                "ref": "latest Gate",
                "identity": {"scheme": "label", "value": "current result"},
            },
            "obligation_set_ref": None,
            "obligation_set_required": False,
            "scope_contract_ref": exact_ref("CONTRACT", "scope"),
            "acceptance_oracle_refs": [exact_ref("CONTRACT", "oracle")],
            "evidence_compilation_contract_ref": exact_ref("CONTRACT", "evidence-contract"),
            "trusted_basis": trusted_basis(),
            "task_anchor": {"revision": "c" * 40, "relation": "ancestor"},
        }

    def _assert_ec_s02_rejected(self, package_module):
        result = package_module.PackageBindingPreflight.check(self._floating_projection())
        self.assertFalse(result.ok)
        self.assertIn(package_module.PreflightCode.FLOATING_DEPENDENCY, {f.code for f in result.findings})

    def _future_self_nodes(self):
        return [
            {"id": "artifact_content", "phase": "EVIDENCE_COMPILE", "depends_on": ["artifact_identity"]},
            {"id": "artifact_identity", "phase": "ARTIFACT_MATERIALIZE", "depends_on": ["artifact_content"]},
        ]

    def _assert_ec_s03_rejected(self, package_module):
        result = package_module.EvidenceContractPreflight.check(self._future_self_nodes())
        self.assertFalse(result.ok)
        self.assertIn(
            package_module.PreflightCode.STRUCTURALLY_UNSATISFIABLE,
            {f.code for f in result.findings},
        )

    def test_canonical_package_rejects_empty_trusted_basis(self):
        record = valid_package()
        record["trusted_basis"] = {}
        record["package_digest"] = canonical_digest(record, self_digest_field="package_digest")
        with self.assertRaisesRegex(CanonicalValidationError, "TrustedBasis"):
            validate_record(record)

    def test_canonical_package_accepts_valid_nested_contract(self):
        record = valid_package()
        record["package_digest"] = canonical_digest(record, self_digest_field="package_digest")
        validate_record(record)

    def test_canonical_package_rejects_wrong_verification_ref_type(self):
        record = valid_package()
        record["verification_binding"]["verification_spec_ref"] = exact_ref("CONTRACT", "not-spec")
        record["package_digest"] = canonical_digest(record, self_digest_field="package_digest")
        with self.assertRaisesRegex(CanonicalValidationError, "VERIFICATION_SPEC"):
            validate_record(record)

    def test_canonical_package_rejects_wrong_package_digest(self):
        record = valid_package()
        record["package_digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(CanonicalValidationError, "package_digest mismatch"):
            validate_record(record)

    def test_ec_s02_floating_dependency_is_rejected_before_p32(self):
        package_module = self._module("tools.aegis_proof.package")
        self._assert_ec_s02_rejected(package_module)

    def test_ec_m02_floating_dependency_mutant_is_killed(self):
        package_module = self._module("tools.aegis_proof.package")
        original_check = package_module.PackageBindingPreflight.check

        def admit_floating_dependency(projection):
            original = original_check(projection)
            findings = tuple(
                finding
                for finding in original.findings
                if finding.code != package_module.PreflightCode.FLOATING_DEPENDENCY
            )
            return package_module.PreflightResult(not findings, findings)

        with patch.object(
            package_module.PackageBindingPreflight,
            "check",
            side_effect=admit_floating_dependency,
        ):
            mutant_result = package_module.PackageBindingPreflight.check(self._floating_projection())
            self.assertTrue(mutant_result.ok, mutant_result.findings)
            with self.assertRaises(AssertionError):
                self._assert_ec_s02_rejected(package_module)

    def test_ec_s03_future_self_materialization_cycle_is_structurally_unsatisfiable(self):
        package_module = self._module("tools.aegis_proof.package")
        self._assert_ec_s03_rejected(package_module)

    def test_ec_m03_future_self_mutant_is_killed(self):
        package_module = self._module("tools.aegis_proof.package")
        original_check = package_module.EvidenceContractPreflight.check
        suppressed = {
            package_module.PreflightCode.FUTURE_PHASE_DEPENDENCY,
            package_module.PreflightCode.STRUCTURALLY_UNSATISFIABLE,
        }

        def admit_future_self(nodes):
            original = original_check(nodes)
            findings = tuple(finding for finding in original.findings if finding.code not in suppressed)
            return package_module.PreflightResult(not findings, findings)

        with patch.object(
            package_module.EvidenceContractPreflight,
            "check",
            side_effect=admit_future_self,
        ):
            mutant_result = package_module.EvidenceContractPreflight.check(self._future_self_nodes())
            self.assertTrue(mutant_result.ok, mutant_result.findings)
            with self.assertRaises(AssertionError):
                self._assert_ec_s03_rejected(package_module)

    def test_p34_judgment_cannot_be_required_as_p32_deterministic_input(self):
        package_module = self._module("tools.aegis_proof.package")
        nodes = [
            {"id": "executor_evidence", "phase": "P32_EXECUTION", "depends_on": ["gate_judgment"]},
            {"id": "gate_judgment", "phase": "P34_REVIEW", "depends_on": []},
        ]
        result = package_module.EvidenceContractPreflight.check(nodes)
        self.assertFalse(result.ok)
        self.assertIn(
            package_module.PreflightCode.FUTURE_PHASE_DEPENDENCY,
            {f.code for f in result.findings},
        )


if __name__ == "__main__":
    unittest.main()
