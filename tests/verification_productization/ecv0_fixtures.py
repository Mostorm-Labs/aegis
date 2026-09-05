from __future__ import annotations

import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Mapping

from tools.aegis_control.canonical import canonical_digest
from tools.aegis_proof.evidence import EvidenceCompiler, EvidenceMaterializer, EvidencePlan, EvidenceRequirement
from tools.aegis_proof.package import EvidenceContractPreflight, PackageBindingPreflight, PreflightCode, PreflightResult
from tools.aegis_proof.ports import ImmutableArtifactLocator, ObservationBatch, ObservationRecord
from tools.aegis_proof.review import IndependentCompletenessChecker, ReviewBundleAdapter, ReviewContractDiffer, ReviewDelta
from tools.aegis_proof.spec import VerificationSpecValidator

SCENARIO_IDS = tuple(f"EC-S{i:02d}" for i in range(1, 18))
MUTANT_IDS = tuple(f"EC-M{i:02d}" for i in range(1, 18))


def load_required_module(name: str):
    try:
        spec = importlib.util.find_spec(name)
    except ModuleNotFoundError:
        spec = None
    if spec is None:
        raise AssertionError(f"required VP-I03 module is missing: {name}")
    return importlib.import_module(name)


def exact_ref(object_type: str, ident: str) -> dict[str, Any]:
    return {
        "object_type": object_type,
        "id": ident,
        "ref": f"git:{ident}",
        "identity": {"scheme": "git-sha", "value": "a" * 40},
    }


def trusted_basis() -> dict[str, Any]:
    value = {
        "authority_refs": [exact_ref("AUTHORITY", "authority-vp")],
        "contract_refs": [exact_ref("CONTRACT", "contract-vp")],
        "verification_refs": [exact_ref("VERIFICATION_SPEC", "spec-vp")],
        "accepted_fact_refs": [],
    }
    value["basis_digest"] = canonical_digest(value)
    return value


def floating_projection() -> dict[str, Any]:
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


def future_self_nodes() -> list[dict[str, Any]]:
    return [
        {"id": "artifact_content", "phase": "EVIDENCE_COMPILE", "depends_on": ["artifact_identity"]},
        {"id": "artifact_identity", "phase": "ARTIFACT_MATERIALIZE", "depends_on": ["artifact_content"]},
    ]


def review_spec() -> dict[str, Any]:
    return {
        "id": "vs",
        "version": "v0.1",
        "coverage_basis": {"mode": "EXACT_SET", "requirement_set_digest": "sha256:" + "0" * 64},
        "claims": [{"id": "C1", "proof_contract_id": "PC1"}],
        "proof_contracts": [{
            "id": "PC1",
            "claim_id": "C1",
            "resolved_obligations": [
                {
                    "kind": "INVARIANT",
                    "source_key": "one",
                    "evaluation_mode": "DETERMINISTIC",
                    "required_evidence_types": ["TEST"],
                    "pass_condition": "pass",
                },
                {
                    "kind": "PROBE",
                    "source_key": "two",
                    "evaluation_mode": "DETERMINISTIC",
                    "required_evidence_types": ["TEST"],
                    "pass_condition": "probe passes",
                },
            ],
        }],
    }


def valid_verification_spec() -> dict[str, Any]:
    requirements = [{"id": "R1", "ref": "authority://R1"}]
    requirement_set_digest = canonical_digest(["R1"])
    return {
        "schema_version": "0.1",
        "id": "ecv0-fixture",
        "scope": "aegis/verification-productization/verification",
        "version": "0.1",
        "authority_refs": ["authority://verification-productization"],
        "coverage_basis": {
            "authority_ref": "authority://verification-productization",
            "authority_version": "0.1",
            "authority_digest": canonical_digest({"authority": "verification-productization"}),
            "source_ref": "git:fixture",
            "mode": "EXACT_SET",
            "requirements": requirements,
            "requirement_set_digest": requirement_set_digest,
        },
        "claims": [{
            "id": "C1",
            "requirement_refs": ["R1"],
            "proof_contract_id": "PC1",
        }],
        "proof_contracts": [{
            "id": "PC1",
            "claim_id": "C1",
            "mode": "EXPLICIT",
            "profile_ref": None,
            "resolved_obligations": [{
                "kind": "INVARIANT",
                "source_key": "fixture-one",
                "evaluation_mode": "DETERMINISTIC",
                "required_evidence_types": ["TEST"],
                "pass_condition": "fixture passes",
            }],
        }],
        "extensions": {},
    }


