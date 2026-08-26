from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .http import HTTPResult
from .prompt import build_case_prompt, build_strict_result_schema, sanitize_case


@dataclass(frozen=True)
class SkillRef:
    skill_id: str
    version: str


def build_response_payload(
    case: dict,
    skill: SkillRef,
    *,
    model: str = "gpt-5.6-sol",
    reasoning_effort: str = "medium",
) -> dict:
    sanitized = sanitize_case(case)
    return {
        "model": model,
        "reasoning": {"effort": reasoning_effort},
        "tools": [
            {
                "type": "shell",
                "environment": {
                    "type": "container_auto",
                    "network_policy": {"type": "disabled"},
                    "skills": [
                        {
                            "type": "skill_reference",
                            "skill_id": skill.skill_id,
                            "version": skill.version,
                        }
                    ],
                },
            }
        ],
        "input": build_case_prompt(sanitized),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "aegis_lifecycle_result",
                "schema": build_strict_result_schema(),
                "strict": True,
            }
        },
    }


class OpenAIHostedSkillAPI:
    def __init__(self, transport):
        self.transport = transport

    def create_skill(self, zip_path: str | Path) -> SkillRef:
        result = self.transport.post_multipart_file(
            "/skills",
            "files",
            Path(zip_path),
            "application/zip",
        )
        skill_id = result.body.get("id")
        version = result.body.get("default_version") or result.body.get("latest_version")
        if not isinstance(skill_id, str) or not skill_id:
            raise ValueError("Skills API response missing skill id")
        if not isinstance(version, str) or not version:
            raise ValueError("Skills API response missing skill version")
        return SkillRef(skill_id=skill_id, version=version)

    def create_response(
        self,
        case: dict,
        skill: SkillRef,
        *,
        model: str = "gpt-5.6-sol",
        reasoning_effort: str = "medium",
    ) -> HTTPResult:
        payload = build_response_payload(
            case,
            skill,
            model=model,
            reasoning_effort=reasoning_effort,
        )
        return self.transport.post_json("/responses", payload)


__all__ = ["HTTPResult", "OpenAIHostedSkillAPI", "SkillRef", "build_response_payload"]
