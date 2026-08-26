from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .api import SkillRef


def compute_corpus_digest(cases_dir: str | Path) -> str:
    root = Path(cases_dir)
    digest = hashlib.sha256()
    files = sorted(path for path in root.glob("*.json") if path.is_file())
    for path in files:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _load_provider_evidence(provider_evidence_dir: Path) -> dict[str, dict]:
    evidence_by_case: dict[str, dict] = {}
    for path in sorted(provider_evidence_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"provider evidence must be object: {path}")
        case_id = payload.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"provider evidence missing case_id: {path}")
        if case_id in evidence_by_case:
            raise ValueError(f"duplicate provider evidence for {case_id}")
        evidence_by_case[case_id] = payload
    return evidence_by_case


def _aggregate_usage(records: list[dict]) -> dict:
    totals: dict[str, int | float] = {}
    for record in records:
        usage = record.get("usage") or {}
        if not isinstance(usage, dict):
            continue
        for key, value in usage.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                totals[key] = totals.get(key, 0) + value
    return totals


def _latency_stats(records: list[dict]) -> dict:
    values = [float(record["latency_ms"]) for record in records if isinstance(record.get("latency_ms"), (int, float))]
    if not values:
        return {"count": 0, "min": None, "max": None, "mean": None}
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def build_baseline_manifest(
    *,
    provider_evidence_dir: str | Path,
    expected_case_ids: list[str],
    skill: SkillRef,
    skill_bundle_sha256: str,
    source_git_sha: str,
    runner_git_sha: str,
    corpus_digest: str,
    summary: dict,
    model: str,
    reasoning_effort: str,
    prompt_template_version: str,
    run_timestamp: str,
) -> dict:
    provider_evidence_dir = Path(provider_evidence_dir)
    evidence = _load_provider_evidence(provider_evidence_dir)
    missing = [case_id for case_id in expected_case_ids if case_id not in evidence]
    if missing:
        raise ValueError(f"missing provider evidence for: {', '.join(missing)}")

    unexpected = sorted(set(evidence) - set(expected_case_ids))
    if unexpected:
        raise ValueError(f"unexpected provider evidence for: {', '.join(unexpected)}")

    records = [evidence[case_id] for case_id in expected_case_ids]
    response_ids = []
    for record in records:
        response_id = record.get("response_id")
        if not isinstance(response_id, str) or not response_id:
            raise ValueError(f"provider evidence missing response_id for {record.get('case_id')}")
        response_ids.append(response_id)

    retry_count = sum(
        int(record.get("retry_count", 0))
        for record in records
        if isinstance(record.get("retry_count", 0), int)
    )

    return {
        "schema_version": "aegis-openai-baseline/v0.1",
        "provider": "openai",
        "endpoint": "/v1/responses",
        "model": model,
        "reasoning_effort": reasoning_effort,
        "source_git_sha": source_git_sha,
        "runner_git_sha": runner_git_sha,
        "skill_id": skill.skill_id,
        "skill_version": skill.version,
        "skill_bundle_sha256": skill_bundle_sha256,
        "corpus_digest": corpus_digest,
        "corpus_case_count": len(expected_case_ids),
        "prompt_template_version": prompt_template_version,
        "run_timestamp": run_timestamp,
        "response_ids": response_ids,
        "usage": _aggregate_usage(records),
        "latency_ms": _latency_stats(records),
        "retry_count": retry_count,
        "deterministic_gate_pass": bool(summary.get("deterministic_gate_pass")),
        "behavioral_gate_status": summary.get("behavioral_gate_status"),
        "summary": summary,
    }


def write_baseline_manifest(output_dir: str | Path, manifest: dict) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "baseline-manifest.json"
    temp = path.with_suffix(".json.tmp")
    temp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return path
