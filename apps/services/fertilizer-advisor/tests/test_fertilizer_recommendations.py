"""
Comprehensive Tests for Fertilizer Recommendations - Fertilizer Advisor Service
اختبارات شاملة لتوصيات الأسمدة - خدمة مستشار السماد

This module tests:
- NPK requirement calculations
- Fertilizer selection algorithms
- Soil analysis interpretation
- Application scheduling
- Cost calculations
- Data validation
- API endpoints
- Crop and growth stage specific recommendations
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create FastAPI test client"""
    from src.main import app
    return TestClient(app)


@pytest.fixture
def sample_soil_analysis():
    """Sample soil analysis data"""
    return {
        "field_id": "test_field_001",
        "analysis_date": datetime.now().isoformat(),
        "ph": 6.8,
        "nitrogen_ppm": 30.0,
        "phosphorus_ppm": 25.0,
        "potassium_ppm": 150.0,
        "organic_matter_percent": 2.5,
        "ec_ds_m": 1.5,
        "calcium_ppm": 500.0,
        "magnesium_ppm": 100.0,
        "sulfur_ppm": 15.0,
        "iron_ppm": 5.0,
        "zinc_ppm": 2.0,
        "soil_type": "loamy"
    }


@pytest.fixture
def sample_fertilizer_request():
    """Sample fertilizer recommendation request"""
    return {
        "field_id": "test_field_001",
        "crop": "tomato",
        "growth_stage": "vegetative",
        "area_hectares": 5.0,
        "soil_type": "loamy",
        "organic_only": False
    }


