from __future__ import annotations

from copy import deepcopy

from tools.aegis_control.canonical import canonical_digest
from tools.aegis_control.dispatch import DispatchAuthorizationResolver
from tools.aegis_control.execution_surface import DeterministicExecutionSurface, ExecutionPositionResolver
from tools.aegis_control.external_ports import DeterministicExternalAdapter
from tools.aegis_control.mutation import MutationService
from tools.aegis_control.trust import ResultMaterializationRequest, TrustFactRequest, TrustResolver

TASK_ANCHOR = "a3fd350c350bec9220a1c6e283de88c14dfbcd2a"
PACKAGE_ID = "CP-I05-P31-01"
RESULT_REF = {
    "object_type": "RESULT",
    "id": "result_cp_i05",
    "ref": "github:artifact:cp-i05-result",
    "identity": {"scheme": "sha256", "value": "sha256:" + "1" * 64},
}
POLICY_REF = {
    "object_type": "CONTRACT",
    "id": "contract_cp_i05_dispatch_current",
    "ref": "control:dispatch-policy:current",
    "identity": {"scheme": "sha256", "value": "sha256:" + "8" * 64},
}


def navigation(execution_ref: str, revision: str, *, next_action: str = "review"):
    return {
        "execution_surface": "CODE_EXECUTION",
        "task_anchor": {"revision": TASK_ANCHOR, "relation": "ancestor"},
        "execution_cursor": {
            "execution_ref": execution_ref,
            "revision": revision,
            "completed_through": ["implementation"],
            "next_action": next_action,
        },
    }


def seed_surface(
    surface: DeterministicExecutionSurface,
    *,
    occurrence_id: str,
    execution_ref: str,
    revision: str = "exec-r1",
    state: str = "RUNNING",
    completed_through=("implementation",),
    next_action: str = "review",
    correlation_id: str | None = None,
):
    return surface.seed_execution(
        occurrence_id=occurrence_id,
        correlation_id=correlation_id or f"corr_{occurrence_id}",
        execution_ref=execution_ref,
        revision=revision,
        state=state,
        completed_through=completed_through,
        next_action=next_action,
    )


def result_trust(
    *,
    occurrence_id: str,
    result_ref=RESULT_REF,
    resolved_ref=None,
    ambiguous: bool = False,
    satisfies: bool = True,
):
    adapter = DeterministicExternalAdapter(
        source_kind="result-store",
        adapter_id="cp-i05-result",
        secret=b"cp-i05-result-secret",
        callback_available=False,
        query_correlation_available=True,
    )
    adapter.set_resource(
        "result-current",
        version_scheme=result_ref["identity"]["scheme"],
        version_value=result_ref["identity"]["value"],
        resolved_refs=[deepcopy(resolved_ref or result_ref)],
        satisfies=satisfies,
        ambiguous=ambiguous,
    )
    request = ResultMaterializationRequest(
        source_kind="result-store",
        resource_key="result-current",
        occurrence_id=occurrence_id,
        package_id=PACKAGE_ID,
        task_anchor_revision=TASK_ANCHOR,
    )
    return TrustResolver(
        {"result-store": adapter},
        result_sources={canonical_digest(result_ref): request},
    )


def configured_mutation(store, surface, *, result_resolver=None):
    position = ExecutionPositionResolver(
        authorized_task_anchor=TASK_ANCHOR,
        current_revision=surface.current_revision,
        is_ancestor=surface.is_ancestor,
    )
    return MutationService(
        store,
        trust_resolver=result_resolver,
        execution_position_resolver=position,
        implementation_package_id=PACKAGE_ID,
        task_anchor_revision=TASK_ANCHOR,
    )


def policy_trust(*, satisfies: bool = True):
    adapter = DeterministicExternalAdapter(
        source_kind="control-policy",
        adapter_id="cp-i05-policy",
        secret=b"cp-i05-policy-secret",
        callback_available=False,
        query_correlation_available=True,
    )
    adapter.set_resource(
        "dispatch-current",
        version_scheme="sha256",
        version_value=POLICY_REF["identity"]["value"],
        resolved_refs=[POLICY_REF],
        satisfies=satisfies,
    )
    return TrustResolver({"control-policy": adapter})


def dispatch_authorization(*, satisfies: bool = True, source_primary_owner: str = "aegis-implementation"):
    return DispatchAuthorizationResolver(
        policy_trust(satisfies=satisfies),
        TrustFactRequest("control-policy", "dispatch-current"),
        source_primary_owner=source_primary_owner,
    )
