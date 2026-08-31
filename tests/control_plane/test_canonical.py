import math
import unittest

from tools.aegis_control.canonical import (
    CanonicalValidationError,
    canonical_digest,
    canonical_dumps,
    validate_canonical_ref,
    validate_record,
    validate_revision_lineage,
)


class CanonicalSemanticsTests(unittest.TestCase):
    def test_orders_object_keys_and_preserves_utf8(self):
        value = {"z": 1, "a": "雪", "nested": {"b": True, "a": None}}
        self.assertEqual(canonical_dumps(value), '{"a":"雪","nested":{"a":null,"b":true},"z":1}')

    def test_uses_utf16_property_sort_order(self):
        value = {"\u20ac": 1, "\r": 2, "\ufb33": 3, "1": 4, "😀": 5, "\u0080": 6, "ö": 7}
        self.assertEqual(canonical_dumps(value), '{"\\r":2,"1":4,"\u0080":6,"ö":7,"€":1,"😀":5,"דּ":3}')

    def test_escapes_json_strings_deterministically(self):
        value = {"s": 'quote" slash\\ controls\b\t\n\f\r'}
        self.assertEqual(canonical_dumps(value), '{"s":"quote\\\" slash\\\\ controls\\b\\t\\n\\f\\r"}')

    def test_canonicalizes_supported_numbers(self):
        vectors = {0: "0", -0.0: "0", 1.0: "1", 1e-6: "0.000001", 1e-7: "1e-7", 1e20: "100000000000000000000", 1e21: "1e+21", 4.5: "4.5"}
        for value, expected in vectors.items():
            with self.subTest(value=value):
                self.assertEqual(canonical_dumps(value), expected)
        with self.assertRaises(CanonicalValidationError):
            canonical_dumps(math.inf)
        with self.assertRaises(CanonicalValidationError):
            canonical_dumps(math.nan)

    def test_digest_is_deterministic_and_can_exclude_own_field(self):
        record = {"id": "x", "payload": {"b": 2, "a": 1}, "record_digest": "ignored"}
        first = canonical_digest(record, self_digest_field="record_digest")
        second = canonical_digest({"payload": {"a": 1, "b": 2}, "id": "x"})
        self.assertEqual(first, second)
        self.assertRegex(first, r"^sha256:[0-9a-f]{64}$")

    def test_rejects_unknown_top_level_record_fields(self):
        record = {"schema_version": "0.2", "kind": "STAGE_OCCURRENCE", "id_scheme": "stage-occurrence-v0.2", "id": "so_018f47b0-5d89-7baf-8c0a-111111111111", "record_revision": 1, "recorded_at": "2026-08-31T00:00:00Z", "control_lane_id": "lane_018f47b0-5d89-7baf-8c0a-222222222222", "stage_span": {"stages": ["P32"]}, "primary_owner": "aegis-implementation", "state": "OPEN", "trusted_basis": {}, "policy_binding": {}, "schedule_basis": {}, "input_refs": [], "repair_context": None, "execution_navigation": None, "terminal": None, "extensions": {}, "surprise": True}
        with self.assertRaisesRegex(CanonicalValidationError, "unknown top-level"):
            validate_record(record)

    def test_validates_exact_canonical_ref(self):
        ref = {"object_type": "RESULT", "id": "result-1", "ref": "git:abc123", "identity": {"scheme": "git-sha", "value": "a" * 40}}
        validate_canonical_ref(ref)
        bad = dict(ref)
        bad["identity"] = {"scheme": "git-sha"}
        with self.assertRaises(CanonicalValidationError):
            validate_canonical_ref(bad)

    def test_validates_immutable_revision_lineage(self):
        base = {"schema_version": "0.2", "kind": "STAGE_OCCURRENCE", "id_scheme": "stage-occurrence-v0.2", "id": "so_018f47b0-5d89-7baf-8c0a-111111111111", "recorded_at": "2026-08-31T00:00:00Z", "control_lane_id": "lane_018f47b0-5d89-7baf-8c0a-222222222222", "stage_span": {"stages": ["P32"]}, "primary_owner": "aegis-implementation", "trusted_basis": {}, "policy_binding": {}, "schedule_basis": {}, "input_refs": [], "repair_context": None, "execution_navigation": None, "extensions": {}}
        open_record = dict(base, record_revision=1, state="OPEN", terminal=None)
        terminal_record = dict(base, record_revision=2, state="TERMINAL", terminal={"outcome_category": "COMPLETED", "status": "READY"})
        validate_revision_lineage([open_record, terminal_record])
        with self.assertRaisesRegex(CanonicalValidationError, "contiguous"):
            validate_revision_lineage([open_record, dict(terminal_record, record_revision=3)])


if __name__ == "__main__":
    unittest.main()
