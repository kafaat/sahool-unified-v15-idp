"""
Tests for Response Schemas — اختبارات نماذج الاستجابة
=====================================================
Tests cover Pydantic models, enums, and helper functions in responses.py.
"""

import pytest

from src.responses import (
    ActionType,
    AlertLevel,
    AnalysisSectionSummary,
    BaseResponse,
    BilingualText,
    CacheStatsResponse,
    ComprehensiveAnalysisResponse,
    DiseaseDetectionResponse,
    DiseaseDetectionResult,
    DiseaseInfo,
    FertilizerRecommendation,
    MapLayer,
    NutrientAnalysisResponse,
    NutrientInfo,
    NutrientStatusSummary,
    OverallHealthStatus,
    PestAssessmentResponse,
    PestAssessmentSummary,
    PestRisk,
    ResponseMetadata,
    ResponseStatus,
    TimelineDataPoint,
    TimelineTrend,
    TreatmentInfo,
    YieldComparisonBase,
    YieldFactors,
    YieldPredictionResponse,
    YieldRange,
    ZoneAction,
    ZoneDiagnosisResponse,
    ZoneSummary,
    ZoneTimelineResponse,
    create_bilingual_text,
    create_error_response,
    create_success_response,
    get_alert_level_from_severity,
    get_health_score,
)


# ── Enums ────────────────────────────────────────────────────────────────────


class TestEnums:
    def test_response_status_values(self):
        assert ResponseStatus.SUCCESS == "success"
        assert ResponseStatus.PARTIAL == "partial"
        assert ResponseStatus.ERROR == "error"

    def test_alert_level_values(self):
        assert AlertLevel.CRITICAL == "critical"
        assert AlertLevel.HIGH == "high"
        assert AlertLevel.MEDIUM == "medium"
        assert AlertLevel.LOW == "low"
        assert AlertLevel.INFO == "info"

    def test_action_type_values(self):
        assert ActionType.IRRIGATION == "irrigation"
        assert ActionType.FERTILIZATION == "fertilization"
        assert ActionType.PEST_CONTROL == "pest_control"
        assert ActionType.DISEASE_TREATMENT == "disease_treatment"
        assert ActionType.SCOUTING == "scouting"
        assert ActionType.HARVEST == "harvest"
        assert ActionType.PRUNING == "pruning"
        assert ActionType.NONE == "none"


# ── Base Models ──────────────────────────────────────────────────────────────


class TestBilingualText:
    def test_create(self):
        t = BilingualText(en="Hello", ar="مرحبا")
        assert t.en == "Hello"
        assert t.ar == "مرحبا"


class TestResponseMetadata:
    def test_defaults(self):
        m = ResponseMetadata()
        assert m.request_id  # non-empty UUID string
        assert m.timestamp  # non-empty ISO string
        assert m.processing_time_ms == 0.0
        assert m.version == "16.0.0"
        assert m.cached is False

    def test_custom_values(self):
        m = ResponseMetadata(processing_time_ms=123.4, cached=True)
        assert m.processing_time_ms == 123.4
        assert m.cached is True


class TestBaseResponse:
    def test_defaults(self):
        r = BaseResponse()
        assert r.status == ResponseStatus.SUCCESS
        assert r.metadata is not None
        assert r.message is None
        assert r.errors == []

    def test_with_message(self):
        r = BaseResponse(
            message=BilingualText(en="Done", ar="تم"),
            status=ResponseStatus.ERROR,
        )
        assert r.status == ResponseStatus.ERROR
        assert r.message.en == "Done"


# ── Disease Models ───────────────────────────────────────────────────────────


class TestDiseaseModels:
    def test_disease_info(self):
        d = DiseaseInfo(
            disease_type="rust",
            name=BilingualText(en="Rust", ar="صدأ"),
            description=BilingualText(en="Fungal disease", ar="مرض فطري"),
            severity="high",
            confidence=0.85,
            affected_indicator="ndvi",
        )
        assert d.disease_type == "rust"
        assert d.confidence == 0.85

    def test_treatment_info(self):
        t = TreatmentInfo(
            treatment_type="fungicide",
            product=BilingualText(en="Product A", ar="منتج أ"),
            dosage=BilingualText(en="2 kg/ha", ar="2 كجم/هكتار"),
            application_method=BilingualText(en="Spray", ar="رش"),
            urgency_days=7,
        )
        assert t.urgency_days == 7

    def test_disease_detection_result(self):
        disease = DiseaseInfo(
            disease_type="blight",
            name=BilingualText(en="Blight", ar="لفحة"),
            description=BilingualText(en="desc", ar="وصف"),
            severity="medium",
            confidence=0.7,
            affected_indicator="evi",
        )
        r = DiseaseDetectionResult(disease=disease)
        assert r.treatments == []
        assert r.prevention == []

    def test_overall_health_status(self):
        h = OverallHealthStatus(
            status=BilingualText(en="Fair", ar="متوسط"),
            score=65.0,
            alert_level=AlertLevel.MEDIUM,
        )
        assert h.score == 65.0

    def test_disease_detection_response(self):
        r = DiseaseDetectionResponse(
            health_status=OverallHealthStatus(
                status=BilingualText(en="Good", ar="جيد"),
                score=85.0,
                alert_level=AlertLevel.LOW,
            ),
            detection_count=0,
        )
        assert r.detection_count == 0
        assert r.detections == []


