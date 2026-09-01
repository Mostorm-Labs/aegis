from __future__ import annotations

import unittest


class CpI07OpenApiRedTests(unittest.TestCase):
    def test_openapi_declares_public_and_internal_boundaries_without_generic_patch(self):
        from tools.aegis_control.openapi import build_openapi_contract
        spec = build_openapi_contract(); self.assertEqual("3.1.0", spec["openapi"])
        paths = spec["paths"]
        self.assertIn("post", paths["/v1/operations"])
        self.assertIn("post", paths["/internal/v1/outbox/claim"])
        self.assertIn("post", paths["/internal/v1/occurrences/{occurrence_id}/reconcile"])
        for path, operations in paths.items(): self.assertNotIn("patch", operations, path)


if __name__ == "__main__": unittest.main()
