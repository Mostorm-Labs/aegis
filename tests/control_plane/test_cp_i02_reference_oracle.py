import unittest
from copy import deepcopy

from tests.control_plane.cp_i02_fixtures import (
    expected_state,
    occurrence_record,
    package_record,
    terminal_facts,
)
from tests.control_plane.reference_model import (
    idempotency_expectation,
    lineage_violations,
    transition_violations,
)


class ReferenceOracleReuseTests(unittest.TestCase):
    def test_o_crm_accepts_representative_cp_i02_transitions(self):
        package = package_record()
        self.assertEqual(
            set(),
            transition_violations("MATERIALIZE_IMPLEMENTATION_PACKAGE", None, package, expected_state()),
        )
        occurrence = occurrence_record()
        self.assertEqual(
            set(),
            transition_violations("SCHEDULE_STAGE_OCCURRENCE", None, occurrence, expected_state()),
        )
        terminal = deepcopy(occurrence)
        terminal["record_revision"] = 2
        terminal["state"] = "TERMINAL"
        terminal["terminal"] = terminal_facts()
        self.assertEqual(
            set(),
            transition_violations(
                "TERMINATE_STAGE_OCCURRENCE",
                occurrence,
                terminal,
                {"target_record_revision": 1},
            ),
        )
        self.assertEqual(set(), lineage_violations([occurrence, terminal]))

    def test_o_crm_idempotency_expectation_matches_cp_i02_contract(self):
        existing = {"req_same": "sha256:" + "1" * 64}
        self.assertEqual("REPLAY", idempotency_expectation(existing, "req_same", "sha256:" + "1" * 64))
        self.assertEqual("CONFLICT", idempotency_expectation(existing, "req_same", "sha256:" + "2" * 64))
        self.assertEqual("EXECUTE", idempotency_expectation(existing, "req_new", "sha256:" + "3" * 64))


if __name__ == "__main__":
    unittest.main()
