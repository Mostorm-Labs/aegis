import unittest
from dataclasses import replace
from pathlib import Path

from tools.aegis_skillset.distribution import (
    evaluate_catalog_snapshot,
    load_distribution_contract,
    validate_distribution_contract,
)
from tools.aegis_skillset.model import load_skillset

ROOT = Path(__file__).resolve().parents[2]
RELEASE = "0.1.0-task6.1"


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
        contract = load_distribution_contract(ROOT)
        cases = [
            replace(contract, plugin=replace(contract.plugin, skills=contract.plugin.skills + ("extra",))),
            replace(contract, plugin=replace(contract.plugin, skills=contract.plugin.skills[:-1])),
            replace(contract, standalone=replace(contract.standalone, skills=("aegis", "aegis-modeling"))),
            replace(contract, plugin=replace(contract.plugin, required_apps=("github",))),
        ]
        for bad in cases:
            self.assertTrue(validate_distribution_contract(ROOT, bad))

    def _all_skills(self):
        return list(load_distribution_contract(ROOT).plugin.skills)

    def _observation(self, kind, version=RELEASE):
        ids = {
            "plugin": "aegis",
            "standalone": "aegis-standalone",
            "individual_skills": "aegis-individual",
        }
        return {"kind": kind, "id": ids.get(kind, "unknown"), "release_version": version}

    def _snapshot(self, kind="plugin", skills=None, version=RELEASE, observations=None):
        if skills is None:
            skills = ["aegis"] if kind == "standalone" else self._all_skills()
        return {
            "schema_version": "0.1",
            "fresh_platform_event": True,
            "complete_catalog_capture": True,
            "platform_event_id": "synthetic",
            "surface": {"product": "chatgpt", "surface": "web"},
            "observed_distributions": observations or [self._observation(kind, version)],
            "installed_skills": skills,
            "component_release_versions": {},
            "release_manifest_ref": "skillset/releases/aegis-0.1.0-task6.1.json",
            "materialization_ref": "https://example.test/materialization",
        }

    def test_catalog_state_and_distribution_provenance_are_orthogonal(self):
        plugin = evaluate_catalog_snapshot(ROOT, self._snapshot("plugin"))
        self.assertEqual(
            ("PASS", "FULL_SPECIALIST", "PLUGIN", "multi_skill"),
            (plugin.verdict, plugin.catalog_state, plugin.distribution_provenance, plugin.runtime_mode),
        )

        standalone = evaluate_catalog_snapshot(ROOT, self._snapshot("standalone"))
        self.assertEqual(
            ("PASS", "COMPOSITE_ONLY", "STANDALONE", "compatibility"),
            (standalone.verdict, standalone.catalog_state, standalone.distribution_provenance, standalone.runtime_mode),
        )

        manual_full = evaluate_catalog_snapshot(
            ROOT,
            self._snapshot("individual_skills", skills=list(reversed(self._all_skills()))),
        )
        self.assertEqual(
            ("PASS", "FULL_SPECIALIST", "INDIVIDUAL_SKILLS", "multi_skill"),
            (manual_full.verdict, manual_full.catalog_state, manual_full.distribution_provenance, manual_full.runtime_mode),
        )

        manual_composite = evaluate_catalog_snapshot(
            ROOT,
            self._snapshot("individual_skills", skills=["aegis"]),
        )
        self.assertEqual(
            ("PASS", "COMPOSITE_ONLY", "INDIVIDUAL_SKILLS", "compatibility"),
            (manual_composite.verdict, manual_composite.catalog_state, manual_composite.distribution_provenance, manual_composite.runtime_mode),
        )

    def test_product_provenance_mismatch_fails_closed_without_faking_compatibility(self):
        broken_plugin = evaluate_catalog_snapshot(ROOT, self._snapshot("plugin", skills=["aegis"]))
        self.assertEqual(
            ("BLOCKED_ENVIRONMENT", "COMPOSITE_ONLY", "PLUGIN", None),
            (broken_plugin.verdict, broken_plugin.catalog_state, broken_plugin.distribution_provenance, broken_plugin.runtime_mode),
        )

        impossible_standalone = evaluate_catalog_snapshot(ROOT, self._snapshot("standalone", skills=self._all_skills()))
        self.assertEqual(
            ("BLOCKED_ENVIRONMENT", "FULL_SPECIALIST", "STANDALONE", None),
            (impossible_standalone.verdict, impossible_standalone.catalog_state, impossible_standalone.distribution_provenance, impossible_standalone.runtime_mode),
        )

    def test_partial_mixed_duplicate_and_unknown_states_fail_closed(self):
        partial = evaluate_catalog_snapshot(
            ROOT,
            self._snapshot("individual_skills", skills=["aegis", "aegis-project-state"]),
        )
        self.assertEqual(
            ("BLOCKED_ENVIRONMENT", "PARTIAL_CATALOG", "INDIVIDUAL_SKILLS"),
            (partial.verdict, partial.catalog_state, partial.distribution_provenance),
        )

        mixed = evaluate_catalog_snapshot(ROOT, self._snapshot("individual_skills", version="0.9.9"))
        self.assertEqual(
            ("BLOCKED_ENVIRONMENT", "MIXED_REVISION", "INDIVIDUAL_SKILLS"),
            (mixed.verdict, mixed.catalog_state, mixed.distribution_provenance),
        )

        duplicate = evaluate_catalog_snapshot(
            ROOT,
            self._snapshot(
                observations=[self._observation("plugin"), self._observation("standalone")],
                skills=self._all_skills(),
            ),
        )
        self.assertEqual(
            ("BLOCKED_ENVIRONMENT", "FULL_SPECIALIST", "DUPLICATE_DISTRIBUTION"),
            (duplicate.verdict, duplicate.catalog_state, duplicate.distribution_provenance),
        )

        unknown = evaluate_catalog_snapshot(
            ROOT,
            self._snapshot(observations=[{"kind": "mystery", "id": "mystery", "release_version": RELEASE}]),
        )
        self.assertEqual(
            ("BLOCKED_EVIDENCE", "FULL_SPECIALIST", "UNKNOWN"),
            (unknown.verdict, unknown.catalog_state, unknown.distribution_provenance),
        )

    def test_missing_evidence_envelope_is_blocked_evidence(self):
        for key in ("materialization_ref", "platform_event_id"):
            snapshot = self._snapshot()
            snapshot.pop(key)
            result = evaluate_catalog_snapshot(ROOT, snapshot)
            self.assertEqual(("BLOCKED_EVIDENCE", None), (result.verdict, result.catalog_state))
        snapshot = self._snapshot()
        snapshot["complete_catalog_capture"] = False
        result = evaluate_catalog_snapshot(ROOT, snapshot)
        self.assertEqual(("BLOCKED_EVIDENCE", None), (result.verdict, result.catalog_state))


if __name__ == "__main__":
    unittest.main()
