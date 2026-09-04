from __future__ import annotations

import json
import unittest


class _MutationStub:
    def __init__(self): self.calls = []
    def apply(self, request): self.calls.append(request); return {"accepted": True, "operation_request_id": request["operation_request_id"]}


class CpI07ApiBehaviorRedTests(unittest.TestCase):
    def test_v1_operation_requires_matching_idempotency_key(self):
        from tools.aegis_control.api import ApiRequestError, ControlApi
        mutation = _MutationStub(); api = ControlApi(mutation_service=mutation)
        body = {"operation_name":"SCHEDULE_STAGE_OCCURRENCE","operation_request_id":"req_cp_i07","actor":{"class":"CONTROL_PLANE","id":"api"},"control_lane_id":"lane_cp_i07","expected_state":{},"idempotency_fingerprint":"sha256:"+"0"*64,"payload":{}}
        with self.assertRaises(ApiRequestError) as ctx:
            api.handle(method="POST", path="/v1/operations", headers={"Content-Type":"application/json","Idempotency-Key":"req_other","X-Aegis-Protocol-Version":"v1"}, body=json.dumps(body).encode("utf-8"))
        self.assertEqual("IDEMPOTENCY_KEY_MISMATCH", ctx.exception.code); self.assertEqual([], mutation.calls)

    def test_unsupported_version_fails_before_mutation(self):
        from tools.aegis_control.api import ApiRequestError, ControlApi
        mutation = _MutationStub(); api = ControlApi(mutation_service=mutation)
        with self.assertRaises(ApiRequestError) as ctx:
            api.handle(method="POST", path="/v1/operations", headers={"Content-Type":"application/json","Idempotency-Key":"req_x","X-Aegis-Protocol-Version":"v2"}, body=b"{}")
        self.assertEqual("UNSUPPORTED_PROTOCOL_VERSION", ctx.exception.code); self.assertEqual([], mutation.calls)

    def test_forbidden_patch_route_fails_closed(self):
        from tools.aegis_control.api import ApiRequestError, ControlApi
        api = ControlApi(mutation_service=_MutationStub())
        with self.assertRaises(ApiRequestError) as ctx:
            api.handle(method="PATCH", path="/v1/gate", headers={"Content-Type":"application/json","X-Aegis-Protocol-Version":"v1"}, body=b"{}")
        self.assertEqual("FORBIDDEN_CANONICAL_MUTATION_ROUTE", ctx.exception.code)

    def test_malformed_json_fails_before_mutation(self):
        from tools.aegis_control.api import ApiRequestError, ControlApi
        mutation = _MutationStub(); api = ControlApi(mutation_service=mutation)
        with self.assertRaises(ApiRequestError) as ctx:
            api.handle(method="POST", path="/v1/operations", headers={"Content-Type":"application/json","Idempotency-Key":"req_x","X-Aegis-Protocol-Version":"v1"}, body=b"{not-json")
        self.assertEqual("INVALID_JSON", ctx.exception.code); self.assertEqual([], mutation.calls)


if __name__ == "__main__": unittest.main()
