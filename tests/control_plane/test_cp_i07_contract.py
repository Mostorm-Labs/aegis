from __future__ import annotations

import unittest


class CpI07ContractRedTests(unittest.TestCase):
    def test_public_api_module_exists_and_exposes_v1_operation_boundary(self):
        try:
            from tools.aegis_control.api import ControlApi, ApiRequestError
        except ImportError as exc:
            self.fail(f"CP-I07 public API boundary is not implemented: {exc}")
        self.assertIsNotNone(ControlApi)
        self.assertIsNotNone(ApiRequestError)

    def test_capability_module_denies_worker_canonical_write(self):
        try:
            from tools.aegis_control.capabilities import worker_capability_profile
        except ImportError as exc:
            self.fail(f"CP-I07 capability boundary is not implemented: {exc}")
        profile = worker_capability_profile()
        self.assertNotIn("CANONICAL_WRITE", profile.capabilities)
        self.assertNotIn("GATE_WRITE", profile.capabilities)
        self.assertNotIn("PRIMARY_OWNER", profile.capabilities)

    def test_provider_event_module_requires_query_for_autonomous_claim(self):
        try:
            from tools.aegis_control.provider_events import AdapterCapability, validate_adapter_capability
        except ImportError as exc:
            self.fail(f"CP-I07 provider-event boundary is not implemented: {exc}")
        with self.assertRaises(ValueError):
            validate_adapter_capability(AdapterCapability(provider_class="CALLBACK_ONLY", authenticated_events=True, durable_query=False, durable_correlation=False, autonomous_trust_sensitive=True))

    def test_openapi_contract_is_31_and_has_no_forbidden_patch(self):
        try:
            from tools.aegis_control.openapi import build_openapi_contract
        except ImportError as exc:
            self.fail(f"CP-I07 OpenAPI contract is not implemented: {exc}")
        spec = build_openapi_contract()
        self.assertTrue(spec["openapi"].startswith("3.1"))
        self.assertIn("/v1/operations", spec["paths"])
        for forbidden in ("/status", "/cursor", "/gate", "/stage-occurrence"):
            self.assertNotIn(forbidden, spec["paths"])


if __name__ == "__main__":
    unittest.main()
