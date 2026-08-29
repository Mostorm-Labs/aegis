from __future__ import annotations

from .model import ManifestSet


def _normalized_gate(gate: dict) -> dict:
    return {
        "id": gate.get("id"),
        "stage": gate.get("stage"),
        "authority_ids": sorted(gate.get("authority_ids", [])),
    }


def _normalized_decision(decision: dict) -> dict:
    result = {
        "id": decision.get("id"),
        "gate_id": decision.get("gate_id"),
        "verdict": decision.get("verdict"),
        "evidence_ids": sorted(decision.get("evidence_ids", [])),
    }
    if "supersedes" in decision:
        result["supersedes"] = decision.get("supersedes")
    return result


def validate_v05_transition(previous: ManifestSet, current: ManifestSet) -> list[str]:
    errors: list[str] = []
    if previous.schema_version != "0.5" or current.schema_version != "0.5":
        return ["gate decision transition validation requires schema_version 0.5 on both snapshots"]

    previous_gates = {g.get("id"): g for g in previous.gate_items if isinstance(g.get("id"), str)}
    current_gates = {g.get("id"): g for g in current.gate_items if isinstance(g.get("id"), str)}
    for gate_id, old_gate in previous_gates.items():
        new_gate = current_gates.get(gate_id)
        if new_gate is None:
            errors.append(f"removed immutable gate contract {gate_id}")
        elif _normalized_gate(old_gate) != _normalized_gate(new_gate):
            errors.append(f"immutable gate contract {gate_id} changed in place")

    previous_decisions = {d.get("id"): d for d in previous.decision_items if isinstance(d.get("id"), str)}
    current_decisions = {d.get("id"): d for d in current.decision_items if isinstance(d.get("id"), str)}
    for decision_id, old_decision in previous_decisions.items():
        new_decision = current_decisions.get(decision_id)
        if new_decision is None:
            errors.append(f"removed immutable gate decision {decision_id}")
        elif _normalized_decision(old_decision) != _normalized_decision(new_decision):
            errors.append(f"immutable gate decision {decision_id} changed in place")

    return errors
