"""Aegis Control Plane v0.2 bounded runtime primitives.

CP-I01 supplies canonical encoding/validation. CP-I02 adds the local durable
Control Store mechanics and the single canonical MutationService writer for
the authorized P13 subset. Scheduler, policy, projection, remote dispatch,
provider adapters, and service APIs remain outside this slice.
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
from .mutation import MutationRejected, MutationService, semantic_fingerprint
from .store import ControlStore, LaneHead, StoredRecord

__all__ = [
    "CanonicalValidationError",
    "ControlStore",
    "LaneHead",
    "MutationRejected",
    "MutationService",
    "StoredRecord",
    "canonical_digest",
    "canonical_dumps",
    "canonical_json_bytes",
    "semantic_fingerprint",
    "validate_canonical_ref",
    "validate_record",
    "validate_revision_lineage",
]
