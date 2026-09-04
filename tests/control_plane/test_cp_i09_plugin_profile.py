import copy, unittest

from tests.control_plane.cp_i09_plugin_profile import qualify_pp0, validate_workload


class CpI09PluginProfileQualificationTests(unittest.TestCase):
    def test_pp0_exact_40_workscope_contract_is_implemented(self):
        result = qualify_pp0()
        self.assertTrue(result["implemented"])
        self.assertEqual({k: 8 for k in "ABCDE"}, result["cohorts"])
        self.assertEqual(40, len(result["traces"]))
        self.assertTrue(all(v == 0 for v in result["metrics"].values()))
        self.assertEqual("DENIED", result["rollout"])
        self.assertFalse(result["p34_gate_pass"])

    def test_harness_fails_closed_on_contract_mutants(self):
        source = qualify_pp0()["manifest"]
        mutants = []
        m = copy.deepcopy(source); m["workscopes"].pop(); mutants.append(m)
        m = copy.deepcopy(source); m["workscopes"][1]["id"] = m["workscopes"][0]["id"]; mutants.append(m)
        m = copy.deepcopy(source); m["workscopes"][0]["seed"] = None; mutants.append(m)
        m = copy.deepcopy(source); m["interleavings"]["unrelated_lane"] = 7; mutants.append(m)
        m = copy.deepcopy(source); m["interleavings"]["same_lane_cas"] = 3; mutants.append(m)
        for index, mutant in enumerate(mutants):
            with self.subTest(index=index), self.assertRaises(ValueError): validate_workload(mutant)


if __name__ == "__main__":
    unittest.main()
