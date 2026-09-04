from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Mapping

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tests.control_plane.cp_i05_fixtures import (
    PACKAGE_ID,
    RESULT_REF,
    TASK_ANCHOR,
    configured_mutation,
    dispatch_authorization,
    navigation,
    result_trust,
    seed_surface,
)
from tools.aegis_control.canonical import canonical_digest
from tools.aegis_control.dispatch import DispatchRejected, DispatchService
from tools.aegis_control.execution_surface import DeterministicExecutionSurface, classify_resume
from tools.aegis_control.external_ports import DeterministicExternalAdapter
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.recovery import (
    RecoveryCoordinator,
    delivery_is_uncertain,
    dispatch_retry_delay_seconds,
    reconciliation_policy,
)
from tools.aegis_control.store import ControlStore
from tools.aegis_control.trust import ResultMaterializationRequest, TrustResolver


REPAIR_PACKAGE_ID = "CP-I05-P36-01"
SOURCE_P34_COMMENT = "5488464223"
SOURCE_P35_COMMENT = "5489296080"
SOURCE_REVISION = "033637a5be7cb04bb60f0d8176e48130027b9b93"
SOURCE_CP_I04_P34_COMMENT = "5486917398"

EVIDENCE_FAMILIES = {
    "dispatch-fault-matrix.json": "CPV-E-DISPATCH-FAULT-MATRIX",
    "resume-corpus.json": "CPV-E-RESUME-CORPUS",
    "delivery-policy.json": "CPV-E-DELIVERY-POLICY",
    "reconciliation-policy.json": "CPV-E-RECONCILIATION-POLICY",
}

ZERO_METRIC_KEYS = {
    "age_only_terminalization",
    "dispatch_before_commit",
    "diverged_resume_accepted",
    "duplicate_terminal_revision",
    "semantic_occurrence_amplification_from_duplicate_transport",
    "unauthorized_cross_primary_provider_request",
    "unreviewable_result_accepted_as_complete",
    "valid_descendant_resume_replayed_completed_work",
    "worker_direct_canonical_writes",
}


