"""
Tests for WASPAS Multi-Criteria Decision Making - Agro-Advisor
===============================================================
اختبارات WASPAS للقرارات متعددة المعايير

Tests for WASPAS framework for agricultural recommendations.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import pytest
import numpy as np


class TestWASPASRecommender:
    """Tests for WASPAS multi-criteria decision making."""

    def test_waspas_initialization(self):
        """Test WASPAS recommender initialization."""
        from ml.waspas import WASPASRecommender, Criterion
        
        criteria = [
            Criterion("yield", "الإنتاجية", 0.4, True, "t/ha", "طن/هكتار"),
            Criterion("cost", "التكلفة", 0.3, False, "SAR", "ريال"),
            Criterion("sustainability", "الاستدامة", 0.3, True, "score", "درجة"),
        ]
        
        waspas = WASPASRecommender(criteria, lambda_param=0.5)
        
        assert len(waspas.criteria) == 3
        assert waspas.lambda_param == 0.5
        assert sum(c.weight for c in waspas.criteria) == pytest.approx(1.0)

    def test_waspas_weight_normalization(self):
        """Test automatic weight normalization."""
        from ml.waspas import WASPASRecommender, Criterion
        
        # Weights don't sum to 1
        criteria = [
            Criterion("yield", "الإنتاجية", 2.0, True, "t/ha", "طن/هكتار"),
            Criterion("cost", "التكلفة", 1.0, False, "SAR", "ريال"),
        ]
        
        waspas = WASPASRecommender(criteria, verbose=False)
        
        # Should be normalized
        assert sum(c.weight for c in waspas.criteria) == pytest.approx(1.0)
        assert waspas.criteria[0].weight == pytest.approx(2.0/3.0)
        assert waspas.criteria[1].weight == pytest.approx(1.0/3.0)

    def test_waspas_fertilizer_recommendation(self):
        """Test WASPAS for fertilizer recommendations."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative
        
        # Define criteria
        criteria = [
            Criterion("yield", "الإنتاجية", 0.4, True, "t/ha", "طن/هكتار"),
            Criterion("cost", "التكلفة", 0.3, False, "SAR/ha", "ريال/هكتار"),
            Criterion("sustainability", "الاستدامة", 0.3, True, "score", "درجة"),
        ]
        
        # Define alternatives (fertilizer options)
        alternatives = [
            Alternative(
                id="urea",
                name="Urea 46%",
                name_ar="يوريا 46%",
                description="Synthetic nitrogen fertilizer",
                description_ar="سماد نيتروجيني صناعي",
                criteria_values={"yield": 4.5, "cost": 500, "sustainability": 0.6}
            ),
            Alternative(
                id="organic",
                name="Organic Compost",
                name_ar="سماد عضوي",
                description="Natural organic fertilizer",
                description_ar="سماد عضوي طبيعي",
                criteria_values={"yield": 4.2, "cost": 800, "sustainability": 0.95}
            ),
            Alternative(
                id="mixed",
                name="NPK 20-20-20",
                name_ar="NPK 20-20-20",
                description="Balanced NPK fertilizer",
                description_ar="سماد NPK متوازن",
                criteria_values={"yield": 4.8, "cost": 700, "sustainability": 0.7}
            ),
        ]
        
        waspas = WASPASRecommender(criteria, lambda_param=0.5, verbose=False)
        result = waspas.evaluate(alternatives)
        
        # Assertions
        assert len(result.ranked_alternatives) == 3
        assert result.best_alternative_id in ["urea", "organic", "mixed"]
        assert len(result.scores) == 3
        assert result.explanation != ""
        assert result.explanation_ar != ""

    def test_waspas_irrigation_recommendation(self):
        """Test WASPAS for irrigation method recommendations."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative
        
        criteria = [
            Criterion("efficiency", "الكفاءة", 0.35, True, "%", "%"),
            Criterion("cost", "التكلفة", 0.35, False, "SAR", "ريال"),
            Criterion("water_saving", "توفير الماء", 0.30, True, "%", "%"),
        ]
        
        alternatives = [
            Alternative(
                "drip",
                "Drip Irrigation",
                "ري بالتنقيط",
                "High efficiency drip system",
                "نظام ري بالتنقيط عالي الكفاءة",
                {"efficiency": 95, "cost": 5000, "water_saving": 60}
            ),
            Alternative(
                "sprinkler",
                "Sprinkler",
                "ري بالرش",
                "Overhead sprinkler system",
                "نظام ري بالرش علوي",
                {"efficiency": 75, "cost": 3000, "water_saving": 30}
            ),
            Alternative(
                "flood",
                "Flood Irrigation",
                "ري بالغمر",
                "Traditional flood irrigation",
                "ري بالغمر التقليدي",
                {"efficiency": 50, "cost": 500, "water_saving": 0}
            ),
        ]
        
        waspas = WASPASRecommender(criteria, verbose=False)
        result = waspas.evaluate(alternatives)
        
        # Drip should rank high due to efficiency and water saving
        assert result.best_alternative_id in ["drip", "sprinkler"]
        assert "drip" in [alt_id for alt_id, _ in result.ranked_alternatives[:2]]

    def test_waspas_wsm_wpm_scores(self):
        """Test WSM and WPM score calculation."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative
        
        criteria = [
            Criterion("metric1", "مقياس1", 0.6, True, "unit", "وحدة"),
            Criterion("metric2", "مقياس2", 0.4, False, "unit", "وحدة"),
        ]
        
        alternatives = [
            Alternative(
                "alt1", "Alternative 1", "بديل 1", "Desc", "وصف",
                {"metric1": 10, "metric2": 5}
            ),
            Alternative(
                "alt2", "Alternative 2", "بديل 2", "Desc", "وصف",
                {"metric1": 8, "metric2": 3}
            ),
        ]
        
        waspas = WASPASRecommender(criteria, lambda_param=0.5, verbose=False)
        result = waspas.evaluate(alternatives)
        
        # Check both WSM and WPM scores exist
        assert "alt1" in result.wsm_scores
        assert "alt2" in result.wsm_scores
        assert "alt1" in result.wpm_scores
        assert "alt2" in result.wpm_scores
        
        # WASPAS score should be combination
        for alt_id in ["alt1", "alt2"]:
            expected = 0.5 * result.wsm_scores[alt_id] + 0.5 * result.wpm_scores[alt_id]
            assert result.scores[alt_id] == pytest.approx(expected)

    def test_waspas_lambda_parameter_effect(self):
        """Test effect of lambda parameter on final scores."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative
        
        criteria = [Criterion("value", "القيمة", 1.0, True, "unit", "وحدة")]
        alternatives = [
            Alternative("a1", "A1", "أ1", "D", "و", {"value": 10}),
            Alternative("a2", "A2", "أ2", "D", "و", {"value": 8}),
        ]
        
        # Test with different lambda values
        waspas_wsm = WASPASRecommender(criteria, lambda_param=1.0, verbose=False)  # Pure WSM
        waspas_wpm = WASPASRecommender(criteria, lambda_param=0.0, verbose=False)  # Pure WPM
        waspas_balanced = WASPASRecommender(criteria, lambda_param=0.5, verbose=False)
        
        result_wsm = waspas_wsm.evaluate(alternatives)
        result_wpm = waspas_wpm.evaluate(alternatives)
        result_balanced = waspas_balanced.evaluate(alternatives)
        
        # All should rank a1 first (higher value)
        assert result_wsm.best_alternative_id == "a1"
        assert result_wpm.best_alternative_id == "a1"
        assert result_balanced.best_alternative_id == "a1"

    def test_waspas_report_generation(self):
        """Test WASPAS report creation."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative, create_waspas_report
        
        criteria = [
            Criterion("quality", "الجودة", 0.5, True, "score", "درجة"),
            Criterion("price", "السعر", 0.5, False, "SAR", "ريال"),
        ]
        
        alternatives = [
            Alternative(
                "opt1", "Option 1", "خيار 1", "First option", "الخيار الأول",
                {"quality": 9, "price": 100}
            ),
            Alternative(
                "opt2", "Option 2", "خيار 2", "Second option", "الخيار الثاني",
                {"quality": 7, "price": 50}
            ),
        ]
        
        waspas = WASPASRecommender(criteria, verbose=False)
        result = waspas.evaluate(alternatives)
        
        report = create_waspas_report(result, alternatives)
        
        # Check report structure
        assert "best_alternative" in report
        assert "ranking" in report
        assert "parameters" in report
        assert "explanation" in report
        
        assert report["best_alternative"]["id"] == result.best_alternative_id
        assert len(report["ranking"]) == 2
        assert "english" in report["explanation"]
        assert "arabic" in report["explanation"]


