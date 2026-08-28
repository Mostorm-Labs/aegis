from __future__ import annotations

import re
from pathlib import Path

from .model import load_skillset

_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_PLACEHOLDER_WORD_RE = re.compile(r"\b(?:TODO|TBD)\b")
_PLACEHOLDER_TOKENS = ("example_asset", "example_script", "example_reference")


def _frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate_generated_skills(root: Path) -> list[str]:
    root = Path(root)
    config = load_skillset(root)
    errors: list[str] = []
    for skill in config.skills:
        skill_dir = root / skill.distribution_path
        skill_md = skill_dir / "SKILL.md"
        agents = skill_dir / "agents/openai.yaml"
        if not skill_md.is_file():
            errors.append(f"{skill.name}: missing SKILL.md")
            continue
        if not agents.is_file():
            errors.append(f"{skill.name}: missing agents/openai.yaml")
        text = skill_md.read_text(encoding="utf-8")
        fm = _frontmatter(skill_md)
        if fm.get("name") != skill.name:
            errors.append(f"{skill.name}: frontmatter name mismatch")
        if not fm.get("description"):
            errors.append(f"{skill.name}: missing frontmatter description")
        if _PLACEHOLDER_WORD_RE.search(text):
            errors.append(f"{skill.name}: placeholder token")
        for token in _PLACEHOLDER_TOKENS:
            if token in text:
                errors.append(f"{skill.name}: placeholder token {token}")
        for target in _LINK_RE.findall(text):
            if "://" in target or target.startswith("#"):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (skill_dir / clean).is_file():
                errors.append(f"{skill.name}: missing reference {clean}")
    return errors
