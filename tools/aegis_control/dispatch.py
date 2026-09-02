"""Committed-outbox dispatch boundary for Control Plane CP-I05.

Dispatch is operational delivery only. It has no canonical mutation primitive
and cannot turn provider acknowledgement into semantic completion.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping

from .canonical import canonical_digest
from .execution_surface import DispatchReceipt
from .recovery import delivery_is_uncertain, dispatch_retry_delay_seconds
from .store import ControlStore, StoreConflict
from .trust import TrustFactRequest, TrustResolver, _validate_exact_trust_ref


class DispatchRejected(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class DispatchAuthorization:
    authorized: bool
    code: str
    basis_digest: str | None = None


class DispatchAuthorizationResolver:
    """Resolve Current dispatch authorization from exact external trust facts."""

    def __init__(
        self,
        trust_resolver: TrustResolver,
        request: TrustFactRequest,
        *,
        source_primary_owner: str,
    ):
        self._trust_resolver = trust_resolver
        self._request = request
        self._source_primary_owner = source_primary_owner

    def resolve(self, occurrence: Mapping[str, Any]) -> DispatchAuthorization:
        resolution = self._trust_resolver.resolve_for_mutation([self._request])
        if not resolution.valid:
            return DispatchAuthorization(False, "DISPATCH_NOT_AUTHORIZED")
        fresh = self._trust_resolver.verify_freshness(resolution)
        if not fresh.valid or not fresh.resolved_refs:
            return DispatchAuthorization(False, "DISPATCH_NOT_AUTHORIZED")
        try:
            for ref in fresh.resolved_refs:
                _validate_exact_trust_ref(ref)
        except (TypeError, ValueError):
            return DispatchAuthorization(False, "DISPATCH_NOT_AUTHORIZED")

        target_owner = occurrence.get("primary_owner")
        if target_owner != self._source_primary_owner:
            return DispatchAuthorization(False, "CURRENT_CROSS_PRIMARY_ROLLOUT_DENIED")
        basis = {
            "source_primary_owner": self._source_primary_owner,
            "target_primary_owner": target_owner,
            "request": {
                "source_kind": self._request.source_kind,
                "resource_key": self._request.resource_key,
            },
            "resolved_refs": list(fresh.resolved_refs),
            "snapshot_tokens": [item.snapshot_token for item in fresh.snapshots],
        }
        return DispatchAuthorization(True, "DISPATCH_AUTHORIZED", canonical_digest(basis))


class DispatchService:
    """Deliver committed outbox entries without owning canonical write authority."""

    def __init__(
        self,
        store: ControlStore,
        execution_surface: Any,
        *,
        authorization_resolver: DispatchAuthorizationResolver,
        fault_injector: Callable[[str], None] | None = None,
    ):
        self._store = store
        self._execution_surface = execution_surface
        self._authorization_resolver = authorization_resolver
        self._fault_injector = fault_injector

    def dispatch(self, outbox_id: str, *, attempted_at: str) -> DispatchReceipt:
        outbox = self._store.read_outbox_entry(outbox_id)
        if outbox is None:
            raise DispatchRejected("OUTBOX_NOT_FOUND")
        occurrence = self._store.read_latest("STAGE_OCCURRENCE", outbox["occurrence_id"])
        if occurrence is None or occurrence.record.get("state") != "OPEN":
            raise DispatchRejected("OCCURRENCE_NOT_OPEN")

        authorization = self._authorization_resolver.resolve(occurrence.record)
        if not authorization.authorized:
            raise DispatchRejected(authorization.code)

        expected_ref = (
            f"STAGE_OCCURRENCE:{occurrence.record['id']}@{occurrence.record['record_revision']}#"
            f"{occurrence.digest}"
        )
        payload = outbox.get("payload")
        if not isinstance(payload, Mapping) or payload.get("occurrence_ref") != expected_ref:
            raise DispatchRejected("OCCURRENCE_REF_MISMATCH")

        attempted = _parse_time(attempted_at)
        previous = self._store.read_delivery_state(outbox_id)
        if previous is not None and previous.get("next_attempt_at"):
            eligible = _parse_time(previous["next_attempt_at"])
            if attempted < eligible:
                raise DispatchRejected("RETRY_NOT_YET_ELIGIBLE")

        prior_attempts = int(previous["attempt_count"]) if previous else 0
        attempt_number = prior_attempts + 1
        next_attempt = attempted + timedelta(
            seconds=dispatch_retry_delay_seconds(attempt_number)
        )
        known_correlation = previous.get("provider_correlation_id") if previous else None
        try:
            delivery = self._store.record_delivery_attempt(
                outbox_id,
                attempted_at,
                next_attempt_at=_format_time(next_attempt),
                provider_state="ATTEMPTING" if known_correlation is None else None,
            )
        except StoreConflict as exc:
            raise DispatchRejected("DELIVERY_STATE_CONFLICT") from exc

        first_attempt = _parse_time(delivery["first_attempt_at"])
        elapsed = max(0, int((attempted - first_attempt).total_seconds()))
        if delivery_is_uncertain(
            attempt_count=int(delivery["attempt_count"]), elapsed_seconds=elapsed
        ):
            try:
                delivery = self._store.record_delivery_diagnostic(
                    outbox_id,
                    "DELIVERY_UNCERTAIN",
                    observed_at=attempted_at,
                )
            except StoreConflict as exc:
                raise DispatchRejected("DELIVERY_STATE_CONFLICT") from exc

        envelope = {
            "outbox_id": outbox_id,
            "occurrence_id": occurrence.record["id"],
            "occurrence_ref": expected_ref,
            "control_lane_id": outbox["control_lane_id"],
            "payload": dict(payload),
            "authorization_basis_digest": authorization.basis_digest,
        }
        receipt = self._execution_surface.dispatch(envelope)
        if not isinstance(receipt, DispatchReceipt) or not receipt.acknowledged:
            raise DispatchRejected("PROVIDER_DISPATCH_NOT_ACKNOWLEDGED")
        if receipt.occurrence_id != occurrence.record["id"] or not receipt.correlation_id:
            raise DispatchRejected("PROVIDER_CORRELATION_MISMATCH")
        self._checkpoint("after_provider_dispatch")
        current_correlation = delivery.get("provider_correlation_id")
        if current_correlation is not None and current_correlation != receipt.correlation_id:
            raise DispatchRejected("DELIVERY_STATE_CONFLICT")
        if current_correlation is None:
            try:
                self._store.record_delivery_correlation(
                    outbox_id,
                    receipt.correlation_id,
                    observed_at=attempted_at,
                    provider_state="ACCEPTED",
                )
            except StoreConflict as exc:
                raise DispatchRejected("DELIVERY_STATE_CONFLICT") from exc
        return DispatchReceipt(
            receipt.occurrence_id,
            receipt.correlation_id,
            receipt.acknowledged,
            authorization.basis_digest,
        )

    def _checkpoint(self, name: str) -> None:
        if self._fault_injector is not None:
            self._fault_injector(name)


def _parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise DispatchRejected("INVALID_DELIVERY_TIMESTAMP")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise DispatchRejected("INVALID_DELIVERY_TIMESTAMP") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
