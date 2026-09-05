from __future__ import annotations
import copy
from .model import ManifestSet, validate_manifests
from .migrate_v05 import legacy_decision_id

def migrate_v05_to_v06(manifests: ManifestSet) -> ManifestSet:
    if manifests.schema_version != "0.5":
        raise ValueError("v0.6 migration requires schema_version 0.5")
    errors = validate_manifests(manifests, strict_gate_validity=True)
    if errors:
        raise ValueError("invalid v0.5 source: " + "; ".join(errors))
    docs = [copy.deepcopy(x) for x in (manifests.project, manifests.authorities, manifests.gates, manifests.evidence, manifests.integrations)]
    project, authorities, gates, evidence, integrations = docs
    for doc in docs: doc["schema_version"] = "0.6"
    for item in integrations.get("integrations", []):
        decision_id = item.pop("gate_decision_id", None)
        if not isinstance(decision_id, str) or not decision_id:
            raise ValueError("v0.5 integration missing gate_decision_id")
        item["gate_decision_binding"] = {"kind": "bound", "gate_decision_id": decision_id}
    return ManifestSet(root=manifests.root, project=project, authorities=authorities, gates=gates, evidence=evidence, integrations=integrations)
