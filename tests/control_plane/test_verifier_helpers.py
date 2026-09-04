import unittest

import verifier_helpers as vh


class VerifierHelperTests(unittest.TestCase):
    def setUp(self):
        self.key = b"cp-i01-test-key"
        self.payload = {"adapter": "github", "source_kind": "pull_request", "resource_id": "Mostorm-Labs/aegis#29", "resource_version": "e8b2fa8c2bd29778a6a3c8bf5beb3d65ff9c364c"}
        self.binding = dict(self.payload)

    def test_valid_snapshot_token_and_binding(self):
        token = vh.issue_snapshot_token(self.payload, self.key)
        result = vh.verify_snapshot_token(token, self.key, self.binding)
        self.assertTrue(result.ok, result.reason)

    def test_m16_payload_mutation_with_original_tag_is_rejected_with_provenance(self):
        token = vh.issue_snapshot_token(self.payload, self.key)
        mutated = vh.mutate_snapshot_payload_without_resigning(token, "resource_version", "deadbeef")
        result = vh.verify_snapshot_token(mutated, self.key, self.binding)
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "INVALID_INTEGRITY")
        self.assertNotEqual(mutated, token)
        self.assertTrue(mutated.hex())

    def test_m17_wrong_adapter_source_kind_is_rejected(self):
        token = vh.issue_snapshot_token(self.payload, self.key)
        wrong = dict(self.binding, adapter="slack")
        result = vh.verify_snapshot_token(token, self.key, wrong)
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "BINDING_MISMATCH")

    def test_m18_wrong_resource_version_is_rejected(self):
        token = vh.issue_snapshot_token(self.payload, self.key)
        wrong = dict(self.binding, resource_version="other-version")
        result = vh.verify_snapshot_token(token, self.key, wrong)
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "BINDING_MISMATCH")

    def test_m19_callback_only_provider_is_not_full_autonomous(self):
        self.assertFalse(vh.supports_autonomous_trust_sensitive_provider(supports_callback=True, supports_durable_query=False, supports_correlation=False))
        self.assertTrue(vh.supports_autonomous_trust_sensitive_provider(supports_callback=True, supports_durable_query=True, supports_correlation=True))

    def test_m20_truncated_canonical_representation_is_rejected(self):
        full = b'{"payload":"0123456789"}'
        truncated = full[:12]
        digest = vh.sha256_prefixed(full)
        self.assertTrue(vh.verify_full_representation(full, full, digest))
        self.assertFalse(vh.verify_full_representation(full, truncated, digest))


if __name__ == "__main__":
    unittest.main()
