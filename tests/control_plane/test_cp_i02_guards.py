import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import (
    escalation_record,
    expected_state,
    make_request,
    occurrence_record,
    package_record,
    terminal_facts,
)
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.store import ControlStore


class MutationGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "control.db")
        self.store = ControlStore(self.db)
        self.mutation = MutationService(self.store)

    def tearDown(self):
        self.tmp.cleanup()

    def _schedule(self):
        request = make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_guard_schedule",
            "lane_01",
            {"occurrence": occurrence_record()},
        )
        self.mutation.apply(request)
        return self.store.read_latest("STAGE_OCCURRENCE", "so_01")

    def test_terminal_facts_must_match_exact_p12_shape(self):
        current = self._schedule()
        malformed_terminal = {
            "outcome_category": "COMPLETED",
            "status": "READY",
            "produced_refs": [],
            "raised_escalation_ids": [],
        }
        request = make_request(
            "TERMINATE_STAGE_OCCURRENCE",
            "req_guard_terminal",
            "lane_01",
            {
                "occurrence_id": "so_01",
                "recorded_at": "2026-08-31T06:31:00Z",
                "terminal": malformed_terminal,
            },
            expected_state(
                target_record_revision=1,
                target_record_digest=current.digest,
            ),
        )
        before = self.store.snapshot_counts()
        with self.assertRaisesRegex(MutationRejected, "INVALID_TERMINAL_FACTS"):
            self.mutation.apply(request)
        self.assertEqual(before, self.store.snapshot_counts())
        self.assertEqual("OPEN", self.store.read_latest("STAGE_OCCURRENCE", "so_01").record["state"])

    def test_escalation_must_bind_exact_open_occurrence(self):
        current = self._schedule()
        escalation = escalation_record()
        escalation["raised_from_occurrence_ref"] = {
            "object_type": "STAGE_OCCURRENCE",
            "id": "so_other",
            "ref": "control:STAGE_OCCURRENCE:so_other@1",
            "identity": {"scheme": "sha256", "value": "sha256:" + "1" * 64},
        }
        terminal = {
            "outcome_category": "ESCALATED",
            "status": "BLOCKED_UNRESOLVED_DECISION",
            "produced_refs": [],
            "finding_refs": [],
            "raised_escalation_ids": ["esc_01"],
            "resolved_escalation_ids": [],
            "earliest_untrusted_layer": "P21",
            "navigation_result": None,
        }
        request = make_request(
            "RAISE_ESCALATION",
            "req_guard_escalation",
            "lane_01",
            {
                "occurrence_id": "so_01",
                "recorded_at": "2026-08-31T06:32:00Z",
                "escalation": escalation,
                "terminal": terminal,
            },
            expected_state(
                target_record_revision=1,
                target_record_digest=current.digest,
            ),
        )
        before = self.store.snapshot_counts()
        with self.assertRaisesRegex(MutationRejected, "ESCALATION_SOURCE_MISMATCH"):
            self.mutation.apply(request)
        self.assertEqual(before, self.store.snapshot_counts())
        self.assertIsNone(self.store.read_latest("ESCALATION", "esc_01"))

    def test_package_revision_cannot_cross_request_lane(self):
        first = make_request(
            "MATERIALIZE_IMPLEMENTATION_PACKAGE",
            "req_guard_pkg_1",
            "lane_pkg",
            {"package": package_record()},
        )
        self.mutation.apply(first)
        current = self.store.read_latest("VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "pkg_01")
        revised = package_record(revision=2, lane_id="lane_other", scope_name="cross-lane")
        request = make_request(
            "REVISE_IMPLEMENTATION_PACKAGE",
            "req_guard_pkg_2",
            "lane_pkg",
            {"package": revised},
            expected_state(
                target_record_revision=1,
                target_record_digest=current.digest,
            ),
        )
        before = self.store.snapshot_counts()
        with self.assertRaisesRegex(MutationRejected, "PACKAGE_LANE_MISMATCH"):
            self.mutation.apply(request)
        self.assertEqual(before, self.store.snapshot_counts())
        self.assertEqual(1, len(self.store.read_revisions("VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "pkg_01")))


if __name__ == "__main__":
    unittest.main()

class CriticalCasAndIdempotencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "critical.db")
        self.store = ControlStore(self.db)
        self.mutation = MutationService(self.store)

    def tearDown(self):
        self.tmp.cleanup()

    def test_schedule_rejects_stale_predecessor_guard_with_zero_mutation(self):
        request = make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_stale_predecessor",
            "lane_critical",
            {"occurrence": occurrence_record("so_critical", "lane_critical")},
            expected_state(predecessor_occurrence_ref="STAGE_OCCURRENCE:old@2#sha256:" + "1" * 64),
        )
        before = self.store.snapshot_counts()
        with self.assertRaisesRegex(MutationRejected, "CONTROL_LANE_SCHEDULE_CONFLICT"):
            self.mutation.apply(request)
        self.assertEqual(before, self.store.snapshot_counts())

    def test_existing_request_id_conflict_precedes_operation_subset_rejection(self):
        original = make_request(
            "MATERIALIZE_IMPLEMENTATION_PACKAGE",
            "req_idempotency_priority",
            "lane_pkg",
            {"package": package_record(package_id="pkg_priority")},
        )
        self.mutation.apply(original)
        before = self.store.snapshot_counts()
        conflicting = make_request(
            "RECORD_EXECUTION_PROGRESS",
            "req_idempotency_priority",
            "lane_pkg",
            {"checkpoint": "changed semantic request"},
        )
        with self.assertRaisesRegex(MutationRejected, "OPERATION_IDEMPOTENCY_CONFLICT"):
            self.mutation.apply(conflicting)
        self.assertEqual(before, self.store.snapshot_counts())

class CompanionAndLaneGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "companion.db")
        self.store = ControlStore(self.db)
        self.mutation = MutationService(self.store)
        self.mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE", "req_companion_schedule", "lane_01",
            {"occurrence": occurrence_record()},
        ))
        self.current = self.store.read_latest("STAGE_OCCURRENCE", "so_01")

    def tearDown(self):
        self.tmp.cleanup()

    def test_terminate_request_lane_must_match_occurrence_lane(self):
        request = make_request(
            "TERMINATE_STAGE_OCCURRENCE", "req_wrong_lane_terminal", "lane_other",
            {"occurrence_id": "so_01", "recorded_at": "2026-08-31T06:50:00Z", "terminal": terminal_facts()},
            expected_state(target_record_revision=1, target_record_digest=self.current.digest),
        )
        before = self.store.snapshot_counts()
        with self.assertRaisesRegex(MutationRejected, "OCCURRENCE_LANE_MISMATCH"):
            self.mutation.apply(request)
        self.assertEqual(before, self.store.snapshot_counts())

    def test_plain_terminal_cannot_create_orphan_escalation_reference(self):
        terminal = terminal_facts()
        terminal["raised_escalation_ids"] = ["esc_ghost"]
        request = make_request(
            "TERMINATE_STAGE_OCCURRENCE", "req_orphan_escalation", "lane_01",
            {"occurrence_id": "so_01", "recorded_at": "2026-08-31T06:51:00Z", "terminal": terminal},
            expected_state(target_record_revision=1, target_record_digest=self.current.digest),
        )
        before = self.store.snapshot_counts()
        with self.assertRaisesRegex(MutationRejected, "INVALID_TERMINAL_FACTS"):
            self.mutation.apply(request)
        self.assertEqual(before, self.store.snapshot_counts())

    def test_raise_escalation_requires_matching_trusted_basis_digest(self):
        escalation = escalation_record()
        escalation["trusted_basis_digest"] = "sha256:" + "0" * 64
        request = make_request(
            "RAISE_ESCALATION", "req_wrong_basis", "lane_01",
            {
                "occurrence_id": "so_01", "recorded_at": "2026-08-31T06:52:00Z",
                "escalation": escalation,
                "terminal": terminal_facts(
                    "ESCALATED", "BLOCKED_UNRESOLVED_DECISION", raised=["esc_01"], earliest="P21"
                ),
            },
            expected_state(target_record_revision=1, target_record_digest=self.current.digest),
        )
        before = self.store.snapshot_counts()
        with self.assertRaisesRegex(MutationRejected, "ESCALATION_TRUSTED_BASIS_MISMATCH"):
            self.mutation.apply(request)
        self.assertEqual(before, self.store.snapshot_counts())

    def test_raise_escalation_rejects_unmaterialized_extra_companion(self):
        request = make_request(
            "RAISE_ESCALATION", "req_extra_companion", "lane_01",
            {
                "occurrence_id": "so_01", "recorded_at": "2026-08-31T06:53:00Z",
                "escalation": escalation_record(),
                "terminal": terminal_facts(
                    "ESCALATED", "BLOCKED_UNRESOLVED_DECISION",
                    raised=["esc_01", "esc_ghost"], earliest="P21",
                ),
            },
            expected_state(target_record_revision=1, target_record_digest=self.current.digest),
        )
        before = self.store.snapshot_counts()
        with self.assertRaisesRegex(MutationRejected, "ESCALATION_TERMINAL_BINDING_MISSING"):
            self.mutation.apply(request)
        self.assertEqual(before, self.store.snapshot_counts())
