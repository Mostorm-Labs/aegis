from __future__ import annotations

from copy import deepcopy
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tools.aegis_control.canonical import canonical_digest
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.store import ControlStore


def exact_ref(object_type: str, object_id: str, scheme: str = "sha256") -> dict:
    value = canonical_digest({"type": object_type, "id": object_id}) if scheme == "sha256" else "1.0.0"
    return {
        "object_type": object_type,
        "id": object_id,
        "ref": f"fixture://{object_type.lower()}/{object_id}",
        "identity": {"scheme": scheme, "value": value},
    }


def stored_occurrence_ref(stored) -> dict:
    return {
        "object_type": "STAGE_OCCURRENCE",
        "id": stored.record["id"],
        "ref": f"control:STAGE_OCCURRENCE:{stored.record['id']}@{stored.record['record_revision']}",
        "identity": {"scheme": "sha256", "value": stored.digest},
    }


def internal_ref(stored) -> str:
    return f"STAGE_OCCURRENCE:{stored.record['id']}@{stored.record['record_revision']}#{stored.digest}"


def repair_policy(max_attempts: int = 2) -> dict:
    base = {
        "gate_policy_ref": exact_ref("CONTRACT", "gate-policy"),
        "control_autonomy": "REVIEW_GUARDED",
        "repair_policy": {
            "allowed_classes": ["IMPLEMENTATION_DEFECT"],
            "max_attempts": max_attempts,
            "require_reverification": True,
            "require_fresh_independent_review": True,
            "escalation_conditions": ["REPAIR_BUDGET_EXHAUSTED"],
        },
    }
    return {**base, "policy_digest": canonical_digest(base)}


