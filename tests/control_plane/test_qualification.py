import json
import unittest

import evidence_manifest
import qualification


class QualificationTests(unittest.TestCase):
    def test_all_mandatory_mutants_detected_without_false_acceptance(self):
        result = qualification.run_qualification()
        self.assertEqual(result["mandatory_total"], 20)
        self.assertEqual(result["detected"], 20)
        self.assertEqual(result["false_acceptance"], 0)
        self.assertEqual(set(result["results"]), {f"M{i:02d}" for i in range(1, 21)})
        self.assertTrue(all(item["detected"] for item in result["results"].values()))

    def test_evidence_manifest_has_required_exact_provenance(self):
        manifest = evidence_manifest.build_manifest(result_revision="a" * 40, package_ref="e8b2fa8c2bd29778a6a3c8bf5beb3d65ff9c364c", commands=["python3 -m unittest discover -s tests/control_plane -v"])
        self.assertEqual(manifest["task_id"], "CP-I01-P31-01")
        self.assertEqual(manifest["qualification"]["detected"], 20)
        self.assertEqual(manifest["qualification"]["false_acceptance"], 0)
        self.assertIn("fixture_catalog_digest", manifest)
        self.assertIn("mutant_catalog_digest", manifest)
        self.assertIn("canonical_golden_vector_digest", manifest)
        self.assertEqual(len(manifest["snapshot_mutant_provenance"]), 3)
        self.assertIn("full_canonical_digest", manifest["m20_provenance"])
        self.assertIn("truncated_digest", manifest["m20_provenance"])
        json.dumps(manifest, sort_keys=True)

    def test_manifest_catalog_digests_are_repeatable(self):
        a = evidence_manifest.build_manifest("b" * 40, "pkg", ["cmd"])
        b = evidence_manifest.build_manifest("b" * 40, "pkg", ["cmd"])
        for key in ("fixture_catalog_digest", "mutant_catalog_digest", "canonical_golden_vector_digest"):
            self.assertEqual(a[key], b[key])


if __name__ == "__main__":
    unittest.main()
