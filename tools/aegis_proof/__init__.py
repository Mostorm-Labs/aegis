"""Deterministic Verification Productization proof-runtime primitives."""

from .domain import EvidenceInputIdentity, ObligationIdentityCodec, ProofCodec, ProofValidationError
from .obligations import ObligationGenerator, ObligationSet
from .package import EvidenceContractPreflight, PackageBindingPreflight, P31TaskProjector
from .spec import ValidationFinding, ValidationResult, VerificationSpecValidator

__all__ = [
    "EvidenceInputIdentity",
    "ObligationGenerator",
    "ObligationIdentityCodec",
    "ObligationSet",
    "ProofCodec",
    "ProofValidationError",
    "EvidenceContractPreflight",
    "PackageBindingPreflight",
    "P31TaskProjector",
    "ValidationFinding",
    "ValidationResult",
    "VerificationSpecValidator",
]
