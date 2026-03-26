"""
Tests for Explainability Layer Module
اختبارات وحدة طبقة التفسير
"""

from datetime import datetime

import pytest

from shared.ai.explainability import (
    AlternativeRecommendation,
    ContributingFactor,
    ExplainabilityEngine,
    Explanation,
    ExplanationType,
    FactorType,
    ImpactLevel,
    RuleExplanation,
    explain_recommendation,
    get_explainability_engine,
)


class TestContributingFactor:
    """Tests for ContributingFactor"""

    def test_create_factor(self):
        """Test creating a contributing factor"""
        factor = ContributingFactor(
            factor_type=FactorType.SOIL,
            name="Soil Moisture",
            name_ar="رطوبة التربة",
            value="35%",
            description="Soil moisture is low",
            description_ar="رطوبة التربة منخفضة",
            impact=ImpactLevel.HIGH,
            weight=0.35,
            direction="supports",
        )
        assert factor.name == "Soil Moisture"
        assert factor.name_ar == "رطوبة التربة"
        assert factor.impact == ImpactLevel.HIGH
        assert factor.weight == 0.35

    def test_factor_to_dict(self):
        """Test converting factor to dictionary"""
        factor = ContributingFactor(
            factor_type=FactorType.WEATHER,
            name="Temperature",
            name_ar="درجة الحرارة",
            value="28°C",
            description="Temperature is optimal",
            description_ar="درجة الحرارة مثالية",
            impact=ImpactLevel.MEDIUM,
            weight=0.25,
            direction="neutral",
            source="Weather Service",
            confidence=0.9,
        )
        d = factor.to_dict()
        assert d["factor_type"] == "weather"
        assert d["name"] == "Temperature"
        assert d["impact"] == "medium"
        assert d["source"] == "Weather Service"
        assert d["confidence"] == 0.9


class TestAlternativeRecommendation:
    """Tests for AlternativeRecommendation"""

    def test_create_alternative(self):
        """Test creating an alternative recommendation"""
        alt = AlternativeRecommendation(
            title="Drip Irrigation",
            title_ar="الري بالتنقيط",
            description="Use drip irrigation instead",
            description_ar="استخدم الري بالتنقيط بدلاً من ذلك",
            score=75,
            rank=2,
            rejection_reasons=["Higher initial cost"],
            rejection_reasons_ar=["تكلفة أولية أعلى"],
        )
        assert alt.title == "Drip Irrigation"
        assert alt.score == 75
        assert alt.rank == 2
        assert len(alt.rejection_reasons) == 1

    def test_alternative_with_pros_cons(self):
        """Test alternative with pros and cons"""
        alt = AlternativeRecommendation(
            title="Manual Irrigation",
            title_ar="الري اليدوي",
            description="Water manually",
            description_ar="ري يدوي",
            score=50,
            rank=3,
            pros=["Low cost", "Simple"],
            cons=["Labor intensive", "Inconsistent"],
            pros_ar=["تكلفة منخفضة", "بسيط"],
            cons_ar=["يتطلب عمالة", "غير متسق"],
        )
        assert len(alt.pros) == 2
        assert len(alt.cons) == 2
        assert "Low cost" in alt.pros

    def test_alternative_to_dict(self):
        """Test converting alternative to dictionary"""
        alt = AlternativeRecommendation(
            title="Test",
            title_ar="اختبار",
            description="Test desc",
            description_ar="وصف الاختبار",
            score=80,
            rank=1,
        )
        d = alt.to_dict()
        assert d["title"] == "Test"
        assert d["score"] == 80


class TestRuleExplanation:
    """Tests for RuleExplanation"""

    def test_create_rule(self):
        """Test creating a rule explanation"""
        rule = RuleExplanation(
            rule_id="IRR_001",
            rule_name="Soil Moisture Threshold",
            rule_name_ar="عتبة رطوبة التربة",
            condition="Soil moisture < 40%",
            condition_ar="رطوبة التربة < 40%",
            action="Apply irrigation",
            action_ar="تطبيق الري",
            matched=True,
            match_details="Current moisture: 35%",
            match_details_ar="الرطوبة الحالية: 35%",
        )
        assert rule.rule_id == "IRR_001"
        assert rule.matched is True

    def test_rule_to_dict(self):
        """Test converting rule to dictionary"""
        rule = RuleExplanation(
            rule_id="FERT_001",
            rule_name="Nitrogen Rule",
            rule_name_ar="قاعدة النيتروجين",
            condition="N < 25 ppm",
            condition_ar="ن < 25 جزء",
            action="Apply urea",
            action_ar="تطبيق اليوريا",
            matched=True,
            match_details="N = 18 ppm",
            match_details_ar="ن = 18 جزء",
            category="fertilizer",
        )
        d = rule.to_dict()
        assert d["rule_id"] == "FERT_001"
        assert d["category"] == "fertilizer"


