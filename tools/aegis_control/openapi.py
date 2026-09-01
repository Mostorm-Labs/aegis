from __future__ import annotations


def build_openapi_contract() -> dict:
    json_content = {"application/json": {"schema": {"type": "object"}}}
    return {
        "openapi": "3.1.0",
        "info": {"title": "Aegis Control Service", "version": "v1"},
        "paths": {
            "/v1/operations": {
                "post": {
                    "operationId": "submitOperation",
                    "parameters": [
                        {"name": "Idempotency-Key", "in": "header", "required": True, "schema": {"type": "string"}},
                        {"name": "X-Aegis-Protocol-Version", "in": "header", "required": True, "schema": {"const": "v1"}},
                    ],
                    "requestBody": {"required": True, "content": json_content},
                    "responses": {"200": {"description": "Operation result"}},
                }
            },
            "/v1/work-scopes/{work_scope_id}/control": {"get": {"operationId": "getControlProjection", "responses": {"200": {"description": "Projection DTO"}}}},
            "/internal/v1/outbox/claim": {"post": {"operationId": "claimOutbox", "responses": {"200": {"description": "Operational outbox claims"}}}},
            "/internal/v1/outbox/{entry}/attempts": {"post": {"operationId": "recordDeliveryAttempt", "responses": {"200": {"description": "Operational metadata only"}}}},
            "/internal/v1/occurrences/{occurrence_id}/reconcile": {"post": {"operationId": "requestReconciliation", "responses": {"202": {"description": "Reconciliation requested"}}}},
            "/internal/v1/provider-observations": {"post": {"operationId": "submitProviderObservation", "responses": {"202": {"description": "Observation accepted for reconciliation"}}}},
        },
        "x-aegis-contract": {
            "canonical_writer": "control-mutation",
            "idempotency_identity": "Idempotency-Key == operation_request_id",
            "current_cross_primary_rollout": "DENIED",
            "worker_canonical_write": False,
        },
    }
