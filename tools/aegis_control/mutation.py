"""Single canonical mutation boundary for the CP-I02 P13 subset."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping

from .canonical import (
    CanonicalValidationError, canonical_digest, validate_canonical_ref, validate_digest, validate_record,
)
from .store import ControlStore, StoreConflict, StoredRecord

SUPPORTED_OPERATIONS = {
    "MATERIALIZE_IMPLEMENTATION_PACKAGE",
    "REVISE_IMPLEMENTATION_PACKAGE",
    "SCHEDULE_STAGE_OCCURRENCE",
    "TERMINATE_STAGE_OCCURRENCE",
    "RAISE_ESCALATION",
}
KNOWN_LATER_OPERATIONS = {
    "RECORD_EXECUTION_PROGRESS",
    "RECORD_ESCALATION_RESOLUTION",
    "SCHEDULE_REPAIR_OCCURRENCE",
    "SCHEDULE_REVERIFICATION_OCCURRENCE",
    "SCHEDULE_REREVIEW_OCCURRENCE",
    "RECOMPUTE_CONTROL_PROJECTION",
}
EXPECTED_STATE_KEYS = {
    "active_occurrence_ref", "predecessor_occurrence_ref", "target_record_revision",
    "target_record_digest", "trusted_basis_digest", "package_ref",
}
ACTOR_CLASSES = {
    "CONTROL_PLANE", "PRIMARY_OWNER", "EXECUTION_SURFACE", "REVIEW_SURFACE",
    "HUMAN", "EXTERNAL_SYSTEM",
}
PACKAGE_FIELDS = {
    "schema_version", "kind", "id_scheme", "id", "record_revision", "recorded_at",
    "extensions", "control_lane_id", "trusted_basis", "scope", "verification_binding",
    "policy_binding", "task_anchor", "package_digest",
}
OCCURRENCE_FIELDS = {
    "schema_version", "kind", "id_scheme", "id", "record_revision", "recorded_at",
    "extensions", "control_lane_id", "stage_span", "primary_owner", "state",
    "trusted_basis", "policy_binding", "schedule_basis", "input_refs", "repair_context",
    "execution_navigation", "terminal",
}
TERMINAL_FIELDS = {
    "outcome_category", "status", "produced_refs", "finding_refs",
    "raised_escalation_ids", "resolved_escalation_ids", "earliest_untrusted_layer",
    "navigation_result",
}
BLOCKED_STATUSES = {
    "BLOCKED_AUTHORITY", "BLOCKED_MISSING_INPUT", "BLOCKED_UNRESOLVED_DECISION",
    "BLOCKED_EVIDENCE", "BLOCKED_IMPLEMENTATION", "BLOCKED_ENVIRONMENT",
}

ESCALATION_FIELDS = {
    "schema_version", "kind", "id_scheme", "id", "record_revision", "recorded_at",
    "extensions", "control_lane_id", "raised_from_occurrence_ref", "trusted_basis_digest",
    "category", "owning_layer", "required_decision", "evidence_snapshot_refs",
}


class MutationRejected(RuntimeError):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}: {detail}")


def semantic_fingerprint(request: Mapping[str, Any]) -> str:
    payload = {
        key: request[key]
        for key in ("operation_name", "actor", "control_lane_id", "expected_state", "payload")
    }
    return canonical_digest(payload)


class MutationService:
    def __init__(
        self,
        store: ControlStore,
        *,
        fault_injector: Callable[[str], None] | None = None,
        before_transaction: Callable[[], None] | None = None,
    ):
        self._store = store
        self._fault_injector = fault_injector
        self._before_transaction = before_transaction

    def apply(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        self._validate_request(request)
        operation = request["operation_name"]
        if operation in KNOWN_LATER_OPERATIONS or operation not in SUPPORTED_OPERATIONS:
            raise MutationRejected("UNSUPPORTED_OPERATION_IN_CP_I02", operation)
        if self._before_transaction is not None:
            self._before_transaction()
        with self._store._mutation_transaction() as tx:
            replay = tx.read_idempotency(request["operation_request_id"])
            if replay is not None:
                fingerprint, result = replay
                if fingerprint != request["idempotency_fingerprint"]:
                    raise MutationRejected("OPERATION_IDEMPOTENCY_CONFLICT")
                return result
            try:
                if operation == "MATERIALIZE_IMPLEMENTATION_PACKAGE":
                    result = self._materialize_package(tx, request)
                elif operation == "REVISE_IMPLEMENTATION_PACKAGE":
                    result = self._revise_package(tx, request)
                elif operation == "SCHEDULE_STAGE_OCCURRENCE":
                    result = self._schedule_occurrence(tx, request)
                elif operation == "TERMINATE_STAGE_OCCURRENCE":
                    result = self._terminate_occurrence(tx, request)
                elif operation == "RAISE_ESCALATION":
                    result = self._raise_escalation(tx, request)
                else:
                    raise MutationRejected("UNSUPPORTED_OPERATION_IN_CP_I02", operation)
            except StoreConflict as exc:
                raise MutationRejected("CANONICAL_STORE_CONFLICT", str(exc)) from exc
            tx.append_idempotency(
                request["operation_request_id"], request["idempotency_fingerprint"], result
            )
            self._checkpoint("after_idempotency")
            return result

    def _validate_request(self, request: Mapping[str, Any]) -> None:
        required = {
            "operation_name", "operation_request_id", "actor", "control_lane_id",
            "expected_state", "idempotency_fingerprint", "payload",
        }
        if not isinstance(request, Mapping) or set(request) != required:
            raise MutationRejected("INVALID_OPERATION_REQUEST_SHAPE")
        if not isinstance(request["operation_name"], str) or not request["operation_name"]:
            raise MutationRejected("INVALID_OPERATION_NAME")
        if not isinstance(request["operation_request_id"], str) or not request["operation_request_id"].startswith("req_"):
            raise MutationRejected("INVALID_OPERATION_REQUEST_ID")
        actor = request["actor"]
        if not isinstance(actor, Mapping) or set(actor) != {"class", "id"}:
            raise MutationRejected("INVALID_OPERATION_ACTOR")
        if actor["class"] not in ACTOR_CLASSES or not isinstance(actor["id"], str) or not actor["id"]:
            raise MutationRejected("INVALID_OPERATION_ACTOR")
        if not isinstance(request["control_lane_id"], str) or not request["control_lane_id"]:
            raise MutationRejected("INVALID_CONTROL_LANE")
        if not isinstance(request["expected_state"], Mapping) or set(request["expected_state"]) != EXPECTED_STATE_KEYS:
            raise MutationRejected("INVALID_EXPECTED_STATE")
        if not isinstance(request["payload"], Mapping):
            raise MutationRejected("INVALID_OPERATION_PAYLOAD")
        try:
            validate_digest(request["idempotency_fingerprint"])
        except CanonicalValidationError as exc:
            raise MutationRejected("INVALID_IDEMPOTENCY_FINGERPRINT") from exc
        if semantic_fingerprint(request) != request["idempotency_fingerprint"]:
            raise MutationRejected("IDEMPOTENCY_FINGERPRINT_MISMATCH")

    def _materialize_package(self, tx, request):
        record = self._complete_package(request["payload"].get("package"))
        if record["record_revision"] != 1:
            raise MutationRejected("PACKAGE_REVISION_MUST_START_AT_ONE")
        if record["control_lane_id"] != request["control_lane_id"]:
            raise MutationRejected("PACKAGE_LANE_MISMATCH")
        if tx.read_latest("VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", record["id"]):
            raise MutationRejected("PACKAGE_IDENTITY_CONFLICT")
        stored = tx.append_canonical(record)
        self._checkpoint("after_canonical")
        return self._result(request, [stored])

    def _revise_package(self, tx, request):
        record = self._complete_package(request["payload"].get("package"))
        current = tx.read_latest("VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", record["id"])
        if current is None:
            raise MutationRejected("PACKAGE_NOT_FOUND")
        expected = request["expected_state"]
        if expected["target_record_revision"] != current.record["record_revision"] or expected["target_record_digest"] != current.digest:
            raise MutationRejected("STALE_PACKAGE_REVISION")
        if record["control_lane_id"] != request["control_lane_id"] or record["control_lane_id"] != current.record["control_lane_id"]:
            raise MutationRejected("PACKAGE_LANE_MISMATCH")
        if record["record_revision"] != current.record["record_revision"] + 1:
            raise MutationRejected("PACKAGE_REVISION_NOT_CONTIGUOUS")
        if record["id_scheme"] != current.record["id_scheme"]:
            raise MutationRejected("PACKAGE_IDENTITY_CONFLICT")
        stored = tx.append_canonical(record)
        self._checkpoint("after_canonical")
        return self._result(request, [stored])

    def _schedule_occurrence(self, tx, request):
        record = self._require_complete_record(request["payload"].get("occurrence"), OCCURRENCE_FIELDS, "STAGE_OCCURRENCE")
        if record["record_revision"] != 1 or record["state"] != "OPEN" or record["terminal"] is not None:
            raise MutationRejected("SCHEDULE_REQUIRES_OPEN_REVISION_ONE")
        lane_id = request["control_lane_id"]
        if record["control_lane_id"] != lane_id:
            raise MutationRejected("OCCURRENCE_LANE_MISMATCH")
        if tx.read_latest("STAGE_OCCURRENCE", record["id"]):
            raise MutationRejected("OCCURRENCE_IDENTITY_CONFLICT")
        expected = request["expected_state"]
        if expected["active_occurrence_ref"] is not None:
            raise MutationRejected("CONTROL_LANE_SCHEDULE_CONFLICT")
        stored = tx.append_canonical(record)
        self._checkpoint("after_canonical")
        ref = self._record_ref(stored)
        try:
            lane = tx.compare_and_advance_lane(lane_id, None, ref)
        except StoreConflict as exc:
            raise MutationRejected("CONTROL_LANE_SCHEDULE_CONFLICT") from exc
        self._checkpoint("after_lane")
        outbox_id = "out_" + request["operation_request_id"][4:]
        outbox_payload = {
            "occurrence_ref": ref,
            "control_lane_id": lane_id,
            "operation_request_id": request["operation_request_id"],
        }
        tx.append_outbox(outbox_id, record["id"], lane_id, outbox_payload)
        self._checkpoint("after_outbox")
        return self._result(request, [stored], lane=lane, outbox_ids=[outbox_id])

    def _terminate_occurrence(self, tx, request):
        occurrence_id = request["payload"].get("occurrence_id")
        current = tx.read_latest("STAGE_OCCURRENCE", occurrence_id)
        self._validate_open_target(current, request["expected_state"], request["control_lane_id"])
        terminal = self._validate_terminal_facts(request["payload"].get("terminal"), require_escalation=False)
        record = deepcopy(current.record)
        record["record_revision"] += 1
        record["recorded_at"] = request["payload"].get("recorded_at") or current.record["recorded_at"]
        record["state"] = "TERMINAL"
        record["terminal"] = deepcopy(terminal)
        stored = tx.append_canonical(record)
        self._checkpoint("after_canonical")
        return self._result(request, [stored])

    def _raise_escalation(self, tx, request):
        occurrence_id = request["payload"].get("occurrence_id")
        current = tx.read_latest("STAGE_OCCURRENCE", occurrence_id)
        self._validate_open_target(current, request["expected_state"], request["control_lane_id"])
        escalation = self._require_complete_record(
            request["payload"].get("escalation"), ESCALATION_FIELDS, "ESCALATION"
        )
        if escalation["record_revision"] != 1:
            raise MutationRejected("ESCALATION_REVISION_MUST_START_AT_ONE")
        if tx.read_latest("ESCALATION", escalation["id"]):
            raise MutationRejected("ESCALATION_IDENTITY_CONFLICT")
        if escalation["control_lane_id"] != request["control_lane_id"]:
            raise MutationRejected("ESCALATION_LANE_MISMATCH")
        if escalation["trusted_basis_digest"] != canonical_digest(current.record["trusted_basis"]):
            raise MutationRejected("ESCALATION_TRUSTED_BASIS_MISMATCH")
        source_ref = escalation.get("raised_from_occurrence_ref")
        try:
            validate_canonical_ref(source_ref)
        except CanonicalValidationError as exc:
            raise MutationRejected("ESCALATION_SOURCE_MISMATCH", str(exc)) from exc
        if (
            source_ref.get("object_type") != "STAGE_OCCURRENCE"
            or source_ref.get("id") != current.record["id"]
            or source_ref.get("identity", {}).get("value") != current.digest
        ):
            raise MutationRejected("ESCALATION_SOURCE_MISMATCH")
        stored_escalation = tx.append_canonical(escalation)
        self._checkpoint("after_escalation")
        terminal = self._validate_terminal_facts(request["payload"].get("terminal"), require_escalation=True)
        raised = terminal.get("raised_escalation_ids")
        if raised != [escalation["id"]] or terminal["resolved_escalation_ids"]:
            raise MutationRejected("ESCALATION_TERMINAL_BINDING_MISSING")
        occurrence = deepcopy(current.record)
        occurrence["record_revision"] += 1
        occurrence["recorded_at"] = request["payload"].get("recorded_at") or current.record["recorded_at"]
        occurrence["state"] = "TERMINAL"
        occurrence["terminal"] = deepcopy(terminal)
        stored_occurrence = tx.append_canonical(occurrence)
        self._checkpoint("after_terminal")
        return self._result(request, [stored_escalation, stored_occurrence])


    def _validate_terminal_facts(self, terminal, *, require_escalation: bool):
        if not isinstance(terminal, Mapping) or set(terminal) != TERMINAL_FIELDS:
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        outcome = terminal.get("outcome_category")
        status = terminal.get("status")
        if outcome not in {"COMPLETED", "BLOCKED", "ESCALATED", "FAILED_WITH_FINDING"}:
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        if status not in {"READY", "READY_WITH_FINDINGS"} | BLOCKED_STATUSES:
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        if not all(isinstance(terminal.get(name), list) for name in (
            "produced_refs", "finding_refs", "raised_escalation_ids", "resolved_escalation_ids"
        )):
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        if outcome == "COMPLETED" and status not in {"READY", "READY_WITH_FINDINGS"}:
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        if outcome == "BLOCKED" and status not in BLOCKED_STATUSES:
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        if outcome == "ESCALATED" and status not in BLOCKED_STATUSES:
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        if outcome == "FAILED_WITH_FINDING" and status not in BLOCKED_STATUSES | {"READY_WITH_FINDINGS"}:
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        if require_escalation and (outcome != "ESCALATED" or not terminal["raised_escalation_ids"]):
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        if not require_escalation and (outcome == "ESCALATED" or terminal["raised_escalation_ids"]):
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        if outcome == "FAILED_WITH_FINDING" and not terminal["finding_refs"]:
            raise MutationRejected("INVALID_TERMINAL_FACTS")
        return deepcopy(terminal)

    def _validate_open_target(self, current, expected, lane_id):
        if current is None:
            raise MutationRejected("OCCURRENCE_NOT_FOUND")
        if current.record.get("state") != "OPEN":
            raise MutationRejected("OCCURRENCE_ALREADY_TERMINAL")
        if current.record.get("control_lane_id") != lane_id:
            raise MutationRejected("OCCURRENCE_LANE_MISMATCH")
        if expected["target_record_revision"] != current.record["record_revision"] or expected["target_record_digest"] != current.digest:
            raise MutationRejected("STALE_OCCURRENCE_REVISION")

    def _complete_package(self, record):
        record = self._require_complete_record(record, PACKAGE_FIELDS, "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE")
        record = deepcopy(record)
        record["package_digest"] = canonical_digest(record, self_digest_field="package_digest")
        validate_record(record)
        return record

    def _require_complete_record(self, record, required_fields, kind):
        if not isinstance(record, Mapping) or set(record) != required_fields:
            raise MutationRejected(f"{kind}_INCOMPLETE")
        record = deepcopy(record)
        if record.get("kind") != kind:
            raise MutationRejected(f"{kind}_KIND_MISMATCH")
        try:
            validate_record(record)
        except CanonicalValidationError as exc:
            raise MutationRejected(f"{kind}_INVALID", str(exc)) from exc
        return record

    def _result(self, request, records, *, lane=None, outbox_ids=None):
        result = {
            "status": "APPLIED",
            "operation_name": request["operation_name"],
            "operation_request_id": request["operation_request_id"],
            "canonical_records": [self._record_ref(record) for record in records],
            "outbox_ids": list(outbox_ids or []),
        }
        if lane is not None:
            result["lane_head"] = {
                "lane_id": lane.lane_id,
                "version": lane.version,
                "occurrence_ref": lane.occurrence_ref,
            }
        return result

    @staticmethod
    def _record_ref(record: StoredRecord) -> str:
        return f"{record.record['kind']}:{record.record['id']}@{record.record['record_revision']}#{record.digest}"

    def _checkpoint(self, name: str) -> None:
        if self._fault_injector is not None:
            self._fault_injector(name)
