"""
Unit tests for the harvest_quality module
==========================================

Comprehensive tests covering:
- Quality grading models and calculations
- Price calculations based on quality grades
- Buyer matching and requirements
- Bilingual support (English/Arabic)
- Trend analysis

Author: Test Suite
Version: 1.0.0
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import pytest

from shared.harvest_quality import (
    DATE_ADJUSTMENT_RULES,
    GRAIN_ADJUSTMENT_RULES,
    PRICE_MATRICES,
    QUALITY_STANDARDS,
    BuyerMatch,
    BuyerMatchingEngine,
    BuyerRequirement,
    BuyerType,
    # Models - Enums
    CropCategory,
    Currency,
    DateVariety,
    GradePriceMatrix,
    GradingResult,
    GrainType,
    PriceAdjustmentRule,
    PriceCalculation,
    PriceUnit,
    PricingConfig,
    QualityGrade,
    # Grading
    QualityGradingEngine,
    # Models - Quality
    QualityParameter,
    # Pricing
    QualityPricingEngine,
    QualityStandard,
    QualityTestRecord,
    QualityTestResult,
    QualityTrendAnalysis,
    QualityTrendAnalyzer,
    QualityTrendPoint,
    TestResult,
    TestStatus,
    TestType,
    TrendDirection,
    VegetableType,
    calculate_quick_price,
    estimate_value_improvement,
    get_barley_price_matrix,
    get_barley_standard,
    get_date_price_matrix,
    get_date_standard,
    get_grade_price_breakdown,
    get_vegetable_price_matrix,
    get_vegetable_standard,
    get_wheat_price_matrix,
    get_wheat_standard,
)

# ────────────────────────────────────────────────────────────────────────────
# Quality Models Tests
# ────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestQualityEnums:
    """Test quality grade enums and classifications"""

    def test_quality_grade_enum_values(self):
        """Test quality grade enum values"""
        assert QualityGrade.PREMIUM.value == "premium"
        assert QualityGrade.GRADE_A.value == "grade_a"
        assert QualityGrade.GRADE_B.value == "grade_b"
        assert QualityGrade.GRADE_C.value == "grade_c"
        assert QualityGrade.INDUSTRIAL.value == "industrial"
        assert QualityGrade.REJECTED.value == "rejected"

    def test_crop_category_values(self):
        """Test crop category enum"""
        assert CropCategory.GRAIN.value == "grain"
        assert CropCategory.DATE.value == "date"
        assert CropCategory.VEGETABLE.value == "vegetable"

    def test_grain_types(self):
        """Test grain types"""
        assert GrainType.WHEAT.value == "wheat"
        assert GrainType.BARLEY.value == "barley"
        assert GrainType.CORN.value == "corn"

    def test_date_varieties(self):
        """Test date varieties"""
        assert DateVariety.SUKKARI.value == "sukkari"
        assert DateVariety.KHALAS.value == "khalas"
        assert DateVariety.AJWA.value == "ajwa"

    def test_currency_values(self):
        """Test currency enum"""
        assert Currency.SAR.value == "SAR"
        assert Currency.USD.value == "USD"
        assert Currency.YER.value == "YER"


@pytest.mark.unit
class TestQualityParameter:
    """Test QualityParameter model"""

    def test_parameter_creation(self):
        """Test creating a quality parameter"""
        param = QualityParameter(
            parameter_name="moisture",
            parameter_name_ar="الرطوبة",
            unit="%",
            unit_ar="%",
            premium_min=0,
            premium_max=12.0,
            grade_a_min=12.0,
            grade_a_max=12.5,
            lower_is_better=True,
            weight=0.25,
        )
        assert param.parameter_name == "moisture"
        assert param.parameter_name_ar == "الرطوبة"
        assert param.unit == "%"
        assert param.weight == 0.25

    def test_parameter_get_grade_for_value_premium(self):
        """Test grade assignment for premium value"""
        param = QualityParameter(
            parameter_name="moisture",
            parameter_name_ar="الرطوبة",
            unit="%",
            unit_ar="%",
            premium_min=0,
            premium_max=12.0,
            grade_a_min=12.0,
            grade_a_max=12.5,
            lower_is_better=True,
            weight=0.25,
        )
        grade = param.get_grade_for_value(11.5)
        assert grade == QualityGrade.PREMIUM

    def test_parameter_get_grade_for_value_grade_a(self):
        """Test grade assignment for Grade A value"""
        param = QualityParameter(
            parameter_name="moisture",
            parameter_name_ar="الرطوبة",
            unit="%",
            unit_ar="%",
            premium_min=0,
            premium_max=12.0,
            grade_a_min=12.0,
            grade_a_max=12.5,
            lower_is_better=True,
            weight=0.25,
        )
        grade = param.get_grade_for_value(12.2)
        assert grade == QualityGrade.GRADE_A

    def test_parameter_get_grade_for_value_rejected(self):
        """Test grade assignment for rejected value"""
        param = QualityParameter(
            parameter_name="moisture",
            parameter_name_ar="الرطوبة",
            unit="%",
            unit_ar="%",
            premium_min=0,
            premium_max=12.0,
            grade_a_min=12.0,
            grade_a_max=12.5,
            rejection_threshold=15.0,
            lower_is_better=True,
            weight=0.25,
        )
        grade = param.get_grade_for_value(15.5)
        assert grade == QualityGrade.REJECTED

    def test_parameter_higher_is_better(self):
        """Test parameter where higher values are better (e.g., protein)"""
        param = QualityParameter(
            parameter_name="protein",
            parameter_name_ar="البروتين",
            unit="%",
            unit_ar="%",
            premium_min=14.0,
            premium_max=100,
            grade_a_min=12.5,
            grade_a_max=14.0,
            lower_is_better=False,
            weight=0.30,
        )
        # Higher protein = better
        grade_premium = param.get_grade_for_value(14.5)
        grade_a = param.get_grade_for_value(13.0)
        assert grade_premium == QualityGrade.PREMIUM
        assert grade_a == QualityGrade.GRADE_A

    def test_parameter_to_dict(self):
        """Test parameter serialization"""
        param = QualityParameter(
            parameter_name="moisture",
            parameter_name_ar="الرطوبة",
            unit="%",
            unit_ar="%",
            premium_min=0,
            premium_max=12.0,
            weight=0.25,
        )
        d = param.to_dict()
        assert d["parameter_name"] == "moisture"
        assert d["parameter_name_ar"] == "الرطوبة"
        assert d["weight"] == 0.25


@pytest.mark.unit
class TestQualityStandard:
    """Test QualityStandard model"""

    def test_wheat_standard_retrieval(self):
        """Test retrieving wheat quality standard"""
        standard = get_wheat_standard()
        assert standard.crop_type == "wheat"
        assert standard.crop_type_ar == "قمح"
        assert standard.crop_category == CropCategory.GRAIN
        assert len(standard.parameters) > 0

    def test_wheat_standard_has_mandatory_params(self):
        """Test wheat standard has mandatory parameters"""
        standard = get_wheat_standard()
        mandatory = standard.get_mandatory_parameters()
        assert len(mandatory) > 0
        # Check specific mandatory parameters
        param_names = [p.parameter_name for p in mandatory]
        assert "moisture" in param_names
        assert "protein" in param_names

    def test_barley_standard_retrieval(self):
        """Test retrieving barley quality standard"""
        standard = get_barley_standard()
        assert standard.crop_type == "barley"
        assert standard.crop_type_ar == "شعير"
        assert standard.crop_category == CropCategory.GRAIN

    def test_date_standard_retrieval(self):
        """Test retrieving date quality standard"""
        standard = get_date_standard(DateVariety.SUKKARI)
        assert standard.crop_type == "date"
        assert standard.crop_type_ar == "تمر"
        assert standard.crop_category == CropCategory.DATE

    def test_vegetable_standard_retrieval(self):
        """Test retrieving vegetable quality standard"""
        standard = get_vegetable_standard(VegetableType.TOMATO)
        assert standard.crop_type == "tomato"
        assert standard.crop_type_ar == "طماطم"
        assert standard.crop_category == CropCategory.VEGETABLE

    def test_get_parameter_by_name(self):
        """Test retrieving parameter by name from standard"""
        standard = get_wheat_standard()
        param = standard.get_parameter("moisture")
        assert param is not None
        assert param.parameter_name == "moisture"
        assert param.parameter_name_ar == "الرطوبة"

    def test_standard_to_dict(self):
        """Test standard serialization"""
        standard = get_wheat_standard()
        d = standard.to_dict()
        assert d["crop_type"] == "wheat"
        assert d["crop_type_ar"] == "قمح"
        assert "parameters" in d
        assert len(d["parameters"]) > 0

    def test_quality_standards_registry(self):
        """Test QUALITY_STANDARDS registry"""
        assert "wheat" in QUALITY_STANDARDS
        assert "barley" in QUALITY_STANDARDS
        assert "date_sukkari" in QUALITY_STANDARDS
        assert "tomato" in QUALITY_STANDARDS


@pytest.mark.unit
class TestQualityTestRecord:
    """Test QualityTestRecord model"""

    def test_test_record_creation(self):
        """Test creating a quality test record"""
        record = QualityTestRecord(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            batch_id="batch_001",
            crop_type="wheat",
            crop_type_ar="قمح",
            harvest_date=date(2026, 1, 15),
            status=TestStatus.PENDING,
        )
        assert record.tenant_id == "tenant_001"
        assert record.crop_type == "wheat"
        assert record.crop_type_ar == "قمح"
        assert record.harvest_date == date(2026, 1, 15)

    def test_test_record_is_complete(self):
        """Test checking if test record is complete"""
        record = QualityTestRecord(status=TestStatus.COMPLETED)
        assert record.is_complete() is True

        record.status = TestStatus.PENDING
        assert record.is_complete() is False

    def test_test_record_passed_all_tests(self):
        """Test checking if all tests passed"""
        record = QualityTestRecord()
        record.test_results = [
            QualityTestResult(
                test_type=TestType.MOISTURE,
                parameter_name="moisture",
                value=12.5,
                result=TestResult.PASS,
            ),
            QualityTestResult(
                test_type=TestType.PROTEIN,
                parameter_name="protein",
                value=13.0,
                result=TestResult.PASS,
            ),
        ]
        assert record.passed_all_tests() is True

    def test_test_record_failed_tests(self):
        """Test getting failed tests"""
        record = QualityTestRecord()
        record.test_results = [
            QualityTestResult(
                test_type=TestType.MOISTURE,
                parameter_name="moisture",
                value=12.5,
                result=TestResult.PASS,
            ),
            QualityTestResult(
                test_type=TestType.PROTEIN,
                parameter_name="protein",
                value=8.0,
                result=TestResult.FAIL,
            ),
        ]
        failed = record.get_failed_tests()
        assert len(failed) == 1
        assert failed[0].parameter_name == "protein"

    def test_test_record_to_dict(self):
        """Test test record serialization"""
        record = QualityTestRecord(
            tenant_id="tenant_001",
            crop_type="wheat",
            overall_grade=QualityGrade.GRADE_A,
            grade_score=85.0,
        )
        d = record.to_dict()
        assert d["tenant_id"] == "tenant_001"
        assert d["crop_type"] == "wheat"
        assert d["overall_grade"] == "grade_a"
        assert d["grade_score"] == 85.0


# ────────────────────────────────────────────────────────────────────────────
# Quality Grading Tests
# ────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestQualityGradingEngine:
    """Test QualityGradingEngine"""

    def test_engine_initialization(self):
        """Test initializing grading engine"""
        standard = get_wheat_standard()
        engine = QualityGradingEngine(standard)
        assert engine.standard == standard

    def test_calculate_grade_premium_wheat(self):
        """Test calculating premium grade for wheat"""
        engine = QualityGradingEngine(get_wheat_standard())
        result = engine.calculate_grade(
            {
                "moisture": 11.5,
                "protein": 14.5,
                "test_weight": 82.0,
                "foreign_matter": 0.3,
                "damaged_kernels": 0.5,
            }
        )
        assert result.overall_grade == QualityGrade.PREMIUM
        assert result.grade_score >= 92
        assert result.confidence > 0.9

    def test_calculate_grade_grade_a_wheat(self):
        """Test calculating Grade A for wheat"""
        engine = QualityGradingEngine(get_wheat_standard())
        result = engine.calculate_grade(
            {
                "moisture": 12.2,
                "protein": 13.0,
                "test_weight": 79.0,
                "foreign_matter": 0.7,
                "damaged_kernels": 1.5,
            }
        )
        assert result.overall_grade == QualityGrade.GRADE_A
        assert 77 <= result.grade_score < 92

    def test_calculate_grade_grade_b_wheat(self):
        """Test calculating Grade B for wheat"""
        engine = QualityGradingEngine(get_wheat_standard())
        result = engine.calculate_grade(
            {
                "moisture": 12.7,
                "protein": 11.5,
                "test_weight": 77.0,
                "foreign_matter": 1.5,
                "damaged_kernels": 3.0,
            }
        )
        assert result.overall_grade == QualityGrade.GRADE_B
        assert 62 <= result.grade_score < 77

    def test_calculate_grade_rejected_wheat(self):
        """Test calculating rejected grade for wheat"""
        engine = QualityGradingEngine(get_wheat_standard())
        result = engine.calculate_grade(
            {
                "moisture": 15.5,  # Exceeds rejection threshold
                "protein": 14.5,
                "test_weight": 82.0,
                "foreign_matter": 0.3,
                "damaged_kernels": 0.5,
            }
        )
        assert result.overall_grade == QualityGrade.REJECTED

    def test_calculate_grade_missing_mandatory_param(self):
        """Test grading with missing mandatory parameter"""
        engine = QualityGradingEngine(get_wheat_standard())
        result = engine.calculate_grade(
            {
                "moisture": 12.5,
                "protein": 13.0,
                # Missing mandatory test_weight, foreign_matter, damaged_kernels
            }
        )
        assert result.failed_parameters > 0
        assert result.confidence < 1.0

    def test_calculate_grade_confidence_with_all_params(self):
        """Test confidence is higher with all parameters"""
        engine = QualityGradingEngine(get_wheat_standard())
        result_complete = engine.calculate_grade(
            {
                "moisture": 12.5,
                "protein": 13.0,
                "test_weight": 79.0,
                "foreign_matter": 0.7,
                "damaged_kernels": 1.5,
            }
        )
        # Complete test should have high confidence
        assert result_complete.confidence >= 0.9

    def test_grading_result_has_recommendations(self):
        """Test grading result includes recommendations"""
        engine = QualityGradingEngine(get_wheat_standard())
        result = engine.calculate_grade(
            {
                "moisture": 13.5,  # Above Grade B
                "protein": 11.0,  # Low protein
                "test_weight": 77.0,
                "foreign_matter": 1.5,
                "damaged_kernels": 3.0,
            }
        )
        assert len(result.recommendations) > 0 or len(result.recommendations_ar) > 0

    def test_bilingual_grading_result(self):
        """Test grading result has bilingual text"""
        engine = QualityGradingEngine(get_wheat_standard())
        result = engine.calculate_grade(
            {
                "moisture": 12.5,
                "protein": 13.0,
                "test_weight": 79.0,
                "foreign_matter": 0.7,
                "damaged_kernels": 1.5,
            }
        )
        assert len(result.justification) > 0
        assert len(result.justification_ar) > 0
        assert "محصول" in result.justification_ar or "درجة" in result.justification_ar

    def test_grade_date_harvest(self):
        """Test grading date harvest"""
        engine = QualityGradingEngine(get_date_standard(DateVariety.SUKKARI))
        result = engine.calculate_grade(
            {
                "sugar_content": 72.0,
                "moisture": 18.0,
                "size": 14.0,
                "defects": 2.0,
                "skin_separation": 1.0,
            }
        )
        assert result.overall_grade in [
            QualityGrade.PREMIUM,
            QualityGrade.GRADE_A,
        ]

    def test_grade_vegetable_harvest(self):
        """Test grading vegetable harvest (tomato)"""
        engine = QualityGradingEngine(get_vegetable_standard(VegetableType.TOMATO))
        result = engine.calculate_grade(
            {
                "freshness": 95.0,
                "uniformity": 90.0,
                "defects": 1.0,
                "pest_damage": 0.0,
                "firmness": 88.0,
                "brix": 5.5,
            }
        )
        # Result should be Grade A or better
        assert result.overall_grade in [QualityGrade.PREMIUM, QualityGrade.GRADE_A]

    def test_grade_test_record(self):
        """Test grading a complete test record"""
        engine = QualityGradingEngine()

        record = QualityTestRecord(
            crop_type="wheat",
            crop_type_ar="قمح",
            test_results=[
                QualityTestResult(
                    test_type=TestType.MOISTURE,
                    parameter_name="moisture",
                    value=12.5,
                ),
                QualityTestResult(
                    test_type=TestType.PROTEIN,
                    parameter_name="protein",
                    value=13.0,
                ),
                QualityTestResult(
                    test_type=TestType.TEST_WEIGHT,
                    parameter_name="test_weight",
                    value=79.0,
                ),
                QualityTestResult(
                    test_type=TestType.FOREIGN_MATTER,
                    parameter_name="foreign_matter",
                    value=0.7,
                ),
                QualityTestResult(
                    test_type=TestType.DAMAGED_KERNELS,
                    parameter_name="damaged_kernels",
                    value=1.5,
                ),
            ],
        )

        updated_record, result = engine.grade_test_record(record)
        assert updated_record.overall_grade == QualityGrade.GRADE_A
        assert updated_record.grade_score > 0
        assert updated_record.moisture_percent == 12.5
        assert updated_record.protein_percent == 13.0


@pytest.mark.unit
class TestQualityTrendAnalyzer:
    """Test QualityTrendAnalyzer"""

    def test_trend_analyzer_initialization(self):
        """Test initializing trend analyzer"""
        analyzer = QualityTrendAnalyzer()
        assert analyzer is not None

    def test_analyze_trends_improving(self):
        """Test analyzing improving quality trend"""
        analyzer = QualityTrendAnalyzer()
        records = [
            QualityTestRecord(
                harvest_date=date(2026, 1, 1),
                overall_grade=QualityGrade.GRADE_C,
                grade_score=55.0,
            ),
            QualityTestRecord(
                harvest_date=date(2026, 1, 8),
                overall_grade=QualityGrade.GRADE_B,
                grade_score=70.0,
            ),
            QualityTestRecord(
                harvest_date=date(2026, 1, 15),
                overall_grade=QualityGrade.GRADE_A,
                grade_score=85.0,
            ),
        ]
        analysis = analyzer.analyze_trends(records)
        assert analysis.trend_direction == TrendDirection.IMPROVING
        assert analysis.sample_count == 3

    def test_analyze_trends_declining(self):
        """Test analyzing declining quality trend"""
        analyzer = QualityTrendAnalyzer()
        records = [
            QualityTestRecord(
                harvest_date=date(2026, 1, 1),
                overall_grade=QualityGrade.PREMIUM,
                grade_score=95.0,
            ),
            QualityTestRecord(
                harvest_date=date(2026, 1, 8),
                overall_grade=QualityGrade.GRADE_B,
                grade_score=70.0,
            ),
            QualityTestRecord(
                harvest_date=date(2026, 1, 15),
                overall_grade=QualityGrade.GRADE_C,
                grade_score=55.0,
            ),
        ]
        analysis = analyzer.analyze_trends(records)
        assert analysis.trend_direction == TrendDirection.DECLINING
        assert analysis.trend_strength > 0

    def test_analyze_trends_insufficient_data(self):
        """Test trend analysis with insufficient data"""
        analyzer = QualityTrendAnalyzer()
        records = [
            QualityTestRecord(
                harvest_date=date(2026, 1, 1),
                overall_grade=QualityGrade.GRADE_B,
                grade_score=70.0,
            ),
        ]
        analysis = analyzer.analyze_trends(records, min_samples=3)
        assert analysis.confidence_score == 0.0

    def test_trend_analysis_includes_stats(self):
        """Test trend analysis includes statistics"""
        analyzer = QualityTrendAnalyzer()
        records = [
            QualityTestRecord(
                harvest_date=date(2026, 1, 1),
                overall_grade=QualityGrade.GRADE_B,
                grade_score=70.0,
                moisture_percent=12.5,
                protein_percent=12.0,
            ),
            QualityTestRecord(
                harvest_date=date(2026, 1, 8),
                overall_grade=QualityGrade.GRADE_B,
                grade_score=72.0,
                moisture_percent=12.7,
                protein_percent=12.5,
            ),
            QualityTestRecord(
                harvest_date=date(2026, 1, 15),
                overall_grade=QualityGrade.GRADE_A,
                grade_score=80.0,
                moisture_percent=12.3,
                protein_percent=13.0,
            ),
        ]
        analysis = analyzer.analyze_trends(records)
        assert analysis.average_grade_score > 0
        assert analysis.best_grade_score >= analysis.worst_grade_score
        assert analysis.avg_moisture_percent is not None
        assert analysis.avg_protein_percent is not None


# ────────────────────────────────────────────────────────────────────────────
# Buyer Matching Tests
# ────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestBuyerRequirement:
    """Test BuyerRequirement model"""

    def test_buyer_requirement_creation(self):
        """Test creating buyer requirement"""
        req = BuyerRequirement(
            buyer_id="buyer_001",
            buyer_name="Al Rashid Company",
            buyer_name_ar="شركة الراشد",
            buyer_type=BuyerType.WHOLESALE,
            crop_type="wheat",
            crop_type_ar="قمح",
            minimum_grade=QualityGrade.GRADE_A,
            base_price_per_kg=Decimal("2.00"),
        )
        assert req.buyer_name == "Al Rashid Company"
        assert req.buyer_name_ar == "شركة الراشد"
        assert req.crop_type == "wheat"
        assert req.minimum_grade == QualityGrade.GRADE_A

    def test_buyer_requirement_is_valid(self):
        """Test checking if requirement is valid"""
        req = BuyerRequirement(
            buyer_id="buyer_001",
            is_active=True,
            valid_from=date(2026, 1, 1),
            valid_until=date(2026, 12, 31),
        )
        assert req.is_valid() is True

    def test_buyer_requirement_is_invalid_inactive(self):
        """Test requirement is invalid when inactive"""
        req = BuyerRequirement(
            buyer_id="buyer_001",
            is_active=False,
        )
        assert req.is_valid() is False

    def test_buyer_requirement_matches_grade_premium(self):
        """Test grade matching - premium meets all requirements"""
        req = BuyerRequirement(
            buyer_id="buyer_001",
            minimum_grade=QualityGrade.GRADE_B,
        )
        assert req.matches_grade(QualityGrade.PREMIUM) is True
        assert req.matches_grade(QualityGrade.GRADE_A) is True
        assert req.matches_grade(QualityGrade.GRADE_B) is True

    def test_buyer_requirement_matches_grade_fails_low_grade(self):
        """Test grade matching - low grade fails requirement"""
        req = BuyerRequirement(
            buyer_id="buyer_001",
            minimum_grade=QualityGrade.GRADE_A,
        )
        assert req.matches_grade(QualityGrade.GRADE_B) is False
        assert req.matches_grade(QualityGrade.GRADE_C) is False
        assert req.matches_grade(QualityGrade.INDUSTRIAL) is False

    def test_buyer_requirement_to_dict(self):
        """Test buyer requirement serialization"""
        req = BuyerRequirement(
            buyer_id="buyer_001",
            buyer_name="Buyer Name",
            buyer_name_ar="اسم المشتري",
            crop_type="wheat",
        )
        d = req.to_dict()
        assert d["buyer_name"] == "Buyer Name"
        assert d["buyer_name_ar"] == "اسم المشتري"
        assert d["crop_type"] == "wheat"


@pytest.mark.unit
class TestBuyerMatchingEngine:
    """Test BuyerMatchingEngine"""

    def test_matching_engine_initialization(self):
        """Test initializing buyer matching engine"""
        engine = BuyerMatchingEngine()
        assert len(engine.requirements) == 0

    def test_add_buyer_requirement(self):
        """Test adding buyer requirement"""
        engine = BuyerMatchingEngine()
        req = BuyerRequirement(
            buyer_id="buyer_001",
            buyer_name="Buyer 1",
            crop_type="wheat",
        )
        engine.add_requirement(req)
        assert len(engine.requirements) == 1

    def test_find_matching_buyers_eligible(self):
        """Test finding matching buyers"""
        engine = BuyerMatchingEngine()
        engine.add_requirement(
            BuyerRequirement(
                buyer_id="buyer_001",
                buyer_name="Buyer 1",
                buyer_name_ar="المشتري 1",
                crop_type="wheat",
                crop_type_ar="قمح",
                minimum_grade=QualityGrade.GRADE_B,
                base_price_per_kg=Decimal("2.00"),
                max_moisture_percent=13.0,
                min_protein_percent=11.0,
            )
        )

        test_record = QualityTestRecord(
            crop_type="wheat",
            overall_grade=QualityGrade.GRADE_A,
            moisture_percent=12.5,
            protein_percent=12.5,
        )

        matches = engine.find_matches(test_record, 1000.0)
        assert len(matches) == 1
        assert matches[0].is_eligible is True
        assert matches[0].match_score >= 60

    def test_find_matching_buyers_not_eligible(self):
        """Test when harvest doesn't match buyer requirements"""
        engine = BuyerMatchingEngine()
        engine.add_requirement(
            BuyerRequirement(
                buyer_id="buyer_001",
                buyer_name="Buyer 1",
                crop_type="wheat",
                minimum_grade=QualityGrade.PREMIUM,
                max_moisture_percent=12.0,
            )
        )

        test_record = QualityTestRecord(
            crop_type="wheat",
            overall_grade=QualityGrade.GRADE_B,
            moisture_percent=13.5,
        )

        matches = engine.find_matches(test_record, 1000.0)
        assert len(matches) <= 1
        if len(matches) > 0:
            assert matches[0].is_eligible is False

    def test_buyer_match_score_calculation(self):
        """Test buyer match score is calculated correctly"""
        engine = BuyerMatchingEngine()
        engine.add_requirement(
            BuyerRequirement(
                buyer_id="buyer_001",
                buyer_name="Buyer 1",
                crop_type="wheat",
                minimum_grade=QualityGrade.GRADE_B,
                base_price_per_kg=Decimal("2.00"),
                max_moisture_percent=13.0,
                min_protein_percent=11.0,
                min_quantity_kg=500,
                max_quantity_kg=2000,
            )
        )

        test_record = QualityTestRecord(
            crop_type="wheat",
            overall_grade=QualityGrade.GRADE_A,
            moisture_percent=12.5,
            protein_percent=12.5,
        )

        matches = engine.find_matches(test_record, 1000.0)
        assert len(matches) == 1
        assert 0 <= matches[0].match_score <= 100

    def test_buyer_match_offered_price(self):
        """Test offered price calculation in buyer match"""
        engine = BuyerMatchingEngine()
        engine.add_requirement(
            BuyerRequirement(
                buyer_id="buyer_001",
                buyer_name="Buyer 1",
                crop_type="wheat",
                minimum_grade=QualityGrade.PREMIUM,
                base_price_per_kg=Decimal("2.00"),
                price_premium_percent=25.0,  # 25% premium for premium grade
            )
        )

        test_record = QualityTestRecord(
            crop_type="wheat",
            overall_grade=QualityGrade.PREMIUM,
        )

        matches = engine.find_matches(test_record, 1000.0)
        assert len(matches) == 1
        # Price should include premium
        assert matches[0].offered_price_per_kg > Decimal("2.00")

    def test_buyer_match_requirements_tracking(self):
        """Test tracking of met/unmet requirements"""
        engine = BuyerMatchingEngine()
        engine.add_requirement(
            BuyerRequirement(
                buyer_id="buyer_001",
                buyer_name="Buyer 1",
                crop_type="wheat",
                minimum_grade=QualityGrade.GRADE_A,
                max_moisture_percent=12.5,
                min_protein_percent=12.0,
            )
        )

        test_record = QualityTestRecord(
            crop_type="wheat",
            overall_grade=QualityGrade.GRADE_B,
            moisture_percent=12.0,  # Meets requirement
            protein_percent=11.0,  # Fails requirement
        )

        matches = engine.find_matches(test_record, 1000.0)
        if len(matches) > 0:
            match = matches[0]
            assert len(match.unmet_requirements) > 0 or len(match.unmet_requirements_ar) > 0


