# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Pluggable checker contract for the Prescription Safety Gateway (ADR-013).

The gateway itself is dumb: it iterates over a list of ``PrescriptionChecker``
implementations, collects their results, and aggregates a single ``Decision``.

Every concrete checker (forbidden substance, pesticide, dosage, GlobalGAP,
...) implements the same Protocol and is fully unit-testable in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from .models import PrescriptionRequest, Reason


@dataclass(frozen=True)
class CheckerResult:
    """Outcome of a single checker run.

    Attributes
    ----------
    passed:
        ``True`` when the checker found no problem at all. ``False`` when at
        least one ``Reason`` was emitted.
    blocking:
        ``True`` when at least one of the emitted reasons is severe enough
        that the gateway must short-circuit with ``REJECTED``. ``False``
        means the reasons only escalate the decision to ``REVIEW``.
    reasons:
        Ordered list of bilingual reasons. May be empty when ``passed`` is
        true.
    evidence:
        Raw payload retained for the audit trail. Should be JSON-serialisable
        so it can be persisted as-is.
    """

    passed: bool
    blocking: bool
    reasons: list[Reason] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls) -> CheckerResult:
        """Convenience: a clean pass with no reasons and no evidence."""

        return cls(passed=True, blocking=False, reasons=[], evidence={})


@runtime_checkable
class PrescriptionChecker(Protocol):
    """One safety check that the gateway can run against a prescription.

    Implementations should be cheap to construct and stateless across
    requests; per-request state belongs in the ``check()`` call.
    """

    #: Stable identifier used in ``Reason.source_checker`` and audit logs.
    name: str

    async def check(self, request: PrescriptionRequest) -> CheckerResult:
        """Evaluate ``request`` and return a ``CheckerResult``.

        Implementations must not raise on expected business outcomes; they
        should encode them as ``Reason`` entries. Unexpected exceptions are
        caught by the gateway and surfaced as a non-blocking ``UNCHECKED_*``
        reason so the caller sees that a checker was unavailable.
        """
        ...
