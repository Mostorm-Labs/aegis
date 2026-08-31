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

FROZEN_OCCURRENCE_FIELDS = (
    "control_lane_id",
    "stage_span",
    "primary_owner",
    "trusted_basis",
    "policy_binding",
    "schedule_basis",
    "input_refs",
    "repair_context",
)

_OCCURRENCE_SCHEDULE_OPERATIONS = {
    "SCHEDULE_STAGE_OCCURRENCE",
    "SCHEDULE_REPAIR_OCCURRENCE",
    "SCHEDULE_REVERIFICATION_OCCURRENCE",
    "SCHEDULE_REREVIEW_OCCURRENCE",
}


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


def classify_p33(
    task_anchor_revision: str,
    observed_revision: str,
    cursor_revision: str | None,
    ancestry: Iterable[tuple[str, str]],
) -> str:
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
    if "DISPATCH" in event_order and "OPEN_OUTBOX_COMMIT" in event_order:
        if event_order.index("DISPATCH") < event_order.index("OPEN_OUTBOX_COMMIT"):
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


def _record_identity_matches(current: Mapping[str, object], proposed: Mapping[str, object]) -> bool:
    for field in ("kind", "id", "id_scheme"):
        if field in current or field in proposed:
            if current.get(field) != proposed.get(field):
                return False
    return True


def _expected_revision_matches(current: Mapping[str, object], expected_state: Mapping[str, object] | None) -> bool:
    if not expected_state or "target_record_revision" not in expected_state:
        return True
    return expected_state.get("target_record_revision") == current.get("record_revision")


def _next_revision_matches(current: Mapping[str, object], proposed: Mapping[str, object]) -> bool:
    current_revision = current.get("record_revision")
    proposed_revision = proposed.get("record_revision")
    return isinstance(current_revision, int) and proposed_revision == current_revision + 1


def _frozen_occurrence_facts_match(current: Mapping[str, object], proposed: Mapping[str, object]) -> bool:
    return all(current.get(field) == proposed.get(field) for field in FROZEN_OCCURRENCE_FIELDS)


def transition_violations(
    operation_name: str,
    current_record: Mapping[str, object] | None,
    proposed_record: Mapping[str, object] | None,
    expected_state: Mapping[str, object] | None = None,
) -> set[str]:
    """Independently classify representative P13 record-transition legality.

    This models semantic preconditions only; it is not a production mutation
    implementation and has no database, scheduler, policy, or dispatch dependency.
    """
    violations: set[str] = set()
    if operation_name not in ALLOWED_OPERATIONS:
        return {"UNKNOWN_OPERATION"}

    if operation_name == "RECOMPUTE_CONTROL_PROJECTION":
        if proposed_record is not None:
            violations.add("PROJECTION_MUTATED_CANONICAL")
        return violations

    if operation_name == "MATERIALIZE_IMPLEMENTATION_PACKAGE":
        if current_record is not None:
            violations.add("PACKAGE_ALREADY_EXISTS")
        if proposed_record is None or proposed_record.get("kind") != "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE":
            violations.add("WRONG_TARGET_KIND")
        elif proposed_record.get("record_revision") != 1:
            violations.add("INVALID_INITIAL_REVISION")
        return violations

    if operation_name in _OCCURRENCE_SCHEDULE_OPERATIONS:
        if proposed_record is None or proposed_record.get("kind") != "STAGE_OCCURRENCE":
            violations.add("WRONG_TARGET_KIND")
        else:
            if proposed_record.get("record_revision") != 1:
                violations.add("INVALID_INITIAL_REVISION")
            if proposed_record.get("state") != "OPEN":
                violations.add("SCHEDULE_MUST_CREATE_OPEN")
        return violations

    if operation_name == "RAISE_ESCALATION":
        if proposed_record is None or proposed_record.get("kind") != "ESCALATION":
            violations.add("WRONG_TARGET_KIND")
        elif proposed_record.get("record_revision") != 1:
            violations.add("ESCALATION_IMMUTABLE")
        return violations

    if current_record is None or proposed_record is None:
        return {"MISSING_TRANSITION_RECORD"}

    if not _record_identity_matches(current_record, proposed_record):
        violations.add("LINEAGE_IDENTITY_CHANGED")
    if not _expected_revision_matches(current_record, expected_state):
        violations.add("EXPECTED_REVISION_MISMATCH")
    if not _next_revision_matches(current_record, proposed_record):
        violations.add("NON_CONTIGUOUS_REVISION")

    if operation_name == "REVISE_IMPLEMENTATION_PACKAGE":
        if current_record.get("kind") != "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE" or proposed_record.get("kind") != "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE":
            violations.add("WRONG_TARGET_KIND")
        return violations

    if operation_name in {"RECORD_EXECUTION_PROGRESS", "TERMINATE_STAGE_OCCURRENCE", "RECORD_ESCALATION_RESOLUTION"}:
        if current_record.get("kind") != "STAGE_OCCURRENCE" or proposed_record.get("kind") != "STAGE_OCCURRENCE":
            violations.add("WRONG_TARGET_KIND")
            return violations
        if current_record.get("state") != "OPEN":
            violations.add("TARGET_NOT_OPEN")
        if not _frozen_occurrence_facts_match(current_record, proposed_record):
            violations.add("FROZEN_START_FACT_CHANGED")

        if operation_name == "RECORD_EXECUTION_PROGRESS":
            if proposed_record.get("state") != "OPEN":
                violations.add("PROGRESS_MUST_REMAIN_OPEN")
            if proposed_record.get("terminal") is not None:
                violations.add("PROGRESS_CANNOT_TERMINATE")
        else:
            if proposed_record.get("state") != "TERMINAL":
                violations.add("TERMINATION_MUST_BE_TERMINAL")
            if not isinstance(proposed_record.get("terminal"), Mapping):
                violations.add("TERMINAL_FACTS_REQUIRED")
        return violations

    return violations


