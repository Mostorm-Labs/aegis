import unittest
from unittest import mock

import qualification
import reference_model as crm


FROZEN_OCCURRENCE = {
    "control_lane_id": "lane_1",
    "stage_span": {"stages": ["P32"]},
    "primary_owner": "aegis-implementation",
    "trusted_basis": {"digest": "basis"},
    "policy_binding": {"digest": "policy"},
    "schedule_basis": {"reason": "NEXT"},
    "input_refs": ["input@1"],
    "repair_context": None,
}


def occurrence(revision, state, **updates):
    record = {
        "kind": "STAGE_OCCURRENCE",
        "id": "so_1",
        "record_revision": revision,
        "state": state,
        **FROZEN_OCCURRENCE,
        "execution_navigation": None,
        "terminal": None if state == "OPEN" else {"status": "READY"},
    }
    record.update(updates)
    return record


class P36ReferenceModelRegressionTests(unittest.TestCase):
    def test_terminate_is_operation_and_state_aware(self):
        current = occurrence(1, "OPEN")
        proposed = occurrence(2, "TERMINAL")
        self.assertEqual(
            crm.transition_violations(
                "TERMINATE_STAGE_OCCURRENCE",
                current,
                proposed,
                {"target_record_revision": 1},
            ),
            set(),
        )
        self.assertIn(
            "TARGET_NOT_OPEN",
            crm.transition_violations(
                "TERMINATE_STAGE_OCCURRENCE",
                proposed,
                occurrence(3, "TERMINAL"),
                {"target_record_revision": 2},
            ),
        )

    def test_progress_cannot_change_frozen_start_facts(self):
        current = occurrence(1, "OPEN")
        proposed = occurrence(
            2,
            "OPEN",
            stage_span={"stages": ["P33"]},
            execution_navigation={"cursor": "abc"},
        )
        self.assertIn(
            "FROZEN_START_FACT_CHANGED",
            crm.transition_violations(
                "RECORD_EXECUTION_PROGRESS",
                current,
                proposed,
                {"target_record_revision": 1},
            ),
        )

    def test_expected_revision_guard_is_independent(self):
        current = {"kind": "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "id": "pkg_1", "record_revision": 1}
        proposed = {"kind": "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "id": "pkg_1", "record_revision": 2}
        self.assertEqual(
            crm.transition_violations(
                "REVISE_IMPLEMENTATION_PACKAGE",
                current,
                proposed,
                {"target_record_revision": 1},
            ),
            set(),
        )
        self.assertIn(
            "EXPECTED_REVISION_MISMATCH",
            crm.transition_violations(
                "REVISE_IMPLEMENTATION_PACKAGE",
                current,
                proposed,
                {"target_record_revision": 9},
            ),
        )

    def test_package_lineage_preserves_identity_and_revision(self):
        good = [
            {"kind": "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "id": "pkg_1", "record_revision": 1},
            {"kind": "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "id": "pkg_1", "record_revision": 2},
        ]
        self.assertEqual(crm.lineage_violations(good), set())
        self.assertIn(
            "LINEAGE_ID_CHANGED",
            crm.lineage_violations([good[0], {"kind": good[0]["kind"], "id": "pkg_2", "record_revision": 2}]),
        )
        self.assertIn(
            "NON_CONTIGUOUS_REVISION",
            crm.lineage_violations([good[0], {"kind": good[0]["kind"], "id": "pkg_1", "record_revision": 3}]),
        )

    def test_escalation_is_single_revision_immutable(self):
        one = [{"kind": "ESCALATION", "id": "esc_1", "record_revision": 1}]
        self.assertEqual(crm.lineage_violations(one), set())
        self.assertIn(
            "ESCALATION_IMMUTABLE",
            crm.lineage_violations(one + [{"kind": "ESCALATION", "id": "esc_1", "record_revision": 2}]),
        )

    def test_schedule_requires_new_open_occurrence(self):
        violations = crm.transition_violations("SCHEDULE_STAGE_OCCURRENCE", None, occurrence(2, "TERMINAL"))
        self.assertIn("INVALID_INITIAL_REVISION", violations)
        self.assertIn("SCHEDULE_MUST_CREATE_OPEN", violations)


class P36QualificationProvenanceRegressionTests(unittest.TestCase):
    def test_provenance_matches_exact_executed_snapshot_cases(self):
        cases = qualification.snapshot_qualification_cases()
        provenance = {item["mutant_id"]: item for item in qualification.snapshot_mutant_provenance()}
        original_verify = qualification.vh.verify_snapshot_token
        executed = []

        def capture(token, key, expected_binding):
            executed.append((token, key, dict(expected_binding)))
            return original_verify(token, key, expected_binding)

        with mock.patch.object(qualification.vh, "verify_snapshot_token", side_effect=capture):
            result = qualification.run_qualification()

        self.assertEqual(result["detected"], 20)
        self.assertEqual(result["false_acceptance"], 0)
        self.assertEqual(len(executed), 3)
        for mutant_id, (token, key, expected_binding) in zip(("M16", "M17", "M18"), executed):
            case = cases[mutant_id]
            self.assertEqual(token, case["token"])
            self.assertEqual(key, case["key"])
            self.assertEqual(expected_binding, case["expected_binding"])
            self.assertEqual(provenance[mutant_id]["expected_binding"], case["expected_binding"])
            self.assertEqual(provenance[mutant_id]["actual_binding"], case["actual_binding"])
            token_field = "mutated_token_hex" if mutant_id == "M16" else "token_hex"
            self.assertEqual(provenance[mutant_id][token_field], token.hex())


if __name__ == "__main__":
    unittest.main()