class TestNPKRequirementCalculation:
    """Test NPK requirement calculations"""

    def test_basic_npk_calculation(self):
        """Test basic NPK calculation for crop"""
        from src.main import calculate_npk_needs, CropType, GrowthStage

        needs = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=10.0,
            target_yield=None,
            soil_analysis=None
        )

        # Should return NPK values
        assert "N" in needs
        assert "P" in needs
        assert "K" in needs

        # All should be positive
        assert needs["N"] > 0
        assert needs["P"] > 0
        assert needs["K"] > 0

    def test_npk_scales_with_area(self):
        """Test that NPK requirements scale with area"""
        from src.main import calculate_npk_needs, CropType, GrowthStage

        needs_small = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=5.0,
            target_yield=None,
            soil_analysis=None
        )

        needs_large = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=10.0,
            target_yield=None,
            soil_analysis=None
        )

        # Should be approximately 2x
        assert abs((needs_large["N"] / needs_small["N"]) - 2.0) < 0.1
        assert abs((needs_large["P"] / needs_small["P"]) - 2.0) < 0.1
        assert abs((needs_large["K"] / needs_small["K"]) - 2.0) < 0.1

    def test_growth_stage_impact(self):
        """Test that growth stage affects NPK distribution"""
        from src.main import calculate_npk_needs, CropType, GrowthStage

        needs_seedling = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.SEEDLING,
            area_ha=10.0,
            target_yield=None,
            soil_analysis=None
        )

        needs_fruiting = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.FRUITING,
            area_ha=10.0,
            target_yield=None,
            soil_analysis=None
        )

        # Different stages should have different requirements
        assert needs_seedling["N"] != needs_fruiting["N"] or \
               needs_seedling["P"] != needs_fruiting["P"] or \
               needs_seedling["K"] != needs_fruiting["K"]

        # Fruiting stage typically needs more K
        assert needs_fruiting["K"] > needs_seedling["K"]

    def test_target_yield_adjustment(self):
        """Test adjustment for target yield"""
        from src.main import calculate_npk_needs, CropType, GrowthStage, CROP_NPK_REQUIREMENTS

        base_yield = CROP_NPK_REQUIREMENTS[CropType.TOMATO]["target_yield"]

        needs_normal = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=10.0,
            target_yield=base_yield,
            soil_analysis=None
        )

        needs_high = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=10.0,
            target_yield=base_yield * 1.5,  # 50% higher target
            soil_analysis=None
        )

        # Higher target should require more fertilizer
        assert needs_high["N"] > needs_normal["N"]
        assert needs_high["P"] > needs_normal["P"]
        assert needs_high["K"] > needs_normal["K"]

    def test_soil_analysis_nitrogen_adjustment(self):
        """Test NPK adjustment based on soil nitrogen levels"""
        from src.main import calculate_npk_needs, CropType, GrowthStage, SoilAnalysis

        # High nitrogen soil
        high_n_soil = SoilAnalysis(
            field_id="test",
            analysis_date=datetime.now(),
            ph=6.5,
            nitrogen_ppm=50.0,  # High
            phosphorus_ppm=20.0,
            potassium_ppm=150.0,
            organic_matter_percent=3.0,
            ec_ds_m=1.5,
            soil_type="loamy"
        )

        # Low nitrogen soil
        low_n_soil = SoilAnalysis(
            field_id="test",
            analysis_date=datetime.now(),
            ph=6.5,
            nitrogen_ppm=15.0,  # Low
            phosphorus_ppm=20.0,
            potassium_ppm=150.0,
            organic_matter_percent=3.0,
            ec_ds_m=1.5,
            soil_type="loamy"
        )

        needs_high_n = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=10.0,
            target_yield=None,
            soil_analysis=high_n_soil
        )

        needs_low_n = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=10.0,
            target_yield=None,
            soil_analysis=low_n_soil
        )

        # High N soil should need less N fertilizer
        assert needs_high_n["N"] < needs_low_n["N"]

    def test_soil_analysis_phosphorus_adjustment(self):
        """Test P adjustment based on soil P levels"""
        from src.main import calculate_npk_needs, CropType, GrowthStage, SoilAnalysis

        high_p_soil = SoilAnalysis(
            field_id="test",
            analysis_date=datetime.now(),
            ph=6.5,
            nitrogen_ppm=30.0,
            phosphorus_ppm=40.0,  # High
            potassium_ppm=150.0,
            organic_matter_percent=3.0,
            ec_ds_m=1.5,
            soil_type="loamy"
        )

        needs = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=10.0,
            target_yield=None,
            soil_analysis=high_p_soil
        )

        needs_no_soil = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=10.0,
            target_yield=None,
            soil_analysis=None
        )

        # High P soil should need less P fertilizer
        assert needs["P"] < needs_no_soil["P"]

    def test_low_organic_matter_adjustment(self):
        """Test N increase for low organic matter"""
        from src.main import calculate_npk_needs, CropType, GrowthStage, SoilAnalysis

        low_om_soil = SoilAnalysis(
            field_id="test",
            analysis_date=datetime.now(),
            ph=6.5,
            nitrogen_ppm=30.0,
            phosphorus_ppm=20.0,
            potassium_ppm=150.0,
            organic_matter_percent=1.0,  # Very low
            ec_ds_m=1.5,
            soil_type="loamy"
        )

        needs_low_om = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=10.0,
            target_yield=None,
            soil_analysis=low_om_soil
        )

        needs_no_soil = calculate_npk_needs(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=10.0,
            target_yield=None,
            soil_analysis=None
        )

        # Low OM should require more N
        assert needs_low_om["N"] > needs_no_soil["N"]


