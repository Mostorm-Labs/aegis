#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.providers.openai.api import OpenAIHostedSkillAPI
from evals.providers.openai.baseline import (
    build_baseline_manifest,
    compute_corpus_digest,
    write_baseline_manifest,
)
from evals.providers.openai.bundle import build_skill_bundle
from evals.providers.openai.http import OpenAIHTTPTransport, ProviderEnvironmentError, ProviderRequestError
from evals.providers.openai.prompt import PROMPT_TEMPLATE_VERSION

DEFAULT_SKILL_DIR = ROOT / "skills" / "aegis"
DEFAULT_CASES_DIR = ROOT / "evals" / "cases"
DEFAULT_OUTPUT = ROOT / "artifacts" / "aegis-v0.1-openai-gpt-5.6-sol"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Aegis baseline through OpenAI hosted Agent Skill execution")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skill-dir", type=Path, default=DEFAULT_SKILL_DIR)
    parser.add_argument("--cases-dir", type=Path, default=DEFAULT_CASES_DIR)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--base-url", default=None)
    return parser


def _load_case_ids(cases_dir: Path) -> list[str]:
    case_ids: list[str] = []
    seen: set[str] = set()
    for path in sorted(cases_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"case file must contain array: {path}")
        for case in payload:
            if not isinstance(case, dict) or not isinstance(case.get("id"), str):
                raise ValueError(f"invalid case in {path}")
            case_id = case["id"]
            if case_id in seen:
                raise ValueError(f"duplicate case id: {case_id}")
            seen.add(case_id)
            case_ids.append(case_id)
    return case_ids


def _git_sha(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to resolve repository git SHA")
    return completed.stdout.strip()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("BLOCKED_ENVIRONMENT: OPENAI_API_KEY is required for a real provider baseline", file=sys.stderr)
        return 3

    output = args.output.resolve()
    provider_dir = output / "provider"
    provider_evidence_dir = output / "provider-evidence"
    bundle_path = provider_dir / "aegis-skill.zip"

    try:
        case_ids = _load_case_ids(args.cases_dir.resolve())
        source_git_sha = _git_sha(ROOT)
        bundle = build_skill_bundle(args.skill_dir.resolve(), bundle_path)

        transport_kwargs = {}
        if args.base_url:
            transport_kwargs["base_url"] = args.base_url
        transport = OpenAIHTTPTransport(api_key, **transport_kwargs)
        api = OpenAIHostedSkillAPI(transport)
        skill = api.create_skill(bundle.path)

        provider_dir.mkdir(parents=True, exist_ok=True)
        (provider_dir / "skill-reference.json").write_text(
            json.dumps(
                {
                    "skill_id": skill.skill_id,
                    "skill_version": skill.version,
                    "skill_bundle_sha256": bundle.sha256,
                    "source_git_sha": source_git_sha,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        driver_command = shlex.join(
            [
                sys.executable,
                "-m",
                "evals.providers.openai.driver",
                "--skill-id",
                skill.skill_id,
                "--skill-version",
                skill.version,
                "--evidence-dir",
                str(provider_evidence_dir),
                "--model",
                args.model,
                "--reasoning-effort",
                args.reasoning_effort,
                *(["--base-url", args.base_url] if args.base_url else []),
            ]
        )
        runner_command = [
            sys.executable,
            str(ROOT / "evals" / "scripts" / "run_eval.py"),
            "--adapter",
            "command",
            "--command",
            driver_command,
            "--cases-dir",
            str(args.cases_dir.resolve()),
            "--output",
            str(output),
        ]
        completed = subprocess.run(
            runner_command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            env=os.environ.copy(),
        )
        if completed.returncode not in (0, 2):
            diagnostic = (completed.stderr or completed.stdout).strip()
            if "BLOCKED_ENVIRONMENT" in diagnostic:
                print(diagnostic, file=sys.stderr)
                return 3
            print(f"PROVIDER_BASELINE_EXECUTION_ERROR: {diagnostic}", file=sys.stderr)
            return 1

        summary_path = output / "summary.json"
        if not summary_path.is_file():
            raise RuntimeError("evaluation runner completed without summary.json")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        manifest = build_baseline_manifest(
            provider_evidence_dir=provider_evidence_dir,
            expected_case_ids=case_ids,
            skill=skill,
            skill_bundle_sha256=bundle.sha256,
            source_git_sha=source_git_sha,
            runner_git_sha=source_git_sha,
            corpus_digest=compute_corpus_digest(args.cases_dir.resolve()),
            summary=summary,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            prompt_template_version=PROMPT_TEMPLATE_VERSION,
            run_timestamp=_utc_now(),
        )
        manifest_path = write_baseline_manifest(output, manifest)
    except ProviderEnvironmentError as exc:
        print(f"BLOCKED_ENVIRONMENT: {exc}", file=sys.stderr)
        return 3
    except (ProviderRequestError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"PROVIDER_BASELINE_EXECUTION_ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({"manifest": str(manifest_path), "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if summary.get("deterministic_gate_pass") else 2


if __name__ == "__main__":
    raise SystemExit(main())
