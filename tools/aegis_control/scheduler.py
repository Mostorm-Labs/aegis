"""Transient CP-I03 scheduler candidates with fresh mutation revalidation."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .canonical import canonical_digest
from .mutation import MutationRejected, MutationService, semantic_fingerprint
from .policy import PolicyDecision, PolicyEvaluator
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
    next_legal_action: str
    source_primary_owner: str
    target_primary_owner: str
    control_autonomy: str
    pinned_policy_binding_digest: str
    operation_request_id: str
    occurrence: Mapping[str, Any]


PolicyBasisResolver = Callable[[ScheduleCandidate], Mapping[str, Any] | None]


class Scheduler:
    """Planner/coordinator only; all canonical commits go through MutationService."""

    def __init__(
        self,
        store: ControlStore,
        mutation: MutationService,
        *,
        policy_basis_resolver: PolicyBasisResolver | None = None,
    ):
        self._store = store
        self._mutation = mutation
        self._policy_basis_resolver = policy_basis_resolver
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

        policy_binding = occurrence.get("policy_binding")
        if (
            not isinstance(policy_binding, Mapping)
            or policy_binding.get("control_autonomy") != policy.control_autonomy
        ):
            raise SchedulingDenied("CANDIDATE_POLICY_BINDING_MISMATCH")

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
            next_legal_action=projection.next_legal_action,
            source_primary_owner=policy.source_primary_owner,
            target_primary_owner=policy.target_primary_owner,
            control_autonomy=policy.control_autonomy,
            pinned_policy_binding_digest=canonical_digest(policy_binding),
            operation_request_id=f"req_sched_{occurrence['id']}",
            occurrence=deepcopy(dict(occurrence)),
        )

    def submit_candidate(self, candidate: ScheduleCandidate) -> Mapping[str, Any]:
        if candidate.control_lane_id in self._paused_lanes:
            raise MutationRejected("SCHEDULER_PAUSED")

        policy_binding = candidate.occurrence.get("policy_binding")
        if (
            not isinstance(policy_binding, Mapping)
            or policy_binding.get("control_autonomy") != candidate.control_autonomy
            or canonical_digest(policy_binding) != candidate.pinned_policy_binding_digest
            or candidate.occurrence.get("control_lane_id") != candidate.control_lane_id
            or candidate.occurrence.get("primary_owner") != candidate.target_primary_owner
        ):
            raise MutationRejected("CANDIDATE_POLICY_BINDING_MISMATCH")

        lane = self._store.read_lane_head(candidate.control_lane_id)
        if (
            lane.version != candidate.expected_lane_version
            or lane.occurrence_ref != candidate.expected_lane_ref
        ):
            raise MutationRejected("STALE_SCHEDULER_CANDIDATE")

        fresh_projection = ProjectionEngine(self._store).project_lane(candidate.control_lane_id)
        if fresh_projection.projection_basis_digest != candidate.projection_basis_digest:
            raise MutationRejected("STALE_SCHEDULER_CANDIDATE")

        if self._policy_basis_resolver is None:
            raise MutationRejected("MISSING_CURRENT_POLICY_BASIS")
        try:
            fresh_policy_basis = self._policy_basis_resolver(candidate)
        except Exception as exc:
            raise MutationRejected("CURRENT_POLICY_RESOLUTION_FAILED") from exc

        fresh_policy = PolicyEvaluator().evaluate_next_action(
            next_legal_action=candidate.next_legal_action,
            source_primary_owner=candidate.source_primary_owner,
            target_primary_owner=candidate.target_primary_owner,
            control_autonomy=candidate.control_autonomy,
            policy_basis=fresh_policy_basis,
        )
        if not fresh_policy.auto_schedule_authorized or fresh_policy.mode != "AUTONOMOUS":
            raise MutationRejected("POLICY_REVALIDATION_DENIED")
        if fresh_policy.policy_digest != candidate.policy_digest:
            raise MutationRejected("STALE_POLICY_AUTHORIZATION")

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
