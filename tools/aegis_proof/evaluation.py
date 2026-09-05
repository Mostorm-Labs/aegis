from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

@dataclass(frozen=True)
class EvaluationResult:
    proof_evaluation: Mapping[str, Any]
    verification_summary: Mapping[str, Any]

class ProofEvaluator:
    ALLOWED = {"SATISFIED", "EXCEPTION", "UNSATISFIED"}
    def evaluate(self, *, verification_spec: Mapping[str, Any], obligation_set: Mapping[str, Any], evidence_input_refs: Sequence[Mapping[str, Any]], evaluator_version: str) -> EvaluationResult:
        evidence_by_obligation = {str(item.get("obligation_id")): item for item in evidence_input_refs if item.get("obligation_id")}
        results = []
        for obligation in obligation_set.get("obligations", ()):
            oid = str(obligation.get("id"))
            evidence = evidence_by_obligation.get(oid)
            status = "UNSATISFIED" if evidence is None else str(evidence.get("status", "UNSATISFIED"))
            if status not in self.ALLOWED:
                status = "UNSATISFIED"
            results.append({"obligation_id": oid, "status": status})
        counts = {key: sum(1 for item in results if item["status"] == key) for key in sorted(self.ALLOWED)}
        evaluation = {"evaluator_version": evaluator_version, "results": results, "states": counts}
        summary = {"obligation_count": len(results), "satisfied": counts["SATISFIED"], "exception": counts["EXCEPTION"], "unsatisfied": counts["UNSATISFIED"]}
        return EvaluationResult(evaluation, summary)
