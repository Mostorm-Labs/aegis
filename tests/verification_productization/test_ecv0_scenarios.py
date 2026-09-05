import unittest

from tests.verification_productization.ecv0_fixtures import run_scenario


class ECV0ScenarioTests(unittest.TestCase):
    def test_EC_S01(self): self.assertTrue(run_scenario("EC-S01"))
    def test_EC_S02(self): self.assertTrue(run_scenario("EC-S02"))
    def test_EC_S03(self): self.assertTrue(run_scenario("EC-S03"))
    def test_EC_S04(self): self.assertTrue(run_scenario("EC-S04"))
    def test_EC_S05(self): self.assertTrue(run_scenario("EC-S05"))
    def test_EC_S06(self): self.assertTrue(run_scenario("EC-S06"))
    def test_EC_S07(self): self.assertTrue(run_scenario("EC-S07"))
    def test_EC_S08(self): self.assertTrue(run_scenario("EC-S08"))
    def test_EC_S09(self): self.assertTrue(run_scenario("EC-S09"))
    def test_EC_S10(self): self.assertTrue(run_scenario("EC-S10"))
    def test_EC_S11(self): self.assertTrue(run_scenario("EC-S11"))
    def test_EC_S12(self): self.assertTrue(run_scenario("EC-S12"))
    def test_EC_S13(self): self.assertTrue(run_scenario("EC-S13"))
    def test_EC_S14(self): self.assertTrue(run_scenario("EC-S14"))
    def test_EC_S15(self): self.assertTrue(run_scenario("EC-S15"))
    def test_EC_S16(self): self.assertTrue(run_scenario("EC-S16"))
    def test_EC_S17(self): self.assertTrue(run_scenario("EC-S17"))


if __name__ == "__main__":
    unittest.main()
