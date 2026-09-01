import tempfile
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import make_request
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.store import ControlStore


class CpI06FoundationRedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ControlStore(str(Path(self.tmp.name) / "control.db"))
        self.mutation = MutationService(self.store)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cp_i06_semantic_operations_are_promoted_from_known_later_set(self):
        for operation_name in (
            "SCHEDULE_REPAIR_OCCURRENCE",
            "SCHEDULE_REVERIFICATION_OCCURRENCE",
            "SCHEDULE_REREVIEW_OCCURRENCE",
            "RECORD_ESCALATION_RESOLUTION",
        ):
            with self.subTest(operation_name=operation_name):
                result = self.mutation.apply(
                    make_request(operation_name, f"req_{operation_name.lower()}", "lane_cp_i06", {})
                )
                self.assertNotEqual(
                    "OPERATION_NOT_IMPLEMENTED_IN_THIS_SLICE",
                    result.get("reason"),
                    operation_name,
                )


if __name__ == "__main__":
    unittest.main()
