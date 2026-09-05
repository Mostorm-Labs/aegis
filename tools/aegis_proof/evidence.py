from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence
from .ports import ArtifactStorePort, ObservationBatch

@dataclass(frozen=True)
class EvidenceRequirement:
    fact_key: str
    authoritative_producer: str
    required: bool

@dataclass(frozen=True)
class EvidencePlan:
    requirements: tuple[EvidenceRequirement, ...]

class EvidencePlanBuilder:
    def build(self, *, verification_spec: Mapping[str, Any], obligation_set: Mapping[str, Any], evidence_compilation_contract: Mapping[str, Any]) -> EvidencePlan:
        source = evidence_compilation_contract.get("requirements", ())
        requirements = tuple(EvidenceRequirement(str(i["fact_key"]), str(i["authoritative_producer"]), bool(i.get("required", True))) for i in source)
        return EvidencePlan(requirements)

class EvidenceCompiler:
    def compile(self, *, plan: EvidencePlan, batches: Sequence[ObservationBatch]) -> Mapping[str, Any]:
        by_producer = {batch.producer_id: batch for batch in batches}
        facts: dict[str, Any] = {}
        conflicts: list[dict[str, Any]] = []
        missing: list[str] = []
        for requirement in plan.requirements:
            batch = by_producer.get(requirement.authoritative_producer)
            matching = [] if batch is None else [o for o in batch.observations if o.fact_key == requirement.fact_key]
            if batch is None or not batch.complete or not matching:
                if requirement.required:
                    missing.append(requirement.fact_key)
                continue
            authoritative = matching[-1]
            facts[requirement.fact_key] = authoritative.value
            for other in batches:
                if other.producer_id == requirement.authoritative_producer:
                    continue
                for observation in other.observations:
                    if observation.fact_key == requirement.fact_key and observation.value != authoritative.value:
                        conflicts.append({"fact_key": requirement.fact_key, "producer_id": other.producer_id, "value": observation.value})
        return {"facts": facts, "missing_required": sorted(set(missing)), "conflicts": conflicts, "complete": not missing}

class EvidenceMaterializer:
    def materialize(self, evidence_artifact: Mapping[str, Any], *, store: ArtifactStorePort) -> Mapping[str, Any]:
        payload = json.dumps(evidence_artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        locator = store.materialize(payload, media_type="application/vnd.aegis.evidence+json", metadata={"kind": "EvidenceArtifact"})
        if not locator.reviewer_resolvable:
            raise ValueError("materialized evidence must be reviewer-resolvable")
        digest = "sha256:" + hashlib.sha256(payload).hexdigest()
        if locator.digest != digest:
            raise ValueError("artifact locator digest mismatch")
        return {
            "evidence_id": f"evidence:{locator.native_id}",
            "ref": locator.ref,
            "digest": locator.digest,
            "producer_class": "DETERMINISTIC_COLLECTOR",
            "subject_result_revision": evidence_artifact.get("subject_result_revision"),
            "provider": locator.provider,
            "native_id": locator.native_id,
            "reviewer_resolvable": True,
        }
