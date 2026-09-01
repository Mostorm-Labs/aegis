from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import (
    escalation_record,
    expected_state,
    make_request,
    occurrence_record,
    terminal_facts,
)
from tools.aegis_control.canonical import canonical_digest
from tools.aegis_control.external_ports import DeterministicExternalAdapter
from tools.aegis_control.mutation import (
    HumanDecisionSupportBinding,
    MutationRejected,
    MutationService,
)
from tools.aegis_control.store import ControlStore
from tools.aegis_control.trust import TrustFactRequest, TrustResolver


def decision_ref(decision_id="decision_cp_i06", *, scheme="sha256"):
    value = (
        canonical_digest({"decision": decision_id})
        if scheme == "sha256"
        else "draft-v1"
    )
    return {
        "object_type": "EXTERNAL_DECISION",
        "id": decision_id,
        "ref": f"decision://{decision_id}",
        "identity": {"scheme": scheme, "value": value},
    }


def internal_ref(stored):
    return f"STAGE_OCCURRENCE:{stored.record['id']}@{stored.record['record_revision']}#{stored.digest}"


class CpI06HumanDecisionRedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.decision = decision_ref()
        clock = lambda: datetime(2026, 9, 1, 9, 30, tzinfo=timezone.utc)
        self.adapter = DeterministicExternalAdapter(
            source_kind="HUMAN_DECISION",
            adapter_id="fixture-human",
            secret=b"cp-i06-human-secret",
            callback_available=True,
            query_correlation_available=True,
            clock=clock,
        )
        self.adapter.set_resource(
            "escalation/esc_cp_i06",
            version_scheme="native-immutable-id",
            version_value="decision-v1",
            resolved_refs=[self.decision],
            satisfies=True,
        )
        trust = TrustResolver({"HUMAN_DECISION": self.adapter})
        self.mutation = MutationService(
            self.store,
            trust_resolver=trust,
            human_decision_sources={
                canonical_digest(self.decision): HumanDecisionSupportBinding(
                    escalation_id="esc_cp_i06",
                    trust_fact_request=TrustFactRequest(
                        "HUMAN_DECISION", "escalation/esc_cp_i06"
                    ),
                )
            },
        )
        self.source_terminal = self._raise_escalation()

    def tearDown(self):
        self.tmp.cleanup()

    def _raise_escalation(self):
        source = occurrence_record("so_source", "lane_human")
        self.mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE", "req_source_schedule", "lane_human", {"occurrence": source}
        ))
        current = self.store.read_latest("STAGE_OCCURRENCE", "so_source")
        escalation = escalation_record("esc_cp_i06", "so_source", "lane_human")
        escalation["raised_from_occurrence_ref"] = {
            "object_type": "STAGE_OCCURRENCE",
            "id": "so_source",
            "ref": "control:STAGE_OCCURRENCE:so_source@1",
            "identity": {"scheme": "sha256", "value": current.digest},
        }
        terminal = terminal_facts(
            outcome="ESCALATED",
            status="BLOCKED_UNRESOLVED_DECISION",
            raised=["esc_cp_i06"],
        )
        self.mutation.apply(make_request(
            "RAISE_ESCALATION",
            "req_raise_escalation",
            "lane_human",
            {
                "occurrence_id": "so_source",
                "recorded_at": "2026-09-01T09:20:00Z",
                "escalation": escalation,
                "terminal": terminal,
            },
            expected_state(
                target_record_revision=1,
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        ))
        return self.store.read_latest("STAGE_OCCURRENCE", "so_source")

    def _seed_resolver(self, *, inputs):
        resolving = occurrence_record("so_resolve", "lane_human")
        resolving["stage_span"] = {"stages": ["P21"]}
        resolving["primary_owner"] = "aegis-governance"
        resolving["schedule_basis"] = {
            "reason_code": "NEXT_LEGAL_STAGE",
            "required_child_acceptance_bindings": [],
        }
        resolving["input_refs"] = deepcopy(inputs)
        self.mutation.apply(make_request(
            "SCHEDULE_STAGE_OCCURRENCE",
            "req_resolver_schedule",
            "lane_human",
            {"occurrence": resolving},
            expected_state(
                predecessor_occurrence_ref=internal_ref(self.source_terminal),
                work_scope_ref=resolving["work_scope_ref"],
            ),
        ))
        return self.store.read_latest("STAGE_OCCURRENCE", "so_resolve")

    def _resolution_request(self, current, decision):
        terminal = terminal_facts()
        terminal["resolved_escalation_ids"] = ["esc_cp_i06"]
        return make_request(
            "RECORD_ESCALATION_RESOLUTION",
            "req_resolve_escalation",
            "lane_human",
            {
                "occurrence_id": "so_resolve",
                "recorded_at": "2026-09-01T09:31:00Z",
                "escalation_id": "esc_cp_i06",
                "decision_ref": decision,
                "terminal": terminal,
            },
            expected_state(
                target_record_revision=current.record["record_revision"],
                target_record_digest=current.digest,
                work_scope_ref=current.record["work_scope_ref"],
            ),
        )

    def test_exact_durable_external_decision_resolves_without_mutating_escalation(self):
        current = self._seed_resolver(inputs=[self.decision])
        before_escalation = self.store.read_latest("ESCALATION", "esc_cp_i06")
        result = self.mutation.apply(self._resolution_request(current, self.decision))
        self.assertEqual("APPLIED", result["status"])
        after_escalation = self.store.read_latest("ESCALATION", "esc_cp_i06")
        self.assertEqual(before_escalation.digest, after_escalation.digest)
        resolved = self.store.read_latest("STAGE_OCCURRENCE", "so_resolve")
        self.assertEqual(["esc_cp_i06"], resolved.record["terminal"]["resolved_escalation_ids"])

    def test_chat_boolean_or_missing_acknowledgement_cannot_resolve(self):
        current = self._seed_resolver(inputs=[])
        for invalid in (None, "approved", True, {"approved": True}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(MutationRejected) as blocked:
                    self.mutation.apply(self._resolution_request(current, invalid))
                self.assertEqual("HUMAN_DECISION_EXACT_REF_REQUIRED", blocked.exception.code)

    def test_mutable_unpinned_decision_ref_fails_closed(self):
        mutable = decision_ref("decision_cp_i06", scheme="semantic-version")
        current = self._seed_resolver(inputs=[mutable])
        with self.assertRaises(MutationRejected) as blocked:
            self.mutation.apply(self._resolution_request(current, mutable))
        self.assertEqual("HUMAN_DECISION_EXACT_REF_REQUIRED", blocked.exception.code)

    def test_stale_decision_identity_after_provider_change_fails_closed(self):
        current = self._seed_resolver(inputs=[self.decision])
        replacement = decision_ref("decision_replacement")
        self.adapter.set_resource(
            "escalation/esc_cp_i06",
            version_scheme="native-immutable-id",
            version_value="decision-v2",
            resolved_refs=[replacement],
            satisfies=True,
        )
        with self.assertRaises(MutationRejected) as blocked:
            self.mutation.apply(self._resolution_request(current, self.decision))
        self.assertEqual("HUMAN_DECISION_IDENTITY_MISMATCH", blocked.exception.code)

    def test_wrong_or_unmaterialized_decision_ref_fails_closed(self):
        wrong = decision_ref("other")
        current = self._seed_resolver(inputs=[wrong])
        with self.assertRaises(MutationRejected) as blocked:
            self.mutation.apply(self._resolution_request(current, wrong))
        self.assertEqual("HUMAN_DECISION_UNRESOLVABLE", blocked.exception.code)

    def test_conflicting_second_resolution_is_rejected(self):
        current = self._seed_resolver(inputs=[self.decision])
        request = self._resolution_request(current, self.decision)
        self.mutation.apply(request)
        replay = self.mutation.apply(request)
        self.assertEqual("APPLIED", replay["status"])
        other = decision_ref("other")
        terminal = self.store.read_latest("STAGE_OCCURRENCE", "so_resolve")
        with self.assertRaises(MutationRejected) as conflict:
            self.mutation.apply(make_request(
                "RECORD_ESCALATION_RESOLUTION",
                "req_resolve_conflict",
                "lane_human",
                {
                    "occurrence_id": "so_resolve",
                    "recorded_at": "2026-09-01T09:32:00Z",
                    "escalation_id": "esc_cp_i06",
                    "decision_ref": other,
                    "terminal": terminal_facts(),
                },
                expected_state(
                    target_record_revision=terminal.record["record_revision"],
                    target_record_digest=terminal.digest,
                    work_scope_ref=terminal.record["work_scope_ref"],
                ),
            ))
        self.assertIn(conflict.exception.code, {"OCCURRENCE_ALREADY_TERMINAL", "ESCALATION_RESOLUTION_CONFLICT"})


if __name__ == "__main__":
    unittest.main()
