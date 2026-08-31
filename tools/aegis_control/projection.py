"""Deterministic, disposable derived-state projection for Control Plane CP-I03."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .canonical import canonical_digest
from .store import ControlStore, StoredRecord

PROJECTION_ALGORITHM_VERSION = "cp-i03-projection-v0.1"


@dataclass(frozen=True)
class ControlCursor:
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
class ControlProjection:
    algorithm_version: str
    control_cursor: ControlCursor
    current_macro_phase: str
    repair_lineage: tuple[str, ...]
    open_escalations: tuple[str, ...]
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
    def __init__(self, store: ControlStore, *, cache: ProjectionCache | None = None):
        self._store = store
        self._cache = cache

    def project_lane(
        self,
        lane_id: str,
        trust_snapshot_bundle: Mapping[str, Any] | None = None,
    ) -> ControlProjection:
        lane = self._store.read_lane_head(lane_id)
        latest = self._store.read_lane_latest_records(lane_id)
        trust_snapshot = dict(trust_snapshot_bundle or {})
        state_token = tuple((record.record["kind"], record.record["id"], record.digest) for record in latest)
        trust_digest = canonical_digest(trust_snapshot)
        cache_key = (
            lane_id,
            lane.version,
            lane.occurrence_ref,
            state_token,
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

        macro_phase, next_action = self._derive_phase_and_action(current)
        summary = LifecycleSummary(
            occurrence_lineages=len(occurrences),
            open_occurrences=sum(item.record.get("state") == "OPEN" for item in occurrences.values()),
            terminal_occurrences=sum(item.record.get("state") == "TERMINAL" for item in occurrences.values()),
            open_escalations=len(open_escalations),
        )
        basis_payload = {
            "algorithm_version": PROJECTION_ALGORITHM_VERSION,
            "control_lane_id": lane_id,
            "lane_version": lane.version,
            "lane_head_ref": lane.occurrence_ref,
            "latest_record_digests": list(state_token),
            "trust_snapshot_digest": trust_digest,
        }
        projection = ControlProjection(
            algorithm_version=PROJECTION_ALGORITHM_VERSION,
            control_cursor=ControlCursor(
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
            next_legal_action=next_action,
            lifecycle_summary=summary,
            projection_basis_digest=canonical_digest(basis_payload),
        )
        if self._cache is not None:
            self._cache.put(cache_key, projection)
        return projection

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
