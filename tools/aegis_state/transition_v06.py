from __future__ import annotations
from .model import ManifestSet
def _binding(item: dict, schema_version: str) -> dict | None:
    if schema_version == "0.6":
        return item.get("gate_decision_binding")
    decision_id = item.get("gate_decision_id")
    return {"kind": "bound", "gate_decision_id": decision_id} if isinstance(decision_id, str) else None

def validate_v06_transition(previous: ManifestSet, current: ManifestSet) -> list[str]:
    errors: list[str] = []
    if previous.schema_version not in {"0.5", "0.6"} or current.schema_version != "0.6":
        return ["v0.6 transition validation requires a v0.5 or v0.6 previous snapshot and a v0.6 current snapshot"]
    previous_gates = {x.get("id"): x for x in previous.gate_items if isinstance(x.get("id"), str)}
    current_gates = {x.get("id"): x for x in current.gate_items if isinstance(x.get("id"), str)}
    for gid, old in previous_gates.items():
        new = current_gates.get(gid)
        if new is None:
            errors.append(f"removed immutable gate contract {gid}")
        elif {k: old.get(k) for k in ("id", "stage", "authority_ids")} != {k: new.get(k) for k in ("id", "stage", "authority_ids")}:
            errors.append(f"immutable gate contract {gid} changed in place")
    previous_decisions = {x.get("id"): x for x in previous.decision_items if isinstance(x.get("id"), str)}
    current_decisions = {x.get("id"): x for x in current.decision_items if isinstance(x.get("id"), str)}
    for did, old in previous_decisions.items():
        new = current_decisions.get(did)
        if new is None:
            errors.append(f"removed immutable gate decision {did}")
        elif {k: old.get(k) for k in ("id", "gate_id", "verdict", "evidence_ids", "supersedes")} != {k: new.get(k) for k in ("id", "gate_id", "verdict", "evidence_ids", "supersedes")}:
            errors.append(f"immutable gate decision {did} changed in place")
    old = {x.get("id"): x for x in previous.integration_items if isinstance(x.get("id"), str)}
    new = {x.get("id"): x for x in current.integration_items if isinstance(x.get("id"), str)}
    for iid, item in old.items():
        if iid not in new:
            errors.append(f"removed immutable integration {iid}")
            continue
        if item.get("status") == "integrated":
            for key in ("id", "kind", "ref", "target_ref", "integrated_revision"):
                if item.get(key) != new[iid].get(key): errors.append(f"integrated occurrence {iid} immutable field {key} changed")
            if _binding(item, previous.schema_version) != _binding(new[iid], current.schema_version):
                errors.append(f"integrated occurrence {iid} immutable field gate_decision_binding changed")
            old_evidence = item.get("evidence_ids", [])
            new_evidence = new[iid].get("evidence_ids", [])
            if not (isinstance(old_evidence, list) and isinstance(new_evidence, list)):
                errors.append(f"integrated occurrence {iid} evidence_ids must remain list-valued")
            elif new_evidence[:len(old_evidence)] != old_evidence:
                errors.append(f"integrated occurrence {iid} evidence_ids must be append-only")
    return errors
