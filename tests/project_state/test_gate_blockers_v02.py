import unittest
from pathlib import Path

from tools.aegis_state.compute import compute_state
from tools.aegis_state.model import ManifestSet


def make_manifests(verdict="BLOCKED_ENVIRONMENT", validity="current"):
    return ManifestSet(
        root=Path("."),
        project={"schema_version":"0.1","project":{"id":"demo","name":"Demo","profile":"standard","lifecycle_hint":"verification"}},
        authorities={"schema_version":"0.1","authorities":[{"id":"auth","scope":"eval","kind":"verification","version":"v1","status":"Current","ref":"docs/eval.md","depends_on":[]}],"impact_reviews":[]},
        gates={"schema_version":"0.1","gates":[{"id":"G1","stage":"P34","verdict":verdict,"validity":validity,"authority_ids":["auth"],"evidence_ids":["ev"]}]},
        evidence={"schema_version":"0.1","evidence":[{"id":"ev","type":"probe","ref":"ci://probe","status":"available"}]},
    )


class GateBlockerV02Tests(unittest.TestCase):
    def test_blocked_environment_becomes_verification_blocker(self):
        state = compute_state(make_manifests("BLOCKED_ENVIRONMENT"))
        self.assertEqual(state.get("blocking_gates"), ["G1"])
        self.assertEqual(state.get("earliest_untrusted_layer"), "verification")
        self.assertEqual(state.get("recommended_next_stage"), "P34")

    def test_blocked_authority_routes_p21(self):
        state = compute_state(make_manifests("BLOCKED_AUTHORITY"))
        self.assertEqual(state.get("earliest_untrusted_layer"), "authority")
        self.assertEqual(state.get("recommended_next_stage"), "P21")

    def test_blocked_implementation_routes_p35(self):
        state = compute_state(make_manifests("BLOCKED_IMPLEMENTATION"))
        self.assertEqual(state.get("earliest_untrusted_layer"), "implementation")
        self.assertEqual(state.get("recommended_next_stage"), "P35")

    def test_blocked_evidence_routes_p34(self):
        state = compute_state(make_manifests("BLOCKED_EVIDENCE"))
        self.assertEqual(state.get("earliest_untrusted_layer"), "verification")
        self.assertEqual(state.get("recommended_next_stage"), "P34")

    def test_pass_with_findings_is_not_blocker(self):
        state = compute_state(make_manifests("PASS_WITH_FINDINGS"))
        self.assertEqual(state.get("blocking_gates"), [])

    def test_stale_blocked_gate_is_not_active_verdict_blocker(self):
        state = compute_state(make_manifests("BLOCKED_ENVIRONMENT", "stale"))
        self.assertEqual(state.get("blocking_gates"), [])


if __name__ == "__main__":
    unittest.main()