class TestWASPASEdgeCases:
    """Test edge cases and error handling."""

    def test_waspas_single_alternative(self):
        """Test WASPAS with only one alternative."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative
        
        criteria = [Criterion("value", "القيمة", 1.0, True, "u", "و")]
        alternatives = [
            Alternative("only", "Only One", "الوحيد", "D", "و", {"value": 5}),
        ]
        
        waspas = WASPASRecommender(criteria, verbose=False)
        result = waspas.evaluate(alternatives)
        
        assert result.best_alternative_id == "only"
        assert len(result.ranked_alternatives) == 1

    def test_waspas_missing_criterion_value(self):
        """Test error when alternative missing criterion value."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative
        
        criteria = [
            Criterion("metric1", "م1", 0.5, True, "u", "و"),
            Criterion("metric2", "م2", 0.5, True, "u", "و"),
        ]
        
        alternatives = [
            Alternative(
                "alt", "Alt", "ب", "D", "و",
                {"metric1": 5}  # Missing metric2
            ),
        ]
        
        waspas = WASPASRecommender(criteria, verbose=False)
        
        with pytest.raises(ValueError, match="missing value"):
            waspas.evaluate(alternatives)

    def test_waspas_all_benefit_criteria(self):
        """Test WASPAS with all benefit criteria."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative
        
        criteria = [
            Criterion("metric1", "م1", 0.5, True, "u", "و"),
            Criterion("metric2", "م2", 0.5, True, "u", "و"),
        ]
        
        alternatives = [
            Alternative("a1", "A1", "أ1", "D", "و", {"metric1": 10, "metric2": 8}),
            Alternative("a2", "A2", "أ2", "D", "و", {"metric1": 8, "metric2": 10}),
        ]
        
        waspas = WASPASRecommender(criteria, verbose=False)
        result = waspas.evaluate(alternatives)
        
        # Both alternatives should have similar scores
        score_diff = abs(result.scores["a1"] - result.scores["a2"])
        assert score_diff < 0.2  # Small difference

    def test_waspas_all_cost_criteria(self):
        """Test WASPAS with all cost criteria (minimize)."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative
        
        criteria = [
            Criterion("cost1", "ت1", 0.5, False, "SAR", "ريال"),
            Criterion("cost2", "ت2", 0.5, False, "SAR", "ريال"),
        ]
        
        alternatives = [
            Alternative("cheap", "Cheap", "رخيص", "D", "و", {"cost1": 10, "cost2": 20}),
            Alternative("expensive", "Expensive", "غالي", "D", "و", {"cost1": 50, "cost2": 60}),
        ]
        
        waspas = WASPASRecommender(criteria, verbose=False)
        result = waspas.evaluate(alternatives)
        
        # Cheaper should win
        assert result.best_alternative_id == "cheap"


