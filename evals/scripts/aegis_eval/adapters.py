from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Protocol, Sequence


class ExecutionAdapter(Protocol):
    name: str

    def run(self, case: dict) -> str:
        ...


class RecordedAdapter:
    """Replay previously captured raw/structured outputs for reproducible scoring."""

    name = "recorded"

    def __init__(self, path: str | Path):
        self.path = Path(path)
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("recorded results must be a JSON object keyed by case_id")
        self.results = payload

    def run(self, case: dict) -> str:
        case_id = case["id"]
        if case_id not in self.results:
            raise KeyError(f"missing recorded result for {case_id}")
        value = self.results[case_id]
        return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


class CommandAdapter:
    """Invoke an external model/skill driver as a subprocess.

    The complete evaluation case is written to stdin as JSON. The command must
    write a JSON object or prose containing one fenced ```json block to stdout.
    """

    name = "command"

    def __init__(self, command: Sequence[str], timeout_seconds: int = 120):
        if not command:
            raise ValueError("command adapter requires a non-empty command")
        self.command = list(command)
        self.timeout_seconds = timeout_seconds

    def run(self, case: dict) -> str:
        completed = subprocess.run(
            self.command,
            input=json.dumps(case, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip()
            raise RuntimeError(
                f"adapter command failed for {case.get('id')} with exit {completed.returncode}: {stderr}"
            )
        return completed.stdout
