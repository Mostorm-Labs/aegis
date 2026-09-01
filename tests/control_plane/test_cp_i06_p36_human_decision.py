from __future__ import annotations

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
from tests.control_plane.test_cp_i06_human_decision import decision_ref, internal_ref
from tools.aegis_control.canonical import canonical_digest
from tools.aegis_control.external_ports import DeterministicExternalAdapter
from tools.aegis_control.mutation import (
    HumanDecisionSupportBinding,
    MutationRejected,
    MutationService,
)
from tools.aegis_control.store import ControlStore
from tools.aegis_control.trust import TrustFactRequest, TrustResolver


class CpI06P36HumanDecisionTests(unittest.TestCase):
    def test_valid_fresh_materialized_wrong_resource_decision_is_rejected_with_zero_residue(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ControlStore(str(Path(tmp) / "control.db"))
            wrong_decision = decision_ref("decision_other_escalation")
            clock = lambda: datetime(2026, 9, 1, 9, 30, tzinfo=timezone.utc)
            adapter = DeterministicExternalAdapter(
                source_kind="HUMAN_DECISION",
                adapter_id="fixture-human",
                secret=b"cp-i06-human-secret",
                callback_available=True,
                query_correlation_available=True,
                clock=clock,
            )
            adapter.set_resource(
                "opaque-human-resource-7",
                version_scheme="native-immutable-id",
                version_value="decision-other-v1",
                resolved_refs=[wrong_decision],
                satisfies=True,
            )
            mutation = MutationService(
                store,
                trust_resolver=TrustResolver({"HUMAN_DECISION": adapter}),
                human_decision_sources={
                    canonical_digest(wrong_decision): HumanDecisionSupportBinding(
                        escalation_id="esc_other",
                        trust_fact_request=TrustFactRequest(
                            "HUMAN_DECISION", "opaque-human-resource-7"
                        ),
                    )
                },
            )

            source = occurrence_record("so_source_p36", "lane_human_p36")
            mutation.apply(make_request(
                "SCHEDULE_STAGE_OCCURRENCE",
                "req_source_schedule_p36",
                "lane_human_p36",
                {"occurrence": source},
            ))
            current = store.read_latest("STAGE_OCCURRENCE", "so_source_p36")
            escalation = escalation_record("esc_cp_i06", "so_source_p36", "lane_human_p36")
            escalation["raised_from_occurrence_ref"] = {
                "object_type": "STAGE_OCCURRENCE",
                "id": "so_source_p36",
                "ref": "control:STAGE_OCCURRENCE:so_source_p36@1",
                "identity": {"scheme": "sha256", "value": current.digest},
            }
            mutation.apply(make_request(
                "RAISE_ESCALATION",
                "req_raise_escalation_p36",
                "lane_human_p36",
                {
                    "occurrence_id": "so_source_p36",
                    "recorded_at": "2026-09-01T09:20:00Z",
                    "escalation": escalation,
                    "terminal": terminal_facts(
                        outcome="ESCALATED",
                        status="BLOCKED_UNRESOLVED_DECISION",
                        raised=["esc_cp_i06"],
                    ),
                },
                expected_state(
                    target_record_revision=1,
                    target_record_digest=current.digest,
                    work_scope_ref=current.record["work_scope_ref"],
                ),
            ))
            source_terminal = store.read_latest("STAGE_OCCURRENCE", "so_source_p36")

            resolving = occurrence_record("so_resolve_p36", "lane_human_p36")
            resolving["stage_span"] = {"stages": ["P21"]}
            resolving["primary_owner"] = "aegis-governance"
            resolving["schedule_basis"] = {
                "reason_code": "NEXT_LEGAL_STAGE",
                "required_child_acceptance_bindings": [],
            }
            resolving["input_refs"] = [wrong_decision]
            mutation.apply(make_request(
                "SCHEDULE_STAGE_OCCURRENCE",
                "req_resolver_schedule_p36",
                "lane_human_p36",
                {"occurrence": resolving},
                expected_state(
                    predecessor_occurrence_ref=internal_ref(source_terminal),
                    work_scope_ref=resolving["work_scope_ref"],
                ),
            ))
            resolver_current = store.read_latest("STAGE_OCCURRENCE", "so_resolve_p36")
            terminal = terminal_facts()
            terminal["resolved_escalation_ids"] = ["esc_cp_i06"]
            request = make_request(
                "RECORD_ESCALATION_RESOLUTION",
                "req_resolve_wrong_resource_p36",
                "lane_human_p36",
                {
                    "occurrence_id": "so_resolve_p36",
                    "recorded_at": "2026-09-01T09:31:00Z",
                    "escalation_id": "esc_cp_i06",
                    "decision_ref": wrong_decision,
                    "terminal": terminal,
                },
                expected_state(
                    target_record_revision=resolver_current.record["record_revision"],
                    target_record_digest=resolver_current.digest,
                    work_scope_ref=resolver_current.record["work_scope_ref"],
                ),
            )
            before = dict(store.snapshot_counts())
            before_escalation = store.read_latest("ESCALATION", "esc_cp_i06")

            with self.assertRaises(MutationRejected) as blocked:
                mutation.apply(request)

            self.assertEqual("HUMAN_DECISION_WRONG_RESOURCE", blocked.exception.code)
            self.assertEqual(before, store.snapshot_counts())
            after_escalation = store.read_latest("ESCALATION", "esc_cp_i06")
            self.assertEqual(before_escalation.digest, after_escalation.digest)
            self.assertEqual("OPEN", store.read_latest("STAGE_OCCURRENCE", "so_resolve_p36").record["state"])


if __name__ == "__main__":
    unittest.main()
