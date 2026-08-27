import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "tools/aegis_skillset/dogfood.py"
MANIFEST = ROOT / "skillset/dogfood/installed-platform-rerun-v0.2.json"


class InstalledPlatformGateTests(unittest.TestCase):
    def _dogfood(self):
        self.assertTrue(MODULE.is_file(), "installed-platform evaluator module missing")
        spec = importlib.util.spec_from_file_location("tools.aegis_skillset.dogfood", MODULE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_current_rerun_manifest_fails_closed_without_platform_evidence(self):
        self.assertTrue(MANIFEST.is_file(), "Task 6 rerun manifest missing")
        module = self._dogfood()
        result = module.evaluate_installed_platform_rerun(ROOT, MANIFEST)
        self.assertEqual("BLOCKED_EVIDENCE", result.verdict)
        self.assertEqual(4, len(result.cases))
        self.assertTrue(all(case.verdict == "BLOCKED_EVIDENCE" for case in result.cases))
        self.assertEqual((), result.errors)

    def test_four_admissible_terminal_traces_pass(self):
        self.assertTrue(MANIFEST.is_file(), "Task 6 rerun manifest missing")
        module = self._dogfood()
        traces = {
            "09-01-direct-specialist": {
                "terminal": True,
                "mode": "multi_skill",
                "invocations": [
                    {"skill": "aegis-project-state", "role": "support"},
                    {"skill": "aegis-gate-review", "role": "primary"},
                ],
                "final_answer_owner": "aegis-gate-review",
                "genuine_ambiguity": False,
                "earlier_blocker_conclusively_established": False,
                "specialist_availability": {"aegis-gate-review": "available"},
                "ownership_edges": [],
                "handoff_edges": [],
                "forbidden_downstream_substantive_execution": 0,
                "primary_substantive_result_emitted": True,
            },
            "09-01-ambiguous-router": {
                "terminal": True,
                "mode": "multi_skill",
                "invocations": [{"skill": "aegis", "role": "router"}],
                "final_answer_owner": "aegis",
                "genuine_ambiguity": True,
                "earlier_blocker_conclusively_established": False,
                "specialist_availability": {},
                "ownership_edges": [],
                "handoff_edges": [],
                "forbidden_downstream_substantive_execution": 0,
                "primary_substantive_result_emitted": False,
            },
            "09-01-upstream-blocker-reroute": {
                "terminal": True,
                "mode": "multi_skill",
                "invocations": [
                    {"skill": "aegis-project-state", "role": "support"},
                    {"skill": "aegis", "role": "router"},
                ],
                "final_answer_owner": "aegis",
                "genuine_ambiguity": False,
                "earlier_blocker_conclusively_established": True,
                "specialist_availability": {"aegis-architecture": "available"},
                "ownership_edges": [],
                "handoff_edges": [],
                "forbidden_downstream_substantive_execution": 0,
                "primary_substantive_result_emitted": False,
            },
            "09-01-composite-fallback": {
                "terminal": True,
                "mode": "compatibility",
                "invocations": [{"skill": "aegis", "role": "router"}],
                "final_answer_owner": "aegis",
                "genuine_ambiguity": False,
                "earlier_blocker_conclusively_established": False,
                "specialist_availability": {"aegis-modeling": "unavailable"},
                "ownership_edges": [],
                "handoff_edges": [],
                "forbidden_downstream_substantive_execution": 0,
                "primary_substantive_result_emitted": True,
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            for case in manifest["cases"]:
                evidence = {
                    "schema_version": "0.2",
                    "case_id": case["id"],
                    "fresh_platform_event": True,
                    "complete_response_captured": True,
                    "platform_event_id": "synthetic-test-" + case["id"],
                    "environment": {"catalog_mode": case["required_catalog_mode"]},
                    "trace": traces[case["id"]],
                }
                path = tmp / (case["id"] + ".json")
                path.write_text(json.dumps(evidence), encoding="utf-8")
                case["evidence_ref"] = str(path)
            manifest_path = tmp / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = module.evaluate_installed_platform_rerun(ROOT, manifest_path)
        self.assertEqual("PASS", result.verdict)
        self.assertTrue(all(case.verdict == "PASS" for case in result.cases))

    def test_hard_ownership_violation_fails_aggregate_gate(self):
        self.assertTrue(MANIFEST.is_file(), "Task 6 rerun manifest missing")
        module = self._dogfood()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            target = manifest["cases"][0]
            evidence = {
                "schema_version": "0.2",
                "case_id": target["id"],
                "fresh_platform_event": True,
                "complete_response_captured": True,
                "platform_event_id": "bad-direct",
                "environment": {"catalog_mode": target["required_catalog_mode"]},
                "trace": {
                    "terminal": True,
                    "mode": "multi_skill",
                    "invocations": [{"skill": "aegis", "role": "router"}],
                    "final_answer_owner": "aegis",
                    "genuine_ambiguity": False,
                    "earlier_blocker_conclusively_established": False,
                    "specialist_availability": {"aegis-gate-review": "available"},
                    "ownership_edges": [],
                    "handoff_edges": [],
                    "forbidden_downstream_substantive_execution": 0,
                    "primary_substantive_result_emitted": True,
                },
            }
            evidence_path = tmp / "bad.json"
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            target["evidence_ref"] = str(evidence_path)
            manifest_path = tmp / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = module.evaluate_installed_platform_rerun(ROOT, manifest_path)
        self.assertEqual("FAIL", result.verdict)
        first = next(case for case in result.cases if case.case_id == "09-01-direct-specialist")
        self.assertIn("ROUTER_OWNERSHIP_LEAK", first.violations)


if __name__ == "__main__":
    unittest.main()
