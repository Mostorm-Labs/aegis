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
