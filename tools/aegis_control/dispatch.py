"""Committed-outbox dispatch boundary for Control Plane CP-I05.

Dispatch is operational delivery only. It has no canonical mutation primitive
and cannot turn provider acknowledgement into semantic completion.
"""
from __future__ import annotations

from typing import Any, Mapping

from .execution_surface import DispatchReceipt
from .store import ControlStore, StoreConflict


class DispatchRejected(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class DispatchService:
    """Deliver committed outbox entries without owning canonical write authority."""

    def __init__(self, store: ControlStore, execution_surface: Any):
        self._store = store
        self._execution_surface = execution_surface

    def dispatch(
        self,
        outbox_id: str,
        *,
        dispatch_authorized: bool,
        attempted_at: str,
    ) -> DispatchReceipt:
        if not dispatch_authorized:
            raise DispatchRejected("DISPATCH_NOT_AUTHORIZED")

        outbox = self._store.read_outbox_entry(outbox_id)
        if outbox is None:
            raise DispatchRejected("OUTBOX_NOT_FOUND")
        occurrence = self._store.read_latest("STAGE_OCCURRENCE", outbox["occurrence_id"])
        if occurrence is None or occurrence.record.get("state") != "OPEN":
            raise DispatchRejected("OCCURRENCE_NOT_OPEN")

        expected_ref = (
            f"STAGE_OCCURRENCE:{occurrence.record['id']}@{occurrence.record['record_revision']}#"
            f"{occurrence.digest}"
        )
        payload = outbox.get("payload")
        if not isinstance(payload, Mapping) or payload.get("occurrence_ref") != expected_ref:
            raise DispatchRejected("OCCURRENCE_REF_MISMATCH")

        envelope = {
            "outbox_id": outbox_id,
            "occurrence_id": occurrence.record["id"],
            "occurrence_ref": expected_ref,
            "control_lane_id": outbox["control_lane_id"],
            "payload": dict(payload),
        }
        receipt = self._execution_surface.dispatch(envelope)
        if not isinstance(receipt, DispatchReceipt) or not receipt.acknowledged:
            raise DispatchRejected("PROVIDER_DISPATCH_NOT_ACKNOWLEDGED")
        if receipt.occurrence_id != occurrence.record["id"] or not receipt.correlation_id:
            raise DispatchRejected("PROVIDER_CORRELATION_MISMATCH")
        try:
            self._store.record_delivery_attempt(
                outbox_id,
                attempted_at,
                provider_state="ACCEPTED",
            )
            self._store.record_delivery_correlation(
                outbox_id,
                receipt.correlation_id,
                observed_at=attempted_at,
                provider_state="ACCEPTED",
            )
        except StoreConflict as exc:
            raise DispatchRejected("DELIVERY_STATE_CONFLICT") from exc
        return receipt
