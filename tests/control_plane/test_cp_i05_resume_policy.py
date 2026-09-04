import unittest

from tools.aegis_control.execution_surface import classify_resume
from tools.aegis_control.recovery import (
    delivery_is_uncertain,
    dispatch_retry_delay_seconds,
    reconciliation_policy,
)


class CpI05ResumePolicyTests(unittest.TestCase):
    def test_exact_cursor(self):
        result = classify_resume(
            task_anchor_revision="A",
            resume_cursor={"revision": "C", "completed_through": ["P32.1"], "next_action": "P32.2"},
            observed_revision="C",
            is_ancestor=lambda a, b: a == b,
        )
        self.assertEqual("EXACT_CURSOR", result.state)
        self.assertEqual("C", result.accepted_revision)
        self.assertFalse(result.replay_completed_work)
        self.assertEqual(("P32.1",), result.completed_through)

    def test_descendant_cursor(self):
        result = classify_resume(
            task_anchor_revision="A",
            resume_cursor={"revision": "C", "completed_through": ["P32.1"], "next_action": "reconcile delta"},
            observed_revision="D",
            is_ancestor=lambda a, b: (a, b) in {("C", "D"), ("A", "D")},
        )
        self.assertEqual("DESCENDANT_CURSOR", result.state)
        self.assertEqual("D", result.accepted_revision)
        self.assertFalse(result.replay_completed_work)

    def test_anchor_descendant_without_cursor(self):
        result = classify_resume(
            task_anchor_revision="A",
            resume_cursor=None,
            observed_revision="D",
            is_ancestor=lambda a, b: (a, b) == ("A", "D"),
        )
        self.assertEqual("ANCHOR_DESCENDANT_WITHOUT_CURSOR", result.state)
        self.assertEqual("D", result.accepted_revision)
        self.assertFalse(result.replay_completed_work)

    def test_diverged_fails_closed(self):
        result = classify_resume(
            task_anchor_revision="A",
            resume_cursor={"revision": "C", "completed_through": [], "next_action": "continue"},
            observed_revision="X",
            is_ancestor=lambda a, b: False,
        )
        self.assertEqual("DIVERGED", result.state)
        self.assertEqual("BLOCKED_EXECUTION_DIVERGENCE", result.blocker)
        self.assertFalse(result.replay_completed_work)

    def test_dispatch_retry_schedule_and_uncertainty_boundary(self):
        self.assertEqual([1, 2, 4, 8, 16, 30, 60, 300], [dispatch_retry_delay_seconds(i) for i in range(1, 9)])
        self.assertFalse(delivery_is_uncertain(attempt_count=11, elapsed_seconds=1799))
        self.assertTrue(delivery_is_uncertain(attempt_count=12, elapsed_seconds=1))
        self.assertTrue(delivery_is_uncertain(attempt_count=1, elapsed_seconds=1800))

    def test_reconciliation_age_bands(self):
        cases = [
            (0, 30, False),
            (299, 30, False),
            (300, 120, False),
            (1799, 120, False),
            (1800, 300, False),
            (7199, 300, False),
            (7200, 900, True),
        ]
        for age, interval, alert in cases:
            with self.subTest(age=age):
                policy = reconciliation_policy(age)
                self.assertEqual(interval, policy.interval_seconds)
                self.assertEqual(alert, policy.operator_alert)
                self.assertFalse(policy.semantic_terminalization)


if __name__ == "__main__":
    unittest.main()