class CpI06RepairRedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.finding = exact_ref("FINDING", "finding_cp_i06")
        self.mutation = MutationService(
            self.store,
            finding_classifications={canonical_digest(self.finding): "IMPLEMENTATION_DEFECT"},
        )
        self.root_terminal = self._seed_root_terminal()

    def tearDown(self):
        self.tmp.cleanup()

    def _seed_root_terminal(self):
        root = occurrence_record("so_root", "lane_cp_i06")
        self.mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE", "req_root_schedule", "lane_cp_i06", {"occurrence": root}
        ))
        current = self.store.read_latest("STAGE_OCCURRENCE", "so_root")
        result = self.mutation.apply(make_request(
            "TERMINATE_STAGE_OCCURRENCE",
            "req_root_terminal",
            "lane_cp_i06",
            {
                "occurrence_id": "so_root",
                "recorded_at": "2026-09-01T09:00:00Z",
                "terminal": terminal_facts(),
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        ))
        self.assertEqual("APPLIED", result["status"])
        return self.store.read_latest("STAGE_OCCURRENCE", "so_root")

    def _repair_record(self, occurrence_id: str, ordinal: int, previous=None, *, max_attempts: int = 2):
        record = occurrence_record(occurrence_id, "lane_cp_i06")
        policy = repair_policy(max_attempts)
        record["policy_binding"] = policy
        record["schedule_basis"] = {
            "reason_code": "REPAIR",
            "required_child_acceptance_bindings": [],
        }
        record["repair_context"] = {
            "finding_ref": deepcopy(self.finding),
            "root_occurrence_ref": stored_occurrence_ref(self.root_terminal),
            "previous_attempt_occurrence_ref": stored_occurrence_ref(previous) if previous else None,
            "attempt_ordinal": ordinal,
            "repair_policy_digest": policy["policy_digest"],
        }
        return record

    def _schedule_repair(self, occurrence_id: str, ordinal: int, predecessor, previous=None, *, max_attempts=2):
        record = self._repair_record(occurrence_id, ordinal, previous, max_attempts=max_attempts)
        return self.mutation.apply(make_request(
            "SCHEDULE_REPAIR_OCCURRENCE",
            f"req_{occurrence_id}",
            "lane_cp_i06",
            {"occurrence": record, "repair_class": "IMPLEMENTATION_DEFECT"},
            expected_state(
                predecessor_occurrence_ref=internal_ref(predecessor),
                work_scope_ref=record["work_scope_ref"],
            ),
        ))

    def _terminalize(self, occurrence_id: str):
        current = self.store.read_latest("STAGE_OCCURRENCE", occurrence_id)
        self.mutation.apply(make_request(
            "TERMINATE_STAGE_OCCURRENCE",
            f"req_terminal_{occurrence_id}",
            "lane_cp_i06",
            {
                "occurrence_id": occurrence_id,
                "recorded_at": "2026-09-01T09:05:00Z",
                "terminal": terminal_facts(),
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        ))
        return self.store.read_latest("STAGE_OCCURRENCE", occurrence_id)

    def test_first_and_second_repair_attempts_are_new_contiguous_occurrences(self):
        first = self._schedule_repair("so_repair_1", 1, self.root_terminal)
        self.assertEqual("APPLIED", first["status"])
        first_current = self.store.read_latest("STAGE_OCCURRENCE", "so_repair_1")
        self.assertEqual(1, first_current.record["repair_context"]["attempt_ordinal"])
        self.assertEqual([], first["outbox_ids"])
        first_terminal = self._terminalize("so_repair_1")

        second = self._schedule_repair("so_repair_2", 2, first_terminal, first_terminal)
        self.assertEqual("APPLIED", second["status"])
        second_current = self.store.read_latest("STAGE_OCCURRENCE", "so_repair_2")
        self.assertEqual(2, second_current.record["repair_context"]["attempt_ordinal"])
        self.assertNotEqual("so_repair_1", second_current.record["id"])

    def test_repair_ordinal_gap_and_budget_exhaustion_fail_with_zero_residue(self):
        before = self.store.snapshot_counts()
        with self.assertRaises(MutationRejected) as gap:
            self._schedule_repair("so_gap", 2, self.root_terminal)
        self.assertEqual("REPAIR_ATTEMPT_ORDINAL_GAP", gap.exception.code)
        self.assertEqual(before, self.store.snapshot_counts())

        first = self._schedule_repair("so_budget_1", 1, self.root_terminal, max_attempts=1)
        self.assertEqual("APPLIED", first["status"])
        first_terminal = self._terminalize("so_budget_1")
        before_exhausted = self.store.snapshot_counts()
        with self.assertRaises(MutationRejected) as exhausted:
            self._schedule_repair("so_budget_2", 2, first_terminal, first_terminal, max_attempts=1)
        self.assertEqual("REPAIR_BUDGET_EXHAUSTED", exhausted.exception.code)
        self.assertEqual(before_exhausted, self.store.snapshot_counts())

    def test_wrong_finding_or_caller_reclassification_fails_closed(self):
        record = self._repair_record("so_wrong_finding", 1)
        record["repair_context"]["finding_ref"] = exact_ref("FINDING", "other")
        with self.assertRaises(MutationRejected) as wrong:
            self.mutation.apply(make_request(
                "SCHEDULE_REPAIR_OCCURRENCE", "req_wrong_finding", "lane_cp_i06",
                {"occurrence": record, "repair_class": "IMPLEMENTATION_DEFECT"},
                expected_state(
                    predecessor_occurrence_ref=internal_ref(self.root_terminal),
                    work_scope_ref=record["work_scope_ref"],
                ),
            ))
        self.assertEqual("REPAIR_FINDING_CLASSIFICATION_MISSING", wrong.exception.code)

        record = self._repair_record("so_wrong_class", 1)
        with self.assertRaises(MutationRejected) as reclassified:
            self.mutation.apply(make_request(
                "SCHEDULE_REPAIR_OCCURRENCE", "req_wrong_class", "lane_cp_i06",
                {"occurrence": record, "repair_class": "AUTHORITY_CHANGE"},
                expected_state(
                    predecessor_occurrence_ref=internal_ref(self.root_terminal),
                    work_scope_ref=record["work_scope_ref"],
                ),
            ))
        self.assertEqual("REPAIR_FINDING_CLASSIFICATION_CONFLICT", reclassified.exception.code)

    def test_required_reverification_cannot_be_skipped_before_rereview(self):
        self._schedule_repair("so_skip_repair", 1, self.root_terminal)
        repair_terminal = self._terminalize("so_skip_repair")
        result_ref = exact_ref("RESULT", "repair-result-skip")
        evidence_ref = exact_ref("EVIDENCE", "unverified-local-evidence")
        rereview = occurrence_record("so_skip_rereview", "lane_cp_i06")
        rereview["stage_span"] = {"stages": ["P34"]}
        rereview["primary_owner"] = "aegis-gate-review"
        rereview["schedule_basis"] = {"reason_code": "REREVIEW", "required_child_acceptance_bindings": []}
        rereview["input_refs"] = [result_ref, evidence_ref]
        before = self.store.snapshot_counts()
        with self.assertRaises(MutationRejected) as blocked:
            self.mutation.apply(make_request(
                "SCHEDULE_REREVIEW_OCCURRENCE", "req_skip_rereview", "lane_cp_i06",
                {"occurrence": rereview},
                expected_state(
                    predecessor_occurrence_ref=internal_ref(repair_terminal),
                    work_scope_ref=rereview["work_scope_ref"],
                ),
            ))
        self.assertEqual("REQUIRED_REVERIFICATION_NOT_COMPLETED", blocked.exception.code)
        self.assertEqual(before, self.store.snapshot_counts())

    def test_reverify_then_rereview_are_separate_occurrences_without_gate_truth(self):
        self._schedule_repair("so_repair", 1, self.root_terminal)
        repair_terminal = self._terminalize("so_repair")
        result_ref = exact_ref("RESULT", "repair-result")
        reverify = occurrence_record("so_reverify", "lane_cp_i06")
        reverify["stage_span"] = {"stages": ["P20"]}
        reverify["primary_owner"] = "aegis-verification"
        reverify["schedule_basis"] = {"reason_code": "REVERIFY", "required_child_acceptance_bindings": []}
        reverify["input_refs"] = [result_ref]
        result = self.mutation.apply(make_request(
            "SCHEDULE_REVERIFICATION_OCCURRENCE", "req_reverify", "lane_cp_i06",
            {"occurrence": reverify},
            expected_state(
                predecessor_occurrence_ref=internal_ref(repair_terminal),
                work_scope_ref=reverify["work_scope_ref"],
            ),
        ))
        self.assertEqual("APPLIED", result["status"])
        self.assertEqual([], result["outbox_ids"])
        reverify_terminal = self._terminalize("so_reverify")

        evidence_ref = exact_ref("EVIDENCE", "fresh-reverify-evidence")
        rereview = occurrence_record("so_rereview", "lane_cp_i06")
        rereview["stage_span"] = {"stages": ["P34"]}
        rereview["primary_owner"] = "aegis-gate-review"
        rereview["schedule_basis"] = {"reason_code": "REREVIEW", "required_child_acceptance_bindings": []}
        rereview["input_refs"] = [result_ref, evidence_ref]
        review_result = self.mutation.apply(make_request(
            "SCHEDULE_REREVIEW_OCCURRENCE", "req_rereview", "lane_cp_i06",
            {"occurrence": rereview},
            expected_state(
                predecessor_occurrence_ref=internal_ref(reverify_terminal),
                work_scope_ref=rereview["work_scope_ref"],
            ),
        ))
        self.assertEqual("APPLIED", review_result["status"])
        self.assertEqual([], review_result["outbox_ids"])
        stored = self.store.read_latest("STAGE_OCCURRENCE", "so_rereview")
        self.assertEqual("aegis-gate-review", stored.record["primary_owner"])
        self.assertNotIn("gate_decision", stored.record)


if __name__ == "__main__":
    unittest.main()
