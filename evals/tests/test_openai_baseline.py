import json
import tempfile
import unittest
from pathlib import Path

from evals.providers.openai.api import SkillRef
from evals.providers.openai.baseline import (
    build_baseline_manifest,
    compute_corpus_digest,
    write_baseline_manifest,
)


class OpenAIBaselineTests(unittest.TestCase):
    def test_compute_corpus_digest_is_stable_and_path_sensitive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.json").write_text('[{"id":"a"}]')
            (root / "b.json").write_text('[{"id":"b"}]')
            first = compute_corpus_digest(root)
            second = compute_corpus_digest(root)
            self.assertEqual(first, second)
            (root / "b.json").write_text('[{"id":"changed"}]')
            self.assertNotEqual(first, compute_corpus_digest(root))

    def test_manifest_requires_complete_provider_evidence_and_records_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence_dir = root / "provider"
            evidence_dir.mkdir()
            for case_id, response_id, latency, retries in (
                ("case-1", "resp_1", 10.0, 0),
                ("case-2", "resp_2", 30.0, 1),
            ):
                (evidence_dir / f"{case_id}.json").write_text(
                    json.dumps(
                        {
                            "case_id": case_id,
                            "response_id": response_id,
                            "model": "gpt-5.6-sol",
                            "latency_ms": latency,
                            "retry_count": retries,
                            "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
                        }
                    )
                )

            summary = {
                "overall_weighted_score": 0.91,
                "critical_safety_errors": [],
                "deterministic_gate_pass": True,
                "behavioral_gate_status": "BLOCKED_EVIDENCE",
            }
            manifest = build_baseline_manifest(
                provider_evidence_dir=evidence_dir,
                expected_case_ids=["case-1", "case-2"],
                skill=SkillRef("skill_123", "7"),
                skill_bundle_sha256="abc",
                source_git_sha="source-sha",
                runner_git_sha="runner-sha",
                corpus_digest="corpus-sha",
                summary=summary,
                model="gpt-5.6-sol",
                reasoning_effort="medium",
                prompt_template_version="openai-hosted-aegis-baseline/v0.1",
                run_timestamp="2026-08-26T12:00:00Z",
            )

            self.assertEqual(manifest["provider"], "openai")
            self.assertEqual(manifest["endpoint"], "/v1/responses")
            self.assertEqual(manifest["skill_id"], "skill_123")
            self.assertEqual(manifest["skill_version"], "7")
            self.assertEqual(manifest["corpus_case_count"], 2)
            self.assertEqual(manifest["response_ids"], ["resp_1", "resp_2"])
            self.assertEqual(manifest["usage"]["input_tokens"], 20)
            self.assertEqual(manifest["usage"]["output_tokens"], 10)
            self.assertEqual(manifest["latency_ms"]["mean"], 20.0)
            self.assertEqual(manifest["retry_count"], 1)
            self.assertTrue(manifest["deterministic_gate_pass"])
            self.assertEqual(manifest["behavioral_gate_status"], "BLOCKED_EVIDENCE")

            path = write_baseline_manifest(root, manifest)
            self.assertEqual(json.loads(path.read_text()), manifest)

    def test_manifest_blocks_when_provider_evidence_is_missing(self):
        with tempfile.TemporaryDirectory() as td:
            evidence_dir = Path(td)
            (evidence_dir / "case-1.json").write_text(json.dumps({"case_id": "case-1", "response_id": "resp_1"}))
            with self.assertRaisesRegex(ValueError, "missing provider evidence"):
                build_baseline_manifest(
                    provider_evidence_dir=evidence_dir,
                    expected_case_ids=["case-1", "case-2"],
                    skill=SkillRef("skill_123", "7"),
                    skill_bundle_sha256="abc",
                    source_git_sha="source-sha",
                    runner_git_sha="runner-sha",
                    corpus_digest="corpus-sha",
                    summary={"deterministic_gate_pass": False, "behavioral_gate_status": "BLOCKED_IMPLEMENTATION"},
                    model="gpt-5.6-sol",
                    reasoning_effort="medium",
                    prompt_template_version="v0.1",
                    run_timestamp="2026-08-26T12:00:00Z",
                )


if __name__ == "__main__":
    unittest.main()
