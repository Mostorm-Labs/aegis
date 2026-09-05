from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence

from .ports import ExactRefResolverPort


@dataclass(frozen=True)
class EvaluationResult:
    proof_evaluation: Mapping[str, Any]
    verification_summary: Mapping[str, Any]


class ProofEvaluator:
    ALLOWED = {"SATISFIED", "EXCEPTION", "UNSATISFIED"}

    def __init__(self, *, resolver: ExactRefResolverPort | None = None):
        self._resolver = resolver

    @staticmethod
    def _artifact_digest(artifact: Mapping[str, Any]) -> str:
        payload = json.dumps(
            artifact,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
        return "sha256:" + hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _resolved_descriptor(
        *, verification_spec: Mapping[str, Any], obligation: Mapping[str, Any]
    ) -> Mapping[str, Any] | None:
        subject = obligation.get("subject")
        if not isinstance(subject, Mapping) or subject.get("kind") != "CLAIM":
            return None
        claim_id = subject.get("claim_id")
        contract_id = subject.get("proof_contract_id")
        claims = {
            str(item.get("id")): item
            for item in verification_spec.get("claims", ())
            if isinstance(item, Mapping) and item.get("id")
        }
        claim = claims.get(str(claim_id))
        if not isinstance(claim, Mapping) or claim.get("proof_contract_id") != contract_id:
            return None
        contracts = {
            str(item.get("id")): item
            for item in verification_spec.get("proof_contracts", ())
            if isinstance(item, Mapping) and item.get("id")
        }
        contract = contracts.get(str(contract_id))
        if not isinstance(contract, Mapping) or contract.get("claim_id") != claim_id:
            return None
        for descriptor in contract.get("resolved_obligations", ()):
            if not isinstance(descriptor, Mapping):
                continue
            if (
                descriptor.get("kind") == obligation.get("kind")
                and descriptor.get("source_key") == obligation.get("source_key")
                and descriptor.get("evaluation_mode") == obligation.get("evaluation_mode")
                and list(descriptor.get("required_evidence_types", ()))
                == list(obligation.get("required_evidence_types", ()))
                and descriptor.get("pass_condition") == obligation.get("pass_condition")
            ):
                return descriptor
        return None

    def _deterministic_status(
        self,
        *,
        obligation: Mapping[str, Any],
        verification_spec: Mapping[str, Any],
        evidence_input_refs: Sequence[Mapping[str, Any]],
    ) -> str:
        if self._resolved_descriptor(verification_spec=verification_spec, obligation=obligation) is None:
            return "UNSATISFIED"

        oid = str(obligation.get("id"))
        pass_condition = obligation.get("pass_condition")
        bound_results: list[bool] = []

        for evidence_ref in evidence_input_refs:
            if not isinstance(evidence_ref, Mapping):
                continue
            if not (
                isinstance(evidence_ref.get("evidence_id"), str)
                and evidence_ref.get("evidence_id")
                and isinstance(evidence_ref.get("ref"), str)
                and evidence_ref.get("ref")
                and isinstance(evidence_ref.get("digest"), str)
                and evidence_ref.get("digest").startswith("sha256:")
                and len(evidence_ref.get("digest")) == 71
                and isinstance(evidence_ref.get("provider"), str)
                and evidence_ref.get("provider")
                and isinstance(evidence_ref.get("native_id"), str)
                and evidence_ref.get("native_id")
                and evidence_ref.get("reviewer_resolvable") is True
            ):
                continue
            if self._resolver is None:
                continue
            try:
                resolved = self._resolver.resolve(evidence_ref)
            except Exception:
                return "UNSATISFIED"
            if not isinstance(resolved, Mapping):
                return "UNSATISFIED"
            if not (
                resolved.get("ref") == evidence_ref.get("ref")
                and resolved.get("digest") == evidence_ref.get("digest")
                and resolved.get("provider") == evidence_ref.get("provider")
                and str(resolved.get("native_id")) == str(evidence_ref.get("native_id"))
                and resolved.get("reviewer_resolvable") is True
            ):
                return "UNSATISFIED"

            artifact = resolved.get("content")
            if not isinstance(artifact, Mapping):
                return "UNSATISFIED"
            if self._artifact_digest(artifact) != evidence_ref.get("digest"):
                return "UNSATISFIED"
            if evidence_ref.get("producer_class") != artifact.get("producer_class"):
                return "UNSATISFIED"

            subjects = artifact.get("subjects")
            if not isinstance(subjects, Mapping) or oid not in {
                str(item) for item in subjects.get("obligation_ids", ())
            }:
                continue

            observations = [
                item
                for item in artifact.get("observations", ())
                if isinstance(item, Mapping)
                and str(item.get("obligation_id")) == oid
                and item.get("pass_condition") == pass_condition
                and isinstance(item.get("passed"), bool)
            ]
            if not observations:
                return "UNSATISFIED"
            values = {item["passed"] for item in observations}
            if len(values) != 1:
                return "UNSATISFIED"
            bound_results.append(values.pop())

        if not bound_results:
            return "UNSATISFIED"
        return "SATISFIED" if all(bound_results) else "UNSATISFIED"

    def evaluate(
        self,
        *,
        verification_spec: Mapping[str, Any],
        obligation_set: Mapping[str, Any],
        evidence_input_refs: Sequence[Mapping[str, Any]],
        evaluator_version: str,
    ) -> EvaluationResult:
        results = []
        for obligation in obligation_set.get("obligations", ()):
            oid = str(obligation.get("id"))
            if obligation.get("evaluation_mode") == "REVIEW_REQUIRED":
                status = "EXCEPTION"
            elif obligation.get("evaluation_mode") == "DETERMINISTIC":
                status = self._deterministic_status(
                    obligation=obligation,
                    verification_spec=verification_spec,
                    evidence_input_refs=evidence_input_refs,
                )
            else:
                status = "UNSATISFIED"
            results.append({"obligation_id": oid, "status": status})

        counts = {
            key: sum(1 for item in results if item["status"] == key)
            for key in sorted(self.ALLOWED)
        }
        evaluation = {
            "evaluator_version": evaluator_version,
            "results": results,
            "states": counts,
        }
        summary = {
            "obligation_count": len(results),
            "satisfied": counts["SATISFIED"],
            "exception": counts["EXCEPTION"],
            "unsatisfied": counts["UNSATISFIED"],
        }
        return EvaluationResult(evaluation, summary)
