# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Prescription Safety Gateway orchestrator (ADR-013).

Sequential, short-circuit-on-block aggregator over a list of
``PrescriptionChecker`` implementations. Stateless across requests so a
single ``PrescriptionGateway`` instance is safe to share between FastAPI
workers.

Aggregation rules
-----------------

* Any checker that returns ``blocking=True`` short-circuits to
  ``REJECTED`` and the remaining checkers are skipped.
* If no checker blocks but at least one returns ``passed=False``, the
  decision is ``REVIEW``.
* Otherwise ``APPROVED``.
* Unexpected exceptions are caught and converted to a non-blocking
  ``UNCHECKED_EXCEPTION`` reason so a buggy checker can't break the
  whole pipeline.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from .models import Decision, DecisionEnum, Evidence, PrescriptionRequest, Reason
from .protocols import CheckerResult, PrescriptionChecker

log = logging.getLogger(__name__)


class PrescriptionGateway:
    """Aggregator over the existing v16 compliance checkers.

    Parameters
    ----------
    checkers:
        Ordered sequence of checkers. Order matters: forbidden-substance
        checks first so the cheapest hard-block runs before the more
        expensive PHI/REI lookups.
    mode:
        ``"standalone"`` (default) — the gateway runs in its own service.
        ``"embed"`` — same code, mounted inside ``agro-rules``. Carried
        through into evidence and audit logs only.
    """

    def __init__(
        self,
        checkers: Sequence[PrescriptionChecker] | None = None,
        mode: str = "standalone",
    ) -> None:
        self.checkers: list[PrescriptionChecker] = list(checkers or [])
        if mode not in {"standalone", "embed"}:
            raise ValueError(f"mode must be 'standalone' or 'embed', got {mode!r}")
        self.mode = mode

    # -- public API ------------------------------------------------------

    async def check(
        self,
        request: PrescriptionRequest,
        *,
        correlation_id: str | None = None,
    ) -> Decision:
        correlation_id = correlation_id or str(uuid.uuid4())
        all_reasons: list[Reason] = []
        all_evidence: list[Evidence] = []
        any_failure = False
        rejected = False

        if not self.checkers:
            all_reasons.append(
                Reason(
                    code="UNCHECKED_NO_CHECKERS_CONFIGURED",
                    message_en="No safety checkers configured; gateway approved by default.",
                    message_ar="لا توجد فاحصات سلامة مهيأة؛ تمت الموافقة افتراضيًا.",
                    severity="info",
                    source_checker="gateway",
                )
            )

        for checker in self.checkers:
            checker_name = getattr(checker, "name", checker.__class__.__name__)
            try:
                result = await checker.check(request)
            except Exception as exc:  # defensive: don't let one checker poison the pipeline
                log.exception(
                    "prescription_gateway.checker_failed",
                    extra={
                        "checker": checker_name,
                        "prescription_id": request.prescription_id,
                        "tenant_id": request.tenant_id,
                        "correlation_id": correlation_id,
                    },
                )
                all_reasons.append(
                    Reason(
                        code="UNCHECKED_EXCEPTION",
                        message_en=f"Checker '{checker_name}' raised an exception: {exc!s}",
                        message_ar=f"رفع الفاحص '{checker_name}' استثناءً: {exc!s}",
                        severity="warning",
                        source_checker=checker_name,
                    )
                )
                all_evidence.append(
                    Evidence(
                        checker=checker_name,
                        payload={"error": str(exc), "type": type(exc).__name__},
                        checked_at=datetime.now(UTC),
                    )
                )
                any_failure = True
                continue

            if not isinstance(result, CheckerResult):
                # Defensive: a checker returned the wrong type. Treat it
                # like an exception above.
                all_reasons.append(
                    Reason(
                        code="UNCHECKED_BAD_RETURN_TYPE",
                        message_en=(
                            f"Checker '{checker_name}' returned {type(result).__name__}, "
                            "expected CheckerResult."
                        ),
                        message_ar=(
                            f"أرجع الفاحص '{checker_name}' نوع {type(result).__name__} "
                            "بينما المتوقع CheckerResult."
                        ),
                        severity="warning",
                        source_checker=checker_name,
                    )
                )
                any_failure = True
                continue

            all_reasons.extend(result.reasons)
            all_evidence.append(
                Evidence(
                    checker=checker_name,
                    payload=dict(result.evidence),
                    checked_at=datetime.now(UTC),
                )
            )
            if not result.passed:
                any_failure = True
            if result.blocking:
                rejected = True
                break  # short-circuit

        if rejected:
            decision = DecisionEnum.REJECTED
        elif any_failure:
            decision = DecisionEnum.REVIEW
        else:
            decision = DecisionEnum.APPROVED

        # stable severity ordering: critical > warning > info
        severity_rank = {"critical": 0, "warning": 1, "info": 2}
        all_reasons.sort(key=lambda r: severity_rank.get(r.severity, 99))

        return Decision(
            decision=decision,
            reasons=all_reasons,
            evidence=all_evidence,
            decided_at=datetime.now(UTC),
            correlation_id=correlation_id,
        )
