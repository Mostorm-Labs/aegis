"""Deterministic, disposable derived-state projection for Control Plane CP-I03/CP-I04."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from .canonical import canonical_digest
from .store import ControlStore, StoredRecord
from .trust import TrustResolver

PROJECTION_ALGORITHM_VERSION = "cp-i04-projection-v0.2"


@dataclass(frozen=True)
class ControlCursor:
    work_scope_ref: Mapping[str, Any] | None
    control_lane_id: str
    lane_version: int
    lane_head_ref: str | None
    current_occurrence_ref: str | None
    active_occurrence_id: str | None
    last_terminal_occurrence_id: str | None


@dataclass(frozen=True)
class LifecycleSummary:
    occurrence_lineages: int
    open_occurrences: int
    terminal_occurrences: int
    open_escalations: int


@dataclass(frozen=True)
class ChildWorkState:
    work_scope_ref: Mapping[str, Any]
    control_lane_id: str
    completed: bool
    accepted_for_parent: bool
    accepted_fact_refs: tuple[Mapping[str, Any], ...]
    blocking_reason: str | None


@dataclass(frozen=True)
class ControlProjection:
    algorithm_version: str
    control_cursor: ControlCursor
    current_macro_phase: str
    repair_lineage: tuple[str, ...]
    open_escalations: tuple[str, ...]
    child_work: tuple[ChildWorkState, ...]
    next_legal_action: str
    lifecycle_summary: LifecycleSummary
    projection_basis_digest: str


class ProjectionCache:
    """Process-local disposable cache; it owns no canonical or lifecycle truth."""

    def __init__(self):
        self._values: dict[tuple[object, ...], ControlProjection] = {}

    def get(self, key: tuple[object, ...]) -> ControlProjection | None:
        return self._values.get(key)

    def put(self, key: tuple[object, ...], projection: ControlProjection) -> None:
        self._values[key] = projection

    def invalidate_lane(self, lane_id: str) -> None:
        self._values = {key: value for key, value in self._values.items() if key[0] != lane_id}

    def clear(self) -> None:
        self._values.clear()


class ProjectionEngine:
    def __init__(
        self,
        store: ControlStore,
        *,
        cache: ProjectionCache | None = None,
        trust_resolver: TrustResolver | None = None,
    ):
        self._store = store
        self._cache = cache
        self._trust_resolver = trust_resolver

    def project_lane(
        self,
        lane_id: str,
        trust_snapshot_bundle: Mapping[str, Any] | None = None,
    ) -> ControlProjection:
        lane = self._store.read_lane_head(lane_id)
        latest = self._store.read_lane_latest_records(lane_id)
        global_occurrences = self._store.read_latest_stage_occurrences()
        trust_snapshot = dict(trust_snapshot_bundle or {})
        state_token = tuple((record.record["kind"], record.record["id"], record.digest) for record in latest)
        work_scope_ref = self._lane_work_scope(latest)
        child_state_token = tuple(
            sorted(
                (item.record["id"], item.digest)
                for item in global_occurrences
                if self._is_child_of(item.record.get("work_scope_ref"), work_scope_ref)
            )
        )
        trust_digest = canonical_digest(trust_snapshot)
        cache_key = (
            lane_id,
            lane.version,
            lane.occurrence_ref,
            state_token,
            child_state_token,
            trust_digest,
            PROJECTION_ALGORITHM_VERSION,
        )
        if self._cache is not None:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        occurrences = {
            item.record["id"]: item
            for item in latest
            if item.record.get("kind") == "STAGE_OCCURRENCE"
        }
        escalations = {
            item.record["id"]: item
            for item in latest
            if item.record.get("kind") == "ESCALATION"
        }
        current = self._current_occurrence(lane.occurrence_ref, occurrences)
        active_id = current.record["id"] if current is not None and current.record.get("state") == "OPEN" else None
        last_terminal_id = self._last_terminal_occurrence_id(current, occurrences)
        current_ref = _record_ref(current) if current is not None else None

        resolved_escalation_ids: set[str] = set()
        for occurrence in occurrences.values():
            terminal = occurrence.record.get("terminal")
            if isinstance(terminal, Mapping):
                resolved_escalation_ids.update(terminal.get("resolved_escalation_ids") or [])
        open_escalations = tuple(sorted(set(escalations) - resolved_escalation_ids))

        repair_items: list[tuple[int, str]] = []
        for occurrence in occurrences.values():
            context = occurrence.record.get("repair_context")
            if isinstance(context, Mapping):
                ordinal = context.get("attempt_ordinal")
                repair_items.append((ordinal if isinstance(ordinal, int) else 0, occurrence.record["id"]))
        repair_lineage = tuple(item[1] for item in sorted(repair_items))

        child_work = self._project_child_work(work_scope_ref, global_occurrences)
        macro_phase, next_action = self._derive_phase_and_action(current)
        if next_action == "SCHEDULE_SUCCESSOR" and any(
            child.blocking_reason is not None
            and child.work_scope_ref.get("child_work_binding", {}).get("parent_gate") == "REQUIRED"
            for child in child_work
        ):
            next_action = "WAIT_FOR_REQUIRED_CHILD"

        summary = LifecycleSummary(
            occurrence_lineages=len(occurrences),
            open_occurrences=sum(item.record.get("state") == "OPEN" for item in occurrences.values()),
            terminal_occurrences=sum(item.record.get("state") == "TERMINAL" for item in occurrences.values()),
            open_escalations=len(open_escalations),
        )
        basis_payload = {
            "algorithm_version": PROJECTION_ALGORITHM_VERSION,
            "control_lane_id": lane_id,
            "work_scope_ref": work_scope_ref,
            "lane_version": lane.version,
            "lane_head_ref": lane.occurrence_ref,
            "latest_record_digests": list(state_token),
            "child_record_digests": list(child_state_token),
            "child_work": [
                {
                    "work_scope_ref": child.work_scope_ref,
                    "control_lane_id": child.control_lane_id,
                    "completed": child.completed,
                    "accepted_for_parent": child.accepted_for_parent,
                    "accepted_fact_refs": list(child.accepted_fact_refs),
                    "blocking_reason": child.blocking_reason,
                }
                for child in child_work
            ],
            "trust_snapshot_digest": trust_digest,
        }
        projection = ControlProjection(
            algorithm_version=PROJECTION_ALGORITHM_VERSION,
            control_cursor=ControlCursor(
                work_scope_ref=deepcopy(work_scope_ref) if work_scope_ref is not None else None,
                control_lane_id=lane_id,
                lane_version=lane.version,
                lane_head_ref=lane.occurrence_ref,
                current_occurrence_ref=current_ref,
                active_occurrence_id=active_id,
                last_terminal_occurrence_id=last_terminal_id,
            ),
            current_macro_phase=macro_phase,
            repair_lineage=repair_lineage,
            open_escalations=open_escalations,
            child_work=child_work,
            next_legal_action=next_action,
            lifecycle_summary=summary,
            projection_basis_digest=canonical_digest(basis_payload),
        )
        if self._cache is not None:
            self._cache.put(cache_key, projection)
        return projection

    def replay_required_child_acceptance(self, occurrence_id: str) -> tuple[Mapping[str, Any], ...]:
        """Replay immutable historical transition basis without consulting current trust."""
        revisions = self._store.read_revisions("STAGE_OCCURRENCE", occurrence_id)
        if not revisions:
            raise KeyError(occurrence_id)
        schedule_basis = revisions[0].record.get("schedule_basis")
        bindings = schedule_basis.get("required_child_acceptance_bindings") if isinstance(schedule_basis, Mapping) else None
        if not isinstance(bindings, list):
            return ()
        return tuple(deepcopy(bindings))

    def _project_child_work(
        self,
        parent_scope: Mapping[str, Any] | None,
        global_occurrences: list[StoredRecord],
    ) -> tuple[ChildWorkState, ...]:
        if parent_scope is None:
            return ()
        child_scopes: dict[str, Mapping[str, Any]] = {}
        for item in global_occurrences:
            scope = item.record.get("work_scope_ref")
            if self._is_child_of(scope, parent_scope):
                child_scopes.setdefault(scope["id"], deepcopy(dict(scope)))
        values = [self._project_one_child(scope, global_occurrences) for scope in child_scopes.values()]
        return tuple(sorted(values, key=lambda item: item.work_scope_ref["id"]))

    def _project_one_child(
        self,
        child_scope: Mapping[str, Any],
        global_occurrences: list[StoredRecord],
    ) -> ChildWorkState:
        child_id = child_scope["id"]
        records = [
            item for item in global_occurrences
            if isinstance(item.record.get("work_scope_ref"), Mapping)
            and item.record["work_scope_ref"].get("id") == child_id
        ]
        lanes = {item.record.get("control_lane_id") for item in records}
        if len(lanes) != 1:
            return ChildWorkState(child_scope, "", False, False, (), "WORK_SCOPE_LANE_CONFLICT")
        lane_id = next(iter(lanes))
        lane = self._store.read_lane_head(lane_id)
        current_id = _occurrence_id_from_internal_ref(lane.occurrence_ref)
        current = self._store.read_latest("STAGE_OCCURRENCE", current_id) if current_id else None
        completed = bool(
            current is not None
            and current.record.get("state") == "TERMINAL"
            and isinstance(current.record.get("terminal"), Mapping)
            and current.record["terminal"].get("outcome_category") == "COMPLETED"
            and not self._unresolved_child_escalations(child_id, records)
        )
        if not completed:
            return ChildWorkState(child_scope, lane_id, False, False, (), "CHILD_INCOMPLETE")

        binding = child_scope.get("child_work_binding")
        contracts = binding.get("acceptance_contract_refs") if isinstance(binding, Mapping) else []
        if not contracts:
            return ChildWorkState(child_scope, lane_id, True, True, (), None)
        if self._trust_resolver is None:
            return ChildWorkState(child_scope, lane_id, True, False, (), "REQUIRED_CHILD_WORK_NOT_ACCEPTED")
        support = self._trust_resolver.resolve_child_acceptance(
            child_scope,
            _canonical_occurrence_ref(current),
            contracts,
        )
        if not support.accepted:
            return ChildWorkState(child_scope, lane_id, True, False, (), support.code)
        fresh = self._trust_resolver.verify_freshness(support.snapshot_resolution)
        if not fresh.valid:
            return ChildWorkState(child_scope, lane_id, True, False, (), fresh.code)
        return ChildWorkState(
            child_scope,
            lane_id,
            True,
            True,
            tuple(deepcopy(list(support.acceptance_fact_refs))),
            None,
        )

    def _unresolved_child_escalations(self, child_id: str, child_occurrences: list[StoredRecord]) -> bool:
        resolved: set[str] = set()
        for occurrence in child_occurrences:
            terminal = occurrence.record.get("terminal")
            if isinstance(terminal, Mapping):
                resolved.update(terminal.get("resolved_escalation_ids") or [])
        for escalation in self._store.read_latest_escalations():
            scope = escalation.record.get("work_scope_ref")
            if isinstance(scope, Mapping) and scope.get("id") == child_id and escalation.record["id"] not in resolved:
                return True
        return False

    @staticmethod
    def _lane_work_scope(latest: list[StoredRecord]) -> Mapping[str, Any] | None:
        scopes = [
            item.record.get("work_scope_ref")
            for item in latest
            if item.record.get("kind") == "STAGE_OCCURRENCE"
            and isinstance(item.record.get("work_scope_ref"), Mapping)
        ]
        if not scopes:
            return None
        first = scopes[0]
        return deepcopy(dict(first)) if all(scope == first for scope in scopes) else None

    @staticmethod
    def _is_child_of(scope: object, parent_scope: Mapping[str, Any] | None) -> bool:
        if not isinstance(scope, Mapping) or parent_scope is None:
            return False
        binding = scope.get("child_work_binding")
        parent = binding.get("parent_work_scope_ref") if isinstance(binding, Mapping) else None
        return isinstance(parent, Mapping) and parent.get("id") == parent_scope.get("id")

    @staticmethod
    def _current_occurrence(
        lane_head_ref: str | None,
        occurrences: Mapping[str, StoredRecord],
    ) -> StoredRecord | None:
        occurrence_id = _occurrence_id_from_internal_ref(lane_head_ref)
        return occurrences.get(occurrence_id) if occurrence_id is not None else None

    @staticmethod
    def _last_terminal_occurrence_id(
        current: StoredRecord | None,
        occurrences: Mapping[str, StoredRecord],
    ) -> str | None:
        if current is None:
            return None
        if current.record.get("state") == "TERMINAL":
            return current.record["id"]
        schedule_basis = current.record.get("schedule_basis")
        if isinstance(schedule_basis, Mapping):
            predecessor = schedule_basis.get("predecessor_occurrence_ref")
            predecessor_id = _canonical_ref_id(predecessor)
            if predecessor_id is None and isinstance(predecessor, str):
                predecessor_id = _occurrence_id_from_internal_ref(predecessor)
            record = occurrences.get(predecessor_id) if predecessor_id else None
            if record is not None and record.record.get("state") == "TERMINAL":
                return predecessor_id
        return None

    @staticmethod
    def _derive_phase_and_action(current: StoredRecord | None) -> tuple[str, str]:
        if current is None:
            return "IDLE", "SCHEDULE_INITIAL"
        if current.record.get("state") == "OPEN":
            return "ACTIVE", "WAIT_FOR_TERMINAL"
        terminal = current.record.get("terminal")
        outcome = terminal.get("outcome_category") if isinstance(terminal, Mapping) else None
        if outcome == "COMPLETED":
            return "TERMINAL_BOUNDARY", "SCHEDULE_SUCCESSOR"
        if outcome in {"BLOCKED", "ESCALATED"}:
            return "BLOCKED", "WAIT_FOR_RESOLUTION"
        if outcome == "FAILED_WITH_FINDING":
            return "REVIEW_REQUIRED", "REVIEW_FINDING"
        return "TERMINAL_BOUNDARY", "NO_ACTION"


def _record_ref(record: StoredRecord | None) -> str | None:
    if record is None:
        return None
    return (
        f"{record.record['kind']}:{record.record['id']}"
        f"@{record.record['record_revision']}#{record.digest}"
    )


def _canonical_occurrence_ref(record: StoredRecord) -> Mapping[str, Any]:
    return {
        "object_type": "STAGE_OCCURRENCE",
        "id": record.record["id"],
        "ref": f"control:STAGE_OCCURRENCE:{record.record['id']}@{record.record['record_revision']}",
        "identity": {"scheme": "sha256", "value": record.digest},
    }


def _occurrence_id_from_internal_ref(ref: str | None) -> str | None:
    if not isinstance(ref, str):
        return None
    try:
        prefix = ref.rsplit("#", 1)[0]
        kind_and_id = prefix.rsplit("@", 1)[0]
        kind, record_id = kind_and_id.split(":", 1)
    except ValueError:
        return None
    if kind != "STAGE_OCCURRENCE" or not record_id:
        return None
    return record_id


def _canonical_ref_id(ref: object) -> str | None:
    if isinstance(ref, Mapping) and ref.get("object_type") == "STAGE_OCCURRENCE":
        value = ref.get("id")
        return value if isinstance(value, str) and value else None
    return None
