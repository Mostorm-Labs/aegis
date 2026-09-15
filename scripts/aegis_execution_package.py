#!/usr/bin/env python3
"""Deterministic repo-local Aegis execution-package tooling."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

LOCAL_REF_FIELDS = {
    "authority_lock_ref": "authority.lock.json",
    "verification_lock_ref": "verification.lock.json",
    "execution_contract_ref": "execution-contract.json",
    "evidence_contract_ref": "evidence-contract.json",
    "implementation_context_ref": "implementation-context.md",
}
VALID_MODES = {"remote", "repo_materialized", "hybrid"}
VALID_STAGES = {"P32", "P33", "P36"}


class PackageError(ValueError):
    pass


def fail(code: str, message: str) -> None:
    raise PackageError(f"{code}: {message}")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("MISSING_FILE", str(path))
    except json.JSONDecodeError as exc:
        fail("INVALID_JSON", f"{path}: {exc}")
    if not isinstance(value, dict):
        fail("INVALID_OBJECT", f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_string(mapping: dict[str, Any], key: str, where: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        fail("INVALID_FIELD", f"{where}.{key} must be a non-empty string")
    return value


def validate_repository(package: dict[str, Any]) -> None:
    repository = package.get("repository")
    if not isinstance(repository, dict):
        fail("BLOCKED_REPOSITORY_IDENTITY", "repository must be an object")
    require_string(repository, "provider", "repository")
    require_string(repository, "full_name", "repository")
    if repository.get("provider") != "github":
        fail("BLOCKED_REPOSITORY_IDENTITY", "only provider=github is supported by this tool version")


def validate_anchor_and_cursor(package: dict[str, Any]) -> None:
    anchor = package.get("task_anchor")
    if not isinstance(anchor, dict):
        fail("INVALID_TASK_ANCHOR", "task_anchor is required")
    revision = require_string(anchor, "revision", "task_anchor")
    if len(revision) != 40 or any(ch not in "0123456789abcdefABCDEF" for ch in revision):
        fail("INVALID_TASK_ANCHOR", "task_anchor.revision must be a 40-character hex revision")
    if anchor.get("relation") != "ancestor":
        fail("INVALID_TASK_ANCHOR", "task_anchor.relation must be ancestor")
    cursor = package.get("resume_cursor")
    if cursor is None:
        return
    if not isinstance(cursor, dict):
        fail("INVALID_RESUME_CURSOR", "resume_cursor must be null or an object")
    cursor_revision = require_string(cursor, "revision", "resume_cursor")
    if len(cursor_revision) != 40 or any(ch not in "0123456789abcdefABCDEF" for ch in cursor_revision):
        fail("INVALID_RESUME_CURSOR", "resume_cursor.revision must be a 40-character hex revision")
    require_string(cursor, "execution_ref", "resume_cursor")
    if not isinstance(cursor.get("completed_through"), list):
        fail("INVALID_RESUME_CURSOR", "resume_cursor.completed_through must be a list")
    require_string(cursor, "next_action", "resume_cursor")


def safe_local_ref(package_dir: Path, ref: Any, field: str) -> Path:
    if not isinstance(ref, dict):
        fail("MISSING_BINDING", f"{field} must be an object")
    rel = require_string(ref, "path", field)
    expected_hash = require_string(ref, "sha256", field)
    path = Path(rel)
    if path.is_absolute() or ".." in path.parts or len(path.parts) != 1:
        fail("INVALID_BINDING_PATH", f"{field}.path must be a same-directory file name")
    target = package_dir / path
    if not target.is_file():
        fail("MISSING_BINDING", f"{field} target is missing: {rel}")
    actual_hash = sha256_file(target)
    if actual_hash != expected_hash:
        fail("HASH_MISMATCH", f"{field} expected {expected_hash}, got {actual_hash}")
    return target


def validate_authority_lock(value: dict[str, Any]) -> None:
    require_string(value, "authority_id", "authority_lock")
    require_string(value, "authority_version", "authority_lock")
    if value.get("authority_state") != "Current":
        fail("AUTHORITY_CONFLICT", "authority_lock.authority_state must be Current")
    if value.get("superseded_by") not in (None, "", []):
        fail("AUTHORITY_CONFLICT", "authority lock is explicitly superseded")
    source = value.get("source")
    if not isinstance(source, dict):
        fail("AUTHORITY_CONFLICT", "authority_lock.source must be an object")
    for key in ("provider", "source_id", "source_revision", "content_hash"):
        require_string(source, key, "authority_lock.source")
    statements = value.get("frozen_statements")
    if not isinstance(statements, list) or not statements:
        fail("AUTHORITY_CONFLICT", "authority_lock.frozen_statements must be non-empty")


def validate_verification_lock(value: dict[str, Any]) -> None:
    require_string(value, "verification_spec", "verification_lock")
    obligations = value.get("obligations")
    if not isinstance(obligations, list) or not obligations:
        fail("VERIFICATION_DESIGN_DEFECT", "verification_lock.obligations must be non-empty")
    seen: set[str] = set()
    for obligation in obligations:
        if not isinstance(obligation, dict):
            fail("VERIFICATION_DESIGN_DEFECT", "each obligation must be an object")
        oid = require_string(obligation, "id", "verification_lock.obligations[]")
        if oid in seen:
            fail("VERIFICATION_DESIGN_DEFECT", f"duplicate obligation id {oid}")
        seen.add(oid)
        require_string(obligation, "requirement", f"obligation[{oid}]")
        if not isinstance(obligation.get("oracle"), dict) or not obligation["oracle"]:
            fail("VERIFICATION_DESIGN_DEFECT", f"obligation[{oid}].oracle must be explicit")
        require_string(obligation, "acceptance", f"obligation[{oid}]")
        if not isinstance(obligation.get("evidence_required"), list):
            fail("VERIFICATION_DESIGN_DEFECT", f"obligation[{oid}].evidence_required must be a list")


def validate_execution_contract(value: dict[str, Any]) -> None:
    for key in ("required_changes", "forbidden_changes", "authorized_mutation_scope", "preserve_completed_work", "required_verification", "blocking_evidence", "corroborative_evidence", "terminal_blockers"):
        if not isinstance(value.get(key), list):
            fail("TASK_PACKAGE_DEFECT", f"execution_contract.{key} must be a list")
    terminal = value.get("terminal_success")
    if not isinstance(terminal, dict) or not terminal.get("all_of"):
        fail("TASK_PACKAGE_DEFECT", "execution_contract.terminal_success.all_of must be non-empty")
    if value.get("continue_until_terminal_state") is not True:
        fail("TASK_PACKAGE_DEFECT", "execution_contract.continue_until_terminal_state must be true")
    ret = value.get("return_contract")
    if not isinstance(ret, dict) or ret.get("success_status") != "READY_FOR_CONTROL_REVIEW" or ret.get("return_surface") != "CONTROL_REVIEW":
        fail("TASK_PACKAGE_DEFECT", "return contract must be READY_FOR_CONTROL_REVIEW -> CONTROL_REVIEW")
    design = value.get("implementation_design_preflight")
    if design is not None:
        if not isinstance(design, dict) or design.get("continue_without_control_return_when_resolved") is not True:
            fail("TASK_PACKAGE_DEFECT", "resolved design preflight must continue without a control round trip")
    oracle = value.get("oracle_precondition")
    if oracle is not None and oracle.get("red_required") is True:
        require_string(oracle, "expected_failure", "oracle_precondition")
        require_string(oracle, "observation_seam", "oracle_precondition")


def validate_local_package(package_path: Path, package: dict[str, Any]) -> None:
    paths: dict[str, Path] = {}
    for field, expected_name in LOCAL_REF_FIELDS.items():
        path = safe_local_ref(package_path.parent, package.get(field), field)
        if path.name != expected_name:
            fail("INVALID_BINDING_PATH", f"{field} must resolve to {expected_name}")
        paths[field] = path
    validate_authority_lock(read_json(paths["authority_lock_ref"]))
    validate_verification_lock(read_json(paths["verification_lock_ref"]))
    validate_execution_contract(read_json(paths["execution_contract_ref"]))
    evidence = read_json(paths["evidence_contract_ref"])
    if not isinstance(evidence.get("blocking"), list) or not isinstance(evidence.get("corroborative"), list):
        fail("TASK_PACKAGE_DEFECT", "evidence contract must separate blocking and corroborative evidence")
    if not paths["implementation_context_ref"].read_text(encoding="utf-8").strip():
        fail("TASK_PACKAGE_DEFECT", "implementation-context.md must be non-empty")


def validate_package(package_path: Path) -> str:
    package = read_json(package_path)
    require_string(package, "schema_version", "package")
    require_string(package, "task_id", "package")
    stage = require_string(package, "stage", "package")
    if stage not in VALID_STAGES:
        fail("INVALID_FIELD", f"unsupported execution stage {stage}")
    require_string(package, "stage_owner", "package")
    validate_repository(package)
    require_string(package, "execution_ref", "package")
    validate_anchor_and_cursor(package)
    if package.get("continue_until_terminal_state") is not True:
        fail("INVALID_FIELD", "package.continue_until_terminal_state must be true")
    if package.get("return_surface") != "CONTROL_REVIEW":
        fail("INVALID_FIELD", "package.return_surface must be CONTROL_REVIEW")
    mode = package.get("execution_authority_mode", "remote")
    if mode not in VALID_MODES:
        fail("INVALID_FIELD", f"execution_authority_mode must be one of {sorted(VALID_MODES)}")
    if mode in {"repo_materialized", "hybrid"}:
        validate_local_package(package_path, package)
    elif not (package.get("package_ref") or package.get("package_materialization_ref")):
        fail("TASK_PACKAGE_DEFECT", "legacy remote package needs package_ref or package_materialization_ref")
    return mode


def materialize(descriptor_path: Path, root: Path, force: bool) -> Path:
    descriptor = read_json(descriptor_path)
    package = descriptor.get("package")
    if not isinstance(package, dict):
        fail("TASK_PACKAGE_DEFECT", "descriptor.package must be an object")
    if package.get("execution_authority_mode") not in {"repo_materialized", "hybrid"}:
        fail("TASK_PACKAGE_DEFECT", "materialize requires repo_materialized or hybrid mode")
    task_id = require_string(package, "task_id", "package")
    if task_id in {".", ".."} or "/" in task_id or "\\" in task_id:
        fail("INVALID_TASK_ID", "task_id must be one safe path component")
    target = root.resolve() / ".aegis" / "packages" / task_id
    staging = target.with_name(target.name + ".tmp")
    if target.exists() and not force:
        fail("PACKAGE_EXISTS", f"{target} already exists; use --force to replace")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=False)
    payloads = {
        "authority.lock.json": descriptor.get("authority_lock"),
        "verification.lock.json": descriptor.get("verification_lock"),
        "execution-contract.json": descriptor.get("execution_contract"),
        "evidence-contract.json": descriptor.get("evidence_contract"),
    }
    try:
        for filename, value in payloads.items():
            if not isinstance(value, dict):
                fail("TASK_PACKAGE_DEFECT", f"descriptor field for {filename} must be an object")
            write_json(staging / filename, value)
        context = descriptor.get("implementation_context")
        if not isinstance(context, str) or not context.strip():
            fail("TASK_PACKAGE_DEFECT", "descriptor.implementation_context must be non-empty text")
        (staging / "implementation-context.md").write_text(context.rstrip() + "\n", encoding="utf-8")
        output = dict(package)
        for field, filename in LOCAL_REF_FIELDS.items():
            output[field] = {"path": filename, "sha256": sha256_file(staging / filename)}
        write_json(staging / "package.json", output)
        validate_package(staging / "package.json")
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        staging.replace(target)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return (target / "package.json").resolve()


def display_path(path: Path) -> str:
    parts = list(path.resolve().parts)
    if ".aegis" not in parts:
        return path.as_posix()
    index = len(parts) - 1 - parts[::-1].index(".aegis")
    return Path(*parts[index:]).as_posix()


def render_handoff(package_path: Path, materialization_ref: str | None) -> str:
    package = read_json(package_path)
    mode = validate_package(package_path)
    repo = package["repository"]
    lines = [
        "请按以下 Aegis handoff 直接执行：以 repo-local package 为任务授权，按 task_anchor/resume_cursor 从首个未完成步骤连续执行到 terminal state；仅在 Authority / Verification / Package / scope 冲突时 fail closed。",
        "type: surface_handoff",
        f"task_id: {package['task_id']}",
        f"stage: {package['stage']}",
        f"stage_owner: {package['stage_owner']}",
        "repository:",
        f"  provider: {repo['provider']}",
        f"  full_name: {repo['full_name']}",
        "package:",
        f"  path: {display_path(package_path)}",
    ]
    if materialization_ref:
        lines.append(f"  materialization_ref: {materialization_ref}")
    lines += [f"execution_authority_mode: {mode}", f"execution_ref: {package['execution_ref']}"]
    cursor = package.get("resume_cursor")
    if cursor is None:
        lines.append("resume_cursor: null")
    else:
        lines += ["resume_cursor:", f"  revision: {cursor['revision']}", f"  next_action: {json.dumps(cursor['next_action'], ensure_ascii=False)}"]
    lines += ["continue_until_terminal_state: true", "return_surface: CONTROL_REVIEW"]
    return "\n".join(lines) + "\n"


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, descendant], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def classify_cursor(package_path: Path, observed_revision: str, root: Path) -> str:
    package = read_json(package_path)
    validate_package(package_path)
    cursor = package.get("resume_cursor")
    anchor = package["task_anchor"]["revision"]
    if cursor:
        revision = cursor["revision"]
        if observed_revision == revision:
            return "EXACT_CURSOR"
        if is_ancestor(root, revision, observed_revision):
            return "DESCENDANT_CURSOR"
    if is_ancestor(root, anchor, observed_revision):
        return "ANCHOR_DESCENDANT_WITHOUT_CURSOR" if not cursor else "DIVERGED"
    return "DIVERGED"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("materialize"); p.add_argument("descriptor", type=Path); p.add_argument("--root", type=Path, default=Path.cwd()); p.add_argument("--force", action="store_true")
    p = sub.add_parser("validate"); p.add_argument("package", type=Path)
    p = sub.add_parser("render-handoff"); p.add_argument("package", type=Path); p.add_argument("--materialization-ref")
    p = sub.add_parser("check-cursor"); p.add_argument("package", type=Path); p.add_argument("observed_revision"); p.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        if args.command == "materialize": print(materialize(args.descriptor, args.root, args.force))
        elif args.command == "validate": print(f"AEGIS_EXECUTION_PACKAGE_OK mode={validate_package(args.package.resolve())}")
        elif args.command == "render-handoff": sys.stdout.write(render_handoff(args.package.resolve(), args.materialization_ref))
        else: print(classify_cursor(args.package.resolve(), args.observed_revision, args.root.resolve()))
        return 0
    except PackageError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
