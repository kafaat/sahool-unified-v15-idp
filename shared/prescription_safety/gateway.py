# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Prescription Safety Gateway orchestrator. Skeleton — see ADR-013.

Sequential short-circuit on REJECTED:

    1. Forbidden-substance blacklist (from agri-taxonomy-service)
    2. PesticideComplianceChecker (PHI / REI / PPE / tank-mix / drift)
    3. Dosage ±10 % gate (agro-rules)
    4. GlobalGAP registration (globalgap-compliance)
    5. Audit-log emit + NATS publish
"""

from __future__ import annotations

from .models import Decision, PrescriptionRequest


class PrescriptionGateway:
    """Aggregator over the existing v16 compliance checkers.

    Phase 4 implementation. The class boundary is defined here so that
    consumers can type against it from Phase 3 onward.
    """

    def __init__(self, mode: str = "standalone") -> None:
        # ``mode`` is "standalone" or "embed" (mounted inside agro-rules).
        self.mode = mode

    async def check(self, request: PrescriptionRequest) -> Decision:
        raise NotImplementedError("ADR-013: implemented in Phase 4")
