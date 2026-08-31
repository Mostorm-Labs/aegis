"""Aegis Control Plane v0.2 bounded runtime primitives.

CP-I01 supplies canonical encoding/validation. CP-I02 adds the local durable
Control Store mechanics and the single canonical MutationService writer.
CP-I03 adds deterministic projection, fail-closed policy, and transient
scheduler candidates while preserving MutationService as the only writer.
CP-I04 adds bounded external-trust read ports and opaque snapshot guards;
remote dispatch and later Control Plane slices remain out of scope.
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
from .external_ports import (
    DeterministicExternalAdapter,
    ProviderCapability,
    SourceSnapshot,
)
from .mutation import MutationRejected, MutationService, semantic_fingerprint
from .policy import PolicyDecision, PolicyEvaluator
from .projection import (
    ControlCursor,
    ControlProjection,
    LifecycleSummary,
    ProjectionCache,
    ProjectionEngine,
)
from .scheduler import ScheduleCandidate, Scheduler, SchedulingDenied
from .snapshot import SnapshotVerification, SourceSnapshotTokenCodec
from .store import ControlStore, LaneHead, StoredRecord
from .trust import TrustFactRequest, TrustResolution, TrustResolver

__all__ = [
    "CanonicalValidationError",
    "ControlCursor",
    "ControlProjection",
    "ControlStore",
    "DeterministicExternalAdapter",
    "LaneHead",
    "LifecycleSummary",
    "MutationRejected",
    "MutationService",
    "PolicyDecision",
    "PolicyEvaluator",
    "ProjectionCache",
    "ProjectionEngine",
    "ProviderCapability",
    "ScheduleCandidate",
    "Scheduler",
    "SchedulingDenied",
    "SnapshotVerification",
    "SourceSnapshot",
    "SourceSnapshotTokenCodec",
    "StoredRecord",
    "TrustFactRequest",
    "TrustResolution",
    "TrustResolver",
    "canonical_digest",
    "canonical_dumps",
    "canonical_json_bytes",
    "semantic_fingerprint",
    "validate_canonical_ref",
    "validate_record",
    "validate_revision_lineage",
]