def _time(seconds: int) -> str:
    value = datetime(2026, 9, 1, 2, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return value.isoformat().replace("+00:00", "Z")


def _case(name: str, passed: bool, **facts: Any) -> Mapping[str, Any]:
    return {"case": name, "pass": bool(passed), **facts}


def _schedule(
    mutation: MutationService,
    occurrence_id: str,
    lane_id: str,
    *,
    request_id: str | None = None,
    stage: str = "P32",
    owner: str = "aegis-implementation",
):
    record = occurrence_record(occurrence_id, lane_id)
    record["stage_span"] = {"stages": [stage]}
    record["primary_owner"] = owner
    return mutation.apply(make_request(
        "SCHEDULE_STAGE_OCCURRENCE",
        request_id or f"req_{occurrence_id}_schedule",
        lane_id,
        {"occurrence": record},
    ))


def _progress_request(store, occurrence_id, lane_id, checkpoint, request_id, *, current_override=None):
    current = current_override or store.read_latest("STAGE_OCCURRENCE", occurrence_id)
    return make_request(
        "RECORD_EXECUTION_PROGRESS",
        request_id,
        lane_id,
        {
            "occurrence_id": occurrence_id,
            "recorded_at": _time(10),
            "execution_navigation": checkpoint,
        },
        expected_state(
            target_record_revision=current.record["record_revision"],
            target_record_digest=current.digest,
            work_scope_ref=current.record["work_scope_ref"],
        ),
    )


def _terminal_request(store, occurrence_id, lane_id, refs, request_id):
    current = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
    terminal = terminal_facts()
    terminal["produced_refs"] = [deepcopy(ref) for ref in refs]
    return make_request(
        "TERMINATE_STAGE_OCCURRENCE",
        request_id,
        lane_id,
        {
            "occurrence_id": occurrence_id,
            "recorded_at": _time(20),
            "terminal": terminal,
        },
        expected_state(
            target_record_revision=current.record["record_revision"],
            target_record_digest=current.digest,
            work_scope_ref=current.record["work_scope_ref"],
        ),
    )


def _result_resolver(
    requested_ref: Mapping[str, Any],
    *,
    occurrence_id: str,
    package_id: str = PACKAGE_ID,
    task_anchor_revision: str = TASK_ANCHOR,
    resolved_ref: Mapping[str, Any] | None = None,
    ambiguous: bool = False,
    satisfies: bool = True,
) -> TrustResolver:
    adapter = DeterministicExternalAdapter(
        source_kind="result-store",
        adapter_id="cp-i05-p36-result",
        secret=b"cp-i05-p36-result-secret",
        callback_available=False,
        query_correlation_available=True,
    )
    adapter.set_resource(
        "result-current",
        version_scheme=requested_ref["identity"]["scheme"],
        version_value=requested_ref["identity"]["value"],
        resolved_refs=[deepcopy(resolved_ref or requested_ref)],
        satisfies=satisfies,
        ambiguous=ambiguous,
    )
    request = ResultMaterializationRequest(
        source_kind="result-store",
        resource_key="result-current",
        occurrence_id=occurrence_id,
        package_id=package_id,
        task_anchor_revision=task_anchor_revision,
    )
    return TrustResolver(
        {"result-store": adapter},
        result_sources={canonical_digest(requested_ref): request},
    )


def _state_counts(store: ControlStore) -> Mapping[str, int]:
    return dict(store.snapshot_counts())


def _dispatch_fault_cases() -> list[Mapping[str, Any]]:
    cases: list[Mapping[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "committed.db"))
        scheduled = _schedule(MutationService(store), "so_ev_committed", "lane_ev_committed")
        surface = DeterministicExecutionSurface()
        service = DispatchService(store, surface, authorization_resolver=dispatch_authorization())
        before = _state_counts(store)
        receipt = service.dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        after = _state_counts(store)
        cases.append(_case(
            "committed_outbox_dispatch",
            receipt.acknowledged and before == after and surface.provider_request_count == 1,
            provider_request_count=surface.provider_request_count,
            before=before,
            after=after,
            canonical_delta=after["canonical_records"] - before["canonical_records"],
            authorization_basis_digest=receipt.authorization_basis_digest,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "transient.db"))
        surface = DeterministicExecutionSurface()
        service = DispatchService(store, surface, authorization_resolver=dispatch_authorization())
        code = None
        try:
            service.dispatch("out_transient_not_committed", attempted_at=_time(0))
        except DispatchRejected as exc:
            code = exc.code
        cases.append(_case(
            "transient_or_uncommitted_schedule_no_dispatch",
            code == "OUTBOX_NOT_FOUND" and surface.provider_request_count == 0,
            rejection=code,
            provider_request_count=surface.provider_request_count,
        ))

    for checkpoint in ("after_canonical", "after_lane", "after_outbox", "after_idempotency"):
        with tempfile.TemporaryDirectory() as tmp:
            store = ControlStore(str(Path(tmp) / f"crash-{checkpoint}.db"))
            before = _state_counts(store)

            class InjectedCrash(RuntimeError):
                pass

            def fault(name: str, target=checkpoint):
                if name == target:
                    raise InjectedCrash(target)

            code = None
            try:
                _schedule(
                    MutationService(store, fault_injector=fault),
                    f"so_ev_{checkpoint}",
                    f"lane_ev_{checkpoint}",
                )
            except InjectedCrash:
                code = "INJECTED_CRASH"
            after = _state_counts(store)
            cases.append(_case(
                f"schedule_crash_{checkpoint}",
                code == "INJECTED_CRASH" and before == after and not store.read_outbox(),
                checkpoint=checkpoint,
                rejection=code,
                provider_request_count=0,
                before=before,
                after=after,
                zero_residue=before == after,
            ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "metadata.db"))
        scheduled = _schedule(MutationService(store), "so_ev_metadata", "lane_ev_metadata")
        surface = DeterministicExecutionSurface()
        service = DispatchService(store, surface, authorization_resolver=dispatch_authorization())
        before = _state_counts(store)
        service.dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        store.record_delivery_diagnostic(
            scheduled["outbox_ids"][0], "TEST_DIAGNOSTIC", observed_at=_time(1)
        )
        after = _state_counts(store)
        cases.append(_case(
            "operational_delivery_metadata_no_canonical_change",
            before == after,
            before=before,
            after=after,
            canonical_delta=after["canonical_records"] - before["canonical_records"],
            diagnostic_state=store.read_delivery_state(scheduled["outbox_ids"][0])["diagnostic_state"],
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "duplicate.db"))
        scheduled = _schedule(MutationService(store), "so_ev_duplicate", "lane_ev_duplicate")
        surface = DeterministicExecutionSurface()
        service = DispatchService(store, surface, authorization_resolver=dispatch_authorization())
        first = service.dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        second = service.dispatch(scheduled["outbox_ids"][0], attempted_at=_time(1))
        occurrence_count = len(store.read_revisions("STAGE_OCCURRENCE", "so_ev_duplicate"))
        cases.append(_case(
            "duplicate_transport_same_occurrence",
            first.correlation_id == second.correlation_id
            and surface.unique_execution_count == 1
            and occurrence_count == 1,
            unique_execution_count=surface.unique_execution_count,
            semantic_occurrence_count=occurrence_count,
            correlation_id=first.correlation_id,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "ack-loss.db"))
        scheduled = _schedule(MutationService(store), "so_ev_ack_loss", "lane_ev_ack_loss")
        surface = DeterministicExecutionSurface()

        class WorkerCrash(RuntimeError):
            pass

        def fault(name: str):
            if name == "after_provider_dispatch":
                raise WorkerCrash

        crashed = False
        try:
            DispatchService(
                store,
                surface,
                authorization_resolver=dispatch_authorization(),
                fault_injector=fault,
            ).dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        except WorkerCrash:
            crashed = True
        state_after_crash = store.read_delivery_state(scheduled["outbox_ids"][0])
        receipt = DispatchService(
            store, surface, authorization_resolver=dispatch_authorization()
        ).dispatch(scheduled["outbox_ids"][0], attempted_at=_time(1))
        state_after_restart = store.read_delivery_state(scheduled["outbox_ids"][0])
        cases.append(_case(
            "provider_ack_lost_then_restart_same_execution",
            crashed
            and state_after_crash["provider_correlation_id"] is None
            and state_after_restart["provider_correlation_id"] == receipt.correlation_id
            and surface.unique_execution_count == 1,
            provider_request_count=surface.provider_request_count,
            unique_execution_count=surface.unique_execution_count,
            correlation_after_restart=state_after_restart["provider_correlation_id"],
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "cross-primary.db"))
        scheduled = _schedule(
            MutationService(store),
            "so_ev_cross_primary",
            "lane_ev_cross_primary",
            stage="P34",
            owner="aegis-gate-review",
        )
        surface = DeterministicExecutionSurface()
        code = None
        before = _state_counts(store)
        try:
            DispatchService(
                store, surface, authorization_resolver=dispatch_authorization()
            ).dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        except DispatchRejected as exc:
            code = exc.code
        after = _state_counts(store)
        cases.append(_case(
            "unauthorized_cross_primary_no_provider_request",
            code == "CURRENT_CROSS_PRIMARY_ROLLOUT_DENIED"
            and surface.provider_request_count == 0
            and before == after,
            rejection=code,
            provider_request_count=surface.provider_request_count,
            before=before,
            after=after,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "noncurrent.db"))
        scheduled = _schedule(MutationService(store), "so_ev_noncurrent", "lane_ev_noncurrent")
        surface = DeterministicExecutionSurface()
        code = None
        try:
            DispatchService(
                store,
                surface,
                authorization_resolver=dispatch_authorization(satisfies=False),
            ).dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        except DispatchRejected as exc:
            code = exc.code
        cases.append(_case(
            "noncurrent_authorization_no_provider_request",
            code == "DISPATCH_NOT_AUTHORIZED" and surface.provider_request_count == 0,
            rejection=code,
            provider_request_count=surface.provider_request_count,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "ack.db"))
        scheduled = _schedule(MutationService(store), "so_ev_ack", "lane_ev_ack")
        surface = DeterministicExecutionSurface()
        DispatchService(
            store, surface, authorization_resolver=dispatch_authorization()
        ).dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        latest = store.read_latest("STAGE_OCCURRENCE", "so_ev_ack")
        cases.append(_case(
            "provider_ack_not_completion",
            latest.record["state"] == "OPEN" and latest.record["record_revision"] == 1,
            state=latest.record["state"],
            record_revision=latest.record["record_revision"],
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "callback-loss.db"))
        scheduled = _schedule(MutationService(store), "so_ev_callback", "lane_ev_callback")
        surface = DeterministicExecutionSurface()
        receipt = DispatchService(
            store, surface, authorization_resolver=dispatch_authorization()
        ).dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        surface.set_observation(
            receipt.correlation_id,
            state="RUNNING",
            execution_ref="exec://callback-loss",
            execution_revision="exec-r1",
            completed_through=["implementation"],
            next_action="review",
        )
        before = _state_counts(store)
        observation = RecoveryCoordinator(store, surface).reconcile_outbox(
            scheduled["outbox_ids"][0], observed_at=_time(30)
        )
        after = _state_counts(store)
        cases.append(_case(
            "callback_loss_query_recovery",
            observation.state == "RUNNING" and surface.query_count == 1 and before == after,
            query_count=surface.query_count,
            before=before,
            after=after,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "uncertain.db"))
        scheduled = _schedule(MutationService(store), "so_ev_uncertain", "lane_ev_uncertain")
        surface = DeterministicExecutionSurface()
        service = DispatchService(store, surface, authorization_resolver=dispatch_authorization())
        outbox_id = scheduled["outbox_ids"][0]
        for second in [0, 1, 3, 7, 15, 31, 61, 121, 421, 721, 1021, 1321]:
            service.dispatch(outbox_id, attempted_at=_time(second))
        state = store.read_delivery_state(outbox_id)
        occurrence_count = len(store.read_revisions("STAGE_OCCURRENCE", "so_ev_uncertain"))
        cases.append(_case(
            "delivery_uncertain_boundary_no_replacement_occurrence",
            state["attempt_count"] == 12
            and state["diagnostic_state"] == "DELIVERY_UNCERTAIN"
            and occurrence_count == 1,
            attempt_count=state["attempt_count"],
            diagnostic_state=state["diagnostic_state"],
            semantic_occurrence_count=occurrence_count,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "running-materialized.db"))
        surface = DeterministicExecutionSurface()
        mutation = configured_mutation(
            store,
            surface,
            result_resolver=result_trust(occurrence_id="so_ev_running"),
        )
        scheduled = _schedule(mutation, "so_ev_running", "lane_ev_running")
        receipt = DispatchService(
            store, surface, authorization_resolver=dispatch_authorization()
        ).dispatch(scheduled["outbox_ids"][0], attempted_at=_time(0))
        surface.set_observation(
            receipt.correlation_id,
            state="RUNNING",
            execution_ref="exec://running-materialized",
            execution_revision="exec-r1",
            completed_through=["implementation"],
            next_action="review",
        )
        recovery = RecoveryCoordinator(
            store,
            surface,
            mutation=mutation,
            task_anchor_revision=TASK_ANCHOR,
            execution_surface_name="CODE_EXECUTION",
        )
        running = recovery.reconcile_outbox(scheduled["outbox_ids"][0], observed_at=_time(30))
        running_revision = store.read_latest("STAGE_OCCURRENCE", "so_ev_running").record["record_revision"]
        surface.set_observation(
            receipt.correlation_id,
            state="MATERIALIZED",
            execution_ref="exec://running-materialized",
            execution_revision="exec-r1",
            completed_through=["implementation"],
            next_action="review",
            materialized_ref=RESULT_REF,
        )
        materialized = recovery.reconcile_outbox(scheduled["outbox_ids"][0], observed_at=_time(60))
        latest = store.read_latest("STAGE_OCCURRENCE", "so_ev_running")
        terminal_revision = latest.record["record_revision"]
        recovery.reconcile_outbox(
            scheduled["outbox_ids"][0], observed_at=_time(90), event_hint=True
        )
        terminal_count = sum(
            item.record["state"] == "TERMINAL"
            for item in store.read_revisions("STAGE_OCCURRENCE", "so_ev_running")
        )
        cases.append(_case(
            "provider_running_to_materialized_exact_result",
            running.state == "RUNNING"
            and materialized.state == "MATERIALIZED"
            and running_revision == 2
            and latest.record["state"] == "TERMINAL"
            and latest.record["terminal"]["produced_refs"] == [RESULT_REF],
            running_revision=running_revision,
            terminal_revision=terminal_revision,
            produced_refs=latest.record["terminal"]["produced_refs"],
        ))
        cases.append(_case(
            "duplicate_callback_no_duplicate_terminal_revision",
            terminal_count == 1
            and store.read_latest("STAGE_OCCURRENCE", "so_ev_running").record["record_revision"] == terminal_revision,
            terminal_revision_count=terminal_count,
            terminal_revision=terminal_revision,
        ))
        cases.append(_case(
            "worker_restart_reuses_durable_correlation",
            store.read_delivery_state(scheduled["outbox_ids"][0])["provider_correlation_id"]
            == receipt.correlation_id,
            provider_correlation_id=store.read_delivery_state(scheduled["outbox_ids"][0])["provider_correlation_id"],
        ))

    return cases


def _result_cases() -> list[Mapping[str, Any]]:
    cases: list[Mapping[str, Any]] = []

    def run_case(
        name: str,
        *,
        refs,
        resolver: TrustResolver | None,
        expected_code: str | None,
        occurrence_id: str,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            store = ControlStore(str(Path(tmp) / f"{name}.db"))
            surface = DeterministicExecutionSurface()
            seed_surface(surface, occurrence_id=occurrence_id, execution_ref=f"exec://{name}")
            mutation = configured_mutation(store, surface, result_resolver=resolver)
            _schedule(mutation, occurrence_id, f"lane_{name}")
            mutation.apply(_progress_request(
                store,
                occurrence_id,
                f"lane_{name}",
                navigation(f"exec://{name}", "exec-r1"),
                f"req_{name}_progress",
            ))
            before = _state_counts(store)
            code = None
            applied = False
            try:
                result = mutation.apply(_terminal_request(
                    store, occurrence_id, f"lane_{name}", refs, f"req_{name}_terminal"
                ))
                applied = result["status"] == "APPLIED"
            except MutationRejected as exc:
                code = exc.code
            after = _state_counts(store)
            latest = store.read_latest("STAGE_OCCURRENCE", occurrence_id)
            passed = (
                applied and expected_code is None and latest.record["state"] == "TERMINAL"
            ) or (
                not applied
                and code == expected_code
                and before == after
                and latest.record["state"] == "OPEN"
            )
            cases.append(_case(
                name,
                passed,
                rejection=code,
                applied=applied,
                final_state=latest.record["state"],
                before=before,
                after=after,
                zero_residue=(before == after) if expected_code else None,
            ))

    run_case(
        "exact_result_resolved",
        refs=[RESULT_REF],
        resolver=result_trust(occurrence_id="so_result_exact"),
        expected_code=None,
        occurrence_id="so_result_exact",
    )
    run_case(
        "missing_result",
        refs=[],
        resolver=result_trust(occurrence_id="so_result_missing"),
        expected_code="RESULT_MATERIALIZATION_REQUIRED",
        occurrence_id="so_result_missing",
    )
    run_case(
        "inaccessible_result",
        refs=[RESULT_REF],
        resolver=TrustResolver({}),
        expected_code="RESULT_MATERIALIZATION_UNRESOLVABLE",
        occurrence_id="so_result_inaccessible",
    )
    local_ref = deepcopy(RESULT_REF)
    local_ref["id"] = "result_local_only"
    local_ref["ref"] = "file:///tmp/local-result"
    local_ref["identity"] = {"scheme": "local-path", "value": "/tmp/local-result"}
    run_case(
        "local_only_unreviewable_result",
        refs=[local_ref],
        resolver=TrustResolver({}),
        expected_code="RESULT_MATERIALIZATION_UNPINNED",
        occurrence_id="so_result_local",
    )
    mutable_ref = deepcopy(RESULT_REF)
    mutable_ref["id"] = "result_mutable"
    mutable_ref["identity"] = {"scheme": "branch", "value": "main"}
    run_case(
        "mutable_unpinned_result",
        refs=[mutable_ref],
        resolver=TrustResolver({}),
        expected_code="RESULT_MATERIALIZATION_UNPINNED",
        occurrence_id="so_result_mutable",
    )
    mismatch_ref = deepcopy(RESULT_REF)
    mismatch_ref["id"] = "result_other_exact"
    mismatch_ref["identity"] = {"scheme": "sha256", "value": "sha256:" + "2" * 64}
    run_case(
        "result_identity_mismatch",
        refs=[RESULT_REF],
        resolver=_result_resolver(
            RESULT_REF,
            occurrence_id="so_result_identity",
            resolved_ref=mismatch_ref,
        ),
        expected_code="RESULT_MATERIALIZATION_IDENTITY_MISMATCH",
        occurrence_id="so_result_identity",
    )
    run_case(
        "ambiguous_result_resolution",
        refs=[RESULT_REF],
        resolver=_result_resolver(
            RESULT_REF,
            occurrence_id="so_result_ambiguous",
            ambiguous=True,
        ),
        expected_code="RESULT_MATERIALIZATION_AMBIGUOUS",
        occurrence_id="so_result_ambiguous",
    )
    run_case(
        "occurrence_lineage_mismatch",
        refs=[RESULT_REF],
        resolver=_result_resolver(RESULT_REF, occurrence_id="different_occurrence"),
        expected_code="RESULT_MATERIALIZATION_LINEAGE_MISMATCH",
        occurrence_id="so_result_occurrence_lineage",
    )
    run_case(
        "package_lineage_mismatch",
        refs=[RESULT_REF],
        resolver=_result_resolver(
            RESULT_REF,
            occurrence_id="so_result_package_lineage",
            package_id="different-package",
        ),
        expected_code="RESULT_MATERIALIZATION_LINEAGE_MISMATCH",
        occurrence_id="so_result_package_lineage",
    )
    run_case(
        "task_anchor_lineage_mismatch",
        refs=[RESULT_REF],
        resolver=_result_resolver(
            RESULT_REF,
            occurrence_id="so_result_task_lineage",
            task_anchor_revision="0" * 40,
        ),
        expected_code="RESULT_MATERIALIZATION_LINEAGE_MISMATCH",
        occurrence_id="so_result_task_lineage",
    )
    return cases


def _progress_cases() -> list[Mapping[str, Any]]:
    cases: list[Mapping[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "exact.db"))
        surface = DeterministicExecutionSurface()
        seed_surface(surface, occurrence_id="so_progress_exact", execution_ref="exec://progress-exact")
        mutation = configured_mutation(store, surface)
        _schedule(mutation, "so_progress_exact", "lane_progress_exact")
        prior = store.read_latest("STAGE_OCCURRENCE", "so_progress_exact")
        request = _progress_request(
            store,
            "so_progress_exact",
            "lane_progress_exact",
            navigation("exec://progress-exact", "exec-r1"),
            "req_progress_exact",
        )
        first = mutation.apply(request)
        replay = mutation.apply(request)
        latest = store.read_latest("STAGE_OCCURRENCE", "so_progress_exact")
        frozen_fields = (
            "control_lane_id", "work_scope_ref", "stage_span", "primary_owner",
            "trusted_basis", "policy_binding", "schedule_basis", "input_refs", "repair_context",
        )
        frozen_unchanged = all(prior.record[field] == latest.record[field] for field in frozen_fields)
        cases.append(_case(
            "exact_checkpoint_applied",
            first["status"] == "APPLIED" and latest.record["record_revision"] == 2,
            record_revision=latest.record["record_revision"],
            execution_navigation=latest.record["execution_navigation"],
        ))
        cases.append(_case(
            "execution_navigation_only_delta",
            frozen_unchanged,
            frozen_fields=list(frozen_fields),
            frozen_unchanged=frozen_unchanged,
        ))
        cases.append(_case(
            "exact_idempotent_progress_replay",
            first == replay and len(store.read_revisions("STAGE_OCCURRENCE", "so_progress_exact")) == 2,
            replay_same_result=(first == replay),
            revision_count=len(store.read_revisions("STAGE_OCCURRENCE", "so_progress_exact")),
        ))

        before = _state_counts(store)
        surface.set_execution_revision(
            "exec://progress-exact", "exec-r2", ancestor_revision="exec-r1"
        )
        code = None
        try:
            mutation.apply(_progress_request(
                store,
                "so_progress_exact",
                "lane_progress_exact",
                navigation("exec://progress-exact", "exec-r1"),
                "req_progress_diverged",
            ))
        except MutationRejected as exc:
            code = exc.code
        after = _state_counts(store)
        cases.append(_case(
            "unreconciled_descendant_checkpoint_rejected",
            code == "EXECUTION_NAVIGATION_DIVERGENCE" and before == after,
            rejection=code,
            before=before,
            after=after,
            zero_residue=before == after,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "flat.db"))
        surface = DeterministicExecutionSurface()
        seed_surface(surface, occurrence_id="so_progress_flat", execution_ref="exec://progress-flat")
        mutation = configured_mutation(store, surface)
        _schedule(mutation, "so_progress_flat", "lane_progress_flat")
        flat = {
            "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
            "classification": "EXACT_CURSOR",
            "accepted_revision": "exec-r1",
            "completed_through": ["implementation"],
            "next_action": "review",
        }
        before = _state_counts(store)
        code = None
        try:
            mutation.apply(_progress_request(
                store,
                "so_progress_flat",
                "lane_progress_flat",
                flat,
                "req_progress_flat",
            ))
        except MutationRejected as exc:
            code = exc.code
        after = _state_counts(store)
        cases.append(_case(
            "flat_or_unknown_navigation_rejected",
            code == "INVALID_EXECUTION_NAVIGATION" and before == after,
            rejection=code,
            before=before,
            after=after,
            zero_residue=before == after,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "anchor.db"))
        surface = DeterministicExecutionSurface()
        seed_surface(surface, occurrence_id="so_progress_anchor", execution_ref="exec://progress-anchor")
        mutation = configured_mutation(store, surface)
        _schedule(mutation, "so_progress_anchor", "lane_progress_anchor")
        bad = navigation("exec://progress-anchor", "exec-r1")
        bad["task_anchor"] = {"revision": "0" * 40, "relation": "ancestor"}
        before = _state_counts(store)
        code = None
        try:
            mutation.apply(_progress_request(
                store,
                "so_progress_anchor",
                "lane_progress_anchor",
                bad,
                "req_progress_anchor",
            ))
        except MutationRejected as exc:
            code = exc.code
        after = _state_counts(store)
        cases.append(_case(
            "wrong_task_anchor_rejected",
            code == "EXECUTION_NAVIGATION_DIVERGENCE" and before == after,
            rejection=code,
            zero_residue=before == after,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "stale.db"))
        surface = DeterministicExecutionSurface()
        seed_surface(surface, occurrence_id="so_progress_stale", execution_ref="exec://progress-stale")
        mutation = configured_mutation(store, surface)
        _schedule(mutation, "so_progress_stale", "lane_progress_stale")
        prior = store.read_latest("STAGE_OCCURRENCE", "so_progress_stale")
        first = _progress_request(
            store,
            "so_progress_stale",
            "lane_progress_stale",
            navigation("exec://progress-stale", "exec-r1"),
            "req_progress_stale_first",
        )
        mutation.apply(first)
        stale = _progress_request(
            store,
            "so_progress_stale",
            "lane_progress_stale",
            navigation("exec://progress-stale", "exec-r1"),
            "req_progress_stale_second",
            current_override=prior,
        )
        before = _state_counts(store)
        code = None
        try:
            mutation.apply(stale)
        except MutationRejected as exc:
            code = exc.code
        after = _state_counts(store)
        cases.append(_case(
            "stale_revision_digest_zero_residue",
            code == "STALE_OCCURRENCE_REVISION" and before == after,
            rejection=code,
            zero_residue=before == after,
        ))

    with tempfile.TemporaryDirectory() as tmp:
        store = ControlStore(str(Path(tmp) / "competing.db"))
        surface = DeterministicExecutionSurface()
        seed_surface(surface, occurrence_id="so_progress_competing", execution_ref="exec://progress-competing")
        mutation = configured_mutation(store, surface)
        _schedule(mutation, "so_progress_competing", "lane_progress_competing")
        prior = store.read_latest("STAGE_OCCURRENCE", "so_progress_competing")
        first = _progress_request(
            store,
            "so_progress_competing",
            "lane_progress_competing",
            navigation("exec://progress-competing", "exec-r1", next_action="review-a"),
            "req_progress_competing_a",
            current_override=prior,
        )
        second = _progress_request(
            store,
            "so_progress_competing",
            "lane_progress_competing",
            navigation("exec://progress-competing", "exec-r1", next_action="review-b"),
            "req_progress_competing_b",
            current_override=prior,
        )
        mutation.apply(first)
        code = None
        try:
            mutation.apply(second)
        except MutationRejected as exc:
            code = exc.code
        revisions = store.read_revisions("STAGE_OCCURRENCE", "so_progress_competing")
        cases.append(_case(
            "competing_checkpoints_one_winner",
            code == "STALE_OCCURRENCE_REVISION" and len(revisions) == 2,
            rejection=code,
            revision_count=len(revisions),
        ))

    return cases


def _resume_corpus() -> Mapping[str, Any]:
    ancestry = {("C", "D"), ("A", "D")}
    scenarios = [
        (
            "EXACT_CURSOR",
            classify_resume(
                task_anchor_revision="A",
                resume_cursor={"revision": "C", "completed_through": ["P32.1"], "next_action": "P32.2"},
                observed_revision="C",
                is_ancestor=lambda a, b: a == b,
            ),
        ),
        (
            "DESCENDANT_CURSOR",
            classify_resume(
                task_anchor_revision="A",
                resume_cursor={"revision": "C", "completed_through": ["P32.1"], "next_action": "reconcile delta"},
                observed_revision="D",
                is_ancestor=lambda a, b: (a, b) in ancestry,
            ),
        ),
        (
            "ANCHOR_DESCENDANT_WITHOUT_CURSOR",
            classify_resume(
                task_anchor_revision="A",
                resume_cursor=None,
                observed_revision="D",
                is_ancestor=lambda a, b: (a, b) == ("A", "D"),
            ),
        ),
        (
            "DIVERGED",
            classify_resume(
                task_anchor_revision="A",
                resume_cursor={"revision": "C", "completed_through": [], "next_action": "continue"},
                observed_revision="X",
                is_ancestor=lambda a, b: False,
            ),
        ),
    ]
    cases = [
        {
            "state": expected,
            "accepted_revision": result.accepted_revision,
            "completed_through": list(result.completed_through),
            "next_action": result.next_action,
            "replay_completed_work": result.replay_completed_work,
            "blocker": result.blocker,
            "pass": result.state == expected
            and result.replay_completed_work is False
            and (expected != "DIVERGED" or result.blocker == "BLOCKED_EXECUTION_DIVERGENCE"),
        }
        for expected, result in scenarios
    ]
    return {
        "evidence_family": "CPV-E-RESUME-CORPUS",
        "cases": cases,
        "passed": all(case["pass"] for case in cases),
    }


def _delivery_policy() -> Mapping[str, Any]:
    retry = [dispatch_retry_delay_seconds(i) for i in range(1, 9)]
    boundary = {
        "before_boundary": delivery_is_uncertain(attempt_count=11, elapsed_seconds=1799),
        "attempt_12": delivery_is_uncertain(attempt_count=12, elapsed_seconds=1),
        "minute_30": delivery_is_uncertain(attempt_count=1, elapsed_seconds=1800),
    }
    passed = retry == [1, 2, 4, 8, 16, 30, 60, 300] and boundary == {
        "before_boundary": False,
        "attempt_12": True,
        "minute_30": True,
    }
    return {
        "evidence_family": "CPV-E-DELIVERY-POLICY",
        "retry_delays_seconds": retry,
        "boundary_cases": boundary,
        "semantic_replacement_occurrences": 0,
        "passed": passed,
    }


def _reconciliation_policy() -> Mapping[str, Any]:
    ages = [0, 299, 300, 1799, 1800, 7199, 7200]
    expected = [
        (0, 30, False),
        (299, 30, False),
        (300, 120, False),
        (1799, 120, False),
        (1800, 300, False),
        (7199, 300, False),
        (7200, 900, True),
    ]
    cases = []
    for age in ages:
        policy = reconciliation_policy(age)
        cases.append({
            "age_seconds": age,
            "interval_seconds": policy.interval_seconds,
            "operator_alert": policy.operator_alert,
            "semantic_terminalization": policy.semantic_terminalization,
        })
    observed = [
        (case["age_seconds"], case["interval_seconds"], case["operator_alert"])
        for case in cases
    ]
    return {
        "evidence_family": "CPV-E-RECONCILIATION-POLICY",
        "cases": cases,
        "passed": observed == expected and all(not case["semantic_terminalization"] for case in cases),
    }


def _derive_metrics(
    dispatch_cases: list[Mapping[str, Any]],
    result_cases: list[Mapping[str, Any]],
    resume: Mapping[str, Any],
    reconciliation: Mapping[str, Any],
) -> Mapping[str, int]:
    by_name = {case["case"]: case for case in dispatch_cases}
    precommit_names = {
        "transient_or_uncommitted_schedule_no_dispatch",
        "schedule_crash_after_canonical",
        "schedule_crash_after_lane",
        "schedule_crash_after_outbox",
        "schedule_crash_after_idempotency",
    }
    dispatch_before_commit = sum(
        int(by_name[name].get("provider_request_count", 0) != 0) for name in precommit_names
    )
    operational_names = {
        "committed_outbox_dispatch",
        "operational_delivery_metadata_no_canonical_change",
        "unauthorized_cross_primary_no_provider_request",
    }
    worker_direct = sum(
        int(by_name[name].get("before") != by_name[name].get("after"))
        for name in operational_names
    )
    duplicate = by_name["duplicate_transport_same_occurrence"]
    terminal = by_name["duplicate_callback_no_duplicate_terminal_revision"]
    cross = by_name["unauthorized_cross_primary_no_provider_request"]
    unreviewable = [case for case in result_cases if case["case"] != "exact_result_resolved"]
    resume_cases = resume["cases"]
    descendant_cases = [
        case for case in resume_cases
        if case["state"] in {"EXACT_CURSOR", "DESCENDANT_CURSOR", "ANCHOR_DESCENDANT_WITHOUT_CURSOR"}
    ]
    diverged = next(case for case in resume_cases if case["state"] == "DIVERGED")
    return {
        "age_only_terminalization": sum(
            int(case["semantic_terminalization"]) for case in reconciliation["cases"]
        ),
        "dispatch_before_commit": dispatch_before_commit,
        "diverged_resume_accepted": int(diverged.get("blocker") != "BLOCKED_EXECUTION_DIVERGENCE"),
        "duplicate_terminal_revision": max(0, int(terminal["terminal_revision_count"]) - 1),
        "semantic_occurrence_amplification_from_duplicate_transport": max(
            0, int(duplicate["semantic_occurrence_count"]) - 1
        ),
        "unauthorized_cross_primary_provider_request": int(cross["provider_request_count"]),
        "unreviewable_result_accepted_as_complete": sum(
            int(case["final_state"] == "TERMINAL") for case in unreviewable
        ),
        "valid_descendant_resume_replayed_completed_work": sum(
            int(case["replay_completed_work"]) for case in descendant_cases
        ),
        "worker_direct_canonical_writes": worker_direct,
    }


def _write(path: Path, payload: Mapping[str, Any]) -> str:
    data = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.write_bytes(data)
    return "sha256:" + hashlib.sha256(data).hexdigest()


def build_evidence_bundle(*, result_revision: str, package_ref: str, output_dir: Path) -> Mapping[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dispatch_cases = _dispatch_fault_cases()
    result_cases = _result_cases()
    progress_cases = _progress_cases()
    dispatch = {
        "evidence_family": "CPV-E-DISPATCH-FAULT-MATRIX",
        "repair_package_id": REPAIR_PACKAGE_ID,
        "cases": dispatch_cases,
        "result_cases": result_cases,
        "progress_cases": progress_cases,
        "passed": all(case["pass"] for case in dispatch_cases + result_cases + progress_cases),
    }
    resume = _resume_corpus()
    delivery = _delivery_policy()
    reconciliation = _reconciliation_policy()
    metrics = _derive_metrics(dispatch_cases, result_cases, resume, reconciliation)
    if set(metrics) != ZERO_METRIC_KEYS:
        raise AssertionError("CP-I05 zero-tolerance metric key set drifted")

    payloads = {
        "dispatch-fault-matrix.json": dispatch,
        "resume-corpus.json": resume,
        "delivery-policy.json": delivery,
        "reconciliation-policy.json": reconciliation,
    }
    evidence_files = []
    for filename, payload in payloads.items():
        digest = _write(output_dir / filename, payload)
        evidence_files.append({
            "file": filename,
            "evidence_family": EVIDENCE_FAMILIES[filename],
            "digest": digest,
            "passed": bool(payload["passed"]),
        })

    manifest = {
        "schema_version": "0.2",
        "kind": "CP-I05_EVIDENCE_MANIFEST",
        "package_id": PACKAGE_ID,
        "package_ref": package_ref,
        "repair_package_id": REPAIR_PACKAGE_ID,
        "result_revision": result_revision,
        "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
        "source_cp_i04_p34_comment": SOURCE_CP_I04_P34_COMMENT,
        "repair_lineage": {
            "source_p34_comment": SOURCE_P34_COMMENT,
            "source_p35_classification_comment": SOURCE_P35_COMMENT,
            "source_revision": SOURCE_REVISION,
        },
        "evidence_files": sorted(evidence_files, key=lambda item: item["file"]),
        "metrics": metrics,
        "claims": {
            "p34_gate_pass": False,
            "evidence_compiler_gate_authority": False,
            "cp_i06_plus": False,
            "current_cross_primary_rollout": "DENIED",
        },
        "passed": dispatch["passed"]
        and resume["passed"]
        and delivery["passed"]
        and reconciliation["passed"]
        and all(value == 0 for value in metrics.values()),
    }
    if not manifest["passed"]:
        raise AssertionError("CP-I05 evidence bundle contains a failing mandatory case")
    _write(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--package-ref", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    manifest = build_evidence_bundle(
        result_revision=args.result_revision,
        package_ref=args.package_ref,
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
