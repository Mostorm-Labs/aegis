import ast
from pathlib import Path
import unittest

import reference_model as crm


class ReferenceModelTests(unittest.TestCase):
    def test_p13_operation_vocabulary_is_exact(self):
        self.assertEqual(set(crm.ALLOWED_OPERATIONS), {"MATERIALIZE_IMPLEMENTATION_PACKAGE", "REVISE_IMPLEMENTATION_PACKAGE", "SCHEDULE_STAGE_OCCURRENCE", "RECORD_EXECUTION_PROGRESS", "TERMINATE_STAGE_OCCURRENCE", "RAISE_ESCALATION", "RECORD_ESCALATION_RESOLUTION", "SCHEDULE_REPAIR_OCCURRENCE", "SCHEDULE_REVERIFICATION_OCCURRENCE", "SCHEDULE_REREVIEW_OCCURRENCE", "RECOMPUTE_CONTROL_PROJECTION"})
        self.assertFalse(crm.is_legal_operation("PATCH_STAGE_OCCURRENCE"))

    def test_delivery_retry_reuses_semantic_occurrence(self):
        trace = {"semantic_attempt_id": "attempt-1", "delivery_occurrence_ids": ["so_1", "so_1", "so_1"]}
        self.assertEqual(crm.detect_semantic_violations(trace), set())
        trace["delivery_occurrence_ids"] = ["so_1", "so_2"]
        self.assertIn("DELIVERY_CREATED_SEMANTIC_RETRY", crm.detect_semantic_violations(trace))

    def test_required_child_barrier_requires_exact_binding(self):
        trace = {"required_child_ids": ["so_child_a", "so_child_b"], "required_child_acceptance_bindings": ["so_child_a"], "successor_scheduled": True}
        self.assertIn("REQUIRED_CHILD_BARRIER_BYPASS", crm.detect_semantic_violations(trace))

    def test_current_rollout_denies_cross_primary_auto_dispatch(self):
        trace = {"cross_primary_auto_dispatch": True, "rollout_authorized": False}
        self.assertIn("UNAUTHORIZED_CROSS_PRIMARY_DISPATCH", crm.detect_semantic_violations(trace))

    def test_p33_four_states_are_distinct(self):
        ancestry = {("anchor", "cursor"), ("anchor", "desc"), ("cursor", "desc"), ("anchor", "observed")}
        self.assertEqual(crm.classify_p33("anchor", "cursor", "cursor", ancestry), "EXACT_CURSOR")
        self.assertEqual(crm.classify_p33("anchor", "desc", "cursor", ancestry), "DESCENDANT_CURSOR")
        self.assertEqual(crm.classify_p33("anchor", "observed", None, ancestry), "ANCHOR_DESCENDANT_WITHOUT_CURSOR")
        self.assertEqual(crm.classify_p33("anchor", "other", "cursor", ancestry), "DIVERGED")

    def test_reference_model_has_no_production_control_flow_imports(self):
        path = Path(__file__).with_name("reference_model.py")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        forbidden = ("tools.aegis_control.scheduler", "tools.aegis_control.mutation", "tools.aegis_control.projection", "tools.aegis_control.policy", "tools.aegis_control.dispatch", "tools.aegis_control.recovery", "tools.aegis_control.service", "tools.aegis_control.store")
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertFalse([name for name in imported if name.startswith(forbidden)])


if __name__ == "__main__":
    unittest.main()
