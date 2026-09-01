from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.control_plane.generate_cp_i06_p36_final_evidence import (
    CP_I05_DISPATCH_CASE_IDS,
    CP_I05_EVIDENCE_ARTIFACT_ID,
    CP_I05_MATERIALIZED_REF,
    CP_I05_REVISION,
    generate,
)


class CpI06P36CoverageTests(unittest.TestCase):
    def test_acknowledged_gap_is_direct_and_all_inherited_cases_exist_in_exact_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            manifest = generate(output, result_revision="c" * 40)
            self.assertTrue(manifest["passed"])
            coverage = manifest["p31_mandatory_coverage"]
            self.assertEqual(72, coverage["obligation_count"])
            self.assertTrue(coverage["passed"])

            gap = coverage["obligations"]["possible_acknowledged_commit_gap_blocks_continuation"]
            self.assertEqual("DIRECT_CP_I06", gap["mode"])
            self.assertEqual(
                "CPV-E-BACKUP-RESTORE::stale_valid_backup_missing_acknowledged_terminal_blocks_continuation",
                gap["case_id"],
            )

            backup = json.loads((output / "backup-restore.json").read_text(encoding="utf-8"))
            cases = {case["case"]: case for case in backup["cases"]}
            self.assertEqual(3, len(cases))
            gap_case = cases["stale_valid_backup_missing_acknowledged_terminal_blocks_continuation"]
            self.assertTrue(gap_case["passed"])
            self.assertTrue(gap_case["zero_residue"])
            self.assertEqual("CONTROL_LANE_SCHEDULE_CONFLICT", gap_case["rejection"])
            self.assertEqual("OPEN", gap_case["restored_state"])

            inherited = [
                (obligation, entry)
                for obligation, entry in coverage["obligations"].items()
                if entry["mode"] == "INHERITED_EXACT_PREDECESSOR"
            ]
            self.assertEqual(4, len(inherited))
            for obligation, entry in inherited:
                self.assertEqual(CP_I05_REVISION, entry["predecessor_revision"], obligation)
                self.assertEqual(CP_I05_EVIDENCE_ARTIFACT_ID, entry["artifact_id"], obligation)
                self.assertEqual(CP_I05_MATERIALIZED_REF, entry["materialized_ref"], obligation)
                self.assertEqual("dispatch-fault-matrix.json", entry["evidence_file"], obligation)
                self.assertIn(entry["case_id"], CP_I05_DISPATCH_CASE_IDS, obligation)

            repair = manifest["p36_repair"]
            self.assertTrue(repair["inherited_case_catalog_validated"])
            self.assertEqual(
                "stale_valid_backup_missing_acknowledged_terminal_blocks_continuation",
                repair["acknowledged_gap_direct_case"],
            )


if __name__ == "__main__":
    unittest.main()
