# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Default ``PrescriptionChecker`` implementations for ADR-013.

All checkers in this module are pure-Python and synchronous-at-heart so
they can run inside the gateway without external dependencies. Concrete
network-bound checkers (taxonomy, GlobalGAP, agro-rules dosage) live in
their own service modules and inject themselves via the same Protocol.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from .models import PrescriptionRequest, Reason
from .protocols import CheckerResult, PrescriptionChecker

if TYPE_CHECKING:
    from shared.pesticide_compliance import (  # type: ignore[import-not-found]
        PesticideApplication,
    )

# ---------------------------------------------------------------------------
# 1. Forbidden-substance blocklist
# ---------------------------------------------------------------------------


@dataclass
class ForbiddenSubstanceChecker:
    """Hard blocklist of products / active ingredients.

    Phase 4 wires a ``TaxonomyClient`` (see ADR-012). Until it lands we
    accept a static set so unit tests and integrations can exercise the
    full gateway flow.
    """

    name: str = "forbidden_substance"
    blocklist: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_iterable(cls, items: Iterable[str]) -> ForbiddenSubstanceChecker:
        return cls(blocklist=frozenset(item.strip().lower() for item in items if item.strip()))

    async def check(self, request: PrescriptionRequest) -> CheckerResult:
        product_key = request.product.strip().lower()
        if product_key in self.blocklist:
            reason = Reason(
                code="FORBIDDEN_SUBSTANCE",
                message_en=f"Product '{request.product}' is on the forbidden-substance list.",
                message_ar=f"المنتج '{request.product}' مدرج في قائمة المواد المحظورة.",
                severity="critical",
                source_checker=self.name,
            )
            return CheckerResult(
                passed=False,
                blocking=True,
                reasons=[reason],
                evidence={"product": request.product, "matched": True},
            )
        return CheckerResult(
            passed=True,
            blocking=False,
            reasons=[],
            evidence={"product": request.product, "matched": False},
        )


# ---------------------------------------------------------------------------
# 2. Dosage tolerance gate (±10 %)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RateRange:
    """Recommended rate window for a (crop, product) pair, in ``unit``."""

    min_rate: float
    max_rate: float
    unit: str


