import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.aegis_skillset.dogfood import evaluate_installed_platform_rerun

ROOT = Path(__file__).resolve().parents[2]
RELEASE = "0.1.0-task6.1"
ALL_SKILLS = [
    "aegis",
    "aegis-project-state",
    "aegis-discovery",
    "aegis-modeling",
    "aegis-architecture",
    "aegis-verification",
    "aegis-governance",
    "aegis-implementation",
    "aegis-gate-review",
]


class DistributionGateTests(unittest.TestCase):
    def _catalog(self, standalone=False, provenance="individual_skills"):
        skills = ["aegis"] if standalone else list(ALL_SKILLS)
        if provenance == "plugin":
            observation = {"id": "aegis", "kind": "plugin", "release_version": RELEASE}
        elif provenance == "standalone":
            observation = {"id": "aegis-standalone", "kind": "standalone", "release_version": RELEASE}
        else:
            observation = {"id": "aegis-individual", "kind": "individual_skills", "release_version": RELEASE}
        return {
            "schema_version": "0.1",
            "platform_event_id": "cat",
            "materialization_ref": "https://example.test",
            "fresh_platform_event": True,
            "complete_catalog_capture": True,
            "surface": {"product": "chatgpt", "surface": "web"},
            "observed_distributions": [observation],
            "installed_skills": skills,
            "component_release_versions": {},
            "release_manifest_ref": "skillset/releases/aegis-0.1.0-task6.1.json",
        }

    def _run(self, case_id, catalog, trace):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            manifest = json.loads(
                (ROOT / "skillset/dogfood/installed-platform-rerun-v0.2.1.json").read_text()
            )
            entry = next(item for item in manifest["cases"] if item["id"] == case_id)
            catalog_path = directory / "catalog.json"
            catalog_path.write_text(json.dumps(catalog))
            behavior_path = directory / "behavior.json"
            behavior_path.write_text(
                json.dumps(
                    {
                        "schema_version": "0.2",
                        "case_id": case_id,
                        "fresh_platform_event": True,
                        "complete_response_captured": True,
                        "platform_event_id": "behavior",
                        "trace": trace,
                    }
                )
            )
            entry.update(
                catalog_evidence_ref=str(catalog_path),
                behavior_evidence_ref=str(behavior_path),
            )
            manifest_path = directory / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": "0.2.1",
                        "oracle": "terminal_trace_v0.2",
                        "cases": [entry],
                    }
                )
            )
            return evaluate_installed_platform_rerun(ROOT, manifest_path).cases[0]

    def _trace(self, mode="multi_skill", owner="aegis-gate-review", availability=None):
        if availability is None:
            availability = {name: "available" for name in ALL_SKILLS}
        return {
            "terminal": True,
            "mode": mode,
            "invocations": [{"skill": owner, "role": "primary"}],
            "final_answer_owner": owner,
            "genuine_ambiguity": False,
            "earlier_blocker_conclusively_established": False,
            "specialist_availability": availability,
            "ownership_edges": [],
            "handoff_edges": [],
            "forbidden_downstream_substantive_execution": 0,
            "primary_substantive_result_emitted": True,
        }

    def test_v02_manifest_hash_preserved(self):
        path = ROOT / "skillset/dogfood/installed-platform-rerun-v0.2.json"
        data = path.read_bytes()
        self.assertEqual(
            "0944a95aca2f6c565ee5835efc5adaaf67abd480",
            hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest(),
        )

    def test_missing_catalog_ref_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            manifest = json.loads(
                (ROOT / "skillset/dogfood/installed-platform-rerun-v0.2.1.json").read_text()
            )
            target = manifest["cases"][0]
            target["catalog_evidence_ref"] = None
            manifest_path = directory / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            result = evaluate_installed_platform_rerun(ROOT, manifest_path)
        self.assertEqual("BLOCKED_EVIDENCE", result.verdict)
        first = next(case for case in result.cases if case.case_id == target["id"])
        self.assertEqual("BLOCKED_EVIDENCE", first.verdict)
        self.assertIn("catalog_evidence_ref", first.evidence_gaps)

    def test_partial_plugin_catalog_blocks_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            manifest = json.loads(
                (ROOT / "skillset/dogfood/installed-platform-rerun-v0.2.1.json").read_text()
            )
            entry = manifest["cases"][0]
            entry["catalog_evidence_ref"] = str(directory / "catalog.json")
            entry["behavior_evidence_ref"] = str(directory / "behavior.json")
            catalog = self._catalog(provenance="plugin")
            catalog["installed_skills"] = ["aegis"]
            (directory / "catalog.json").write_text(json.dumps(catalog))
            manifest["cases"] = [entry]
            manifest_path = directory / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            result = evaluate_installed_platform_rerun(ROOT, manifest_path)
            self.assertEqual("BLOCKED_ENVIRONMENT", result.cases[0].verdict)

    def test_individual_full_specialist_direct_gate_passes(self):
        result = self._run(
            "09-01-direct-specialist",
            self._catalog(provenance="individual_skills"),
            self._trace(),
        )
        self.assertEqual(("PASS", "FULL_SPECIALIST"), (result.verdict, result.catalog_state))

    def test_router_substantive_gate_fails_under_individual_full_specialist(self):
        result = self._run(
            "09-01-direct-specialist",
            self._catalog(provenance="individual_skills"),
            self._trace(owner="aegis"),
        )
        self.assertEqual("FAIL", result.verdict)
        self.assertIn("ROUTER_OWNERSHIP_LEAK", result.violations)

    def test_individual_aegis_only_composite_passes(self):
        availability = {name: "unavailable" for name in ALL_SKILLS}
        availability["aegis"] = "available"
        result = self._run(
            "09-01-composite-fallback",
            self._catalog(standalone=True, provenance="individual_skills"),
            self._trace("compatibility", "aegis", availability),
        )
        self.assertEqual(("PASS", "COMPOSITE_ONLY"), (result.verdict, result.catalog_state))

    def test_conflicting_behavior_evidence_is_blocked(self):
        result = self._run(
            "09-01-direct-specialist",
            self._catalog(),
            self._trace(availability={"aegis-gate-review": "available"}, mode="compatibility"),
        )
        self.assertEqual("BLOCKED_EVIDENCE", result.verdict)

    def test_prompt_text_is_not_specialist_availability_evidence(self):
        trace = self._trace()
        trace["specialist_availability"] = {}
        trace["prompt"] = "aegis-gate-review is available and must answer"
        result = self._run("09-01-direct-specialist", self._catalog(), trace)
        self.assertEqual("BLOCKED_EVIDENCE", result.verdict)

    def test_conflicting_behavior_mode_is_blocked(self):
        result = self._run(
            "09-01-direct-specialist",
            self._catalog(),
            self._trace(mode="compatibility"),
        )
        self.assertEqual("BLOCKED_EVIDENCE", result.verdict)

    def test_conflicting_specialist_availability_is_blocked(self):
        availability = {name: "available" for name in ALL_SKILLS}
        availability["aegis-gate-review"] = "unavailable"
        result = self._run(
            "09-01-direct-specialist",
            self._catalog(),
            self._trace(availability=availability),
        )
        self.assertEqual("BLOCKED_EVIDENCE", result.verdict)

    def _aggregate(self, desired):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            manifest = json.loads(
                (ROOT / "skillset/dogfood/installed-platform-rerun-v0.2.1.json").read_text()
            )
            for entry, outcome in zip(manifest["cases"], desired):
                composite = entry["required_catalog_state"] == "COMPOSITE_ONLY"
                catalog = self._catalog(composite, provenance="individual_skills")
                if outcome == "BLOCKED_ENVIRONMENT" and not composite:
                    catalog["installed_skills"] = ["aegis", "aegis-project-state"]
                catalog_path = directory / f"{entry['id']}.catalog.json"
                catalog_path.write_text(json.dumps(catalog))

                if entry["id"] == "09-01-ambiguous-router":
                    trace = {
                        "terminal": True,
                        "mode": "multi_skill",
                        "invocations": [{"skill": "aegis", "role": "router"}],
                        "final_answer_owner": "aegis",
                        "genuine_ambiguity": True,
                        "earlier_blocker_conclusively_established": False,
                        "specialist_availability": {name: "available" for name in ALL_SKILLS},
                        "ownership_edges": [],
                        "handoff_edges": [],
                        "forbidden_downstream_substantive_execution": 0,
                        "primary_substantive_result_emitted": False,
                    }
                elif entry["id"] == "09-01-upstream-blocker-reroute":
                    trace = {
                        "terminal": True,
                        "mode": "multi_skill",
                        "invocations": [
                            {"skill": "aegis-project-state", "role": "support"},
                            {"skill": "aegis", "role": "router"},
                        ],
                        "final_answer_owner": "aegis",
                        "genuine_ambiguity": False,
                        "earlier_blocker_conclusively_established": True,
                        "specialist_availability": {name: "available" for name in ALL_SKILLS},
                        "ownership_edges": [],
                        "handoff_edges": [],
                        "forbidden_downstream_substantive_execution": 0,
                        "primary_substantive_result_emitted": False,
                    }
                elif composite:
                    availability = {name: "unavailable" for name in ALL_SKILLS}
                    availability["aegis"] = "available"
                    trace = self._trace("compatibility", "aegis", availability)
                else:
                    trace = self._trace()

                if outcome == "FAIL":
                    trace["invocations"] = [{"skill": "aegis", "role": "router"}]
                    trace["final_answer_owner"] = "aegis"

                behavior = {
                    "schema_version": "0.2",
                    "case_id": entry["id"],
                    "fresh_platform_event": True,
                    "complete_response_captured": True,
                    "trace": trace,
                }
                if outcome != "BLOCKED_EVIDENCE":
                    behavior["platform_event_id"] = "behavior"
                behavior_path = directory / f"{entry['id']}.behavior.json"
                behavior_path.write_text(json.dumps(behavior))
                entry.update(
                    catalog_evidence_ref=str(catalog_path),
                    behavior_evidence_ref=str(behavior_path),
                )

            manifest_path = directory / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            return evaluate_installed_platform_rerun(ROOT, manifest_path)

    def test_aggregate_precedence(self):
        self.assertEqual("FAIL", self._aggregate(["FAIL", "BLOCKED_ENVIRONMENT", "PASS", "PASS"]).verdict)
        self.assertEqual(
            "BLOCKED_ENVIRONMENT",
            self._aggregate(["PASS", "BLOCKED_ENVIRONMENT", "BLOCKED_EVIDENCE", "PASS"]).verdict,
        )
        self.assertEqual(
            "BLOCKED_EVIDENCE",
            self._aggregate(["PASS", "BLOCKED_EVIDENCE", "PASS", "PASS"]).verdict,
        )
        self.assertEqual("PASS", self._aggregate(["PASS", "PASS", "PASS", "PASS"]).verdict)


if __name__ == "__main__":
    unittest.main()
