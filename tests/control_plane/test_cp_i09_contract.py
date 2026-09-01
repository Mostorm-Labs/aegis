from __future__ import annotations

import unittest


class CpI09ContractRedTests(unittest.TestCase):
    def test_r0_rejects_short_warmup_measurement_or_accelerated_clock(self):
        from tests.control_plane.cp_i09_contract import BenchmarkContractError, R0Evidence, reference_data_shape, reference_r0_load, validate_r0

        base = dict(
            data_shape=reference_data_shape(),
            offered_load=reference_r0_load(),
            bursts={"api_200_rps_wall_seconds": 60, "mutation_100_rps_wall_seconds": 30, "provider_callbacks_per_minute": 1000},
            latency_quantiles_ms={},
            invariant_failures=0,
            accidental_semantic_duplicates=0,
            provider_call_inside_open_mutation_transaction=0,
        )
        for evidence in (
            R0Evidence(clock_class="REAL_MONOTONIC_WALL_CLOCK", warmup_wall_seconds=599.9, measurement_wall_seconds=1800.0, **base),
            R0Evidence(clock_class="REAL_MONOTONIC_WALL_CLOCK", warmup_wall_seconds=600.0, measurement_wall_seconds=1799.9, **base),
            R0Evidence(clock_class="ACCELERATED_REPLAY", warmup_wall_seconds=600.0, measurement_wall_seconds=1800.0, **base),
        ):
            with self.assertRaises(BenchmarkContractError):
                validate_r0(evidence, require_latency_targets=False)

    def test_r0_rejects_fixture_floor_or_missing_burst(self):
        from tests.control_plane.cp_i09_contract import BenchmarkContractError, DataShape, R0Evidence, reference_data_shape, reference_r0_load, validate_r0

        shape = reference_data_shape()
        too_small = DataShape(**{**shape.__dict__, "canonical_record_revisions_retained": 4_999_999})
        with self.assertRaises(BenchmarkContractError):
            validate_r0(R0Evidence(
                clock_class="REAL_MONOTONIC_WALL_CLOCK",
                warmup_wall_seconds=600,
                measurement_wall_seconds=1800,
                data_shape=too_small,
                offered_load=reference_r0_load(),
                bursts={"api_200_rps_wall_seconds": 60, "mutation_100_rps_wall_seconds": 30, "provider_callbacks_per_minute": 1000},
                latency_quantiles_ms={},
                invariant_failures=0,
                accidental_semantic_duplicates=0,
                provider_call_inside_open_mutation_transaction=0,
            ), require_latency_targets=False)
        with self.assertRaises(BenchmarkContractError):
            validate_r0(R0Evidence(
                clock_class="REAL_MONOTONIC_WALL_CLOCK",
                warmup_wall_seconds=600,
                measurement_wall_seconds=1800,
                data_shape=shape,
                offered_load=reference_r0_load(),
                bursts={"api_200_rps_wall_seconds": 59, "mutation_100_rps_wall_seconds": 30, "provider_callbacks_per_minute": 1000},
                latency_quantiles_ms={},
                invariant_failures=0,
                accidental_semantic_duplicates=0,
                provider_call_inside_open_mutation_transaction=0,
            ), require_latency_targets=False)

    def test_s0_requires_exact_four_x_real_15_min_and_recovery_below_yellow(self):
        from tests.control_plane.cp_i09_contract import BenchmarkContractError, S0Evidence, reference_data_shape, reference_s0_load, validate_s0

        base = dict(
            clock_class="REAL_MONOTONIC_WALL_CLOCK",
            data_shape=reference_data_shape(),
            offered_load=reference_s0_load(),
            invariant_failures=0,
            accidental_semantic_duplicates=0,
            recovery_pressure="GREEN",
        )
        with self.assertRaises(BenchmarkContractError):
            validate_s0(S0Evidence(stress_wall_seconds=899.9, **base))
        wrong_load = {**reference_s0_load(), "projection_evaluations_per_second": 799}
        with self.assertRaises(BenchmarkContractError):
            validate_s0(S0Evidence(stress_wall_seconds=900, **{**base, "offered_load": wrong_load}))
        with self.assertRaises(BenchmarkContractError):
            validate_s0(S0Evidence(stress_wall_seconds=900, **{**base, "recovery_pressure": "YELLOW"}))

    def test_w7d_requires_exact_168_accelerated_slices_and_raw_recompute(self):
        from tests.control_plane.cp_i09_contract import BenchmarkContractError, CostEvent, SevenDayCostEvidence, validate_w7d

        events = [CostEvent(hour=i, unit="PIU", classification="SUBSTANTIVE", count=100) for i in range(168)]
        events += [CostEvent(hour=i, unit="PRU", classification="OVERHEAD", count=5) for i in range(168)]
        valid = SevenDayCostEvidence(measurement_class="ACCELERATED_REPLAY", hourly_slices=tuple(range(168)), raw_events=tuple(events), reported_overhead_cost=840.0, reported_substantive_cost=16800.0, reported_ratio=0.05)
        self.assertAlmostEqual(0.05, validate_w7d(valid)["independent_ratio"])
        with self.assertRaises(BenchmarkContractError):
            validate_w7d(SevenDayCostEvidence(**{**valid.__dict__, "hourly_slices": tuple(range(167))}))
        with self.assertRaises(BenchmarkContractError):
            validate_w7d(SevenDayCostEvidence(**{**valid.__dict__, "measurement_class": "REAL_MONOTONIC_WALL_CLOCK"}))
        with self.assertRaises(BenchmarkContractError):
            validate_w7d(SevenDayCostEvidence(**{**valid.__dict__, "reported_ratio": 0.01}))

    def test_monthly_availability_cannot_be_claimed_by_cp_i09(self):
        from tests.control_plane.cp_i09_contract import BenchmarkContractError, validate_monthly_availability_claim
        self.assertEqual("NOT_CLAIMED_PRELAUNCH", validate_monthly_availability_claim("NOT_CLAIMED_PRELAUNCH"))
        with self.assertRaises(BenchmarkContractError):
            validate_monthly_availability_claim("PASS_99_9")


if __name__ == "__main__":
    unittest.main()