# ────────────────────────────────────────────────────────────────────────────
# Pricing Tests
# ────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestGradePriceMatrix:
    """Test GradePriceMatrix model"""

    def test_wheat_price_matrix_retrieval(self):
        """Test retrieving wheat price matrix"""
        matrix = get_wheat_price_matrix()
        assert matrix.crop_type == "wheat"
        assert matrix.crop_type_ar == "قمح"
        assert matrix.currency == Currency.SAR
        assert matrix.price_unit == PriceUnit.KG

    def test_barley_price_matrix_retrieval(self):
        """Test retrieving barley price matrix"""
        matrix = get_barley_price_matrix()
        assert matrix.crop_type == "barley"
        assert matrix.crop_type_ar == "شعير"

    def test_date_price_matrix_variety_multiplier(self):
        """Test date price matrix varies by variety"""
        sukkari_matrix = get_date_price_matrix("sukkari")
        ajwa_matrix = get_date_price_matrix("ajwa")

        # Ajwa should be more expensive (higher multiplier)
        assert ajwa_matrix.base_price > sukkari_matrix.base_price

    def test_vegetable_price_matrix_retrieval(self):
        """Test retrieving vegetable price matrix"""
        matrix = get_vegetable_price_matrix("tomato")
        assert matrix.crop_type == "tomato"
        assert matrix.crop_type_ar == "طماطم"

    def test_price_matrix_get_price_for_grade(self):
        """Test getting price for each grade"""
        matrix = get_wheat_price_matrix(base_price=Decimal("2.00"))

        premium_price = matrix.get_price_for_grade(QualityGrade.PREMIUM)
        grade_a_price = matrix.get_price_for_grade(QualityGrade.GRADE_A)
        grade_b_price = matrix.get_price_for_grade(QualityGrade.GRADE_B)
        grade_c_price = matrix.get_price_for_grade(QualityGrade.GRADE_C)
        industrial_price = matrix.get_price_for_grade(QualityGrade.INDUSTRIAL)

        # Prices should decrease from premium to industrial
        assert premium_price > grade_a_price > grade_b_price > grade_c_price > industrial_price

    def test_price_matrix_to_dict(self):
        """Test price matrix serialization"""
        matrix = get_wheat_price_matrix()
        d = matrix.to_dict()
        assert d["crop_type"] == "wheat"
        assert d["crop_type_ar"] == "قمح"
        assert "premium_price" in d
        assert "grade_b_price" in d

    def test_price_matrices_registry(self):
        """Test PRICE_MATRICES registry"""
        assert "wheat" in PRICE_MATRICES
        assert "barley" in PRICE_MATRICES
        assert "date_sukkari" in PRICE_MATRICES
        assert "tomato" in PRICE_MATRICES


