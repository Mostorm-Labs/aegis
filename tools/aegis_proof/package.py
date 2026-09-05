"""Exact P31 package projection and evidence-contract satisfiability preflight."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from tools.aegis_control.canonical import (
    CanonicalValidationError,
    validate_canonical_ref,
    validate_trusted_basis,
)

from .domain import ProofValidationError


class PreflightCode(str, Enum):
    FLOATING_DEPENDENCY = "FLOATING_DEPENDENCY"
    INVALID_EXACT_REF = "INVALID_EXACT_REF"
    MISSING_OBLIGATION_SET = "MISSING_OBLIGATION_SET"
    INVALID_TASK_ANCHOR = "INVALID_TASK_ANCHOR"
    STRUCTURALLY_UNSATISFIABLE = "STRUCTURALLY_UNSATISFIABLE"
    FUTURE_PHASE_DEPENDENCY = "FUTURE_PHASE_DEPENDENCY"
    UNKNOWN_DEPENDENCY = "UNKNOWN_DEPENDENCY"
    INVALID_PHASE = "INVALID_PHASE"
    UNRESOLVED_SEMANTIC_CHOICE = "UNRESOLVED_SEMANTIC_CHOICE"


@dataclass(frozen=True)
class PreflightFinding:
    code: PreflightCode
    message: str
    subject: str


@dataclass(frozen=True)
class PreflightResult:
    ok: bool
    findings: tuple[PreflightFinding, ...]


_FLOATING_PHRASES = (
    "accepted a4",
    "latest gate",
    "latest run",
    "current result",
    "previous accepted baseline",
)
_MUTABLE_IDENTITY_SCHEMES = {"label", "branch", "mutable", "latest", "human-label"}


def _contains_floating(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return any(phrase in lowered for phrase in _FLOATING_PHRASES)
    if isinstance(value, Mapping):
        identity = value.get("identity")
        if isinstance(identity, Mapping) and identity.get("scheme") in _MUTABLE_IDENTITY_SCHEMES:
            return True
        return any(_contains_floating(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_floating(item) for item in value)
    return False


def _check_ref(
    value: Any,
    *,
    object_types: set[str],
    subject: str,
    findings: list[PreflightFinding],
) -> None:
    if _contains_floating(value):
        findings.append(
            PreflightFinding(
                PreflightCode.FLOATING_DEPENDENCY,
                "floating or mutable dependency cannot cross the executable trust boundary",
                subject,
            )
        )
        return
    try:
        validate_canonical_ref(value)
    except CanonicalValidationError as exc:
        findings.append(PreflightFinding(PreflightCode.INVALID_EXACT_REF, str(exc), subject))
        return
    if value.get("object_type") not in object_types:
        findings.append(
            PreflightFinding(
                PreflightCode.INVALID_EXACT_REF,
                f"expected object_type in {sorted(object_types)}",
                subject,
            )
        )


class P31TaskProjector:
    @staticmethod
    def project(
        *,
        exact_verification_spec_ref: Mapping[str, Any],
        exact_obligation_set_ref: Mapping[str, Any] | None,
        exact_scope_contract_ref: Mapping[str, Any],
        exact_acceptance_oracle_refs: Sequence[Mapping[str, Any]],
        exact_evidence_compilation_contract_ref: Mapping[str, Any],
        exact_trusted_basis: Mapping[str, Any],
        task_anchor: Mapping[str, Any] | None,
        obligation_set_required: bool = True,
    ) -> dict[str, Any]:
        projection = {
            "verification_spec_ref": exact_verification_spec_ref,
            "obligation_set_ref": exact_obligation_set_ref,
            "obligation_set_required": obligation_set_required,
            "scope_contract_ref": exact_scope_contract_ref,
            "acceptance_oracle_refs": list(exact_acceptance_oracle_refs),
            "evidence_compilation_contract_ref": exact_evidence_compilation_contract_ref,
            "trusted_basis": exact_trusted_basis,
            "task_anchor": task_anchor,
        }
        result = PackageBindingPreflight.check(projection)
        if not result.ok:
            codes = ",".join(f.code.value for f in result.findings)
            raise ProofValidationError(f"package projection failed preflight: {codes}")
        return projection


class PackageBindingPreflight:
    @staticmethod
    def check(projection: Mapping[str, Any]) -> PreflightResult:
        findings: list[PreflightFinding] = []
        _check_ref(
            projection.get("verification_spec_ref"),
            object_types={"VERIFICATION_SPEC"},
            subject="verification_spec_ref",
            findings=findings,
        )
        obligation_ref = projection.get("obligation_set_ref")
        if obligation_ref is None:
            if projection.get("obligation_set_required", True):
                findings.append(
                    PreflightFinding(
                        PreflightCode.MISSING_OBLIGATION_SET,
                        "exact obligation_set_ref is required by the governing contract",
                        "obligation_set_ref",
                    )
                )
        else:
            _check_ref(
                obligation_ref,
                object_types={"PROOF_OBLIGATION_SET"},
                subject="obligation_set_ref",
                findings=findings,
            )
        _check_ref(
            projection.get("scope_contract_ref"),
            object_types={"CONTRACT"},
            subject="scope_contract_ref",
            findings=findings,
        )
        oracles = projection.get("acceptance_oracle_refs")
        if not isinstance(oracles, list) or not oracles:
            findings.append(
                PreflightFinding(
                    PreflightCode.INVALID_EXACT_REF,
                    "acceptance_oracle_refs must be a non-empty exact-ref list",
                    "acceptance_oracle_refs",
                )
            )
        else:
            for index, oracle in enumerate(oracles):
                _check_ref(
                    oracle,
                    object_types={"CONTRACT"},
                    subject=f"acceptance_oracle_refs[{index}]",
                    findings=findings,
                )
        _check_ref(
            projection.get("evidence_compilation_contract_ref"),
            object_types={"CONTRACT"},
            subject="evidence_compilation_contract_ref",
            findings=findings,
        )
        try:
            validate_trusted_basis(projection.get("trusted_basis"))
        except CanonicalValidationError as exc:
            findings.append(PreflightFinding(PreflightCode.INVALID_EXACT_REF, str(exc), "trusted_basis"))
        if _contains_floating(projection.get("trusted_basis")):
            findings.append(
                PreflightFinding(
                    PreflightCode.FLOATING_DEPENDENCY,
                    "TrustedBasis contains a floating dependency",
                    "trusted_basis",
                )
            )
        anchor = projection.get("task_anchor")
        if anchor is not None:
            if (
                not isinstance(anchor, Mapping)
                or set(anchor) != {"revision", "relation"}
                or anchor.get("relation") != "ancestor"
                or not isinstance(anchor.get("revision"), str)
                or not anchor.get("revision")
            ):
                findings.append(
                    PreflightFinding(
                        PreflightCode.INVALID_TASK_ANCHOR,
                        "repository task_anchor requires exact revision + ancestor relation",
                        "task_anchor",
                    )
                )
        return PreflightResult(not findings, tuple(findings))


class EvidenceContractPreflight:
    PHASES = (
        "P31_FREEZE",
        "P32_EXECUTION",
        "EVIDENCE_COMPILE",
        "ARTIFACT_MATERIALIZE",
        "RESULT_MATERIALIZE",
        "P34_REVIEW",
    )
    PHASE_INDEX = {phase: index for index, phase in enumerate(PHASES)}

    @classmethod
    def check(cls, nodes: Sequence[Mapping[str, Any]]) -> PreflightResult:
        findings: list[PreflightFinding] = []
        by_id: dict[str, Mapping[str, Any]] = {}
        for index, node in enumerate(nodes):
            node_id = node.get("id") if isinstance(node, Mapping) else None
            phase = node.get("phase") if isinstance(node, Mapping) else None
            if not isinstance(node_id, str) or not node_id:
                findings.append(
                    PreflightFinding(PreflightCode.UNKNOWN_DEPENDENCY, "dependency node id is required", f"nodes[{index}]")
                )
                continue
            if node_id in by_id:
                findings.append(
                    PreflightFinding(PreflightCode.STRUCTURALLY_UNSATISFIABLE, "duplicate dependency node id", node_id)
                )
                continue
            if phase not in cls.PHASE_INDEX:
                findings.append(PreflightFinding(PreflightCode.INVALID_PHASE, "unknown evidence phase", node_id))
            by_id[node_id] = node

        graph: dict[str, list[str]] = {}
        for node_id, node in by_id.items():
            deps = node.get("depends_on", [])
            if not isinstance(deps, list) or any(not isinstance(dep, str) or not dep for dep in deps):
                findings.append(
                    PreflightFinding(PreflightCode.UNKNOWN_DEPENDENCY, "depends_on must be a string list", node_id)
                )
                deps = []
            graph[node_id] = list(deps)
            if node.get("required_exact") and node.get("identity_kind") == "mutable":
                findings.append(
                    PreflightFinding(PreflightCode.INVALID_EXACT_REF, "required exact identity is provider-mutable", node_id)
                )
            if node.get("semantic_choice_resolved") is False:
                findings.append(
                    PreflightFinding(
                        PreflightCode.UNRESOLVED_SEMANTIC_CHOICE,
                        "semantic choice must be resolved by the owning earlier layer",
                        node_id,
                    )
                )
            for dep in deps:
                if dep not in by_id:
                    findings.append(
                        PreflightFinding(PreflightCode.UNKNOWN_DEPENDENCY, f"unknown dependency {dep}", node_id)
                    )
                    continue
                node_phase = node.get("phase")
                dep_phase = by_id[dep].get("phase")
                if node_phase in cls.PHASE_INDEX and dep_phase in cls.PHASE_INDEX:
                    if cls.PHASE_INDEX[dep_phase] > cls.PHASE_INDEX[node_phase]:
                        findings.append(
                            PreflightFinding(
                                PreflightCode.FUTURE_PHASE_DEPENDENCY,
                                f"{node_id} requires future-phase value {dep}",
                                node_id,
                            )
                        )

        visiting: set[str] = set()
        visited: set[str] = set()
        cycle_nodes: set[str] = set()

        def visit(node_id: str, stack: list[str]) -> None:
            if node_id in visited:
                return
            if node_id in visiting:
                if node_id in stack:
                    cycle_nodes.update(stack[stack.index(node_id):])
                else:
                    cycle_nodes.add(node_id)
                return
            visiting.add(node_id)
            stack.append(node_id)
            for dep in graph.get(node_id, []):
                if dep in graph:
                    visit(dep, stack)
            stack.pop()
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in graph:
            visit(node_id, [])
        if cycle_nodes:
            findings.append(
                PreflightFinding(
                    PreflightCode.STRUCTURALLY_UNSATISFIABLE,
                    f"circular evidence dependency has no externally fixed anchor: {sorted(cycle_nodes)}",
                    ",".join(sorted(cycle_nodes)),
                )
            )
        return PreflightResult(not findings, tuple(findings))