# ── Nutrient Models ──────────────────────────────────────────────────────────


class TestNutrientModels:
    def test_nutrient_info(self):
        n = NutrientInfo(
            nutrient_type="nitrogen",
            name=BilingualText(en="Nitrogen", ar="نيتروجين"),
            deficiency_level="moderate",
            confidence=0.8,
        )
        assert n.nutrient_type == "nitrogen"

    def test_fertilizer_recommendation(self):
        f = FertilizerRecommendation(
            product=BilingualText(en="Urea", ar="يوريا"),
            rate_per_hectare="46 kg/ha",
            application_timing=BilingualText(en="Morning", ar="صباحا"),
            application_method=BilingualText(en="Broadcast", ar="نثر"),
            estimated_cost_usd=50.0,
        )
        assert f.estimated_cost_usd == 50.0

    def test_nutrient_analysis_response(self):
        r = NutrientAnalysisResponse(
            nutrient_status=NutrientStatusSummary(
                status=BilingualText(en="Deficient", ar="ناقص"),
                deficiency_count=2,
                priority_nutrients=["nitrogen", "phosphorus"],
            ),
        )
        assert r.nutrient_status.deficiency_count == 2


# ── Yield Models ─────────────────────────────────────────────────────────────


class TestYieldModels:
    def test_yield_range(self):
        y = YieldRange(low=3000, expected=4500, high=6000)
        assert y.expected == 4500

    def test_yield_comparison(self):
        c = YieldComparisonBase(
            regional_average=4000.0,
            percent_vs_regional=12.5,
        )
        assert c.regional_average == 4000.0

    def test_yield_factors(self):
        f = YieldFactors(
            ndvi_contribution=0.35,
            evi_contribution=0.25,
            water_status=BilingualText(en="Adequate", ar="كاف"),
            nutrient_status=BilingualText(en="Good", ar="جيد"),
            growth_stage_effect=0.8,
        )
        assert f.ndvi_contribution == 0.35

    def test_yield_prediction_response(self):
        r = YieldPredictionResponse(
            crop_type="wheat",
            crop_type_ar="قمح",
            yield_prediction=YieldRange(low=3000, expected=4500, high=6000),
            total_predicted_kg=22500.0,
            confidence=0.82,
            prediction_basis=BilingualText(en="NDVI-based", ar="مبني على NDVI"),
            field_area_hectares=5.0,
        )
        assert r.total_predicted_kg == 22500.0


# ── Pest Models ──────────────────────────────────────────────────────────────


class TestPestModels:
    def test_pest_risk(self):
        p = PestRisk(
            pest_type="aphid",
            name=BilingualText(en="Aphid", ar="من"),
            risk_level=AlertLevel.HIGH,
            probability=0.75,
        )
        assert p.probability == 0.75

    def test_pest_assessment_summary(self):
        s = PestAssessmentSummary(
            overall_risk=AlertLevel.MEDIUM,
            high_risk_count=1,
            medium_risk_count=2,
            low_risk_count=3,
        )
        assert s.high_risk_count == 1

    def test_pest_assessment_response(self):
        r = PestAssessmentResponse(
            assessment_summary=PestAssessmentSummary(
                overall_risk=AlertLevel.LOW,
                high_risk_count=0,
                medium_risk_count=1,
                low_risk_count=2,
            ),
        )
        assert r.risks == []


# ── Zone Models ──────────────────────────────────────────────────────────────


class TestZoneModels:
    def test_zone_action(self):
        a = ZoneAction(
            zone_id="zone-1",
            action_type=ActionType.IRRIGATION,
            priority=AlertLevel.HIGH,
            title=BilingualText(en="Irrigate now", ar="اسق الآن"),
            reason=BilingualText(en="Low moisture", ar="رطوبة منخفضة"),
        )
        assert a.action_type == ActionType.IRRIGATION

    def test_zone_summary(self):
        s = ZoneSummary(zones_total=10, zones_critical=1, zones_warning=3, zones_ok=6)
        assert s.zones_total == 10

    def test_map_layer(self):
        m = MapLayer(
            layer_type="ndvi",
            name=BilingualText(en="NDVI", ar="مؤشر NDVI"),
            url="/tiles/ndvi/{z}/{x}/{y}",
        )
        assert m.available is True

    def test_zone_diagnosis_response(self):
        r = ZoneDiagnosisResponse(
            field_id="field-1",
            diagnosis_date="2026-03-22",
            summary=ZoneSummary(zones_total=5, zones_critical=0, zones_warning=1, zones_ok=4),
        )
        assert r.field_id == "field-1"


# ── Comprehensive Analysis ───────────────────────────────────────────────────


