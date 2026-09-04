from __future__ import annotations

import unittest


class CpI07WorkerApiRedTests(unittest.TestCase):
    def test_worker_api_surface_has_only_operational_capabilities(self):
        from tools.aegis_control.capabilities import WorkerControlPort
        names = {name for name in dir(WorkerControlPort) if not name.startswith("_")}
        self.assertTrue({"claim_ready_outbox","record_delivery_attempt","request_reconciliation","submit_provider_observation","query_platform_capability"}.issubset(names))
        for forbidden in {"append_canonical","advance_lane","set_terminal","set_gate_verdict"}:
            self.assertNotIn(forbidden, names)


if __name__ == "__main__": unittest.main()
