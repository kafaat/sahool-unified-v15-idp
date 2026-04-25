# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
shared.prescription_safety — Prescription Safety Gateway (ADR-013)
===================================================================

Skeleton package. See ``README.md`` and
``docs/adr/ADR-013-prescription-safety-gateway.md``.
"""

from __future__ import annotations

from .models import (
    Decision,
    DecisionEnum,
    Evidence,
    PrescriptionRequest,
    Reason,
)

__all__ = [
    "Decision",
    "DecisionEnum",
    "Evidence",
    "PrescriptionRequest",
    "Reason",
]
