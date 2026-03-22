"""
Disease Rules Engine Tests - Advisory Service
Tests for disease assessment, symptom matching, weather adjustment, and action details.
"""

import pytest

try:
    from src.engine.disease_rules import (
        DiseaseAssessment,
        _adjust_for_weather,
        assess_from_image_event,
        assess_from_symptoms,
        get_action_details,
    )
    from src.kb.diseases import DISEASES
except ImportError:
    pytest.skip("advisory-service dependencies not installed", allow_module_level=True)


# ---------------------------------------------------------------------------
# DiseaseAssessment model
# ---------------------------------------------------------------------------


class TestDiseaseAssessment:
    """Test DiseaseAssessment data class."""

    def test_basic_construction(self):
        a = DiseaseAssessment(
            disease_id="test_disease",
            category="disease",
            severity="high",
            title_ar="اختبار",
            title_en="Test Disease",
            actions=["spray_copper"],
            confidence=0.85,
            urgency_hours=24,
        )
        assert a.disease_id == "test_disease"
        assert a.severity == "high"
        assert a.confidence == 0.85
        assert a.details == {}  # default

    def test_construction_with_details(self):
        details = {"pathogen": "fungus", "extra": True}
        a = DiseaseAssessment(
            disease_id="d1",
            category="disease",
            severity="medium",
            title_ar="م",
            title_en="M",
            actions=[],
            confidence=0.5,
            urgency_hours=48,
            details=details,
        )
        assert a.details == details

    def test_to_dict(self):
        a = DiseaseAssessment(
            disease_id="d1",
            category="disease",
            severity="low",
            title_ar="عربي",
            title_en="English",
            actions=["a1", "a2"],
            confidence=0.7,
            urgency_hours=72,
            details={"key": "val"},
        )
        d = a.to_dict()
        assert isinstance(d, dict)
        assert d["disease_id"] == "d1"
        assert d["category"] == "disease"
        assert d["severity"] == "low"
        assert d["title_ar"] == "عربي"
        assert d["title_en"] == "English"
        assert d["actions"] == ["a1", "a2"]
        assert d["confidence"] == 0.7
        assert d["urgency_hours"] == 72
        assert d["details"] == {"key": "val"}

    def test_to_dict_default_details(self):
        a = DiseaseAssessment(
            disease_id="test",
            category="disease",
            severity="low",
            title_ar="t",
            title_en="t",
            actions=[],
            confidence=0.5,
            urgency_hours=48,
        )
        assert a.details == {}
        assert a.to_dict()["details"] == {}


# ---------------------------------------------------------------------------
# assess_from_image_event
# ---------------------------------------------------------------------------


class TestAssessFromImageEvent:
    """Test image-based disease assessment."""

    def test_low_confidence_returns_none(self):
        """Confidence below 0.60 should return None."""
        result = assess_from_image_event(
            condition_id="tomato_late_blight",
            confidence=0.59,
        )
        assert result is None

    def test_exactly_threshold_returns_none(self):
        """Confidence exactly at boundary (< 0.60) returns None."""
        result = assess_from_image_event(
            condition_id="tomato_late_blight",
            confidence=0.599,
        )
        assert result is None

    def test_at_threshold_returns_assessment(self):
        """Confidence at 0.60 should return assessment."""
        result = assess_from_image_event(
            condition_id="tomato_late_blight",
            confidence=0.60,
        )
        assert result is not None
        assert isinstance(result, DiseaseAssessment)
        assert result.disease_id == "tomato_late_blight"

    def test_unknown_condition_returns_none(self):
        """Unknown disease ID should return None."""
        result = assess_from_image_event(
            condition_id="nonexistent_disease_xyz",
            confidence=0.95,
        )
        assert result is None

    def test_valid_assessment_fields(self):
        """Verify all fields of a valid assessment."""
        result = assess_from_image_event(
            condition_id="tomato_late_blight",
            confidence=0.85,
            crop="tomato",
        )
        assert result is not None
        assert result.category == "disease"
        assert result.severity == "high"  # severity_default for late blight
        assert "اشتباه" in result.title_ar
        assert "Suspected" in result.title_en
        assert len(result.actions) > 0
        assert result.confidence == 0.85
        assert result.urgency_hours == 24
        assert "symptoms_ar" in result.details
        assert "symptoms_en" in result.details
        assert "pathogen" in result.details

    def test_assessment_for_each_known_disease(self):
        """Every disease in KB should produce a valid assessment at high confidence."""
        for disease_id in DISEASES:
            result = assess_from_image_event(
                condition_id=disease_id,
                confidence=0.90,
            )
            assert result is not None, f"Failed for {disease_id}"
            assert result.disease_id == disease_id
            assert 0 < result.confidence <= 1.0

    def test_without_weather_uses_defaults(self):
        """No weather context should use default severity and urgency."""
        disease = DISEASES["tomato_early_blight"]
        result = assess_from_image_event(
            condition_id="tomato_early_blight",
            confidence=0.80,
        )
        assert result.severity == disease["severity_default"]
        assert result.urgency_hours == disease["urgency_hours"]

    def test_with_weather_context_adjusts_severity(self):
        """Weather with high humidity should escalate severity for medium diseases."""
        # tomato_early_blight has severity_default=medium, humidity_min=60
        result = assess_from_image_event(
            condition_id="tomato_early_blight",
            confidence=0.80,
            weather_context={"humidity": 80, "temperature": 26},
        )
        assert result is not None
        # High humidity above 60 + temp in range [24,29] -> severity escalated
        assert result.severity == "high"

    def test_weather_with_rain_splash(self):
        """Rain + rain_splash spread should escalate severity and urgency."""
        result = assess_from_image_event(
            condition_id="tomato_late_blight",
            confidence=0.80,
            weather_context={"humidity": 90, "temperature": 20, "precipitation": 10},
        )
        assert result is not None
        # Late blight already high severity; rain should reduce urgency
        assert result.urgency_hours < 24

    def test_weather_no_humidity_key(self):
        """Weather dict without humidity key uses default of 50."""
        result = assess_from_image_event(
            condition_id="tomato_early_blight",
            confidence=0.80,
            weather_context={"temperature": 26},
        )
        assert result is not None
        # humidity defaults to 50, below humidity_min=60, no escalation on humidity
        # but temp 26 in [24,29] should halve urgency
        assert result.urgency_hours <= 48

    def test_details_include_symptoms(self):
        result = assess_from_image_event("wheat_rust", confidence=0.8)
        assert result is not None
        assert "symptoms_ar" in result.details
        assert "symptoms_en" in result.details


