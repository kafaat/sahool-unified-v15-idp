"""
Comprehensive Tests for Crop Analysis - Crop Intelligence Service
اختبارات شاملة لتحليل المحاصيل - خدمة ذكاء المحاصيل

This module tests:
- Vegetation indices analysis
- Zone health assessment
- Multi-temporal analysis
- Data validation
- API endpoints for crop analysis
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient


class TestVegetationIndicesAnalysis:
    """Test vegetation indices calculation and analysis"""

    def test_ndvi_healthy_crop(self):
        """Test NDVI analysis for healthy crop"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Healthy crop indices
        indices = Indices(
            ndvi=0.85,  # Excellent vegetation
            evi=0.75,
            ndre=0.35,
            lci=0.40,
            ndwi=0.10,
            savi=0.80
        )

        obs = ZoneObservation(
            zone_id="zone_healthy",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Healthy crop should have no urgent actions
        urgent_actions = [a for a in actions if a["priority"] in ["P0", "P1"]]
        assert len(urgent_actions) == 0

        # Should have a "no action" or low priority action
        assert any(a["type"] == "none" for a in actions)

    def test_ndvi_stressed_crop(self):
        """Test NDVI analysis for stressed crop"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Stressed crop indices
        indices = Indices(
            ndvi=0.32,  # Very low vegetation
            evi=0.25,
            ndre=0.15,
            lci=0.10,
            ndwi=-0.15,
            savi=0.28
        )

        obs = ZoneObservation(
            zone_id="zone_stressed",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Stressed crop should have multiple actions
        assert len(actions) >= 2

        # Should have urgent actions
        urgent_actions = [a for a in actions if a["priority"] in ["P0", "P1", "P2"]]
        assert len(urgent_actions) > 0

    def test_ndvi_boundary_values(self):
        """Test NDVI at boundary values"""
        from src.decision_engine import _clamp01

        # Test clamping function
        assert _clamp01(-0.5) == 0.0
        assert _clamp01(0.0) == 0.0
        assert _clamp01(0.5) == 0.5
        assert _clamp01(1.0) == 1.0
        assert _clamp01(1.5) == 1.0

    def test_evi_analysis(self):
        """Test Enhanced Vegetation Index analysis"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Test with high EVI
        high_evi_indices = Indices(
            ndvi=0.80,
            evi=0.85,  # Very high EVI
            ndre=0.30,
            lci=0.35,
            ndwi=0.05,
            savi=0.75
        )

        obs = ZoneObservation(
            zone_id="zone_high_evi",
            growth_stage=GrowthStage.mid,
            indices=high_evi_indices
        )

        actions = diagnose_zone(obs)

        # High EVI indicates healthy vegetation
        critical_actions = [a for a in actions if a["priority"] == "P0"]
        assert len(critical_actions) == 0

    def test_ndre_nitrogen_stress(self):
        """Test NDRE for nitrogen deficiency detection"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Good NDVI but low NDRE (hidden hunger)
        indices = Indices(
            ndvi=0.70,  # Decent vegetation
            evi=0.60,
            ndre=0.20,  # Low nitrogen indicator
            lci=0.18,
            ndwi=0.00,
            savi=0.65
        )

        obs = ZoneObservation(
            zone_id="zone_nitrogen_deficient",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should recommend fertilization
        fert_actions = [a for a in actions if a["type"] == "fertilization"]
        assert len(fert_actions) > 0

        # Check for nitrogen-related recommendation
        assert any("nitrogen" in a["reason"].lower() or "نيتروجين" in a["reason"]
                   for a in fert_actions)

    def test_ndwi_water_stress_detection(self):
        """Test NDWI for water stress detection"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Low NDWI indicating water stress
        indices = Indices(
            ndvi=0.50,
            evi=0.45,
            ndre=0.25,
            lci=0.22,
            ndwi=-0.18,  # Severe water stress
            savi=0.45
        )

        obs = ZoneObservation(
            zone_id="zone_water_stressed",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should recommend irrigation
        irrig_actions = [a for a in actions if a["type"] == "irrigation"]
        assert len(irrig_actions) > 0

        # Should be high priority
        urgent_irrig = [a for a in irrig_actions if a["priority"] in ["P0", "P1"]]
        assert len(urgent_irrig) > 0

    def test_savi_seedling_stage(self):
        """Test SAVI for seedling stage analysis"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Low SAVI in seedling stage
        indices = Indices(
            ndvi=0.25,
            evi=0.20,
            ndre=0.15,
            lci=0.12,
            ndwi=-0.05,
            savi=0.18  # Very low for seedlings
        )

        obs = ZoneObservation(
            zone_id="zone_seedling",
            growth_stage=GrowthStage.seedling,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should recommend scouting
        scout_actions = [a for a in actions if a["type"] == "scouting"]
        assert len(scout_actions) > 0


class TestZoneHealthAssessment:
    """Test zone health status classification"""

    def test_classify_critical_status(self):
        """Test classification of critical zone status"""
        from src.decision_engine import classify_zone_status

        critical_actions = [
            {"priority": "P0", "type": "irrigation"},
            {"priority": "P1", "type": "scouting"}
        ]

        status = classify_zone_status(critical_actions)
        assert status == "critical"

    def test_classify_warning_status(self):
        """Test classification of warning zone status"""
        from src.decision_engine import classify_zone_status

        warning_actions = [
            {"priority": "P1", "type": "fertilization"},
            {"priority": "P2", "type": "scouting"}
        ]

        status = classify_zone_status(warning_actions)
        assert status == "warning"

    def test_classify_attention_status(self):
        """Test classification of attention zone status"""
        from src.decision_engine import classify_zone_status

        attention_actions = [
            {"priority": "P2", "type": "scouting"}
        ]

        status = classify_zone_status(attention_actions)
        assert status == "attention"

    def test_classify_ok_status(self):
        """Test classification of OK zone status"""
        from src.decision_engine import classify_zone_status

        ok_actions = [
            {"priority": "P3", "type": "none"}
        ]

        status = classify_zone_status(ok_actions)
        assert status == "ok"

    def test_empty_actions_list(self):
        """Test classification with empty actions list"""
        from src.decision_engine import classify_zone_status

        status = classify_zone_status([])
        assert status == "ok"


class TestHealthStatusDetermination:
    """Test health status determination from NDVI"""

    def test_excellent_health_status(self):
        """Test excellent health status (NDVI >= 0.7)"""
        from src.decision_engine import _get_health_status

        status_en, status_ar = _get_health_status(0.85)
        assert status_en == "excellent"
        assert status_ar == "ممتاز"

    def test_good_health_status(self):
        """Test good health status (0.5 <= NDVI < 0.7)"""
        from src.decision_engine import _get_health_status

        status_en, status_ar = _get_health_status(0.60)
        assert status_en == "good"
        assert status_ar == "جيد"

    def test_moderate_health_status(self):
        """Test moderate health status (0.35 <= NDVI < 0.5)"""
        from src.decision_engine import _get_health_status

        status_en, status_ar = _get_health_status(0.42)
        assert status_en == "moderate"
        assert status_ar == "متوسط"

    def test_poor_health_status(self):
        """Test poor health status (0.2 <= NDVI < 0.35)"""
        from src.decision_engine import _get_health_status

        status_en, status_ar = _get_health_status(0.28)
        assert status_en == "poor"
        assert status_ar == "ضعيف"

    def test_critical_health_status(self):
        """Test critical health status (NDVI < 0.2)"""
        from src.decision_engine import _get_health_status

        status_en, status_ar = _get_health_status(0.15)
        assert status_en == "critical"
        assert status_ar == "حرج"


class TestFertilizerDoseCalculation:
    """Test fertilizer dose hint calculation"""

    def test_high_dose_hint(self):
        """Test high dose recommendation for low NDRE"""
        from src.decision_engine import _dose_hint_from_ndre

        dose = _dose_hint_from_ndre(0.15)
        assert dose == "high"

    def test_medium_dose_hint(self):
        """Test medium dose recommendation for moderate NDRE"""
        from src.decision_engine import _dose_hint_from_ndre

        dose = _dose_hint_from_ndre(0.22)
        assert dose == "medium"

    def test_low_dose_hint(self):
        """Test low dose recommendation for high NDRE"""
        from src.decision_engine import _dose_hint_from_ndre

        dose = _dose_hint_from_ndre(0.30)
        assert dose == "low"


class TestGrowthStageAnalysis:
    """Test analysis across different growth stages"""

    def test_seedling_stage_analysis(self):
        """Test analysis during seedling stage"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        indices = Indices(
            ndvi=0.35,
            evi=0.28,
            ndre=0.20,
            lci=0.18,
            ndwi=0.00,
            savi=0.18  # Low SAVI triggers seedling-specific checks
        )

        obs = ZoneObservation(
            zone_id="zone_seedling",
            growth_stage=GrowthStage.seedling,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should have seedling-specific recommendations
        assert len(actions) > 0

    def test_rapid_growth_stage_analysis(self):
        """Test analysis during rapid growth stage"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        indices = Indices(
            ndvi=0.70,
            evi=0.65,
            ndre=0.30,
            lci=0.32,
            ndwi=0.05,
            savi=0.68
        )

        obs = ZoneObservation(
            zone_id="zone_rapid",
            growth_stage=GrowthStage.rapid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Healthy rapid growth should have minimal actions
        urgent = [a for a in actions if a["priority"] in ["P0", "P1"]]
        assert len(urgent) == 0

    def test_mid_season_analysis(self):
        """Test analysis during mid-season"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Mid-season with low NDRE should trigger fertilization
        indices = Indices(
            ndvi=0.68,
            evi=0.58,
            ndre=0.22,  # Low NDRE
            lci=0.25,
            ndwi=0.02,
            savi=0.62
        )

        obs = ZoneObservation(
            zone_id="zone_mid",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should recommend fertilization
        fert_actions = [a for a in actions if a["type"] == "fertilization"]
        assert len(fert_actions) > 0

    def test_late_season_analysis(self):
        """Test analysis during late season"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Late season with low NDRE
        indices = Indices(
            ndvi=0.70,
            evi=0.62,
            ndre=0.24,
            lci=0.28,
            ndwi=0.00,
            savi=0.65
        )

        obs = ZoneObservation(
            zone_id="zone_late",
            growth_stage=GrowthStage.late,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Late season should also get fertilization recommendation
        fert_actions = [a for a in actions if a["type"] == "fertilization"]
        assert len(fert_actions) > 0


class TestAPIEndpointsForAnalysis:
    """Test API endpoints for crop analysis"""

    def test_quick_diagnose_endpoint(self, client):
        """Test quick diagnosis endpoint with various conditions"""
        observation_data = {
            "captured_at": "2025-12-27T10:00:00Z",
            "source": "drone",
            "growth_stage": "mid",
            "indices": {
                "ndvi": 0.75,
                "evi": 0.65,
                "ndre": 0.28,
                "lci": 0.30,
                "ndwi": 0.00,
                "savi": 0.68
            }
        }

        response = client.post(
            "/api/v1/diagnose",
            json=observation_data,
            params={"zone_id": "test_zone"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "zone_id" in data
        assert data["zone_id"] == "test_zone"
        assert "status" in data
        assert "actions" in data
        assert "indices_received" in data

        # Verify indices received matches input
        assert data["indices_received"]["ndvi"] == 0.75

    def test_field_diagnosis_with_multiple_zones(self, client):
        """Test field diagnosis aggregating multiple zones"""
        response = client.get(
            "/api/v1/fields/field_demo/diagnosis",
            params={"date": "2025-12-14"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "summary" in data
        summary = data["summary"]

        # Check summary aggregation
        assert summary["zones_total"] >= 0
        assert summary["zones_critical"] >= 0
        assert summary["zones_warning"] >= 0
        assert summary["zones_ok"] >= 0

        # Total should equal sum of categories
        total = summary["zones_critical"] + summary["zones_warning"] + summary["zones_ok"]
        assert total == summary["zones_total"]

    def test_zone_timeline_analysis(self, client):
        """Test zone timeline for temporal analysis"""
        response = client.get(
            "/api/v1/fields/field_demo/zones/zone_a/timeline",
            params={"from": "2025-12-01", "to": "2025-12-31"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "series" in data

        # Verify time series structure
        if len(data["series"]) > 0:
            point = data["series"][0]
            assert "date" in point
            assert "ndvi" in point


class TestDataValidation:
    """Test data validation for crop analysis inputs"""

    def test_invalid_ndvi_range(self, client):
        """Test validation of NDVI out of valid range"""
        invalid_data = {
            "captured_at": "2025-12-27T10:00:00Z",
            "source": "sentinel-2",
            "growth_stage": "mid",
            "indices": {
                "ndvi": 1.5,  # Invalid: > 1
                "evi": 0.60,
                "ndre": 0.25,
                "lci": 0.30,
                "ndwi": -0.05,
                "savi": 0.65
            }
        }

        response = client.post(
            "/api/v1/fields/test_field/zones/test_zone/observations",
            json=invalid_data
        )

        assert response.status_code == 422  # Validation error

    def test_invalid_growth_stage(self, client):
        """Test validation of invalid growth stage"""
        invalid_data = {
            "captured_at": "2025-12-27T10:00:00Z",
            "source": "sentinel-2",
            "growth_stage": "invalid_stage",
            "indices": {
                "ndvi": 0.75,
                "evi": 0.60,
                "ndre": 0.25,
                "lci": 0.30,
                "ndwi": -0.05,
                "savi": 0.65
            }
        }

        response = client.post(
            "/api/v1/fields/test_field/zones/test_zone/observations",
            json=invalid_data
        )

        assert response.status_code == 422

    def test_missing_required_indices(self, client):
        """Test validation when required indices are missing"""
        invalid_data = {
            "captured_at": "2025-12-27T10:00:00Z",
            "source": "sentinel-2",
            "growth_stage": "mid",
            "indices": {
                "ndvi": 0.75,
                "evi": 0.60,
                # Missing ndre, lci, ndwi, savi
            }
        }

        response = client.post(
            "/api/v1/fields/test_field/zones/test_zone/observations",
            json=invalid_data
        )

        assert response.status_code == 422

    def test_invalid_date_format(self, client):
        """Test validation of invalid date format"""
        response = client.get(
            "/api/v1/fields/field_demo/diagnosis",
            params={"date": "not-a-date"}
        )

        assert response.status_code == 400


class TestMultiTemporalAnalysis:
    """Test multi-temporal analysis capabilities"""

    def test_temporal_trend_detection(self, client, sample_observation_data):
        """Test detection of temporal trends in vegetation indices"""
        field_id = "temporal_test_field"
        zone_id = "temporal_test_zone"

        # Create multiple observations over time
        dates = [
            "2025-12-01T10:00:00Z",
            "2025-12-08T10:00:00Z",
            "2025-12-15T10:00:00Z",
            "2025-12-22T10:00:00Z"
        ]

        ndvi_values = [0.45, 0.55, 0.65, 0.75]  # Improving trend

        for date, ndvi in zip(dates, ndvi_values):
            obs_data = sample_observation_data.copy()
            obs_data["captured_at"] = date
            obs_data["indices"]["ndvi"] = ndvi

            client.post(
                f"/api/v1/fields/{field_id}/zones/{zone_id}/observations",
                json=obs_data
            )

        # Get timeline
        response = client.get(
            f"/api/v1/fields/{field_id}/zones/{zone_id}/timeline",
            params={"from": "2025-12-01", "to": "2025-12-31"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify trend
        series = data["series"]
        assert len(series) == 4

        # Verify NDVI values are in correct order
        ndvi_series = [point["ndvi"] for point in series]
        assert ndvi_series == sorted(ndvi_series)  # Should be increasing

    def test_observation_filtering_by_date_range(self, client, sample_observation_data):
        """Test filtering observations by date range"""
        field_id = "filter_test_field"
        zone_id = "filter_test_zone"

        # Create observations across different dates
        dates = [
            "2025-11-15T10:00:00Z",  # Outside range
            "2025-12-05T10:00:00Z",  # Inside range
            "2025-12-15T10:00:00Z",  # Inside range
            "2026-01-05T10:00:00Z",  # Outside range
        ]

        for date in dates:
            obs_data = sample_observation_data.copy()
            obs_data["captured_at"] = date

            client.post(
                f"/api/v1/fields/{field_id}/zones/{zone_id}/observations",
                json=obs_data
            )

        # Get timeline for December only
        response = client.get(
            f"/api/v1/fields/{field_id}/zones/{zone_id}/timeline",
            params={"from": "2025-12-01", "to": "2025-12-31"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should only have 2 observations from December
        assert len(data["series"]) == 2


class TestVRTGeneration:
    """Test Variable Rate Technology (VRT) data generation"""

    def test_vrt_properties_generation(self):
        """Test VRT properties generation for zone"""
        from src.decision_engine import generate_vrt_properties

        zone_id = "vrt_test_zone"
        actions = [
            {
                "type": "irrigation",
                "priority": "P0",
                "recommended_dose_hint": None
            },
            {
                "type": "fertilization",
                "priority": "P1",
                "recommended_dose_hint": "medium"
            }
        ]

        vrt_props = generate_vrt_properties(zone_id, actions)

        assert vrt_props["zone_id"] == zone_id
        assert vrt_props["status"] == "critical"  # P0 action present
        assert vrt_props["irrigation_required"] is True
        assert vrt_props["irrigation_priority"] == "P0"
        assert vrt_props["fertilization_required"] is True
        assert vrt_props["n_dose_hint"] == "medium"

    def test_vrt_export_endpoint(self, client):
        """Test VRT export endpoint"""
        response = client.get(
            "/api/v1/fields/field_demo/vrt",
            params={"date": "2025-12-14"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert "metadata" in data

        # Verify metadata
        metadata = data["metadata"]
        assert metadata["export_type"] == "vrt"
        assert "field_id" in metadata
        assert "generated_at" in metadata

        # Verify features have VRT properties
        if len(data["features"]) > 0:
            feature = data["features"][0]
            props = feature["properties"]
            assert "status" in props
            assert "irrigation_required" in props
            assert "fertilization_required" in props


class TestPerformanceAndScalability:
    """Test performance with large datasets"""

    @pytest.mark.slow
    def test_multiple_zones_analysis_performance(self, client, sample_observation_data):
        """Test performance with multiple zones"""
        field_id = "perf_test_field"
        num_zones = 20

        # Create multiple zones with observations
        for i in range(num_zones):
            zone_id = f"zone_{i}"
            client.post(
                f"/api/v1/fields/{field_id}/zones/{zone_id}/observations",
                json=sample_observation_data
            )

        # Time the diagnosis
        import time
        start = time.time()

        response = client.get(
            f"/api/v1/fields/{field_id}/diagnosis",
            params={"date": "2025-12-27"}
        )

        duration = time.time() - start

        assert response.status_code == 200

        # Should complete in reasonable time (< 2 seconds for 20 zones)
        assert duration < 2.0

        data = response.json()
        assert data["summary"]["zones_total"] == num_zones
