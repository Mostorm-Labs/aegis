"""Reconciliation/recovery boundary for Control Plane CP-I05.

Age, callback loss, and delivery uncertainty are operational diagnostics. This
module does not author semantic failure or replacement StageOccurrences.
Canonical progress/completion, when derived, is submitted only through the
single MutationService writer.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from .execution_surface import ProviderObservation
from .mutation import MutationRejected, MutationService, semantic_fingerprint
from .store import ControlStore, StoreConflict


class ReconciliationBlocked(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class ReconciliationPolicy:
    interval_seconds: int
    operator_alert: bool
    semantic_terminalization: bool = False


def dispatch_retry_delay_seconds(attempt_count: int) -> int:
    if attempt_count < 1:
        raise ValueError("attempt_count must be positive")
    schedule = (1, 2, 4, 8, 16, 30, 60)
    if attempt_count <= len(schedule):
        return schedule[attempt_count - 1]
    return 300


def delivery_is_uncertain(*, attempt_count: int, elapsed_seconds: int) -> bool:
    if attempt_count < 0 or elapsed_seconds < 0:
        raise ValueError("attempt_count and elapsed_seconds must be non-negative")
    return attempt_count >= 12 or elapsed_seconds >= 1800


def reconciliation_policy(age_seconds: int) -> ReconciliationPolicy:
    if age_seconds < 0:
        raise ValueError("age_seconds must be non-negative")
    if age_seconds < 300:
        return ReconciliationPolicy(30, False)
    if age_seconds < 1800:
        return ReconciliationPolicy(120, False)
    if age_seconds < 7200:
        return ReconciliationPolicy(300, False)
    return ReconciliationPolicy(900, True)


class RecoveryCoordinator:
    """Query durable provider correlation and derive bounded canonical requests."""

    def __init__(
        self,
        store: ControlStore,
        execution_surface: Any,
        *,
        mutation: MutationService | None = None,
        task_anchor_revision: str | None = None,
        execution_surface_name: str | None = None,
    ):
        self._store = store
        self._execution_surface = execution_surface
        self._mutation = mutation
        self._task_anchor_revision = task_anchor_revision
        self._execution_surface_name = execution_surface_name

    def reconcile_outbox(
        self,
        outbox_id: str,
        *,
        observed_at: str,
        event_hint: bool = False,
    ) -> ProviderObservation:
        outbox = self._store.read_outbox_entry(outbox_id)
        if outbox is None:
            raise ReconciliationBlocked("OUTBOX_NOT_FOUND")
        delivery = self._store.read_delivery_state(outbox_id)
        if delivery is None or not delivery.get("provider_correlation_id"):
            raise ReconciliationBlocked("DELIVERY_CORRELATION_MISSING")
        self._require_query_eligibility(delivery, observed_at, event_hint=event_hint)

        correlation_id = delivery["provider_correlation_id"]
        try:
            observation = self._execution_surface.query(correlation_id)
        except KeyError as exc:
            raise ReconciliationBlocked("PROVIDER_CORRELATION_NOT_FOUND") from exc
        if not isinstance(observation, ProviderObservation):
            raise ReconciliationBlocked("PROVIDER_OBSERVATION_INVALID")
        if observation.occurrence_id != outbox["occurrence_id"]:
            raise ReconciliationBlocked("PROVIDER_CORRELATION_MISMATCH")
        try:
            self._store.record_delivery_correlation(
                outbox_id,
                correlation_id,
                observed_at=observed_at,
                provider_state=observation.state,
            )
        except StoreConflict as exc:
            raise ReconciliationBlocked("DELIVERY_STATE_CONFLICT") from exc

        if self._mutation is None:
            return observation
        current = self._store.read_latest("STAGE_OCCURRENCE", outbox["occurrence_id"])
        if current is None:
            raise ReconciliationBlocked("OCCURRENCE_NOT_FOUND")
        if current.record.get("state") == "TERMINAL":
            return observation
        if observation.state not in {"RUNNING", "MATERIALIZED"}:
            return observation
        if not self._task_anchor_revision or not self._execution_surface_name:
            raise ReconciliationBlocked("RECONCILIATION_CONFIGURATION_MISSING")
        try:
            navigation = self._execution_surface.navigation_snapshot(
                observation,
                execution_surface=self._execution_surface_name,
                task_anchor_revision=self._task_anchor_revision,
            )
        except (AttributeError, ValueError) as exc:
            raise ReconciliationBlocked("EXECUTION_NAVIGATION_DIVERGENCE") from exc

        if current.record.get("execution_navigation") != navigation:
            self._submit_progress(outbox, current.record, current.digest, navigation, observed_at)
            current = self._store.read_latest("STAGE_OCCURRENCE", outbox["occurrence_id"])
            assert current is not None

        if observation.state == "MATERIALIZED":
            if not isinstance(observation.materialized_ref, Mapping):
                raise ReconciliationBlocked("RESULT_MATERIALIZATION_REQUIRED")
            self._submit_terminal(
                outbox,
                current.record,
                current.digest,
                observation.materialized_ref,
                observed_at,
            )
        return observation

    def _require_query_eligibility(
        self,
        delivery: Mapping[str, Any],
        observed_at: str,
        *,
        event_hint: bool,
    ) -> None:
        if event_hint or not delivery.get("last_observed_at"):
            return
        now = _parse_time(observed_at)
        last = _parse_time(delivery["last_observed_at"])
        first_text = delivery.get("first_attempt_at") or delivery["last_observed_at"]
        first = _parse_time(first_text)
        age = max(0, int((now - first).total_seconds()))
        interval = reconciliation_policy(age).interval_seconds
        if (now - last).total_seconds() < interval:
            raise ReconciliationBlocked("RECONCILIATION_NOT_YET_ELIGIBLE")

    def _submit_progress(
        self,
        outbox: Mapping[str, Any],
        current: Mapping[str, Any],
        digest: str,
        navigation: Mapping[str, Any],
        observed_at: str,
    ) -> None:
        semantic = {
            "operation_name": "RECORD_EXECUTION_PROGRESS",
            "actor": {"class": "CONTROL_PLANE", "id": "control-recovery"},
            "control_lane_id": outbox["control_lane_id"],
            "expected_state": self._expected_state(current, digest),
            "payload": {
                "occurrence_id": current["id"],
                "recorded_at": observed_at,
                "execution_navigation": navigation,
            },
        }
        request = {
            **semantic,
            "operation_request_id": (
                "req_reconcile_progress_"
                + outbox["outbox_id"].replace("out_", "", 1)
                + "_"
                + navigation["execution_cursor"]["revision"].replace("/", "_")
            ),
            "idempotency_fingerprint": semantic_fingerprint(semantic),
        }
        try:
            self._mutation.apply(request)
        except MutationRejected as exc:
            raise ReconciliationBlocked(exc.code) from exc

    def _submit_terminal(
        self,
        outbox: Mapping[str, Any],
        current: Mapping[str, Any],
        digest: str,
        result_ref: Mapping[str, Any],
        observed_at: str,
    ) -> None:
        terminal = {
            "outcome_category": "COMPLETED",
            "status": "READY",
            "produced_refs": [dict(result_ref)],
            "finding_refs": [],
            "raised_escalation_ids": [],
            "resolved_escalation_ids": [],
            "earliest_untrusted_layer": None,
            "navigation_result": None,
        }
        semantic = {
            "operation_name": "TERMINATE_STAGE_OCCURRENCE",
            "actor": {"class": "CONTROL_PLANE", "id": "control-recovery"},
            "control_lane_id": outbox["control_lane_id"],
            "expected_state": self._expected_state(current, digest),
            "payload": {
                "occurrence_id": current["id"],
                "recorded_at": observed_at,
                "terminal": terminal,
            },
        }
        request = {
            **semantic,
            "operation_request_id": (
                "req_reconcile_terminal_" + outbox["outbox_id"].replace("out_", "", 1)
            ),
            "idempotency_fingerprint": semantic_fingerprint(semantic),
        }
        try:
            self._mutation.apply(request)
        except MutationRejected as exc:
            raise ReconciliationBlocked(exc.code) from exc

    @staticmethod
    def _expected_state(current: Mapping[str, Any], digest: str) -> Mapping[str, Any]:
        return {
            "active_occurrence_ref": None,
            "predecessor_occurrence_ref": None,
            "target_record_revision": current["record_revision"],
            "target_record_digest": digest,
            "trusted_basis_digest": None,
            "package_ref": None,
            "work_scope_ref": current["work_scope_ref"],
        }


def _parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ReconciliationBlocked("INVALID_RECONCILIATION_TIMESTAMP")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ReconciliationBlocked("INVALID_RECONCILIATION_TIMESTAMP") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
