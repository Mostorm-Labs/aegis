"""Committed-outbox dispatch boundary for Control Plane CP-I05.

Dispatch is operational delivery only. It has no canonical mutation primitive
and cannot turn provider acknowledgement into semantic completion.
"""
from __future__ import annotations


class DispatchRejected(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)