def successor_allowed(required_child_ids: Iterable[str], accepted_child_ids: Iterable[str]) -> bool:
    return set(required_child_ids).issubset(set(accepted_child_ids))


def derive_projection(occurrences: Iterable[Mapping[str, object]]) -> dict[str, object]:
    """Derive a tiny deterministic expected projection for fixture comparison."""
    records = list(occurrences)
    if not records:
        return {"active_occurrence_id": None, "last_terminal_occurrence_id": None}
    active = [r for r in records if r.get("state") == "OPEN"]
    terminal = [r for r in records if r.get("state") == "TERMINAL"]
    return {
        "active_occurrence_id": active[-1].get("id") if active else None,
        "last_terminal_occurrence_id": terminal[-1].get("id") if terminal else None,
    }


def idempotency_expectation(existing_requests: Mapping[str, str], operation_request_id: str, fingerprint: str) -> str:
    existing = existing_requests.get(operation_request_id)
    if existing is None:
        return "EXECUTE"
    if existing == fingerprint:
        return "REPLAY"
    return "CONFLICT"


def lane_guard_matches(current_state: Mapping[str, object], expected_state: Mapping[str, object]) -> bool:
    for field in ("active_occurrence_ref", "predecessor_occurrence_ref"):
        if expected_state.get(field) != current_state.get(field):
            return False
    return True


def lineage_violations(records: Iterable[Mapping[str, object]]) -> set[str]:
    items = list(records)
    violations: set[str] = set()
    if not items:
        return {"EMPTY_LINEAGE"}

    first = items[0]
    stable_id = first.get("id")
    stable_kind = first.get("kind")
    stable_id_scheme = first.get("id_scheme")

    for expected_revision, record in enumerate(items, start=1):
        if record.get("id") != stable_id:
            violations.add("LINEAGE_ID_CHANGED")
        if stable_kind is not None or record.get("kind") is not None:
            if record.get("kind") != stable_kind:
                violations.add("LINEAGE_KIND_CHANGED")
        if stable_id_scheme is not None or record.get("id_scheme") is not None:
            if record.get("id_scheme") != stable_id_scheme:
                violations.add("LINEAGE_ID_SCHEME_CHANGED")
        if record.get("record_revision") != expected_revision:
            violations.add("NON_CONTIGUOUS_REVISION")

    if stable_kind == "ESCALATION":
        if len(items) != 1 or first.get("record_revision") != 1:
            violations.add("ESCALATION_IMMUTABLE")
        return violations

    if stable_kind in {None, "STAGE_OCCURRENCE"}:
        terminal_indexes = [index for index, record in enumerate(items) if record.get("state") == "TERMINAL"]
        if len(terminal_indexes) > 1:
            violations.add("MULTIPLE_TERMINAL_REVISIONS")
        if terminal_indexes and terminal_indexes[0] != len(items) - 1:
            violations.add("REVISION_AFTER_TERMINAL")
        if stable_kind == "STAGE_OCCURRENCE":
            if first.get("state") != "OPEN":
                violations.add("LINEAGE_MUST_START_OPEN")
            for record in items[1:]:
                if not _frozen_occurrence_facts_match(first, record):
                    violations.add("FROZEN_START_FACT_CHANGED")
        return violations

    if stable_kind == "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE":
        return violations

    return violations


def specialized_attempt_identity_is_legal(reason_code: str, previous_occurrence_id: str, new_occurrence_id: str) -> bool:
    if reason_code not in {"REPAIR", "REVERIFY", "REREVIEW"}:
        return False
    return bool(previous_occurrence_id and new_occurrence_id and previous_occurrence_id != new_occurrence_id)