class TestComprehensiveAnalysis:
    def test_analysis_section_summary(self):
        s = AnalysisSectionSummary(
            status=BilingualText(en="OK", ar="جيد"),
            alert_level=AlertLevel.INFO,
            action_required=False,
        )
        assert s.action_required is False

    def test_comprehensive_response(self):
        section = AnalysisSectionSummary(
            status=BilingualText(en="Good", ar="جيد"),
            alert_level=AlertLevel.INFO,
        )
        r = ComprehensiveAnalysisResponse(
            overall_status=AlertLevel.LOW,
            overall_score=80.0,
            overall_message=BilingualText(en="Good condition", ar="حالة جيدة"),
            health_summary=section,
            nutrient_summary=section,
            pest_summary=section,
            yield_summary=section,
        )
        assert r.overall_score == 80.0


# ── Timeline Models ──────────────────────────────────────────────────────────


class TestTimelineModels:
    def test_timeline_data_point(self):
        p = TimelineDataPoint(date="2026-03-22", ndvi=0.72, evi=0.55)
        assert p.ndvi == 0.72

    def test_timeline_trend(self):
        t = TimelineTrend(
            direction="improving",
            direction_ar="تحسن",
            change_percent=5.2,
            significance="significant",
        )
        assert t.direction == "improving"

    def test_zone_timeline_response(self):
        r = ZoneTimelineResponse(
            field_id="f1",
            zone_id="z1",
        )
        assert r.series == []


# ── Cache Stats ──────────────────────────────────────────────────────────────


class TestCacheStats:
    def test_cache_stats_response(self):
        c = CacheStatsResponse(
            hits=100,
            misses=20,
            hit_rate=0.833,
            evictions=5,
            total_entries=50,
            memory_used_kb=1024.5,
        )
        assert c.hit_rate == 0.833
        assert c.redis_connected is False


# ── Helper Functions ─────────────────────────────────────────────────────────


class TestHelperFunctions:
    def test_create_bilingual_text(self):
        t = create_bilingual_text("Hello", "مرحبا")
        assert t.en == "Hello"
        assert t.ar == "مرحبا"

    def test_create_success_response(self):
        r = create_success_response({"key": "value"}, processing_time_ms=12.5)
        assert r["status"] == "success"
        assert r["key"] == "value"
        assert r["metadata"]["processing_time_ms"] == 12.5
        assert r["metadata"]["version"] == "16.0.0"

    def test_create_success_response_cached(self):
        r = create_success_response({}, cached=True)
        assert r["metadata"]["cached"] is True

    def test_create_error_response(self):
        r = create_error_response("E1001", "Invalid input", "إدخال غير صالح")
        assert r["status"] == "error"
        assert r["error"]["code"] == "E1001"
        assert r["error"]["message"] == "Invalid input"
        assert r["error"]["message_ar"] == "إدخال غير صالح"

    def test_create_error_response_with_details(self):
        r = create_error_response(
            "E1002", "Error", "خطأ",
            details={"field": "name", "reason": "required"},
        )
        assert r["error"]["details"]["field"] == "name"

    def test_create_error_response_without_details(self):
        r = create_error_response("E1003", "Error", "خطأ")
        assert "details" not in r["error"]

    def test_get_alert_level_critical(self):
        assert get_alert_level_from_severity("critical") == AlertLevel.CRITICAL

    def test_get_alert_level_high(self):
        assert get_alert_level_from_severity("high") == AlertLevel.HIGH

    def test_get_alert_level_medium(self):
        assert get_alert_level_from_severity("medium") == AlertLevel.MEDIUM

    def test_get_alert_level_low(self):
        assert get_alert_level_from_severity("low") == AlertLevel.LOW

    def test_get_alert_level_healthy(self):
        assert get_alert_level_from_severity("healthy") == AlertLevel.INFO

    def test_get_alert_level_none(self):
        assert get_alert_level_from_severity("none") == AlertLevel.INFO

    def test_get_alert_level_unknown(self):
        assert get_alert_level_from_severity("unknown") == AlertLevel.INFO

    def test_get_alert_level_case_insensitive(self):
        assert get_alert_level_from_severity("CRITICAL") == AlertLevel.CRITICAL
        assert get_alert_level_from_severity("High") == AlertLevel.HIGH

    def test_get_health_score_no_detections(self):
        assert get_health_score([], "healthy") == 100.0

    def test_get_health_score_healthy(self):
        score = get_health_score(["d1"], "healthy")
        assert score == 95.0  # 100 - 5

    def test_get_health_score_critical(self):
        score = get_health_score(["d1", "d2", "d3"], "critical")
        assert score == 0.0  # 15 - 15 = 0

    def test_get_health_score_fair(self):
        score = get_health_score(["d1"], "fair")
        assert score == 60.0  # 65 - 5

    def test_get_health_score_unknown_status(self):
        score = get_health_score(["d1"], "unknown")
        assert score == 45.0  # 50 - 5

    def test_get_health_score_many_detections_capped(self):
        detections = [f"d{i}" for i in range(10)]
        score = get_health_score(detections, "good")
        assert score == 55.0  # 85 - 30 (capped at 30)

    def test_get_health_score_floor_at_zero(self):
        detections = [f"d{i}" for i in range(6)]
        score = get_health_score(detections, "critical")
        assert score == 0.0  # max(0, 15 - 30) = 0
