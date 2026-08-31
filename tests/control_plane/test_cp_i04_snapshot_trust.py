from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from tools import aegis_control


NOW = datetime(2026, 8, 31, 16, 0, tzinfo=timezone.utc)


def exact_ref(object_type: str, object_id: str, value: str):
    return {
        "object_type": object_type,
        "id": object_id,
        "ref": f"test:{object_type}:{object_id}",
        "identity": {"scheme": "sha256", "value": value},
    }


class CpI04SnapshotTrustTests(unittest.TestCase):
    def _adapter(
        self,
        *,
        adapter_id="project-state-a",
        source_kind="PROJECT_STATE",
        query_correlation=True,
        clock=None,
    ):
        required = (
            "DeterministicExternalAdapter",
            "TrustFactRequest",
            "TrustResolver",
        )
        missing = [name for name in required if not hasattr(aegis_control, name)]
        if missing:
            self.fail(f"CP-I04 public trust surface missing: {missing}")
        return aegis_control.DeterministicExternalAdapter(
            source_kind=source_kind,
            adapter_id=adapter_id,
            secret=b"cp-i04-test-secret",
            callback_available=True,
            query_correlation_available=query_correlation,
            clock=clock or (lambda: NOW),
        )

    def test_snapshot_token_rejects_tamper_wrong_adapter_and_complete_version_drift(self):
        adapter = self._adapter()
        adapter.set_resource(
            "gate/main",
            version_scheme="git-commit+blob",
            version_value="v1",
            resolved_refs=[exact_ref("GATE_DECISION", "gate-1", "sha256:" + "1" * 64)],
            satisfies=True,
        )
        snapshot = adapter.resolve("gate/main")
        self.assertTrue(adapter.verify_snapshot(snapshot.snapshot_token, expected_resource_key="gate/main").valid)

        replacement = "A" if snapshot.snapshot_token[-1] != "A" else "B"
        tampered_tag = snapshot.snapshot_token[:-1] + replacement
        result = adapter.verify_snapshot(tampered_tag, expected_resource_key="gate/main")
        self.assertFalse(result.valid)
        self.assertEqual("SNAPSHOT_INTEGRITY_INVALID", result.code)

        prefix, payload, tag = snapshot.snapshot_token.split(".")
        payload_replacement = "A" if payload[-1] != "A" else "B"
        tampered_payload = f"{prefix}.{payload[:-1]}{payload_replacement}.{tag}"
        result = adapter.verify_snapshot(tampered_payload, expected_resource_key="gate/main")
        self.assertFalse(result.valid)
        self.assertEqual("SNAPSHOT_INTEGRITY_INVALID", result.code)

        wrong_adapter = self._adapter(adapter_id="project-state-b")
        wrong_adapter.set_resource(
            "gate/main",
            version_scheme="git-commit+blob",
            version_value="v1",
            resolved_refs=[exact_ref("GATE_DECISION", "gate-1", "sha256:" + "1" * 64)],
            satisfies=True,
        )
        result = wrong_adapter.verify_snapshot(snapshot.snapshot_token, expected_resource_key="gate/main")
        self.assertFalse(result.valid)
        self.assertEqual("SNAPSHOT_ADAPTER_MISMATCH", result.code)

        wrong_source = self._adapter(source_kind="PROOF_PLANE")
        wrong_source.set_resource(
            "gate/main",
            version_scheme="git-commit+blob",
            version_value="v1",
            resolved_refs=[exact_ref("GATE_DECISION", "gate-1", "sha256:" + "1" * 64)],
            satisfies=True,
        )
        result = wrong_source.verify_snapshot(snapshot.snapshot_token, expected_resource_key="gate/main")
        self.assertFalse(result.valid)
        self.assertEqual("SNAPSHOT_SOURCE_KIND_MISMATCH", result.code)

        adapter.set_resource(
            "gate/other",
            version_scheme="git-commit+blob",
            version_value="v1",
            resolved_refs=[exact_ref("GATE_DECISION", "gate-other", "sha256:" + "2" * 64)],
            satisfies=True,
        )
        result = adapter.verify_snapshot(snapshot.snapshot_token, expected_resource_key="gate/other")
        self.assertFalse(result.valid)
        self.assertEqual("SNAPSHOT_RESOURCE_MISMATCH", result.code)

        adapter.set_resource(
            "gate/main",
            version_scheme="semantic-version",
            version_value="v1",
            resolved_refs=[exact_ref("GATE_DECISION", "gate-1", "sha256:" + "1" * 64)],
            satisfies=True,
        )
        stale_scheme = adapter.verify_snapshot(snapshot.snapshot_token, expected_resource_key="gate/main")
        self.assertFalse(stale_scheme.valid)
        self.assertEqual("SNAPSHOT_VERSION_STALE", stale_scheme.code)

        adapter.set_resource(
            "gate/main",
            version_scheme="git-commit+blob",
            version_value="v2",
            resolved_refs=[exact_ref("GATE_DECISION", "gate-2", "sha256:" + "2" * 64)],
            satisfies=True,
        )
        stale_value = adapter.verify_snapshot(snapshot.snapshot_token, expected_resource_key="gate/main")
        self.assertFalse(stale_value.valid)
        self.assertEqual("SNAPSHOT_VERSION_STALE", stale_value.code)

    def test_snapshot_token_rejects_expired_currentness_window(self):
        observed = [NOW]
        adapter = self._adapter(clock=lambda: observed[0])
        adapter.set_resource(
            "gate/expiring",
            version_scheme="gate-version",
            version_value="v1",
            resolved_refs=[exact_ref("GATE_DECISION", "gate-expiring", "sha256:" + "b" * 64)],
            satisfies=True,
        )
        snapshot = adapter.resolve("gate/expiring")
        observed[0] = NOW + timedelta(seconds=11)
        result = adapter.verify_snapshot(snapshot.snapshot_token, expected_resource_key="gate/expiring")
        self.assertFalse(result.valid)
        self.assertEqual("SNAPSHOT_EXPIRED", result.code)

    def test_trust_resolver_bundle_becomes_stale_when_provider_version_changes(self):
        adapter = self._adapter()
        adapter.set_resource(
            "proof/result",
            version_scheme="proof-version",
            version_value="p1",
            resolved_refs=[exact_ref("PROOF_EVALUATION", "proof-1", "sha256:" + "3" * 64)],
            satisfies=True,
        )
        resolver = aegis_control.TrustResolver({"PROJECT_STATE": adapter})
        bundle = resolver.resolve_for_mutation(
            [aegis_control.TrustFactRequest("PROJECT_STATE", "proof/result")]
        )
        self.assertTrue(bundle.valid)
        self.assertTrue(resolver.verify_freshness(bundle).valid)

        adapter.set_resource(
            "proof/result",
            version_scheme="proof-version-v2",
            version_value="p1",
            resolved_refs=[exact_ref("PROOF_EVALUATION", "proof-1", "sha256:" + "3" * 64)],
            satisfies=True,
        )
        self.assertFalse(resolver.verify_freshness(bundle).valid)

        adapter.set_resource(
            "proof/result",
            version_scheme="proof-version",
            version_value="p1",
            resolved_refs=[exact_ref("PROOF_EVALUATION", "proof-1", "sha256:" + "3" * 64)],
            satisfies=True,
        )
        bundle = resolver.resolve_for_mutation(
            [aegis_control.TrustFactRequest("PROJECT_STATE", "proof/result")]
        )
        adapter.set_resource(
            "proof/result",
            version_scheme="proof-version",
            version_value="p2",
            resolved_refs=[exact_ref("PROOF_EVALUATION", "proof-2", "sha256:" + "4" * 64)],
            satisfies=True,
        )
        self.assertFalse(resolver.verify_freshness(bundle).valid)

    def test_callback_only_provider_is_not_full_autonomous_trust_capability(self):
        callback_only = self._adapter(query_correlation=False)
        self.assertFalse(callback_only.capability.full_autonomous_trust_capable)

        queryable = self._adapter(query_correlation=True)
        self.assertTrue(queryable.capability.full_autonomous_trust_capable)


if __name__ == "__main__":
    unittest.main()