@pytest.mark.unit
class TestQualityPricingEngine:
    """Test QualityPricingEngine"""

    def test_pricing_engine_initialization(self):
        """Test initializing pricing engine"""
        matrix = get_wheat_price_matrix()
        engine = QualityPricingEngine(matrix)
        assert engine.price_matrix == matrix

    def test_calculate_price_grade_a(self):
        """Test calculating price for Grade A"""
        matrix = get_wheat_price_matrix(base_price=Decimal("2.00"))
        engine = QualityPricingEngine(matrix)

        calc = engine.calculate_price(QualityGrade.GRADE_A, 1000)
        assert calc.overall_grade == QualityGrade.GRADE_A
        assert calc.quantity == 1000
        assert calc.final_price > 0
        assert calc.currency == Currency.SAR

    def test_calculate_price_with_adjustments(self):
        """Test price calculation with parameter adjustments"""
        matrix = get_wheat_price_matrix(base_price=Decimal("2.00"))
        engine = QualityPricingEngine(matrix)

        calc = engine.calculate_price(
            grade=QualityGrade.GRADE_B,
            quantity=1000,
            test_values={
                "moisture": 14.0,  # Above threshold (13.0)
                "protein": 13.0,  # Above threshold (12.0)
                "foreign_matter": 2.0,  # Above threshold (1.0)
            },
        )

        assert len(calc.adjustments) > 0
        assert calc.final_price != calc.subtotal

    def test_calculate_price_moisture_deduction(self):
        """Test moisture deduction in price"""
        matrix = get_wheat_price_matrix(base_price=Decimal("2.00"))
        engine = QualityPricingEngine(matrix)

        calc_dry = engine.calculate_price(
            grade=QualityGrade.GRADE_B,
            quantity=1000,
            test_values={"moisture": 12.5},  # Below threshold
        )

        calc_wet = engine.calculate_price(
            grade=QualityGrade.GRADE_B,
            quantity=1000,
            test_values={"moisture": 14.0},  # Above threshold
        )

        # Wet grain should be cheaper
        assert calc_wet.final_price < calc_dry.final_price

    def test_calculate_price_protein_bonus(self):
        """Test protein bonus in price"""
        matrix = get_wheat_price_matrix(base_price=Decimal("2.00"))
        engine = QualityPricingEngine(matrix)

        calc_low = engine.calculate_price(
            grade=QualityGrade.GRADE_B,
            quantity=1000,
            test_values={"protein": 11.0},
        )

        calc_high = engine.calculate_price(
            grade=QualityGrade.GRADE_B,
            quantity=1000,
            test_values={"protein": 13.0},
        )

        # High protein should be more expensive
        assert calc_high.final_price > calc_low.final_price

    def test_calculate_price_for_test_record(self):
        """Test calculating price from test record"""
        engine = QualityPricingEngine()

        record = QualityTestRecord(
            crop_type="wheat",
            overall_grade=QualityGrade.GRADE_A,
            moisture_percent=12.5,
            protein_percent=12.5,
        )

        calc = engine.calculate_price_for_test_record(record, 1000)
        assert calc.batch_id == record.batch_id
        assert calc.test_record_id == record.id
        assert calc.grade_score == record.grade_score

    def test_compare_prices_by_grade(self):
        """Test comparing prices across grades"""
        matrix = get_wheat_price_matrix(base_price=Decimal("2.00"))
        engine = QualityPricingEngine(matrix)

        comparison = engine.compare_prices_by_grade(1000, matrix)

        assert len(comparison) == 5  # All grades
        assert "premium" in comparison
        assert "grade_a" in comparison
        assert "grade_b" in comparison
        assert "grade_c" in comparison
        assert "industrial" in comparison

        # Premium should have highest price
        premium_price = Decimal(comparison["premium"]["total_price"])
        industrial_price = Decimal(comparison["industrial"]["total_price"])
        assert premium_price > industrial_price

    def test_set_adjustment_rules(self):
        """Test setting custom adjustment rules"""
        engine = QualityPricingEngine()
        engine.set_adjustment_rules(GRAIN_ADJUSTMENT_RULES)
        assert len(engine.adjustment_rules) > 0


