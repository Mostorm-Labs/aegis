from __future__ import annotations

import tempfile
import unittest

from tests.control_plane.cp_i02_fixtures import expected_state, make_request, occurrence_record
from tests.control_plane.reference_model import detect_semantic_violations
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.store import ControlStore


DAY = 24 * 60 * 60


class CpI08GoldenDirectTests(unittest.TestCase):
    def test_g22_explicit_test_policy_fixture_can_model_cross_owner_capability_without_current_authority(self):
        violations = detect_semantic_violations({"cross_primary_auto_dispatch": True, "rollout_authorized": True})
        self.assertNotIn("UNAUTHORIZED_CROSS_PRIMARY_DISPATCH", violations)
        denied = detect_semantic_violations({"cross_primary_auto_dispatch": True, "rollout_authorized": False})
        self.assertIn("UNAUTHORIZED_CROSS_PRIMARY_DISPATCH", denied)

    def test_g27_store_unavailable_before_transaction_creates_no_semantic_residue(self):
        with tempfile.TemporaryDirectory() as td:
            store = ControlStore(f"{td}/control.db")
            before = dict(store.snapshot_counts())
            def unavailable():
                raise RuntimeError("store unavailable")
            mutation = MutationService(store, before_transaction=unavailable)
            request = make_request(
                "SCHEDULE_STAGE_OCCURRENCE",
                "req_g27_store_down",
                "lane_g27",
                {"occurrence": occurrence_record("so_g27", "lane_g27")},
                expected_state(),
            )
            with self.assertRaises(RuntimeError):
                mutation.apply(request)
            self.assertEqual(before, dict(store.snapshot_counts()))
            self.assertIsNone(store.read_latest("STAGE_OCCURRENCE", "so_g27"))

    def test_g44_virtual_time_retention_and_alert_boundary_sweep(self):
        from tools.aegis_control.observability import evaluate_alerts
        from tools.aegis_control.retention import evaluate_retention

        self.assertEqual("KEEP", evaluate_retention("HIGH_CARDINALITY_TRACE", age_seconds=14 * DAY - 1).action)
        self.assertEqual("EXPIRE_OPERATIONAL", evaluate_retention("HIGH_CARDINALITY_TRACE", age_seconds=14 * DAY).action)
        self.assertEqual("NO_AUTO_DELETE", evaluate_retention("STAGE_OCCURRENCE", age_seconds=1000 * DAY).action)
        self.assertEqual([], evaluate_alerts({"oldest_ready_outbox_seconds": 300, "reconciliation_lag_seconds": 900}))
        urgent = evaluate_alerts({"oldest_ready_outbox_seconds": 301, "reconciliation_lag_seconds": 901})
        self.assertEqual({"OUTBOX_AGE_URGENT", "RECONCILIATION_LAG_URGENT"}, {a.rule_id for a in urgent})
        self.assertTrue(all(a.semantic_truth is False for a in urgent))


if __name__ == "__main__": unittest.main()
