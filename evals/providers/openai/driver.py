from __future__ import annotations

import json
from pathlib import Path

from .api import SkillRef
from .prompt import PROMPT_TEMPLATE_VERSION, sanitize_case
from .response import extract_output_text, provider_evidence_record


def _safe_case_for_api(case: dict) -> tuple[dict, dict]:
    scenario = sanitize_case(case)
    safe_case = {
        "id": scenario["case_id"],
        "input": {
            "prompt": scenario["prompt"],
            "context": scenario["context"],
        },
    }
    return scenario, safe_case


def _write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def run_case(
    case: dict,
    *,
    api,
    skill: SkillRef,
    evidence_dir: Path,
    model: str,
    reasoning_effort: str,
) -> str:
    scenario, safe_case = _safe_case_for_api(case)
    result = api.create_response(
        safe_case,
        skill,
        model=model,
        reasoning_effort=reasoning_effort,
    )
    output_text = extract_output_text(result.body)
    try:
        normalized = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"provider structured output is not valid JSON: {exc}") from exc
    if not isinstance(normalized, dict):
        raise ValueError("provider structured output must be a JSON object")
    normalized["case_id"] = scenario["case_id"]

    evidence = provider_evidence_record(
        case_id=scenario["case_id"],
        result=result,
        output_text=json.dumps(normalized, ensure_ascii=False),
    )
    evidence.update(
        {
            "provider": "openai",
            "skill_id": skill.skill_id,
            "skill_version": skill.version,
            "prompt_template_version": PROMPT_TEMPLATE_VERSION,
            "scenario": scenario,
        }
    )
    _write_json_atomic(evidence_dir / f"{scenario['case_id']}.json", evidence)
    return json.dumps(normalized, ensure_ascii=False)


def _build_parser():
    import argparse

    parser = argparse.ArgumentParser(description="Run one Aegis evaluation case through OpenAI hosted skill execution")
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--skill-version", required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--base-url", default=None)
    return parser


def main(argv=None) -> int:
    import os
    import sys

    from .api import OpenAIHostedSkillAPI
    from .http import OpenAIHTTPTransport, ProviderEnvironmentError, ProviderRequestError
    from .response import ProviderResponseError

    args = _build_parser().parse_args(argv)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("BLOCKED_ENVIRONMENT: OPENAI_API_KEY is required", file=sys.stderr)
        return 3

    try:
        case = json.load(sys.stdin)
        transport_kwargs = {}
        if args.base_url:
            transport_kwargs["base_url"] = args.base_url
        transport = OpenAIHTTPTransport(api_key, **transport_kwargs)
        api = OpenAIHostedSkillAPI(transport)
        output = run_case(
            case,
            api=api,
            skill=SkillRef(args.skill_id, args.skill_version),
            evidence_dir=args.evidence_dir,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
        )
    except ProviderEnvironmentError as exc:
        print(f"BLOCKED_ENVIRONMENT: {exc}", file=sys.stderr)
        return 3
    except (ProviderRequestError, ProviderResponseError, ValueError, json.JSONDecodeError) as exc:
        print(f"PROVIDER_EXECUTION_ERROR: {exc}", file=sys.stderr)
        return 1

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
