import unittest

from tests.verification_productization.ecv0_fixtures import github_run, load_required_module


class ProviderAdapterTests(unittest.TestCase):
    def test_EC_S07_local_only_evidence_is_not_review_ready(self):
        local = load_required_module("tools.aegis_proof.adapters.local_runner")
        repository = load_required_module("tools.aegis_proof.adapters.repository")
        ref = local.LocalRunnerAdapter.local_evidence_ref("/tmp/local-only.txt")
        self.assertFalse(ref["reviewer_resolvable"])
        with self.assertRaises(ValueError):
            repository.RepositoryAdapter.require_reviewer_resolvable(ref)

    def test_local_runner_truncated_report_is_incomplete(self):
        local = load_required_module("tools.aegis_proof.adapters.local_runner")
        batch = local.LocalRunnerAdapter.to_observation_batch(
            {
                "terminated": True,
                "report_finalized": False,
                "end_condition": False,
                "records": [],
            },
            producer_id="local-unittest",
            producer_class="DETERMINISTIC_COLLECTOR",
            subject_ref="result@1",
            expected_fact_keys=("tests.summary",),
        )
        self.assertFalse(batch.complete)
        self.assertEqual(batch.observations, ())

    def test_local_runner_complete_report_produces_structured_observations(self):
        local = load_required_module("tools.aegis_proof.adapters.local_runner")
        batch = local.LocalRunnerAdapter.to_observation_batch(
            {
                "terminated": True,
                "report_finalized": True,
                "end_condition": True,
                "records": [{"fact_key": "tests.summary", "value": {"pass": 4, "fail": 0}}],
            },
            producer_id="local-unittest",
            producer_class="DETERMINISTIC_COLLECTOR",
            subject_ref="result@1",
            expected_fact_keys=("tests.summary",),
        )
        self.assertTrue(batch.complete)
        self.assertEqual(batch.observations[0].fact_key, "tests.summary")
        self.assertEqual(batch.observations[0].value, {"pass": 4, "fail": 0})

    def test_EC_S08_wrong_revision_actions_run_is_rejected(self):
        actions = load_required_module("tools.aegis_proof.adapters.github_actions")
        batch = actions.GitHubActionsAdapter.to_observation_batch(
            github_run(revision="e" * 40),
            expected_repository="Mostorm-Labs/aegis",
            expected_revision="d" * 40,
            required_jobs=("unit (a)", "unit (b)"),
            required_artifacts=(f"verification-productization-ecv0-{'d' * 40}",),
        )
        self.assertFalse(batch.complete)

    def test_EC_S09_missing_matrix_child_is_incomplete(self):
        actions = load_required_module("tools.aegis_proof.adapters.github_actions")
        batch = actions.GitHubActionsAdapter.to_observation_batch(
            github_run(include_matrix_b=False),
            expected_repository="Mostorm-Labs/aegis",
            expected_revision="d" * 40,
            required_jobs=("unit (a)", "unit (b)"),
            required_artifacts=(f"verification-productization-ecv0-{'d' * 40}",),
        )
        self.assertFalse(batch.complete)

    def test_actions_exact_terminal_run_is_complete(self):
        actions = load_required_module("tools.aegis_proof.adapters.github_actions")
        batch = actions.GitHubActionsAdapter.to_observation_batch(
            github_run(),
            expected_repository="Mostorm-Labs/aegis",
            expected_revision="d" * 40,
            required_jobs=("unit (a)", "unit (b)"),
            required_artifacts=(f"verification-productization-ecv0-{'d' * 40}",),
        )
        self.assertTrue(batch.complete)
        values = {record.fact_key: record.value for record in batch.observations}
        self.assertEqual(values["github_actions.result_revision"], "d" * 40)
        self.assertEqual(values["github_actions.run_id"], 9001)
        self.assertEqual(values["github_actions.run_attempt"], 1)

    def test_EC_S10_mutable_navigation_ref_is_rejected(self):
        repository = load_required_module("tools.aegis_proof.adapters.repository")
        with self.assertRaises(ValueError):
            repository.RepositoryAdapter.validate_exact_ref(
                {"repository": "Mostorm-Labs/aegis", "branch": "main", "ref": "latest"},
                expected_repository="Mostorm-Labs/aegis",
            )

    def test_EC_S11_signed_url_rotation_does_not_change_durable_identity(self):
        repository = load_required_module("tools.aegis_proof.adapters.repository")
        locator = {
            "repository": "Mostorm-Labs/aegis",
            "provider": "github-actions",
            "native_id": "501",
            "ref": "actions-artifact://501",
            "digest": "sha256:" + "2" * 64,
            "reviewer_resolvable": True,
            "signed_url": "https://example.invalid/one?sig=secret",
        }
        rotated = dict(locator, signed_url="https://example.invalid/two?sig=new")
        first = repository.RepositoryAdapter.durable_artifact_ref(locator, expected_repository="Mostorm-Labs/aegis")
        second = repository.RepositoryAdapter.durable_artifact_ref(rotated, expected_repository="Mostorm-Labs/aegis")
        self.assertEqual(first, second)
        self.assertNotIn("signed_url", first)

    def test_EC_S12_inaccessible_required_artifact_is_rejected(self):
        repository = load_required_module("tools.aegis_proof.adapters.repository")
        with self.assertRaises(ValueError):
            repository.RepositoryAdapter.require_reviewer_resolvable(
                {"ref": "actions-artifact://501", "reviewer_resolvable": False}
            )

    def test_EC_S13_cross_repository_ref_is_rejected(self):
        repository = load_required_module("tools.aegis_proof.adapters.repository")
        with self.assertRaises(ValueError):
            repository.RepositoryAdapter.validate_exact_ref(
                {
                    "repository": "Other/repo",
                    "revision": "d" * 40,
                    "ref": "git:d",
                    "reviewer_resolvable": True,
                },
                expected_repository="Mostorm-Labs/aegis",
            )


if __name__ == "__main__":
    unittest.main()
