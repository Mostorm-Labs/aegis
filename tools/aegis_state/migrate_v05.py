from __future__ import annotations

import copy

from .model import ManifestSet


def legacy_decision_id(gate_id: str) -> str:
    if not isinstance(gate_id, str) or not gate_id:
        raise ValueError("gate_id must be a non-empty string")
    return f"{gate_id}::decision::0001"


def migrate_v04_to_v05(manifests: ManifestSet) -> ManifestSet:
    if manifests.schema_version != "0.4":
        raise ValueError("v0.5 migration requires schema_version 0.4")

    project = copy.deepcopy(manifests.project)
    authorities = copy.deepcopy(manifests.authorities)
    evidence = copy.deepcopy(manifests.evidence)
    integrations = copy.deepcopy(manifests.integrations)

    contracts: list[dict] = []
    decisions: list[dict] = []
    for gate in manifests.gate_items:
        gate_id = gate["id"]
        contracts.append({
            "id": gate_id,
            "stage": gate["stage"],
            "authority_ids": list(gate.get("authority_ids", [])),
        })
        decisions.append({
            "id": legacy_decision_id(gate_id),
            "gate_id": gate_id,
            "verdict": gate["verdict"],
            "evidence_ids": list(gate.get("evidence_ids", [])),
        })
    gates = {"schema_version": "0.5", "gates": contracts, "decisions": decisions}

    migrated_integrations: list[dict] = []
    for item in integrations.get("integrations", []):
        migrated = copy.deepcopy(item)
        gate_id = migrated.pop("gate_id")
        migrated["gate_decision_id"] = legacy_decision_id(gate_id)
        migrated_integrations.append(migrated)
    integrations["integrations"] = migrated_integrations

    for document in (project, authorities, evidence, integrations):
        document["schema_version"] = "0.5"

    return ManifestSet(
        root=manifests.root,
        project=project,
        authorities=authorities,
        gates=gates,
        evidence=evidence,
        integrations=integrations,
    )
