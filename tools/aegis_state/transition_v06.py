from __future__ import annotations
from .model import ManifestSet
from .transition_v05 import validate_v05_transition

def validate_v06_transition(previous: ManifestSet, current: ManifestSet) -> list[str]:
    errors: list[str] = []
    if previous.schema_version != "0.6" or current.schema_version != "0.6":
        return ["v0.6 transition validation requires schema_version 0.6 on both snapshots"]
    old = {x.get("id"): x for x in previous.integration_items if isinstance(x.get("id"), str)}
    new = {x.get("id"): x for x in current.integration_items if isinstance(x.get("id"), str)}
    for iid, item in old.items():
        if iid not in new:
            errors.append(f"removed immutable integration {iid}")
            continue
        if item.get("status") == "integrated":
            for key in ("id", "kind", "ref", "target_ref", "integrated_revision", "gate_decision_binding"):
                if item.get(key) != new[iid].get(key): errors.append(f"integrated occurrence {iid} immutable field {key} changed")
    return errors
