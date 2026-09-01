from __future__ import annotations

import unittest


DAY = 24 * 60 * 60


class CpI08RetentionAlertRedTests(unittest.TestCase):
    def test_canonical_history_is_never_auto_delete_eligible(self):
        from tools.aegis_control.retention import evaluate_retention
        for record_class in ("STAGE_OCCURRENCE", "VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE", "ESCALATION", "SEMANTIC_IDEMPOTENCY"):
            decision = evaluate_retention(record_class, age_seconds=10 * 365 * DAY)
            self.assertEqual("NO_AUTO_DELETE", decision.action)

    def test_operational_retention_exact_boundaries(self):
        from tools.aegis_control.retention import evaluate_retention
        self.assertEqual("KEEP", evaluate_retention("HIGH_CARDINALITY_TRACE", age_seconds=14 * DAY - 1).action)
        self.assertEqual("EXPIRE_OPERATIONAL", evaluate_retention("HIGH_CARDINALITY_TRACE", age_seconds=14 * DAY).action)
        self.assertEqual("KEEP", evaluate_retention("COMPLETED_DELIVERY_METADATA", age_seconds=30 * DAY - 1).action)
        self.assertEqual("COMPACT_OPERATIONAL", evaluate_retention("COMPLETED_DELIVERY_METADATA", age_seconds=30 * DAY).action)

    def test_alert_thresholds_are_exact_and_operational_only(self):
        from tools.aegis_control.observability import evaluate_alerts
        self.assertEqual([], evaluate_alerts({"oldest_ready_outbox_seconds": 300}))
        alerts = evaluate_alerts({"oldest_ready_outbox_seconds": 301})
        self.assertEqual(["OUTBOX_AGE_URGENT"], [a.rule_id for a in alerts])
        self.assertTrue(all(a.semantic_truth is False for a in alerts))

    def test_store_unavailable_critical_requires_production_traffic_and_more_than_two_minutes(self):
        from tools.aegis_control.observability import evaluate_alerts
        self.assertEqual([], evaluate_alerts({"store_unavailable_seconds": 120, "production_traffic": True}))
        self.assertEqual([], evaluate_alerts({"store_unavailable_seconds": 121, "production_traffic": False}))
        alerts = evaluate_alerts({"store_unavailable_seconds": 121, "production_traffic": True})
        self.assertIn("STORE_UNAVAILABLE_CRITICAL", [a.rule_id for a in alerts])


if __name__ == "__main__": unittest.main()