class TestFertilizerSelection:
    """Test fertilizer selection algorithm"""

    def test_select_chemical_fertilizers(self):
        """Test selection of chemical fertilizers"""
        from src.main import select_fertilizers

        npk_needs = {"N": 100.0, "P": 50.0, "K": 120.0}

        recommendations = select_fertilizers(
            npk_needs=npk_needs,
            organic_only=False,
            budget=None
        )

        # Should return fertilizer recommendations
        assert len(recommendations) > 0

        # Should use chemical fertilizers
        from src.main import FertilizerType
        fert_types = [r.fertilizer_type for r in recommendations]
        assert FertilizerType.NPK_20_20_20 in fert_types or \
               FertilizerType.UREA in fert_types

    def test_select_organic_fertilizers_only(self):
        """Test selection of organic fertilizers only"""
        from src.main import select_fertilizers, FertilizerType

        npk_needs = {"N": 100.0, "P": 50.0, "K": 120.0}

        recommendations = select_fertilizers(
            npk_needs=npk_needs,
            organic_only=True,
            budget=None
        )

        # Should only use organic fertilizers
        organic_types = {
            FertilizerType.ORGANIC_COMPOST,
            FertilizerType.CHICKEN_MANURE,
            FertilizerType.COW_MANURE
        }

        for rec in recommendations:
            assert rec.fertilizer_type in organic_types

    def test_fertilizer_quantities_positive(self):
        """Test that fertilizer quantities are positive"""
        from src.main import select_fertilizers

        npk_needs = {"N": 100.0, "P": 50.0, "K": 120.0}

        recommendations = select_fertilizers(
            npk_needs=npk_needs,
            organic_only=False,
            budget=None
        )

        for rec in recommendations:
            assert rec.quantity_kg_per_hectare > 0
            assert rec.quantity_kg_per_donum > 0

    def test_fertilizer_cost_calculation(self):
        """Test fertilizer cost calculation"""
        from src.main import select_fertilizers

        npk_needs = {"N": 100.0, "P": 50.0, "K": 120.0}

        recommendations = select_fertilizers(
            npk_needs=npk_needs,
            organic_only=False,
            budget=None
        )

        for rec in recommendations:
            # Cost should be positive
            assert rec.cost_estimate_yer > 0

            # Cost should be quantity * price_per_kg
            from src.main import FERTILIZER_PRICES
            expected_cost = rec.quantity_kg_per_hectare * \
                          FERTILIZER_PRICES[rec.fertilizer_type]
            assert abs(rec.cost_estimate_yer - expected_cost) < 10.0

    def test_application_method_assignment(self):
        """Test that appropriate application methods are assigned"""
        from src.main import select_fertilizers, ApplicationMethod

        npk_needs = {"N": 100.0, "P": 50.0, "K": 120.0}

        recommendations = select_fertilizers(
            npk_needs=npk_needs,
            organic_only=False,
            budget=None
        )

        for rec in recommendations:
            # Should have a valid application method
            assert rec.application_method in ApplicationMethod
            assert rec.application_method_ar is not None


class TestSoilAnalysisInterpretation:
    """Test soil analysis interpretation"""

    def test_interpret_healthy_soil(self, test_client):
        """Test interpretation of healthy soil"""
        healthy_soil = {
            "field_id": "test_field",
            "analysis_date": datetime.now().isoformat(),
            "ph": 6.8,
            "nitrogen_ppm": 35.0,
            "phosphorus_ppm": 25.0,
            "potassium_ppm": 180.0,
            "organic_matter_percent": 3.5,
            "ec_ds_m": 1.2,
            "soil_type": "loamy"
        }

        response = test_client.post("/v1/soil-analysis/interpret", json=healthy_soil)

        assert response.status_code == 200
        data = response.json()

        # Should have mostly green indicators
        interpretations = data["interpretations_ar"]
        green_count = sum(1 for i in interpretations if "🟢" in i)
        assert green_count >= 3

        # Overall fertility should be good
        assert data["overall_fertility"] in ["جيدة", "متوسطة"]

    def test_interpret_acidic_soil(self, test_client):
        """Test interpretation of acidic soil"""
        acidic_soil = {
            "field_id": "test_field",
            "analysis_date": datetime.now().isoformat(),
            "ph": 5.0,  # Too acidic
            "nitrogen_ppm": 30.0,
            "phosphorus_ppm": 20.0,
            "potassium_ppm": 150.0,
            "organic_matter_percent": 2.5,
            "ec_ds_m": 1.2,
            "soil_type": "loamy"
        }

        response = test_client.post("/v1/soil-analysis/interpret", json=acidic_soil)

        assert response.status_code == 200
        data = response.json()

        # Should flag acidic pH
        assert any("حامضية" in i for i in data["interpretations_ar"])

        # Should recommend lime
        assert any("جير" in r for r in data["recommendations_ar"])

    def test_interpret_alkaline_soil(self, test_client):
        """Test interpretation of alkaline soil"""
        alkaline_soil = {
            "field_id": "test_field",
            "analysis_date": datetime.now().isoformat(),
            "ph": 8.5,  # Too alkaline
            "nitrogen_ppm": 30.0,
            "phosphorus_ppm": 20.0,
            "potassium_ppm": 150.0,
            "organic_matter_percent": 2.5,
            "ec_ds_m": 1.2,
            "soil_type": "loamy"
        }

        response = test_client.post("/v1/soil-analysis/interpret", json=alkaline_soil)

        assert response.status_code == 200
        data = response.json()

        # Should flag alkaline pH
        assert any("قلوية" in i for i in data["interpretations_ar"])

        # Should recommend sulfur or acidic fertilizer
        assert any("كبريت" in r or "حامضي" in r for r in data["recommendations_ar"])

    def test_interpret_nitrogen_deficiency(self, test_client):
        """Test interpretation of nitrogen deficiency"""
        n_deficient_soil = {
            "field_id": "test_field",
            "analysis_date": datetime.now().isoformat(),
            "ph": 6.5,
            "nitrogen_ppm": 10.0,  # Very low
            "phosphorus_ppm": 25.0,
            "potassium_ppm": 180.0,
            "organic_matter_percent": 2.5,
            "ec_ds_m": 1.2,
            "soil_type": "loamy"
        }

        response = test_client.post("/v1/soil-analysis/interpret", json=n_deficient_soil)

        assert response.status_code == 200
        data = response.json()

        # Should flag N deficiency
        assert any("نقص النيتروجين" in i for i in data["interpretations_ar"])

        # Should recommend N fertilizer
        assert any("يوريا" in r or "نترات" in r for r in data["recommendations_ar"])

    def test_interpret_high_salinity(self, test_client):
        """Test interpretation of high salinity"""
        saline_soil = {
            "field_id": "test_field",
            "analysis_date": datetime.now().isoformat(),
            "ph": 7.0,
            "nitrogen_ppm": 30.0,
            "phosphorus_ppm": 20.0,
            "potassium_ppm": 150.0,
            "organic_matter_percent": 2.5,
            "ec_ds_m": 5.0,  # Very high salinity
            "soil_type": "loamy"
        }

        response = test_client.post("/v1/soil-analysis/interpret", json=saline_soil)

        assert response.status_code == 200
        data = response.json()

        # Should flag high salinity
        assert any("ملوحة مرتفعة" in i for i in data["interpretations_ar"])

        # Should recommend leaching
        assert any("غسيل" in r for r in data["recommendations_ar"])