class TestExplanation:
    """Tests for Explanation"""

    @pytest.fixture
    def sample_factors(self):
        """Create sample factors"""
        return [
            ContributingFactor(
                factor_type=FactorType.SOIL,
                name="Moisture",
                name_ar="الرطوبة",
                value="35%",
                description="Low moisture",
                description_ar="رطوبة منخفضة",
                impact=ImpactLevel.CRITICAL,
                weight=0.4,
                direction="supports",
            ),
            ContributingFactor(
                factor_type=FactorType.WEATHER,
                name="Forecast",
                name_ar="التوقعات",
                value="No rain",
                description="No rain expected",
                description_ar="لا أمطار متوقعة",
                impact=ImpactLevel.HIGH,
                weight=0.3,
                direction="supports",
            ),
            ContributingFactor(
                factor_type=FactorType.CROP_STAGE,
                name="Growth Stage",
                name_ar="مرحلة النمو",
                value="Tillering",
                description="Active growth",
                description_ar="نمو نشط",
                impact=ImpactLevel.LOW,
                weight=0.1,
                direction="neutral",
            ),
        ]

    def test_create_explanation(self, sample_factors):
        """Test creating an explanation"""
        explanation = Explanation(
            recommendation_id="rec_001",
            explanation_type=ExplanationType.FACTOR_BASED,
            summary="Based on soil moisture and weather",
            summary_ar="بناءً على رطوبة التربة والطقس",
            factors=sample_factors,
            overall_confidence=0.85,
        )
        assert explanation.recommendation_id == "rec_001"
        assert explanation.overall_confidence == 0.85
        assert len(explanation.factors) == 3

    def test_primary_factors(self, sample_factors):
        """Test getting primary factors"""
        explanation = Explanation(
            recommendation_id="rec_001",
            explanation_type=ExplanationType.FACTOR_BASED,
            factors=sample_factors,
        )
        primary = explanation.primary_factors
        # Should only include CRITICAL and HIGH impact
        assert len(primary) == 2
        assert all(f.impact in [ImpactLevel.CRITICAL, ImpactLevel.HIGH] for f in primary)

    def test_factor_summary(self, sample_factors):
        """Test factor summary generation"""
        explanation = Explanation(
            recommendation_id="rec_001",
            explanation_type=ExplanationType.FACTOR_BASED,
            factors=sample_factors,
        )
        summary = explanation.factor_summary
        assert "Moisture" in summary
        assert "Based on:" in summary

    def test_factor_summary_ar(self, sample_factors):
        """Test Arabic factor summary"""
        explanation = Explanation(
            recommendation_id="rec_001",
            explanation_type=ExplanationType.FACTOR_BASED,
            factors=sample_factors,
        )
        summary_ar = explanation.factor_summary_ar
        assert "الرطوبة" in summary_ar
        assert "بناءً على:" in summary_ar

    def test_explanation_to_dict(self, sample_factors):
        """Test converting explanation to dictionary"""
        explanation = Explanation(
            recommendation_id="rec_001",
            explanation_type=ExplanationType.RULE_BASED,
            factors=sample_factors,
            overall_confidence=0.9,
            data_sources=["IoT Sensors", "Weather API"],
        )
        d = explanation.to_dict()
        assert d["recommendation_id"] == "rec_001"
        assert d["explanation_type"] == "rule_based"
        assert len(d["factors"]) == 3
        assert len(d["data_sources"]) == 2

    def test_explanation_to_json(self, sample_factors):
        """Test converting explanation to JSON"""
        explanation = Explanation(
            recommendation_id="rec_001",
            explanation_type=ExplanationType.FACTOR_BASED,
            factors=sample_factors,
        )
        json_str = explanation.to_json()
        assert "rec_001" in json_str
        assert "factor_based" in json_str


