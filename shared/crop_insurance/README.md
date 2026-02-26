# shared/crop_insurance

Crop insurance management for the SAHOOL platform. Covers policy lifecycle, risk assessment,
premium calculation, claim submission, and automatic parametric trigger processing for
both traditional indemnity-based and index/weather-based insurance products.

## File Structure

```
shared/crop_insurance/
├── __init__.py          # Public API exports
├── models.py            # Data models, enums, and error types
├── risk_assessment.py   # Risk scoring, premium rate calculation
└── claims.py            # Claim submission, validation, payout calculation
```

## Key Components

### models.py

All domain data classes and enumerations.

**Insurance types (`InsuranceType`):**
- `TRADITIONAL` - indemnity-based, field inspection required
- `PARAMETRIC` - index-triggered, automatic payouts
- `WEATHER_INDEX` - rainfall/temperature index
- `AREA_YIELD` - area-level yield index
- `HYBRID` - combination of methods

**Core data classes:**

| Class | Purpose |
|-------|---------|
| `InsurancePolicy` | Policy with coverage details, premium, and parametric triggers |
| `InsuranceClaim` | Claim record with status workflow and evidence attachments |
| `ClaimPayout` | Calculated payout with breakdown by coverage type |
| `FieldRiskProfile` | Aggregated risk profile for a field (weather + soil + location) |
| `RiskFactor` | Single risk factor with name, score, and weight |
| `WeatherIndex` | Index definition for parametric insurance (rainfall, temperature) |
| `ParametricTrigger` | Trigger conditions: threshold, measurement period, data source |
| `PolicyPremium` | Premium with base rate, risk loading, and discounts |
| `PremiumQuote` | Quote response with rate breakdown and validity period |
| `CoverageDetails` | Coverage amount, deductible, coverage types, and exclusions |

**Status enumerations:**
- `PolicyStatus`: DRAFT, PENDING_APPROVAL, ACTIVE, SUSPENDED, EXPIRED, CANCELLED, CLAIMED
- `ClaimStatus`: DRAFT, SUBMITTED, UNDER_REVIEW, FIELD_INSPECTION, APPROVED, REJECTED, PAID
- `RiskLevel`: LOW, MODERATE, HIGH, VERY_HIGH, EXTREME

### risk_assessment.py

Risk scoring engine and premium rate calculation.

| Class | Description |
|-------|-------------|
| `RiskAssessmentEngine` | Orchestrates full risk assessment from field data |
| `RiskCalculator` | Computes composite risk score from weighted factors |
| `WeatherRiskAnalyzer` | Analyses drought frequency, hail, frost, flood risk |
| `HistoricalYieldAnalyzer` | Yield volatility and trend analysis from historical records |
| `WeatherHistoryData` | Structured historical weather statistics for a station |
| `SoilData` | Soil type, drainage class, salinity, chemical properties |

**Convenience functions:**

| Function | Description |
|----------|-------------|
| `assess_field_risk(field_id, ...)` | Returns `FieldRiskProfile` with overall risk level |
| `calculate_premium_rate(risk_profile, coverage)` | Returns `PremiumQuote` |
| `get_risk_assessment_engine()` | Returns singleton engine instance |

### claims.py

Claim lifecycle management from submission to payout.

| Class | Description |
|-------|-------------|
| `ClaimProcessor` | Orchestrates the full claim workflow |
| `ClaimValidator` | Pre-submission validation (policy active, within coverage period) |
| `PayoutCalculator` | Calculates traditional and parametric payouts |
| `ClaimStorage` | Persistence layer for claims and audit records |
| `ValidationResult` | Validation outcome with bilingual error/warning messages |
| `PayoutCalculation` | Detailed payout breakdown with deductible and limits |

**Convenience functions:**

| Function | Description |
|----------|-------------|
| `submit_claim(policy_id, claim_type, ...)` | Creates and validates a new claim |
| `get_claim_status(claim_id)` | Returns current claim status |
| `process_parametric_trigger(trigger_id, index_value)` | Auto-processes weather index breach |
| `get_claim_processor()` | Returns singleton processor instance |

## Usage Example

```python
from shared.crop_insurance import (
    RiskAssessmentEngine,
    ClaimProcessor,
    InsuranceType,
    ClaimType,
    assess_field_risk,
    calculate_premium_rate,
    submit_claim,
    get_claim_status,
    process_parametric_trigger,
)

# 1. Assess field risk
risk_profile = await assess_field_risk(
    field_id="FIELD-003",
    tenant_id="tenant_001",
    crop_type="wheat",
    field_area_ha=8.5,
    region_id="qassim",
)
print(f"Risk level: {risk_profile.overall_risk_level}")  # e.g. MODERATE

# 2. Get premium quote
quote = await calculate_premium_rate(
    risk_profile=risk_profile,
    coverage_amount=85000,   # SAR
    insurance_type=InsuranceType.PARAMETRIC,
)
print(f"Annual premium: {quote.annual_premium} SAR")
print(f"Premium rate: {quote.premium_rate_percent:.2f}%")

# 3. Submit a traditional claim
claim = await submit_claim(
    policy_id="POL-2025-001",
    claim_type=ClaimType.WEATHER_DAMAGE,
    incident_date="2025-11-15",
    description_en="Hail storm damaged 40% of wheat crop",
    description_ar="أضرت العاصفة البردية بـ 40% من محصول القمح",
    estimated_loss_amount=34000,
)
print(f"Claim ID: {claim.id}, Status: {claim.status}")

# 4. Automatic parametric trigger (weather station data)
result = await process_parametric_trigger(
    trigger_id="TRIG-RAINFALL-001",
    observed_value=12.5,   # mm actual rainfall
    # Trigger fires when rainfall < threshold
)
```

## Insurance Types Reference

| Type | Trigger | Inspection | Payout Speed |
|------|---------|------------|--------------|
| Traditional | Field assessment | Required | 30-60 days |
| Parametric | Index threshold | Not required | 7-14 days |
| Weather Index | Rainfall/temp station data | Not required | Automatic |
| Area Yield | Regional yield statistics | Not required | Season-end |
| Hybrid | Mixed triggers | Partial | Varies |
