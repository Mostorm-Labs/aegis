from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from ..ports import ObservationBatch, ObservationRecord


_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


class GitHubActionsAdapter:
    @staticmethod
    def to_observation_batch(
        run: Mapping[str, Any],
        *,
        expected_repository: str,
        expected_revision: str,
        required_jobs: Sequence[str] = (),
        required_artifacts: Sequence[str] = (),
        producer_id: str = "github-actions",
    ) -> ObservationBatch:
        if not isinstance(run, Mapping):
            return ObservationBatch(producer_id, False, ())
        complete = True

        repository = run.get("repository")
        if not isinstance(repository, Mapping) or repository.get("full_name") != expected_repository:
            complete = False

        workflow = run.get("workflow")
        if not isinstance(workflow, Mapping) or not workflow.get("id") or not workflow.get("path"):
            complete = False

        run_id = run.get("run_id")
        run_attempt = run.get("run_attempt")
        if not isinstance(run_id, int) or run_id <= 0:
            complete = False
        if not isinstance(run_attempt, int) or run_attempt <= 0:
            complete = False

        if not isinstance(expected_revision, str) or not _SHA40.fullmatch(expected_revision):
            complete = False
        if run.get("head_sha") != expected_revision:
            complete = False
        if run.get("status") != "completed":
            complete = False
        if not isinstance(run.get("conclusion"), str) or not run.get("conclusion"):
            complete = False

        jobs = run.get("jobs")
        if not isinstance(jobs, list):
            jobs = []
            complete = False
        jobs_by_name = {
            str(job.get("name")): job
            for job in jobs
            if isinstance(job, Mapping) and job.get("name")
        }
        for required_name in required_jobs:
            job = jobs_by_name.get(str(required_name))
            if not isinstance(job, Mapping):
                complete = False
                continue
            if not job.get("id") or job.get("status") != "completed" or not job.get("conclusion"):
                complete = False

        artifacts = run.get("artifacts")
        if not isinstance(artifacts, list):
            artifacts = []
            if required_artifacts:
                complete = False
        artifacts_by_name = {
            str(artifact.get("name")): artifact
            for artifact in artifacts
            if isinstance(artifact, Mapping) and artifact.get("name")
        }
        for required_name in required_artifacts:
            artifact = artifacts_by_name.get(str(required_name))
            if not isinstance(artifact, Mapping):
                complete = False
                continue
            digest = artifact.get("digest")
            if not artifact.get("id") or not isinstance(digest, str) or not _SHA256.fullmatch(digest):
                complete = False

        provider_run_ref = None
        if isinstance(run_id, int) and isinstance(run_attempt, int):
            provider_run_ref = f"github-actions://{run_id}/attempt/{run_attempt}"
        subject_ref = f"result@{expected_revision}"
        observations = (
            ObservationRecord("github_actions.repository", "DETERMINISTIC_COLLECTOR", producer_id, subject_ref, run.get("repository", {}).get("full_name") if isinstance(run.get("repository"), Mapping) else None, provider_run_ref),
            ObservationRecord("github_actions.workflow_id", "DETERMINISTIC_COLLECTOR", producer_id, subject_ref, workflow.get("id") if isinstance(workflow, Mapping) else None, provider_run_ref),
            ObservationRecord("github_actions.run_id", "DETERMINISTIC_COLLECTOR", producer_id, subject_ref, run_id, provider_run_ref),
            ObservationRecord("github_actions.run_attempt", "DETERMINISTIC_COLLECTOR", producer_id, subject_ref, run_attempt, provider_run_ref),
            ObservationRecord("github_actions.result_revision", "DETERMINISTIC_COLLECTOR", producer_id, subject_ref, run.get("head_sha"), provider_run_ref),
            ObservationRecord("github_actions.status", "DETERMINISTIC_COLLECTOR", producer_id, subject_ref, run.get("status"), provider_run_ref),
            ObservationRecord("github_actions.conclusion", "DETERMINISTIC_COLLECTOR", producer_id, subject_ref, run.get("conclusion"), provider_run_ref),
            ObservationRecord("github_actions.required_jobs", "DETERMINISTIC_COLLECTOR", producer_id, subject_ref, {name: name in jobs_by_name for name in required_jobs}, provider_run_ref),
            ObservationRecord("github_actions.required_artifacts", "DETERMINISTIC_COLLECTOR", producer_id, subject_ref, {name: name in artifacts_by_name for name in required_artifacts}, provider_run_ref),
        )
        return ObservationBatch(producer_id, complete, observations)
