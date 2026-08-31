import ast
import inspect
import unittest
from pathlib import Path

from tools.aegis_control.store import ControlStore


class OwnershipTests(unittest.TestCase):
    def test_control_store_public_surface_is_read_only(self):
        public = {
            name for name, value in inspect.getmembers(ControlStore, inspect.isfunction)
            if not name.startswith("_")
        }
        self.assertEqual(
            {"read_latest", "read_revisions", "read_lane_head", "read_idempotency", "read_outbox", "snapshot_counts"},
            public,
        )

    def test_only_mutation_module_invokes_private_mutation_transaction(self):
        root = Path(__file__).resolve().parents[2] / "tools" / "aegis_control"
        callers = []
        for path in root.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr == "_mutation_transaction":
                        callers.append(path.name)
        self.assertEqual(["mutation.py"], sorted(callers))

    def test_raw_canonical_write_sql_exists_only_in_store(self):
        root = Path(__file__).resolve().parents[2] / "tools" / "aegis_control"
        markers = ("INSERT INTO canonical_records", "UPDATE lane_heads SET version")
        owners = set()
        for path in root.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            if any(marker in text for marker in markers):
                owners.add(path.name)
        self.assertEqual({"store.py"}, owners)

    def test_no_production_dispatch_or_network_path_exists_in_cp_i02_modules(self):
        root = Path(__file__).resolve().parents[2] / "tools" / "aegis_control"
        forbidden_imports = {"requests", "httpx", "urllib.request", "socket"}
        observed = set()
        for path in (root / "store.py", root / "mutation.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    observed.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    observed.add(node.module)
        self.assertTrue(forbidden_imports.isdisjoint(observed))


if __name__ == "__main__":
    unittest.main()