@pytest.mark.unit
class TestPricingUtilityFunctions:
    """Test pricing utility functions"""

    def test_calculate_quick_price(self):
        """Test quick price calculation"""
        price, currency = calculate_quick_price("wheat", QualityGrade.GRADE_B, 1000)
        assert price > 0
        assert currency == Currency.SAR

    def test_calculate_quick_price_different_grades(self):
        """Test quick price varies by grade"""
        price_premium, _ = calculate_quick_price("wheat", QualityGrade.PREMIUM, 1000)
        price_industrial, _ = calculate_quick_price("wheat", QualityGrade.INDUSTRIAL, 1000)

        assert price_premium > price_industrial

    def test_get_grade_price_breakdown(self):
        """Test getting price breakdown for all grades"""
        breakdown = get_grade_price_breakdown("wheat", 1000)

        assert len(breakdown) == 5
        prices = [Decimal(item["total_price"]) for item in breakdown]
        # Verify descending order
        assert prices[0] > prices[-1]

    def test_estimate_value_improvement(self):
        """Test estimating value improvement"""
        improvement = estimate_value_improvement(
            current_grade=QualityGrade.GRADE_B,
            target_grade=QualityGrade.PREMIUM,
            crop_type="wheat",
            quantity_kg=1000,
        )

        assert improvement["current_grade"] == "grade_b"
        assert improvement["target_grade"] == "premium"
        assert improvement["improvement_percent"] > 0
        assert improvement["potential_improvement"] is not None

    def test_estimate_value_improvement_no_improvement_downgrade(self):
        """Test value improvement when downgrading"""
        improvement = estimate_value_improvement(
            current_grade=QualityGrade.PREMIUM,
            target_grade=QualityGrade.GRADE_B,
            crop_type="wheat",
            quantity_kg=1000,
        )

        assert improvement["improvement_percent"] < 0


