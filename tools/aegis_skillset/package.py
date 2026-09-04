from __future__ import annotations

import hashlib
import io
import json
import shutil
import zipfile
from pathlib import Path

from .model import load_skillset


def validate_repository_identity(repository: object, expected: str = "Mostorm-Labs/aegis") -> dict[str, str]:
    """Validate the declared GitHub repository before package/anchor work."""
    if not isinstance(repository, dict):
        raise ValueError("BLOCKED_REPOSITORY_IDENTITY: repository declaration is missing")
    provider = repository.get("provider")
    full_name = repository.get("full_name")
    if provider != "github" or full_name != expected:
        raise ValueError(
            "BLOCKED_REPOSITORY_IDENTITY: declared repository must be "
            f"github/{expected}"
        )
    return {"provider": provider, "full_name": full_name}


def tree_sha256(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in Path(directory).rglob("*") if p.is_file()):
        rel = path.relative_to(directory).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def _zip_bytes(files: dict[str, tuple[bytes, int]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for arcname in sorted(files):
            data, mode = files[arcname]
            info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = ((0o100000 | mode) << 16)
            archive.writestr(info, data)
    return buffer.getvalue()


def _skill_zip_bytes(skill_dir: Path) -> bytes:
    files: dict[str, tuple[bytes, int]] = {}
    for path in sorted(p for p in Path(skill_dir).rglob("*") if p.is_file()):
        rel = path.relative_to(skill_dir).as_posix()
        mode = path.stat().st_mode & 0o777
        files[rel] = (path.read_bytes(), mode or 0o644)
    return _zip_bytes(files)


def _skill_release_entry(root: Path, name: str) -> dict:
    skill_dir = root / "skills" / name
    upload_zip = _skill_zip_bytes(skill_dir)
    return {
        "name": name,
        "tree_sha256": tree_sha256(skill_dir),
        "zip_filename": f"{name}.zip",
        "zip_sha256": hashlib.sha256(upload_zip).hexdigest(),
    }


def render_release_manifest(root: Path, release_version: str) -> dict:
    root = Path(root)
    try:
        contract = json.loads((root / "skillset/distribution.json").read_text(encoding="utf-8"))
        plugin_names = contract["plugin"]["skills"]
        standalone_names = contract["standalone"]["skills"]
    except (FileNotFoundError, KeyError):
        config = load_skillset(root)
        plugin_names = [skill.name for skill in config.skills]
        standalone_names = ["aegis"]

    return {
        "schema_version": "0.1",
        "product_id": "aegis",
        "release_version": release_version,
        "distribution_contract_ref": "skillset/distribution.json",
        "plugin": {
            "id": "aegis",
            "skills": [_skill_release_entry(root, name) for name in plugin_names],
        },
        "standalone": {
            "id": "aegis-standalone",
            "skills": [_skill_release_entry(root, name) for name in standalone_names],
        },
    }


def _write_zip(root: Path, release: dict, names: list[str], out: Path, prefix: str) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{prefix}.zip"
    files: dict[str, tuple[bytes, int]] = {
        f"{prefix}/release.json": (
            (json.dumps(release, sort_keys=True, indent=2) + "\n").encode("utf-8"),
            0o644,
        )
    }
    for name in names:
        base = root / "skills" / name
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            arcname = f"{prefix}/skills/{name}/{path.relative_to(base).as_posix()}"
            mode = path.stat().st_mode & 0o777
            files[arcname] = (path.read_bytes(), mode or 0o644)
    target.write_bytes(_zip_bytes(files))
    return target


def build_skill_installation_kit(root: Path, release_version: str, output_dir: Path) -> Path:
    root = Path(root)
    output_dir = Path(output_dir)
    release = render_release_manifest(root, release_version)
    kit_dir = output_dir / f"aegis-skills-{release_version}"
    if kit_dir.exists():
        shutil.rmtree(kit_dir)
    kit_dir.mkdir(parents=True, exist_ok=True)

    (kit_dir / "release.json").write_text(
        json.dumps(release, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    expected_names = [entry["name"] for entry in release["plugin"]["skills"]]
    for entry in release["plugin"]["skills"]:
        skill_name = entry["name"]
        data = _skill_zip_bytes(root / "skills" / skill_name)
        digest = hashlib.sha256(data).hexdigest()
        if digest != entry["zip_sha256"]:
            raise ValueError(f"upload ZIP digest drift for {skill_name}")
        (kit_dir / entry["zip_filename"]).write_bytes(data)

    actual_names = sorted(path.stem for path in kit_dir.glob("*.zip"))
    if actual_names != sorted(expected_names):
        raise ValueError("installation kit must contain exactly the expected nine Skill ZIPs")

    return kit_dir


def build_skill_installation_kit_archive(root: Path, release_version: str, output_dir: Path) -> Path:
    output_dir = Path(output_dir)
    kit_dir = build_skill_installation_kit(root, release_version, output_dir)
    prefix = kit_dir.name
    files: dict[str, tuple[bytes, int]] = {}
    for path in sorted(p for p in kit_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(kit_dir).as_posix()
        mode = path.stat().st_mode & 0o777
        files[f"{prefix}/{rel}"] = (path.read_bytes(), mode or 0o644)

    target = output_dir / f"aegis-skill-installation-kit-{release_version}.zip"
    target.write_bytes(_zip_bytes(files))
    return target


def build_source_bundles(root: Path, release_version: str, output_dir: Path) -> tuple[Path, Path]:
    manifest = render_release_manifest(root, release_version)
    plugin = [entry["name"] for entry in manifest["plugin"]["skills"]]
    standalone = [entry["name"] for entry in manifest["standalone"]["skills"]]
    return (
        _write_zip(root, manifest, plugin, Path(output_dir), f"aegis-plugin-{release_version}"),
        _write_zip(root, manifest, standalone, Path(output_dir), f"aegis-standalone-{release_version}"),
    )
