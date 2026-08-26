import os
import subprocess
import sys
import unittest
from pathlib import Path


class OpenAIBaselineInvocationTests(unittest.TestCase):
    def test_direct_script_invocation_reaches_environment_gate(self):
        root = Path(__file__).resolve().parents[2]
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)
        completed = subprocess.run(
            [
                sys.executable,
                str(root / "evals" / "scripts" / "run_openai_baseline.py"),
                "--output",
                str(root / "tmp-baseline-output"),
            ],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 3, completed.stderr)
        self.assertIn("BLOCKED_ENVIRONMENT", completed.stderr)
        self.assertNotIn("ModuleNotFoundError", completed.stderr)


if __name__ == "__main__":
    unittest.main()
