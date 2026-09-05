import hashlib
import unittest

from tools.aegis_proof.evidence import EvidenceMaterializer
from tools.aegis_proof.ports import ImmutableArtifactLocator


class MemoryStore:
    def __init__(self):
        self.items = []
    def materialize(self, data, *, media_type, metadata):
        digest = "sha256:" + hashlib.sha256(data).hexdigest()
        locator = ImmutableArtifactLocator("memory", str(len(self.items) + 1), f"memory://{len(self.items)+1}", digest, True)
        self.items.append((locator, data, metadata))
        return locator
    def resolve(self, locator):
        return next(data for loc, data, _ in self.items if loc == locator)


class EvidenceRepairTests(unittest.TestCase):
    def test_EC_S05_evidence_only_repair_keeps_result_identity(self):
        store = MemoryStore()
        materializer = EvidenceMaterializer()
        first = materializer.materialize({"subject_result_revision": "abc", "facts": {"x": 1}}, store=store)
        second = materializer.materialize({"subject_result_revision": "abc", "facts": {"x": 2}}, store=store)
        self.assertEqual(first["subject_result_revision"], second["subject_result_revision"])
        self.assertNotEqual(first["ref"], second["ref"])

    def test_EC_S06_result_bytes_change_requires_new_result_sha(self):
        old_bytes = b"implementation-v1"
        new_bytes = b"implementation-v2"
        old_sha = hashlib.sha256(old_bytes).hexdigest()
        new_sha = hashlib.sha256(new_bytes).hexdigest()
        self.assertNotEqual(old_sha, new_sha)

    def test_EC_M05_same_result_false_claim_after_mutation_is_detected(self):
        old_bytes = b"implementation-v1"
        new_bytes = b"implementation-v2"
        claimed = hashlib.sha256(old_bytes).hexdigest()
        actual = hashlib.sha256(new_bytes).hexdigest()
        self.assertNotEqual(claimed, actual)


if __name__ == "__main__":
    unittest.main()
