# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
shared.prescription_safety — Prescription Safety Gateway (ADR-013)
===================================================================

Phase 4 implementation. The package now ships:

* ``models`` — value objects (``PrescriptionRequest``, ``Decision``, ...)
* ``protocols`` — ``PrescriptionChecker`` Protocol + ``CheckerResult``
* ``checkers`` — three default checkers (forbidden, dosage tolerance,
  pesticide PHI/REI adapter)
* ``gateway`` — ``PrescriptionGateway.check()`` orchestrator
"""

from __future__ import annotations

from .checkers import (
    DosageToleranceChecker,
    ForbiddenSubstanceChecker,
    PesticideComplianceCheckerAdapter,
    RateRange,
)
from .gateway import PrescriptionGateway
from .models import (
    Decision,
    DecisionEnum,
    Evidence,
    PrescriptionRequest,
    Reason,
)
from .protocols import CheckerResult, PrescriptionChecker

__all__ = [
    # models
    "Decision",
    "DecisionEnum",
    "Evidence",
    "PrescriptionRequest",
    "Reason",
    # protocol
    "CheckerResult",
    "PrescriptionChecker",
    # gateway
    "PrescriptionGateway",
    # default checkers
    "DosageToleranceChecker",
    "ForbiddenSubstanceChecker",
    "PesticideComplianceCheckerAdapter",
    "RateRange",
]
