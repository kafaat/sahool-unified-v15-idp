"""
Tests for Disease Rules Engine - advisory-service
"""

import pytest
from src.engine.disease_rules import (
    DiseaseAssessment,
    _adjust_for_weather,
    assess_from_image_event,
    assess_from_symptoms,
    get_action_details,
)


class TestDiseaseAssessment:
    """Tests for DiseaseAssessment model"""

    def test_to_dict(self):
        a = DiseaseAssessment(
            disease_id="test_disease",
            category="disease",
            severity="high",
            title_ar="اختبار",
            title_en="Test",
            actions=["spray_copper"],
            confidence=0.85,
            urgency_hours=24,
            details={"key": "value"},
        )
        d = a.to_dict()
        assert d["disease_id"] == "test_disease"
        assert d["category"] == "disease"
        assert d["severity"] == "high"
        assert d["confidence"] == 0.85
        assert d["urgency_hours"] == 24
        assert d["details"] == {"key": "value"}
        assert d["actions"] == ["spray_copper"]

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
class TestAssessFromImageEvent:
    """Tests for assess_from_image_event function"""

    def test_low_confidence_returns_none(self):
        result = assess_from_image_event("tomato_late_blight", confidence=0.5)
        assert result is None

    def test_unknown_disease_returns_none(self):
        result = assess_from_image_event("nonexistent_disease", confidence=0.9)
        assert result is None

    def test_valid_assessment(self):
        result = assess_from_image_event("tomato_late_blight", confidence=0.85)
        assert result is not None
        assert isinstance(result, DiseaseAssessment)
        assert result.disease_id == "tomato_late_blight"
        assert result.category == "disease"
        assert result.confidence == 0.85
        assert "اشتباه" in result.title_ar
        assert "Suspected" in result.title_en

    def test_boundary_confidence_060(self):
        # Exactly 0.60 should be accepted (>= 0.60 fails, < 0.60)
        result = assess_from_image_event("tomato_late_blight", confidence=0.60)
        assert result is not None

    def test_confidence_just_below_threshold(self):
        result = assess_from_image_event("tomato_late_blight", confidence=0.59)
        assert result is None

    def test_weather_adjustment_humidity(self):
        weather = {"humidity": 90, "temperature": 20}
        result = assess_from_image_event(
            "tomato_early_blight",
            confidence=0.8,
            weather_context=weather,
        )
        assert result is not None
        # Early blight has conditions humidity_min=60, so high humidity should escalate

    def test_weather_adjustment_rain(self):
        weather = {"precipitation": 10}
        result = assess_from_image_event(
            "tomato_late_blight",
            confidence=0.8,
            weather_context=weather,
        )
        assert result is not None
        # Late blight spreads via rain_splash, so rain should increase urgency

    def test_details_include_symptoms(self):
        result = assess_from_image_event("wheat_rust", confidence=0.8)
        assert result is not None
        assert "symptoms_ar" in result.details
        assert "symptoms_en" in result.details
class TestAssessFromSymptoms:
    """Tests for assess_from_symptoms function"""

    def test_matching_symptoms_ar(self):
        results = assess_from_symptoms(
            symptoms=["بقع مائية على الأوراق", "بقع بنية داكنة"],
            crop="tomato",
            lang="ar",
        )
        assert len(results) > 0
        # Should match late blight
        ids = [r.disease_id for r in results]
        assert "tomato_late_blight" in ids

    def test_matching_symptoms_en(self):
        results = assess_from_symptoms(
            symptoms=["leaf yellowing", "leaf curling"],
            crop="tomato",
            lang="en",
        )
        assert len(results) > 0

    def test_no_matching_symptoms(self):
        results = assess_from_symptoms(
            symptoms=["completely unrelated symptom xyz"],
            crop="tomato",
            lang="en",
        )
        assert len(results) == 0

    def test_general_diseases_matched(self):
        # Aphid symptoms should match for any crop
        results = assess_from_symptoms(
            symptoms=["leaf curling"],
            crop="tomato",
            lang="en",
        )
        ids = [r.disease_id for r in results]
        # aphid_infestation has "Leaf curling" as a symptom and is "general" crop
        assert "aphid_infestation" in ids

    def test_results_sorted_by_confidence(self):
        results = assess_from_symptoms(
            symptoms=["leaf yellowing", "brown spots"],
            crop="tomato",
            lang="en",
        )
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].confidence >= results[i + 1].confidence

    def test_max_5_results(self):
        # Even with many matching symptoms, max 5 returned
        results = assess_from_symptoms(
            symptoms=["yellowing", "spots", "rot", "mold", "curling", "stunted"],
            crop="general",
            lang="en",
        )
        assert len(results) <= 5

    def test_wrong_crop_excluded(self):
        results = assess_from_symptoms(
            symptoms=["orange or brown pustules on leaves"],
            crop="banana",  # wheat_rust only applies to wheat
            lang="en",
        )
        # wheat_rust should not appear for banana (it is crop=wheat)
        ids = [r.disease_id for r in results]
        assert "wheat_rust" not in ids
class TestAdjustForWeather:
    """Tests for _adjust_for_weather function"""

    def test_high_humidity_escalates(self):
        disease = {
            "conditions": {"humidity_min": 70},
        }
        severity, urgency = _adjust_for_weather(disease, {"humidity": 80}, "medium", 48)
        assert severity == "high"
        assert urgency < 48

    def test_optimal_temperature_reduces_urgency(self):
        disease = {
            "conditions": {"temp_range": [15, 25]},
        }
        severity, urgency = _adjust_for_weather(disease, {"temperature": 20}, "medium", 48)
        assert urgency < 48

    def test_rain_with_splash_spread(self):
        disease = {
            "conditions": {"spread": "rain_splash"},
        }
        severity, urgency = _adjust_for_weather(
            disease, {"precipitation": 10}, "medium", 48
        )
        assert severity == "high"
        assert urgency < 48

    def test_no_conditions_no_change(self):
        disease = {"conditions": {}}
        severity, urgency = _adjust_for_weather(disease, {"humidity": 90}, "medium", 48)
        assert severity == "medium"
        assert urgency == 48
class TestGetActionDetails:
    """Tests for get_action_details function"""

    def test_known_action(self):
        details = get_action_details("spray_copper", "ar")
        assert details["name_ar"] == "رش بالنحاس"
        assert details["task_type"] == "spray"
        assert details["priority"] == "high"

    def test_unknown_action_returns_default(self):
        details = get_action_details("nonexistent_action", "en")
        assert details["name_en"] == "nonexistent_action"
        assert details["task_type"] == "general"

    def test_all_defined_actions_have_fields(self):
        known_actions = [
            "spray_copper", "spray_mancozeb", "remove_infected_parts",
            "avoid_overhead_irrigation", "improve_air_circulation",
            "spray_sulfur", "spray_neem_oil", "use_yellow_sticky_traps",
        ]
        for action_id in known_actions:
            d = get_action_details(action_id, "en")
            assert "name_ar" in d
            assert "name_en" in d
            assert "instructions_ar" in d
            assert "instructions_en" in d
            assert "task_type" in d
            assert "priority" in d
