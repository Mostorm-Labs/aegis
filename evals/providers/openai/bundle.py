from __future__ import annotations

import hashlib
import zipfile
from dataclasses import dataclass
from pathlib import Path

_IGNORED_NAMES = {".DS_Store"}
_IGNORED_PARTS = {"__pycache__", ".git"}
_FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)


@dataclass(frozen=True)
class SkillBundle:
    path: Path
    sha256: str
    top_level: str
    files: tuple[str, ...]


def _included_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(skill_dir)
        if path.name in _IGNORED_NAMES:
            continue
        if any(part in _IGNORED_PARTS for part in rel.parts):
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(skill_dir).as_posix())


def build_skill_bundle(skill_dir: Path, output_path: Path) -> SkillBundle:
    skill_dir = Path(skill_dir)
    output_path = Path(output_path)
    if not (skill_dir / "SKILL.md").is_file():
        raise ValueError(f"missing SKILL.md in {skill_dir}")

    files = _included_files(skill_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    top_level = "aegis"
    archive_names: list[str] = []

    with zipfile.ZipFile(
        output_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zf:
        for path in files:
            rel = path.relative_to(skill_dir).as_posix()
            archive_name = f"{top_level}/{rel}"
            info = zipfile.ZipInfo(archive_name, date_time=_FIXED_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            archive_names.append(archive_name)

    digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
    return SkillBundle(
        path=output_path,
        sha256=digest,
        top_level=top_level,
        files=tuple(archive_names),
    )
