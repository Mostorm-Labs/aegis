"""P36-03 CP-I04 evidence materialization wrapper.

Extends the frozen CP-I04 evidence bundle with the P36-02 trust-repair closure
and the P36-03 mandatory case-level matrix required by fresh P34 re-review.
This compiler never issues a Gate verdict.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import timedelta
import hashlib
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.control_plane import generate_cp_i04_evidence as base
from tests.control_plane.test_cp_i04_p36_matrix import (
    NOW as MATRIX_NOW,
    RESOURCE as MATRIX_RESOURCE,
    ReplaySnapshotAdapter,
)
from tests.control_plane.test_cp_i04_required_child_barrier import (
    canonical_occurrence_ref,
    child_scope,
    exact_ref,
    internal_ref,
    root_scope,
    scoped_occurrence,
)
from tools import aegis_control


P36_02_REPAIR_PACKAGE_ID = "CP-I04-P36-02"
P36_02_SOURCE_P35_COMMENT = "5483198734"
P36_02_SOURCE_P36_COMMENT = "5483129237"
P36_02_RETURN_COMMENT = "5483324780"
REPAIR_PACKAGE_ID = "CP-I04-P36-03"
SOURCE_P34_REREVIEW_COMMENT = "5483456044"
SOURCE_P35_COMMENT = "5483634948"
SOURCE_REVISION = "3cb0aa61f69459048f228dc5c979e679d97daf43"
RESOURCE = "p36/repair/acceptance"


def _exact_resolver(adapter, contract_ref: dict, resource_key: str):
    return aegis_control.TrustResolver(
        {"PROJECT_STATE": adapter},
        acceptance_contract_sources={
            aegis_control.canonical_digest(contract_ref): aegis_control.TrustFactRequest(
                "PROJECT_STATE", resource_key
            )
        },
    )


def _adapter(adapter_id: str):
    return aegis_control.DeterministicExternalAdapter(
        source_kind="PROJECT_STATE",
        adapter_id=adapter_id,
        secret=b"cp-i04-p36-repair-evidence",
        callback_available=True,
        query_correlation_available=True,
        clock=lambda: base.NOW,
    )


def _support(resolver, contract, suffix: str):
    return resolver.resolve_child_acceptance(
        root_scope(f"ws_p36_{suffix}"),
        exact_ref("STAGE_OCCURRENCE", f"so_p36_{suffix}", "d"),
        [contract],
    )


def _repair_closure() -> dict:
    """Preserve the already-green P36-02 N1/N2/N3 resolver controls."""

    missing_adapter = _adapter("p36-missing-fact")
    missing_contract = exact_ref("CONTRACT", "contract-p36-missing", "1")
    missing_adapter.set_resource(
        RESOURCE,
        version_scheme="acceptance-fact",
        version_value="m1",
        resolved_refs=[],
        satisfies=True,
    )
    missing = _support(
        _exact_resolver(missing_adapter, missing_contract, RESOURCE),
        missing_contract,
        "missing",
    )

    mutable_adapter = _adapter("p36-mutable-ref")
    mutable_contract = exact_ref("CONTRACT", "contract-p36-mutable", "2")
    mutable_fact = exact_ref("GATE_DECISION", "gate-p36-mutable", "3")
    mutable_fact["identity"] = {"scheme": "git-ref", "value": "refs/heads/main"}
    mutable_adapter.set_resource(
        RESOURCE,
        version_scheme="acceptance-fact",
        version_value="r1",
        resolved_refs=[mutable_fact],
        satisfies=True,
    )
    mutable = _support(
        _exact_resolver(mutable_adapter, mutable_contract, RESOURCE),
        mutable_contract,
        "mutable",
    )

    wrong_contract_results = {}
    exact_contract_results = {}
    for index, object_type in enumerate(("GATE_DECISION", "PROOF_EVALUATION", "RESULT")):
        adapter = _adapter(f"p36-contract-{index}")
        configured = exact_ref("CONTRACT", f"contract-p36-exact-{index}", "4")
        altered = exact_ref("CONTRACT", f"contract-p36-exact-{index}", "5")
        fact = exact_ref(object_type, f"fact-p36-exact-{index}", "6")
        adapter.set_resource(
            RESOURCE,
            version_scheme="acceptance-fact",
            version_value=f"c{index}",
            resolved_refs=[fact],
            satisfies=True,
        )
        resolver = _exact_resolver(adapter, configured, RESOURCE)
        wrong_contract_results[object_type] = _support(
            resolver, altered, f"wrong_contract_{index}"
        ).accepted
        exact_contract_results[object_type] = _support(
            resolver, configured, f"exact_contract_{index}"
        ).accepted

    metrics = {
        "missing_exact_acceptance_fact_accepted": 1 if missing.accepted else 0,
        "mutable_unpinned_trust_ref_accepted": 1 if mutable.accepted else 0,
        "wrong_acceptance_contract_identity_accepted": 1
        if any(wrong_contract_results.values())
        else 0,
    }
    return {
        "evidence_family": "CP-I04-P36-REPAIR-CLOSURE",
        "repair_package_id": P36_02_REPAIR_PACKAGE_ID,
        "source_p35_comment": P36_02_SOURCE_P35_COMMENT,
        "source_p36_comment": P36_02_SOURCE_P36_COMMENT,
        "oracle": "O-AUTH + exact CanonicalRef/contract-binding checker",
        "missing_exact_acceptance_fact": {
            "accepted": missing.accepted,
            "code": missing.code,
        },
        "mutable_unpinned_trust_ref": {
            "accepted": mutable.accepted,
            "code": mutable.code,
        },
        "wrong_acceptance_contract_identity": wrong_contract_results,
        "exact_configured_contract_identity": exact_contract_results,
        "metrics": metrics,
        "passed": (
            all(value == 0 for value in metrics.values())
            and all(exact_contract_results.values())
        ),
    }


def _store_state(store, *, request_id: str, occurrence_id: str, lane_id: str) -> dict:
    canonical_counts, outbox_count = base._snapshot(store)
    lane_head = store.read_lane_head(lane_id)
    return {
        "canonical_counts": canonical_counts,
        "outbox_count": outbox_count,
        "idempotency_present": store.read_idempotency(request_id) is not None,
        "occurrence_present": store.read_latest("STAGE_OCCURRENCE", occurrence_id) is not None,
        "lane_head_ref": lane_head.occurrence_ref,
    }


def _zero_residue(before: dict, after: dict) -> bool:
    return (
        before["canonical_counts"] == after["canonical_counts"]
        and before["outbox_count"] == after["outbox_count"]
        and not after["idempotency_present"]
        and not after["occurrence_present"]
        and before["lane_head_ref"] == after["lane_head_ref"]
    )


def _child_spawn_precommit_matrix() -> list[dict]:
    cases = []
    checkpoints = ("after_canonical", "after_lane", "after_outbox", "after_idempotency")
    for index, checkpoint in enumerate(checkpoints):
        with tempfile.TemporaryDirectory() as tmp:
            store = aegis_control.ControlStore(str(Path(tmp) / "control.db"))
            service = aegis_control.MutationService(store)
            contract = exact_ref("CONTRACT", f"contract-p36-03-spawn-{index}", "1")
            parent_scope = root_scope(f"ws_p36_03_spawn_parent_{index}")
            parent_id = f"so_p36_03_spawn_parent_{index}"
            parent_lane = f"lane_p36_03_spawn_parent_{index}"
            base._schedule(
                service,
                scoped_occurrence(parent_id, parent_lane, parent_scope),
                f"req_p36_03_spawn_parent_{index}",
            )
            parent_open = store.read_latest("STAGE_OCCURRENCE", parent_id)
            child_ws = child_scope(
                f"ws_p36_03_spawn_child_{index}",
                parent_scope,
                canonical_occurrence_ref(parent_open),
                contract,
            )
            child_id = f"so_p36_03_spawn_child_{index}"
            child_lane = f"lane_p36_03_spawn_child_{index}"
            child = scoped_occurrence(child_id, child_lane, child_ws)
            request_id = f"req_p36_03_spawn_fault_{index}"
            before = _store_state(
                store,
                request_id=request_id,
                occurrence_id=child_id,
                lane_id=child_lane,
            )

            def fault(name, expected=checkpoint):
                if name == expected:
                    raise RuntimeError(f"synthetic {expected}")

            rejection = None
            crashing = aegis_control.MutationService(store, fault_injector=fault)
            try:
                base._schedule(crashing, child, request_id)
            except RuntimeError as exc:
                rejection = {"type": type(exc).__name__, "message": str(exc)}

            after = _store_state(
                store,
                request_id=request_id,
                occurrence_id=child_id,
                lane_id=child_lane,
            )
            cases.append(
                {
                    "case": checkpoint,
                    "injected_checkpoint": checkpoint,
                    "rejection": rejection,
                    "before": before,
                    "after": after,
                    "child_occurrence_absent": not after["occurrence_present"],
                    "child_lane_head_absent": after["lane_head_ref"] is None,
                    "idempotency_residue_absent": not after["idempotency_present"],
                    "zero_residue": rejection is not None and _zero_residue(before, after),
                }
            )
    return cases


def _historical_future_currentness() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        store = aegis_control.ControlStore(str(Path(tmp) / "control.db"))
        adapter = ReplaySnapshotAdapter()
        contract = exact_ref("CONTRACT", "contract-p36-03-history", "2")
        gate_d1 = exact_ref("GATE_DECISION", "gate-p36-03-history-d1", "3")
        gate_d2 = exact_ref("GATE_DECISION", "gate-p36-03-history-d2", "4")
        adapter.set_resource(
            MATRIX_RESOURCE,
            version_scheme="gate-decision",
            version_value="d1",
            resolved_refs=[gate_d1],
            satisfies=True,
        )
        resolver = _exact_resolver(adapter, contract, MATRIX_RESOURCE)
        service = aegis_control.MutationService(store, trust_resolver=resolver)
        materialized = base._materialize_parent_child(
            store,
            service,
            contract,
            prefix="p36_03_history",
        )

        successor = scoped_occurrence(
            "so_p36_03_history_s",
            materialized["parent_lane"],
            materialized["parent_scope"],
        )
        base._schedule(
            service,
            successor,
            "req_p36_03_history_s",
            predecessor_ref=internal_ref(materialized["parent_terminal"]),
        )
        successor_open = store.read_latest("STAGE_OCCURRENCE", successor["id"])
        replay_before = aegis_control.ProjectionEngine(store).replay_required_child_acceptance(
            successor["id"]
        )

        adapter.set_resource(
            MATRIX_RESOURCE,
            version_scheme="gate-decision",
            version_value="d2",
            resolved_refs=[gate_d2],
            satisfies=False,
        )
        replay_after = aegis_control.ProjectionEngine(store).replay_required_child_acceptance(
            successor["id"]
        )

        future_child = child_scope(
            "ws_p36_03_history_child_2",
            materialized["parent_scope"],
            canonical_occurrence_ref(successor_open),
            contract,
        )
        base._schedule(
            service,
            scoped_occurrence(
                "so_p36_03_history_child_2",
                "lane_p36_03_history_child_2",
                future_child,
            ),
            "req_p36_03_history_child_2",
        )
        base._terminate(
            service,
            store,
            "so_p36_03_history_child_2",
            "lane_p36_03_history_child_2",
            future_child,
        )
        successor_terminal = base._terminate(
            service,
            store,
            successor["id"],
            successor["control_lane_id"],
            materialized["parent_scope"],
        )

        future = scoped_occurrence(
            "so_p36_03_history_t",
            successor["control_lane_id"],
            materialized["parent_scope"],
        )
        request_id = "req_p36_03_history_t"
        before = _store_state(
            store,
            request_id=request_id,
            occurrence_id=future["id"],
            lane_id=future["control_lane_id"],
        )
        mutation_code = None
        try:
            base._schedule(
                service,
                future,
                request_id,
                predecessor_ref=internal_ref(successor_terminal),
            )
        except aegis_control.MutationRejected as exc:
            mutation_code = exc.code
        after = _store_state(
            store,
            request_id=request_id,
            occurrence_id=future["id"],
            lane_id=future["control_lane_id"],
        )
        return {
            "historical_successor": successor["id"],
            "pinned_d1_fact": replay_before[0]["acceptance_fact_refs"][0],
            "replay_before": replay_before,
            "provider_current_d2_fact": gate_d2,
            "provider_current_satisfies": False,
            "replay_after": replay_after,
            "historical_replay_preserved": replay_before == replay_after,
            "future_occurrence": future["id"],
            "future_current_evaluated": True,
            "future_mutation_rejected": mutation_code is not None,
            "future_mutation_code": mutation_code,
            "before": before,
            "after": after,
            "successor_absent": not after["occurrence_present"],
            "idempotency_residue_absent": not after["idempotency_present"],
            "zero_residue": mutation_code is not None and _zero_residue(before, after),
        }


def _snapshot_negative_matrix() -> list[dict]:
    cases = (
        "payload_tamper",
        "tag_tamper",
        "wrong_adapter",
        "wrong_source",
        "wrong_resource",
        "version_scheme_drift",
        "version_value_drift",
        "expiry",
    )
    results = []
    for index, case in enumerate(cases):
        with tempfile.TemporaryDirectory() as tmp:
            observed = [MATRIX_NOW]
            adapter = ReplaySnapshotAdapter(clock=lambda: observed[0])
            contract = exact_ref("CONTRACT", f"contract-p36-03-negative-{index}", "6")
            gate = exact_ref("GATE_DECISION", f"gate-p36-03-negative-{index}", "7")
            adapter.set_resource(
                MATRIX_RESOURCE,
                version_scheme="gate-decision",
                version_value="d1",
                resolved_refs=[gate],
                satisfies=True,
            )
            captured = adapter.resolve(MATRIX_RESOURCE)
            store = aegis_control.ControlStore(str(Path(tmp) / "control.db"))
            resolver = _exact_resolver(adapter, contract, MATRIX_RESOURCE)
            service = aegis_control.MutationService(store, trust_resolver=resolver)
            materialized = base._materialize_parent_child(
                store,
                service,
                contract,
                prefix=f"p36_03_negative_{index}",
            )

            if case == "payload_tamper":
                prefix, payload, tag = captured.snapshot_token.split(".")
                replacement = "A" if payload[-1] != "A" else "B"
                adapter.forced_snapshot = replace(
                    captured,
                    snapshot_token=f"{prefix}.{payload[:-1]}{replacement}.{tag}",
                )
            elif case == "tag_tamper":
                replacement = "A" if captured.snapshot_token[-1] != "A" else "B"
                adapter.forced_snapshot = replace(
                    captured,
                    snapshot_token=captured.snapshot_token[:-1] + replacement,
                )
            elif case == "wrong_adapter":
                foreign = ReplaySnapshotAdapter(adapter_id="p36-03-provider-other")
                foreign.set_resource(
                    MATRIX_RESOURCE,
                    version_scheme="gate-decision",
                    version_value="d1",
                    resolved_refs=[gate],
                    satisfies=True,
                )
                adapter.forced_snapshot = foreign.resolve(MATRIX_RESOURCE)
            elif case == "wrong_source":
                foreign = ReplaySnapshotAdapter(source_kind="PROOF_PLANE")
                foreign.set_resource(
                    MATRIX_RESOURCE,
                    version_scheme="gate-decision",
                    version_value="d1",
                    resolved_refs=[gate],
                    satisfies=True,
                )
                adapter.forced_snapshot = foreign.resolve(MATRIX_RESOURCE)
            elif case == "wrong_resource":
                adapter.set_resource(
                    "child/other",
                    version_scheme="gate-decision",
                    version_value="d1",
                    resolved_refs=[gate],
                    satisfies=True,
                )
                adapter.forced_snapshot = super(ReplaySnapshotAdapter, adapter).resolve("child/other")
            elif case == "version_scheme_drift":
                adapter.set_resource(
                    MATRIX_RESOURCE,
                    version_scheme="gate-decision-v2",
                    version_value="d1",
                    resolved_refs=[gate],
                    satisfies=True,
                )
                adapter.forced_snapshot = captured
            elif case == "version_value_drift":
                adapter.set_resource(
                    MATRIX_RESOURCE,
                    version_scheme="gate-decision",
                    version_value="d2",
                    resolved_refs=[gate],
                    satisfies=True,
                )
                adapter.forced_snapshot = captured
            elif case == "expiry":
                observed[0] = MATRIX_NOW + timedelta(seconds=11)
                adapter.forced_snapshot = captured

            verification = adapter.verify_snapshot(
                adapter.forced_snapshot.snapshot_token,
                expected_resource_key=MATRIX_RESOURCE,
            )
            successor = scoped_occurrence(
                f"so_p36_03_negative_successor_{index}",
                materialized["parent_lane"],
                materialized["parent_scope"],
            )
            request_id = f"req_p36_03_negative_successor_{index}"
            before = _store_state(
                store,
                request_id=request_id,
                occurrence_id=successor["id"],
                lane_id=successor["control_lane_id"],
            )
            mutation_code = None
            try:
                base._schedule(
                    service,
                    successor,
                    request_id,
                    predecessor_ref=internal_ref(materialized["parent_terminal"]),
                )
            except aegis_control.MutationRejected as exc:
                mutation_code = exc.code
            after = _store_state(
                store,
                request_id=request_id,
                occurrence_id=successor["id"],
                lane_id=successor["control_lane_id"],
            )
            results.append(
                {
                    "case": case,
                    "snapshot_accepted": verification.valid,
                    "snapshot_code": verification.code,
                    "mutation_rejected": mutation_code is not None,
                    "mutation_code": mutation_code,
                    "before": before,
                    "after": after,
                    "successor_absent": not after["occurrence_present"],
                    "idempotency_residue_absent": not after["idempotency_present"],
                    "zero_residue": mutation_code is not None and _zero_residue(before, after),
                }
            )
    return results


def _repair_mutation_bound_case(case: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        store = aegis_control.ControlStore(str(Path(tmp) / "control.db"))
        adapter = ReplaySnapshotAdapter(adapter_id=f"p36-03-{case}")
        contract = exact_ref("CONTRACT", f"contract-p36-03-{case}", "8")
        if case == "missing_exact_acceptance_fact":
            resolved_refs = []
        elif case == "mutable_unpinned_trust_ref":
            mutable_fact = exact_ref("GATE_DECISION", "gate-p36-03-mutable", "9")
            mutable_fact["identity"] = {"scheme": "git-ref", "value": "refs/heads/main"}
            resolved_refs = [mutable_fact]
        else:
            raise ValueError(f"unknown repair mutation-bound case: {case}")

        adapter.set_resource(
            MATRIX_RESOURCE,
            version_scheme="acceptance-fact",
            version_value="d1",
            resolved_refs=resolved_refs,
            satisfies=True,
        )
        resolver = _exact_resolver(adapter, contract, MATRIX_RESOURCE)
        support = resolver.resolve_child_acceptance(
            root_scope(f"ws_p36_03_{case}_probe"),
            exact_ref("STAGE_OCCURRENCE", f"so_p36_03_{case}_probe", "a"),
            [contract],
        )
        service = aegis_control.MutationService(store, trust_resolver=resolver)
        materialized = base._materialize_parent_child(
            store,
            service,
            contract,
            prefix=f"p36_03_{case}",
        )
        successor = scoped_occurrence(
            f"so_p36_03_{case}_successor",
            materialized["parent_lane"],
            materialized["parent_scope"],
        )
        request_id = f"req_p36_03_{case}_successor"
        before = _store_state(
            store,
            request_id=request_id,
            occurrence_id=successor["id"],
            lane_id=successor["control_lane_id"],
        )
        mutation_code = None
        try:
            base._schedule(
                service,
                successor,
                request_id,
                predecessor_ref=internal_ref(materialized["parent_terminal"]),
            )
        except aegis_control.MutationRejected as exc:
            mutation_code = exc.code
        after = _store_state(
            store,
            request_id=request_id,
            occurrence_id=successor["id"],
            lane_id=successor["control_lane_id"],
        )
        return {
            "case": case,
            "resolver_accepted": support.accepted,
            "resolver_code": support.code,
            "mutation_rejected": mutation_code is not None,
            "mutation_code": mutation_code,
            "before": before,
            "after": after,
            "successor_absent": not after["occurrence_present"],
            "idempotency_residue_absent": not after["idempotency_present"],
            "zero_residue": mutation_code is not None and _zero_residue(before, after),
        }


def _mandatory_matrix(repair: dict) -> dict:
    child_spawn = _child_spawn_precommit_matrix()
    historical = _historical_future_currentness()
    snapshot_negative = _snapshot_negative_matrix()
    repair_mutation_bound = {
        case: _repair_mutation_bound_case(case)
        for case in ("missing_exact_acceptance_fact", "mutable_unpinned_trust_ref")
    }
    n3_controls = {
        "wrong_acceptance_contract_identity": repair["wrong_acceptance_contract_identity"],
        "exact_configured_contract_identity": repair["exact_configured_contract_identity"],
    }
    passed = (
        all(case["zero_residue"] for case in child_spawn)
        and historical["historical_replay_preserved"]
        and historical["future_mutation_rejected"]
        and historical["zero_residue"]
        and all(not case["snapshot_accepted"] for case in snapshot_negative)
        and all(case["mutation_rejected"] and case["zero_residue"] for case in snapshot_negative)
        and all(
            not case["resolver_accepted"]
            and case["mutation_rejected"]
            and case["zero_residue"]
            for case in repair_mutation_bound.values()
        )
        and all(not value for value in n3_controls["wrong_acceptance_contract_identity"].values())
        and all(n3_controls["exact_configured_contract_identity"].values())
    )
    return {
        "evidence_family": "CP-I04-P36-MANDATORY-MATRIX",
        "repair_package_id": REPAIR_PACKAGE_ID,
        "source_p34_rereview_comment": SOURCE_P34_REREVIEW_COMMENT,
        "source_p35_comment": SOURCE_P35_COMMENT,
        "source_revision": SOURCE_REVISION,
        "oracle": "O-AUTH + mutation/store residue + exact trust/currentness case matrix",
        "child_spawn_precommit": child_spawn,
        "historical_d1_future_d2": historical,
        "snapshot_negative_matrix": snapshot_negative,
        "repair_mutation_bound": repair_mutation_bound,
        "n3_contract_identity_controls": n3_controls,
        "passed": passed,
    }


def generate(output_dir: Path, result_revision: str, package_ref: str = base.PACKAGE_REF) -> dict:
    # The original compiler predates N3 and keyed fake contract sources by stable id.
    # Patch only its in-memory fixture resolver so all evidence executes against the
    # already-repaired exact-binding production contract.
    base._resolver = _exact_resolver
    manifest = base.generate(output_dir, result_revision, package_ref)

    repair = _repair_closure()
    if not repair["passed"]:
        raise RuntimeError("CP-I04 P36-02 repair evidence failed")
    mandatory = _mandatory_matrix(repair)
    if not mandatory["passed"]:
        raise RuntimeError("CP-I04 P36-03 mandatory evidence matrix failed")

    repair_path = output_dir / "p36-repair-closure.json"
    mandatory_path = output_dir / "p36-mandatory-matrix.json"
    base._write_json(repair_path, repair)
    base._write_json(mandatory_path, mandatory)

    manifest["repair"] = {
        "repair_package_id": REPAIR_PACKAGE_ID,
        "source_p34_rereview_comment": SOURCE_P34_REREVIEW_COMMENT,
        "source_p35_comment": SOURCE_P35_COMMENT,
        "source_revision": SOURCE_REVISION,
        "previous_repair": {
            "repair_package_id": P36_02_REPAIR_PACKAGE_ID,
            "source_p35_comment": P36_02_SOURCE_P35_COMMENT,
            "source_p36_comment": P36_02_SOURCE_P36_COMMENT,
            "return_comment": P36_02_RETURN_COMMENT,
        },
    }
    manifest["evidence"]["CP-I04-P36-REPAIR-CLOSURE"] = repair_path.name
    manifest["evidence"]["CP-I04-P36-MANDATORY-MATRIX"] = mandatory_path.name
    manifest["metrics"].update(repair["metrics"])
    if any(manifest["metrics"].values()):
        raise RuntimeError("CP-I04 P36-03 zero-tolerance metric failure")
    if "test_cp_i04_p36_matrix.CpI04P36MandatoryMatrixTests" not in manifest["test_identities"]:
        manifest["test_identities"].append(
            "test_cp_i04_p36_matrix.CpI04P36MandatoryMatrixTests"
        )

    manifest["file_digests"][repair_path.name] = base._sha256(repair_path)
    manifest["file_digests"][mandatory_path.name] = base._sha256(mandatory_path)
    payload_digest = "sha256:" + hashlib.sha256(
        "\n".join(
            f"{name}={digest}"
            for name, digest in sorted(manifest["file_digests"].items())
        ).encode("utf-8")
    ).hexdigest()
    manifest["artifact"]["payload_digest"] = payload_digest
    manifest["artifact"]["binding_note"] = (
        "GitHub assigns artifact id/digest after upload; durable P36-03 return binds "
        "those values externally without self-digest recursion."
    )
    base._write_json(output_dir / "evidence-manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--package-ref", default=base.PACKAGE_REF)
    parser.add_argument("--output-dir", default="artifacts/cp-i04")
    args = parser.parse_args()
    generate(Path(args.output_dir), args.result_revision, args.package_ref)


if __name__ == "__main__":
    main()
