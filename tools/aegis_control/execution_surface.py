"""Execution-surface boundary for Control Plane CP-I05.

This module deliberately owns no canonical write capability. Provider
acknowledgement, correlation, navigation, and materialization are observations
that must be reconciled before control-mutation can append canonical truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any


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
