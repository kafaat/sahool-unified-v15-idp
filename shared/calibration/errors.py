# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Errors - أخطاء المعايرة
=====================================
Domain-specific exceptions for the calibration subsystem.
"""

from __future__ import annotations

from shared.errors_py import ErrorCode, SahoolException


class CalibrationError(SahoolException):
    """Base calibration exception. خطأ المعايرة الأساسي."""

    def __init__(
        self,
        message: str,
        message_ar: str | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message,
            message_ar=message_ar or message,
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            status_code=422,
            details=details or {},
        )


class CalibrationNotEnabled(CalibrationError):
    """Raised when calibration feature flag is off."""

    def __init__(self) -> None:
        super().__init__(
            message="Calibration is not enabled for this environment",
            message_ar="المعايرة غير مفعّلة في هذه البيئة",
        )


class InsufficientObservations(CalibrationError):
    """Raised when too few observations are provided."""

    def __init__(self, variable: str, got: int, minimum: int = 3) -> None:
        super().__init__(
            message=f"Insufficient observations for '{variable}': got {got}, need >= {minimum}",
            message_ar=f"أرصاد غير كافية للمتغير '{variable}': وُجد {got}، المطلوب >= {minimum}",
            details={"variable": variable, "got": got, "minimum": minimum},
        )


class CalibrationFailed(CalibrationError):
    """Raised when the optimizer fails to converge."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Calibration failed: {reason}",
            message_ar=f"فشلت المعايرة: {reason}",
            details={"reason": reason},
        )


class UnsafeActivation(CalibrationError):
    """Raised when parameter set fails quality gates."""

    def __init__(self, violations: dict[str, float]) -> None:
        super().__init__(
            message="Parameter set does not meet quality gates for activation",
            message_ar="مجموعة المعاملات لا تستوفي بوابات الجودة للتفعيل",
            details={"violations": violations},
        )