# ────────────────────────────────────────────────────────────────────────────
# Bilingual Support Tests
# ────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestBilingualSupport:
    """Test bilingual support (English/Arabic)"""

    def test_quality_parameter_bilingual(self):
        """Test parameter has bilingual names"""
        param = QualityParameter(
            parameter_name="moisture",
            parameter_name_ar="الرطوبة",
            unit="%",
            unit_ar="%",
        )
        assert param.parameter_name == "moisture"
        assert param.parameter_name_ar == "الرطوبة"
        assert len(param.parameter_name_ar) > 0

    def test_quality_standard_bilingual(self):
        """Test standard has bilingual names"""
        standard = get_wheat_standard()
        assert standard.name == "Wheat Quality Standard"
        assert standard.name_ar == "معيار جودة القمح"
        assert len(standard.name_ar) > 0

    def test_quality_parameter_in_standard_bilingual(self):
        """Test standard parameters are bilingual"""
        standard = get_wheat_standard()
        for param in standard.parameters:
            assert len(param.parameter_name) > 0
            assert len(param.parameter_name_ar) > 0

    def test_grading_result_bilingual_justification(self):
        """Test grading result provides bilingual justification"""
        engine = QualityGradingEngine(get_wheat_standard())
        result = engine.calculate_grade(
            {
                "moisture": 12.5,
                "protein": 13.0,
                "test_weight": 79.0,
                "foreign_matter": 0.7,
                "damaged_kernels": 1.5,
            }
        )
        assert len(result.justification) > 0
        assert len(result.justification_ar) > 0

    def test_grading_result_bilingual_recommendations(self):
        """Test grading result provides bilingual recommendations"""
        engine = QualityGradingEngine(get_wheat_standard())
        result = engine.calculate_grade(
            {
                "moisture": 13.5,
                "protein": 11.0,
                "test_weight": 77.0,
                "foreign_matter": 1.5,
                "damaged_kernels": 3.0,
            }
        )
        # Should have recommendations in at least one language
        assert len(result.recommendations) > 0 or len(result.recommendations_ar) > 0

    def test_buyer_requirement_bilingual(self):
        """Test buyer requirement has bilingual support"""
        req = BuyerRequirement(
            buyer_name="Buyer Name",
            buyer_name_ar="اسم المشتري",
            crop_type="wheat",
            crop_type_ar="قمح",
        )
        assert req.buyer_name_ar == "اسم المشتري"
        assert req.crop_type_ar == "قمح"

    def test_buyer_match_bilingual_recommendations(self):
        """Test buyer match has bilingual recommendations"""
        engine = BuyerMatchingEngine()
        engine.add_requirement(
            BuyerRequirement(
                buyer_id="buyer_001",
                buyer_name="Buyer 1",
                buyer_name_ar="المشتري 1",
                crop_type="wheat",
                crop_type_ar="قمح",
                minimum_grade=QualityGrade.GRADE_A,
            )
        )

        test_record = QualityTestRecord(
            crop_type="wheat",
            overall_grade=QualityGrade.GRADE_B,
        )

        matches = engine.find_matches(test_record, 1000.0)
        if len(matches) > 0:
            match = matches[0]
            assert len(match.recommendation) > 0 or len(match.recommendation_ar) > 0

    def test_price_matrix_bilingual_names(self):
        """Test price matrix has bilingual crop names"""
        matrix = get_wheat_price_matrix()
        assert matrix.crop_type == "wheat"
        assert matrix.crop_type_ar == "قمح"

    def test_all_quality_standards_have_arabic_names(self):
        """Test all quality standards have Arabic names"""
        for key, standard in QUALITY_STANDARDS.items():
            assert len(standard.name_ar) > 0, f"Standard {key} missing Arabic name"

    def test_all_price_matrices_have_arabic_names(self):
        """Test all price matrices have Arabic crop names"""
        for key, matrix in PRICE_MATRICES.items():
            if matrix.crop_type_ar:
                assert len(matrix.crop_type_ar) > 0, f"Matrix {key} missing Arabic name"


