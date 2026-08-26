from __future__ import annotations

import json
import re

_STATUS_ALIASES = {
    "READY_TO_ROUTE": "READY",
}

_DEFAULTS = {
    "earliest_untrusted_layer": None,
    "start_stage": None,
    "route": [],
    "authority_classification": [],
    "defect_classification": None,
    "gate_verdict": None,
    "findings": [],
    "evidence_requirements": [],
}

_FENCED_JSON_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def _parse_payload(raw: str) -> dict:
    raw = raw.strip()
    if not raw:
        raise ValueError("empty model result")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        match = _FENCED_JSON_RE.search(raw)
        if not match:
            raise ValueError("raw result does not contain a JSON object or fenced JSON block")
        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid fenced JSON result: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("normalized result must be a JSON object")
    return payload


def normalize_raw_result(case_id: str, raw: str) -> dict:
    payload = _parse_payload(raw)
    result = {"case_id": case_id, **_DEFAULTS, **payload}
    result["case_id"] = case_id

    status = result.get("status")
    if status in _STATUS_ALIASES:
        result["status"] = _STATUS_ALIASES[status]

    for field in ("route", "authority_classification", "findings", "evidence_requirements"):
        if result.get(field) is None:
            result[field] = []
        if not isinstance(result[field], list):
            raise ValueError(f"{field} must be a list")

    if not isinstance(result.get("status"), str):
        raise ValueError("status must be a string")
    return result
