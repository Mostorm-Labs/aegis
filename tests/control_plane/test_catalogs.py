import unittest

import catalogs


class CatalogTests(unittest.TestCase):
    def test_g01_g44_are_present_exactly_once(self):
        self.assertEqual(list(catalogs.GOLDEN_SCENARIOS), [f"G{i:02d}" for i in range(1, 45)])
        self.assertEqual(len(catalogs.GOLDEN_SCENARIOS), 44)

    def test_m01_m20_are_present_exactly_once(self):
        self.assertEqual(list(catalogs.MANDATORY_MUTANTS), [f"M{i:02d}" for i in range(1, 21)])
        self.assertEqual(len(catalogs.MANDATORY_MUTANTS), 20)

    def test_catalog_digests_are_deterministic(self):
        self.assertEqual(catalogs.fixture_catalog_digest(), catalogs.fixture_catalog_digest())
        self.assertEqual(catalogs.mutant_catalog_digest(), catalogs.mutant_catalog_digest())
        self.assertRegex(catalogs.fixture_catalog_digest(), r"^sha256:[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
