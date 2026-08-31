"""Deterministic M01-M20 verifier qualification runner."""

from __future__ import annotations

import catalogs
import reference_model as crm
import verifier_helpers as vh


_M01_M15_CASES = {
    "M01": ({"event_order": ["DISPATCH", "OPEN_OUTBOX_COMMIT"]}, "DISPATCH_BEFORE_COMMIT"),
    "M02": ({"delivery_occurrence_ids": ["so_1", "so_2"]}, "DELIVERY_CREATED_SEMANTIC_RETRY"),
    "M03": ({"canonical_writers": ["control-mutation", "direct-store-writer"]}, "SECOND_CANONICAL_WRITER"),
    "M04": ({"snapshot_accepted": True, "snapshot_version": "v1", "current_provider_version": "v2"}, "STALE_SNAPSHOT_ACCEPTED"),
    "M05": ({"required_child_ids": ["child"], "required_child_acceptance_bindings": [], "successor_scheduled": True}, "REQUIRED_CHILD_BARRIER_BYPASS"),
    "M06": ({"historical_basis_source": "CURRENT_PROJECTION"}, "HISTORICAL_FACT_FROM_CURRENT_PROJECTION"),
    "M07": ({"terminal_and_successor_same_transaction": True}, "TERMINAL_SUCCESSOR_COLLAPSED"),
    "M08": ({"restart_created_new_occurrence": True}, "RESTART_CREATED_SEMANTIC_RETRY"),
    "M09": ({"gate_pass_inferred": True, "gate_source": "CI"}, "GATE_INFERRED_FROM_NON_GATE_SOURCE"),
    "M10": ({"execution_cursor_authorizes_scope": True}, "EXECUTION_CURSOR_USED_AS_AUTHORITY"),
    "M11": ({"cross_primary_auto_dispatch": True, "rollout_authorized": False}, "UNAUTHORIZED_CROSS_PRIMARY_DISPATCH"),
    "M12": ({"stale_projection_authorized_mutation": True}, "STALE_PROJECTION_AUTHORIZED_MUTATION"),
    "M13": ({"schedule_acknowledged": True, "outbox_persisted": False}, "ACKNOWLEDGED_SCHEDULE_WITHOUT_OUTBOX"),
    "M14": ({"manual_duplicate_active_work": True}, "UNSAFE_MANUAL_DUPLICATE"),
    "M15": ({"terminal_history_rewritten": True}, "TERMINAL_HISTORY_REWRITTEN"),
}


def _snapshot_fixture():
    key = b"cp-i01-qualification-key"
    payload = {"adapter": "github", "source_kind": "pull_request", "resource_id": "Mostorm-Labs/aegis#29", "resource_version": "e8b2fa8c2bd29778a6a3c8bf5beb3d65ff9c364c"}
    return key, payload, vh.issue_snapshot_token(payload, key)


def snapshot_mutant_provenance() -> list[dict[str, object]]:
    key, payload, token = _snapshot_fixture()
    m16 = vh.mutate_snapshot_payload_without_resigning(token, "resource_version", "deadbeef")
    m17_binding = dict(payload, adapter="slack", source_kind="channel")
    m18_binding = dict(payload, resource_id="Mostorm-Labs/aegis#30", resource_version="other")
    return [
        {"mutant_id": "M16", "mutated_token_hex": m16.hex(), "expected_binding": payload},
        {"mutant_id": "M17", "token_hex": token.hex(), "expected_binding": m17_binding, "actual_binding": payload},
        {"mutant_id": "M18", "token_hex": token.hex(), "expected_binding": m18_binding, "actual_binding": payload},
    ]


def m20_provenance() -> dict[str, str]:
    full = b'{"kind":"fixture","payload":"0123456789abcdef"}'
    truncated = full[:24]
    return {"full_canonical_hex": full.hex(), "truncated_hex": truncated.hex(), "full_canonical_digest": vh.sha256_prefixed(full), "truncated_digest": vh.sha256_prefixed(truncated)}


def run_qualification() -> dict[str, object]:
    results: dict[str, dict[str, object]] = {}
    for mutant_id, (trace, expected_violation) in _M01_M15_CASES.items():
        violations = crm.detect_semantic_violations(trace)
        results[mutant_id] = {"detected": expected_violation in violations, "observed": sorted(violations), "expected": expected_violation}
    key, payload, token = _snapshot_fixture()
    m16 = vh.mutate_snapshot_payload_without_resigning(token, "resource_version", "deadbeef")
    m16_result = vh.verify_snapshot_token(m16, key, payload)
    results["M16"] = {"detected": not m16_result.ok, "observed": m16_result.reason, "expected": "INVALID_INTEGRITY"}
    m17_result = vh.verify_snapshot_token(token, key, dict(payload, adapter="slack"))
    results["M17"] = {"detected": not m17_result.ok, "observed": m17_result.reason, "expected": "BINDING_MISMATCH"}
    m18_result = vh.verify_snapshot_token(token, key, dict(payload, resource_version="other"))
    results["M18"] = {"detected": not m18_result.ok, "observed": m18_result.reason, "expected": "BINDING_MISMATCH"}
    m19_detected = not vh.supports_autonomous_trust_sensitive_provider(supports_callback=True, supports_durable_query=False, supports_correlation=False)
    results["M19"] = {"detected": m19_detected, "observed": "DEGRADED" if m19_detected else "FULL", "expected": "DEGRADED"}
    m20 = m20_provenance()
    full = bytes.fromhex(m20["full_canonical_hex"])
    truncated = bytes.fromhex(m20["truncated_hex"])
    m20_detected = not vh.verify_full_representation(full, truncated, m20["full_canonical_digest"])
    results["M20"] = {"detected": m20_detected, "observed": "REJECTED" if m20_detected else "ACCEPTED", "expected": "REJECTED"}
    if set(results) != set(catalogs.MANDATORY_MUTANTS):
        missing = sorted(set(catalogs.MANDATORY_MUTANTS) - set(results))
        extra = sorted(set(results) - set(catalogs.MANDATORY_MUTANTS))
        raise AssertionError(f"qualification/catalog identity mismatch missing={missing} extra={extra}")
    detected = sum(bool(item["detected"]) for item in results.values())
    return {"mandatory_total": len(results), "detected": detected, "false_acceptance": len(results) - detected, "results": results}
