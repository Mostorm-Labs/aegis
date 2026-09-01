from __future__ import annotations

import unittest


class CpI08AvailabilityRedTests(unittest.TestCase):
    def test_seeded_availability_classifications_and_no_false_local_exclusion(self):
        from tools.aegis_control.availability import AvailabilityObservation, classify_observation
        cases = [
            (AvailabilityObservation("local-api", "CONTROL_API_AVAILABILITY", "FAILURE"), "BAD"),
            (AvailabilityObservation("write-store", "WRITE_PATH_AVAILABILITY", "FAILURE", store_healthy=False), "BAD"),
            (AvailabilityObservation("query-store-healthy", "QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY", "FAILURE", store_healthy=True), "BAD"),
            (AvailabilityObservation("provider-excluded", "CONTROL_API_AVAILABILITY", "FAILURE", external_provider_failure=True, provider_incident_ref="sha256:" + "1" * 64, local_path_healthy=True, exclusion_manifested=True), "EXCLUDED_EXTERNAL"),
            (AvailabilityObservation("provider-false-label", "CONTROL_API_AVAILABILITY", "FAILURE", external_provider_failure=True, local_path_healthy=False, exclusion_manifested=True), "BAD"),
            (AvailabilityObservation("semantic-4xx", "CONTROL_API_AVAILABILITY", "SEMANTIC_4XX"), "GOOD"),
        ]
        for observation, expected in cases:
            self.assertEqual(expected, classify_observation(observation).classification, observation.observation_id)

    def test_query_store_unhealthy_is_outside_only_conditional_query_denominator(self):
        from tools.aegis_control.availability import AvailabilityObservation, classify_observation
        observation = AvailabilityObservation("query-store-down", "QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY", "FAILURE", store_healthy=False)
        self.assertEqual("OUTSIDE_CONDITIONAL_DENOMINATOR", classify_observation(observation).classification)

    def test_evaluator_deduplicates_and_reports_missing_probe_without_attainment_claim(self):
        from tools.aegis_control.availability import AvailabilityObservation, evaluate_window
        rows = [
            AvailabilityObservation("probe-1", "CONTROL_API_AVAILABILITY", "SUCCESS", synthetic_probe=True),
            AvailabilityObservation("probe-1", "CONTROL_API_AVAILABILITY", "SUCCESS", synthetic_probe=True),
        ]
        result = evaluate_window(rows, required_probe_intervals=2, complete_window=False)
        self.assertEqual(1, result.denominator)
        self.assertEqual(1, result.numerator)
        self.assertIn("MISSING_SYNTHETIC_PROBE_INTERVAL", result.evidence_gaps)
        self.assertFalse(result.historical_attainment_claimed)
        self.assertEqual("INCOMPLETE", result.status)


if __name__ == "__main__": unittest.main()
