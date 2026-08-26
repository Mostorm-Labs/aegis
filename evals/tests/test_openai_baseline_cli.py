import io
import os
import unittest
from unittest import mock

from evals.scripts.run_openai_baseline import main


class OpenAIBaselineCLITests(unittest.TestCase):
    def test_missing_api_key_returns_blocked_environment_before_live_work(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            code = main(["--output", "/tmp/aegis-baseline-test"])
        self.assertEqual(code, 3)
        self.assertIn("BLOCKED_ENVIRONMENT", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