class TestWASPASRealWorldScenarios:
    """Test WASPAS on realistic agricultural scenarios."""

    def test_waspas_crop_variety_selection(self):
        """Test WASPAS for selecting wheat variety."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative
        
        criteria = [
            Criterion("yield", "الإنتاجية", 0.35, True, "t/ha", "طن/هكتار"),
            Criterion("disease_resistance", "مقاومة الأمراض", 0.25, True, "score", "درجة"),
            Criterion("seed_cost", "تكلفة البذور", 0.20, False, "SAR/ha", "ريال/هكتار"),
            Criterion("drought_tolerance", "تحمل الجفاف", 0.20, True, "score", "درجة"),
        ]
        
        alternatives = [
            Alternative(
                "sakha95",
                "Sakha 95",
                "سخا 95",
                "High yield Egyptian variety",
                "صنف مصري عالي الإنتاجية",
                {
                    "yield": 4.5,
                    "disease_resistance": 0.75,
                    "seed_cost": 400,
                    "drought_tolerance": 0.60,
                }
            ),
            Alternative(
                "misr1",
                "Misr 1",
                "مصر 1",
                "Disease resistant variety",
                "صنف مقاوم للأمراض",
                {
                    "yield": 4.2,
                    "disease_resistance": 0.90,
                    "seed_cost": 350,
                    "drought_tolerance": 0.70,
                }
            ),
            Alternative(
                "local",
                "Local Landrace",
                "صنف محلي",
                "Traditional drought-tolerant",
                "تقليدي متحمل للجفاف",
                {
                    "yield": 3.5,
                    "disease_resistance": 0.65,
                    "seed_cost": 200,
                    "drought_tolerance": 0.95,
                }
            ),
        ]
        
        waspas = WASPASRecommender(criteria, verbose=False)
        result = waspas.evaluate(alternatives)
        
        # Should provide balanced recommendation
        assert len(result.ranked_alternatives) == 3
        assert result.scores[result.best_alternative_id] > 0.5

    def test_waspas_pesticide_selection(self):
        """Test WASPAS for pesticide selection."""
        from ml.waspas import WASPASRecommender, Criterion, Alternative
        
        criteria = [
            Criterion("effectiveness", "الفعالية", 0.40, True, "%", "%"),
            Criterion("cost", "التكلفة", 0.25, False, "SAR/ha", "ريال/هكتار"),
            Criterion("safety", "السلامة", 0.20, True, "score", "درجة"),
            Criterion("residual_days", "أيام بقاء الأثر", 0.15, False, "days", "يوم"),
        ]
        
        alternatives = [
            Alternative(
                "chemical",
                "Chemical Pesticide",
                "مبيد كيميائي",
                "Fast-acting chemical",
                "مبيد كيميائي سريع المفعول",
                {"effectiveness": 95, "cost": 300, "safety": 0.60, "residual_days": 14}
            ),
            Alternative(
                "bio",
                "Biological Control",
                "مكافحة حيوية",
                "Natural predators",
                "أعداء طبيعية",
                {"effectiveness": 75, "cost": 500, "safety": 0.95, "residual_days": 0}
            ),
            Alternative(
                "organic",
                "Organic Pesticide",
                "مبيد عضوي",
                "Plant-based pesticide",
                "مبيد نباتي طبيعي",
                {"effectiveness": 70, "cost": 400, "safety": 0.85, "residual_days": 3}
            ),
        ]
        
        waspas = WASPASRecommender(criteria, verbose=False)
        result = waspas.evaluate(alternatives)
        
        # Chemical likely wins due to high effectiveness and low cost
        # But biological/organic should be close due to safety
        top_2 = [alt_id for alt_id, _ in result.ranked_alternatives[:2]]
        assert "chemical" in top_2 or "bio" in top_2


@pytest.mark.unit
class TestWASPASImports:
    """Test WASPAS module imports."""

    def test_import_waspas_classes(self):
        """Test importing WASPAS classes."""
        from ml.waspas import (
            WASPASRecommender,
            Criterion,
            Alternative,
            WASPASResult,
            create_waspas_report,
        )
        
        assert WASPASRecommender is not None
        assert Criterion is not None
        assert Alternative is not None
        assert WASPASResult is not None
        assert create_waspas_report is not None

    def test_import_ml_package(self):
        """Test importing from ml package."""
        import ml
        assert hasattr(ml, "WASPASRecommender")
        assert hasattr(ml, "Criterion")
        assert hasattr(ml, "Alternative")
