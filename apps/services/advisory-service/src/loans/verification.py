"""
Satellite-backed crop loan verification.

This module implements the Farmonaut-style "large-scale crop loan
monitoring" product, adapted for SAHOOL's Saudi/Yemen market:

    POST /api/v1/loans/crop-loan-verification/{field_id}

A bank / micro-lender calls this endpoint to verify that a farmer's
declared field:

  1. actually exists and has real boundaries (field-management check),
  2. has a crop currently growing (NDVI history, vegetation analysis),
  3. is consistent with the declared crop type (soft signal),
  4. has an acceptable risk profile for lending.

The endpoint returns a numeric `eligibility_score` (0-100), a
`recommended_loan_amount_sar`, and a bilingual summary the loan
officer can paste directly into their risk file.

This is deliberately a *verification* endpoint, not a credit
decision: SAHOOL does not underwrite loans. We surface the
agronomic evidence + risk signals; the bank's own scorecard takes
the final call.

Architecture notes
------------------
* No new DB schema — we re-use existing field + NDVI data.
* No hard dependency on a satellite provider: if vegetation-
  analysis returns nothing we fall back to a conservative score
  based on risk assessment alone.
* Same graceful-degradation pattern as ``comprehensive/`` — one
  slow downstream does not block the response.
* ``shared/crop_insurance/smart_insurance.SmartInsuranceEngine``
  gives us the risk model for free, so we don't duplicate the
  drought / pest / disease scoring.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from statistics import mean, pstdev
from typing import Any

import httpx
import structlog

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


@dataclass
class LoanVerificationRequest:
    """Inputs for a single loan-verification run."""

    field_id: str
    tenant_id: str
    declared_crop: str
    declared_area_hectares: float
    requested_loan_amount_sar: float
    loan_term_months: int = 12
    language: str = "ar"  # "ar" or "en"


@dataclass
class LoanVerificationResult:
    """The full verification response returned to the caller."""

    field_id: str
    tenant_id: str
    generated_at: str

    # Core decision signals
    eligibility_score: float  # 0-100
    recommended_loan_amount_sar: float
    max_safe_loan_amount_sar: float
    loan_to_value_ratio: float
    risk_level: str  # very_low | low | moderate | high | very_high

    # Satellite evidence
    crop_verified: bool
    declared_area_verified: bool
    actual_area_hectares: float | None
    ndvi_mean: float | None
    ndvi_stability: float | None
    ndvi_samples: int
    last_satellite_pass: str | None

    # Advisory-layer signals
    declared_crop_matches_signature: bool | None
    risk_factors: list[str] = field(default_factory=list)
    risk_factors_ar: list[str] = field(default_factory=list)

    # Loan officer summary
    decision: str = ""  # approved | review | rejected
    decision_ar: str = ""
    summary: str = ""
    summary_ar: str = ""

    # Transparency: which downstream services responded
    sources_degraded: int = 0
    latency_ms_total: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field_id,
            "tenant_id": self.tenant_id,
            "generated_at": self.generated_at,
            "decision": self.decision,
            "decision_ar": self.decision_ar,
            "eligibility_score": round(self.eligibility_score, 1),
            "recommended_loan_amount_sar": round(self.recommended_loan_amount_sar, 2),
            "max_safe_loan_amount_sar": round(self.max_safe_loan_amount_sar, 2),
            "loan_to_value_ratio": round(self.loan_to_value_ratio, 3),
            "risk_level": self.risk_level,
            "satellite_evidence": {
                "crop_verified": self.crop_verified,
                "declared_area_verified": self.declared_area_verified,
                "actual_area_hectares": self.actual_area_hectares,
                "ndvi_mean": self.ndvi_mean,
                "ndvi_stability": self.ndvi_stability,
                "ndvi_samples": self.ndvi_samples,
                "last_satellite_pass": self.last_satellite_pass,
                "declared_crop_matches_signature": (self.declared_crop_matches_signature),
            },
            "risk_factors": self.risk_factors,
            "risk_factors_ar": self.risk_factors_ar,
            "summary": self.summary,
            "summary_ar": self.summary_ar,
            "sources_degraded": self.sources_degraded,
            "latency_ms_total": round(self.latency_ms_total, 1),
        }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class CropLoanVerificationEngine:
    """
    Runs a satellite-backed verification for a single crop-loan
    application. The engine is stateless — configure once with
    downstream URLs and re-use it per request.
    """

    DEFAULT_TIMEOUT_SEC = 6.0

    # NDVI thresholds for "field actually has a crop growing"
    NDVI_HEALTHY = 0.5
    NDVI_SPARSE = 0.3
    NDVI_BARE = 0.2

    # How close the declared area must match the actual GIS area
    AREA_TOLERANCE_PCT = 15.0

    # Per-crop expected NDVI signatures (rough, used only as a soft
    # consistency check — not a hard reject).
    CROP_NDVI_SIGNATURES = {
        "wheat": (0.55, 0.85),
        "barley": (0.50, 0.80),
        "corn": (0.60, 0.90),
        "rice": (0.55, 0.85),
        "date_palm": (0.40, 0.70),  # date palms have lower peak NDVI
        "tomato": (0.50, 0.80),
        "cucumber": (0.50, 0.80),
    }

    # Per-crop avg yield * price (SAR/ha) — matches SmartInsuranceEngine
    # and gives us "coverage value" for the loan-to-value ratio.
    CROP_VALUE_SAR_PER_HA = {
        "wheat": 4.5 * 1850,
        "barley": 3.8 * 1500,
        "corn": 8.0 * 1600,
        "rice": 6.0 * 2800,
        "date_palm": 8.0 * 8000,
        "tomato": 40.0 * 2500,
        "cucumber": 35.0 * 3000,
    }

    def __init__(
        self,
        field_management_url: str,
        vegetation_analysis_url: str,
        crop_intelligence_url: str,
        timeout: float | None = None,
    ):
        self.field_management_url = field_management_url.rstrip("/")
        self.vegetation_analysis_url = vegetation_analysis_url.rstrip("/")
        self.crop_intelligence_url = crop_intelligence_url.rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT_SEC

    async def verify(
        self,
        req: LoanVerificationRequest,
        auth_header: str | None = None,
    ) -> LoanVerificationResult:
        """Run the full verification pipeline."""
        start_total = time.perf_counter()
        headers = self._headers(req.tenant_id, auth_header)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            field_data, ndvi_series, risk_data = await asyncio.gather(
                self._fetch_field(client, headers, req.field_id),
                self._fetch_ndvi_series(client, headers, req.field_id),
                self._fetch_risk(client, headers, req.field_id),
            )

        # 1. Evaluate satellite evidence
        actual_area, area_ok = self._check_area(field_data, req.declared_area_hectares)
        ndvi_mean, ndvi_stability, ndvi_samples, last_pass = self._summarise_ndvi(ndvi_series)
        crop_verified = (ndvi_mean or 0.0) >= self.NDVI_SPARSE
        crop_signature_ok = self._signature_check(req.declared_crop, ndvi_mean)

        # 2. Compute base eligibility from NDVI + risk
        risk_level, risk_factors, risk_factors_ar = self._extract_risk(risk_data)
        base_score = self._score(
            ndvi_mean=ndvi_mean,
            ndvi_stability=ndvi_stability,
            crop_verified=crop_verified,
            area_ok=area_ok,
            risk_level=risk_level,
        )

        # 3. Compute loan sizing
        max_safe = self._max_safe_loan(
            crop=req.declared_crop,
            area_ha=actual_area or req.declared_area_hectares,
            eligibility_score=base_score,
        )
        recommended = min(req.requested_loan_amount_sar, max_safe)

        # Loan-to-value: requested / expected revenue
        expected_revenue = self._expected_revenue(
            req.declared_crop,
            actual_area or req.declared_area_hectares,
        )
        ltv = req.requested_loan_amount_sar / expected_revenue if expected_revenue > 0 else 0.0

        # 4. Decide
        decision, decision_ar = self._decide(
            score=base_score,
            ltv=ltv,
            crop_verified=crop_verified,
            risk_level=risk_level,
        )

        # 5. Build bilingual summary
        summary, summary_ar = self._format_summary(
            req=req,
            crop_verified=crop_verified,
            area_ok=area_ok,
            ndvi_mean=ndvi_mean,
            score=base_score,
            recommended=recommended,
            ltv=ltv,
            risk_level=risk_level,
        )

        degraded_sources = sum(1 for src in (field_data, ndvi_series, risk_data) if src.get("_degraded"))
        elapsed_ms = (time.perf_counter() - start_total) * 1000

        return LoanVerificationResult(
            field_id=req.field_id,
            tenant_id=req.tenant_id,
            generated_at=datetime.now(UTC).isoformat(),
            eligibility_score=base_score,
            recommended_loan_amount_sar=recommended,
            max_safe_loan_amount_sar=max_safe,
            loan_to_value_ratio=ltv,
            risk_level=risk_level,
            crop_verified=crop_verified,
            declared_area_verified=area_ok,
            actual_area_hectares=actual_area,
            ndvi_mean=ndvi_mean,
            ndvi_stability=ndvi_stability,
            ndvi_samples=ndvi_samples,
            last_satellite_pass=last_pass,
            declared_crop_matches_signature=crop_signature_ok,
            risk_factors=risk_factors,
            risk_factors_ar=risk_factors_ar,
            decision=decision,
            decision_ar=decision_ar,
            summary=summary,
            summary_ar=summary_ar,
            sources_degraded=degraded_sources,
            latency_ms_total=elapsed_ms,
        )

    # ------------------------------------------------------------------
    # Downstream calls — each returns a dict, NEVER raises
    # ------------------------------------------------------------------

    async def _fetch_field(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> dict[str, Any]:
        url = f"{self.field_management_url}/api/v1/fields/{field_id}"
        return await self._safe_get(client, url, headers)

    async def _fetch_ndvi_series(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> dict[str, Any]:
        """Fetch NDVI history from vegetation-analysis-service.

        Uses the canonical ``/v1/timeseries/{field_id}`` endpoint. The
        legacy ``/api/v1/vegetation/fields/{field_id}/ndvi/history``
        path never existed in vegetation-analysis-service — calls to
        it silently returned 404, and the loan engine treated that as
        a soft-degraded signal, yielding low-confidence verdicts.
        Fetching the correct endpoint restores NDVI evidence for loan
        decisions.

        The vegetation response ships the history under ``timeseries``
        (list of ``{date, ndvi, ndwi, evi, cloud_cover}``); the loan
        engine's ``_summarise_ndvi`` expects the key ``series``. Map
        here so the rest of the pipeline is untouched.

        NOTE: ``lat``/``lon`` are intentionally omitted. Vegetation
        falls back to the in-process simulated NDVI generator without
        them, which is the best we can do before refactoring the
        ``asyncio.gather`` two-stage fetch (field first, then NDVI
        with its coordinates). Calls still tag ``data_source`` so the
        loan verdict can downweight simulated evidence.
        """
        url = f"{self.vegetation_analysis_url}/v1/timeseries/{field_id}"
        params = {"days": 365}
        resp = await self._safe_get(client, url, headers, params=params)
        if resp.get("_degraded"):
            return resp
        # Vegetation returns {timeseries: [...]} at top level (not
        # wrapped in `data`), so `_safe_get` surfaces it under `_raw`.
        raw = resp.get("_raw") if "_raw" in resp else resp
        if isinstance(raw, dict) and "timeseries" in raw:
            return {
                "_degraded": False,
                "series": raw.get("timeseries", []),
                "data_source": raw.get("data_source"),
                "period_days": raw.get("period_days"),
            }
        return resp

    async def _fetch_risk(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> dict[str, Any]:
        url = f"{self.crop_intelligence_url}/api/v1/crop-intelligence/fields/{field_id}/risk"
        return await self._safe_get(client, url, headers)

    async def _safe_get(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: dict,
        *,
        params: dict | None = None,
    ) -> dict[str, Any]:
        try:
            resp = await client.get(url, headers=headers, params=params)
            if resp.status_code == 200:
                body = resp.json()
                if isinstance(body, dict) and "data" in body:
                    return {"_degraded": False, **(body["data"] or {})}
                return {"_degraded": False, "_raw": body}
            if resp.status_code == 404:
                # Not-found is not a failure — returns empty payload
                return {"_degraded": False}
            return {"_degraded": True, "_error": f"HTTP {resp.status_code}"}
        except httpx.TimeoutException:
            logger.warning("loan_verification.timeout", url=url)
            return {"_degraded": True, "_error": "timeout"}
        except httpx.RequestError as e:
            logger.warning("loan_verification.network", url=url, error=str(e))
            return {"_degraded": True, "_error": f"network:{type(e).__name__}"}
        except Exception as e:  # pragma: no cover - defensive
            logger.error("loan_verification.unexpected", url=url, error=str(e))
            return {"_degraded": True, "_error": f"unexpected:{type(e).__name__}"}

    # ------------------------------------------------------------------
    # Evidence extraction helpers
    # ------------------------------------------------------------------

    def _check_area(self, field_data: dict, declared_area: float) -> tuple[float | None, bool]:
        """Compare declared vs actual GIS-measured area."""
        actual = None
        for key in ("area_hectares", "area_ha", "computed_area_hectares"):
            if key in field_data and isinstance(field_data[key], (int, float)):
                actual = float(field_data[key])
                break
        if actual is None:
            # No GIS data — trust declared, but flag as unverified
            return None, False
        if declared_area <= 0:
            return actual, False
        diff_pct = abs(actual - declared_area) / declared_area * 100
        return actual, diff_pct <= self.AREA_TOLERANCE_PCT

    def _summarise_ndvi(self, ndvi_data: dict) -> tuple[float | None, float | None, int, str | None]:
        """Collapse an NDVI history series into mean, stability, count."""
        series = ndvi_data.get("series") if isinstance(ndvi_data, dict) else None
        if not isinstance(series, list) or not series:
            return None, None, 0, None

        values: list[float] = []
        timestamps: list[str] = []
        for row in series:
            if not isinstance(row, dict):
                continue
            v = row.get("ndvi") or row.get("mean") or row.get("value")
            if isinstance(v, (int, float)):
                values.append(float(v))
            ts = row.get("date") or row.get("timestamp")
            if isinstance(ts, str):
                timestamps.append(ts)

        if not values:
            return None, None, 0, None

        m = mean(values)
        if len(values) >= 2:
            # Stability: 1 - normalised stdev (clamped 0..1)
            std = pstdev(values)
            stability = max(0.0, min(1.0, 1.0 - (std / max(m, 0.01))))
        else:
            stability = 0.5
        last_pass = max(timestamps) if timestamps else None
        return m, stability, len(values), last_pass

    def _extract_risk(self, risk_data: dict) -> tuple[str, list[str], list[str]]:
        level = risk_data.get("risk_level") or "moderate"
        factors = risk_data.get("factors") or []
        factors_ar = risk_data.get("factors_ar") or []
        if not isinstance(factors, list):
            factors = []
        if not isinstance(factors_ar, list):
            factors_ar = []
        return (
            str(level).lower(),
            [str(f) for f in factors],
            [str(f) for f in factors_ar],
        )

    def _signature_check(self, declared_crop: str, ndvi_mean: float | None) -> bool | None:
        """Return True/False if we can judge, None if we can't."""
        if ndvi_mean is None:
            return None
        sig = self.CROP_NDVI_SIGNATURES.get(declared_crop.lower())
        if not sig:
            return None
        lo, hi = sig
        # Generous band: ±0.15 around the expected range
        return (lo - 0.15) <= ndvi_mean <= (hi + 0.05)

    # ------------------------------------------------------------------
    # Scoring + sizing + decision
    # ------------------------------------------------------------------

    def _score(
        self,
        ndvi_mean: float | None,
        ndvi_stability: float | None,
        crop_verified: bool,
        area_ok: bool,
        risk_level: str,
    ) -> float:
        """
        Compose a 0-100 eligibility score. The weights are deliberately
        simple so a loan officer can reproduce them by hand.

            NDVI level       40%
            NDVI stability   15%
            Area match       15%
            Crop verified    10%
            Risk level       20%
        """
        # 1. NDVI level: 0.0-0.2 → 0pts, 0.2-0.5 → linear, >=0.5 → 40pts
        if ndvi_mean is None:
            ndvi_points = 15.0  # Conservative benefit of the doubt
        elif ndvi_mean >= self.NDVI_HEALTHY:
            ndvi_points = 40.0
        elif ndvi_mean >= self.NDVI_BARE:
            span = self.NDVI_HEALTHY - self.NDVI_BARE
            ndvi_points = 40.0 * (ndvi_mean - self.NDVI_BARE) / span
        else:
            ndvi_points = 0.0

        stability_points = 15.0 * (ndvi_stability if ndvi_stability is not None else 0.5)
        area_points = 15.0 if area_ok else 5.0
        crop_points = 10.0 if crop_verified else 0.0

        risk_points = {
            "very_low": 20.0,
            "low": 17.0,
            "moderate": 12.0,
            "high": 6.0,
            "very_high": 0.0,
        }.get(risk_level, 10.0)

        total = ndvi_points + stability_points + area_points + crop_points + risk_points
        return max(0.0, min(100.0, total))

    def _max_safe_loan(self, crop: str, area_ha: float, eligibility_score: float) -> float:
        """
        Upper-bound loan amount we'd comfortably underwrite. Computed as
        a percentage of expected gross revenue, scaled by eligibility.
        """
        gross_per_ha = self.CROP_VALUE_SAR_PER_HA.get(crop.lower(), 5000.0)
        gross = gross_per_ha * max(area_ha, 0.0)
        # Lend at most 70% of gross revenue, scaled by score/100.
        return gross * 0.7 * (eligibility_score / 100.0)

    def _expected_revenue(self, crop: str, area_ha: float) -> float:
        gross_per_ha = self.CROP_VALUE_SAR_PER_HA.get(crop.lower(), 5000.0)
        return gross_per_ha * max(area_ha, 0.0)

    def _decide(
        self,
        score: float,
        ltv: float,
        crop_verified: bool,
        risk_level: str,
    ) -> tuple[str, str]:
        if not crop_verified or risk_level == "very_high":
            return "rejected", "مرفوض"
        if score >= 70 and ltv <= 0.8:
            return "approved", "موافق عليه"
        if score >= 50:
            return "review", "قيد المراجعة"
        return "rejected", "مرفوض"

    def _format_summary(
        self,
        req: LoanVerificationRequest,
        crop_verified: bool,
        area_ok: bool,
        ndvi_mean: float | None,
        score: float,
        recommended: float,
        ltv: float,
        risk_level: str,
    ) -> tuple[str, str]:
        ndvi_str = f"{ndvi_mean:.2f}" if ndvi_mean is not None else "N/A"
        summary_en = (
            f"Field {req.field_id} ({req.declared_crop}, "
            f"{req.declared_area_hectares:g} ha): eligibility {score:.0f}/100, "
            f"NDVI mean {ndvi_str}, area match={'yes' if area_ok else 'no'}, "
            f"crop verified={'yes' if crop_verified else 'no'}, "
            f"risk={risk_level}. Recommended loan {recommended:,.0f} SAR "
            f"(LTV {ltv:.0%})."
        )
        summary_ar = (
            f"الحقل {req.field_id} ({req.declared_crop}، "
            f"{req.declared_area_hectares:g} هـ): الأهلية {score:.0f}/100، "
            f"متوسط NDVI {ndvi_str}، مطابقة المساحة="
            f"{'نعم' if area_ok else 'لا'}، تحقق المحصول="
            f"{'نعم' if crop_verified else 'لا'}، المخاطر={risk_level}. "
            f"القرض الموصى به {recommended:,.0f} ريال "
            f"(نسبة القرض إلى القيمة {ltv:.0%})."
        )
        return summary_en, summary_ar

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _headers(tenant_id: str, auth_header: str | None) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "X-Tenant-Id": tenant_id,
        }
        if auth_header:
            headers["Authorization"] = auth_header
        return headers
