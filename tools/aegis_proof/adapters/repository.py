from __future__ import annotations

import re
from typing import Any, Mapping


_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_MUTABLE_TOKENS = {"latest", "current", "head", "main"}


class RepositoryAdapter:
    @staticmethod
    def validate_exact_ref(ref: Mapping[str, Any], *, expected_repository: str) -> dict[str, Any]:
        if not isinstance(ref, Mapping):
            raise ValueError("repository ref must be an object")
        repository = ref.get("repository")
        if repository != expected_repository:
            raise ValueError("repository namespace mismatch")
        revision = ref.get("revision")
        if not isinstance(revision, str) or not _SHA40.fullmatch(revision):
            raise ValueError("exact 40-character revision is required")
        durable_ref = ref.get("ref")
        if not isinstance(durable_ref, str) or not durable_ref:
            raise ValueError("exact durable ref is required")
        if durable_ref.lower() in _MUTABLE_TOKENS:
            raise ValueError("mutable navigation ref cannot cross trust boundary")
        return {
            "repository": repository,
            "revision": revision,
            "ref": durable_ref,
            "reviewer_resolvable": bool(ref.get("reviewer_resolvable", False)),
        }

    @staticmethod
    def exact_result_ref(
        *,
        repository_full_name: str,
        revision: str,
        ref: str,
        reviewer_resolvable: bool,
    ) -> dict[str, Any]:
        return RepositoryAdapter.validate_exact_ref(
            {
                "repository": repository_full_name,
                "revision": revision,
                "ref": ref,
                "reviewer_resolvable": reviewer_resolvable,
            },
            expected_repository=repository_full_name,
        )

    @staticmethod
    def durable_artifact_ref(locator: Mapping[str, Any], *, expected_repository: str) -> dict[str, Any]:
        if not isinstance(locator, Mapping):
            raise ValueError("artifact locator must be an object")
        if locator.get("repository") != expected_repository:
            raise ValueError("repository namespace mismatch")
        provider = locator.get("provider")
        native_id = locator.get("native_id")
        durable_ref = locator.get("ref")
        digest = locator.get("digest")
        if not isinstance(provider, str) or not provider:
            raise ValueError("artifact provider is required")
        if not isinstance(native_id, (str, int)) or str(native_id) == "":
            raise ValueError("artifact native_id is required")
        if not isinstance(durable_ref, str) or not durable_ref:
            raise ValueError("artifact durable ref is required")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ValueError("artifact sha256 digest is required")
        return {
            "repository": expected_repository,
            "provider": provider,
            "native_id": str(native_id),
            "ref": durable_ref,
            "digest": digest,
            "reviewer_resolvable": bool(locator.get("reviewer_resolvable", False)),
        }

    @staticmethod
    def require_reviewer_resolvable(ref: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(ref, Mapping) or not ref.get("ref"):
            raise ValueError("reviewer-resolvable ref is required")
        if ref.get("reviewer_resolvable") is not True:
            raise ValueError("required evidence is not reviewer-resolvable")
        return ref
