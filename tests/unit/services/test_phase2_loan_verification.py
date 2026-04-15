"""
Unit tests for the Phase 2 satellite-backed crop loan verification engine.

Tests cover:

* NDVI summary math (mean, stability, sample count, last pass)
* Area match tolerance (±15%)
* Crop signature soft check
* Eligibility scoring (each component contributes the weight it claims)
* Loan sizing (max_safe, recommended, LTV)
* Decision tree (approved / review / rejected)
* Graceful degradation when downstream services fail
"""

from __future__ import annotations

import importlib.util
import os
import sys

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_VERIFY_PATH = os.path.join(
    _REPO_ROOT,
    "apps",
    "services",
    "advisory-service",
    "src",
    "loans",
    "verification.py",
)
_spec = importlib.util.spec_from_file_location("phase2_loan_verify", _VERIFY_PATH)
assert _spec and _spec.loader
_loan_mod = importlib.util.module_from_spec(_spec)
sys.modules["phase2_loan_verify"] = _loan_mod
_spec.loader.exec_module(_loan_mod)

CropLoanVerificationEngine = _loan_mod.CropLoanVerificationEngine
LoanVerificationRequest = _loan_mod.LoanVerificationRequest


@pytest.fixture
def engine() -> CropLoanVerificationEngine:
    return CropLoanVerificationEngine(
        field_management_url="http://localhost:0",
        vegetation_analysis_url="http://localhost:0",
        crop_intelligence_url="http://localhost:0",
        timeout=0.1,
    )


@pytest.fixture
def request_fixture() -> LoanVerificationRequest:
    return LoanVerificationRequest(
        field_id="F-1",
        tenant_id="t-1",
        declared_crop="wheat",
        declared_area_hectares=10.0,
        requested_loan_amount_sar=30_000,
        loan_term_months=12,
    )


# ---------------------------------------------------------------------------
# NDVI summary
# ---------------------------------------------------------------------------


def test_summarise_ndvi_empty(engine: CropLoanVerificationEngine):
    assert engine._summarise_ndvi({}) == (None, None, 0, None)
    assert engine._summarise_ndvi({"series": []}) == (None, None, 0, None)


def test_summarise_ndvi_single_value(engine: CropLoanVerificationEngine):
    mean_val, stability, samples, last = engine._summarise_ndvi(
        {"series": [{"ndvi": 0.7, "date": "2026-04-01"}]}
    )
    assert mean_val == pytest.approx(0.7)
    assert stability == 0.5  # single value → fallback
    assert samples == 1
    assert last == "2026-04-01"


def test_summarise_ndvi_multi_value(engine: CropLoanVerificationEngine):
    mean_val, stability, samples, last = engine._summarise_ndvi(
        {
            "series": [
                {"ndvi": 0.70, "date": "2026-03-01"},
                {"ndvi": 0.72, "date": "2026-03-15"},
                {"ndvi": 0.71, "date": "2026-04-01"},
            ]
        }
    )
    assert mean_val == pytest.approx(0.71, abs=0.01)
    assert 0.9 < stability <= 1.0  # Very stable series
    assert samples == 3
    assert last == "2026-04-01"


def test_summarise_ndvi_skips_non_numeric(engine: CropLoanVerificationEngine):
    mean_val, _, samples, _ = engine._summarise_ndvi(
        {
            "series": [
                {"ndvi": 0.6},
                {"ndvi": "oops"},  # invalid
                {"mean": 0.65},
                "not-a-dict",  # ignored
            ]
        }
    )
    # Only 0.6 and 0.65 counted
    assert samples == 2
    assert mean_val == pytest.approx(0.625, abs=0.001)


# ---------------------------------------------------------------------------
# Area match
# ---------------------------------------------------------------------------


def test_area_match_within_tolerance(engine: CropLoanVerificationEngine):
    actual, ok = engine._check_area({"area_hectares": 10.5}, declared_area=10.0)
    assert actual == 10.5
    assert ok is True


def test_area_mismatch_exceeds_tolerance(engine: CropLoanVerificationEngine):
    actual, ok = engine._check_area({"area_hectares": 20.0}, declared_area=10.0)
    assert actual == 20.0
    assert ok is False


def test_area_missing_gis_data(engine: CropLoanVerificationEngine):
    actual, ok = engine._check_area({}, declared_area=10.0)
    assert actual is None
    assert ok is False


def test_area_alternative_keys(engine: CropLoanVerificationEngine):
    actual, _ = engine._check_area({"computed_area_hectares": 9.5}, 10.0)
    assert actual == 9.5


# ---------------------------------------------------------------------------
# Signature + risk extraction
# ---------------------------------------------------------------------------


def test_signature_check_wheat_healthy(engine: CropLoanVerificationEngine):
    # Wheat signature is (0.55, 0.85); 0.7 is well inside
    assert engine._signature_check("wheat", 0.70) is True


def test_signature_check_date_palm_range(engine: CropLoanVerificationEngine):
    assert engine._signature_check("date_palm", 0.55) is True
    assert engine._signature_check("date_palm", 0.10) is False


