from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from .model import SkillSpec, load_skillset

@dataclass(frozen=True)
class BuildResult:
    rendered: dict[str, bytes]
    drift: tuple[str, ...]


def _safe_rel(path: str) -> PurePosixPath:
    rel = PurePosixPath(path)
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError(f'unsafe output path: {path}')
    return rel


def render_distribution(root: Path, skill: SkillSpec) -> dict[str, bytes]:
    root = Path(root)
    src = root / skill.source_path
    if not src.is_dir():
        raise FileNotFoundError(src)
    out: dict[str, bytes] = {}
    dist = PurePosixPath(skill.distribution_path)
    for path in sorted(p for p in src.rglob('*') if p.is_file()):
        rel = PurePosixPath(path.relative_to(src).as_posix())
        _safe_rel(rel.as_posix())
        out[(dist / rel).as_posix()] = path.read_bytes()
    for slug in sorted(skill.shared_refs):
        canonical = root / 'skillset/shared' / f'{slug}.md'
        if not canonical.is_file():
            raise FileNotFoundError(canonical)
        rel = PurePosixPath('references/shared') / f'{slug}.md'
        out[(dist / rel).as_posix()] = canonical.read_bytes()
    return dict(sorted(out.items()))


def build_all(root: Path, write: bool = False) -> BuildResult:
    root = Path(root)
    config = load_skillset(root)
    rendered: dict[str, bytes] = {}
    for skill in config.skills:
        rendered.update(render_distribution(root, skill))
    drift: list[str] = []
    for rel, data in rendered.items():
        target = root / rel
        if not target.is_file() or target.read_bytes() != data:
            drift.append(rel)
        if write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return BuildResult(dict(sorted(rendered.items())), tuple(sorted(drift)))


def check_distributions(root: Path) -> list[str]:
    root = Path(root)
    result = build_all(root, write=False)
    drift = set(result.drift)
    config = load_skillset(root)
    expected = set(result.rendered)
    for skill in config.skills:
        dist = root / skill.distribution_path
        if dist.is_dir():
            for path in dist.rglob('*'):
                if path.is_file():
                    rel = path.relative_to(root).as_posix()
                    if rel not in expected:
                        drift.add(rel)
    return sorted(drift)
