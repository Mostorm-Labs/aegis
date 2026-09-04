from __future__ import annotations

import hashlib
import json
import unittest


class _MutationStub:
    def __init__(self):
        self.calls = []

    def apply(self, request):
        self.calls.append(request)
        return {"operation_request_id": request["operation_request_id"], "accepted": True}


class CpI07CompletenessTests(unittest.TestCase):
    def test_valid_v1_operation_delegates_exactly_once(self):
        from tools.aegis_control.api import ControlApi
        mutation = _MutationStub()
        api = ControlApi(mutation_service=mutation)
        request = {
            "operation_name": "RECOMPUTE_CONTROL_PROJECTION",
            "operation_request_id": "req_valid_cp_i07",
            "actor": {"class": "CONTROL_PLANE", "id": "api"},
            "control_lane_id": "lane_cp_i07",
            "expected_state": {},
            "idempotency_fingerprint": "sha256:" + "0" * 64,
            "payload": {},
        }
        response = api.handle(
            method="POST",
            path="/v1/operations",
            headers={"Content-Type": "application/json", "Idempotency-Key": "req_valid_cp_i07", "X-Aegis-Protocol-Version": "v1"},
            body=json.dumps(request).encode("utf-8"),
        )
        self.assertEqual(200, response.status)
        self.assertEqual([request], mutation.calls)

    def test_public_query_response_is_explicitly_nonsemantic(self):
        from tools.aegis_control.api import ControlApi
        api = ControlApi(mutation_service=_MutationStub(), query_service=lambda path: {"path": path, "exact_refs": []})
        response = api.handle(method="GET", path="/v1/work-scopes/ws/control", headers={"X-Aegis-Protocol-Version": "v1"})
        self.assertEqual(200, response.status)
        self.assertFalse(response.body["semantic_truth"])

    def test_audit_fields_refuse_secret_values(self):
        from tools.aegis_control.api import ApiRequestError, safe_audit_fields
        with self.assertRaises(ApiRequestError) as ctx:
            safe_audit_fields({"request_id": "req_1", "authorization": "Bearer secret"})
        self.assertEqual("SECRET_MATERIAL_IN_PROHIBITED_LOG", ctx.exception.code)

    def test_unsigned_event_is_rejected_before_query(self):
        from tools.aegis_control.provider_events import AdapterCapability, ProviderEvent, reconcile_provider_event
        calls = []
        adapter = AdapterCapability("GITHUB_REPOSITORY_CI", True, True, True, True)
        event = ProviderEvent("evt-unsigned", "github", "workflow_run", "run-1", "2026-09-01T00:00:00Z", False, {})
        with self.assertRaises(ValueError):
            reconcile_provider_event(event, adapter, query=lambda key: calls.append(key) or {})
        self.assertEqual([], calls)

    def test_missed_callback_reconciles_through_durable_query(self):
        from tools.aegis_control.provider_events import github_ci_adapter_capability, reconcile_by_query
        result = reconcile_by_query("run-42", github_ci_adapter_capability(), query=lambda key: {"resource": key, "status": "completed"})
        self.assertEqual("QUERY", result.truth_source)
        self.assertEqual("run-42", result.observation["resource"])

    def test_reference_request_limit_accepts_exact_bytes_and_rejects_plus_one_without_truncation(self):
        from tools.aegis_control.api import ApiRequestError, REFERENCE_SUPPORTED_REQUEST_BYTES, enforce_envelope_size
        at_limit = b"x" * REFERENCE_SUPPORTED_REQUEST_BYTES
        self.assertEqual(at_limit, enforce_envelope_size(at_limit))
        source_digest = hashlib.sha256(at_limit).hexdigest()
        self.assertEqual(source_digest, hashlib.sha256(enforce_envelope_size(at_limit)).hexdigest())
        with self.assertRaises(ApiRequestError) as ctx:
            enforce_envelope_size(at_limit + b"x")
        self.assertEqual("REQUEST_TOO_LARGE", ctx.exception.code)
        self.assertEqual(REFERENCE_SUPPORTED_REQUEST_BYTES + 1, ctx.exception.detail["actual_bytes"])

    def test_capability_profiles_contain_references_not_secret_values(self):
        from tools.aegis_control.capabilities import api_capability_profile, worker_capability_profile
        for profile in (api_capability_profile(), worker_capability_profile()):
            self.assertEqual(frozenset(), profile.credential_refs)
            self.assertNotIn("PRIMARY_OWNER", profile.capabilities)
            self.assertNotIn("GATE_WRITE", profile.capabilities)


if __name__ == "__main__":
    unittest.main()
