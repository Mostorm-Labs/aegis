from __future__ import annotations

import json
import sys
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .evidence import EvidenceCompiler, EvidencePlan, EvidenceRequirement
from .evaluation import ProofEvaluator
from .obligations import ObligationGenerator
from .package import EvidenceContractPreflight, P31TaskProjector, PackageBindingPreflight
from .ports import ObservationBatch, ObservationRecord
from .review import IndependentCompletenessChecker, ReviewContractDiffer
from .spec import VerificationSpecValidator


COMMANDS = {
    "validate-spec",
    "build-obligations",
    "project-package",
    "preflight-package",
    "preflight-evidence",
    "compile-evidence",
    "evaluate",
    "review-check",
}


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _plain(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if hasattr(value, "value") and value.__class__.__module__ == "enum":
        return value.value
    try:
        from enum import Enum
        if isinstance(value, Enum):
            return value.value
    except Exception:
        pass
    return value


def _preflight_payload(result) -> dict[str, Any]:
    return {
        "ok": result.ok,
        "findings": [
            {
                "code": finding.code.value,
                "message": finding.message,
                "subject": finding.subject,
            }
            for finding in result.findings
        ],
    }


class _MappingResolver:
    def __init__(self, resolved: Any):
        self._by_ref: dict[str, Mapping[str, Any]] = {}
        if isinstance(resolved, list):
            for item in resolved:
                if isinstance(item, Mapping) and isinstance(item.get("ref"), str):
                    self._by_ref[item["ref"]] = item
        elif isinstance(resolved, Mapping):
            for key, item in resolved.items():
                if isinstance(item, Mapping):
                    self._by_ref[str(key)] = item

    def resolve(self, ref: Mapping[str, Any]) -> Mapping[str, Any]:
        key = ref.get("ref")
        if key not in self._by_ref:
            raise KeyError(key)
        return self._by_ref[str(key)]


def execute(command: str, payload: Any) -> Any:
    if command not in COMMANDS:
        raise ValueError(f"unknown command: {command}")

    if command == "validate-spec":
        result = VerificationSpecValidator.validate(payload)
        return {
            "valid": result.valid,
            "findings": [
                {"code": finding.code, "message": finding.message, "path": finding.path}
                for finding in result.findings
            ],
        }

    if not isinstance(payload, Mapping):
        raise ValueError(f"{command} input must be a JSON object")

    if command == "build-obligations":
        spec = payload.get("verification_spec")
        version = payload.get("generator_version")
        generated = ObligationGenerator.generate(spec, generator_version=version)
        return _plain(generated)

    if command == "project-package":
        return P31TaskProjector.project(**dict(payload))

    if command == "preflight-package":
        return _preflight_payload(PackageBindingPreflight.check(payload))

    if command == "preflight-evidence":
        nodes = payload.get("nodes")
        if not isinstance(nodes, list):
            raise ValueError("preflight-evidence requires nodes list")
        return _preflight_payload(EvidenceContractPreflight.check(nodes))

    if command == "compile-evidence":
        plan_value = payload.get("plan")
        if isinstance(plan_value, Mapping):
            requirements_value = plan_value.get("requirements", [])
        else:
            requirements_value = plan_value
        if not isinstance(requirements_value, list):
            raise ValueError("compile-evidence requires plan requirements")
        plan = EvidencePlan(tuple(
            EvidenceRequirement(
                fact_key=str(item["fact_key"]),
                authoritative_producer=str(item["authoritative_producer"]),
                required=bool(item.get("required", True)),
            )
            for item in requirements_value
        ))
        batches_value = payload.get("batches")
        if not isinstance(batches_value, list):
            raise ValueError("compile-evidence requires batches")
        batches = []
        for batch in batches_value:
            if not isinstance(batch, Mapping):
                raise ValueError("batch must be object")
            observations = tuple(
                ObservationRecord(
                    fact_key=str(item["fact_key"]),
                    producer_class=str(item["producer_class"]),
                    producer_id=str(item["producer_id"]),
                    subject_ref=str(item["subject_ref"]),
                    value=item.get("value"),
                    provider_run_ref=item.get("provider_run_ref"),
                )
                for item in batch.get("observations", [])
            )
            batches.append(ObservationBatch(str(batch["producer_id"]), bool(batch.get("complete")), observations))
        return _plain(EvidenceCompiler().compile(plan=plan, batches=tuple(batches)))

    if command == "evaluate":
        resolver = _MappingResolver(payload.get("resolved_evidence", []))
        result = ProofEvaluator(resolver=resolver).evaluate(
            verification_spec=payload.get("verification_spec", {}),
            obligation_set=payload.get("obligation_set", {}),
            evidence_input_refs=payload.get("evidence_input_refs", []),
            evaluator_version=str(payload.get("evaluator_version", "0.1")),
        )
        return {
            "proof_evaluation": _plain(result.proof_evaluation),
            "verification_summary": _plain(result.verification_summary),
        }

    if command == "review-check":
        checker = IndependentCompletenessChecker()
        completeness = checker.check(
            verification_spec=payload.get("verification_spec", {}),
            actual_obligation_set=payload.get("actual_obligation_set", {}),
        )
        result: dict[str, Any] = {"completeness": _plain(completeness)}
        if "requested_requirement" in payload:
            result["review_delta"] = ReviewContractDiffer().classify(
                requested_requirement=payload.get("requested_requirement", {}),
                verification_spec=payload.get("verification_spec", {}),
                package=payload.get("package", {}),
            ).value
        return result

    raise AssertionError(command)


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        payload = {"ok": False, "error": {"type": "UsageError", "message": "exactly one subcommand is required"}}
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        print("exactly one subcommand is required", file=sys.stderr)
        return 2
    command = args[0]
    try:
        raw = sys.stdin.read()
        value = json.loads(raw)
        result = execute(command, value)
    except Exception as exc:
        payload = {"ok": False, "error": {"type": exc.__class__.__name__, "message": str(exc)}}
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(_plain(result), sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