class TestFertilizationSchedule:
    """Test fertilization schedule generation"""

    def test_generate_schedule_seedling_stage(self):
        """Test schedule for seedling stage"""
        from src.main import generate_schedule, CropType, GrowthStage, FertilizerRecommendation, FertilizerType, ApplicationMethod

        recommendations = [
            FertilizerRecommendation(
                fertilizer_type=FertilizerType.NPK_15_15_15,
                fertilizer_name_ar="سماد مركب",
                fertilizer_name_en="NPK 15-15-15",
                quantity_kg_per_hectare=100.0,
                quantity_kg_per_donum=10.0,
                application_method=ApplicationMethod.BROADCAST,
                application_method_ar="نثر",
                timing_ar="صباحاً",
                timing_en="Morning",
                npk_content={"N": 15, "P": 15, "K": 15},
                cost_estimate_yer=100000.0,
                notes_ar=["ملاحظة"],
                notes_en=["Note"]
            )
        ]

        schedule = generate_schedule(
            crop=CropType.TOMATO,
            stage=GrowthStage.SEEDLING,
            recommendations=recommendations
        )

        # Seedling stage should have 2 applications
        assert len(schedule) == 2

        # Each application should have date and fertilizers
        for app in schedule:
            assert "date" in app
            assert "fertilizers" in app
            assert len(app["fertilizers"]) > 0

    def test_generate_schedule_vegetative_stage(self):
        """Test schedule for vegetative stage"""
        from src.main import generate_schedule, CropType, GrowthStage, FertilizerRecommendation, FertilizerType, ApplicationMethod

        recommendations = [
            FertilizerRecommendation(
                fertilizer_type=FertilizerType.UREA,
                fertilizer_name_ar="يوريا",
                fertilizer_name_en="Urea",
                quantity_kg_per_hectare=120.0,
                quantity_kg_per_donum=12.0,
                application_method=ApplicationMethod.SIDE_DRESSING,
                application_method_ar="تسميد جانبي",
                timing_ar="صباحاً",
                timing_en="Morning",
                npk_content={"N": 46, "P": 0, "K": 0},
                cost_estimate_yer=96000.0,
                notes_ar=[],
                notes_en=[]
            )
        ]

        schedule = generate_schedule(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            recommendations=recommendations
        )

        # Vegetative stage should have 3 applications
        assert len(schedule) == 3

    def test_schedule_split_quantities(self):
        """Test that schedule splits fertilizer quantities"""
        from src.main import generate_schedule, CropType, GrowthStage, FertilizerRecommendation, FertilizerType, ApplicationMethod

        total_quantity = 120.0

        recommendations = [
            FertilizerRecommendation(
                fertilizer_type=FertilizerType.UREA,
                fertilizer_name_ar="يوريا",
                fertilizer_name_en="Urea",
                quantity_kg_per_hectare=total_quantity,
                quantity_kg_per_donum=12.0,
                application_method=ApplicationMethod.SIDE_DRESSING,
                application_method_ar="تسميد جانبي",
                timing_ar="صباحاً",
                timing_en="Morning",
                npk_content={"N": 46, "P": 0, "K": 0},
                cost_estimate_yer=96000.0,
                notes_ar=[],
                notes_en=[]
            )
        ]

        schedule = generate_schedule(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,  # 3 applications
            recommendations=recommendations
        )

        # Sum of split quantities should equal total
        total_applied = sum(
            app["fertilizers"][0]["quantity_kg"]
            for app in schedule
        )

        assert abs(total_applied - total_quantity) < 0.1


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/healthz")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data["service"] == "fertilizer-advisor"
        assert "crops_supported" in data

    def test_list_crops_endpoint(self, test_client):
        """Test list crops endpoint"""
        response = test_client.get("/v1/crops")

        assert response.status_code == 200
        data = response.json()

        assert "crops" in data
        assert len(data["crops"]) > 0

        crop = data["crops"][0]
        assert "id" in crop
        assert "name_ar" in crop
        assert "npk_requirements" in crop

    def test_list_fertilizers_endpoint(self, test_client):
        """Test list fertilizers endpoint"""
        response = test_client.get("/v1/fertilizers")

        assert response.status_code == 200
        data = response.json()

        assert "fertilizers" in data
        assert len(data["fertilizers"]) > 0

        fertilizer = data["fertilizers"][0]
        assert "id" in fertilizer
        assert "name_ar" in fertilizer
        assert "name_en" in fertilizer
        assert "npk_content" in fertilizer
        assert "price_yer_per_kg" in fertilizer

    def test_get_recommendation_endpoint(self, test_client, sample_fertilizer_request):
        """Test get recommendation endpoint"""
        response = test_client.post("/v1/recommend", json=sample_fertilizer_request)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "plan_id" in data
        assert "field_id" in data
        assert "crop" in data
        assert "crop_name_ar" in data
        assert "recommendations" in data
        assert "total_nitrogen_kg" in data
        assert "total_phosphorus_kg" in data
        assert "total_potassium_kg" in data
        assert "total_cost_yer" in data
        assert "schedule" in data

    def test_get_deficiency_symptoms_endpoint(self, test_client):
        """Test get deficiency symptoms endpoint"""
        response = test_client.get("/v1/deficiency-symptoms/tomato")

        assert response.status_code == 200
        data = response.json()

        assert "crop" in data
        assert "deficiency_symptoms" in data

        symptoms = data["deficiency_symptoms"]
        assert "nitrogen" in symptoms
        assert "phosphorus" in symptoms
        assert "potassium" in symptoms


