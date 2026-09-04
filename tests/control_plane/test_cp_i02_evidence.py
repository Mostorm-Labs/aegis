import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.generate_cp_i02_evidence import generate


class EvidenceTests(unittest.TestCase):
    def test_generates_reviewer_resolvable_zero_tolerance_bundle_without_gate_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "cp-i02"
            revision = "f" * 40
            manifest = generate(output, revision)
            self.assertEqual(revision, manifest["result_revision"])
            self.assertTrue(manifest["claims"]["cp_i02_bounded_conformance"])
            self.assertFalse(manifest["claims"]["p34_gate_pass"])
            self.assertFalse(manifest["claims"]["complete_CPV_E_D0_CONFORMANCE"])
            self.assertTrue(all(value == 0 for value in manifest["metrics"].values()))
            for filename in (
                "evidence-manifest.json", "canonical-conformance.json", "store-audit.json",
                "trace-corpus.json", "crash-matrix.json",
            ):
                path = output / filename
                self.assertTrue(path.is_file(), filename)
                json.loads(path.read_text(encoding="utf-8"))
            corpus = json.loads((output / "trace-corpus.json").read_text(encoding="utf-8"))
            self.assertEqual("EXERCISED", corpus["scenario_bindings"]["G02"]["coverage"])
            self.assertEqual("BOUND_SUBSTRATE_ONLY", corpus["scenario_bindings"]["G09"]["coverage"])

    def test_p36_bundle_exercises_terminal_successor_and_established_lane_race(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "cp-i02"
            manifest = generate(output, "d" * 40)
            corpus = json.loads((output / "trace-corpus.json").read_text(encoding="utf-8"))
            store_bundle = json.loads((output / "store-audit.json").read_text(encoding="utf-8"))

            traces = {trace["trace_id"]: trace for trace in corpus["traces"]}
            self.assertIn("G01-separate-successor", traces)
            self.assertIn("G01-stale-predecessor-zero-residue", traces)
            self.assertIn("G02-established-predecessor-race", traces)
            self.assertEqual("PASS", traces["G01-separate-successor"]["status"])
            self.assertEqual("PASS", traces["G01-stale-predecessor-zero-residue"]["status"])
            self.assertEqual("PASS", traces["G02-established-predecessor-race"]["status"])

            g01 = store_bundle["audits"]["g01_lifecycle"]
            self.assertEqual([1, 2], g01["lineages"]["STAGE_OCCURRENCE:so_g01_a"]["revisions"])
            self.assertEqual([1], g01["lineages"]["STAGE_OCCURRENCE:so_g01_b"]["revisions"])
            self.assertEqual(2, g01["lane_heads"]["lane_g01"]["version"])
            self.assertEqual(["so_g01_b"], g01["open_occurrences_by_lane"]["lane_g01"])
            self.assertEqual(0, g01["metrics"]["same_lane_double_winners"])

            stale = store_bundle["audits"]["g01_stale_predecessor"]
            self.assertEqual(1, stale["lane_heads"]["lane_g01_stale"]["version"])
            self.assertEqual(0, stale["metrics"]["same_lane_double_winners"])

            g02 = store_bundle["audits"]["g02_same_lane"]
            self.assertEqual(2, g02["lane_heads"]["lane_race"]["version"])
            self.assertEqual(2, len(g02["outbox"]))
            self.assertEqual(0, g02["metrics"]["same_lane_double_winners"])

            self.assertFalse(manifest["claims"]["p34_gate_pass"])
            self.assertTrue(all(value == 0 for value in manifest["metrics"].values()))

    def test_generator_is_directly_executable_from_repository_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(__file__).resolve().parents[2]
            script = root / "tests" / "control_plane" / "generate_cp_i02_evidence.py"
            result = subprocess.run(
                [sys.executable, str(script), "--result-revision", "e" * 40, "--output-dir", tmp],
                cwd=root, capture_output=True, text=True, check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((Path(tmp) / "evidence-manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
