import unittest

from tools.aegis_control.operational import (
    AdmissionController,
    ProviderRateLimitController,
    classify_backpressure,
    manual_fallback_guard,
)


class CpI06OperationalRedTests(unittest.TestCase):
    def test_backpressure_watermarks_and_pause_are_operational_only(self):
        self.assertEqual("GREEN", classify_backpressure(0.69))
        self.assertEqual("YELLOW", classify_backpressure(0.70))
        self.assertEqual("ORANGE", classify_backpressure(0.85))
        self.assertEqual("RED", classify_backpressure(0.95))

        controller = AdmissionController()
        green = controller.evaluate(utilization=0.2, autonomous=True)
        self.assertTrue(green.admit)
        controller.pause()
        paused = controller.evaluate(utilization=0.2, autonomous=True)
        self.assertFalse(paused.admit)
        self.assertEqual("OPERATOR_PAUSED", paused.reason)
        controller.resume()
        resumed = controller.evaluate(utilization=0.2, autonomous=True)
        self.assertTrue(resumed.admit)
        self.assertTrue(resumed.requires_fresh_recompute)

    def test_orange_red_defer_new_autonomy_but_keep_committed_recovery(self):
        controller = AdmissionController()
        orange = controller.evaluate(utilization=0.90, autonomous=True)
        self.assertFalse(orange.admit)
        self.assertEqual("DEFER_NEW_AUTONOMOUS_ADMISSION", orange.reason)
        self.assertTrue(controller.evaluate(utilization=0.99, autonomous=False, recovery=True).admit)
        red = controller.evaluate(utilization=0.99, autonomous=True)
        self.assertFalse(red.admit)
        self.assertEqual("STOP_NEW_AUTONOMOUS_ADMISSION", red.reason)

    def test_rate_limit_threshold_halves_and_recovery_is_gradual(self):
        controller = ProviderRateLimitController(baseline_concurrency=100)
        below = controller.observe(window_seconds=300, request_count=100, rate_limited_count=5)
        self.assertEqual(100, below.concurrency)
        breached = controller.observe(
            window_seconds=300,
            request_count=100,
            rate_limited_count=6,
            retry_after_seconds=120,
        )
        self.assertEqual(50, breached.concurrency)
        self.assertEqual(120, breached.retry_after_seconds)
        stable_once = controller.observe(window_seconds=300, request_count=100, rate_limited_count=0)
        self.assertGreater(stable_once.concurrency, 50)
        self.assertLess(stable_once.concurrency, 100)
        stable_twice = controller.observe(window_seconds=300, request_count=100, rate_limited_count=0)
        self.assertLessEqual(stable_twice.concurrency, 100)
        self.assertGreaterEqual(stable_twice.concurrency, stable_once.concurrency)

    def test_rate_limit_state_never_requests_semantic_retry(self):
        controller = ProviderRateLimitController(baseline_concurrency=8)
        state = controller.observe(window_seconds=300, request_count=20, rate_limited_count=2)
        self.assertFalse(state.semantic_retry)
        self.assertTrue(state.reduce_polling_before_proof_or_review)

    def test_active_controlled_work_cannot_fall_back_to_duplicate_manual_execution(self):
        active = manual_fallback_guard(active_controlled_work=True)
        self.assertFalse(active.allowed)
        self.assertEqual("ACTIVE_CONTROLLED_WORK_REQUIRES_RECONCILIATION", active.reason)
        self.assertFalse(active.semantic_retry)
        self.assertFalse(active.replacement_occurrence)

        inactive = manual_fallback_guard(active_controlled_work=False)
        self.assertFalse(inactive.allowed)
        self.assertEqual("MANUAL_EXECUTION_REQUIRES_GOVERNED_POLICY", inactive.reason)
        self.assertFalse(inactive.semantic_retry)


if __name__ == "__main__":
    unittest.main()
