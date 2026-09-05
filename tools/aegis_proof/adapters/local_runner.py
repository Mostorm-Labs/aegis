from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..ports import ObservationBatch, ObservationRecord


class LocalRunnerAdapter:
    @staticmethod
    def to_observation_batch(
        report: Mapping[str, Any],
        *,
        producer_id: str,
        producer_class: str,
        subject_ref: str,
        expected_fact_keys: Sequence[str],
    ) -> ObservationBatch:
        if not isinstance(report, Mapping):
            return ObservationBatch(producer_id, False, ())
        records = report.get("records")
        if not isinstance(records, list):
            records = []
        structural_complete = (
            report.get("terminated") is True
            and report.get("report_finalized") is True
            and report.get("end_condition") is True
        )
        observations: list[ObservationRecord] = []
        seen: set[str] = set()
        for item in records:
            if not isinstance(item, Mapping):
                structural_complete = False
                continue
            fact_key = item.get("fact_key")
            if not isinstance(fact_key, str) or not fact_key or "value" not in item:
                structural_complete = False
                continue
            seen.add(fact_key)
            observations.append(
                ObservationRecord(
                    fact_key=fact_key,
                    producer_class=producer_class,
                    producer_id=producer_id,
                    subject_ref=subject_ref,
                    value=item["value"],
                    provider_run_ref=None,
                )
            )
        expected = {str(key) for key in expected_fact_keys}
        complete = structural_complete and expected.issubset(seen)
        if not complete:
            return ObservationBatch(producer_id, False, tuple(observations) if structural_complete else ())
        return ObservationBatch(producer_id, True, tuple(observations))

    @staticmethod
    def local_evidence_ref(path: str) -> dict[str, Any]:
        if not isinstance(path, str) or not path:
            raise ValueError("local evidence path is required")
        return {
            "provider": "local-filesystem",
            "native_id": path,
            "ref": path,
            "reviewer_resolvable": False,
            "staging_only": True,
        }