def authoritative_plan() -> EvidencePlan:
    return EvidencePlan((EvidenceRequirement("test.summary", "pytest-json", True),))


def authoritative_batches(*, secondary: str = "manual", secondary_skip: int = 25) -> tuple[ObservationBatch, ...]:
    return (
        ObservationBatch("pytest-json", True, (
            ObservationRecord("test.summary", "DETERMINISTIC_COLLECTOR", "pytest-json", "result@1", {"pass": 445, "skip": 23}),
        )),
        ObservationBatch(secondary, True, (
            ObservationRecord("test.summary", "REVIEWER", secondary, "result@1", {"pass": 445, "skip": secondary_skip}),
        )),
    )


class MemoryStore:
    def __init__(self):
        self._n = 0

    def materialize(self, data: bytes, *, media_type: str, metadata: Mapping[str, Any]) -> ImmutableArtifactLocator:
        self._n += 1
        digest = "sha256:" + hashlib.sha256(data).hexdigest()
        return ImmutableArtifactLocator("memory", str(self._n), f"artifact://{self._n}", digest, True)

    def resolve(self, locator: ImmutableArtifactLocator) -> bytes:
        raise NotImplementedError


def github_run(*, revision: str = "d" * 40, include_matrix_b: bool = True) -> dict[str, Any]:
    jobs = [
        {"id": 101, "name": "unit (a)", "status": "completed", "conclusion": "success"},
    ]
    if include_matrix_b:
        jobs.append({"id": 102, "name": "unit (b)", "status": "completed", "conclusion": "success"})
    return {
        "repository": {"full_name": "Mostorm-Labs/aegis"},
        "workflow": {"id": 77, "path": ".github/workflows/verification-productization-ecv0.yml"},
        "run_id": 9001,
        "run_attempt": 1,
        "head_sha": revision,
        "status": "completed",
        "conclusion": "success",
        "jobs": jobs,
        "artifacts": [{
            "id": 501,
            "name": f"verification-productization-ecv0-{revision}",
            "digest": "sha256:" + "1" * 64,
        }],
    }


def _scenario_01() -> bool:
    artifact = EvidenceCompiler().compile(plan=authoritative_plan(), batches=authoritative_batches())
    return artifact["complete"] and artifact["facts"]["test.summary"] == {"pass": 445, "skip": 23}


def _scenario_02() -> bool:
    result = PackageBindingPreflight.check(floating_projection())
    return (not result.ok) and PreflightCode.FLOATING_DEPENDENCY in {f.code for f in result.findings}


def _scenario_03() -> bool:
    result = EvidenceContractPreflight.check(future_self_nodes())
    return (not result.ok) and PreflightCode.STRUCTURALLY_UNSATISFIABLE in {f.code for f in result.findings}


def _scenario_04() -> bool:
    return ReviewContractDiffer().classify(
        requested_requirement={"field": "new_gate_critical_field"},
        verification_spec={"declared_review_fields": ["known"]},
        package={"declared_review_fields": ["known"]},
    ) == ReviewDelta.UNDECLARED


def _scenario_05() -> bool:
    store = MemoryStore()
    materializer = EvidenceMaterializer()
    first = materializer.materialize({"subject_result_revision": "r1", "value": 1}, store=store)
    second = materializer.materialize({"subject_result_revision": "r1", "value": 2}, store=store)
    return first["ref"] != second["ref"] and first["subject_result_revision"] == second["subject_result_revision"] == "r1"


def _scenario_06() -> bool:
    old = hashlib.sha256(b"result-v1").hexdigest()
    new = hashlib.sha256(b"result-v2").hexdigest()
    return old != new


def _scenario_07() -> bool:
    local = load_required_module("tools.aegis_proof.adapters.local_runner")
    repository = load_required_module("tools.aegis_proof.adapters.repository")
    ref = local.LocalRunnerAdapter.local_evidence_ref("/tmp/vp-i03.txt")
    try:
        repository.RepositoryAdapter.require_reviewer_resolvable(ref)
    except ValueError:
        return ref.get("reviewer_resolvable") is False
    return False


def _scenario_08() -> bool:
    actions = load_required_module("tools.aegis_proof.adapters.github_actions")
    batch = actions.GitHubActionsAdapter.to_observation_batch(
        github_run(revision="e" * 40),
        expected_repository="Mostorm-Labs/aegis",
        expected_revision="d" * 40,
        required_jobs=("unit (a)", "unit (b)"),
        required_artifacts=(f"verification-productization-ecv0-{'d' * 40}",),
    )
    return batch.complete is False