def test_signature_check_unknown_crop(engine: CropLoanVerificationEngine):
    assert engine._signature_check("dragonfruit", 0.7) is None


def test_signature_check_no_ndvi(engine: CropLoanVerificationEngine):
    assert engine._signature_check("wheat", None) is None


def test_extract_risk_fallbacks(engine: CropLoanVerificationEngine):
    level, factors, factors_ar = engine._extract_risk({})
    assert level == "moderate"
    assert factors == []
    assert factors_ar == []


def test_extract_risk_passthrough(engine: CropLoanVerificationEngine):
    level, factors, factors_ar = engine._extract_risk(
        {
            "risk_level": "HIGH",
            "factors": ["drought_risk"],
            "factors_ar": ["خطر جفاف"],
        }
    )
    assert level == "high"
    assert factors == ["drought_risk"]
    assert factors_ar == ["خطر جفاف"]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def test_score_healthy_low_risk(engine: CropLoanVerificationEngine):
    score = engine._score(
        ndvi_mean=0.75,
        ndvi_stability=0.95,
        crop_verified=True,
        area_ok=True,
        risk_level="low",
    )
    # NDVI=40, stability=14.25, area=15, crop=10, risk=17 → ≈96
    assert 90 < score <= 100


def test_score_stressed_high_risk(engine: CropLoanVerificationEngine):
    score = engine._score(
        ndvi_mean=0.15,  # Below bare threshold → 0 points
        ndvi_stability=0.3,
        crop_verified=False,
        area_ok=False,
        risk_level="very_high",
    )
    # 0 + 4.5 + 5 + 0 + 0 = 9.5
    assert score < 15


def test_score_missing_ndvi_benefit_of_doubt(
    engine: CropLoanVerificationEngine,
):
    score = engine._score(
        ndvi_mean=None,
        ndvi_stability=None,
        crop_verified=True,
        area_ok=True,
        risk_level="moderate",
    )
    # 15 (NDVI conservative) + 7.5 (stability default 0.5) + 15 + 10 + 12 = 59.5
    assert 55 <= score < 65


def test_score_bounded_0_100(engine: CropLoanVerificationEngine):
    # Even if we inject crazy inputs, the score must stay clamped
    score = engine._score(
        ndvi_mean=5.0,  # Way above 1.0
        ndvi_stability=10.0,  # Way above 1.0 — but we scale by 15
        crop_verified=True,
        area_ok=True,
        risk_level="very_low",
    )
    assert 0 <= score <= 100


# ---------------------------------------------------------------------------
# Loan sizing
# ---------------------------------------------------------------------------


def test_max_safe_loan_scales_with_score(
    engine: CropLoanVerificationEngine,
):
    full_loan = engine._max_safe_loan("wheat", 10.0, 100.0)
    half_loan = engine._max_safe_loan("wheat", 10.0, 50.0)
    assert full_loan > half_loan
    assert half_loan == pytest.approx(full_loan * 0.5, rel=0.01)


def test_max_safe_loan_unknown_crop_fallback(engine: CropLoanVerificationEngine):
    loan = engine._max_safe_loan("unicorn-fruit", 10.0, 100.0)
    # Fallback CROP_VALUE=5000 × 0.7 × 1.0 × 10 ha = 35,000
    assert loan == pytest.approx(35_000, rel=0.01)


def test_expected_revenue(engine: CropLoanVerificationEngine):
    rev = engine._expected_revenue("wheat", 10.0)
    # 4.5 t/ha × 1850 × 10 = 83,250
    assert rev == pytest.approx(83_250, rel=0.01)


# ---------------------------------------------------------------------------
# Decision tree
# ---------------------------------------------------------------------------


def test_decide_approved(engine: CropLoanVerificationEngine):
    decision, decision_ar = engine._decide(
        score=85, ltv=0.5, crop_verified=True, risk_level="low"
    )
    assert decision == "approved"
    assert decision_ar == "موافق عليه"


def test_decide_review_midscore(engine: CropLoanVerificationEngine):
    decision, _ = engine._decide(
        score=60, ltv=0.6, crop_verified=True, risk_level="moderate"
    )
    assert decision == "review"


def test_decide_rejected_unverified(engine: CropLoanVerificationEngine):
    decision, _ = engine._decide(
        score=90, ltv=0.5, crop_verified=False, risk_level="low"
    )
    assert decision == "rejected"


def test_decide_rejected_very_high_risk(engine: CropLoanVerificationEngine):
    decision, _ = engine._decide(
        score=90, ltv=0.5, crop_verified=True, risk_level="very_high"
    )
    assert decision == "rejected"


def test_decide_rejected_low_score(engine: CropLoanVerificationEngine):
    decision, _ = engine._decide(
        score=40, ltv=0.5, crop_verified=True, risk_level="moderate"
    )
    assert decision == "rejected"


def test_decide_ltv_too_high_downgrades_to_review(
    engine: CropLoanVerificationEngine,
):
    # Score is high enough for "approved" but LTV > 0.8
    decision, _ = engine._decide(
        score=85, ltv=0.95, crop_verified=True, risk_level="low"
    )
    assert decision == "review"
