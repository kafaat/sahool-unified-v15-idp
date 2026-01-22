"""
SAHOOL Pesticide Compliance Module - وحدة سلامة المبيدات
Critical food and worker safety module

Features:
- Pre-Harvest Interval (PHI) tracking - فترة ما قبل الحصاد
- Re-Entry Interval (REI) tracking - فترة إعادة الدخول
- Tank mix compatibility checking - توافق خلطات الخزان
- PPE requirements - متطلبات معدات الحماية الشخصية
- Spray drift risk assessment - تقييم مخاطر انجراف الرش

Version: 1.0.0
"""

from .models import (
    Pesticide,
    PesticideApplication,
    PHIViolation,
    REIViolation,
    TankMixCompatibility,
    PPERequirement,
    SprayDriftRisk,
    ComplianceCheck,
    ComplianceStatus,
)
from .database import (
    PESTICIDE_DATABASE,
    TANK_MIX_COMPATIBILITY,
    get_pesticide,
    search_pesticides,
)
from .checker import (
    PesticideComplianceChecker,
    check_phi_compliance,
    check_rei_compliance,
    check_tank_mix_compatibility,
    get_ppe_requirements,
    assess_spray_drift_risk,
)
from .alerts import (
    generate_phi_alert,
    generate_rei_alert,
    generate_tank_mix_alert,
)

__all__ = [
    # Models
    "Pesticide",
    "PesticideApplication",
    "PHIViolation",
    "REIViolation",
    "TankMixCompatibility",
    "PPERequirement",
    "SprayDriftRisk",
    "ComplianceCheck",
    "ComplianceStatus",
    # Database
    "PESTICIDE_DATABASE",
    "TANK_MIX_COMPATIBILITY",
    "get_pesticide",
    "search_pesticides",
    # Checker
    "PesticideComplianceChecker",
    "check_phi_compliance",
    "check_rei_compliance",
    "check_tank_mix_compatibility",
    "get_ppe_requirements",
    "assess_spray_drift_risk",
    # Alerts
    "generate_phi_alert",
    "generate_rei_alert",
    "generate_tank_mix_alert",
]
