import unittest

from tests.verification_productization.ecv0_fixtures import run_mutant


class ECV0MutantTests(unittest.TestCase):
    def test_EC_M01(self): self.assertTrue(run_mutant("EC-M01"))
    def test_EC_M02(self): self.assertTrue(run_mutant("EC-M02"))
    def test_EC_M03(self): self.assertTrue(run_mutant("EC-M03"))
    def test_EC_M04(self): self.assertTrue(run_mutant("EC-M04"))
    def test_EC_M05(self): self.assertTrue(run_mutant("EC-M05"))
    def test_EC_M06(self): self.assertTrue(run_mutant("EC-M06"))
    def test_EC_M07(self): self.assertTrue(run_mutant("EC-M07"))
    def test_EC_M08(self): self.assertTrue(run_mutant("EC-M08"))
    def test_EC_M09(self): self.assertTrue(run_mutant("EC-M09"))
    def test_EC_M10(self): self.assertTrue(run_mutant("EC-M10"))
    def test_EC_M11(self): self.assertTrue(run_mutant("EC-M11"))
    def test_EC_M12(self): self.assertTrue(run_mutant("EC-M12"))
    def test_EC_M13(self): self.assertTrue(run_mutant("EC-M13"))
    def test_EC_M14(self): self.assertTrue(run_mutant("EC-M14"))
    def test_EC_M15(self): self.assertTrue(run_mutant("EC-M15"))
    def test_EC_M16(self): self.assertTrue(run_mutant("EC-M16"))
    def test_EC_M17(self): self.assertTrue(run_mutant("EC-M17"))


if __name__ == "__main__":
    unittest.main()
