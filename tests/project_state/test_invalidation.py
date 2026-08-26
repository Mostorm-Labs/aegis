import tempfile
import unittest
from pathlib import Path

from tests.project_state.helpers import manifests, write_project
from tools.aegis_state.compute import compute_state
from tools.aegis_state.model import load_manifests


def add_supersession(authorities, change_class):
    authorities["authorities"][0]["status"] = "Superseded"
    authorities["authorities"].append({"id":"schema-v2","scope":"document","kind":"semantic_schema","version":"v2","status":"Current","ref":"docs/schema-v2.md","depends_on":[],"supersedes":"schema-v1","change_class":change_class})


class InvalidationTests(unittest.TestCase):
    def state(self, authorities, evidence=None):
        with tempfile.TemporaryDirectory() as td:
            project, _, gates, base_ev = manifests()
            gates["gates"][0]["validity"] = "stale"
            write_project(Path(td), project, authorities, gates, evidence or base_ev)
            return compute_state(load_manifests(Path(td)))

    def test_breaking_supersession_marks_direct_dependent_stale(self):
        _, authorities, _, _ = manifests()
        add_supersession(authorities, "breaking")
        state = self.state(authorities)
        self.assertIn("arch-v1", state["stale_authorities"])
        self.assertEqual(state["earliest_untrusted_layer"], "architecture")
        self.assertEqual(state["recommended_next_stage"], "P21")

    def test_compatible_supersession_marks_direct_dependent_needs_review(self):
        _, authorities, _, _ = manifests()
        add_supersession(authorities, "compatible")
        state = self.state(authorities)
        self.assertIn("arch-v1", state["needs_review_authorities"])
        self.assertNotIn("arch-v1", state["stale_authorities"])

    def test_stale_dependency_propagates_transitively(self):
        _, authorities, _, _ = manifests()
        add_supersession(authorities, "semantic")
        authorities["authorities"].append({"id":"plan-v1","scope":"g1","kind":"implementation_plan","version":"v1","status":"Current","ref":"docs/plan-v1.md","depends_on":["arch-v1"]})
        state = self.state(authorities)
        self.assertIn("arch-v1", state["stale_authorities"])
        self.assertIn("plan-v1", state["stale_authorities"])

    def test_available_unaffected_review_suppresses_direct_invalidation(self):
        _, authorities, _, evidence = manifests()
        add_supersession(authorities, "breaking")
        evidence["evidence"].append({"id":"ev-impact","type":"review","ref":"review://impact","status":"available","subject_ids":["arch-v1"]})
        authorities["impact_reviews"].append({"id":"impact-1","source_authority":"schema-v2","dependent_authority":"arch-v1","outcome":"unaffected","evidence_ids":["ev-impact"]})
        state = self.state(authorities, evidence)
        self.assertNotIn("arch-v1", state["stale_authorities"])
        self.assertNotIn("arch-v1", state["needs_review_authorities"])

    def test_unaffected_review_without_available_evidence_fails_closed(self):
        _, authorities, _, evidence = manifests()
        add_supersession(authorities, "breaking")
        evidence["evidence"].append({"id":"ev-impact","type":"review","ref":"review://impact","status":"missing","subject_ids":["arch-v1"]})
        authorities["impact_reviews"].append({"id":"impact-1","source_authority":"schema-v2","dependent_authority":"arch-v1","outcome":"unaffected","evidence_ids":["ev-impact"]})
        state = self.state(authorities, evidence)
        self.assertIn("arch-v1", state["stale_authorities"])


if __name__ == "__main__":
    unittest.main()
