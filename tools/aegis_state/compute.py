from __future__ import annotations

import hashlib
import json
from typing import Literal

from . import GENERATOR_VERSION
from .model import ManifestSet, PASS_VERDICTS

Validity = Literal["current", "needs_review", "stale"]

_CHANGE_IMPACT: dict[str, Validity] = {
    "semantic": "stale",
    "breaking": "stale",
    "ownership": "stale",
    "clarification": "needs_review",
    "compatible": "needs_review",
}
_LAYER_BY_KIND = {
    "problem": "problem",
    "product_requirement": "requirement",
    "capability_traceability": "requirement",
    "product_object_model": "object",
    "interaction_behavior": "behavior",
    "semantic_schema": "schema",
    "operation_model": "operation",
    "system_architecture": "architecture",
    "module_design": "module",
    "runtime_data_flow": "flow",
    "platform_contract": "platform",
    "engineering": "engineering",
    "verification": "verification",
    "verification_design": "verification",
    "implementation_plan": "implementation",
    "release": "release",
}
_LAYER_ORDER = ["problem", "requirement", "object", "behavior", "schema", "operation", "architecture", "module", "flow", "platform", "engineering", "verification", "authority", "implementation", "release"]
_GATE_BLOCK_ROUTE = {
    "BLOCKED_AUTHORITY": ("authority", "P21"),
    "BLOCKED_EVIDENCE": ("verification", "P34"),
    "BLOCKED_IMPLEMENTATION": ("implementation", "P35"),
    "BLOCKED_ENVIRONMENT": ("verification", "P34"),
}


def _worst(values: list[Validity]) -> Validity:
    if "stale" in values:
        return "stale"
    if "needs_review" in values:
        return "needs_review"
    return "current"


def _layer_rank(layer: str) -> int:
    try:
        return _LAYER_ORDER.index(layer)
    except ValueError:
        return _LAYER_ORDER.index("authority")


def _gate_authority_membership(gate: dict, auth_by_id: dict[str, dict]) -> str:
    statuses: list[str] = []
    for aid in gate.get("authority_ids", []):
        authority = auth_by_id.get(aid)
        if not authority:
            return "unknown"
        status = authority.get("status")
        if not isinstance(status, str):
            return "unknown"
        statuses.append(status)
    if not statuses:
        return "unknown"
    has_current = any(status in {"Current", "Proposed"} for status in statuses)
    has_history = any(status in {"Superseded", "Historical"} for status in statuses)
    if has_current and has_history:
        return "mixed"
    if has_history and not has_current:
        return "historical"
    if has_current and not has_history:
        return "current"
    return "unknown"


