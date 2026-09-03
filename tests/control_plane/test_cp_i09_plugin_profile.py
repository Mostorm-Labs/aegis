import unittest

from tests.control_plane.cp_i09_plugin_profile import qualify_pp0


class CpI09PluginProfileQualificationTests(unittest.TestCase):
    def test_pp0_exact_40_workscope_contract_is_implemented(self):
        result = qualify_pp0()
        self.assertTrue(result["implemented"], result["reason"])


if __name__ == "__main__":
    unittest.main()
