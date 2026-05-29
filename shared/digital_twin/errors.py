# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Digital Twin Domain Errors - أخطاء التوأم الرقمي
==================================================
Named exceptions for boundary contract failures.

Raise these explicitly at decision-pipeline boundaries — never swallow with
``except Exception``. Each error carries a programmatic ``reason_code`` so
consumers (API handlers, NATS workers) can route deterministically.
"""

from __future__ import annotations


class DigitalTwinError(Exception):
    """Base for all digital-twin domain errors. أساس أخطاء التوأم الرقمي."""


class ContextPipelineError(DigitalTwinError):
    """
    Raised when a recommendation pipeline is invoked with incomplete context:
    missing tenant_id/field_id, missing governing measurement, or stale state.
    يُرفع عند استدعاء خط التوصية بسياق ناقص.
    """

    def __init__(
        self,
        message: str,
        *,
        reason_code: str,
        missing: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.missing: tuple[str, ...] = tuple(missing or ())

    def __repr__(self) -> str:  # pragma: no cover - debugging only
        return (
            f"ContextPipelineError(reason_code={self.reason_code!r}, "
            f"missing={list(self.missing)!r}, message={self.args[0]!r})"
        )


class NeutralityViolation(DigitalTwinError):
    """
    Raised when location-specific data leaks into a location-neutral surface
    (crop cards, decision engines, shared types).
    يُرفع عند تسرّب بيانات موقع محدّد إلى سطح محايد.
    """

    def __init__(self, message: str, *, path: str | None = None) -> None:
        super().__init__(message)
        self.path = path


class UnsafeRecommendationError(DigitalTwinError):
    """
    Raised when a safety-critical recommendation (e.g. pesticide pre-harvest)
    is requested in a state that cannot satisfy the safety gate.
    يُرفع عند طلب توصية حسّاسة للسلامة في حالة لا تُتيح ذلك.
    """

    def __init__(
        self,
        message: str,
        *,
        gate: str,
        reason_code: str,
    ) -> None:
        super().__init__(message)
        self.gate = gate
        self.reason_code = reason_code


__all__ = [
    "DigitalTwinError",
    "ContextPipelineError",
    "NeutralityViolation",
    "UnsafeRecommendationError",
]
