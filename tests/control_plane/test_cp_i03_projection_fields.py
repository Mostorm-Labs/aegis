from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record, terminal_facts
from tools.aegis_control import ControlStore, MutationService, ProjectionEngine, canonical_digest


def _stored_ref(stored) -> str:
    return (
        f"{stored.record['kind']}:{stored.record['id']}"
        f"@{stored.record['record_revision']}#{stored.digest}"
    )


class CpI03ProjectionFieldTests(unittest.TestCase):
    def test_projection_covers_repair_lineage_open_escalation_and_lifecycle_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ControlStore(str(Path(tmp) / "projection-fields.db"))
            mutation = MutationService(store)
            lane = "lane_projection_fields"
            occurrence = occurrence_record("so_projection_repair_1", lane)
            occurrence["repair_context"] = {
                "finding_ref": {
                    "object_type": "FINDING",
                    "id": "finding_projection_1",
                    "ref": "finding:projection:1",
                    "identity": {"scheme": "sha256", "value": "sha256:" + "1" * 64},
                },
                "root_occurrence_ref": {
                    "object_type": "STAGE_OCCURRENCE",
                    "id": "so_projection_root",
                    "ref": "control:STAGE_OCCURRENCE:so_projection_root@2",
                    "identity": {"scheme": "sha256", "value": "sha256:" + "2" * 64},
                },
                "previous_attempt_occurrence_ref": None,
                "attempt_ordinal": 1,
                "repair_policy_digest": "sha256:" + "3" * 64,
            }
            mutation.apply(make_request(
                "SCHEDULE_STAGE_OCCURRENCE",
                "req_projection_repair_1",
                lane,
                {"occurrence": occurrence},
            ))
            current = store.read_latest("STAGE_OCCURRENCE", occurrence["id"])
            escalation = {
                "schema_version": "0.2",
                "kind": "ESCALATION",
                "id_scheme": "escalation-v0.2",
                "id": "esc_projection_1",
                "record_revision": 1,
                "recorded_at": occurrence["recorded_at"],
                "extensions": {},
                "control_lane_id": lane,
                "work_scope_ref": occurrence["work_scope_ref"],
                "raised_from_occurrence_ref": {
                    "object_type": "STAGE_OCCURRENCE",
                    "id": occurrence["id"],
                    "ref": f"control:STAGE_OCCURRENCE:{occurrence['id']}@1",
                    "identity": {"scheme": "sha256", "value": current.digest},
                },
                "trusted_basis_digest": canonical_digest(current.record["trusted_basis"]),
                "category": "AUTHORITY_CONFLICT",
                "owning_layer": "P21",
                "required_decision": {
                    "decision_kind": "AUTHORITY_RECONCILIATION",
                    "summary": "resolve projection fixture authority question",
                },
                "evidence_snapshot_refs": [],
            }
            mutation.apply(make_request(
                "RAISE_ESCALATION",
                "req_projection_escalation",
                lane,
                {
                    "occurrence_id": occurrence["id"],
                    "escalation": escalation,
                    "terminal": terminal_facts(
                        outcome="ESCALATED",
                        status="BLOCKED_AUTHORITY",
                        raised=[escalation["id"]],
                        earliest="P21",
                    ),
                    "recorded_at": None,
                },
                expected_state(
                    active_occurrence_ref=_stored_ref(current),
                    target_record_revision=current.record["record_revision"],
                    target_record_digest=current.digest,
                ),
            ))

            projection = ProjectionEngine(store).project_lane(lane)
            self.assertEqual((occurrence["id"],), projection.repair_lineage)
            self.assertEqual((escalation["id"],), projection.open_escalations)
            self.assertEqual("BLOCKED", projection.current_macro_phase)
            self.assertEqual("WAIT_FOR_RESOLUTION", projection.next_legal_action)
            self.assertEqual(1, projection.lifecycle_summary.occurrence_lineages)
            self.assertEqual(0, projection.lifecycle_summary.open_occurrences)
            self.assertEqual(1, projection.lifecycle_summary.terminal_occurrences)
            self.assertEqual(1, projection.lifecycle_summary.open_escalations)


if __name__ == "__main__":
    unittest.main()