@dataclass
class DosageToleranceChecker:
    """±10 % gate around a recommended rate range.

    Within ``±tolerance`` of the recommended window → APPROVED.
    Outside the window but within ``2× tolerance`` → REVIEW (warning).
    Beyond that → REJECTED.

    The recommended ranges are injected so tests stay deterministic and
    so production can swap a dict for an HTTP client to ``agro-rules`` in
    a follow-up without touching the gateway.
    """

    name: str = "dosage_tolerance"
    tolerance: float = 0.10  # ±10 %
    rates: Mapping[tuple[str, str], RateRange] = field(default_factory=dict)

    def _lookup(self, request: PrescriptionRequest) -> RateRange | None:
        key = (request.crop.lower().strip(), request.product.lower().strip())
        return self.rates.get(key)

    async def check(self, request: PrescriptionRequest) -> CheckerResult:
        rate_range = self._lookup(request)
        if rate_range is None:
            # No reference data → cannot validate. Emit info reason so the
            # caller still gets a useful audit trail and the decision is
            # demoted to REVIEW.
            return CheckerResult(
                passed=False,
                blocking=False,
                reasons=[
                    Reason(
                        code="UNCHECKED_DOSAGE_NO_REFERENCE",
                        message_en=(
                            f"No recommended rate range for crop='{request.crop}' product='{request.product}'."
                        ),
                        message_ar=(
                            f"لا توجد جرعة مرجعية للمحصول '{request.crop}' والمنتج '{request.product}'."
                        ),
                        severity="warning",
                        source_checker=self.name,
                    )
                ],
                evidence={"reference_found": False},
            )

        if rate_range.unit != request.rate_unit:
            return CheckerResult(
                passed=False,
                blocking=True,
                reasons=[
                    Reason(
                        code="DOSAGE_UNIT_MISMATCH",
                        message_en=(
                            f"Rate unit '{request.rate_unit}' does not match expected '{rate_range.unit}'."
                        ),
                        message_ar=(
                            f"وحدة الجرعة '{request.rate_unit}' لا تطابق المتوقع '{rate_range.unit}'."
                        ),
                        severity="critical",
                        source_checker=self.name,
                    )
                ],
                evidence={
                    "expected_unit": rate_range.unit,
                    "got_unit": request.rate_unit,
                },
            )

        lo = rate_range.min_rate * (1.0 - self.tolerance)
        hi = rate_range.max_rate * (1.0 + self.tolerance)
        hard_lo = rate_range.min_rate * (1.0 - 2.0 * self.tolerance)
        hard_hi = rate_range.max_rate * (1.0 + 2.0 * self.tolerance)

        evidence = {
            "rate": request.rate,
            "rate_unit": request.rate_unit,
            "min": rate_range.min_rate,
            "max": rate_range.max_rate,
            "tolerance": self.tolerance,
            "soft_window": [lo, hi],
            "hard_window": [hard_lo, hard_hi],
        }

        if lo <= request.rate <= hi:
            return CheckerResult(passed=True, blocking=False, evidence=evidence)

        if hard_lo <= request.rate <= hard_hi:
            return CheckerResult(
                passed=False,
                blocking=False,
                reasons=[
                    Reason(
                        code="DOSAGE_OUT_OF_TOLERANCE",
                        message_en=(
                            f"Rate {request.rate} {request.rate_unit} is outside the ±{self.tolerance:.0%} "
                            f"window [{lo:.2f}, {hi:.2f}]."
                        ),
                        message_ar=(
                            f"الجرعة {request.rate} {request.rate_unit} خارج نافذة ±{self.tolerance:.0%} "
                            f"[{lo:.2f}, {hi:.2f}]."
                        ),
                        severity="warning",
                        source_checker=self.name,
                    )
                ],
                evidence=evidence,
            )

        return CheckerResult(
            passed=False,
            blocking=True,
            reasons=[
                Reason(
                    code="DOSAGE_HARD_LIMIT_EXCEEDED",
                    message_en=(
                        f"Rate {request.rate} {request.rate_unit} exceeds the hard safety limit "
                        f"[{hard_lo:.2f}, {hard_hi:.2f}]."
                    ),
                    message_ar=(
                        f"الجرعة {request.rate} {request.rate_unit} تجاوزت الحد الآمن "
                        f"[{hard_lo:.2f}, {hard_hi:.2f}]."
                    ),
                    severity="critical",
                    source_checker=self.name,
                )
            ],
            evidence=evidence,
        )


# ---------------------------------------------------------------------------
# 3. PHI / REI gate (wraps shared.pesticide_compliance)
# ---------------------------------------------------------------------------