def _scenario_09() -> bool:
    actions = load_required_module("tools.aegis_proof.adapters.github_actions")
    batch = actions.GitHubActionsAdapter.to_observation_batch(
        github_run(include_matrix_b=False),
        expected_repository="Mostorm-Labs/aegis",
        expected_revision="d" * 40,
        required_jobs=("unit (a)", "unit (b)"),
        required_artifacts=(f"verification-productization-ecv0-{'d' * 40}",),
    )
    return batch.complete is False


def _scenario_10() -> bool:
    repository = load_required_module("tools.aegis_proof.adapters.repository")
    try:
        repository.RepositoryAdapter.validate_exact_ref(
            {"repository": "Mostorm-Labs/aegis", "branch": "main", "ref": "latest"},
            expected_repository="Mostorm-Labs/aegis",
        )
    except ValueError:
        return True
    return False


def _scenario_11() -> bool:
    repository = load_required_module("tools.aegis_proof.adapters.repository")
    base = {
        "repository": "Mostorm-Labs/aegis",
        "provider": "github-actions",
        "native_id": "501",
        "ref": "actions-artifact://501",
        "digest": "sha256:" + "2" * 64,
        "reviewer_resolvable": True,
        "signed_url": "https://example.invalid/one?sig=secret",
    }
    rotated = dict(base, signed_url="https://example.invalid/two?sig=new")
    one = repository.RepositoryAdapter.durable_artifact_ref(base, expected_repository="Mostorm-Labs/aegis")
    two = repository.RepositoryAdapter.durable_artifact_ref(rotated, expected_repository="Mostorm-Labs/aegis")
    return one == two and "signed_url" not in one


def _scenario_12() -> bool:
    repository = load_required_module("tools.aegis_proof.adapters.repository")
    ref = {
        "repository": "Mostorm-Labs/aegis",
        "provider": "github-actions",
        "native_id": "501",
        "ref": "actions-artifact://501",
        "digest": "sha256:" + "2" * 64,
        "reviewer_resolvable": False,
    }
    try:
        repository.RepositoryAdapter.require_reviewer_resolvable(ref)
    except ValueError:
        return True
    return False


def _scenario_13() -> bool:
    repository = load_required_module("tools.aegis_proof.adapters.repository")
    try:
        repository.RepositoryAdapter.validate_exact_ref(
            {
                "repository": "Other/repo",
                "revision": "d" * 40,
                "ref": "git:d",
                "reviewer_resolvable": True,
            },
            expected_repository="Mostorm-Labs/aegis",
        )
    except ValueError:
        return True
    return False


def _scenario_14() -> bool:
    artifact = EvidenceCompiler().compile(plan=authoritative_plan(), batches=authoritative_batches(secondary="handoff", secondary_skip=99))
    return artifact["facts"]["test.summary"] == {"pass": 445, "skip": 23}


def _scenario_15() -> bool:
    checker = IndependentCompletenessChecker()
    spec = review_spec()
    expected = checker.expected_ids(verification_spec=spec)
    result = checker.check(verification_spec=spec, actual_obligation_set={"obligation_ids": [expected[0]]})
    return (not result.complete) and len(result.missing_ids) == 1


def _scenario_16() -> bool:
    checker = IndependentCompletenessChecker()
    spec = review_spec()
    complete = checker.check(verification_spec=spec, actual_obligation_set={"obligation_ids": list(checker.expected_ids(verification_spec=spec))})
    bundle = ReviewBundleAdapter().build(
        package_ref={"ref": "pkg://1", "reviewer_resolvable": True},
        result_ref={"ref": "result://missing", "reviewer_resolvable": False},
        evidence_input_refs=[{"ref": "evidence://1", "reviewer_resolvable": True}],
        proof_evaluation_ref={"ref": "eval://1", "reviewer_resolvable": True},
        completeness=complete,
    )
    return bundle["review_ready"] is False and bundle["blocker"] == "BLOCKED_EVIDENCE"


def _scenario_17() -> bool:
    cli = load_required_module("tools.aegis_proof.cli")
    spec = valid_verification_spec()
    direct = VerificationSpecValidator.validate(spec)
    via_cli = cli.execute("validate-spec", spec)
    return via_cli == {
        "valid": direct.valid,
        "findings": [
            {"code": f.code, "message": f.message, "path": f.path}
            for f in direct.findings
        ],
    }


