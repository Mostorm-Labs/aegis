from __future__ import annotations

from copy import deepcopy

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record
from tools.aegis_control.canonical import canonical_digest


CP_I06_PACKAGE_REF = "5683e99f5c144ddddad926afd71ad03b6c85ff91"
CP_I06_TASK_ANCHOR = "7b3244417c5beba4c75d5eafd471083007fa1843"


def finding_ref(finding_id: str = "finding_cp_i06") -> dict:
    return {
        "object_type": "FINDING",
        "id": finding_id,
        "ref": f"finding://{finding_id}@1",
        "identity": {"scheme": "sha256", "value": canonical_digest({"finding": finding_id})},
    }


def terminal_occurrence(occurrence_id: str, lane_id: str, *, owner: str = "aegis-implementation") -> dict:
    record = occurrence_record(occurrence_id, lane_id)
    record["primary_owner"] = owner
    record["state"] = "TERMINAL"
    record["terminal"] = {
        "outcome_category": "COMPLETED",
        "status": "READY",
        "produced_refs": [],
        "finding_refs": [],
        "raised_escalation_ids": [],
        "resolved_escalation_ids": [],
        "earliest_untrusted_layer": None,
        "navigation_result": None,
    }
    return record


def repair_occurrence(
    occurrence_id: str,
    lane_id: str,
    *,
    finding: dict | None = None,
    root_occurrence_ref: dict | None = None,
    previous_attempt_occurrence_ref: dict | None = None,
    attempt_ordinal: int = 1,
    max_attempts: int = 2,
    allowed_classes: tuple[str, ...] = ("IMPLEMENTATION_DEFECT",),
    repair_class: str = "IMPLEMENTATION_DEFECT",
) -> dict:
    record = occurrence_record(occurrence_id, lane_id)
    finding = deepcopy(finding or finding_ref())
    policy = {
        "control_autonomy": "REVIEW_GUARDED",
        "repair_policy": {
            "allowed_classes": list(allowed_classes),
            "max_attempts": max_attempts,
            "require_reverification": True,
            "require_fresh_independent_review": True,
            "escalation_conditions": ["REPAIR_BUDGET_EXHAUSTED"],
        },
    }
    policy_digest = canonical_digest(policy)
    record["policy_binding"] = policy
    record["schedule_basis"] = {"reason_code": "REPAIR", "required_child_acceptance_bindings": []}
    record["repair_context"] = {
        "finding_ref": finding,
        "root_occurrence_ref": deepcopy(root_occurrence_ref),
        "previous_attempt_occurrence_ref": deepcopy(previous_attempt_occurrence_ref),
        "attempt_ordinal": attempt_ordinal,
        "repair_policy_digest": policy_digest,
        "repair_class": repair_class,
    }
    return record


def request(operation_name: str, request_id: str, lane_id: str, payload: dict, expected: dict | None = None) -> dict:
    return make_request(operation_name, request_id, lane_id, payload, expected or expected_state())
