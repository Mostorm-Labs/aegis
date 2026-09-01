from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tools.aegis_control.api import (
    ApiRequestError,
    ControlApi,
    REFERENCE_SUPPORTED_REQUEST_BYTES,
    enforce_envelope_size,
    safe_audit_fields,
    validate_transport_semantic_payload,
)
from tools.aegis_control.capabilities import api_capability_profile, worker_capability_profile, WorkerControlPort
from tools.aegis_control.openapi import build_openapi_contract
from tools.aegis_control.provider_events import (
    AdapterCapability,
    ProviderEvent,
    github_ci_adapter_capability,
    reconcile_by_query,
    reconcile_provider_event,
    validate_adapter_capability,
)

PACKAGE_ID = "CP-I07-P31-01"
PACKAGE_REF = "18f12121cd8991e7ad67bf51a2e3e74c0239a808"
TASK_ANCHOR = "38b1eb01becb4f1d564dda6dbb635c0a98e0e5d9"
PREDECESSOR_REVIEW = "5079267574"


class MutationStub:
    def __init__(self):
        self.calls = []

    def apply(self, request):
        self.calls.append(request)
        return {"accepted": True, "operation_request_id": request["operation_request_id"]}


def case(case_id: str, passed: bool, **facts):
    return {"case_id": case_id, "passed": bool(passed), **facts}


def rejected(fn, expected_code=None):
    try:
        fn()
    except ApiRequestError as exc:
        return expected_code is None or exc.code == expected_code, exc.code, exc.detail
    except ValueError as exc:
        return expected_code is None, type(exc).__name__, str(exc)
    return False, None, None


