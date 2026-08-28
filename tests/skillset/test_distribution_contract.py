import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from tools.aegis_skillset.distribution import (
    DistributionSpec,
    evaluate_catalog_snapshot,
    load_distribution_contract,
    validate_distribution_contract,
)
from tools.aegis_skillset.model import load_skillset

ROOT = Path(__file__).resolve().parents[2]


class DistributionContractTests(unittest.TestCase):
    def test_topology_and_no_apps(self):
        contract = load_distribution_contract(ROOT)
        names = tuple(s.name for s in load_skillset(ROOT).skills)
        self.assertEqual(names, contract.plugin.skills)
        self.assertEqual(("aegis",), contract.standalone.skills)
        self.assertEqual((), contract.plugin.required_apps)
        self.assertEqual((), contract.plugin.optional_apps)

    def test_distribution_does_not_create_stage_owner(self):
        self.assertNotIn("aegis-plugin", set(load_skillset(ROOT).primary_owner_by_stage.values()))

    def test_negative_contract_shapes(self):
        c = load_distribution_contract(ROOT)
        cases = [
            replace(c, plugin=replace(c.plugin, skills=c.plugin.skills + ("extra",))),
            replace(c, plugin=replace(c.plugin, skills=c.plugin.skills[:-1])),
            replace(c, standalone=replace(c.standalone, skills=("aegis", "aegis-modeling"))),
            replace(c, plugin=replace(c.plugin, required_apps=("github",))),
        ]
        for bad in cases:
            self.assertTrue(validate_distribution_contract(ROOT, bad))

    def _manifest(self):
        return json.loads((ROOT / "skillset/releases/aegis-0.1.0-task6.1.json").read_text())

    def _snapshot(self, kind="plugin", skills=None, version="0.1.0-task6.1", observations=None):
        return {
            "schema_version": "0.1", "fresh_platform_event": True,
            "complete_catalog_capture": True, "platform_event_id": "synthetic",
            "surface": {"product": "chatgpt", "surface": "web"},
            "observed_distributions": observations or [{"kind": kind, "id": "aegis" if kind == "plugin" else "aegis-standalone", "release_version": version}],
            "installed_skills": skills if skills is not None else list(load_distribution_contract(ROOT).plugin.skills if kind == "plugin" else ("aegis",)),
            "component_release_versions": {},
            "release_manifest_ref": "skillset/releases/aegis-0.1.0-task6.1.json",
            "materialization_ref": "https://example.test/materialization",
        }

    def test_catalog_states(self):
        full = evaluate_catalog_snapshot(ROOT, self._snapshot())
        self.assertEqual(("PASS", "FULL_SPECIALIST", "multi_skill"), (full.verdict, full.catalog_state, full.runtime_mode))
        standalone = evaluate_catalog_snapshot(ROOT, self._snapshot("standalone"))
        self.assertEqual(("PASS", "COMPOSITE_ONLY", "compatibility"), (standalone.verdict, standalone.catalog_state, standalone.runtime_mode))
        partial = evaluate_catalog_snapshot(ROOT, self._snapshot(skills=["aegis"]))
        self.assertEqual(("BLOCKED_ENVIRONMENT", "PARTIAL_CATALOG"), (partial.verdict, partial.catalog_state))
        mixed = evaluate_catalog_snapshot(ROOT, self._snapshot(version="0.9.9"))
        self.assertEqual(("BLOCKED_ENVIRONMENT", "MIXED_REVISION"), (mixed.verdict, mixed.catalog_state))
        duplicate = evaluate_catalog_snapshot(ROOT, self._snapshot(observations=[{"kind":"plugin","id":"aegis","release_version":"0.1.0-task6.1"},{"kind":"standalone","id":"aegis-standalone","release_version":"0.1.0-task6.1"}]))
        self.assertEqual(("BLOCKED_ENVIRONMENT", "DUPLICATE_DISTRIBUTION"), (duplicate.verdict, duplicate.catalog_state))

    def test_missing_evidence_envelope_is_blocked_evidence(self):
        for key in ("materialization_ref", "platform_event_id"):
            snapshot = self._snapshot(); snapshot.pop(key)
            result = evaluate_catalog_snapshot(ROOT, snapshot)
            self.assertEqual(("BLOCKED_EVIDENCE", None), (result.verdict, result.catalog_state))
        snapshot = self._snapshot(); snapshot["complete_catalog_capture"] = False
        result = evaluate_catalog_snapshot(ROOT, snapshot)
        self.assertEqual(("BLOCKED_EVIDENCE", None), (result.verdict, result.catalog_state))


if __name__ == "__main__":
    unittest.main()