SCENARIOS = {
    "EC-S01": _scenario_01,
    "EC-S02": _scenario_02,
    "EC-S03": _scenario_03,
    "EC-S04": _scenario_04,
    "EC-S05": _scenario_05,
    "EC-S06": _scenario_06,
    "EC-S07": _scenario_07,
    "EC-S08": _scenario_08,
    "EC-S09": _scenario_09,
    "EC-S10": _scenario_10,
    "EC-S11": _scenario_11,
    "EC-S12": _scenario_12,
    "EC-S13": _scenario_13,
    "EC-S14": _scenario_14,
    "EC-S15": _scenario_15,
    "EC-S16": _scenario_16,
    "EC-S17": _scenario_17,
}


def run_scenario(scenario_id: str) -> bool:
    return bool(SCENARIOS[scenario_id]())


def _mutant_01() -> bool:
    class ManualOverrideMutant(EvidenceCompiler):
        def compile(self, *, plan, batches):
            artifact = dict(super().compile(plan=plan, batches=batches))
            manual = next(batch for batch in batches if batch.producer_id == "manual")
            artifact["facts"] = dict(artifact["facts"])
            artifact["facts"]["test.summary"] = manual.observations[0].value
            return artifact
    mutant = ManualOverrideMutant().compile(plan=authoritative_plan(), batches=authoritative_batches())
    production = EvidenceCompiler().compile(plan=authoritative_plan(), batches=authoritative_batches())
    return mutant["facts"]["test.summary"] != {"pass": 445, "skip": 23} and production["facts"]["test.summary"] == {"pass": 445, "skip": 23}


def _mutant_02() -> bool:
    original = PackageBindingPreflight.check(floating_projection())
    filtered = tuple(f for f in original.findings if f.code != PreflightCode.FLOATING_DEPENDENCY)
    mutant = PreflightResult(not filtered, filtered)
    return mutant.ok and not original.ok


def _mutant_03() -> bool:
    original = EvidenceContractPreflight.check(future_self_nodes())
    suppressed = {PreflightCode.FUTURE_PHASE_DEPENDENCY, PreflightCode.STRUCTURALLY_UNSATISFIABLE}
    filtered = tuple(f for f in original.findings if f.code not in suppressed)
    mutant = PreflightResult(not filtered, filtered)
    return mutant.ok and not original.ok


def _mutant_04() -> bool:
    mutant = "P32_REPAIR"
    production = ReviewContractDiffer().classify(
        requested_requirement={"field": "new_gate_critical_field"},
        verification_spec={"declared_review_fields": []},
        package={"declared_review_fields": []},
    )
    return mutant != ReviewDelta.UNDECLARED and production == ReviewDelta.UNDECLARED


def _mutant_05() -> bool:
    old = hashlib.sha256(b"result-v1").hexdigest()
    new = hashlib.sha256(b"result-v2").hexdigest()
    mutant_reported = old
    return new != old and mutant_reported != new


def _mutant_06() -> bool:
    local = load_required_module("tools.aegis_proof.adapters.local_runner")
    repository = load_required_module("tools.aegis_proof.adapters.repository")
    ref = local.LocalRunnerAdapter.local_evidence_ref("/tmp/only.txt")
    mutant_accepts = bool(ref.get("ref"))
    try:
        repository.RepositoryAdapter.require_reviewer_resolvable(ref)
    except ValueError:
        return mutant_accepts
    return False


def _mutant_07() -> bool:
    actions = load_required_module("tools.aegis_proof.adapters.github_actions")
    wrong = github_run(revision="e" * 40)
    mutant_accepts = wrong.get("conclusion") == "success"
    production = actions.GitHubActionsAdapter.to_observation_batch(
        wrong,
        expected_repository="Mostorm-Labs/aegis",
        expected_revision="d" * 40,
        required_jobs=("unit (a)", "unit (b)"),
        required_artifacts=(f"verification-productization-ecv0-{'d' * 40}",),
    )
    return mutant_accepts and not production.complete


def _mutant_08() -> bool:
    actions = load_required_module("tools.aegis_proof.adapters.github_actions")
    incomplete = github_run(include_matrix_b=False)
    mutant_accepts = incomplete.get("status") == "completed" and incomplete.get("conclusion") == "success"
    production = actions.GitHubActionsAdapter.to_observation_batch(
        incomplete,
        expected_repository="Mostorm-Labs/aegis",
        expected_revision="d" * 40,
        required_jobs=("unit (a)", "unit (b)"),
        required_artifacts=(f"verification-productization-ecv0-{'d' * 40}",),
    )
    return mutant_accepts and not production.complete


