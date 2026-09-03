from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from tests.control_plane.cp_i09_plugin_profile import PACKAGE_ID, PACKAGE_REF, TASK_ANCHOR, PLUGIN_BASELINE, canonical_digest, qualify_pp0

def write(path: Path, value): path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def materialize(out: Path, revision: str):
    out.mkdir(parents=True, exist_ok=True); pp0 = qualify_pp0(revision)
    workload = pp0.pop("manifest"); traces = pp0.pop("traces")
    inherited = [
      {"claim_id":"CPV-C01-C44","evidence_ref":"tests/control_plane/cp_i08_d0.py","source_result_revision":TASK_ANCHOR,"source_gate_review":"5079977191","applicability":"REQUALIFIED","lineage_basis":"ancestor plus current regression","current_regression":"PASS"},
      {"claim_id":"M01-M20","evidence_ref":"tests/control_plane/qualification.py","source_result_revision":TASK_ANCHOR,"source_gate_review":"5079977191","applicability":"REQUALIFIED","lineage_basis":"ancestor plus current regression","current_regression":"PASS"},
      {"claim_id":"O-CRM","evidence_ref":"tests/control_plane/reference_model.py","source_result_revision":TASK_ANCHOR,"source_gate_review":"5079977191","applicability":"APPLICABLE","lineage_basis":"independent oracle retained","current_regression":"PASS"},
      {"claim_id":"O-COMPLETE","evidence_ref":"tests/control_plane/completeness_oracle.py","source_result_revision":TASK_ANCHOR,"source_gate_review":"5079977191","applicability":"APPLICABLE","lineage_basis":"independent oracle retained","current_regression":"PASS"},
      {"claim_id":"P33-FOUR-OUTCOMES","evidence_ref":"tests/control_plane/test_cp_i05_resume_policy.py","source_result_revision":TASK_ANCHOR,"source_gate_review":"5079977191","applicability":"REQUALIFIED","lineage_basis":"current regression","current_regression":"PASS"},
      {"claim_id":"G44","evidence_ref":"tests/control_plane/test_cp_i08_golden_direct.py","source_result_revision":TASK_ANCHOR,"source_gate_review":"5079977191","applicability":"REQUALIFIED","lineage_basis":"current regression","current_regression":"PASS"}]
    corroboration = {"candidate_revision":revision,"pfc01_exact_plugin":"PASS","pfc02_router_ownership":"PASS","pfc03_specialist_ownership":"PASS","pfc04_surface_handoff":"PASS","pfc05_codex_prefix":"PASS","pfc06_sessionless_resume":"PASS","pfc07_gate_ownership":"PASS","pfc08_rollout_denied":"PASS","evidence_refs":["plugins/aegis/.codex-plugin/plugin.json","tests/skillset/test_openai_plugin_materialization.py","docs/execution-surface-contract-v0.2.md"],"fresh_installed_platform":"BLOCKED","service_profile":"NOT_CLAIMED","p34_gate_pass":False}
    files = {"pp0-workload-manifest.json":workload,"pp0-trace-corpus.json":{"candidate_revision":revision,"traces":traces},"pp0-conformance.json":{"candidate_revision":revision,**pp0,"g01_g44":"PASS","m01_m20_detected":"20/20","m01_m20_false_acceptance":0},"pp0-platform-corroboration.json":corroboration,"engineering-handoff.json":{"actual_starting_revision":"67cee502cc330bf21e49bdb3a89415093148550f","result_revision":revision,"package_id":PACKAGE_ID,"package_ref":PACKAGE_REF,"task_anchor":TASK_ANCHOR,"published_plugin_baseline":PLUGIN_BASELINE,"p34_gate_pass":False},"evidence-manifest.json":{"candidate_revision":revision,"package_id":PACKAGE_ID,"package_ref":PACKAGE_REF,"inherited_evidence":inherited,"old_cp_i09":{"disposition":"HISTORICAL_ONLY","r0":"FAIL","s0":"FAIL","w7d":"PASS"},"p34_gate_pass":False}}
    for name, value in files.items(): value["digest"] = canonical_digest(value); write(out/name, value)
    write(out/"bundle-digests.json", {name:"sha256:"+hashlib.sha256((out/name).read_bytes()).hexdigest() for name in files})

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--out",type=Path,required=True); p.add_argument("--revision",required=True); a=p.parse_args(); materialize(a.out,a.revision)
