from __future__ import annotations

from datetime import datetime, timezone
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
    def _adapter(self, *, adapter_id="project-state-a", query_correlation=True):
        required = (
            "DeterministicExternalAdapter",
            "TrustFactRequest",
            "TrustResolver",
        )
        missing = [name for name in required if not hasattr(aegis_control, name)]
        if missing:
            self.fail(f"CP-I04 public trust surface missing: {missing}")
        return aegis_control.DeterministicExternalAdapter(
            source_kind="PROJECT_STATE",
            adapter_id=adapter_id,
            secret=b"cp-i04-test-secret",
            callback_available=True,
            query_correlation_available=query_correlation,
            clock=lambda: NOW,
        )

    def test_snapshot_token_rejects_tamper_wrong_adapter_and_version_drift(self):
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
        tampered = snapshot.snapshot_token[:-1] + replacement
        self.assertFalse(adapter.verify_snapshot(tampered, expected_resource_key="gate/main").valid)

        wrong_adapter = self._adapter(adapter_id="project-state-b")
        wrong_adapter.set_resource(
            "gate/main",
            version_scheme="git-commit+blob",
            version_value="v1",
            resolved_refs=[exact_ref("GATE_DECISION", "gate-1", "sha256:" + "1" * 64)],
            satisfies=True,
        )
        self.assertFalse(wrong_adapter.verify_snapshot(snapshot.snapshot_token, expected_resource_key="gate/main").valid)

        adapter.set_resource(
            "gate/main",
            version_scheme="git-commit+blob",
            version_value="v2",
            resolved_refs=[exact_ref("GATE_DECISION", "gate-2", "sha256:" + "2" * 64)],
            satisfies=True,
        )
        stale = adapter.verify_snapshot(snapshot.snapshot_token, expected_resource_key="gate/main")
        self.assertFalse(stale.valid)
        self.assertEqual("SNAPSHOT_VERSION_STALE", stale.code)

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
