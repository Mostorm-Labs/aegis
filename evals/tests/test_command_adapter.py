import json
import sys
import unittest

from evals.scripts.aegis_eval.adapters import CommandAdapter


class CommandAdapterTests(unittest.TestCase):
    def test_command_adapter_sends_case_json_on_stdin(self):
        script = (
            "import json,sys; c=json.load(sys.stdin); "
            "print(json.dumps({'status':'READY','start_stage':'P00','route':['P00'],"
            "'findings':[c['id']]}))"
        )
        adapter = CommandAdapter([sys.executable, "-c", script])
        raw = adapter.run({"id": "routing-001", "input": {"prompt": "x", "context": []}})
        payload = json.loads(raw)
        self.assertEqual(payload["status"], "READY")
        self.assertEqual(payload["findings"], ["routing-001"])


if __name__ == "__main__":
    unittest.main()