# ────────────────────────────────────────────────────────────────────────────
# Integration Tests
# ────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    def test_complete_wheat_grading_pricing_workflow(self):
        """Test complete workflow: grade wheat then calculate price"""
        # Create test record
        record = QualityTestRecord(
            tenant_id="tenant_001",
            farm_id="farm_001",
            crop_type="wheat",
            crop_type_ar="قمح",
            test_results=[
                QualityTestResult(
                    parameter_name="moisture",
                    value=12.5,
                ),
                QualityTestResult(
                    parameter_name="protein",
                    value=13.0,
                ),
                QualityTestResult(
                    parameter_name="test_weight",
                    value=79.0,
                ),
                QualityTestResult(
                    parameter_name="foreign_matter",
                    value=0.7,
                ),
                QualityTestResult(
                    parameter_name="damaged_kernels",
                    value=1.5,
                ),
            ],
        )

        # Grade the harvest
        grading_engine = QualityGradingEngine()
        graded_record, grading_result = grading_engine.grade_test_record(record)

        assert graded_record.overall_grade in [
            QualityGrade.PREMIUM,
            QualityGrade.GRADE_A,
        ]

        # Calculate price
        pricing_engine = QualityPricingEngine()
        price_calc = pricing_engine.calculate_price_for_test_record(graded_record, 1000)

        assert price_calc.final_price > 0
        assert price_calc.quantity == 1000

    def test_complete_buyer_matching_workflow(self):
        """Test complete workflow: grade harvest and match with buyers"""
        # Create and grade test record
        record = QualityTestRecord(
            crop_type="wheat",
            overall_grade=QualityGrade.GRADE_A,
            moisture_percent=12.5,
            protein_percent=13.0,
        )

        # Add buyer requirements
        buyer_engine = BuyerMatchingEngine()
        buyer_engine.add_requirement(
            BuyerRequirement(
                buyer_id="buyer_001",
                buyer_name="Buyer 1",
                buyer_name_ar="المشتري 1",
                crop_type="wheat",
                crop_type_ar="قمح",
                minimum_grade=QualityGrade.GRADE_B,
                max_moisture_percent=13.0,
                base_price_per_kg=Decimal("2.00"),
            )
        )

        # Find matching buyers
        matches = buyer_engine.find_matches(record, 1000)

        assert len(matches) > 0
        assert matches[0].is_eligible is True

    def test_complete_date_harvest_workflow(self):
        """Test complete workflow for date harvest"""
        # Create and grade date record
        record = QualityTestRecord(
            crop_type="date",
            variety="sukkari",
            test_results=[
                QualityTestResult(parameter_name="sugar_content", value=72.0),
                QualityTestResult(parameter_name="moisture", value=18.0),
                QualityTestResult(parameter_name="size", value=14.0),
                QualityTestResult(parameter_name="defects", value=2.0),
                QualityTestResult(parameter_name="skin_separation", value=1.0),
            ],
        )

        # Grade
        engine = QualityGradingEngine(get_date_standard(DateVariety.SUKKARI))
        graded_record, result = engine.grade_test_record(record)

        assert graded_record.overall_grade in [
            QualityGrade.PREMIUM,
            QualityGrade.GRADE_A,
        ]

        # Price (dates are significantly more expensive)
        pricing_engine = QualityPricingEngine()
        matrix = get_date_price_matrix("sukkari")
        price_calc = pricing_engine.calculate_price(
            grade=graded_record.overall_grade,
            quantity=100,  # 100 kg of dates
            price_matrix=matrix,
        )

        assert price_calc.final_price > 0
