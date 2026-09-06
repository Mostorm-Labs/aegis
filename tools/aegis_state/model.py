from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_VERSION = "0.6"
SUPPORTED_SCHEMA_VERSIONS = {"0.3", "0.4", "0.5", "0.6"}
AUTHORITY_STATUSES = {"Proposed", "Current", "Superseded", "Historical"}
GATE_VERDICTS = {
    "PASS", "PASS_WITH_FINDINGS", "BLOCKED_IMPLEMENTATION",
    "BLOCKED_AUTHORITY", "BLOCKED_EVIDENCE", "BLOCKED_ENVIRONMENT",
}
GATE_VALIDITY = {"current", "needs_review", "stale"}
EVIDENCE_STATUSES = {"available", "missing", "invalid", "superseded"}
PASS_VERDICTS = {"PASS", "PASS_WITH_FINDINGS"}
INTEGRATION_STATUSES = {"awaiting_integration", "integrated", "closed_unmerged"}
_DECISION_ID_RE = re.compile(r"^(?P<gate>.+)::decision::(?P<seq>[0-9]{4})$")


class ManifestError(ValueError):
    pass


@dataclass(frozen=True)
class ManifestSet:
    root: Path
    project: dict
    authorities: dict
    gates: dict
    evidence: dict
    integrations: dict = field(default_factory=lambda: {"schema_version": SCHEMA_VERSION, "integrations": []})

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
    def decision_items(self) -> list[dict]:
        if self.schema_version not in {"0.5", "0.6"}:
            return []
        return list(self.gates.get("decisions", []))

    @property
    def evidence_items(self) -> list[dict]:
        return list(self.evidence.get("evidence", []))

    @property
    def integration_items(self) -> list[dict]:
        return list(self.integrations.get("integrations", []))

    @property
    def schema_version(self) -> str | None:
        versions = {
            data.get("schema_version")
            for data in (self.project, self.authorities, self.gates, self.evidence, self.integrations)
            if isinstance(data.get("schema_version"), str)
        }
        if len(versions) == 1:
            return next(iter(versions))
        return None


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
        integrations=_read_json(manifest_root / "integrations.json"),
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


def decision_sequence(decision: dict) -> int | None:
    did = decision.get("id")
    gid = decision.get("gate_id")
    if not isinstance(did, str) or not isinstance(gid, str):
        return None
    match = _DECISION_ID_RE.fullmatch(did)
    if not match or match.group("gate") != gid:
        return None
    return int(match.group("seq"))


def current_decisions_by_gate(manifests: ManifestSet) -> dict[str, dict]:
    if manifests.schema_version not in {"0.5", "0.6"}:
        return {}
    decisions = manifests.decision_items
    superseded = {
        item.get("supersedes")
        for item in decisions
        if isinstance(item.get("supersedes"), str)
    }
    result: dict[str, dict] = {}
    for gate in manifests.gate_items:
        gid = gate.get("id")
        if not isinstance(gid, str):
            continue
        heads = [
            item for item in decisions
            if item.get("gate_id") == gid and item.get("id") not in superseded
        ]
        if len(heads) == 1:
            result[gid] = heads[0]
    return result