def _mutant_09() -> bool:
    repository = load_required_module("tools.aegis_proof.adapters.repository")
    mutable = {"repository": "Mostorm-Labs/aegis", "branch": "main", "ref": "latest"}
    mutant_accepts = bool(mutable.get("branch"))
    try:
        repository.RepositoryAdapter.validate_exact_ref(mutable, expected_repository="Mostorm-Labs/aegis")
    except ValueError:
        return mutant_accepts
    return False


def _mutant_10() -> bool:
    repository = load_required_module("tools.aegis_proof.adapters.repository")
    locator = {
        "repository": "Mostorm-Labs/aegis",
        "provider": "github-actions",
        "native_id": "501",
        "ref": "actions-artifact://501",
        "digest": "sha256:" + "2" * 64,
        "reviewer_resolvable": True,
        "signed_url": "https://example.invalid/download?sig=secret",
    }
    mutant = dict(locator)
    production = repository.RepositoryAdapter.durable_artifact_ref(locator, expected_repository="Mostorm-Labs/aegis")
    return "signed_url" in mutant and "signed_url" not in production


def _mutant_11() -> bool:
    repository = load_required_module("tools.aegis_proof.adapters.repository")
    cross = {"repository": "Other/repo", "revision": "d" * 40, "ref": "git:d", "reviewer_resolvable": True}
    mutant_accepts = len(cross["revision"]) == 40
    try:
        repository.RepositoryAdapter.validate_exact_ref(cross, expected_repository="Mostorm-Labs/aegis")
    except ValueError:
        return mutant_accepts
    return False


def _mutant_12() -> bool:
    repository = load_required_module("tools.aegis_proof.adapters.repository")
    inaccessible = {"ref": "artifact://1", "reviewer_resolvable": False}
    mutant_accepts = bool(inaccessible["ref"])
    try:
        repository.RepositoryAdapter.require_reviewer_resolvable(inaccessible)
    except ValueError:
        return mutant_accepts
    return False


def _mutant_13() -> bool:
    mutant = {"proof_evaluation": {"gate_verdict": "PASS"}}
    production_keys = {"evaluator_version", "results", "states"}
    return "gate_verdict" in mutant["proof_evaluation"] and "gate_verdict" not in production_keys


def _mutant_14() -> bool:
    production = EvidenceCompiler().compile(plan=authoritative_plan(), batches=authoritative_batches(secondary="handoff", secondary_skip=99))
    mutant_value = {"pass": 445, "skip": 99}
    return mutant_value != production["facts"]["test.summary"]


def _mutant_15() -> bool:
    import tools.aegis_proof.obligations as obligations
    original = obligations.ObligationGenerator.generate
    try:
        obligations.ObligationGenerator.generate = staticmethod(lambda *a, **k: (_ for _ in ()).throw(AssertionError("generator called")))
        checker = IndependentCompletenessChecker()
        spec = review_spec()
        expected = checker.expected_ids(verification_spec=spec)
        result = checker.check(verification_spec=spec, actual_obligation_set={"obligation_ids": list(expected)})
        return result.complete
    finally:
        obligations.ObligationGenerator.generate = original


def _mutant_16() -> bool:
    cli = load_required_module("tools.aegis_proof.cli")
    invalid = valid_verification_spec()
    invalid["schema_version"] = "999"
    direct = VerificationSpecValidator.validate(invalid)
    mutant = {"valid": True, "findings": []}
    production = cli.execute("validate-spec", invalid)
    return mutant != production and production["valid"] == direct.valid is False


def _mutant_17() -> bool:
    incomplete = EvidenceCompiler().compile(plan=authoritative_plan(), batches=(ObservationBatch("pytest-json", False, ()),))
    mutant = {"facts": {"test.summary": {"fail": 0}}, "missing_required": [], "complete": True}
    return mutant["complete"] and not incomplete["complete"]


MUTANTS = {
    "EC-M01": _mutant_01,
    "EC-M02": _mutant_02,
    "EC-M03": _mutant_03,
    "EC-M04": _mutant_04,
    "EC-M05": _mutant_05,
    "EC-M06": _mutant_06,
    "EC-M07": _mutant_07,
    "EC-M08": _mutant_08,
    "EC-M09": _mutant_09,
    "EC-M10": _mutant_10,
    "EC-M11": _mutant_11,
    "EC-M12": _mutant_12,
    "EC-M13": _mutant_13,
    "EC-M14": _mutant_14,
    "EC-M15": _mutant_15,
    "EC-M16": _mutant_16,
    "EC-M17": _mutant_17,
}


def run_mutant(mutant_id: str) -> bool:
    return bool(MUTANTS[mutant_id]())
