import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CandidatePluginParityTests(unittest.TestCase):
    def test_candidate_artifact_is_exact_nine_non_published_and_exact_head(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "candidate.json"
            subprocess.run(
                ["python3", "scripts/build_candidate_plugin_parity.py", "--output", str(output)],
                cwd=ROOT,
                check=True,
                text=True,
            )
            artifact = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(artifact["artifact_class"], "CANDIDATE_PLUGIN_PARITY_EVIDENCE")
        self.assertEqual(artifact["repository"], {"provider": "github", "full_name": "Mostorm-Labs/aegis"})
        self.assertEqual(artifact["source_revision"], subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip())
        self.assertEqual(len(artifact["plugin"]["skills"]), 9)
        self.assertTrue(artifact["exact_nine"])
        self.assertFalse(artifact["public_release"])
        self.assertFalse(artifact["writes_plugin_tree"])
        self.assertNotIn("release_version", artifact)
        self.assertNotIn("tag", artifact)


if __name__ == "__main__":
    unittest.main()
