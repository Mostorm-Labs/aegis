from __future__ import annotations

from datetime import datetime, timezone
import inspect
import unittest

from tools import aegis_control


NOW = datetime(2026, 8, 31, 16, 2, tzinfo=timezone.utc)


def exact_ref(object_type: str, object_id: str, digit: str):
    return {
        "object_type": object_type,
        "id": object_id,
        "ref": f"test:{object_type}:{object_id}",
        "identity": {"scheme": "sha256", "value": "sha256:" + digit * 64},
    }


class CpI04ChildAcceptanceResolverTests(unittest.TestCase):
    def _fixture(self):
        params = inspect.signature(aegis_control.TrustResolver).parameters
        if "acceptance_contract_sources" not in params or not hasattr(aegis_control.TrustResolver, "resolve_child_acceptance"):
            self.fail("CP-I04 child acceptance resolver contract is not implemented")
        adapter = aegis_control.DeterministicExternalAdapter(
            source_kind="PROJECT_STATE",
            adapter_id="project-state-child",
            secret=b"child-acceptance-test",
            callback_available=True,
            query_correlation_available=True,
            clock=lambda: NOW,
        )
        gate_ref = exact_ref("GATE_DECISION", "gate-child-pass", "5")
        adapter.set_resource(
            "child/ws-child/acceptance",
            version_scheme="gate-decision",
            version_value="gd1",
            resolved_refs=[gate_ref],
            satisfies=True,
        )
        contract_ref = exact_ref("CONTRACT", "contract-child", "6")
        resolver = aegis_control.TrustResolver(
            {"PROJECT_STATE": adapter},
            acceptance_contract_sources={
                "contract-child": aegis_control.TrustFactRequest(
                    "PROJECT_STATE", "child/ws-child/acceptance"
                )
            },
        )
        scope = {"id_scheme": "control-work-scope-v0.2", "id": "ws-child", "child_work_binding": None}
        completion = exact_ref("STAGE_OCCURRENCE", "so-child-terminal", "7")
        return resolver, contract_ref, gate_ref, scope, completion

    def test_resolver_derives_child_acceptance_from_exact_contract_facts(self):
        resolver, contract_ref, gate_ref, scope, completion = self._fixture()
        support = resolver.resolve_child_acceptance(scope, completion, [contract_ref])
        self.assertTrue(support.accepted)
        self.assertEqual((gate_ref,), support.acceptance_fact_refs)
        self.assertEqual((contract_ref,), support.acceptance_contract_refs)
        self.assertTrue(support.snapshot_resolution.valid)
        self.assertTrue(support.acceptance_basis_digest.startswith("sha256:"))

    def test_wrong_or_duplicate_acceptance_contract_fails_closed(self):
        resolver, contract_ref, _, scope, completion = self._fixture()
        wrong_contract = exact_ref("CONTRACT", "contract-other", "8")
        wrong = resolver.resolve_child_acceptance(scope, completion, [wrong_contract])
        self.assertFalse(wrong.accepted)
        self.assertEqual("REQUIRED_CHILD_WORK_NOT_ACCEPTED", wrong.code)
        self.assertEqual((), wrong.acceptance_fact_refs)

        duplicate = resolver.resolve_child_acceptance(scope, completion, [contract_ref, contract_ref])
        self.assertFalse(duplicate.accepted)
        self.assertEqual("CHILD_ACCEPTANCE_BASIS_AMBIGUOUS", duplicate.code)
        self.assertEqual((), duplicate.acceptance_fact_refs)


if __name__ == "__main__":
    unittest.main()
