"""
Crop Insurance Integration Module
=================================
وحدة تكامل التأمين الزراعي

Provides comprehensive crop insurance functionality for the SAHOOL platform:
- Insurance policy management (traditional and parametric/index-based)
- Claim submission, processing, and tracking
- Risk assessment based on field data, weather, and historical yields
- Weather-indexed insurance support
- Premium calculations with multiple risk factors

Author: SAHOOL Platform Team
Updated: January 2026
"""

# Models
# Claims Processing
from shared.crop_insurance.claims import (
    ClaimProcessor,
    ClaimStorage,
    ClaimValidator,
    PayoutCalculator,
    get_claim_processor,
    get_claim_status,
    process_parametric_trigger,
    submit_claim,
)
from shared.crop_insurance.models import (
    # Data classes
    BilingualText,
    ClaimEvidence,
    ClaimPayout,
    ClaimStatus,
    ClaimType,
    CoverageDetails,
    CoverageType,
    FieldRiskProfile,
    InsuranceClaim,
    # Error messages
    InsuranceErrorMessage,
    InsuranceErrors,
    InsuranceException,
    InsurancePolicy,
    InsuranceProvider,
    # Enums
    InsuranceType,
    ParametricTrigger,
    PayoutTriggerType,
    PolicyPremium,
    PolicyStatus,
    PremiumQuote,
    RiskFactor,
    RiskLevel,
    WeatherIndex,
    WeatherIndexType,
)

# Risk Assessment
from shared.crop_insurance.risk_assessment import (
    HistoricalYieldAnalyzer,
    RiskAssessmentEngine,
    RiskCalculator,
    WeatherRiskAnalyzer,
    assess_field_risk,
    calculate_premium_rate,
    get_risk_assessment_engine,
)

__all__ = [
    # Enums
    "InsuranceType",
    "PolicyStatus",
    "ClaimStatus",
    "ClaimType",
    "RiskLevel",
    "CoverageType",
    "PayoutTriggerType",
    "WeatherIndexType",
    # Data classes
    "BilingualText",
    "InsuranceProvider",
    "CoverageDetails",
    "WeatherIndex",
    "ParametricTrigger",
    "PolicyPremium",
    "InsurancePolicy",
    "ClaimEvidence",
    "InsuranceClaim",
    "ClaimPayout",
    "RiskFactor",
    "FieldRiskProfile",
    "PremiumQuote",
    # Errors
    "InsuranceErrorMessage",
    "InsuranceErrors",
    "InsuranceException",
    # Risk Assessment
    "RiskAssessmentEngine",
    "RiskCalculator",
    "WeatherRiskAnalyzer",
    "HistoricalYieldAnalyzer",
    "get_risk_assessment_engine",
    "assess_field_risk",
    "calculate_premium_rate",
    # Claims Processing
    "ClaimProcessor",
    "ClaimValidator",
    "PayoutCalculator",
    "ClaimStorage",
    "get_claim_processor",
    "submit_claim",
    "get_claim_status",
    "process_parametric_trigger",
]

__version__ = "16.0.0"