def manifest_digest(manifests: ManifestSet) -> str:
    canonical = {
        "project": manifests.project,
        "authorities": manifests.authorities,
        "gates": manifests.gates,
        "evidence": manifests.evidence,
        "integrations": manifests.integrations,
    }
    data = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def compute_state(manifests: ManifestSet) -> dict:
    authorities = manifests.authority_items
    gates = manifests.gate_items
    evidence = manifests.evidence_items
    integrations = manifests.integration_items
    reviews = manifests.impact_reviews
    auth_by_id = {a["id"]: a for a in authorities if isinstance(a.get("id"), str)}
    gate_by_id = {g["id"]: g for g in gates if isinstance(g.get("id"), str)}
    ev_by_id = {e["id"]: e for e in evidence if isinstance(e.get("id"), str)}
    replacement_by_old = {
        a["supersedes"]: a
        for a in authorities
        if isinstance(a.get("supersedes"), str) and isinstance(a.get("id"), str)
    }
    reviews_by_pair = {
        (r.get("source_authority"), r.get("dependent_authority")): r
        for r in reviews
        if isinstance(r.get("source_authority"), str) and isinstance(r.get("dependent_authority"), str)
    }
    memo: dict[str, Validity] = {}
    active: set[str] = set()

    def review_impact(replacement: dict | None, dependent_id: str) -> Validity | None:
        if not replacement:
            return None
        review = reviews_by_pair.get((replacement.get("id"), dependent_id))
        if not review:
            return None
        outcome = review.get("outcome")
        if outcome == "unaffected":
            evidence_ids = list(review.get("evidence_ids") or [])
            if evidence_ids and all(ev_by_id.get(eid, {}).get("status") == "available" for eid in evidence_ids):
                return "current"
            return None
        if outcome in {"needs_review", "stale"}:
            return outcome
        return None

    def direct_supersession_impact(dep: dict, dependent_id: str) -> Validity:
        replacement = replacement_by_old.get(dep.get("id"))
        reviewed = review_impact(replacement, dependent_id)
        if reviewed:
            return reviewed
        if replacement:
            return _CHANGE_IMPACT.get(str(replacement.get("change_class")), "needs_review")
        return "needs_review"

    def authority_validity(authority_id: str) -> Validity:
        if authority_id in memo:
            return memo[authority_id]
        if authority_id in active:
            return "needs_review"
        authority = auth_by_id.get(authority_id)
        if not authority:
            return "stale"
        if authority.get("status") not in {"Current", "Proposed"}:
            return "stale"
        active.add(authority_id)
        impacts: list[Validity] = []
        for dep_id in authority.get("depends_on", []):
            dep = auth_by_id.get(dep_id)
            if not dep:
                impacts.append("stale")
                continue
            if dep.get("status") in {"Superseded", "Historical"}:
                impacts.append(direct_supersession_impact(dep, authority_id))
            else:
                impacts.append(authority_validity(dep_id))
        active.remove(authority_id)
        result = _worst(impacts)
        memo[authority_id] = result
        return result

    stale_authorities: list[str] = []
    needs_review_authorities: list[str] = []
    for authority in authorities:
        aid = authority.get("id")
        if not isinstance(aid, str) or authority.get("status") not in {"Current", "Proposed"}:
            continue
        validity = authority_validity(aid)
        if validity == "stale":
            stale_authorities.append(aid)
        elif validity == "needs_review":
            needs_review_authorities.append(aid)

    stale_gates: list[str] = []
    needs_review_gates: list[str] = []
    historical_gates: list[str] = []
    authority_review_gates: set[str] = set()
    completed_history_gate_ids = {
        str(item.get("gate_id"))
        for item in integrations
        if item.get("status") in {"integrated", "closed_unmerged"}
    }
    blocking_gates: list[str] = []
    gate_effective: dict[str, Validity] = {}
    gate_membership: dict[str, str] = {}
    findings: list[str] = []
    route_candidates: list[tuple[str, str | None, str | None]] = []

    for gate in gates:
        gid = str(gate.get("id"))
        membership = _gate_authority_membership(gate, auth_by_id)
        gate_membership[gid] = membership
        if membership == "historical" and gid in completed_history_gate_ids:
            gate_effective[gid] = "stale"
            historical_gates.append(gid)
            continue
        if membership in {"mixed", "unknown"}:
            gate_effective[gid] = "needs_review"
            needs_review_gates.append(gid)
            authority_review_gates.add(gid)
            findings.append(f"gate {gid} needs Authority review because its validity-bearing Authority set is mixed or unresolved")
            route_candidates.append(("authority", "P21", None))
            continue

        impacts: list[Validity] = []
        for aid in gate.get("authority_ids", []):
            impacts.append(authority_validity(aid))
        for eid in gate.get("evidence_ids", []):
            if ev_by_id.get(eid, {}).get("status") != "available":
                impacts.append("stale")
        effective = _worst(impacts)
        gate_effective[gid] = effective
        if effective == "stale":
            stale_gates.append(gid)
        elif effective == "needs_review":
            needs_review_gates.append(gid)
        declared = gate.get("validity")
        if declared in {"current", "needs_review", "stale"} and declared != effective:
            findings.append(f"gate {gid} validity drift: declared={declared}, computed={effective}")
        verdict = gate.get("verdict")
        if declared == "current" and effective == "current" and verdict in _GATE_BLOCK_ROUTE:
            blocking_gates.append(gid)
            layer, stage = _GATE_BLOCK_ROUTE[str(verdict)]
            route_candidates.append((layer, stage, None))
            findings.append(f"gate {gid} is currently {verdict}")

    for aid in stale_authorities:
        findings.append(f"authority {aid} is stale because a validity-bearing dependency is no longer current")
        layer = _LAYER_BY_KIND.get(str(auth_by_id[aid].get("kind")), "authority")
        route_candidates.append((layer, "P21", None))
    for aid in needs_review_authorities:
        findings.append(f"authority {aid} needs review because an upstream dependency changed")
        layer = _LAYER_BY_KIND.get(str(auth_by_id[aid].get("kind")), "authority")
        route_candidates.append((layer, "P21", None))
    for gid in stale_gates:
        findings.append(f"gate {gid} is stale under current authority/evidence")
        route_candidates.append(("verification", "P34", None))
    for gid in needs_review_gates:
        if gid in authority_review_gates:
            continue
        findings.append(f"gate {gid} needs review under current authority/evidence")
        route_candidates.append(("verification", "P34", None))

    awaiting_integrations: list[str] = []
    integration_applicability: list[dict[str, str]] = []
    for integration in integrations:
        iid = str(integration.get("id"))
        status = str(integration.get("status"))
        gate_id = str(integration.get("gate_id"))
        membership = gate_membership.get(gate_id, "unknown")
        effective = gate_effective.get(gate_id, "stale")
        if status in {"integrated", "closed_unmerged"} and membership == "historical":
            applicability = "historical"
        elif membership in {"mixed", "unknown"}:
            applicability = "needs_review"
        elif effective == "stale":
            applicability = "stale"
        elif effective == "needs_review":
            applicability = "needs_review"
        else:
            applicability = "current"
        integration_applicability.append({"integration_id": iid, "applicability": applicability})

        if status != "awaiting_integration":
            continue
        awaiting_integrations.append(iid)
        target = str(integration.get("target_ref"))
        findings.append(f"integration {iid} is awaiting integration into {target} after Gate PASS")
        gate = gate_by_id.get(integration.get("gate_id"))
        if gate and gate.get("verdict") in PASS_VERDICTS and gate.get("validity") == "current" and effective == "current":
            route_candidates.append(("implementation", None, "superpowers:finishing-a-development-branch"))

    if route_candidates:
        primary = min(route_candidates, key=lambda item: (_layer_rank(item[0]), item[1] or "ZZZ", item[2] or "ZZZ"))
        earliest, recommended, handoff = primary
    else:
        earliest = None
        recommended = None
        handoff = None

    project = manifests.project.get("project") or {}
    return {
        "schema_version": "0.3",
        "generator_version": GENERATOR_VERSION,
        "manifest_digest": manifest_digest(manifests),
        "active_stage": project.get("lifecycle_hint"),
        "earliest_untrusted_layer": earliest,
        "blocking_findings": sorted(set(findings)),
        "stale_authorities": sorted(stale_authorities),
        "needs_review_authorities": sorted(needs_review_authorities),
        "stale_gates": sorted(stale_gates),
        "needs_review_gates": sorted(needs_review_gates),
        "historical_gates": sorted(historical_gates),
        "blocking_gates": sorted(blocking_gates),
        "awaiting_integrations": sorted(awaiting_integrations),
        "integration_applicability": sorted(integration_applicability, key=lambda item: item["integration_id"]),
        "recommended_next_stage": recommended,
        "recommended_handoff": handoff,
    }
