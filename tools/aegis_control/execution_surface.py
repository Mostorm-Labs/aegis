"""Execution-surface boundary for Control Plane CP-I05.

This module deliberately owns no canonical write capability. Provider
acknowledgement, correlation, navigation, and materialization are observations
that must be reconciled before control-mutation can append canonical truth.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class DispatchReceipt:
    occurrence_id: str
    correlation_id: str
    acknowledged: bool


@dataclass(frozen=True)
class ProviderObservation:
    occurrence_id: str
    correlation_id: str
    state: str
    execution_revision: str | None = None
    materialized_ref: Mapping[str, Any] | None = None
    reviewer_accessible: bool = False


@dataclass(frozen=True)
class ResumeClassification:
    state: str
    accepted_revision: str | None
    completed_through: tuple[str, ...] = ()
    next_action: str | None = None
    replay_completed_work: bool = False
    blocker: str | None = None


class DeterministicExecutionSurface:
    """Deterministic provider fake with occurrence-scoped transport deduplication."""

    def __init__(self):
        self._by_occurrence: dict[str, str] = {}
        self._observations: dict[str, ProviderObservation] = {}
        self.provider_request_count = 0
        self.query_count = 0

    @property
    def unique_execution_count(self) -> int:
        return len(self._by_occurrence)

    def dispatch(self, envelope: Mapping[str, Any]) -> DispatchReceipt:
        occurrence_id = envelope.get("occurrence_id")
        if not isinstance(occurrence_id, str) or not occurrence_id:
            raise ValueError("occurrence_id is required")
        self.provider_request_count += 1
        correlation_id = self._by_occurrence.get(occurrence_id)
        if correlation_id is None:
            correlation_id = f"exec_{occurrence_id}"
            self._by_occurrence[occurrence_id] = correlation_id
            self._observations[correlation_id] = ProviderObservation(
                occurrence_id=occurrence_id,
                correlation_id=correlation_id,
                state="ACCEPTED",
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
        execution_revision: str | None = None,
        materialized_ref: Mapping[str, Any] | None = None,
        reviewer_accessible: bool = False,
    ) -> ProviderObservation:
        current = self._observations.get(correlation_id)
        if current is None:
            raise KeyError(correlation_id)
        observation = ProviderObservation(
            occurrence_id=current.occurrence_id,
            correlation_id=correlation_id,
            state=state,
            execution_revision=execution_revision,
            materialized_ref=deepcopy(dict(materialized_ref)) if isinstance(materialized_ref, Mapping) else None,
            reviewer_accessible=bool(reviewer_accessible),
        )
        self._observations[correlation_id] = observation
        return observation


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
