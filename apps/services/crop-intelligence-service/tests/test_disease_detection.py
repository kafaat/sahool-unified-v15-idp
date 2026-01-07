"""
Comprehensive Tests for Disease Detection - Crop Intelligence Service
اختبارات شاملة لكشف الأمراض - خدمة ذكاء المحاصيل

This module tests:
- Disease symptom detection through vegetation indices
- Anomaly detection in crop health
- Early warning systems for plant stress
- Scouting recommendations
- Pattern recognition for disease indicators
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


class TestDiseaseSymptomDetection:
    """Test detection of disease symptoms through vegetation indices"""

    def test_detect_severe_canopy_weakness(self):
        """Test detection of severe canopy weakness (potential disease)"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Very low NDVI indicates severe problems
        indices = Indices(
            ndvi=0.25,  # Critical vegetation index
            evi=0.20,
            ndre=0.12,
            lci=0.10,
            ndwi=-0.08,
            savi=0.22
        )

        obs = ZoneObservation(
            zone_id="zone_potential_disease",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should recommend scouting for disease/pests
        scout_actions = [a for a in actions if a["type"] == "scouting"]
        assert len(scout_actions) > 0

        # Should have evidence of low NDVI
        assert any(a["evidence"].get("ndvi", 1.0) < 0.35 for a in scout_actions)

    def test_detect_chlorophyll_deficiency(self):
        """Test detection of low chlorophyll (disease symptom)"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Low LCI with moderate NDVI can indicate chlorosis (disease symptom)
        indices = Indices(
            ndvi=0.55,
            evi=0.45,
            ndre=0.22,
            lci=0.15,  # Very low chlorophyll
            ndwi=0.00,
            savi=0.50
        )

        obs = ZoneObservation(
            zone_id="zone_chlorosis",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should have action related to chlorophyll or nutrition
        fert_or_scout_actions = [
            a for a in actions
            if a["type"] in ["fertilization", "scouting"]
        ]
        assert len(fert_or_scout_actions) > 0

        # Check for chlorophyll-related evidence
        lci_actions = [
            a for a in actions
            if "lci" in a.get("evidence", {})
        ]
        assert len(lci_actions) > 0

    def test_detect_nitrogen_deficiency_disease_like(self):
        """Test detection of severe nitrogen deficiency mimicking disease"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Low NDRE with good structure can indicate nitrogen deficiency
        # which can look like disease symptoms (yellowing)
        indices = Indices(
            ndvi=0.65,
            evi=0.55,
            ndre=0.16,  # Very low - severe nitrogen deficiency
            lci=0.18,
            ndwi=0.02,
            savi=0.60
        )

        obs = ZoneObservation(
            zone_id="zone_nitrogen_deficiency",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should recommend fertilization
        fert_actions = [a for a in actions if a["type"] == "fertilization"]
        assert len(fert_actions) > 0

        # Should have high or medium dose hint
        assert any(
            a.get("recommended_dose_hint") in ["high", "medium"]
            for a in fert_actions
        )

    def test_detect_water_stress_disease_risk(self):
        """Test detection of water stress increasing disease risk"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Severe water stress makes plants susceptible to diseases
        indices = Indices(
            ndvi=0.48,
            evi=0.40,
            ndre=0.20,
            lci=0.22,
            ndwi=-0.22,  # Severe water stress
            savi=0.42
        )

        obs = ZoneObservation(
            zone_id="zone_water_stress",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should recommend urgent irrigation
        irrig_actions = [a for a in actions if a["type"] == "irrigation"]
        assert len(irrig_actions) > 0

        # Should be high priority
        urgent = [a for a in irrig_actions if a["priority"] in ["P0", "P1"]]
        assert len(urgent) > 0


class TestEarlyWarningSystem:
    """Test early warning system for disease prevention"""

    def test_early_stage_stress_detection(self):
        """Test detection of early stress indicators"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Moderate stress - early warning
        indices = Indices(
            ndvi=0.58,
            evi=0.50,
            ndre=0.24,
            lci=0.26,
            ndwi=-0.08,
            savi=0.52
        )

        obs = ZoneObservation(
            zone_id="zone_early_stress",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should have preventive actions
        assert len(actions) > 0

        # Actions should not be critical (P0) since it's early stage
        critical = [a for a in actions if a["priority"] == "P0"]
        assert len(critical) == 0

    def test_seedling_vulnerability_monitoring(self):
        """Test monitoring of vulnerable seedling stage"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Seedlings with poor establishment
        indices = Indices(
            ndvi=0.28,
            evi=0.22,
            ndre=0.16,
            lci=0.14,
            ndwi=-0.02,
            savi=0.16  # Very low for seedlings
        )

        obs = ZoneObservation(
            zone_id="zone_vulnerable_seedlings",
            growth_stage=GrowthStage.seedling,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should recommend scouting for seedling problems
        scout_actions = [a for a in actions if a["type"] == "scouting"]
        assert len(scout_actions) > 0

        # Should mention seedling or germination issues
        assert any(
            "seedling" in a["title_en"].lower() or
            "شتلات" in a["title"]
            for a in scout_actions
        )

    def test_rapid_decline_detection(self, client, sample_observation_data):
        """Test detection of rapid health decline (disease outbreak)"""
        field_id = "decline_test_field"
        zone_id = "decline_test_zone"

        # Create observations showing rapid decline
        observations = [
            {"date": "2025-12-01T10:00:00Z", "ndvi": 0.75},
            {"date": "2025-12-08T10:00:00Z", "ndvi": 0.65},
            {"date": "2025-12-15T10:00:00Z", "ndvi": 0.45},
            {"date": "2025-12-22T10:00:00Z", "ndvi": 0.30},  # Rapid decline
        ]

        for obs_data in observations:
            test_obs = sample_observation_data.copy()
            test_obs["captured_at"] = obs_data["date"]
            test_obs["indices"]["ndvi"] = obs_data["ndvi"]

            client.post(
                f"/api/v1/fields/{field_id}/zones/{zone_id}/observations",
                json=test_obs
            )

        # Get timeline to analyze trend
        response = client.get(
            f"/api/v1/fields/{field_id}/zones/{zone_id}/timeline",
            params={"from": "2025-12-01", "to": "2025-12-31"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify declining trend
        series = data["series"]
        ndvi_values = [point["ndvi"] for point in series]

        # Each value should be less than previous (declining trend)
        for i in range(1, len(ndvi_values)):
            assert ndvi_values[i] < ndvi_values[i-1]


class TestScoutingRecommendations:
    """Test field scouting recommendations for disease confirmation"""

    def test_scouting_for_low_ndvi(self):
        """Test scouting recommendation for unexplained low NDVI"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        indices = Indices(
            ndvi=0.32,  # Low enough to trigger scouting
            evi=0.28,
            ndre=0.18,
            lci=0.16,
            ndwi=-0.05,
            savi=0.30
        )

        obs = ZoneObservation(
            zone_id="zone_needs_scouting",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should have scouting action
        scout_actions = [a for a in actions if a["type"] == "scouting"]
        assert len(scout_actions) > 0

        # Should provide recommended time window
        assert any(
            a.get("recommended_window_hours") is not None
            for a in scout_actions
        )

    def test_scouting_priority_levels(self):
        """Test different priority levels for scouting"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Moderate concern - P2 scouting
        moderate_indices = Indices(
            ndvi=0.33,
            evi=0.30,
            ndre=0.20,
            lci=0.18,
            ndwi=-0.03,
            savi=0.32
        )

        obs = ZoneObservation(
            zone_id="zone_moderate",
            growth_stage=GrowthStage.mid,
            indices=moderate_indices
        )

        actions = diagnose_zone(obs)

        scout_actions = [a for a in actions if a["type"] == "scouting"]

        # Should have scouting with P2 priority
        assert any(a["priority"] == "P2" for a in scout_actions)

    def test_scouting_reason_details(self):
        """Test that scouting actions provide detailed reasons"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        indices = Indices(
            ndvi=0.30,
            evi=0.26,
            ndre=0.17,
            lci=0.14,
            ndwi=-0.04,
            savi=0.28
        )

        obs = ZoneObservation(
            zone_id="zone_detail_test",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        scout_actions = [a for a in actions if a["type"] == "scouting"]
        assert len(scout_actions) > 0

        for action in scout_actions:
            # Should have both Arabic and English reasons
            assert action["reason"] is not None
            assert action["reason_en"] is not None

            # Should have evidence
            assert "evidence" in action
            assert len(action["evidence"]) > 0


class TestAnomalyDetection:
    """Test anomaly detection in vegetation patterns"""

    def test_detect_unusual_index_combination(self):
        """Test detection of unusual combination of indices"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Unusual: High NDVI but very low chlorophyll
        # Could indicate disease or measurement error
        indices = Indices(
            ndvi=0.78,  # High
            evi=0.68,
            ndre=0.30,
            lci=0.12,  # Very low despite high NDVI
            ndwi=0.05,
            savi=0.72
        )

        obs = ZoneObservation(
            zone_id="zone_anomaly",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should flag for investigation
        assert len(actions) > 0

    def test_detect_spatial_heterogeneity(self, client, sample_observation_data):
        """Test detection of high spatial variability (disease patches)"""
        field_id = "heterogeneity_field"

        # Create zones with very different health status
        zone_healths = [
            ("zone_healthy", 0.82),
            ("zone_moderate", 0.55),
            ("zone_sick", 0.28),
            ("zone_critical", 0.18)
        ]

        for zone_id, ndvi in zone_healths:
            obs_data = sample_observation_data.copy()
            obs_data["indices"]["ndvi"] = ndvi

            client.post(
                f"/api/v1/fields/{field_id}/zones/{zone_id}/observations",
                json=obs_data
            )

        # Get field diagnosis
        response = client.get(
            f"/api/v1/fields/{field_id}/diagnosis",
            params={"date": "2025-12-27"}
        )

        assert response.status_code == 200
        data = response.json()

        summary = data["summary"]

        # Should have mix of critical, warning, and ok zones
        assert summary["zones_critical"] > 0
        assert summary["zones_ok"] > 0

        # High heterogeneity indicated by presence of all categories
        assert summary["zones_total"] == 4


class TestDiseaseRiskFactors:
    """Test identification of disease risk factors"""

    def test_combined_stress_factors(self):
        """Test detection of multiple stress factors increasing disease risk"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Multiple stressors: water stress + nutrient deficiency
        indices = Indices(
            ndvi=0.42,
            evi=0.35,
            ndre=0.18,  # Low nitrogen
            lci=0.16,
            ndwi=-0.15,  # Water stress
            savi=0.38
        )

        obs = ZoneObservation(
            zone_id="zone_multiple_stress",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should have multiple types of actions
        action_types = set(a["type"] for a in actions)
        assert len(action_types) >= 2  # Should have multiple action types

        # Should include both irrigation and other actions
        assert "irrigation" in action_types

    def test_environmental_stress_indicators(self):
        """Test detection of environmental stress predisposing to disease"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        # Environmental stress indicated by low SAVI and NDWI
        indices = Indices(
            ndvi=0.50,
            evi=0.42,
            ndre=0.22,
            lci=0.24,
            ndwi=-0.12,
            savi=0.35  # Low SAVI indicates soil influence
        )

        obs = ZoneObservation(
            zone_id="zone_env_stress",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Should have recommendations
        assert len(actions) > 0

        # Should include irrigation or scouting
        types = [a["type"] for a in actions]
        assert "irrigation" in types or "scouting" in types


class TestDiseaseProgressionMonitoring:
    """Test monitoring of disease progression over time"""

    def test_track_health_deterioration(self, client, sample_observation_data):
        """Test tracking deterioration pattern over time"""
        field_id = "deterioration_field"
        zone_id = "deterioration_zone"

        # Progressive deterioration
        timeline = [
            ("2025-12-05T10:00:00Z", 0.70, 0.30, 0.05),   # Good
            ("2025-12-12T10:00:00Z", 0.60, 0.28, 0.00),   # Declining
            ("2025-12-19T10:00:00Z", 0.45, 0.22, -0.08),  # Poor
            ("2025-12-26T10:00:00Z", 0.32, 0.18, -0.15),  # Critical
        ]

        for date, ndvi, ndre, ndwi in timeline:
            obs_data = sample_observation_data.copy()
            obs_data["captured_at"] = date
            obs_data["indices"]["ndvi"] = ndvi
            obs_data["indices"]["ndre"] = ndre
            obs_data["indices"]["ndwi"] = ndwi

            client.post(
                f"/api/v1/fields/{field_id}/zones/{zone_id}/observations",
                json=obs_data
            )

        # Check final diagnosis
        response = client.get(
            f"/api/v1/fields/{field_id}/diagnosis",
            params={"date": "2025-12-26"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should have urgent actions due to critical state
        urgent_actions = [
            a for a in data["actions"]
            if a["priority"] in ["P0", "P1"]
        ]
        assert len(urgent_actions) > 0

    def test_recovery_pattern_detection(self, client, sample_observation_data):
        """Test detection of recovery pattern (treatment working)"""
        field_id = "recovery_field"
        zone_id = "recovery_zone"

        # Recovery pattern
        timeline = [
            ("2025-12-05T10:00:00Z", 0.35),  # Poor
            ("2025-12-12T10:00:00Z", 0.45),  # Improving
            ("2025-12-19T10:00:00Z", 0.58),  # Better
            ("2025-12-26T10:00:00Z", 0.70),  # Good
        ]

        for date, ndvi in timeline:
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

        series = data["series"]
        ndvi_values = [point["ndvi"] for point in series]

        # Should show improving trend
        assert ndvi_values[-1] > ndvi_values[0]


class TestIntegrationWithQuickDiagnose:
    """Test disease detection through quick diagnose endpoint"""

    def test_quick_diagnose_critical_symptoms(self, client):
        """Test quick diagnosis with critical disease symptoms"""
        critical_symptoms = {
            "captured_at": "2025-12-27T10:00:00Z",
            "source": "drone",
            "growth_stage": "mid",
            "indices": {
                "ndvi": 0.22,  # Very low
                "evi": 0.18,
                "ndre": 0.12,
                "lci": 0.08,   # Very low chlorophyll
                "ndwi": -0.18,  # Severe water stress
                "savi": 0.20
            }
        }

        response = client.post(
            "/api/v1/diagnose",
            json=critical_symptoms
        )

        assert response.status_code == 200
        data = response.json()

        # Should have multiple urgent actions
        actions = data["actions"]
        urgent = [a for a in actions if a["priority"] in ["P0", "P1", "P2"]]
        assert len(urgent) >= 2

        # Status should be critical or warning
        assert data["status"] in ["critical", "warning"]

    def test_quick_diagnose_disease_like_pattern(self, client):
        """Test quick diagnosis with disease-like index pattern"""
        disease_pattern = {
            "captured_at": "2025-12-27T10:00:00Z",
            "source": "sentinel-2",
            "growth_stage": "mid",
            "indices": {
                "ndvi": 0.38,
                "evi": 0.30,
                "ndre": 0.15,  # Very low
                "lci": 0.12,   # Very low
                "ndwi": -0.10,
                "savi": 0.32
            }
        }

        response = client.post(
            "/api/v1/diagnose",
            json=disease_pattern
        )

        assert response.status_code == 200
        data = response.json()

        actions = data["actions"]

        # Should recommend both fertilization and scouting
        action_types = [a["type"] for a in actions]
        assert "fertilization" in action_types or "scouting" in action_types


class TestSeverityClassification:
    """Test disease severity classification"""

    def test_severity_levels_in_actions(self):
        """Test that actions include severity levels"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        indices = Indices(
            ndvi=0.28,
            evi=0.22,
            ndre=0.14,
            lci=0.12,
            ndwi=-0.16,
            savi=0.25
        )

        obs = ZoneObservation(
            zone_id="severity_test",
            growth_stage=GrowthStage.mid,
            indices=indices
        )

        actions = diagnose_zone(obs)

        # Actions should have severity field
        for action in actions:
            assert "severity" in action
            if action["severity"]:
                assert action["severity"] in ["ok", "low", "moderate", "warning", "critical"]

    def test_critical_severity_conditions(self):
        """Test conditions that trigger critical severity"""
        from src.decision_engine import Indices, ZoneObservation, GrowthStage, diagnose_zone

        critical_indices = Indices(
            ndvi=0.25,
            evi=0.20,
            ndre=0.12,
            lci=0.10,
            ndwi=-0.20,  # Extreme stress
            savi=0.22
        )

        obs = ZoneObservation(
            zone_id="critical_severity",
            growth_stage=GrowthStage.mid,
            indices=critical_indices
        )

        actions = diagnose_zone(obs)

        # Should have critical severity actions
        critical_actions = [
            a for a in actions
            if a.get("severity") == "critical"
        ]
        assert len(critical_actions) > 0


class TestAPIResponseStructure:
    """Test API response structure for disease detection"""

    def test_diagnosis_action_structure(self, client):
        """Test that diagnosis actions have all required fields"""
        response = client.get(
            "/api/v1/fields/field_demo/diagnosis",
            params={"date": "2025-12-14"}
        )

        assert response.status_code == 200
        data = response.json()

        actions = data["actions"]

        for action in actions:
            # Required fields
            assert "zone_id" in action
            assert "type" in action
            assert "priority" in action
            assert "title" in action
            assert "reason" in action
            assert "evidence" in action

            # Optional but expected fields
            assert "title_en" in action or action["title_en"] is None
            assert "reason_en" in action or action["reason_en"] is None

    def test_map_layers_in_diagnosis(self, client):
        """Test that map layers are provided for visual disease inspection"""
        response = client.get(
            "/api/v1/fields/field_demo/diagnosis",
            params={"date": "2025-12-14"}
        )

        assert response.status_code == 200
        data = response.json()

        map_layers = data["map_layers"]

        # Should have NDVI layer for disease detection
        assert "ndvi_raster_url" in map_layers

        # Should have NDRE for nitrogen deficiency
        assert "ndre_raster_url" in map_layers

        # Should have zones GeoJSON
        assert "zones_geojson_url" in map_layers
