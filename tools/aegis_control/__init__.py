"""Pure Control Plane semantic primitives for CP-I01.

This package intentionally contains no scheduler, mutation, store, policy,
dispatch, recovery, or service control flow.
"""

from .canonical import (
    CanonicalValidationError,
    canonical_digest,
    canonical_dumps,
    canonical_json_bytes,
    validate_canonical_ref,
    validate_record,
    validate_revision_lineage,
)

__all__ = [
    "CanonicalValidationError",
    "canonical_digest",
    "canonical_dumps",
    "canonical_json_bytes",
    "validate_canonical_ref",
    "validate_record",
    "validate_revision_lineage",
]
