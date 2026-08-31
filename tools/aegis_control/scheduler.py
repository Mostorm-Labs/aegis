"""Transient CP-I03 scheduler candidates with fresh mutation revalidation."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from .mutation import MutationRejected, MutationService, semantic_fingerprint
from .policy import PolicyDecision
from .projection import ControlProjection, ProjectionEngine
from .store import ControlStore


class SchedulingDenied(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class ScheduleCandidate:
    control_lane_id: str
    expected_lane_version: int
    expected_lane_ref: str | None
    predecessor_occurrence_ref: str | None
    projection_basis_digest: str
    policy_digest: str
    operation_request_id: str
    occurrence: Mapping[str, Any]


class Scheduler:
    """Planner/coordinator only; all canonical commits go through MutationService."""

    def __init__(self, store: ControlStore, mutation: MutationService):
        self._store = store
        self._mutation = mutation
        self._paused_lanes: set[str] = set()
        self._lease_hints: dict[str, str] = {}

    def derive_candidate(
        self,
        projection: ControlProjection,
        policy: PolicyDecision,
        occurrence: Mapping[str, Any],
    ) -> ScheduleCandidate:
        lane_id = projection.control_cursor.control_lane_id
        if lane_id in self._paused_lanes:
            raise SchedulingDenied("SCHEDULER_PAUSED")
        if not policy.auto_schedule_authorized or policy.mode != "AUTONOMOUS":
            raise SchedulingDenied("POLICY_DENIED_AUTO_SCHEDULE")
        if projection.next_legal_action not in {"SCHEDULE_INITIAL", "SCHEDULE_SUCCESSOR"}:
            raise SchedulingDenied("NO_SCHEDULABLE_ACTION")
        if not isinstance(occurrence, Mapping) or occurrence.get("control_lane_id") != lane_id:
            raise SchedulingDenied("CANDIDATE_LANE_MISMATCH")
        if occurrence.get("primary_owner") != policy.target_primary_owner:
            raise SchedulingDenied("CANDIDATE_OWNER_MISMATCH")

        predecessor_ref = (
            projection.control_cursor.current_occurrence_ref
            if projection.next_legal_action == "SCHEDULE_SUCCESSOR"
            else None
        )
        return ScheduleCandidate(
            control_lane_id=lane_id,
            expected_lane_version=projection.control_cursor.lane_version,
            expected_lane_ref=projection.control_cursor.lane_head_ref,
            predecessor_occurrence_ref=predecessor_ref,
            projection_basis_digest=projection.projection_basis_digest,
            policy_digest=policy.policy_digest,
            operation_request_id=f"req_sched_{occurrence['id']}",
            occurrence=deepcopy(dict(occurrence)),
        )

    def submit_candidate(self, candidate: ScheduleCandidate) -> Mapping[str, Any]:
        if candidate.control_lane_id in self._paused_lanes:
            raise MutationRejected("SCHEDULER_PAUSED")

        lane = self._store.read_lane_head(candidate.control_lane_id)
        if (
            lane.version != candidate.expected_lane_version
            or lane.occurrence_ref != candidate.expected_lane_ref
        ):
            raise MutationRejected("STALE_SCHEDULER_CANDIDATE")

        fresh_projection = ProjectionEngine(self._store).project_lane(candidate.control_lane_id)
        if fresh_projection.projection_basis_digest != candidate.projection_basis_digest:
            raise MutationRejected("STALE_SCHEDULER_CANDIDATE")

        expected_state = {
            "active_occurrence_ref": None,
            "predecessor_occurrence_ref": candidate.predecessor_occurrence_ref,
            "target_record_revision": None,
            "target_record_digest": None,
            "trusted_basis_digest": None,
            "package_ref": None,
        }
        semantic_request = {
            "operation_name": "SCHEDULE_STAGE_OCCURRENCE",
            "actor": {"class": "CONTROL_PLANE", "id": "control-scheduler"},
            "control_lane_id": candidate.control_lane_id,
            "expected_state": expected_state,
            "payload": {"occurrence": deepcopy(dict(candidate.occurrence))},
        }
        request = {
            **semantic_request,
            "operation_request_id": candidate.operation_request_id,
            "idempotency_fingerprint": semantic_fingerprint(semantic_request),
        }
        return self._mutation.apply(request)

    def pause(self, lane_id: str) -> None:
        self._paused_lanes.add(lane_id)

    def resume(self, lane_id: str) -> None:
        self._paused_lanes.discard(lane_id)

    def acquire_lease_hint(self, lane_id: str, worker_identity: str) -> None:
        self._lease_hints[lane_id] = worker_identity

    def release_lease_hint(self, lane_id: str, worker_identity: str) -> None:
        if self._lease_hints.get(lane_id) == worker_identity:
            self._lease_hints.pop(lane_id, None)