class TestWarningGeneration:
    """Test warning generation for fertilization plans"""

    def test_high_nitrogen_warning(self, test_client):
        """Test warning for excessive nitrogen"""
        request = {
            "field_id": "test_field",
            "crop": "tomato",
            "growth_stage": "vegetative",
            "area_hectares": 1.0,
            "soil_type": "loamy",
            "target_yield_kg_ha": 80000.0,  # Very high target
            "organic_only": False
        }

        response = test_client.post("/v1/recommend", json=request)

        assert response.status_code == 200
        data = response.json()

        # May have nitrogen warning if target is very high
        if data["total_nitrogen_kg"] > 200:
            assert len(data["warnings_ar"]) > 0

    def test_high_salinity_warning(self, test_client, sample_soil_analysis):
        """Test warning for high salinity soil"""
        from src.main import SoilAnalysis

        high_salinity_soil = sample_soil_analysis.copy()
        high_salinity_soil["ec_ds_m"] = 5.0  # High salinity

        request = {
            "field_id": "test_field",
            "crop": "tomato",
            "growth_stage": "vegetative",
            "area_hectares": 5.0,
            "soil_type": "loamy",
            "organic_only": False,
            "soil_analysis": high_salinity_soil
        }

        response = test_client.post("/v1/recommend", json=request)

        assert response.status_code == 200
        data = response.json()

        # Should have salinity warning
        assert any("ملوحة" in w for w in data["warnings_ar"])

    def test_alkaline_soil_warning(self, test_client, sample_soil_analysis):
        """Test warning for alkaline soil"""
        alkaline_soil = sample_soil_analysis.copy()
        alkaline_soil["ph"] = 8.5  # Alkaline

        request = {
            "field_id": "test_field",
            "crop": "tomato",
            "growth_stage": "vegetative",
            "area_hectares": 5.0,
            "soil_type": "loamy",
            "organic_only": False,
            "soil_analysis": alkaline_soil
        }

        response = test_client.post("/v1/recommend", json=request)

        assert response.status_code == 200
        data = response.json()

        # Should have alkaline warning
        assert any("قلوية" in w for w in data["warnings_ar"])


