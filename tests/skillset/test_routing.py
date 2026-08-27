import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class RoutingTests(unittest.TestCase):
    def test_routing_module_exists(self):
        self.assertTrue((ROOT/'tools/aegis_skillset/routing.py').is_file())

    def test_protected_routing_corpus_is_valid(self):
        self.assertTrue((ROOT/'tools/aegis_skillset/routing.py').is_file())
        from tools.aegis_skillset.routing import validate_routing_corpus
        self.assertEqual([], validate_routing_corpus(ROOT))

if __name__=='__main__': unittest.main()
