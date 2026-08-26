from __future__ import annotations

import json

PROMPT_TEMPLATE_VERSION = "openai-hosted-aegis-baseline/v0.1"

_STATUS_VALUES = [
    "READY",
    "READY_WITH_FINDINGS",
    "BLOCKED_AUTHORITY",
    "BLOCKED_MISSING_INPUT",
    "BLOCKED_UNRESOLVED_DECISION",
    "BLOCKED_EVIDENCE",
    "BLOCKED_IMPLEMENTATION",
    "BLOCKED_ENVIRONMENT",
]

_DEFECT_VALUES = [
    "IMPLEMENTATION_DEFECT",
    "SPEC_DEFECT",
    "AUTHORITY_CONFLICT",
    "MISSING_CONTRACT",
    "TEST_DEFECT",
    "EVIDENCE_GAP",
    "ENVIRONMENT_DEFECT",
    "DEPENDENCY_BLOCKER",
    "UNRESOLVED_DECISION",
]

_GATE_VALUES = [
    "PASS",
    "PASS_WITH_FINDINGS",
    "BLOCKED_AUTHORITY",
    "BLOCKED_MISSING_INPUT",
    "BLOCKED_UNRESOLVED_DECISION",
    "BLOCKED_EVIDENCE",
    "BLOCKED_IMPLEMENTATION",
    "BLOCKED_ENVIRONMENT",
]


def sanitize_case(case: dict) -> dict:
    if not isinstance(case, dict):
        raise ValueError("evaluation case must be an object")
    case_id = case.get("id")
    input_obj = case.get("input")
    if not isinstance(case_id, str) or not case_id:
        raise ValueError("evaluation case requires non-empty id")
    if not isinstance(input_obj, dict):
        raise ValueError(f"{case_id}: input must be an object")
    prompt = input_obj.get("prompt")
    context = input_obj.get("context", [])
    if not isinstance(prompt, str) or not prompt:
        raise ValueError(f"{case_id}: input.prompt must be non-empty string")
    if not isinstance(context, list) or not all(isinstance(item, str) for item in context):
        raise ValueError(f"{case_id}: input.context must be an array of strings")
    return {
        "case_id": case_id,
        "prompt": prompt,
        "context": list(context),
    }


def build_case_prompt(sanitized_case: dict) -> str:
    case_id = sanitized_case["case_id"]
    prompt = sanitized_case["prompt"]
    context = sanitized_case["context"]
    scenario = json.dumps(
        {
            "case_id": case_id,
            "prompt": prompt,
            "context": context,
        },
        ensure_ascii=False,
        indent=2,
    )
    return (
        "Use the mounted `aegis` skill for this software-development lifecycle decision.\n"
        "Treat only the scenario below as project input. Do not assume access to an answer key, "
        "golden expectation, score, threshold, or hidden metadata.\n"
        "Return only the structured lifecycle result requested by the response schema. "
        "Use canonical Aegis status and defect vocabulary.\n\n"
        f"Scenario:\n{scenario}"
    )


def build_strict_result_schema() -> dict:
    nullable_string = ["string", "null"]
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "case_id",
            "status",
            "earliest_untrusted_layer",
            "start_stage",
            "route",
            "authority_classification",
            "defect_classification",
            "gate_verdict",
            "findings",
            "evidence_requirements",
        ],
        "properties": {
            "case_id": {"type": "string"},
            "status": {"type": "string", "enum": _STATUS_VALUES},
            "earliest_untrusted_layer": {"type": nullable_string},
            "start_stage": {"type": nullable_string},
            "route": {"type": "array", "items": {"type": "string"}},
            "authority_classification": {"type": "array", "items": {"type": "string"}},
            "defect_classification": {
                "type": nullable_string,
                "enum": [*_DEFECT_VALUES, None],
            },
            "gate_verdict": {
                "type": nullable_string,
                "enum": [*_GATE_VALUES, None],
            },
            "findings": {"type": "array", "items": {"type": "string"}},
            "evidence_requirements": {"type": "array", "items": {"type": "string"}},
        },
    }
