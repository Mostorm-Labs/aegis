from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class GateClosureStabilityTests(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_scenario_a_stable_closure_freezes_blocking_target_after_p31(self):
        core = self._read("skills/aegis/references/shared/core-invariants.md")
        gate = self._read("skills/aegis-gate-review/references/gate-review.md")
        self.assertIn("Gate Closure Stability Principle", core)
        self.assertIn("Once P31 authorizes implementation", core)
        self.assertIn("blocking completion target is frozen", core)
        self.assertIn("FROZEN_REQUIREMENT_FAILURE", gate)
        self.assertIn("Frozen Requirement Audit", gate)
        self.assertIn("Frozen Evidence Audit", gate)

    def test_scenario_b_redundant_new_evidence_is_non_blocking(self):
        core = self._read("skills/aegis/references/shared/core-invariants.md")
        gate = self._read("skills/aegis-gate-review/references/gate-review.md")
        self.assertIn("Anti-Proof-Recursion Rule", core)
        self.assertIn("new_evidence_unique_detection_value", gate)
        self.assertIn("NON_BLOCKING_FINDING", gate)
        self.assertIn("solely to increase confidence", core)

    def test_scenario_c_real_late_high_impact_defect_can_override_stability(self):
        gate = self._read("skills/aegis-gate-review/references/gate-review.md")
        self.assertIn("NEWLY_DISCOVERED_FINDING", gate)
        self.assertIn("blocking_high_impact", gate)
        self.assertIn("why_existing_frozen_evidence_did_not_cover_it", gate)
        self.assertIn("why_it_is_severe_enough_to_override_closure_stability", gate)
        self.assertIn("data-integrity", gate)

    def test_scenario_d_p31_ambiguity_returns_to_p20_or_p31_before_coding(self):
        implementation = self._read("skills/aegis-implementation/references/implementation-control.md")
        self.assertIn("EXECUTION_CLOSURE_CONTRACT", implementation)
        self.assertIn("MISSING_REQUIRED_INPUT", implementation)
        self.assertIn("FROZEN_VERIFICATION_FAILURE", implementation)
        self.assertIn("NEW_HIGH_IMPACT_FAILURE_MODE", implementation)
        self.assertIn("continue_until_terminal_state: true", implementation)
        self.assertIn("return to P20/P31", implementation)

    def test_scenario_e_repeated_p33_package_patching_routes_to_earlier_layer(self):
        implementation = self._read("skills/aegis-implementation/references/implementation-control.md")
        gate = self._read("skills/aegis-gate-review/references/gate-review.md")
        self.assertIn("P33_REPETITION_GUARD", implementation)
        self.assertIn("TASK_PACKAGE_DEFECT", implementation)
        self.assertIn("VERIFICATION_DESIGN_DEFECT", implementation)
        self.assertIn("TASK_PACKAGE_DEFECT", gate)
        self.assertIn("VERIFICATION_DESIGN_DEFECT", gate)
        self.assertIn("NON_BLOCKING_HARDENING", gate)

    def test_scenario_f_standard_profile_does_not_require_evidence_only_descendant(self):
        routing = self._read("skills/aegis/references/bootstrap-routing.md")
        implementation = self._read("skills/aegis-implementation/references/implementation-control.md")
        self.assertIn("default for most ordinary feature", routing)
        self.assertIn("exact PR source SHA", routing)
        self.assertIn("required local tests", routing)
        self.assertIn("hosted CI", routing)
        self.assertIn("evidence-only descendant", routing)
        self.assertIn("not mandatory", routing)
        self.assertIn("Standard profile", implementation)
        self.assertIn("PR head", implementation)

    def test_scenario_g_full_profile_remains_strict_with_justification(self):
        routing = self._read("skills/aegis/references/bootstrap-routing.md")
        self.assertIn("profile justification", routing)
        self.assertIn("protocol/schema release", routing)
        self.assertIn("security critical", routing)
        self.assertIn("data-integrity critical", routing)
        self.assertIn("clean checkout", routing)
        self.assertIn("materialized evidence", routing)
        self.assertIn("provenance", routing)


if __name__ == "__main__":
    unittest.main()
