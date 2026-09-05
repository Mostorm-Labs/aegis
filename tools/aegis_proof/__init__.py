"""Deterministic Verification Productization proof-runtime primitives."""

from .domain import EvidenceInputIdentity, ObligationIdentityCodec, ProofCodec, ProofValidationError
from .obligations import ObligationGenerator, ObligationSet
from .package import EvidenceContractPreflight, PackageBindingPreflight, P31TaskProjector
from .spec import ValidationFinding, ValidationResult, VerificationSpecValidator
from .ports import (
    ArtifactStorePort,
    ExactRefResolverPort,
    ImmutableArtifactLocator,
    ObservationBatch,
    ObservationRecord,
    ResultMaterializationPort,
)
from .evidence import EvidenceCompiler, EvidenceMaterializer, EvidencePlan, EvidencePlanBuilder, EvidenceRequirement
from .evaluation import EvaluationResult, ProofEvaluator
from .review import CompletenessResult, IndependentCompletenessChecker, ReviewBundleAdapter, ReviewContractDiffer, ReviewDelta

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
    "ObservationRecord",
    "ObservationBatch",
    "ImmutableArtifactLocator",
    "ArtifactStorePort",
    "ExactRefResolverPort",
    "ResultMaterializationPort",
    "EvidenceRequirement",
    "EvidencePlan",
    "EvidencePlanBuilder",
    "EvidenceCompiler",
    "EvidenceMaterializer",
    "EvaluationResult",
    "ProofEvaluator",
    "ReviewDelta",
    "CompletenessResult",
    "IndependentCompletenessChecker",
    "ReviewContractDiffer",
    "ReviewBundleAdapter",
]