# ---------------------------------------------------------------------------
# _adjust_for_weather (internal helper)
# ---------------------------------------------------------------------------


class TestAdjustForWeather:
    """Test weather adjustment logic directly."""

    def test_humidity_above_min_escalates_medium_to_high(self):
        disease = {
            "conditions": {"humidity_min": 70},
        }
        severity, urgency = _adjust_for_weather(disease, {"humidity": 75}, "medium", 48)
        assert severity == "high"
        assert urgency < 48

    def test_humidity_below_min_no_change(self):
        disease = {
            "conditions": {"humidity_min": 70},
        }
        severity, urgency = _adjust_for_weather(disease, {"humidity": 60}, "medium", 48)
        assert severity == "medium"
        assert urgency == 48

    def test_temp_in_range_reduces_urgency(self):
        disease = {
            "conditions": {"temp_range": [15, 25]},
        }
        severity, urgency = _adjust_for_weather(disease, {"temperature": 20}, "medium", 48)
        assert urgency == 24  # 48 // 2

    def test_temp_out_of_range_no_change(self):
        disease = {
            "conditions": {"temp_range": [15, 25]},
        }
        severity, urgency = _adjust_for_weather(disease, {"temperature": 30}, "medium", 48)
        assert urgency == 48

    def test_rain_with_rain_splash_escalates(self):
        disease = {
            "conditions": {"spread": "rain_splash"},
        }
        severity, urgency = _adjust_for_weather(
            disease, {"precipitation": 10}, "medium", 48
        )
        assert severity == "high"
        assert urgency == max(6, 48 // 3)

    def test_rain_with_wind_rain_escalates(self):
        disease = {
            "conditions": {"spread": "wind_rain"},
        }
        severity, urgency = _adjust_for_weather(
            disease, {"precipitation": 10}, "medium", 48
        )
        assert severity == "high"

    def test_rain_below_threshold_no_change(self):
        disease = {
            "conditions": {"spread": "rain_splash"},
        }
        severity, urgency = _adjust_for_weather(
            disease, {"precipitation": 3}, "medium", 48
        )
        assert severity == "medium"
        assert urgency == 48

    def test_rain_with_non_rain_spread_no_change(self):
        disease = {
            "conditions": {"spread": "wind"},
        }
        severity, urgency = _adjust_for_weather(
            disease, {"precipitation": 20}, "medium", 48
        )
        assert severity == "medium"

    def test_high_severity_not_escalated_by_humidity(self):
        """Only medium severity is escalated to high; high stays high."""
        disease = {
            "conditions": {"humidity_min": 70},
        }
        severity, urgency = _adjust_for_weather(disease, {"humidity": 90}, "high", 24)
        assert severity == "high"  # stays high
        assert urgency == max(12, 24 // 2)

    def test_no_conditions_key_no_crash(self):
        """Disease without conditions should not crash."""
        disease = {}
        severity, urgency = _adjust_for_weather(disease, {"humidity": 90}, "medium", 48)
        assert severity == "medium"
        assert urgency == 48

    def test_no_conditions_no_change(self):
        disease = {"conditions": {}}
        severity, urgency = _adjust_for_weather(disease, {"humidity": 90}, "medium", 48)
        assert severity == "medium"
        assert urgency == 48

    def test_combined_humidity_temp_rain(self):
        """All three triggers active at once."""
        disease = {
            "conditions": {
                "humidity_min": 60,
                "temp_range": [15, 25],
                "spread": "rain_splash",
            },
        }
        weather = {"humidity": 80, "temperature": 20, "precipitation": 10}
        severity, urgency = _adjust_for_weather(disease, weather, "medium", 72)
        assert severity == "high"
        # Urgency reduced by humidity (72//2=36), then temp (36//2=18->max(12,18)=18),
        # then rain (18//3=6->max(6,6)=6)
        assert urgency <= 18

    def test_urgency_floor_at_12_for_humidity(self):
        """Urgency should never go below 12 from humidity alone."""
        disease = {
            "conditions": {"humidity_min": 50},
        }
        severity, urgency = _adjust_for_weather(disease, {"humidity": 80}, "medium", 12)
        assert urgency >= 6  # floor from subsequent steps at minimum

    def test_urgency_floor_at_6_for_rain(self):
        """Urgency should never go below 6 from rain."""
        disease = {
            "conditions": {"spread": "rain_splash"},
        }
        severity, urgency = _adjust_for_weather(disease, {"precipitation": 100}, "medium", 12)
        assert urgency >= 6


# ---------------------------------------------------------------------------
# assess_from_symptoms
# ---------------------------------------------------------------------------


class TestAssessFromSymptoms:
    """Test symptom-based disease assessment."""

    def test_no_matching_crop_returns_empty(self):
        """Symptoms for a crop with no diseases should return empty."""
        result = assess_from_symptoms(
            symptoms=["random symptom"],
            crop="nonexistent_crop_xyz",
        )
        assert result == []

    def test_matching_symptoms_arabic(self):
        """Arabic symptom matching for tomato late blight."""
        result = assess_from_symptoms(
            symptoms=["بقع مائية على الأوراق", "تعفن الثمار"],
            crop="tomato",
            lang="ar",
        )
        assert len(result) > 0
        # Late blight should be among results
        ids = [a.disease_id for a in result]
        assert "tomato_late_blight" in ids

    def test_matching_symptoms_english(self):
        """English symptom matching."""
        result = assess_from_symptoms(
            symptoms=["Water-soaked lesions on leaves", "Fruit rot"],
            crop="tomato",
            lang="en",
        )
        assert len(result) > 0
        ids = [a.disease_id for a in result]
        assert "tomato_late_blight" in ids

    def test_partial_symptom_match(self):
        """Partial symptom text should still match (substring matching)."""
        result = assess_from_symptoms(
            symptoms=["leaf yellowing"],
            crop="tomato",
            lang="en",
        )
        assert len(result) > 0

    def test_general_crop_diseases_included(self):
        """General diseases (crop=general) should match any crop."""
        result = assess_from_symptoms(
            symptoms=["leaf curling", "honeydew"],
            crop="tomato",
            lang="en",
        )
        # aphid_infestation is "general" and has "leaf curling"
        ids = [a.disease_id for a in result]
        assert "aphid_infestation" in ids

    def test_results_sorted_by_confidence(self):
        """Results should be sorted by confidence descending."""
        result = assess_from_symptoms(
            symptoms=["leaf yellowing", "stunted growth"],
            crop="tomato",
            lang="en",
        )
        if len(result) >= 2:
            for i in range(len(result) - 1):
                assert result[i].confidence >= result[i + 1].confidence

    def test_max_five_results(self):
        """Should return at most 5 results."""
        # Use many symptoms to match many diseases
        result = assess_from_symptoms(
            symptoms=[
                "leaf yellowing",
                "leaf curling",
                "spots",
                "rot",
                "mold",
                "insects",
                "stunted",
            ],
            crop="tomato",
            lang="en",
        )
        assert len(result) <= 5

    def test_confidence_capped_at_0_9(self):
        """Confidence should not exceed 0.9."""
        result = assess_from_symptoms(
            symptoms=DISEASES["tomato_late_blight"]["symptoms_en"],
            crop="tomato",
            lang="en",
        )
        for a in result:
            assert a.confidence <= 0.9

    def test_assessment_has_details(self):
        """Each assessment should have matched_symptoms and total_symptoms in details."""
        result = assess_from_symptoms(
            symptoms=["بقع مائية على الأوراق"],
            crop="tomato",
            lang="ar",
        )
        for a in result:
            assert "matched_symptoms" in a.details
            assert "total_symptoms" in a.details
            assert a.details["matched_symptoms"] > 0

    def test_no_matching_symptoms_returns_empty(self):
        """Completely unrelated symptoms should return empty."""
        result = assess_from_symptoms(
            symptoms=["this is not a real symptom at all"],
            crop="tomato",
            lang="en",
        )
        assert result == []

    def test_wheat_rust_symptoms(self):
        """Test wheat-specific disease matching."""
        result = assess_from_symptoms(
            symptoms=["orange or brown pustules on leaves"],
            crop="wheat",
            lang="en",
        )
        ids = [a.disease_id for a in result]
        assert "wheat_rust" in ids

    def test_wrong_crop_excluded(self):
        results = assess_from_symptoms(
            symptoms=["orange or brown pustules on leaves"],
            crop="banana",  # wheat_rust only applies to wheat
            lang="en",
        )
        # wheat_rust should not appear for banana (it is crop=wheat)
        ids = [r.disease_id for r in results]
        assert "wheat_rust" not in ids

    def test_case_insensitive_matching(self):
        """Symptom matching should be case-insensitive."""
        result = assess_from_symptoms(
            symptoms=["LEAF YELLOWING"],
            crop="tomato",
            lang="en",
        )
        assert len(result) > 0


# ---------------------------------------------------------------------------
# get_action_details
# ---------------------------------------------------------------------------


class TestGetActionDetails:
    """Test action detail retrieval."""

    def test_known_action_spray_copper(self):
        details = get_action_details("spray_copper", "en")
        assert details["name_en"] == "Copper Spray"
        assert details["task_type"] == "spray"
        assert details["priority"] == "high"

    def test_known_action_spray_copper_ar(self):
        details = get_action_details("spray_copper", "ar")
        assert details["name_ar"] == "رش بالنحاس"
        assert details["task_type"] == "spray"
        assert details["priority"] == "high"

    def test_known_action_spray_mancozeb(self):
        details = get_action_details("spray_mancozeb", "ar")
        assert details["name_ar"] == "رش مانكوزيب"

    def test_known_action_remove_infected_parts(self):
        details = get_action_details("remove_infected_parts", "en")
        assert details["task_type"] == "manual"
        assert details["priority"] == "medium"

    def test_known_action_avoid_overhead_irrigation(self):
        details = get_action_details("avoid_overhead_irrigation", "en")
        assert details["task_type"] == "irrigation"

    def test_known_action_improve_air_circulation(self):
        details = get_action_details("improve_air_circulation", "en")
        assert details["priority"] == "low"

    def test_known_action_spray_sulfur(self):
        details = get_action_details("spray_sulfur", "en")
        assert "sulfur" in details["instructions_en"].lower()

    def test_known_action_spray_neem_oil(self):
        details = get_action_details("spray_neem_oil", "en")
        assert "neem" in details["instructions_en"].lower()

    def test_known_action_yellow_sticky_traps(self):
        details = get_action_details("use_yellow_sticky_traps", "en")
        assert details["task_type"] == "monitoring"

    def test_unknown_action_fallback(self):
        details = get_action_details("totally_unknown_action", "en")
        assert details["name_en"] == "totally_unknown_action"
        assert details["task_type"] == "general"
        assert "Consult" in details["instructions_en"]
        assert "specialist" in details["instructions_en"].lower()

    def test_unknown_action_fallback_arabic(self):
        details = get_action_details("xyz", "ar")
        assert details["name_ar"] == "xyz"
        assert "المختص" in details["instructions_ar"]

    def test_all_known_actions_have_required_fields(self):
        """Every known action should have all required fields."""
        known_actions = [
            "spray_copper",
            "spray_mancozeb",
            "remove_infected_parts",
            "avoid_overhead_irrigation",
            "improve_air_circulation",
            "spray_sulfur",
            "spray_neem_oil",
            "use_yellow_sticky_traps",
        ]
        for action_id in known_actions:
            details = get_action_details(action_id, "en")
            assert "name_ar" in details, f"Missing name_ar for {action_id}"
            assert "name_en" in details, f"Missing name_en for {action_id}"
            assert "instructions_ar" in details, f"Missing instructions_ar for {action_id}"
            assert "instructions_en" in details, f"Missing instructions_en for {action_id}"
            assert "task_type" in details, f"Missing task_type for {action_id}"
            assert "priority" in details, f"Missing priority for {action_id}"