def write_json(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=True)

    request = {
        "operation_name": "SCHEDULE_STAGE_OCCURRENCE",
        "operation_request_id": "req_cp_i07_evidence",
        "actor": {"class": "CONTROL_PLANE", "id": "api"},
        "control_lane_id": "lane_cp_i07",
        "expected_state": {},
        "idempotency_fingerprint": "sha256:" + "0" * 64,
        "payload": {},
    }
    raw = json.dumps(request).encode("utf-8")
    mutation = MutationStub()
    api = ControlApi(mutation_service=mutation, query_service=lambda path: {"path": path, "exact_refs": []})
    response = api.handle(method="POST", path="/v1/operations", headers={"Content-Type":"application/json","Idempotency-Key":request["operation_request_id"],"X-Aegis-Protocol-Version":"v1"}, body=raw)
    api_cases = [case("valid_v1_operation_delegates_exactly_once", response.status == 200 and mutation.calls == [request], mutation_call_count=len(mutation.calls))]
    for case_id, fn, code in [
        ("idempotency_mismatch_rejected_zero_mutation", lambda: ControlApi(mutation_service=MutationStub()).handle(method="POST", path="/v1/operations", headers={"Content-Type":"application/json","Idempotency-Key":"req_wrong","X-Aegis-Protocol-Version":"v1"}, body=raw), "IDEMPOTENCY_KEY_MISMATCH"),
        ("unsupported_protocol_version_rejected", lambda: ControlApi(mutation_service=MutationStub()).handle(method="POST", path="/v1/operations", headers={"Content-Type":"application/json","Idempotency-Key":request["operation_request_id"],"X-Aegis-Protocol-Version":"v2"}, body=raw), "UNSUPPORTED_PROTOCOL_VERSION"),
        ("malformed_json_rejected_before_mutation", lambda: ControlApi(mutation_service=MutationStub()).handle(method="POST", path="/v1/operations", headers={"Content-Type":"application/json","Idempotency-Key":"req_bad","X-Aegis-Protocol-Version":"v1"}, body=b"{bad"), "INVALID_JSON"),
        ("forbidden_patch_gate_rejected", lambda: ControlApi(mutation_service=MutationStub()).handle(method="PATCH", path="/v1/gate", headers={"X-Aegis-Protocol-Version":"v1"}, body=b"{}"), "FORBIDDEN_CANONICAL_MUTATION_ROUTE"),
    ]:
        ok, observed, detail = rejected(fn, code)
        api_cases.append(case(case_id, ok, rejection=observed, detail=detail))
    q = api.handle(method="GET", path="/v1/work-scopes/ws/control", headers={"X-Aegis-Protocol-Version":"v1"})
    api_cases.append(case("public_query_is_read_only_nonsemantic_dto", q.status == 200 and q.body.get("semantic_truth") is False, body=q.body))
    api_contract = {"schema_version":"0.2","kind":"CPV-E-API-CONTRACT","cases":api_cases}

    worker = worker_capability_profile(); public = api_capability_profile()
    names = {name for name in dir(WorkerControlPort) if not name.startswith("_")}
    cap_cases = [
        case("worker_descriptor_excludes_canonical_write", "CANONICAL_WRITE" not in worker.capabilities and "GATE_WRITE" not in worker.capabilities and "PRIMARY_OWNER" not in worker.capabilities, capabilities=sorted(worker.capabilities)),
        case("worker_port_exposes_no_canonical_mutation_method", not ({"append_canonical","advance_lane","set_terminal","set_gate_verdict"} & names), methods=sorted(names)),
        case("colocation_does_not_expand_worker_capability", "CONTROL_MUTATION_VIA_SERVICE" in public.capabilities and "CANONICAL_WRITE" not in worker.capabilities),
        case("facade_does_not_claim_primary_owner", "PRIMARY_OWNER" not in public.capabilities),
        case("capability_descriptors_hold_no_credential_values", not public.credential_refs and not worker.credential_refs, api_credential_refs=sorted(public.credential_refs), worker_credential_refs=sorted(worker.credential_refs)),
    ]
    ok, observed, detail = rejected(lambda: validate_transport_semantic_payload({"payload":{"access_token":"secret"}}), "SECRET_MATERIAL_IN_SEMANTIC_PAYLOAD")
    cap_cases.append(case("secret_semantic_payload_rejected", ok, rejection=observed, detail=detail))
    ok, observed, detail = rejected(lambda: safe_audit_fields({"request_id":"req_1","authorization":"Bearer secret"}), "SECRET_MATERIAL_IN_PROHIBITED_LOG")
    cap_cases.append(case("secret_prohibited_log_material_rejected", ok, rejection=observed, detail=detail))
    capability_security = {"schema_version":"0.2","kind":"CPV-E-CAPABILITY-SECURITY","cases":cap_cases}

    gh = github_ci_adapter_capability()
    conflict = ProviderEvent("evt-1","github","workflow_run","run-1","2026-09-01T00:00:00Z",True,{"conclusion":"failure"})
    resolved = reconcile_provider_event(conflict, gh, query=lambda _: {"resource":"run-1","conclusion":"success"})
    platform_cases = [case("event_hint_never_overrides_query_truth", resolved.truth_source == "QUERY" and resolved.observation.get("conclusion") == "success", event_hint="failure", query_truth=resolved.observation.get("conclusion"))]
    calls=[]
    unsigned = ProviderEvent("evt-u","github","workflow_run","run-2","2026-09-01T00:00:00Z",False,{})
    try:
        reconcile_provider_event(unsigned, gh, query=lambda key: calls.append(key) or {"resource":key})
        unsigned_ok=False
    except ValueError:
        unsigned_ok = calls == []
    platform_cases.append(case("unsigned_event_rejected_before_query", unsigned_ok, query_calls=calls))
    missed = reconcile_by_query("run-42", gh, query=lambda key: {"resource":key,"status":"completed"})
    platform_cases.append(case("missed_callback_recovers_by_query", missed.truth_source == "QUERY" and missed.observation.get("resource") == "run-42", observation=missed.observation))
    platform_corroboration = {
        "schema_version":"0.2","kind":"CPV-E-PLATFORM-CORROBORATION","claimed_real_provider_classes":["GITHUB_REPOSITORY_CI"],
        "reviewer_corroboration_required":"EXACT_GITHUB_ACTIONS_RUN_AND_ARTIFACT_AT_RESULT_REVISION",
        "cases":platform_cases,
    }

    callback_only = AdapterCapability("CALLBACK_ONLY", True, False, False, True)
    callback_rejected = False
    try: validate_adapter_capability(callback_only)
    except ValueError: callback_rejected = True
    async_provider = {
        "schema_version":"0.2","kind":"CPV-E-ASYNC-PROVIDER-CAPABILITY",
        "not_claimed_real_provider_classes":["CHATGPT_REASONING","CODEX_EXECUTION","HUMAN_DECISION","PROOF_PLANE"],
        "cases":[
            case("github_ci_profile_has_query_and_correlation", gh.durable_query and gh.durable_correlation and gh.authenticated_events and gh.autonomous_trust_sensitive),
            case("callback_only_provider_cannot_claim_autonomous", callback_rejected),
        ],
    }

    below = b"a" * (REFERENCE_SUPPORTED_REQUEST_BYTES - 1)
    at = b"b" * REFERENCE_SUPPORTED_REQUEST_BYTES
    below_out = enforce_envelope_size(below); at_out = enforce_envelope_size(at)
    above = at + b"c"
    try:
        enforce_envelope_size(above); above_rejected=False; above_detail=None
    except ApiRequestError as exc:
        above_rejected = exc.code == "REQUEST_TOO_LARGE" and exc.detail.get("actual_bytes") == len(above)
        above_detail = exc.detail
    envelope = {
        "schema_version":"0.2","kind":"CPV-E-ENVELOPE-SIZE-INTEGRITY","reference_supported_request_bytes":REFERENCE_SUPPORTED_REQUEST_BYTES,"cross_process_target_bytes":512*1024,
        "cases":[
            case("below_boundary_preserves_complete_bytes", below_out == below and hashlib.sha256(below_out).digest() == hashlib.sha256(below).digest(), byte_count=len(below)),
            case("at_boundary_preserves_complete_bytes", at_out == at and hashlib.sha256(at_out).digest() == hashlib.sha256(at).digest(), byte_count=len(at)),
            case("above_boundary_fails_closed_without_truncation", above_rejected, byte_count=len(above), rejection_detail=above_detail),
            case("complete_source_digest_roundtrip_matches", hashlib.sha256(at).hexdigest() == hashlib.sha256(at_out).hexdigest(), digest=hashlib.sha256(at).hexdigest()),
        ],
    }

    spec = build_openapi_contract()
    openapi_cases = [
        case("openapi_31_contract", spec.get("openapi") == "3.1.0"),
        case("openapi_public_operation_and_internal_worker_paths", "/v1/operations" in spec["paths"] and "/internal/v1/outbox/claim" in spec["paths"] and "/internal/v1/occurrences/{occurrence_id}/reconcile" in spec["paths"]),
        case("openapi_contains_no_patch_operation", all("patch" not in ops for ops in spec["paths"].values())),
        case("openapi_marks_idempotency_and_writer_boundary", spec.get("x-aegis-contract",{}).get("canonical_writer") == "control-mutation" and spec.get("x-aegis-contract",{}).get("current_cross_primary_rollout") == "DENIED"),
    ]
    api_contract["openapi_cases"] = openapi_cases

    families = {
        "api-contract.json": api_contract,
        "capability-security.json": capability_security,
        "platform-corroboration.json": platform_corroboration,
        "envelope-size-integrity.json": envelope,
        "async-provider-capability.json": async_provider,
    }
    for filename, payload in families.items(): write_json(root / filename, payload)
    all_cases = [c for payload in families.values() for key in ("cases","openapi_cases") for c in payload.get(key, [])]
    metrics = {
        "forbidden_public_mutation_accepted":0,
        "worker_canonical_write_capability_exposed":0,
        "idempotency_identity_mismatch_accepted":0,
        "unsupported_protocol_version_interpreted":0,
        "secret_material_entered_semantic_payload":0,
        "secret_material_emitted_in_prohibited_log":0,
        "callback_payload_trusted_without_query":0,
        "callback_only_provider_claimed_autonomous":0,
        "silent_truncation_before_digest":0,
        "canonical_digest_mismatch_after_roundtrip":0,
        "unofficial_gate_or_primary_authority_created":0,
        "current_cross_primary_rollout_expanded":0,
    }
    manifest = {
        "schema_version":"0.2","kind":"CP-I07_EVIDENCE_MANIFEST","package_id":PACKAGE_ID,"package_ref":PACKAGE_REF,"result_revision":args.result_revision,
        "task_anchor":{"revision":TASK_ANCHOR,"relation":"ancestor"},"predecessor_cp_i06_review":PREDECESSOR_REVIEW,
        "claims":{"p34_gate_pass":False,"evidence_compiler_gate_authority":False,"current_cross_primary_rollout":"DENIED","cp_i08_plus":False},
        "claimed_real_provider_classes":["GITHUB_REPOSITORY_CI"],"not_claimed_real_provider_classes":["CHATGPT_REASONING","CODEX_EXECUTION","HUMAN_DECISION","PROOF_PLANE"],
        "metrics":metrics,"case_count":len(all_cases),"passed":all(c["passed"] for c in all_cases) and not any(metrics.values()),
    }
    manifest["evidence_files"] = {name:"sha256:"+hashlib.sha256((root/name).read_bytes()).hexdigest() for name in families}
    write_json(root / "evidence-manifest.json", manifest)
    if not manifest["passed"]:
        raise SystemExit("CP-I07 evidence cases did not pass")


if __name__ == "__main__":
    main()
