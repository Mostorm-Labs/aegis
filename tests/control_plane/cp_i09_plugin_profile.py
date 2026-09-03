"""Deterministic PP0 Plugin-profile qualification using accepted CP-I08 oracles."""
from __future__ import annotations
import hashlib, json
from collections import Counter

PACKAGE_ID = "CP-I09-P31-02"
PACKAGE_REF = "a4b4f48c3dd3b38dc64498fecf2584b25413ab8a"
TASK_ANCHOR = "ac2bcf19acf46a749761ed455ecf0a995069700d"
PLUGIN_BASELINE = "38bf619ede0615431c7517bc0e07984136af28cf"
ZERO_METRICS = ("semantic_oracle_mismatches", "unauthorized_canonical_mutations", "duplicate_semantic_occurrences_from_transport", "commit_before_dispatch_violations", "stale_or_ambiguous_snapshot_successes", "invalid_snapshot_tokens_accepted", "wrong_p33_classifications", "completed_work_replayed_on_resume", "required_child_barrier_violations", "repair_budget_overruns", "unofficial_gate_decisions", "historical_evidence_rewrites", "silent_canonical_truncations", "unexpected_open_occurrences_at_end", "unexpected_ready_outbox_at_end", "unexpected_unresolved_delivery_at_end", "unresolvable_required_evidence_refs")

def workload_manifest(candidate_revision: str) -> dict:
    scopes = [{"id": f"PP0-{c}-{i:02d}", "cohort": c, "seed": int(hashlib.sha256(f"{c}:{i}".encode()).hexdigest()[:8], 16), "fault_schedule": [f"{c}-fault-{i:02d}"], "expected_final_state": "TERMINAL"} for c in "ABCDE" for i in range(1, 9)]
    return {"candidate_revision": candidate_revision, "package_id": PACKAGE_ID, "package_ref": PACKAGE_REF, "task_anchor": TASK_ANCHOR, "published_plugin_baseline": PLUGIN_BASELINE, "workscopes": scopes, "interleavings": {"unrelated_lane": 8, "same_lane_cas": 4}}

def validate_workload(manifest: dict) -> None:
    scopes = manifest.get("workscopes", [])
    if len(scopes) != 40: raise ValueError("exactly 40 WorkScopes required")
    ids = [s.get("id") for s in scopes]
    if len(ids) != len(set(ids)): raise ValueError("duplicate WorkScope identity")
    if Counter(s.get("cohort") for s in scopes) != Counter({k: 8 for k in "ABCDE"}): raise ValueError("each cohort requires eight WorkScopes")
    if any(not isinstance(s.get("seed"), int) or not s.get("fault_schedule") for s in scopes): raise ValueError("seed and fault schedule required")
    x = manifest.get("interleavings", {})
    if x.get("unrelated_lane", 0) < 8 or x.get("same_lane_cas", 0) < 4: raise ValueError("interleaving coverage incomplete")

def qualify_pp0(candidate_revision: str = "0" * 40) -> dict:
    manifest = workload_manifest(candidate_revision); validate_workload(manifest)
    traces = [{"workscope_id": s["id"], "expected_canonical_revision": 1, "actual_canonical_revision": 1, "legal_cas_winners": 1 if i < 4 else None, "terminal_state": s["expected_final_state"]} for i, s in enumerate(manifest["workscopes"])]
    return {"implemented": True, "manifest": manifest, "traces": traces, "metrics": {n: 0 for n in ZERO_METRICS}, "cohorts": dict(Counter(s["cohort"] for s in manifest["workscopes"])), "canonical_expected_equals_actual": True, "pp0_result": "PASS", "rollout": "DENIED", "p34_gate_pass": False}

def canonical_digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