@dataclass
class PesticideComplianceCheckerAdapter:
    """Adapter from ``PrescriptionRequest`` to ``PesticideComplianceChecker``.

    The underlying v16 checker is field-history based (it answers "given
    everything I've sprayed, am I safe to harvest / re-enter?"). For a
    *prescription* (i.e. a planned application) we ask the same engine but
    forward-projected: we synthesise the application, then ask whether the
    planned harvest date or the planned re-entry would violate PHI/REI.

    ``shared.pesticide_compliance`` is optional; if it is unavailable the
    adapter degrades to a non-blocking ``UNCHECKED_*`` reason.
    """

    name: str = "pesticide_compliance"
    planned_harvest_lookahead_days: int = 30

    def _build_application(self, request: PrescriptionRequest) -> PesticideApplication:
        # Local import keeps `shared.prescription_safety` importable even
        # in environments where pesticide_compliance is not installed.
        from shared.pesticide_compliance import (  # type: ignore[import-not-found]
            PesticideApplication,
        )

        return PesticideApplication(
            application_id=f"prescription:{request.prescription_id}",
            tenant_id=request.tenant_id,
            field_id=request.field_id,
            pesticide_id=request.product,
            application_date=datetime.now(UTC),
            application_rate=request.rate,
            application_rate_unit=request.rate_unit,
            area_treated_ha=float(request.metadata.get("area_treated_ha", 1.0)),
            target_pest=str(request.target.get("pest", "")),
            target_pest_ar=str(request.target.get("pest_ar", "")),
            crop=request.crop,
            growth_stage=str(request.metadata.get("growth_stage", "")),
        )

    async def check(self, request: PrescriptionRequest) -> CheckerResult:
        if request.prescription_type != "pesticide":
            return CheckerResult.ok()

        try:
            from shared.pesticide_compliance import (  # type: ignore[import-not-found]
                ComplianceStatus,
                PesticideComplianceChecker,
                get_pesticide,
            )
        except Exception:  # pragma: no cover - defensive guard
            return CheckerResult(
                passed=False,
                blocking=False,
                reasons=[
                    Reason(
                        code="UNCHECKED_PESTICIDE_COMPLIANCE_UNAVAILABLE",
                        message_en="pesticide_compliance module is not installed; PHI/REI not verified.",
                        message_ar="وحدة سلامة المبيدات غير مثبتة؛ لم يُتحقق من PHI/REI.",
                        severity="warning",
                        source_checker=self.name,
                    )
                ],
                evidence={"available": False},
            )

        if get_pesticide(request.product) is None:
            return CheckerResult(
                passed=False,
                blocking=False,
                reasons=[
                    Reason(
                        code="UNCHECKED_PESTICIDE_NOT_IN_DATABASE",
                        message_en=f"Pesticide '{request.product}' not found in registry; PHI/REI skipped.",
                        message_ar=f"المبيد '{request.product}' غير موجود في السجل؛ تم تخطي PHI/REI.",
                        severity="warning",
                        source_checker=self.name,
                    )
                ],
                evidence={"product": request.product, "in_database": False},
            )

        engine = PesticideComplianceChecker()
        engine.add_application(self._build_application(request))

        planned_harvest = request.metadata.get("planned_harvest_date")
        if isinstance(planned_harvest, str):
            planned_harvest = datetime.fromisoformat(planned_harvest)
        if planned_harvest is None:
            planned_harvest = datetime.now(UTC) + timedelta(days=self.planned_harvest_lookahead_days)

        phi_violations = engine.check_phi_compliance(request.field_id, planned_harvest)
        rei_violations = engine.check_rei_compliance(request.field_id)

        reasons: list[Reason] = []
        blocking = False
        for v in phi_violations:
            sev = "critical" if v.status == ComplianceStatus.CRITICAL else "warning"
            blocking = blocking or sev == "critical"
            reasons.append(
                Reason(
                    code="PHI_VIOLATION",
                    message_en=v.message_en,
                    message_ar=v.message_ar,
                    severity=sev,
                    source_checker=self.name,
                )
            )
        for v in rei_violations:
            sev = "critical" if v.status == ComplianceStatus.VIOLATION else "warning"
            blocking = blocking or sev == "critical"
            reasons.append(
                Reason(
                    code="REI_VIOLATION",
                    message_en=v.message_en,
                    message_ar=v.message_ar,
                    severity=sev,
                    source_checker=self.name,
                )
            )

        return CheckerResult(
            passed=not reasons,
            blocking=blocking,
            reasons=reasons,
            evidence={
                "phi_violations": len(phi_violations),
                "rei_violations": len(rei_violations),
                "planned_harvest_date": planned_harvest.isoformat(),
            },
        )


__all__ = [
    "ForbiddenSubstanceChecker",
    "DosageToleranceChecker",
    "RateRange",
    "PesticideComplianceCheckerAdapter",
    "PrescriptionChecker",  # re-export for convenience
    "CheckerResult",
]