class TestCropSpecificRecommendations:
    """Test crop-specific fertilization recommendations"""

    def test_tomato_high_potassium(self, test_client):
        """Test that tomato gets high potassium recommendation"""
        request = {
            "field_id": "test_field",
            "crop": "tomato",
            "growth_stage": "fruiting",
            "area_hectares": 5.0,
            "soil_type": "loamy",
            "organic_only": False
        }

        response = test_client.post("/v1/recommend", json=request)

        assert response.status_code == 200
        data = response.json()

        # Tomato in fruiting stage should need more K than N or P
        assert data["total_potassium_kg"] > data["total_nitrogen_kg"]

    def test_wheat_nitrogen_focus(self, test_client):
        """Test that wheat gets nitrogen-focused recommendation"""
        request = {
            "field_id": "test_field",
            "crop": "wheat",
            "growth_stage": "vegetative",
            "area_hectares": 10.0,
            "soil_type": "loamy",
            "organic_only": False
        }

        response = test_client.post("/v1/recommend", json=request)

        assert response.status_code == 200
        data = response.json()

        # Wheat in vegetative stage needs significant N
        assert data["total_nitrogen_kg"] > 0

    def test_banana_very_high_potassium(self, test_client):
        """Test that banana gets very high potassium"""
        request = {
            "field_id": "test_field",
            "crop": "banana",
            "growth_stage": "fruiting",
            "area_hectares": 5.0,
            "soil_type": "loamy",
            "organic_only": False
        }

        response = test_client.post("/v1/recommend", json=request)

        assert response.status_code == 200
        data = response.json()

        # Banana needs high K (at least 1.4x nitrogen)
        assert data["total_potassium_kg"] > data["total_nitrogen_kg"] * 1.4


class TestDataValidation:
    """Test input data validation"""

    def test_negative_area_validation(self, test_client):
        """Test validation of negative area"""
        invalid_request = {
            "field_id": "test_field",
            "crop": "tomato",
            "growth_stage": "vegetative",
            "area_hectares": -5.0,  # Invalid
            "soil_type": "loamy"
        }

        response = test_client.post("/v1/recommend", json=invalid_request)

        assert response.status_code == 422  # Validation error

    def test_invalid_crop_type(self, test_client):
        """Test validation of invalid crop type"""
        invalid_request = {
            "field_id": "test_field",
            "crop": "invalid_crop",
            "growth_stage": "vegetative",
            "area_hectares": 5.0,
            "soil_type": "loamy"
        }

        response = test_client.post("/v1/recommend", json=invalid_request)

        assert response.status_code == 422

    def test_invalid_ph_range(self, test_client):
        """Test validation of pH out of range"""
        invalid_soil = {
            "field_id": "test_field",
            "analysis_date": datetime.now().isoformat(),
            "ph": 15.0,  # Invalid
            "nitrogen_ppm": 30.0,
            "phosphorus_ppm": 20.0,
            "potassium_ppm": 150.0,
            "organic_matter_percent": 2.5,
            "ec_ds_m": 1.2,
            "soil_type": "loamy"
        }

        response = test_client.post("/v1/soil-analysis/interpret", json=invalid_soil)

        assert response.status_code == 422


