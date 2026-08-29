import copy
import unittest
from pathlib import Path

from tools.aegis_state.model import ManifestSet
from tools.aegis_state.transition_v05 import validate_v05_transition


def manifest_with(decisions):
    return ManifestSet(
        root=Path(".aegis"),
        project={"schema_version": "0.5", "project": {"id": "demo", "name": "Demo", "profile": "standard"}},
        authorities={"schema_version": "0.5", "authorities": [], "impact_reviews": []},
        gates={
            "schema_version": "0.5",
            "gates": [{"id": "G1", "stage": "P34", "authority_ids": []}],
            "decisions": copy.deepcopy(decisions),
        },
        evidence={"schema_version": "0.5", "evidence": []},
        integrations={"schema_version": "0.5", "integrations": []},
    )


D1_BLOCKED = {
    "id": "G1::decision::0001",
    "gate_id": "G1",
    "verdict": "BLOCKED_EVIDENCE",
    "evidence_ids": ["ev-old"],
}
D2_PASS = {
    "id": "G1::decision::0002",
    "gate_id": "G1",
    "verdict": "PASS",
    "evidence_ids": ["ev-new"],
    "supersedes": "G1::decision::0001",
}


class GateDecisionTransitionV05Tests(unittest.TestCase):
    def test_existing_decision_verdict_cannot_be_mutated_in_place(self):
        previous = manifest_with([D1_BLOCKED])
        changed = copy.deepcopy(D1_BLOCKED)
        changed["verdict"] = "PASS"
        current = manifest_with([changed])
        errors = validate_v05_transition(previous, current)
        self.assertTrue(any("immutable gate decision" in error for error in errors), errors)

    def test_existing_decision_evidence_set_cannot_be_mutated_in_place(self):
        previous = manifest_with([D1_BLOCKED])
        changed = copy.deepcopy(D1_BLOCKED)
        changed["evidence_ids"] = ["ev-rewritten"]
        current = manifest_with([changed])
        errors = validate_v05_transition(previous, current)
        self.assertTrue(any("immutable gate decision" in error for error in errors), errors)

    def test_existing_decision_cannot_be_deleted(self):
        previous = manifest_with([D1_BLOCKED])
        current = manifest_with([])
        errors = validate_v05_transition(previous, current)
        self.assertTrue(any("removed immutable gate decision" in error for error in errors), errors)

    def test_append_new_decision_preserves_existing_history(self):
        previous = manifest_with([D1_BLOCKED])
        current = manifest_with([D1_BLOCKED, D2_PASS])
        self.assertEqual([], validate_v05_transition(previous, current))

    def test_gate_contract_identity_cannot_be_reassigned(self):
        previous = manifest_with([D1_BLOCKED])
        current = manifest_with([D1_BLOCKED])
        current.gates["gates"][0]["stage"] = "P35"
        errors = validate_v05_transition(previous, current)
        self.assertTrue(any("immutable gate contract" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
