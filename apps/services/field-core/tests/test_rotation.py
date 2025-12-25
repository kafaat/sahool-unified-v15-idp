"""
Tests for Crop Rotation Planning
اختبارات تخطيط تدوير المحاصيل
"""

import pytest
from datetime import date
from src.crop_rotation import (
    CropRotationPlanner,
    CropFamily,
    SeasonPlan,
    to_dict,
)


@pytest.fixture
def planner():
    """Create a crop rotation planner instance"""
    return CropRotationPlanner()


@pytest.fixture
def sample_history():
    """Create sample field history"""
    return [
        SeasonPlan(
            season_id="S1",
            year=2022,
            season="winter",
            crop_code="WHEAT",
            crop_name_ar="قمح",
            crop_name_en="Wheat",
            crop_family=CropFamily.CEREALS,
            planting_date=date(2022, 10, 1),
            harvest_date=date(2023, 3, 1)
        ),
        SeasonPlan(
            season_id="S2",
            year=2023,
            season="winter",
            crop_code="FABA_BEAN",
            crop_name_ar="فول",
            crop_name_en="Faba Bean",
            crop_family=CropFamily.LEGUMES,
            planting_date=date(2023, 10, 1),
            harvest_date=date(2024, 3, 1)
        ),
        SeasonPlan(
            season_id="S3",
            year=2024,
            season="winter",
            crop_code="TOMATO",
            crop_name_ar="طماطم",
            crop_name_en="Tomato",
            crop_family=CropFamily.SOLANACEAE,
            planting_date=date(2024, 10, 1),
            harvest_date=date(2025, 3, 1)
        )
    ]


