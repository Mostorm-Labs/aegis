from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Callable, Mapping


_REQUIRED_FAMILY_KEYS = (
    "planned_count",
    "scheduled_count",
    "completed_count",
    "failed_count",
    "pending_count",
    "pending_peak",
    "schedule_window_overrun_seconds",
    "scheduling_blocker",
)


def write_progress_snapshot(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_name = handle.name
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass


def build_progress_snapshot(
    *,
    profile: str,
    phase: str,
    elapsed_wall_seconds: float,
    result_revision: str,
    package_id: str,
    package_ref: str,
    task_anchor: Mapping[str, str],
    family_snapshots: Mapping[str, Mapping[str, object]],
    abort_reason: str | None,
    resource_observation: Mapping[str, object] | None,
) -> dict:
    families: dict[str, dict[str, object]] = {}
    for name, snapshot in family_snapshots.items():
        row = dict(snapshot)
        for key in _REQUIRED_FAMILY_KEYS:
            row.setdefault(key, None)
        families[name] = row
    return {
        "schema_version": "0.2",
        "kind": f"CP-I09-{profile.upper()}-PROGRESS",
        "package_id": package_id,
        "package_ref": package_ref,
        "result_revision": result_revision,
        "task_anchor": dict(task_anchor),
        "profile": profile,
        "phase": phase,
        "elapsed_wall_seconds": float(elapsed_wall_seconds),
        "abort_reason": abort_reason,
        "families": families,
        "resource_observation": dict(resource_observation or {}),
    }


class ProgressReporter:
    def __init__(
        self,
        path: Path,
        snapshot_factory: Callable[[str], Mapping[str, object]],
        *,
        interval_seconds: float = 5.0,
    ):
        self._path = path
        self._snapshot_factory = snapshot_factory
        self._interval_seconds = float(interval_seconds)
        self._phase = "INITIALIZING"
        self._phase_lock = threading.Lock()
        self._emit_lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _current_phase(self) -> str:
        with self._phase_lock:
            return self._phase

    def _emit(self) -> None:
        with self._emit_lock:
            write_progress_snapshot(self._path, self._snapshot_factory(self._current_phase()))

    def _run(self) -> None:
        while not self._stop.wait(self._interval_seconds):
            self._emit()

    def start(self, phase: str) -> None:
        if self._thread is not None:
            raise RuntimeError("progress reporter already started")
        with self._phase_lock:
            self._phase = phase
        self._emit()
        self._thread = threading.Thread(target=self._run, name="cp-i09-progress", daemon=True)
        self._thread.start()

    def set_phase(self, phase: str) -> None:
        with self._phase_lock:
            self._phase = phase
        self._emit()

    def stop(self, final_phase: str = "COMPLETE") -> None:
        with self._phase_lock:
            self._phase = final_phase
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=max(1.0, self._interval_seconds * 2.0))
        self._emit()
