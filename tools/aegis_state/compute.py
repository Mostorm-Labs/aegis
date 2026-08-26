from __future__ import annotations

import hashlib
import json
from typing import Literal

from . import GENERATOR_VERSION
from .model import ManifestSet

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


def _worst(values: list[Validity]) -> Validity:
    if "stale" in values:
        return "stale"
    if "needs_review" in values:
        return "needs_review"
    return "current"


def manifest_digest(manifests: ManifestSet) -> str:
    canonical = {
        "project": manifests.project,
        "authorities": manifests.authorities,
        "gates": manifests.gates,
        "evidence": manifests.evidence,
    }
    data = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def compute_state(manifests: ManifestSet) -> dict:
    authorities = manifests.authority_items
    gates = manifests.gate_items
    evidence = manifests.evidence_items
    reviews = manifests.impact_reviews
    auth_by_id = {a["id"]: a for a in authorities if isinstance(a.get("id"), str)}
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
    findings: list[str] = []
    for gate in gates:
        gid = gate.get("id")
        impacts: list[Validity] = []
        for aid in gate.get("authority_ids", []):
            authority = auth_by_id.get(aid)
            if not authority or authority.get("status") in {"Superseded", "Historical"}:
                impacts.append("stale")
            else:
                impacts.append(authority_validity(aid))
        for eid in gate.get("evidence_ids", []):
            if ev_by_id.get(eid, {}).get("status") != "available":
                impacts.append("stale")
        effective = _worst(impacts)
        if effective == "stale":
            stale_gates.append(str(gid))
        elif effective == "needs_review":
            needs_review_gates.append(str(gid))
        declared = gate.get("validity")
        if declared in {"current", "needs_review", "stale"} and declared != effective:
            findings.append(f"gate {gid} validity drift: declared={declared}, computed={effective}")

    for aid in stale_authorities:
        findings.append(f"authority {aid} is stale because a validity-bearing dependency is no longer current")
    for aid in needs_review_authorities:
        findings.append(f"authority {aid} needs review because an upstream dependency changed")
    for gid in stale_gates:
        findings.append(f"gate {gid} is stale under current authority/evidence")
    for gid in needs_review_gates:
        findings.append(f"gate {gid} needs review under current authority/evidence")

    affected = stale_authorities + needs_review_authorities
    if affected:
        layers = [_LAYER_BY_KIND.get(str(auth_by_id[aid].get("kind")), "authority") for aid in affected]
        earliest = min(layers, key=lambda x: _LAYER_ORDER.index(x) if x in _LAYER_ORDER else _LAYER_ORDER.index("authority"))
        recommended = "P21"
    elif stale_gates or needs_review_gates:
        earliest = "verification"
        recommended = "P34"
    else:
        earliest = None
        recommended = None

    project = manifests.project.get("project") or {}
    return {
        "schema_version": "0.1",
        "generator_version": GENERATOR_VERSION,
        "manifest_digest": manifest_digest(manifests),
        "active_stage": project.get("lifecycle_hint"),
        "earliest_untrusted_layer": earliest,
        "blocking_findings": sorted(set(findings)),
        "stale_authorities": sorted(stale_authorities),
        "needs_review_authorities": sorted(needs_review_authorities),
        "stale_gates": sorted(stale_gates),
        "needs_review_gates": sorted(needs_review_gates),
        "recommended_next_stage": recommended,
    }
