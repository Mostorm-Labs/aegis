"""Execution-surface boundary for Control Plane CP-I05.

This module deliberately owns no canonical write capability. Provider
acknowledgement, correlation, navigation, and materialization are observations
that must be reconciled before control-mutation can append canonical truth.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence


EXECUTION_SURFACES = {
    "CONTROL_REASONING",
    "CODE_EXECUTION",
    "CONTROL_REVIEW",
    "CODE_REVERIFY",
}


@dataclass(frozen=True)
class DispatchReceipt:
    occurrence_id: str
    correlation_id: str
    acknowledged: bool
    authorization_basis_digest: str | None = None


@dataclass(frozen=True)
class ProviderObservation:
    occurrence_id: str
    correlation_id: str
    state: str
    execution_ref: str | None = None
    execution_revision: str | None = None
    completed_through: tuple[str, ...] = ()
    next_action: str | None = None
    materialized_ref: Mapping[str, Any] | None = None
    reviewer_accessible: bool = False  # legacy observation only; never a trust decision


@dataclass(frozen=True)
class ResumeClassification:
    state: str
    accepted_revision: str | None
    completed_through: tuple[str, ...] = ()
    next_action: str | None = None
    replay_completed_work: bool = False
    blocker: str | None = None


@dataclass(frozen=True)
class ExecutionPositionVerification:
    valid: bool
    code: str
    classification: ResumeClassification | None = None


def validate_execution_navigation_shape(value: Mapping[str, Any] | None) -> bool:
    """Validate the exact P12 ExecutionNavigationSnapshot shape."""
    if not isinstance(value, Mapping) or set(value) != {
        "execution_surface", "task_anchor", "execution_cursor"
    }:
        return False
    if value.get("execution_surface") not in EXECUTION_SURFACES:
        return False
    anchor = value.get("task_anchor")
    if (
        not isinstance(anchor, Mapping)
        or set(anchor) != {"revision", "relation"}
        or not isinstance(anchor.get("revision"), str)
        or not anchor.get("revision")
        or anchor.get("relation") != "ancestor"
    ):
        return False
    cursor = value.get("execution_cursor")
    if (
        not isinstance(cursor, Mapping)
        or set(cursor) != {"execution_ref", "revision", "completed_through", "next_action"}
        or not isinstance(cursor.get("execution_ref"), str)
        or not cursor.get("execution_ref")
        or not isinstance(cursor.get("revision"), str)
        or not cursor.get("revision")
        or not isinstance(cursor.get("completed_through"), list)
        or any(not isinstance(item, str) or not item for item in cursor["completed_through"])
        or not isinstance(cursor.get("next_action"), str)
        or not cursor.get("next_action")
    ):
        return False
    return True


class ExecutionPositionResolver:
    """Validate that an authored checkpoint is already reconciled under P33.

    A checkpoint may be persisted only when its task anchor matches the authorized
    task and its cursor equals the execution surface's current exact revision.
    Descendant discovery is useful to P33 transient reconciliation, but the old
    cursor itself is not accepted as a new canonical checkpoint.
    """

    def __init__(
        self,
        *,
        authorized_task_anchor: str,
        current_revision: Callable[[str], str | None],
        is_ancestor: Callable[[str, str], bool],
    ):
        self._authorized_task_anchor = authorized_task_anchor
        self._current_revision = current_revision
        self._is_ancestor = is_ancestor

    def verify_checkpoint(self, navigation: Mapping[str, Any]) -> ExecutionPositionVerification:
        if not validate_execution_navigation_shape(navigation):
            return ExecutionPositionVerification(False, "INVALID_EXECUTION_NAVIGATION")
        anchor = navigation["task_anchor"]
        if anchor["revision"] != self._authorized_task_anchor or anchor["relation"] != "ancestor":
            return ExecutionPositionVerification(False, "EXECUTION_NAVIGATION_DIVERGENCE")
        cursor = navigation["execution_cursor"]
        observed = self._current_revision(cursor["execution_ref"])
        if observed is None:
            return ExecutionPositionVerification(False, "EXECUTION_NAVIGATION_DIVERGENCE")
        classification = classify_resume(
            task_anchor_revision=self._authorized_task_anchor,
            resume_cursor={
                "revision": cursor["revision"],
                "completed_through": cursor["completed_through"],
                "next_action": cursor["next_action"],
            },
            observed_revision=observed,
            is_ancestor=self._is_ancestor,
        )
        if classification.state != "EXACT_CURSOR":
            return ExecutionPositionVerification(
                False, "EXECUTION_NAVIGATION_DIVERGENCE", classification
            )
        return ExecutionPositionVerification(True, "EXECUTION_NAVIGATION_VALID", classification)


class DeterministicExecutionSurface:
    """Deterministic provider fake with occurrence-scoped transport deduplication."""

    def __init__(self):
        self._by_occurrence: dict[str, str] = {}
        self._observations: dict[str, ProviderObservation] = {}
        self._execution_ref_by_occurrence: dict[str, str] = {}
        self._current_revision_by_ref: dict[str, str] = {}
        self._revision_parent: dict[str, str] = {}
        self.provider_request_count = 0
        self.query_count = 0

    @property
    def unique_execution_count(self) -> int:
        return len(self._by_occurrence)

    def seed_execution(
        self,
        *,
        occurrence_id: str,
        correlation_id: str,
        execution_ref: str,
        revision: str,
        state: str,
        completed_through: Sequence[str],
        next_action: str,
        materialized_ref: Mapping[str, Any] | None = None,
    ) -> ProviderObservation:
        if not all(isinstance(item, str) and item for item in (
            occurrence_id, correlation_id, execution_ref, revision, state, next_action
        )):
            raise ValueError("execution seed identities are required")
        existing = self._by_occurrence.get(occurrence_id)
        if existing is not None and existing != correlation_id:
            raise ValueError("occurrence already has another correlation")
        self._by_occurrence[occurrence_id] = correlation_id
        self._execution_ref_by_occurrence[occurrence_id] = execution_ref
        self._current_revision_by_ref[execution_ref] = revision
        observation = ProviderObservation(
            occurrence_id=occurrence_id,
            correlation_id=correlation_id,
            state=state,
            execution_ref=execution_ref,
            execution_revision=revision,
            completed_through=tuple(completed_through),
            next_action=next_action,
            materialized_ref=deepcopy(dict(materialized_ref)) if isinstance(materialized_ref, Mapping) else None,
        )
        self._observations[correlation_id] = observation
        return observation

    def current_revision(self, execution_ref: str) -> str | None:
        return self._current_revision_by_ref.get(execution_ref)

    def set_execution_revision(
        self,
        execution_ref: str,
        revision: str,
        *,
        ancestor_revision: str | None = None,
    ) -> None:
        if ancestor_revision is not None:
            self._revision_parent[revision] = ancestor_revision
        self._current_revision_by_ref[execution_ref] = revision

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        if ancestor == descendant:
            return True
        seen: set[str] = set()
        cursor = descendant
        while cursor in self._revision_parent and cursor not in seen:
            seen.add(cursor)
            cursor = self._revision_parent[cursor]
            if cursor == ancestor:
                return True
        return False

    def dispatch(self, envelope: Mapping[str, Any]) -> DispatchReceipt:
        occurrence_id = envelope.get("occurrence_id")
        if not isinstance(occurrence_id, str) or not occurrence_id:
            raise ValueError("occurrence_id is required")
        self.provider_request_count += 1
        correlation_id = self._by_occurrence.get(occurrence_id)
        if correlation_id is None:
            correlation_id = f"exec_{occurrence_id}"
            execution_ref = f"execution://{occurrence_id}"
            revision = f"provider-{occurrence_id}-r1"
            self.seed_execution(
                occurrence_id=occurrence_id,
                correlation_id=correlation_id,
                execution_ref=execution_ref,
                revision=revision,
                state="ACCEPTED",
                completed_through=(),
                next_action="implementation",
            )
        return DispatchReceipt(occurrence_id, correlation_id, True)

    def query(self, correlation_id: str) -> ProviderObservation:
        self.query_count += 1
        observation = self._observations.get(correlation_id)
        if observation is None:
            raise KeyError(correlation_id)
        return observation

    def set_observation(
        self,
        correlation_id: str,
        *,
        state: str,
        execution_ref: str | None = None,
        execution_revision: str | None = None,
        completed_through: Sequence[str] | None = None,
        next_action: str | None = None,
        materialized_ref: Mapping[str, Any] | None = None,
        reviewer_accessible: bool = False,
    ) -> ProviderObservation:
        current = self._observations.get(correlation_id)
        if current is None:
            raise KeyError(correlation_id)
        resolved_ref = execution_ref or current.execution_ref
        resolved_revision = execution_revision or current.execution_revision
        if resolved_ref is not None and resolved_revision is not None:
            previous = self._current_revision_by_ref.get(resolved_ref)
            if previous is not None and previous != resolved_revision and not self.is_ancestor(previous, resolved_revision):
                self._revision_parent.setdefault(resolved_revision, previous)
            self._current_revision_by_ref[resolved_ref] = resolved_revision
            self._execution_ref_by_occurrence[current.occurrence_id] = resolved_ref
        observation = ProviderObservation(
            occurrence_id=current.occurrence_id,
            correlation_id=correlation_id,
            state=state,
            execution_ref=resolved_ref,
            execution_revision=resolved_revision,
            completed_through=tuple(
                current.completed_through if completed_through is None else completed_through
            ),
            next_action=current.next_action if next_action is None else next_action,
            materialized_ref=deepcopy(dict(materialized_ref)) if isinstance(materialized_ref, Mapping) else None,
            reviewer_accessible=bool(reviewer_accessible),
        )
        self._observations[correlation_id] = observation
        return observation

    def navigation_snapshot(
        self,
        observation: ProviderObservation,
        *,
        execution_surface: str,
        task_anchor_revision: str,
    ) -> Mapping[str, Any]:
        if (
            execution_surface not in EXECUTION_SURFACES
            or not observation.execution_ref
            or not observation.execution_revision
            or not observation.next_action
        ):
            raise ValueError("provider observation is not a reconciled navigation checkpoint")
        return {
            "execution_surface": execution_surface,
            "task_anchor": {"revision": task_anchor_revision, "relation": "ancestor"},
            "execution_cursor": {
                "execution_ref": observation.execution_ref,
                "revision": observation.execution_revision,
                "completed_through": list(observation.completed_through),
                "next_action": observation.next_action,
            },
        }


def classify_resume(
    *,
    task_anchor_revision: str,
    resume_cursor: Mapping[str, Any] | None,
    observed_revision: str,
    is_ancestor: Callable[[str, str], bool],
) -> ResumeClassification:
    """Classify repository position under the accepted four-state P33 contract."""
    if resume_cursor is not None:
        cursor_revision = resume_cursor.get("revision")
        completed = tuple(resume_cursor.get("completed_through") or ())
        next_action = resume_cursor.get("next_action")
        if cursor_revision == observed_revision:
            return ResumeClassification(
                "EXACT_CURSOR", observed_revision, completed, next_action, False, None
            )
        if isinstance(cursor_revision, str) and is_ancestor(cursor_revision, observed_revision):
            return ResumeClassification(
                "DESCENDANT_CURSOR", observed_revision, completed, next_action, False, None
            )
        return ResumeClassification(
            "DIVERGED", None, completed, next_action, False, "BLOCKED_EXECUTION_DIVERGENCE"
        )

    if task_anchor_revision == observed_revision or is_ancestor(task_anchor_revision, observed_revision):
        return ResumeClassification(
            "ANCHOR_DESCENDANT_WITHOUT_CURSOR", observed_revision, (), None, False, None
        )
    return ResumeClassification(
        "DIVERGED", None, (), None, False, "BLOCKED_EXECUTION_DIVERGENCE"
    )
