"""Independent CP-I01 Control Reference Model (O-CRM).

This module is intentionally test/reference-only and imports no production
Control Plane control-flow implementation.
"""

from __future__ import annotations

from collections import deque
from typing import Iterable, Mapping


ALLOWED_OPERATIONS = (
    "MATERIALIZE_IMPLEMENTATION_PACKAGE",
    "REVISE_IMPLEMENTATION_PACKAGE",
    "SCHEDULE_STAGE_OCCURRENCE",
    "RECORD_EXECUTION_PROGRESS",
    "TERMINATE_STAGE_OCCURRENCE",
    "RAISE_ESCALATION",
    "RECORD_ESCALATION_RESOLUTION",
    "SCHEDULE_REPAIR_OCCURRENCE",
    "SCHEDULE_REVERIFICATION_OCCURRENCE",
    "SCHEDULE_REREVIEW_OCCURRENCE",
    "RECOMPUTE_CONTROL_PROJECTION",
)


def is_legal_operation(operation_name: str) -> bool:
    return operation_name in ALLOWED_OPERATIONS


def _is_ancestor(ancestor: str, descendant: str, ancestry: Iterable[tuple[str, str]]) -> bool:
    if ancestor == descendant:
        return True
    edges: dict[str, set[str]] = {}
    for parent, child in ancestry:
        edges.setdefault(parent, set()).add(child)
    queue = deque([ancestor])
    seen = {ancestor}
    while queue:
        node = queue.popleft()
        for child in edges.get(node, ()):
            if child == descendant:
                return True
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return False


def classify_p33(task_anchor_revision: str, observed_revision: str, cursor_revision: str | None, ancestry: Iterable[tuple[str, str]]) -> str:
    if cursor_revision is not None:
        if observed_revision == cursor_revision:
            return "EXACT_CURSOR"
        if _is_ancestor(cursor_revision, observed_revision, ancestry):
            return "DESCENDANT_CURSOR"
        return "DIVERGED"
    if _is_ancestor(task_anchor_revision, observed_revision, ancestry):
        return "ANCHOR_DESCENDANT_WITHOUT_CURSOR"
    return "DIVERGED"


def detect_semantic_violations(trace: Mapping[str, object]) -> set[str]:
    violations: set[str] = set()
    event_order = list(trace.get("event_order", []))
    if "DISPATCH" in event_order and "OPEN_OUTBOX_COMMIT" in event_order and event_order.index("DISPATCH") < event_order.index("OPEN_OUTBOX_COMMIT"):
        violations.add("DISPATCH_BEFORE_COMMIT")
    delivery_ids = list(trace.get("delivery_occurrence_ids", []))
    if delivery_ids and len(set(delivery_ids)) > 1:
        violations.add("DELIVERY_CREATED_SEMANTIC_RETRY")
    writers = set(trace.get("canonical_writers", []))
    if writers - {"control-mutation"}:
        violations.add("SECOND_CANONICAL_WRITER")
    if trace.get("snapshot_accepted") and trace.get("snapshot_version") != trace.get("current_provider_version"):
        violations.add("STALE_SNAPSHOT_ACCEPTED")
    required = set(trace.get("required_child_ids", []))
    bindings = set(trace.get("required_child_acceptance_bindings", []))
    if trace.get("successor_scheduled") and not required.issubset(bindings):
        violations.add("REQUIRED_CHILD_BARRIER_BYPASS")
    if trace.get("historical_basis_source") == "CURRENT_PROJECTION":
        violations.add("HISTORICAL_FACT_FROM_CURRENT_PROJECTION")
    if trace.get("terminal_and_successor_same_transaction"):
        violations.add("TERMINAL_SUCCESSOR_COLLAPSED")
    if trace.get("restart_created_new_occurrence"):
        violations.add("RESTART_CREATED_SEMANTIC_RETRY")
    if trace.get("gate_pass_inferred") and trace.get("gate_source") in {"CI", "PROOF_EVALUATION"}:
        violations.add("GATE_INFERRED_FROM_NON_GATE_SOURCE")
    if trace.get("execution_cursor_authorizes_scope"):
        violations.add("EXECUTION_CURSOR_USED_AS_AUTHORITY")
    if trace.get("cross_primary_auto_dispatch") and not trace.get("rollout_authorized"):
        violations.add("UNAUTHORIZED_CROSS_PRIMARY_DISPATCH")
    if trace.get("stale_projection_authorized_mutation"):
        violations.add("STALE_PROJECTION_AUTHORIZED_MUTATION")
    if trace.get("schedule_acknowledged") and not trace.get("outbox_persisted"):
        violations.add("ACKNOWLEDGED_SCHEDULE_WITHOUT_OUTBOX")
    if trace.get("manual_duplicate_active_work"):
        violations.add("UNSAFE_MANUAL_DUPLICATE")
    if trace.get("terminal_history_rewritten"):
        violations.add("TERMINAL_HISTORY_REWRITTEN")
    return violations


def successor_allowed(required_child_ids: Iterable[str], accepted_child_ids: Iterable[str]) -> bool:
    return set(required_child_ids).issubset(set(accepted_child_ids))


def derive_projection(occurrences: Iterable[Mapping[str, object]]) -> dict[str, object]:
    records = list(occurrences)
    if not records:
        return {"active_occurrence_id": None, "last_terminal_occurrence_id": None}
    active = [r for r in records if r.get("state") == "OPEN"]
    terminal = [r for r in records if r.get("state") == "TERMINAL"]
    return {
        "active_occurrence_id": active[-1].get("id") if active else None,
        "last_terminal_occurrence_id": terminal[-1].get("id") if terminal else None,
    }
