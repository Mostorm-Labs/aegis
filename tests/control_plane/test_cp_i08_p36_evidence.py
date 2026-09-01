from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


class CpI08P36EvidenceRedTests(unittest.TestCase):
    def test_every_g_binding_materializes_exact_workflow_run_and_job_identity(self):
        from tests.control_plane.generate_cp_i08_evidence import materialize_evidence
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            materialize_evidence(
                result_revision="f" * 40,
                output_dir=root,
                workflow_run="run-exact",
                workflow_job="verify",
            )
            import json
            d0 = json.loads((root / "d0-conformance.json").read_text(encoding="utf-8"))
            self.assertEqual(44, len(d0["golden_results"]))
            for gid, result in d0["golden_results"].items():
                self.assertEqual("run-exact", result["execution"]["workflow_run"], gid)
                self.assertEqual("verify", result["execution"]["workflow_job"], gid)
                self.assertTrue(result["test_id"], gid)


if __name__ == "__main__": unittest.main()
