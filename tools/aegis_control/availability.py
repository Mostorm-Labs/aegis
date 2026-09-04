from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

QUERY_SLI = "QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY"


class AvailabilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class AvailabilityObservation:
    observation_id: str
    sli: str
    outcome: str
    store_healthy: bool | None = None
    external_provider_failure: bool = False
    provider_incident_ref: str | None = None
    local_path_healthy: bool | None = None
    exclusion_manifested: bool = False
    synthetic_probe: bool = False


@dataclass(frozen=True)
class ObservationClassification:
    observation_id: str
    classification: str


@dataclass(frozen=True)
class AvailabilityWindowResult:
    window_id: str
    status: str
    numerator: int
    denominator: int
    excluded: int
    ratio: float | None
    evidence_gaps: tuple[str, ...]
    historical_attainment_claimed: bool


def classify_observation(observation: AvailabilityObservation) -> ObservationClassification:
    if observation.outcome in {"SUCCESS", "SEMANTIC_4XX"}:
        return ObservationClassification(observation.observation_id, "GOOD")
    if observation.outcome != "FAILURE":
        return ObservationClassification(observation.observation_id, "BAD")
    if observation.sli == QUERY_SLI and observation.store_healthy is False:
        return ObservationClassification(observation.observation_id, "OUTSIDE_CONDITIONAL_DENOMINATOR")
    if (
        observation.external_provider_failure
        and observation.provider_incident_ref
        and observation.local_path_healthy is True
        and observation.exclusion_manifested
    ):
        return ObservationClassification(observation.observation_id, "EXCLUDED_EXTERNAL")
    return ObservationClassification(observation.observation_id, "BAD")


def evaluate_window(
    observations: Sequence[AvailabilityObservation],
    *,
    window_id: str,
    required_probe_intervals: int,
    complete_window: bool,
) -> AvailabilityWindowResult:
    if not isinstance(window_id, str) or not window_id.strip():
        raise AvailabilityError("OBSERVATION_WINDOW_ID_REQUIRED")
    if not isinstance(required_probe_intervals, int) or isinstance(required_probe_intervals, bool) or required_probe_intervals < 0:
        raise AvailabilityError("INVALID_REQUIRED_PROBE_INTERVALS")
    unique = {}
    for observation in observations:
        unique.setdefault(observation.observation_id, observation)
    classifications = [classify_observation(o) for o in unique.values()]
    numerator = sum(c.classification == "GOOD" for c in classifications)
    denominator = sum(c.classification in {"GOOD", "BAD"} for c in classifications)
    excluded = sum(c.classification in {"EXCLUDED_EXTERNAL", "OUTSIDE_CONDITIONAL_DENOMINATOR"} for c in classifications)
    probe_count = sum(o.synthetic_probe for o in unique.values())
    gaps: list[str] = []
    if probe_count < required_probe_intervals:
        gaps.append("MISSING_SYNTHETIC_PROBE_INTERVAL")
    if denominator == 0:
        gaps.append("INVALID_DENOMINATOR")
    if not complete_window:
        gaps.append("INCOMPLETE_WINDOW")
    status = "COMPLETE" if complete_window and not gaps else "INCOMPLETE"
    ratio = numerator / denominator if denominator else None
    return AvailabilityWindowResult(window_id, status, numerator, denominator, excluded, ratio, tuple(gaps), False)
