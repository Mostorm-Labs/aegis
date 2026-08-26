from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

SCHEMA_VERSION = "0.1"
AUTHORITY_STATUSES = {"Proposed", "Current", "Superseded", "Historical"}
GATE_VERDICTS = {
    "PASS", "PASS_WITH_FINDINGS", "BLOCKED_IMPLEMENTATION",
    "BLOCKED_AUTHORITY", "BLOCKED_EVIDENCE", "BLOCKED_ENVIRONMENT",
}
GATE_VALIDITY = {"current", "needs_review", "stale"}
EVIDENCE_STATUSES = {"available", "missing", "invalid", "superseded"}
PASS_VERDICTS = {"PASS", "PASS_WITH_FINDINGS"}


class ManifestError(ValueError):
    pass


@dataclass(frozen=True)
class ManifestSet:
    root: Path
    project: dict
    authorities: dict
    gates: dict
    evidence: dict

    @property
    def authority_items(self) -> list[dict]:
        return list(self.authorities.get("authorities", []))

    @property
    def impact_reviews(self) -> list[dict]:
        return list(self.authorities.get("impact_reviews", []))

    @property
    def gate_items(self) -> list[dict]:
        return list(self.gates.get("gates", []))

    @property
    def evidence_items(self) -> list[dict]:
        return list(self.evidence.get("evidence", []))


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise ManifestError(f"missing manifest: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ManifestError(f"manifest must be a JSON object: {path}")
    return data


def load_manifests(project_root: Path | str) -> ManifestSet:
    root = Path(project_root)
    manifest_root = root / ".aegis"
    return ManifestSet(
        root=manifest_root,
        project=_read_json(manifest_root / "project.json"),
        authorities=_read_json(manifest_root / "authorities.json"),
        gates=_read_json(manifest_root / "gates.json"),
        evidence=_read_json(manifest_root / "evidence.json"),
    )


def _duplicates(items: list[dict], key: str) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        value = item.get(key)
        if not isinstance(value, str):
            continue
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _cycle(graph: dict[str, list[str]]) -> list[str] | None:
    visited: set[str] = set()
    active: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in active:
            idx = stack.index(node)
            return stack[idx:] + [node]
        if node in visited:
            return None
        visited.add(node)
        active.add(node)
        stack.append(node)
        for nxt in graph.get(node, []):
            if nxt in graph:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        active.remove(node)
        return None

    for node in graph:
        found = visit(node)
        if found:
            return found
    return None


def validate_manifests(manifests: ManifestSet, *, strict_gate_validity: bool = True) -> list[str]:
    errors: list[str] = []

    for name, data in [
        ("project", manifests.project), ("authorities", manifests.authorities),
        ("gates", manifests.gates), ("evidence", manifests.evidence),
    ]:
        if data.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"{name}: schema_version must be {SCHEMA_VERSION}")

    project = manifests.project.get("project")
    if not isinstance(project, dict):
        errors.append("project: project must be an object")
    else:
        for field in ("id", "name", "profile"):
            if not isinstance(project.get(field), str) or not project.get(field):
                errors.append(f"project: missing non-empty {field}")
        if project.get("profile") not in {"lite", "standard", "full"}:
            errors.append("project: profile must be lite, standard, or full")

    authorities = manifests.authority_items
    gates = manifests.gate_items
    evidence = manifests.evidence_items
    reviews = manifests.impact_reviews

    for registry_name, items in [
        ("authority", authorities), ("gate", gates),
        ("evidence", evidence), ("impact review", reviews),
    ]:
        for duplicate in sorted(_duplicates(items, "id")):
            errors.append(f"duplicate {registry_name} id: {duplicate}")

    auth_by_id = {item.get("id"): item for item in authorities if isinstance(item.get("id"), str)}
    evidence_by_id = {item.get("id"): item for item in evidence if isinstance(item.get("id"), str)}

    current_by_scope_kind: dict[tuple[str, str], list[str]] = {}
    for item in authorities:
        aid = item.get("id")
        for field in ("id", "scope", "kind", "version", "status", "ref"):
            if not isinstance(item.get(field), str) or not item.get(field):
                errors.append(f"authority {aid or '<unknown>'}: missing non-empty {field}")
        if item.get("status") not in AUTHORITY_STATUSES:
            errors.append(f"authority {aid}: invalid status {item.get('status')}")
        deps = item.get("depends_on", [])
        if not isinstance(deps, list) or not all(isinstance(x, str) for x in deps):
            errors.append(f"authority {aid}: depends_on must be a string array")
            deps = []
        for dep in deps:
            if dep not in auth_by_id:
                errors.append(f"authority {aid}: dangling authority dependency {dep}")
        supersedes = item.get("supersedes")
        if supersedes is not None and supersedes not in auth_by_id:
            errors.append(f"authority {aid}: dangling supersedes target {supersedes}")
        if item.get("status") == "Current":
            key = (str(item.get("scope")), str(item.get("kind")))
            current_by_scope_kind.setdefault(key, []).append(str(aid))

    for key, ids in current_by_scope_kind.items():
        if len(ids) > 1:
            errors.append(f"multiple Current authorities for scope/kind {key[0]}/{key[1]}: {', '.join(sorted(ids))}")

    dep_graph = {
        str(item.get("id")): [str(x) for x in item.get("depends_on", []) if isinstance(x, str)]
        for item in authorities if isinstance(item.get("id"), str)
    }
    found = _cycle(dep_graph)
    if found:
        errors.append(f"authority dependency cycle: {' -> '.join(found)}")

    supersession_graph = {
        str(item.get("id")): [str(item.get("supersedes"))] if isinstance(item.get("supersedes"), str) else []
        for item in authorities if isinstance(item.get("id"), str)
    }
    found = _cycle(supersession_graph)
    if found:
        errors.append(f"supersession cycle: {' -> '.join(found)}")

    for item in evidence:
        eid = item.get("id")
        for field in ("id", "type", "ref", "status"):
            if not isinstance(item.get(field), str) or not item.get(field):
                errors.append(f"evidence {eid or '<unknown>'}: missing non-empty {field}")
        if item.get("status") not in EVIDENCE_STATUSES:
            errors.append(f"evidence {eid}: invalid status {item.get('status')}")

    for gate in gates:
        gid = gate.get("id")
        if gate.get("verdict") not in GATE_VERDICTS:
            errors.append(f"gate {gid}: invalid verdict {gate.get('verdict')}")
        if gate.get("validity") not in GATE_VALIDITY:
            errors.append(f"gate {gid}: invalid validity {gate.get('validity')}")
        authority_ids = gate.get("authority_ids", [])
        evidence_ids = gate.get("evidence_ids", [])
        if not isinstance(authority_ids, list) or not all(isinstance(x, str) for x in authority_ids):
            errors.append(f"gate {gid}: authority_ids must be a string array")
            authority_ids = []
        if not isinstance(evidence_ids, list) or not all(isinstance(x, str) for x in evidence_ids):
            errors.append(f"gate {gid}: evidence_ids must be a string array")
            evidence_ids = []
        for aid in authority_ids:
            if aid not in auth_by_id:
                errors.append(f"gate {gid}: dangling authority id {aid}")
        for eid in evidence_ids:
            if eid not in evidence_by_id:
                errors.append(f"gate {gid}: dangling evidence id {eid}")
        if gate.get("verdict") in PASS_VERDICTS and not evidence_ids:
            errors.append(f"PASS gate {gid} requires evidence")
        if strict_gate_validity and gate.get("validity") == "current" and gate.get("verdict") in PASS_VERDICTS:
            for aid in authority_ids:
                authority = auth_by_id.get(aid)
                if authority and authority.get("status") != "Current":
                    errors.append(f"current PASS gate {gid} depends on non-current authority {aid}")
            for eid in evidence_ids:
                ev = evidence_by_id.get(eid)
                if ev and ev.get("status") != "available":
                    errors.append(f"current PASS gate {gid} uses unavailable evidence {eid}")

    for review in reviews:
        rid = review.get("id")
        source = review.get("source_authority")
        dependent = review.get("dependent_authority")
        if source not in auth_by_id:
            errors.append(f"impact review {rid}: dangling source authority {source}")
        if dependent not in auth_by_id:
            errors.append(f"impact review {rid}: dangling dependent authority {dependent}")
        if review.get("outcome") not in {"unaffected", "needs_review", "stale"}:
            errors.append(f"impact review {rid}: invalid outcome {review.get('outcome')}")
        evidence_ids = review.get("evidence_ids", [])
        if not isinstance(evidence_ids, list) or not all(isinstance(x, str) for x in evidence_ids):
            errors.append(f"impact review {rid}: evidence_ids must be a string array")
            evidence_ids = []
        for eid in evidence_ids:
            if eid not in evidence_by_id:
                errors.append(f"impact review {rid}: dangling evidence id {eid}")

    return errors
