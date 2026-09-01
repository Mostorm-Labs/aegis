from __future__ import annotations

import unittest


class CpI08ObservabilityRedTests(unittest.TestCase):
    def test_raw_events_recompute_exact_exported_aggregates(self):
        from tools.aegis_control.observability import ObservabilityBuffer, RawMetricEvent, recompute_aggregates
        buf = ObservabilityBuffer()
        buf.record(RawMetricEvent(1, "2026-09-01T00:00:00Z", "control_api_latency", "corr-1", 10.0, "ms", {"route": "/v1/operations"}))
        buf.record(RawMetricEvent(2, "2026-09-01T00:00:01Z", "control_api_latency", "corr-2", 20.0, "ms", {"route": "/v1/operations"}))
        self.assertEqual(recompute_aggregates(buf.raw_events()), buf.export_aggregates())

    def test_required_metric_families_are_machine_enumerable(self):
        from tools.aegis_control.observability import REQUIRED_METRIC_FAMILIES
        required = {
            "control_api_latency", "canonical_transaction_latency", "projection_latency",
            "outbox_depth", "outbox_oldest_age", "open_occurrence_age", "reconciliation_latency",
            "provider_call_count", "provider_rate_limit", "conflict_count",
            "zero_tolerance_invariant", "orchestration_cost_component",
        }
        self.assertEqual(required, set(REQUIRED_METRIC_FAMILIES))

    def test_raw_event_requires_correlation_id(self):
        from tools.aegis_control.observability import ObservabilityError, ObservabilityBuffer, RawMetricEvent
        with self.assertRaises(ObservabilityError):
            ObservabilityBuffer().record(RawMetricEvent(1, "2026-09-01T00:00:00Z", "outbox_depth", "", 1.0, "count", {}))


if __name__ == "__main__": unittest.main()