class TestNPKContentAccuracy:
    """Test NPK content accuracy in fertilizers"""

    def test_fertilizer_npk_content_definitions(self):
        """Test that fertilizer NPK content is correctly defined"""
        from src.main import FERTILIZER_NPK, FertilizerType

        # Urea should be 46-0-0
        assert FERTILIZER_NPK[FertilizerType.UREA] == {"N": 46, "P": 0, "K": 0}

        # DAP should be 18-46-0
        assert FERTILIZER_NPK[FertilizerType.DAP] == {"N": 18, "P": 46, "K": 0}

        # NPK 15-15-15 should be balanced
        assert FERTILIZER_NPK[FertilizerType.NPK_15_15_15] == {"N": 15, "P": 15, "K": 15}

        # Potassium sulfate should be 0-0-50
        assert FERTILIZER_NPK[FertilizerType.POTASSIUM_SULFATE] == {"N": 0, "P": 0, "K": 50}

    def test_npk_totals_calculation(self, test_client, sample_fertilizer_request):
        """Test that NPK totals are calculated correctly"""
        response = test_client.post("/v1/recommend", json=sample_fertilizer_request)

        assert response.status_code == 200
        data = response.json()

        # Manually calculate totals
        calculated_n = sum(
            rec["quantity_kg_per_hectare"] * rec["npk_content"]["N"] / 100
            for rec in data["recommendations"]
        )
        calculated_p = sum(
            rec["quantity_kg_per_hectare"] * rec["npk_content"]["P"] / 100
            for rec in data["recommendations"]
        )
        calculated_k = sum(
            rec["quantity_kg_per_hectare"] * rec["npk_content"]["K"] / 100
            for rec in data["recommendations"]
        )

        # Should match returned totals (within rounding)
        assert abs(data["total_nitrogen_kg"] - calculated_n) < 1.0
        assert abs(data["total_phosphorus_kg"] - calculated_p) < 1.0
        assert abs(data["total_potassium_kg"] - calculated_k) < 1.0


class TestCostCalculations:
    """Test cost calculations"""

    def test_total_cost_calculation(self, test_client, sample_fertilizer_request):
        """Test that total cost is sum of individual costs"""
        response = test_client.post("/v1/recommend", json=sample_fertilizer_request)

        assert response.status_code == 200
        data = response.json()

        # Calculate total from recommendations
        calculated_total = sum(rec["cost_estimate_yer"] for rec in data["recommendations"])

        # Should match
        assert abs(data["total_cost_yer"] - calculated_total) < 10.0

    def test_cost_per_hectare_scaling(self, test_client):
        """Test that cost scales with area"""
        request_small = {
            "field_id": "test_field",
            "crop": "tomato",
            "growth_stage": "vegetative",
            "area_hectares": 5.0,
            "soil_type": "loamy",
            "organic_only": False
        }

        request_large = {
            "field_id": "test_field",
            "crop": "tomato",
            "growth_stage": "vegetative",
            "area_hectares": 10.0,
            "soil_type": "loamy",
            "organic_only": False
        }

        resp_small = test_client.post("/v1/recommend", json=request_small)
        resp_large = test_client.post("/v1/recommend", json=request_large)

        # Cost per hectare should be similar
        cost_per_ha_small = resp_small.json()["total_cost_yer"] / 5.0
        cost_per_ha_large = resp_large.json()["total_cost_yer"] / 10.0

        # Should be within 30% (may vary due to fertilizer packaging and bulk pricing)
        ratio = cost_per_ha_large / cost_per_ha_small
        assert 0.7 < ratio < 1.3
