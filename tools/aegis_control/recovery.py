"""Reconciliation/recovery boundary for Control Plane CP-I05.

Age, callback loss, and delivery uncertainty are operational diagnostics. This
module does not author semantic failure or replacement StageOccurrences.
"""
from __future__ import annotations


class ReconciliationBlocked(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)