def validate_manifests(manifests: ManifestSet, *, strict_gate_validity: bool = True) -> list[str]:
    errors: list[str] = []

    manifest_docs = [
        ("project", manifests.project), ("authorities", manifests.authorities),
        ("gates", manifests.gates), ("evidence", manifests.evidence),
        ("integrations", manifests.integrations),
    ]
    versions: set[str] = set()
    for name, data in manifest_docs:
        version = data.get("schema_version")
        if version not in SUPPORTED_SCHEMA_VERSIONS:
            errors.append(f"{name}: unsupported schema_version {version!r}; expected one of {', '.join(sorted(SUPPORTED_SCHEMA_VERSIONS))}")
        elif isinstance(version, str):
            versions.add(version)
    if len(versions) > 1:
        errors.append("manifest schema_version values must match")
    schema_version = next(iter(versions)) if len(versions) == 1 else None

    project = manifests.project.get("project")
    if not isinstance(project, dict):
        errors.append("project: project must be an object")
    else:
        for required in ("id", "name", "profile"):
            if not isinstance(project.get(required), str) or not project.get(required):
                errors.append(f"project: missing non-empty {required}")
        if project.get("profile") not in {"lite", "standard", "full"}:
            errors.append("project: profile must be lite, standard, or full")

    authorities = manifests.authority_items
    gates = manifests.gate_items
    decisions = manifests.decision_items
    evidence = manifests.evidence_items
    integrations = manifests.integration_items
    reviews = manifests.impact_reviews

    registry_items = [
        ("authority", authorities), ("gate", gates), ("evidence", evidence),
        ("integration", integrations), ("impact review", reviews),
    ]
    if schema_version in {"0.5", "0.6"}:
        registry_items.append(("gate decision", decisions))
    for registry_name, items in registry_items:
        for duplicate in sorted(_duplicates(items, "id")):
            errors.append(f"duplicate {registry_name} id: {duplicate}")

    auth_by_id = {item.get("id"): item for item in authorities if isinstance(item.get("id"), str)}
    gate_by_id = {item.get("id"): item for item in gates if isinstance(item.get("id"), str)}
    decision_by_id = {item.get("id"): item for item in decisions if isinstance(item.get("id"), str)}
    evidence_by_id = {item.get("id"): item for item in evidence if isinstance(item.get("id"), str)}

    def integration_gate_id(item: dict) -> str | None:
        if schema_version == "0.6":
            binding = item.get("gate_decision_binding")
            decision_item = decision_by_id.get(binding.get("gate_decision_id")) if isinstance(binding, dict) and binding.get("kind") == "bound" else None
            gid = decision_item.get("gate_id") if decision_item else None
            return gid if isinstance(gid, str) else None
        if schema_version == "0.5":
            decision_item = decision_by_id.get(item.get("gate_decision_id"))
            gid = decision_item.get("gate_id") if decision_item else None
            return gid if isinstance(gid, str) else None
        gid = item.get("gate_id")
        return gid if isinstance(gid, str) else None

    completed_history_gate_ids = {
        gid
        for item in integrations
        if item.get("status") in {"integrated", "closed_unmerged"}
        for gid in [integration_gate_id(item)]
        if gid is not None
    }

    current_by_scope_kind: dict[tuple[str, str], list[str]] = {}
    for item in authorities:
        aid = item.get("id")
        for required in ("id", "scope", "kind", "version", "status", "ref"):
            if not isinstance(item.get(required), str) or not item.get(required):
                errors.append(f"authority {aid or '<unknown>'}: missing non-empty {required}")
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
        for required in ("id", "type", "ref", "status"):
            if not isinstance(item.get(required), str) or not item.get(required):
                errors.append(f"evidence {eid or '<unknown>'}: missing non-empty {required}")
        if item.get("status") not in EVIDENCE_STATUSES:
            errors.append(f"evidence {eid}: invalid status {item.get('status')}")

    current_decisions: dict[str, dict] = {}
    if schema_version in {"0.5", "0.6"}:
        decisions_by_gate: dict[str, list[dict]] = {str(g.get("id")): [] for g in gates if isinstance(g.get("id"), str)}
        child_map: dict[str, list[str]] = {}
        lineage_graph: dict[str, list[str]] = {}
        gate_lineage_error: set[str] = set()

        for gate in gates:
            gid = gate.get("id")
            for required in ("id", "stage"):
                if not isinstance(gate.get(required), str) or not gate.get(required):
                    errors.append(f"gate {gid or '<unknown>'}: missing non-empty {required}")
            authority_ids = gate.get("authority_ids", [])
            if not isinstance(authority_ids, list) or not all(isinstance(x, str) for x in authority_ids):
                errors.append(f"gate {gid}: authority_ids must be a string array")
                authority_ids = []
            for aid in authority_ids:
                if aid not in auth_by_id:
                    errors.append(f"gate {gid}: dangling authority id {aid}")

        for item in decisions:
            did = item.get("id")
            gid = item.get("gate_id")
            if not isinstance(did, str) or not did:
                errors.append("gate decision <unknown>: missing non-empty id")
                continue
            if not isinstance(gid, str) or not gid:
                errors.append(f"gate decision {did}: missing non-empty gate_id")
                continue
            if gid not in gate_by_id:
                errors.append(f"gate decision {did}: dangling gate id {gid}")
            else:
                decisions_by_gate.setdefault(gid, []).append(item)
            if item.get("verdict") not in GATE_VERDICTS:
                errors.append(f"gate decision {did}: invalid verdict {item.get('verdict')}")
            evidence_ids = item.get("evidence_ids", [])
            if not isinstance(evidence_ids, list) or not all(isinstance(x, str) for x in evidence_ids):
                errors.append(f"gate decision {did}: evidence_ids must be a string array")
                evidence_ids = []
            for eid in evidence_ids:
                if eid not in evidence_by_id:
                    errors.append(f"gate decision {did}: dangling evidence id {eid}")
            if item.get("verdict") in PASS_VERDICTS and not evidence_ids:
                errors.append(f"PASS gate decision {did} requires evidence")
            seq = decision_sequence(item)
            if seq is None or seq < 1:
                errors.append(f"gate decision {did}: decision id must match gate_id and four-digit sequence")
                gate_lineage_error.add(gid)
            supersedes = item.get("supersedes")
            lineage_graph[did] = [supersedes] if isinstance(supersedes, str) else []
            if isinstance(supersedes, str):
                target = decision_by_id.get(supersedes)
                if target is None:
                    errors.append(f"gate decision {did}: dangling supersedes target {supersedes}")
                    gate_lineage_error.add(gid)
                elif target.get("gate_id") != gid:
                    errors.append(f"gate decision {did}: cross-gate supersedes target {supersedes}")
                    gate_lineage_error.add(gid)
                child_map.setdefault(supersedes, []).append(did)

        found = _cycle(lineage_graph)
        if found:
            errors.append(f"decision lineage cycle: {' -> '.join(found)}")
            for did in found:
                item = decision_by_id.get(did)
                if item and isinstance(item.get("gate_id"), str):
                    gate_lineage_error.add(item["gate_id"])

        for parent, children in child_map.items():
            if len(children) > 1:
                errors.append(f"decision lineage fork at {parent}: {', '.join(sorted(children))}")
                target = decision_by_id.get(parent)
                if target and isinstance(target.get("gate_id"), str):
                    gate_lineage_error.add(target["gate_id"])

        for gate in gates:
            gid = gate.get("id")
            if not isinstance(gid, str):
                continue
            items = decisions_by_gate.get(gid, [])
            if not items:
                errors.append(f"gate {gid}: requires at least one gate decision")
                gate_lineage_error.add(gid)
                continue
            seq_items = [(decision_sequence(item), item) for item in items]
            valid_sequences = sorted(seq for seq, _ in seq_items if isinstance(seq, int) and seq >= 1)
            expected = list(range(1, len(items) + 1))
            if valid_sequences != expected:
                errors.append(f"gate {gid}: decision lineage sequence must be contiguous from 0001")
                gate_lineage_error.add(gid)
            by_seq = {seq: item for seq, item in seq_items if isinstance(seq, int) and seq >= 1}
            first = by_seq.get(1)
            if first and first.get("supersedes") is not None:
                errors.append(f"gate {gid}: decision lineage root 0001 must not supersede another decision")
                gate_lineage_error.add(gid)
            for seq in range(2, len(items) + 1):
                item = by_seq.get(seq)
                prev = by_seq.get(seq - 1)
                if not item or not prev:
                    continue
                if item.get("supersedes") != prev.get("id"):
                    errors.append(f"gate {gid}: decision lineage sequence {seq:04d} must supersede {seq - 1:04d}")
                    gate_lineage_error.add(gid)
            superseded = {
                item.get("supersedes") for item in items if isinstance(item.get("supersedes"), str)
            }
            heads = [item for item in items if item.get("id") not in superseded]
            if len(heads) != 1:
                errors.append(f"gate {gid}: decision lineage requires exactly one unsuperseded head")
                gate_lineage_error.add(gid)
            if gid not in gate_lineage_error and len(heads) == 1:
                current_decisions[gid] = heads[0]

        if strict_gate_validity:
            for gid, current in current_decisions.items():
                if current.get("verdict") not in PASS_VERDICTS:
                    continue
                gate = gate_by_id.get(gid, {})
                authority_ids = list(gate.get("authority_ids") or [])
                authority_statuses = [auth_by_id.get(aid, {}).get("status") for aid in authority_ids]
                all_current = bool(authority_statuses) and all(status in {"Current", "Proposed"} for status in authority_statuses)
                all_historical = bool(authority_statuses) and all(status in {"Superseded", "Historical"} for status in authority_statuses)
                historical_provenance = gid in completed_history_gate_ids and all_historical
                if not all_current and not historical_provenance:
                    for aid in authority_ids:
                        authority = auth_by_id.get(aid)
                        if authority and authority.get("status") not in {"Current", "Proposed"}:
                            errors.append(f"current PASS gate {gid} depends on non-current authority {aid}")
                if all_current:
                    for eid in current.get("evidence_ids", []):
                        ev = evidence_by_id.get(eid)
                        if ev and ev.get("status") != "available":
                            errors.append(f"current PASS gate {gid} uses unavailable evidence {eid}")
    else:
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
                authority_statuses = [auth_by_id.get(aid, {}).get("status") for aid in authority_ids]
                all_current = bool(authority_statuses) and all(status in {"Current", "Proposed"} for status in authority_statuses)
                all_historical = bool(authority_statuses) and all(status in {"Superseded", "Historical"} for status in authority_statuses)
                historical_provenance = gid in completed_history_gate_ids and all_historical
                if not all_current and not historical_provenance:
                    for aid in authority_ids:
                        authority = auth_by_id.get(aid)
                        if authority and authority.get("status") not in {"Current", "Proposed"}:
                            errors.append(f"current PASS gate {gid} depends on non-current authority {aid}")
                if all_current:
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

    for integration in integrations:
        iid = integration.get("id")
        required = ("id", "kind", "ref", "status", "target_ref") + (("gate_decision_id",) if schema_version == "0.5" else (("gate_id",) if schema_version not in {"0.6"} else ()))
        for name in required:
            if not isinstance(integration.get(name), str) or not integration.get(name):
                errors.append(f"integration {iid or '<unknown>'}: missing non-empty {name}")
        if integration.get("status") not in INTEGRATION_STATUSES:
            errors.append(f"integration {iid}: invalid status {integration.get('status')}")

        decision_item = None
        gate = None
        gate_id = None
        if schema_version == "0.6":
            binding = integration.get("gate_decision_binding")
            if "gate_decision_id" in integration:
                errors.append(f"integration {iid}: legacy gate_decision_id is forbidden in v0.6")
            if not isinstance(binding, dict) or binding.get("kind") not in {"bound", "absent"}:
                errors.append(f"integration {iid}: gate_decision_binding must be bound or absent")
            elif binding.get("kind") == "bound":
                if "reason" in binding:
                    errors.append(f"integration {iid}: bound binding must not contain absent reason")
                gate_decision_id = binding.get("gate_decision_id")
                decision_item = decision_by_id.get(gate_decision_id)
                if not isinstance(gate_decision_id, str) or gate_decision_id not in decision_by_id:
                    errors.append(f"integration {iid}: dangling gate decision {gate_decision_id}")
                if decision_item:
                    gate_id = decision_item.get("gate_id")
                    gate = gate_by_id.get(gate_id)
            elif binding.get("reason") != "no_applicable_integration_gate_decision":
                errors.append(f"integration {iid}: absent binding requires canonical reason")
            elif "gate_decision_id" in binding:
                errors.append(f"integration {iid}: absent binding must not contain gate_decision_id")
        elif schema_version == "0.5":
            gate_decision_id = integration.get("gate_decision_id")
            decision_item = decision_by_id.get(gate_decision_id)
            if gate_decision_id not in decision_by_id:
                errors.append(f"integration {iid}: dangling gate decision {gate_decision_id}")
            if decision_item:
                gate_id = decision_item.get("gate_id")
                gate = gate_by_id.get(gate_id)
        else:
            gate_id = integration.get("gate_id")
            gate = gate_by_id.get(gate_id)
            if gate_id not in gate_by_id:
                errors.append(f"integration {iid}: dangling gate id {gate_id}")

        evidence_ids = integration.get("evidence_ids", [])
        if not isinstance(evidence_ids, list) or not all(isinstance(x, str) for x in evidence_ids):
            errors.append(f"integration {iid}: evidence_ids must be a string array")
            evidence_ids = []
        for eid in evidence_ids:
            if eid not in evidence_by_id:
                errors.append(f"integration {iid}: dangling evidence id {eid}")
        status = integration.get("status")
        binding = integration.get("gate_decision_binding") if schema_version == "0.6" else None
        if schema_version == "0.6":
            kind = binding.get("kind") if isinstance(binding, dict) else None
            if status in {"awaiting_integration", "closed_unmerged"} and kind != "bound":
                errors.append(f"integration {iid}: {status} requires bound gate_decision_binding")
            if status == "integrated" and kind not in {"bound", "absent"}:
                errors.append(f"integration {iid}: integrated requires bound or absent gate_decision_binding")
        revision = integration.get("integrated_revision")
        if status == "integrated" and (not isinstance(revision, str) or not revision):
            errors.append(f"integration {iid}: integrated_revision is required when status=integrated")
        if status != "integrated" and revision is not None:
            errors.append(f"integration {iid}: integrated_revision is only allowed when status=integrated")
        if strict_gate_validity and status == "integrated":
            if schema_version == "0.3" and gate and gate.get("verdict") not in PASS_VERDICTS:
                errors.append(f"integration {iid}: requires historical PASS/PASS_WITH_FINDINGS gate {gate_id}")
            for eid in evidence_ids:
                ev = evidence_by_id.get(eid)
                if ev and ev.get("status") != "available":
                    errors.append(f"integration {iid}: uses unavailable evidence {eid}")
        if strict_gate_validity and status == "awaiting_integration":
            if schema_version in {"0.5", "0.6"}:
                current = current_decisions.get(str(gate_id)) if gate_id is not None else None
                if not decision_item or current is not decision_item or decision_item.get("verdict") not in PASS_VERDICTS:
                    errors.append(f"integration {iid}: requires current PASS/PASS_WITH_FINDINGS gate decision {integration.get('gate_decision_id')}")
            elif gate:
                if gate.get("verdict") not in PASS_VERDICTS:
                    errors.append(f"integration {iid}: requires PASS/PASS_WITH_FINDINGS gate {gate_id}")
                if gate.get("validity") != "current":
                    errors.append(f"integration {iid}: requires current gate {gate_id}")
            for eid in evidence_ids:
                ev = evidence_by_id.get(eid)
                if ev and ev.get("status") != "available":
                    errors.append(f"integration {iid}: uses unavailable evidence {eid}")

    if strict_gate_validity and integrations and not errors:
        from .compute import compute_state

        derived = compute_state(manifests)
        noncurrent_gate_ids = (
            set(derived.get("stale_gates", []))
            | set(derived.get("needs_review_gates", []))
            | set(derived.get("historical_gates", []))
        )
        for integration in integrations:
            if integration.get("status") != "awaiting_integration":
                continue
            gate_id = integration_gate_id(integration)
            if gate_id in noncurrent_gate_ids:
                errors.append(f"integration {integration.get('id')}: requires current-valid gate {gate_id}")

    return errors
