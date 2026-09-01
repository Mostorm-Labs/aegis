"""Single canonical mutation boundary for the accepted CP-I02..CP-I05 subset."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping, Sequence

from .canonical import (
    CanonicalValidationError,
    canonical_digest,
    canonical_dumps,
    validate_canonical_ref,
    validate_digest,
    validate_record,
    validate_required_child_acceptance_binding,
    validate_work_scope_ref,
)
from .execution_surface import ExecutionPositionResolver, validate_execution_navigation_shape
from .store import ControlStore, StoreConflict, StoredRecord
from .trust import TrustResolver

SUPPORTED_OPERATIONS = {
    "MATERIALIZE_IMPLEMENTATION_PACKAGE",
    "REVISE_IMPLEMENTATION_PACKAGE",
    "SCHEDULE_STAGE_OCCURRENCE",
    "RECORD_EXECUTION_PROGRESS",
    "TERMINATE_STAGE_OCCURRENCE",
    "RAISE_ESCALATION",
}
KNOWN_LATER_OPERATIONS = {
    "RECORD_ESCALATION_RESOLUTION",
    "SCHEDULE_REPAIR_OCCURRENCE",
    "SCHEDULE_REVERIFICATION_OCCURRENCE",
    "SCHEDULE_REREVIEW_OCCURRENCE",
    "RECOMPUTE_CONTROL_PROJECTION",
}
EXPECTED_STATE_KEYS = {
    "active_occurrence_ref", "predecessor_occurrence_ref", "target_record_revision",
    "target_record_digest", "trusted_basis_digest", "package_ref", "work_scope_ref",
}
ACTOR_CLASSES = {
    "CONTROL_PLANE", "PRIMARY_OWNER", "EXECUTION_SURFACE", "REVIEW_SURFACE",
    "HUMAN", "EXTERNAL_SYSTEM",
}
PACKAGE_FIELDS = {
    "schema_version", "kind", "id_scheme", "id", "record_revision", "recorded_at",
    "extensions", "control_lane_id", "work_scope_ref", "trusted_basis", "scope",
    "verification_binding", "policy_binding", "task_anchor", "package_digest",
}
OCCURRENCE_FIELDS = {
    "schema_version", "kind", "id_scheme", "id", "record_revision", "recorded_at",
    "extensions", "control_lane_id", "work_scope_ref", "stage_span", "primary_owner", "state",
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
    "extensions", "control_lane_id", "work_scope_ref", "raised_from_occurrence_ref",
    "trusted_basis_digest", "category", "owning_layer", "required_decision",
    "evidence_snapshot_refs",
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
        trust_resolver: TrustResolver | None = None,
        execution_position_resolver: ExecutionPositionResolver | None = None,
        implementation_package_id: str | None = None,
        task_anchor_revision: str | None = None,
        fault_injector: Callable[[str], None] | None = None,
        before_transaction: Callable[[], None] | None = None,
    ):
        self._store = store
        self._trust_resolver = trust_resolver
        self._execution_position_resolver = execution_position_resolver
        self._implementation_package_id = implementation_package_id
        self._task_anchor_revision = task_anchor_revision
        self._fault_injector = fault_injector
        self._before_transaction = before_transaction

    def apply(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        self._validate_request(request)
        operation = request["operation_name"]
        if self._before_transaction is not None:
            self._before_transaction()
        with self._store._mutation_transaction() as tx:
            replay = tx.read_idempotency(request["operation_request_id"])
            if replay is not None:
                fingerprint, result = replay
                if fingerprint != request["idempotency_fingerprint"]:
                    raise MutationRejected("OPERATION_IDEMPOTENCY_CONFLICT")
                return result
            if operation in KNOWN_LATER_OPERATIONS or operation not in SUPPORTED_OPERATIONS:
                raise MutationRejected("UNSUPPORTED_OPERATION_IN_CP_I02", operation)
            try:
                if operation == "MATERIALIZE_IMPLEMENTATION_PACKAGE":
                    result = self._materialize_package(tx, request)
                elif operation == "REVISE_IMPLEMENTATION_PACKAGE":
                    result = self._revise_package(tx, request)
                elif operation == "SCHEDULE_STAGE_OCCURRENCE":
                    result = self._schedule_occurrence(tx, request)
                elif operation == "RECORD_EXECUTION_PROGRESS":
                    result = self._record_execution_progress(tx, request)
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
        expected = request["expected_state"]
        if not isinstance(expected, Mapping) or set(expected) != EXPECTED_STATE_KEYS:
            raise MutationRejected("INVALID_EXPECTED_STATE")
        if expected["work_scope_ref"] is not None:
            try:
                validate_work_scope_ref(expected["work_scope_ref"])
            except CanonicalValidationError as exc:
                raise MutationRejected("INVALID_EXPECTED_STATE", str(exc)) from exc
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
        self._require_expected_scope(request["expected_state"], record["work_scope_ref"])
        self._validate_existing_scope_lane(tx, record["work_scope_ref"], record["control_lane_id"])
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
        self._require_expected_scope(expected, current.record["work_scope_ref"])
        if record["work_scope_ref"] != current.record["work_scope_ref"]:
            raise MutationRejected("PACKAGE_WORK_SCOPE_MISMATCH")
        if record["record_revision"] != current.record["record_revision"] + 1:
            raise MutationRejected("PACKAGE_REVISION_NOT_CONTIGUOUS")
        if record["id_scheme"] != current.record["id_scheme"]:
            raise MutationRejected("PACKAGE_IDENTITY_CONFLICT")
        stored = tx.append_canonical(record)
        self._checkpoint("after_canonical")
        return self._result(request, [stored])

    def _schedule_occurrence(self, tx, request):
        record = self._require_complete_record(
            request["payload"].get("occurrence"), OCCURRENCE_FIELDS, "STAGE_OCCURRENCE"
        )
        if record["record_revision"] != 1 or record["state"] != "OPEN" or record["terminal"] is not None:
            raise MutationRejected("SCHEDULE_REQUIRES_OPEN_REVISION_ONE")
        lane_id = request["control_lane_id"]
        if record["control_lane_id"] != lane_id:
            raise MutationRejected("OCCURRENCE_LANE_MISMATCH")
        self._require_expected_scope(request["expected_state"], record["work_scope_ref"])
        if tx.read_latest("STAGE_OCCURRENCE", record["id"]):
            raise MutationRejected("OCCURRENCE_IDENTITY_CONFLICT")
        if record.get("execution_navigation") is not None:
            self._validate_execution_navigation(record["execution_navigation"])

        self._validate_work_scope_for_schedule(tx, record)
        self._validate_expected_package_scope(tx, request["expected_state"], record["work_scope_ref"])
        expected_lane_ref = self._schedule_expected_lane_ref(tx, request["expected_state"], lane_id)
        if request["expected_state"]["predecessor_occurrence_ref"] is not None:
            record = self._bind_required_children(tx, record)

        stored = tx.append_canonical(record)
        self._checkpoint("after_canonical")
        ref = self._record_ref(stored)
        try:
            lane = tx.compare_and_advance_lane(lane_id, expected_lane_ref, ref)
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

    def _validate_work_scope_for_schedule(self, tx, record):
        scope = record["work_scope_ref"]
        scope_id = scope["id"]
        lane_id = record["control_lane_id"]
        existing_lane_scope = self._lane_scope(tx, lane_id)
        if existing_lane_scope is not None and existing_lane_scope != scope:
            raise MutationRejected("WORK_SCOPE_MISMATCH")
        existing_scope_lane = self._work_scope_lane(tx, scope_id)
        if existing_scope_lane is not None and existing_scope_lane != lane_id:
            raise MutationRejected("WORK_SCOPE_LANE_CONFLICT")

        binding = scope.get("child_work_binding")
        if binding is None:
            return
        if existing_scope_lane is not None:
            existing_scope = self._scope_by_id(tx, scope_id)
            if existing_scope != scope:
                raise MutationRejected("WORK_SCOPE_MISMATCH")
            return

        parent_ref = binding["parent_work_scope_ref"]
        parent_id = parent_ref["id"]
        parent_lane = self._work_scope_lane(tx, parent_id)
        if parent_lane is None:
            raise MutationRejected("WORK_SCOPE_MISMATCH")
        if parent_lane == lane_id or parent_id == scope_id:
            raise MutationRejected("WORK_SCOPE_LANE_CONFLICT")
        spawned = self._resolve_exact_occurrence_ref(tx, binding["spawned_by_occurrence_ref"])
        if spawned is None:
            raise MutationRejected("WORK_SCOPE_MISMATCH")
        spawned_scope = spawned.record.get("work_scope_ref")
        if not isinstance(spawned_scope, Mapping) or spawned_scope.get("id") != parent_id:
            raise MutationRejected("WORK_SCOPE_MISMATCH")
        if self._would_create_scope_cycle(tx, scope_id, parent_id):
            raise MutationRejected("WORK_SCOPE_MISMATCH")

    def _validate_expected_package_scope(self, tx, expected, work_scope_ref):
        package_ref = expected.get("package_ref")
        if package_ref is None:
            return
        try:
            kind, package_id, revision, digest = self._parse_record_ref(package_ref)
        except MutationRejected as exc:
            raise MutationRejected("PACKAGE_WORK_SCOPE_MISMATCH") from exc
        if kind != "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE":
            raise MutationRejected("PACKAGE_WORK_SCOPE_MISMATCH")
        package = tx.read_exact(kind, package_id, revision, digest=digest)
        if package is None or package.record.get("work_scope_ref") != work_scope_ref:
            raise MutationRejected("PACKAGE_WORK_SCOPE_MISMATCH")

    def _schedule_expected_lane_ref(self, tx, expected, lane_id):
        if expected["active_occurrence_ref"] is not None:
            raise MutationRejected("CONTROL_LANE_SCHEDULE_CONFLICT")
        predecessor_ref = expected["predecessor_occurrence_ref"]
        if predecessor_ref is None:
            return None
        kind, occurrence_id, _, _ = self._parse_record_ref(predecessor_ref)
        if kind != "STAGE_OCCURRENCE":
            raise MutationRejected("CONTROL_LANE_SCHEDULE_CONFLICT")
        predecessor = tx.read_latest("STAGE_OCCURRENCE", occurrence_id)
        if (
            predecessor is None
            or predecessor.record.get("state") != "TERMINAL"
            or predecessor.record.get("control_lane_id") != lane_id
            or self._record_ref(predecessor) != predecessor_ref
        ):
            raise MutationRejected("CONTROL_LANE_SCHEDULE_CONFLICT")
        expected_scope = expected.get("work_scope_ref")
        if predecessor.record.get("work_scope_ref") != expected_scope:
            raise MutationRejected("WORK_SCOPE_MISMATCH")
        lane = tx.read_lane_head(lane_id)
        if lane.occurrence_ref is None:
            raise MutationRejected("CONTROL_LANE_SCHEDULE_CONFLICT")
        lane_kind, lane_occurrence_id, _, _ = self._parse_record_ref(lane.occurrence_ref)
        if lane_kind != "STAGE_OCCURRENCE" or lane_occurrence_id != occurrence_id:
            raise MutationRejected("CONTROL_LANE_SCHEDULE_CONFLICT")
        return lane.occurrence_ref

    def _bind_required_children(self, tx, record):
        schedule_basis = record.get("schedule_basis")
        if not isinstance(schedule_basis, Mapping):
            raise MutationRejected("STAGE_OCCURRENCE_INVALID")
        if schedule_basis.get("required_child_acceptance_bindings"):
            raise MutationRejected("CHILD_ACCEPTANCE_BASIS_CONFLICT")
        parent_scope = record["work_scope_ref"]
        uncrossed = self._uncrossed_required_children(tx, parent_scope)
        if not uncrossed:
            return record

        record = deepcopy(record)
        bindings = []
        input_refs = list(record.get("input_refs") or [])
        for child_scope in uncrossed:
            child_binding = child_scope["child_work_binding"]
            completion = self._child_completion_record(tx, child_scope)
            if completion is None:
                raise MutationRejected("REQUIRED_CHILD_WORK_NOT_ACCEPTED")
            completion_ref = self._canonical_occurrence_ref(completion)
            contracts = self._sorted_refs(child_binding["acceptance_contract_refs"])
            facts: list[Mapping[str, Any]] = []
            if contracts:
                if self._trust_resolver is None:
                    raise MutationRejected("REQUIRED_CHILD_WORK_NOT_ACCEPTED")
                support = self._trust_resolver.resolve_child_acceptance(
                    child_scope, completion_ref, contracts
                )
                if not support.accepted:
                    raise MutationRejected(support.code)
                self._checkpoint("after_child_acceptance_resolution")
                fresh = self._trust_resolver.verify_freshness(support.snapshot_resolution)
                if not fresh.valid:
                    raise MutationRejected(self._trust_failure_code(fresh.code))
                facts = self._sorted_refs(support.acceptance_fact_refs)
            barrier_ref = deepcopy(child_binding["spawned_by_occurrence_ref"])
            payload = {
                "child_work_scope_ref": deepcopy(child_scope),
                "barrier_after_occurrence_ref": barrier_ref,
                "child_completion_occurrence_ref": completion_ref,
                "acceptance_contract_refs": contracts,
                "acceptance_fact_refs": facts,
            }
            binding = {
                **payload,
                "acceptance_basis_digest": canonical_digest(payload),
            }
            try:
                validate_required_child_acceptance_binding(binding)
            except CanonicalValidationError as exc:
                raise MutationRejected("CHILD_ACCEPTANCE_BASIS_CONFLICT", str(exc)) from exc
            bindings.append(binding)
            input_refs = self._append_unique_refs(input_refs, [completion_ref, *facts])

        bindings.sort(key=lambda item: item["child_work_scope_ref"]["id"])
        record["schedule_basis"] = deepcopy(dict(record["schedule_basis"]))
        record["schedule_basis"]["required_child_acceptance_bindings"] = bindings
        record["input_refs"] = input_refs
        try:
            validate_record(record)
        except CanonicalValidationError as exc:
            raise MutationRejected("STAGE_OCCURRENCE_INVALID", str(exc)) from exc
        return record

    def _uncrossed_required_children(self, tx, parent_scope):
        parent_id = parent_scope["id"]
        children: dict[str, Mapping[str, Any]] = {}
        for occurrence in tx.read_latest_stage_occurrences():
            scope = occurrence.record.get("work_scope_ref")
            if not isinstance(scope, Mapping):
                continue
            binding = scope.get("child_work_binding")
            if not isinstance(binding, Mapping):
                continue
            parent_ref = binding.get("parent_work_scope_ref")
            if (
                isinstance(parent_ref, Mapping)
                and parent_ref.get("id") == parent_id
                and binding.get("parent_gate") == "REQUIRED"
            ):
                children.setdefault(scope["id"], deepcopy(dict(scope)))

        crossed: set[tuple[str, str]] = set()
        for occurrence in tx.read_latest_stage_occurrences():
            if occurrence.record.get("work_scope_ref") != parent_scope:
                continue
            basis = occurrence.record.get("schedule_basis")
            if not isinstance(basis, Mapping):
                continue
            for binding in basis.get("required_child_acceptance_bindings") or []:
                child = binding.get("child_work_scope_ref")
                barrier = binding.get("barrier_after_occurrence_ref")
                if isinstance(child, Mapping) and isinstance(barrier, Mapping):
                    crossed.add((child.get("id"), barrier.get("identity", {}).get("value")))

        uncrossed = []
        for child in children.values():
            binding = child["child_work_binding"]
            key = (
                child["id"],
                binding["spawned_by_occurrence_ref"].get("identity", {}).get("value"),
            )
            if key not in crossed:
                uncrossed.append(child)
        return sorted(uncrossed, key=lambda item: item["id"])

    def _child_completion_record(self, tx, child_scope):
        child_id = child_scope["id"]
        occurrences = [
            item for item in tx.read_latest_stage_occurrences()
            if isinstance(item.record.get("work_scope_ref"), Mapping)
            and item.record["work_scope_ref"].get("id") == child_id
        ]
        if not occurrences:
            return None
        lanes = {item.record.get("control_lane_id") for item in occurrences}
        if len(lanes) != 1:
            raise MutationRejected("WORK_SCOPE_LANE_CONFLICT")
        lane_id = next(iter(lanes))
        lane = tx.read_lane_head(lane_id)
        occurrence_id = self._occurrence_id_from_internal_ref(lane.occurrence_ref)
        if occurrence_id is None:
            return None
        current = tx.read_latest("STAGE_OCCURRENCE", occurrence_id)
        if current is None or current.record.get("state") != "TERMINAL":
            return None
        terminal = current.record.get("terminal")
        if not isinstance(terminal, Mapping) or terminal.get("outcome_category") != "COMPLETED":
            return None
        resolved: set[str] = set()
        for occurrence in occurrences:
            terminal_facts = occurrence.record.get("terminal")
            if isinstance(terminal_facts, Mapping):
                resolved.update(terminal_facts.get("resolved_escalation_ids") or [])
        for escalation in tx.read_latest_escalations():
            scope = escalation.record.get("work_scope_ref")
            if isinstance(scope, Mapping) and scope.get("id") == child_id and escalation.record["id"] not in resolved:
                return None
        return current

    def _record_execution_progress(self, tx, request):
        payload = request["payload"]
        expected_fields = {"occurrence_id", "recorded_at", "execution_navigation"}
        if set(payload) != expected_fields:
            raise MutationRejected("INVALID_EXECUTION_PROGRESS_PAYLOAD")
        occurrence_id = payload.get("occurrence_id")
        current = tx.read_latest("STAGE_OCCURRENCE", occurrence_id)
        self._validate_open_target(current, request["expected_state"], request["control_lane_id"])
        navigation = payload.get("execution_navigation")
        self._validate_execution_navigation(navigation)
        record = deepcopy(current.record)
        record["record_revision"] += 1
        record["recorded_at"] = payload.get("recorded_at") or current.record["recorded_at"]
        record["execution_navigation"] = deepcopy(dict(navigation))
        try:
            validate_record(record)
        except CanonicalValidationError as exc:
            raise MutationRejected("INVALID_EXECUTION_NAVIGATION", str(exc)) from exc
        stored = tx.append_canonical(record)
        self._checkpoint("after_canonical")
        return self._result(request, [stored])

    def _validate_execution_navigation(self, navigation):
        if not validate_execution_navigation_shape(navigation):
            raise MutationRejected("INVALID_EXECUTION_NAVIGATION")
        if (
            self._task_anchor_revision is None
            or navigation["task_anchor"]["revision"] != self._task_anchor_revision
            or self._execution_position_resolver is None
        ):
            raise MutationRejected("EXECUTION_NAVIGATION_DIVERGENCE")
        verification = self._execution_position_resolver.verify_checkpoint(navigation)
        if not verification.valid:
            raise MutationRejected(verification.code)

    def _terminate_occurrence(self, tx, request):
        occurrence_id = request["payload"].get("occurrence_id")
        current = tx.read_latest("STAGE_OCCURRENCE", occurrence_id)
        self._validate_open_target(current, request["expected_state"], request["control_lane_id"])
        terminal = self._validate_terminal_facts(request["payload"].get("terminal"), require_escalation=False)
        self._validate_required_materialization(current.record, terminal)
        record = deepcopy(current.record)
        record["record_revision"] += 1
        record["recorded_at"] = request["payload"].get("recorded_at") or current.record["recorded_at"]
        record["state"] = "TERMINAL"
        record["terminal"] = deepcopy(terminal)
        stored = tx.append_canonical(record)
        self._checkpoint("after_canonical")
        return self._result(request, [stored])

    def _validate_required_materialization(self, occurrence, terminal):
        if terminal.get("outcome_category") != "COMPLETED":
            return
        navigation = occurrence.get("execution_navigation")
        configured_execution_boundary = bool(
            self._implementation_package_id and self._task_anchor_revision
        )
        if navigation is None and not configured_execution_boundary:
            return
        result_refs = [
            ref for ref in terminal.get("produced_refs") or []
            if isinstance(ref, Mapping) and ref.get("object_type") == "RESULT"
        ]
        if len(result_refs) != 1:
            raise MutationRejected(
                "RESULT_MATERIALIZATION_REQUIRED" if not result_refs
                else "RESULT_MATERIALIZATION_AMBIGUOUS"
            )
        result_ref = result_refs[0]
        try:
            validate_canonical_ref(result_ref)
        except CanonicalValidationError as exc:
            raise MutationRejected("RESULT_MATERIALIZATION_UNPINNED", str(exc)) from exc
        if (
            self._trust_resolver is None
            or not self._implementation_package_id
            or not self._task_anchor_revision
        ):
            raise MutationRejected("RESULT_MATERIALIZATION_UNRESOLVABLE")
        resolution = self._trust_resolver.resolve_result_materialization(
            result_ref,
            occurrence_id=occurrence["id"],
            package_id=self._implementation_package_id,
            task_anchor_revision=self._task_anchor_revision,
        )
        if not resolution.valid:
            raise MutationRejected(resolution.code)
        if resolution.result_ref != result_ref:
            raise MutationRejected("RESULT_MATERIALIZATION_IDENTITY_MISMATCH")

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
        if escalation["work_scope_ref"] != current.record["work_scope_ref"]:
            raise MutationRejected("WORK_SCOPE_MISMATCH")
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
        self._require_expected_scope(expected, current.record.get("work_scope_ref"))
        if expected["target_record_revision"] != current.record["record_revision"] or expected["target_record_digest"] != current.digest:
            raise MutationRejected("STALE_OCCURRENCE_REVISION")

    def _complete_package(self, record):
        record = self._require_complete_record(
            record, PACKAGE_FIELDS, "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE"
        )
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

    def _require_expected_scope(self, expected, actual_scope):
        guarded = expected.get("work_scope_ref")
        if guarded is None or guarded != actual_scope:
            raise MutationRejected("WORK_SCOPE_MISMATCH")

    def _lane_scope(self, tx, lane_id):
        scopes = {
            canonical_dumps(item.record["work_scope_ref"]): item.record["work_scope_ref"]
            for item in tx.read_lane_latest_records(lane_id)
            if item.record.get("kind") == "STAGE_OCCURRENCE"
            and isinstance(item.record.get("work_scope_ref"), Mapping)
        }
        if len(scopes) > 1:
            raise MutationRejected("WORK_SCOPE_LANE_CONFLICT")
        return deepcopy(next(iter(scopes.values()))) if scopes else None

    def _work_scope_lane(self, tx, scope_id):
        lanes = {
            item.record.get("control_lane_id")
            for item in tx.read_latest_stage_occurrences()
            if isinstance(item.record.get("work_scope_ref"), Mapping)
            and item.record["work_scope_ref"].get("id") == scope_id
        }
        lanes.discard(None)
        if len(lanes) > 1:
            raise MutationRejected("WORK_SCOPE_LANE_CONFLICT")
        return next(iter(lanes)) if lanes else None

    def _scope_by_id(self, tx, scope_id):
        scopes = {
            canonical_dumps(item.record["work_scope_ref"]): item.record["work_scope_ref"]
            for item in tx.read_latest_stage_occurrences()
            if isinstance(item.record.get("work_scope_ref"), Mapping)
            and item.record["work_scope_ref"].get("id") == scope_id
        }
        if len(scopes) > 1:
            raise MutationRejected("WORK_SCOPE_MISMATCH")
        return deepcopy(next(iter(scopes.values()))) if scopes else None

    def _validate_existing_scope_lane(self, tx, scope, lane_id):
        existing = self._work_scope_lane(tx, scope["id"])
        if existing is not None and existing != lane_id:
            raise MutationRejected("WORK_SCOPE_LANE_CONFLICT")

    def _would_create_scope_cycle(self, tx, child_id, parent_id):
        seen: set[str] = set()
        cursor = parent_id
        while cursor is not None:
            if cursor == child_id:
                return True
            if cursor in seen:
                return True
            seen.add(cursor)
            scope = self._scope_by_id(tx, cursor)
            if scope is None:
                return False
            binding = scope.get("child_work_binding")
            if not isinstance(binding, Mapping):
                return False
            parent_ref = binding.get("parent_work_scope_ref")
            cursor = parent_ref.get("id") if isinstance(parent_ref, Mapping) else None
        return False

    def _resolve_exact_occurrence_ref(self, tx, ref):
        try:
            validate_canonical_ref(ref)
        except CanonicalValidationError:
            return None
        if ref.get("object_type") != "STAGE_OCCURRENCE":
            return None
        digest = ref.get("identity", {}).get("value")
        for revision in tx.read_revisions("STAGE_OCCURRENCE", ref.get("id")):
            if revision.digest == digest:
                return revision
        return None

    @staticmethod
    def _trust_failure_code(code):
        if code in {"TRUST_BASIS_AMBIGUOUS", "TRUST_FACT_DUPLICATE"}:
            return "CHILD_ACCEPTANCE_BASIS_AMBIGUOUS"
        if code == "TRUST_BASIS_CONFLICT":
            return "CHILD_ACCEPTANCE_BASIS_CONFLICT"
        return "REQUIRED_CHILD_WORK_NOT_ACCEPTED"

    @staticmethod
    def _sorted_refs(refs: Sequence[Mapping[str, Any]]):
        return sorted((deepcopy(dict(ref)) for ref in refs), key=canonical_dumps)

    @staticmethod
    def _append_unique_refs(existing, additions):
        result = [deepcopy(dict(ref)) for ref in existing]
        digests = {canonical_digest(ref) for ref in result}
        for ref in additions:
            digest = canonical_digest(ref)
            if digest not in digests:
                result.append(deepcopy(dict(ref)))
                digests.add(digest)
        return result

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

    @staticmethod
    def _canonical_occurrence_ref(record: StoredRecord) -> Mapping[str, Any]:
        return {
            "object_type": "STAGE_OCCURRENCE",
            "id": record.record["id"],
            "ref": f"control:STAGE_OCCURRENCE:{record.record['id']}@{record.record['record_revision']}",
            "identity": {"scheme": "sha256", "value": record.digest},
        }

    @staticmethod
    def _parse_record_ref(ref: str) -> tuple[str, str, int, str]:
        try:
            prefix, digest = ref.rsplit("#", 1)
            kind_and_id, revision_text = prefix.rsplit("@", 1)
            kind, record_id = kind_and_id.split(":", 1)
            revision = int(revision_text)
            validate_digest(digest)
        except (AttributeError, ValueError, CanonicalValidationError) as exc:
            raise MutationRejected("CONTROL_LANE_SCHEDULE_CONFLICT") from exc
        if not kind or not record_id or revision < 1:
            raise MutationRejected("CONTROL_LANE_SCHEDULE_CONFLICT")
        return kind, record_id, revision, digest

    @classmethod
    def _occurrence_id_from_internal_ref(cls, ref):
        if not isinstance(ref, str):
            return None
        try:
            kind, occurrence_id, _, _ = cls._parse_record_ref(ref)
        except MutationRejected:
            return None
        return occurrence_id if kind == "STAGE_OCCURRENCE" else None

    def _checkpoint(self, name: str) -> None:
        if self._fault_injector is not None:
            self._fault_injector(name)
