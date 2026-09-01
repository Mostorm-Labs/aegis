from __future__ import annotations

import unittest


class CpI07IntegrityRedTests(unittest.TestCase):
    def test_secret_shaped_semantic_payload_is_rejected(self):
        from tools.aegis_control.api import ApiRequestError, validate_transport_semantic_payload
        with self.assertRaises(ApiRequestError) as ctx:
            validate_transport_semantic_payload({"payload": {"access_token": "secret-value"}})
        self.assertEqual("SECRET_MATERIAL_IN_SEMANTIC_PAYLOAD", ctx.exception.code)

    def test_callback_only_provider_cannot_claim_autonomous(self):
        from tools.aegis_control.provider_events import AdapterCapability, validate_adapter_capability
        with self.assertRaises(ValueError):
            validate_adapter_capability(AdapterCapability(provider_class="GITHUB_REPOSITORY_CI", authenticated_events=True, durable_query=False, durable_correlation=True, autonomous_trust_sensitive=True))

    def test_query_result_wins_over_conflicting_event_hint(self):
        from tools.aegis_control.provider_events import AdapterCapability, ProviderEvent, reconcile_provider_event
        adapter = AdapterCapability(provider_class="GITHUB_REPOSITORY_CI", authenticated_events=True, durable_query=True, durable_correlation=True, autonomous_trust_sensitive=True)
        event = ProviderEvent(event_id="evt-1", provider="github", event_kind="workflow_run", resource_hint="run-1", observed_at="2026-09-01T00:00:00Z", signature_verified=True, payload_hint={"conclusion":"failure"})
        result = reconcile_provider_event(event, adapter, query=lambda _: {"conclusion":"success","resource":"run-1"})
        self.assertEqual("success", result.observation["conclusion"]); self.assertEqual("QUERY", result.truth_source)

    def test_silent_truncation_is_never_accepted(self):
        from tools.aegis_control.api import ApiRequestError, enforce_envelope_size
        source = ("x" * 1025).encode("utf-8")
        with self.assertRaises(ApiRequestError) as ctx:
            enforce_envelope_size(source, max_bytes=1024)
        self.assertEqual("REQUEST_TOO_LARGE", ctx.exception.code); self.assertEqual(1025, ctx.exception.detail["actual_bytes"])


if __name__ == "__main__": unittest.main()
