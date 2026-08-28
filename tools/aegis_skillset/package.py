from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from .model import load_skillset


def tree_sha256(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in Path(directory).rglob("*") if p.is_file()):
        rel = path.relative_to(directory).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(rel).to_bytes(8, "big")); digest.update(rel)
        digest.update(len(data).to_bytes(8, "big")); digest.update(data)
    return digest.hexdigest()


def render_release_manifest(root: Path, release_version: str) -> dict:
    root = Path(root)
    try:
        contract = json.loads((root / "skillset/distribution.json").read_text(encoding="utf-8"))
        plugin_names = contract["plugin"]["skills"]
        standalone_names = contract["standalone"]["skills"]
    except (FileNotFoundError, KeyError):
        cfg = load_skillset(root)
        plugin_names = [s.name for s in cfg.skills]; standalone_names = ["aegis"]
    def entries(names):
        return [{"name": n, "tree_sha256": tree_sha256(root / "skills" / n)} for n in names]
    return {"schema_version":"0.1", "product_id":"aegis", "release_version":release_version,
            "distribution_contract_ref":"skillset/distribution.json",
            "plugin":{"id":"aegis", "skills":entries(plugin_names)},
            "standalone":{"id":"aegis-standalone", "skills":entries(standalone_names)}}


def _write_zip(root: Path, release: dict, names: list[str], out: Path, prefix: str) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{prefix}.zip"
    files = {f"{prefix}/release.json": json.dumps(release, sort_keys=True, indent=2)+"\n"}
    for name in names:
        base = root / "skills" / name
        for p in base.rglob("*"):
            if p.is_file(): files[f"{prefix}/skills/{name}/{p.relative_to(base).as_posix()}"] = p.read_bytes()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for arc in sorted(files):
            info = zipfile.ZipInfo(arc, date_time=(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=(0o644 << 16)
            data = files[arc]; z.writestr(info, data.encode() if isinstance(data,str) else data)
    return target


def build_source_bundles(root: Path, release_version: str, output_dir: Path) -> tuple[Path, Path]:
    manifest = render_release_manifest(root, release_version)
    plugin = [x["name"] for x in manifest["plugin"]["skills"]]; standalone = [x["name"] for x in manifest["standalone"]["skills"]]
    return (_write_zip(root, manifest, plugin, Path(output_dir), f"aegis-plugin-{release_version}"),
            _write_zip(root, manifest, standalone, Path(output_dir), f"aegis-standalone-{release_version}"))