class TestExplainabilityEngine:
    """Tests for ExplainabilityEngine"""

    @pytest.fixture
    def engine(self):
        """Create engine instance"""
        return ExplainabilityEngine()

    @pytest.fixture
    def sample_factors(self):
        """Create sample factors for testing"""
        return [
            ContributingFactor(
                factor_type=FactorType.SOIL,
                name="Moisture",
                name_ar="الرطوبة",
                value="35%",
                description="Low moisture",
                description_ar="رطوبة منخفضة",
                impact=ImpactLevel.HIGH,
                weight=0.4,
                direction="supports",
                confidence=0.9,
            ),
        ]

    def test_engine_creation(self, engine):
        """Test engine creation"""
        assert engine.language == "both"

    def test_engine_with_language(self):
        """Test engine with specific language"""
        engine = ExplainabilityEngine(language="ar")
        assert engine.language == "ar"

    def test_explain_basic(self, engine, sample_factors):
        """Test basic explanation generation"""
        explanation = engine.explain(
            recommendation_id="rec_001",
            recommendation_type="irrigation",
            factors=sample_factors,
            confidence=0.85,
        )
        assert explanation.recommendation_id == "rec_001"
        assert explanation.overall_confidence == 0.85
        assert len(explanation.factors) == 1

    def test_explain_with_rules(self, engine, sample_factors):
        """Test explanation with rules"""
        rules = [
            RuleExplanation(
                rule_id="IRR_001",
                rule_name="Moisture Rule",
                rule_name_ar="قاعدة الرطوبة",
                condition="SM < 40%",
                condition_ar="الرطوبة < 40%",
                action="Irrigate",
                action_ar="الري",
                matched=True,
                match_details="SM = 35%",
                match_details_ar="الرطوبة = 35%",
            ),
        ]
        explanation = engine.explain(
            recommendation_id="rec_001",
            recommendation_type="irrigation",
            factors=sample_factors,
            rules_applied=rules,
        )
        assert len(explanation.rules) == 1
        assert explanation.rules[0].matched is True

    def test_explain_with_alternatives(self, engine, sample_factors):
        """Test explanation with alternatives"""
        alternatives = [
            AlternativeRecommendation(
                title="Wait for rain",
                title_ar="انتظار المطر",
                description="Delay irrigation",
                description_ar="تأخير الري",
                score=60,
                rank=2,
                rejection_reasons=["No rain forecast"],
            ),
        ]
        explanation = engine.explain(
            recommendation_id="rec_001",
            recommendation_type="irrigation",
            factors=sample_factors,
            alternatives_considered=alternatives,
        )
        assert len(explanation.alternatives) == 1

    def test_determine_type_factor_based(self, engine):
        """Test determining factor-based explanation type"""
        factors = [
            ContributingFactor(
                factor_type=FactorType.SOIL,
                name="Test",
                name_ar="اختبار",
                value="1",
                description="d",
                description_ar="و",
                impact=ImpactLevel.HIGH,
                weight=0.5,
                direction="supports",
            ),
        ]
        result = engine._determine_type(factors, [])
        assert result == ExplanationType.FACTOR_BASED

    def test_determine_type_rule_based(self, engine):
        """Test determining rule-based explanation type"""
        rules = [
            RuleExplanation(
                rule_id="R1",
                rule_name="Rule 1",
                rule_name_ar="قاعدة 1",
                condition="c",
                condition_ar="ش",
                action="a",
                action_ar="ع",
                matched=True,
                match_details="d",
                match_details_ar="ت",
            ),
            RuleExplanation(
                rule_id="R2",
                rule_name="Rule 2",
                rule_name_ar="قاعدة 2",
                condition="c",
                condition_ar="ش",
                action="a",
                action_ar="ع",
                matched=True,
                match_details="d",
                match_details_ar="ت",
            ),
        ]
        result = engine._determine_type([], rules)
        assert result == ExplanationType.RULE_BASED

    def test_explain_irrigation(self, engine):
        """Test irrigation explanation"""
        explanation = engine.explain_irrigation(
            recommendation_id="irr_001",
            soil_moisture=35.0,
            weather_forecast={"rain_probability": 10, "temperature": 28},
            crop_stage="tillering",
            et_value=5.5,
            recommended_amount_mm=25.0,
        )
        assert explanation.recommendation_id == "irr_001"
        assert len(explanation.factors) >= 4
        assert explanation.context["recommended_amount_mm"] == 25.0

    def test_explain_irrigation_with_rain(self, engine):
        """Test irrigation explanation when rain expected"""
        explanation = engine.explain_irrigation(
            recommendation_id="irr_002",
            soil_moisture=45.0,
            weather_forecast={"rain_probability": 70, "temperature": 25},
            crop_stage="heading",
            et_value=4.0,
            recommended_amount_mm=15.0,
        )
        # Confidence should be lower when rain expected
        assert explanation.overall_confidence < 0.8

    def test_explain_irrigation_with_alternatives(self, engine):
        """Test irrigation explanation with alternatives"""
        alternatives = [
            {"title": "Delay irrigation", "title_ar": "تأخير الري", "score": 70},
        ]
        explanation = engine.explain_irrigation(
            recommendation_id="irr_003",
            soil_moisture=40.0,
            weather_forecast={"rain_probability": 30, "temperature": 26},
            crop_stage="booting",
            et_value=5.0,
            recommended_amount_mm=20.0,
            alternatives=alternatives,
        )
        assert len(explanation.alternatives) == 1

    def test_explain_fertilizer(self, engine):
        """Test fertilizer explanation"""
        explanation = engine.explain_fertilizer(
            recommendation_id="fert_001",
            soil_test={"nitrogen": 18, "phosphorus": 25, "potassium": 150},
            crop_type="wheat",
            crop_stage="tillering",
            target_yield=5.0,
            recommended_fertilizer="Urea 46%",
            recommended_rate=46.0,
        )
        assert explanation.recommendation_id == "fert_001"
        assert len(explanation.factors) >= 2
        assert len(explanation.rules) >= 1
        assert explanation.context["crop_type"] == "wheat"

    def test_format_for_display_markdown(self, engine, sample_factors):
        """Test formatting for markdown display"""
        explanation = engine.explain(
            recommendation_id="rec_001",
            recommendation_type="irrigation",
            factors=sample_factors,
        )
        output = engine.format_for_display(explanation, language="both", format="markdown")
        assert "# Why This Recommendation?" in output
        assert "# لماذا هذه التوصية؟" in output

    def test_format_for_display_text(self, engine, sample_factors):
        """Test formatting for text display"""
        explanation = engine.explain(
            recommendation_id="rec_001",
            recommendation_type="irrigation",
            factors=sample_factors,
        )
        output = engine.format_for_display(explanation, language="en", format="text")
        assert "WHY THIS RECOMMENDATION?" in output

    def test_format_for_display_arabic_only(self, engine, sample_factors):
        """Test formatting for Arabic only"""
        explanation = engine.explain(
            recommendation_id="rec_001",
            recommendation_type="irrigation",
            factors=sample_factors,
        )
        output = engine.format_for_display(explanation, language="ar", format="markdown")
        assert "لماذا هذه التوصية؟" in output


