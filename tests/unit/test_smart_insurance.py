"""Tests for smart crop insurance."""
import pytest
from shared.crop_insurance.smart_insurance import (
    SmartInsuranceEngine,
    InsuranceType,
    RiskLevel,
)

class TestSmartInsurance:
    def setup_method(self):
        self.engine = SmartInsuranceEngine()

    def test_risk_assessment(self):
        risk = self.engine.assess_risk("F-001", "wheat")
        assert risk.risk_score > 0
        assert risk.risk_level_ar != ""

    def test_premium_calculation(self):
        premium = self.engine.calculate_premium(
            field_id="F-001", tenant_id="T-001",
            crop_type="wheat", area_hectares=10,
        )
        assert premium.premium_sar > 0
        assert premium.coverage_amount_sar > 0
        assert premium.message_ar != ""

    def test_parametric_triggers_drought(self):
        triggers = self.engine.check_parametric_triggers({"rainfall_mm_30d": 5})
        drought = [t for t in triggers if t.trigger_type == "drought"]
        assert len(drought) == 1
        assert drought[0].triggered is True

    def test_parametric_triggers_no_trigger(self):
        triggers = self.engine.check_parametric_triggers({"rainfall_mm_30d": 50})
        drought = [t for t in triggers if t.trigger_type == "drought"]
        assert drought[0].triggered is False