class TestCropRotationPlanner:
    """Test crop rotation planning functionality"""

    def test_get_crop_family(self, planner):
        """Test getting crop family for a crop code"""
        assert planner.get_crop_family("WHEAT") == CropFamily.CEREALS
        assert planner.get_crop_family("TOMATO") == CropFamily.SOLANACEAE
        assert planner.get_crop_family("FABA_BEAN") == CropFamily.LEGUMES
        assert planner.get_crop_family("ONION") == CropFamily.ALLIUMS

    @pytest.mark.asyncio
    async def test_create_rotation_plan(self, planner):
        """Test creating a rotation plan"""
        plan = await planner.create_rotation_plan(
            field_id="F001",
            field_name="Test Field",
            start_year=2025,
            num_years=5
        )

        assert plan.field_id == "F001"
        assert plan.field_name == "Test Field"
        assert plan.start_year == 2025
        assert plan.end_year == 2029
        assert len(plan.seasons) == 5
        assert 0 <= plan.diversity_score <= 100
        assert 0 <= plan.soil_health_score <= 100
        assert 0 <= plan.disease_risk_score <= 100
        assert plan.nitrogen_balance in ["positive", "neutral", "negative"]

    @pytest.mark.asyncio
    async def test_suggest_next_crop(self, planner, sample_history):
        """Test suggesting next crop based on history"""
        suggestions = await planner.suggest_next_crop(
            field_id="F001",
            history=sample_history,
            season="winter"
        )

        assert len(suggestions) > 0
        assert all(0 <= s.suitability_score <= 100 for s in suggestions)
        assert suggestions[0].suitability_score >= suggestions[-1].suitability_score  # Sorted

    def test_evaluate_rotation(self, planner, sample_history):
        """Test evaluating a rotation plan"""
        evaluation = planner.evaluate_rotation(sample_history)

        assert "diversity_score" in evaluation
        assert "soil_health_score" in evaluation
        assert "disease_risk_score" in evaluation
        assert "nitrogen_balance" in evaluation
        assert 0 <= evaluation["diversity_score"] <= 100
        assert 0 <= evaluation["soil_health_score"] <= 100
        assert 0 <= evaluation["disease_risk_score"] <= 100

    def test_check_rotation_rule_valid(self, planner):
        """Test checking rotation rule - valid case"""
        history = [
            SeasonPlan(
                season_id="S1",
                year=2023,
                season="winter",
                crop_code="WHEAT",
                crop_name_ar="قمح",
                crop_name_en="Wheat",
                crop_family=CropFamily.CEREALS
            )
        ]

        # Legumes are good after cereals
        is_valid, messages = planner.check_rotation_rule(CropFamily.LEGUMES, history)
        assert is_valid

    def test_check_rotation_rule_invalid(self, planner):
        """Test checking rotation rule - invalid case"""
        history = [
            SeasonPlan(
                season_id="S1",
                year=2024,
                season="winter",
                crop_code="TOMATO",
                crop_name_ar="طماطم",
                crop_name_en="Tomato",
                crop_family=CropFamily.SOLANACEAE
            )
        ]

        # Solanaceae should not repeat within 4 years
        is_valid, messages = planner.check_rotation_rule(CropFamily.SOLANACEAE, history)
        assert not is_valid
        assert len(messages) > 0

    def test_calculate_nitrogen_balance(self, planner):
        """Test calculating nitrogen balance"""
        # Nitrogen depleting rotation
        depleting_rotation = [
            SeasonPlan(
                season_id=f"S{i}",
                year=2020+i,
                season="winter",
                crop_code="WHEAT",
                crop_name_ar="قمح",
                crop_name_en="Wheat",
                crop_family=CropFamily.CEREALS
            )
            for i in range(3)
        ]

        balance = planner.calculate_nitrogen_balance(depleting_rotation)
        assert balance == "negative"

        # Nitrogen fixing rotation
        fixing_rotation = [
            SeasonPlan(
                season_id=f"S{i}",
                year=2020+i,
                season="winter",
                crop_code="FABA_BEAN",
                crop_name_ar="فول",
                crop_name_en="Faba Bean",
                crop_family=CropFamily.LEGUMES
            )
            for i in range(3)
        ]

        balance = planner.calculate_nitrogen_balance(fixing_rotation)
        assert balance == "positive"

    def test_get_disease_risk(self, planner, sample_history):
        """Test calculating disease risk"""
        disease_risks = planner.get_disease_risk(sample_history)

        assert isinstance(disease_risks, dict)
        # Should have some disease risks from the crops
        assert len(disease_risks) > 0

    def test_rotation_rules_exist(self, planner):
        """Test that rotation rules exist for all families"""
        for family in CropFamily:
            assert family in planner.ROTATION_RULES

    def test_crop_family_map_complete(self, planner):
        """Test that crop family map has entries"""
        assert len(planner.CROP_FAMILY_MAP) > 40  # Should have 50+ crops

        # Test some specific crops
        assert "WHEAT" in planner.CROP_FAMILY_MAP
        assert "TOMATO" in planner.CROP_FAMILY_MAP
        assert "FABA_BEAN" in planner.CROP_FAMILY_MAP

    def test_to_dict_conversion(self, sample_history):
        """Test converting dataclasses to dictionaries"""
        season = sample_history[0]
        result = to_dict(season)

        assert isinstance(result, dict)
        assert result["season_id"] == "S1"
        assert result["crop_code"] == "WHEAT"
        assert result["crop_family"] == "cereals"  # Enum converted to value

    @pytest.mark.asyncio
    async def test_rotation_diversity(self, planner):
        """Test that generated rotations have diversity"""
        plan = await planner.create_rotation_plan(
            field_id="F002",
            field_name="Diversity Test Field",
            start_year=2025,
            num_years=5
        )

        # Check that not all crops are the same family
        families = set(s.crop_family for s in plan.seasons)
        assert len(families) >= 2  # At least 2 different families

    def test_nitrogen_effect_classification(self, planner):
        """Test that nitrogen effects are properly classified"""
        # Legumes should fix nitrogen
        legume_rule = planner.ROTATION_RULES[CropFamily.LEGUMES]
        assert legume_rule.nitrogen_effect == "fix"

        # Cereals should deplete nitrogen
        cereal_rule = planner.ROTATION_RULES[CropFamily.CEREALS]
        assert cereal_rule.nitrogen_effect == "deplete"

        # Solanaceae should heavily deplete nitrogen
        solanaceae_rule = planner.ROTATION_RULES[CropFamily.SOLANACEAE]
        assert solanaceae_rule.nitrogen_effect == "heavy_deplete"

    def test_root_depth_alternation(self, planner):
        """Test root depth alternation logic"""
        # Shallow vs deep should alternate
        assert planner._check_root_alternation(
            CropFamily.CUCURBITS,  # shallow
            CropFamily.ROOT_CROPS  # deep
        )

        # Same depth should not alternate
        assert not planner._check_root_alternation(
            CropFamily.CUCURBITS,  # shallow
            CropFamily.ALLIUMS  # shallow
        )

    def test_intensive_cultivation_detection(self, planner):
        """Test detection of intensive cultivation"""
        # Create intensive rotation (4 heavy feeders, no fallow)
        intensive = [
            SeasonPlan(
                season_id=f"S{i}",
                year=2020+i,
                season="winter",
                crop_code="TOMATO",
                crop_name_ar="طماطم",
                crop_name_en="Tomato",
                crop_family=CropFamily.SOLANACEAE
            )
            for i in range(4)
        ]

        assert planner._check_intensive_cultivation(intensive)

        # Add fallow period
        with_fallow = intensive[:3] + [
            SeasonPlan(
                season_id="S4",
                year=2023,
                season="winter",
                crop_code="FALLOW",
                crop_name_ar="بور",
                crop_name_en="Fallow",
                crop_family=CropFamily.FALLOW
            )
        ]

        assert not planner._check_intensive_cultivation(with_fallow)


class TestRotationRecommendations:
    """Test rotation recommendations"""

    @pytest.mark.asyncio
    async def test_legume_after_cereal(self, planner):
        """Test that legumes are recommended after cereals"""
        history = [
            SeasonPlan(
                season_id="S1",
                year=2024,
                season="winter",
                crop_code="WHEAT",
                crop_name_ar="قمح",
                crop_name_en="Wheat",
                crop_family=CropFamily.CEREALS
            )
        ]

        suggestions = await planner.suggest_next_crop("F001", history)

        # Legumes should be highly ranked
        legume_suggestions = [s for s in suggestions if s.crop_family == CropFamily.LEGUMES]
        assert len(legume_suggestions) > 0
        assert any(s.suitability_score > 70 for s in legume_suggestions)

    @pytest.mark.asyncio
    async def test_fallow_after_intensive(self, planner):
        """Test that fallow is suggested after intensive cultivation"""
        # Create intensive cultivation history
        history = [
            SeasonPlan(
                season_id=f"S{i}",
                year=2020+i,
                season="winter",
                crop_code="COTTON",
                crop_name_ar="قطن",
                crop_name_en="Cotton",
                crop_family=CropFamily.FIBER
            )
            for i in range(4)
        ]

        suggestions = await planner.suggest_next_crop("F001", history)

        # Fallow should be suggested
        fallow_suggestions = [s for s in suggestions if s.crop_family == CropFamily.FALLOW]
        assert len(fallow_suggestions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