class TestExplanationTypeEnum:
    """Tests for ExplanationType enum"""

    def test_explanation_type_values(self):
        """Test ExplanationType values"""
        assert ExplanationType.FACTOR_BASED.value == "factor_based"
        assert ExplanationType.RULE_BASED.value == "rule_based"
        assert ExplanationType.DATA_DRIVEN.value == "data_driven"
        assert ExplanationType.COMPARATIVE.value == "comparative"


class TestFactorTypeEnum:
    """Tests for FactorType enum"""

    def test_factor_type_values(self):
        """Test FactorType values"""
        assert FactorType.WEATHER.value == "weather"
        assert FactorType.SOIL.value == "soil"
        assert FactorType.CROP_STAGE.value == "crop_stage"
        assert FactorType.SENSOR.value == "sensor"
        assert FactorType.HISTORICAL.value == "historical"


class TestImpactLevelEnum:
    """Tests for ImpactLevel enum"""

    def test_impact_level_values(self):
        """Test ImpactLevel values"""
        assert ImpactLevel.CRITICAL.value == "critical"
        assert ImpactLevel.HIGH.value == "high"
        assert ImpactLevel.MEDIUM.value == "medium"
        assert ImpactLevel.LOW.value == "low"


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_get_explainability_engine(self):
        """Test getting default engine"""
        engine1 = get_explainability_engine()
        engine2 = get_explainability_engine()
        assert engine1 is engine2

    def test_explain_recommendation_function(self):
        """Test explain_recommendation convenience function"""
        factors = [
            ContributingFactor(
                factor_type=FactorType.SOIL,
                name="Test",
                name_ar="اختبار",
                value="1",
                description="d",
                description_ar="و",
                impact=ImpactLevel.HIGH,
                weight=0.5,
                direction="supports",
            ),
        ]
        explanation = explain_recommendation(
            recommendation_id="test_001",
            recommendation_type="test",
            factors=factors,
        )
        assert explanation.recommendation_id == "test_001"
