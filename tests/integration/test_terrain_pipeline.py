# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Integration tests for Terrain Pipeline
اختبارات التكامل لخط أنابيب التضاريس

End-to-end test: field -> analyze terrain -> hydrology -> leveling

This test suite validates the complete flow from field geometry through
terrain analysis to hydrology assessment and leveling recommendations.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_field_geometry() -> dict[str, Any]:
    """Create a sample field geometry for terrain analysis."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [44.0, 15.0],
                [44.05, 15.0],
                [44.05, 15.05],
                [44.0, 15.05],
                [44.0, 15.0],
            ]
        ],
        "properties": {
            "field_id": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "name": "North Field",
            "name_ar": "الحقل الشمالي",
            "area_hectares": 25.0,
            "crop_type": "wheat",
            "irrigation_type": "surface",
        },
    }


@pytest.fixture
def sample_dem_data() -> np.ndarray:
    """Create sample DEM data for testing."""
    rows, cols = 100, 100
    dem = np.zeros((rows, cols), dtype=np.float32)

    # Create realistic terrain with slope and variations
    np.random.seed(42)
    base_elevation = 100.0

    for i in range(rows):
        for j in range(cols):
            # Base slope toward southeast
            dem[i, j] = base_elevation - i * 0.15 - j * 0.05
            # Add random micro-topography
            dem[i, j] += np.random.uniform(-0.3, 0.3)

    # Add a depression
    dem[40:50, 30:40] -= 1.5

    # Add a high spot
    dem[70:80, 70:80] += 0.8

    return dem


@pytest.fixture
def sample_weather_context() -> dict[str, Any]:
    """Create sample weather context for hydrology analysis."""
    return {
        "current": {
            "precipitation_mm": 5.0,
            "soil_moisture_percent": 45.0,
            "temperature_c": 25.0,
            "humidity_percent": 55.0,
        },
        "forecast_7d": [
            {"date": "2026-01-25", "precipitation_mm": 15.0, "probability": 0.8},
            {"date": "2026-01-26", "precipitation_mm": 25.0, "probability": 0.9},
            {"date": "2026-01-27", "precipitation_mm": 10.0, "probability": 0.6},
            {"date": "2026-01-28", "precipitation_mm": 0.0, "probability": 0.1},
            {"date": "2026-01-29", "precipitation_mm": 0.0, "probability": 0.1},
            {"date": "2026-01-30", "precipitation_mm": 5.0, "probability": 0.4},
            {"date": "2026-01-31", "precipitation_mm": 8.0, "probability": 0.5},
        ],
        "historical": {
            "avg_annual_rainfall_mm": 250,
            "max_24h_rainfall_mm": 85,
        },
    }


@pytest.fixture
def mock_terrain_service(sample_dem_data: np.ndarray):
    """Create a mock Terrain Core Service."""
    mock_service = MagicMock()

    # Create realistic analysis results based on sample DEM
    dem = sample_dem_data

    # Calculate slope
    cell_size = 30.0
    gradient_y, gradient_x = np.gradient(dem, cell_size)
    slope_radians = np.arctan(np.sqrt(gradient_x**2 + gradient_y**2))
    slope_degrees = np.degrees(slope_radians)

    # Calculate aspect
    aspect_radians = np.arctan2(-gradient_x, gradient_y)
    aspect_degrees = np.degrees(aspect_radians)
    aspect_degrees = np.where(aspect_degrees < 0, aspect_degrees + 360, aspect_degrees)

    # Calculate TWI (simplified)
    flow_acc = np.ones_like(dem) * 100  # Simplified
    twi = np.log(flow_acc / (np.tan(slope_radians) + 0.001))

    mock_service.analyze_terrain = AsyncMock(
        return_value={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 1250.5,
            "dem_source": "copernicus",
            "resolution_m": 30.0,
            "elevation": {
                "min_m": float(np.min(dem)),
                "max_m": float(np.max(dem)),
                "mean_m": float(np.mean(dem)),
                "std_m": float(np.std(dem)),
                "range_m": float(np.max(dem) - np.min(dem)),
            },
            "slope": {
                "min_degrees": float(np.min(slope_degrees)),
                "max_degrees": float(np.max(slope_degrees)),
                "mean_degrees": float(np.mean(slope_degrees)),
                "std_degrees": float(np.std(slope_degrees)),
                "classification": {
                    "flat_percent": 25.0,
                    "gentle_percent": 45.0,
                    "moderate_percent": 25.0,
                    "steep_percent": 5.0,
                },
            },
            "aspect": {
                "dominant_direction": "SE",
                "dominant_direction_ar": "جنوب شرق",
                "distribution": {
                    "N": 5.0,
                    "NE": 8.0,
                    "E": 15.0,
                    "SE": 35.0,
                    "S": 20.0,
                    "SW": 10.0,
                    "W": 5.0,
                    "NW": 2.0,
                },
            },
            "twi": {
                "min": float(np.min(twi)),
                "max": float(np.max(twi)),
                "mean": float(np.mean(twi)),
                "high_wetness_area_percent": 15.0,
            },
            "contours": {
                "type": "FeatureCollection",
                "features": [],  # Simplified
            },
            "flow_direction": {
                "type": "raster",
                "dominant_direction": "SE",
            },
        }
    )

    mock_service.get_dem = AsyncMock(return_value=dem)

    return mock_service


@pytest.fixture
def mock_hydrology_service(sample_dem_data: np.ndarray):
    """Create a mock Hydrology Service."""
    mock_service = MagicMock()

    mock_service.analyze_drainage = AsyncMock(
        return_value={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 850.3,
            "drainage_network": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "stream_order": 1,
                            "length_m": 180.0,
                        },
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[44.02, 15.02], [44.025, 15.03]],
                        },
                    }
                ],
            },
            "statistics": {
                "total_stream_length_m": 450.0,
                "drainage_density_km_per_km2": 1.8,
                "stream_count": 5,
                "max_stream_order": 2,
            },
            "depressions": [
                {
                    "id": "dep_001",
                    "location": {"lat": 15.025, "lon": 44.015},
                    "depth_m": 1.2,
                    "area_m2": 2700.0,
                    "volume_m3": 1620.0,
                }
            ],
        }
    )

    mock_service.predict_waterlogging = AsyncMock(
        return_value={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 420.5,
            "current_risk": 0.45,
            "risk_level": "moderate",
            "risk_level_ar": "متوسط",
            "risk_zones": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "risk_level": "high",
                            "area_m2": 5000,
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [44.01, 15.02],
                                    [44.02, 15.02],
                                    [44.02, 15.03],
                                    [44.01, 15.03],
                                    [44.01, 15.02],
                                ]
                            ],
                        },
                    }
                ],
            },
            "temporal_forecast": [
                {"date": "2026-01-25", "risk": 0.55},
                {"date": "2026-01-26", "risk": 0.72},
                {"date": "2026-01-27", "risk": 0.65},
                {"date": "2026-01-28", "risk": 0.45},
                {"date": "2026-01-29", "risk": 0.35},
                {"date": "2026-01-30", "risk": 0.40},
                {"date": "2026-01-31", "risk": 0.48},
            ],
            "recommendations": [
                {
                    "action": "Create surface drainage channels",
                    "action_ar": "إنشاء قنوات صرف سطحية",
                    "priority": "medium",
                    "estimated_cost_sar": 5000,
                },
                {
                    "action": "Monitor depression area during rainfall",
                    "action_ar": "مراقبة منطقة الانخفاض أثناء هطول الأمطار",
                    "priority": "high",
                    "estimated_cost_sar": 0,
                },
            ],
        }
    )

    return mock_service


@pytest.fixture
def mock_leveling_service(sample_dem_data: np.ndarray):
    """Create a mock Leveling Optimizer Service."""
    mock_service = MagicMock()

    dem = sample_dem_data
    cell_size = 30.0

    # Calculate cut/fill for target plane
    target_elevation = np.mean(dem)
    diff = dem - target_elevation
    cut_volume = float(np.sum(diff[diff > 0]) * cell_size**2)
    fill_volume = float(np.abs(np.sum(diff[diff < 0])) * cell_size**2)

    mock_service.calculate_leveling = AsyncMock(
        return_value={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 680.2,
            "existing_terrain": {
                "min_elevation_m": float(np.min(dem)),
                "max_elevation_m": float(np.max(dem)),
                "mean_elevation_m": float(np.mean(dem)),
                "std_elevation_m": float(np.std(dem)),
            },
            "optimal_plane": {
                "base_elevation_m": target_elevation,
                "slope_percent": 0.1,
                "slope_direction_degrees": 180,
                "slope_direction_ar": "جنوب",
            },
            "earthwork": {
                "cut_volume_m3": cut_volume,
                "fill_volume_m3": fill_volume,
                "balance_ratio": min(cut_volume, fill_volume) / max(cut_volume, fill_volume),
                "total_volume_m3": cut_volume + fill_volume,
            },
            "statistics": {
                "cut_area_m2": 45000,
                "fill_area_m2": 42500,
                "avg_cut_depth_m": cut_volume / 45000,
                "avg_fill_depth_m": fill_volume / 42500,
                "max_cut_depth_m": float(np.max(diff)),
                "max_fill_depth_m": float(np.abs(np.min(diff))),
            },
            "constraints_check": {
                "meets_max_cut": True,
                "meets_max_fill": True,
                "violations": [],
            },
        }
    )

    mock_service.estimate_cost = AsyncMock(
        return_value={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "cost_breakdown": {
                "earthmoving": {
                    "description": "Cut and fill operations",
                    "description_ar": "عمليات القطع والردم",
                    "cost_sar": 35000,
                },
                "fine_grading": {
                    "description": "Surface finishing",
                    "description_ar": "التشطيب السطحي",
                    "cost_sar": 12500,
                },
                "laser_leveling": {
                    "description": "Precision leveling",
                    "description_ar": "التسوية الدقيقة",
                    "cost_sar": 9500,
                },
            },
            "total_cost_sar": 57000,
            "cost_per_hectare_sar": 2280,
            "estimated_duration_days": 10,
        }
    )

    mock_service.recommend_equipment = AsyncMock(
        return_value={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "recommended_equipment": [
                {
                    "name": "Land Scraper",
                    "name_ar": "كاشطة الأراضي",
                    "quantity": 2,
                    "usage_hours": 48,
                    "phase": "rough_grading",
                },
                {
                    "name": "Motor Grader",
                    "name_ar": "ممهدة",
                    "quantity": 1,
                    "usage_hours": 20,
                    "phase": "fine_grading",
                },
                {
                    "name": "Laser Land Plane",
                    "name_ar": "مسوي بالليزر",
                    "quantity": 1,
                    "usage_hours": 24,
                    "phase": "precision_leveling",
                },
            ],
            "project_phases": [
                {
                    "name": "Rough Grading",
                    "name_ar": "التسوية الخشنة",
                    "duration_days": 6,
                    "sequence": 1,
                },
                {
                    "name": "Fine Grading",
                    "name_ar": "التسوية الدقيقة",
                    "duration_days": 2,
                    "sequence": 2,
                },
                {
                    "name": "Precision Leveling",
                    "name_ar": "التسوية بالليزر",
                    "duration_days": 2,
                    "sequence": 3,
                },
            ],
        }
    )

    return mock_service


@pytest.fixture
def mock_nats_client():
    """Create a mock NATS client for event publishing."""
    mock_nats = MagicMock()
    published_events = []

    async def mock_publish(subject: str, data: bytes):
        published_events.append(
            {
                "subject": subject,
                "data": json.loads(data.decode()),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    mock_nats.publish = AsyncMock(side_effect=mock_publish)
    mock_nats.published_events = published_events

    return mock_nats


# =============================================================================
# Terrain Pipeline Class
# =============================================================================


class TerrainPipeline:
    """
    Terrain Pipeline orchestrator for end-to-end terrain analysis workflow.
    خط أنابيب التضاريس لتنسيق سير عمل تحليل التضاريس من البداية إلى النهاية.
    """

    def __init__(
        self,
        terrain_service,
        hydrology_service,
        leveling_service,
        nats_client,
    ):
        self.terrain_service = terrain_service
        self.hydrology_service = hydrology_service
        self.leveling_service = leveling_service
        self.nats_client = nats_client

    async def analyze_field(
        self,
        field_geometry: dict[str, Any],
        weather_context: dict[str, Any] | None = None,
        include_leveling: bool = True,
    ) -> dict[str, Any]:
        """
        Perform complete terrain analysis for a field.

        Steps:
        1. Load and analyze terrain (DEM, slope, aspect, TWI)
        2. Perform hydrology analysis (drainage, waterlogging)
        3. Calculate leveling requirements
        4. Generate recommendations
        5. Publish events

        Args:
            field_geometry: GeoJSON field polygon with properties
            weather_context: Optional weather data for hydrology analysis
            include_leveling: Whether to include leveling analysis

        Returns:
            Complete terrain analysis result
        """
        pipeline_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        field_id = field_geometry["properties"]["field_id"]
        tenant_id = field_geometry["properties"]["tenant_id"]

        result = {
            "pipeline_id": pipeline_id,
            "field_id": field_id,
            "tenant_id": tenant_id,
            "field_name": field_geometry["properties"]["name"],
            "field_name_ar": field_geometry["properties"]["name_ar"],
            "area_hectares": field_geometry["properties"]["area_hectares"],
            "started_at": start_time.isoformat(),
            "analyses": {},
            "recommendations": [],
            "events_published": [],
        }

        # Step 1: Terrain Analysis
        terrain_result = await self.terrain_service.analyze_terrain(field_geometry)
        result["analyses"]["terrain"] = terrain_result

        # Step 2: Hydrology Analysis
        drainage_result = await self.hydrology_service.analyze_drainage(field_geometry)
        result["analyses"]["drainage"] = drainage_result

        # Waterlogging prediction (requires weather context)
        if weather_context:
            waterlogging_result = await self.hydrology_service.predict_waterlogging(field_geometry, weather_context)
            result["analyses"]["waterlogging"] = waterlogging_result

            # Add waterlogging recommendations
            for rec in waterlogging_result.get("recommendations", []):
                result["recommendations"].append(
                    {
                        "category": "hydrology",
                        "category_ar": "هيدرولوجيا",
                        **rec,
                    }
                )

        # Step 3: Leveling Analysis (if requested)
        if include_leveling:
            leveling_result = await self.leveling_service.calculate_leveling(field_geometry, terrain_result)
            result["analyses"]["leveling"] = leveling_result

            cost_result = await self.leveling_service.estimate_cost(leveling_result)
            result["analyses"]["leveling_cost"] = cost_result

            equipment_result = await self.leveling_service.recommend_equipment(leveling_result)
            result["analyses"]["equipment"] = equipment_result

            # Add leveling recommendations
            result["recommendations"].append(
                {
                    "category": "leveling",
                    "category_ar": "تسوية",
                    "action": f"Land leveling required: {leveling_result['earthwork']['total_volume_m3']:.0f} m3",
                    "action_ar": f"التسوية مطلوبة: {leveling_result['earthwork']['total_volume_m3']:.0f} م3",
                    "priority": "medium",
                    "estimated_cost_sar": cost_result["total_cost_sar"],
                }
            )

        # Step 4: Generate summary recommendations based on terrain analysis
        terrain_data = terrain_result
        if terrain_data["slope"]["mean_degrees"] > 5:
            result["recommendations"].append(
                {
                    "category": "erosion",
                    "category_ar": "انجراف",
                    "action": "Consider contour farming to reduce erosion",
                    "action_ar": "النظر في الزراعة الكنتورية لتقليل الانجراف",
                    "priority": "medium",
                    "estimated_cost_sar": None,
                }
            )

        if terrain_data["twi"]["high_wetness_area_percent"] > 20:
            result["recommendations"].append(
                {
                    "category": "drainage",
                    "category_ar": "صرف",
                    "action": "Install drainage in high wetness areas",
                    "action_ar": "تركيب نظام صرف في مناطق الرطوبة العالية",
                    "priority": "high",
                    "estimated_cost_sar": 8000,
                }
            )

        # Step 5: Publish events
        event = {
            "event_type": "terrain.analysis.completed",
            "pipeline_id": pipeline_id,
            "field_id": field_id,
            "tenant_id": tenant_id,
            "summary": {
                "mean_slope_degrees": terrain_data["slope"]["mean_degrees"],
                "dominant_aspect": terrain_data["aspect"]["dominant_direction"],
                "drainage_density": drainage_result["statistics"]["drainage_density_km_per_km2"],
                "depression_count": len(drainage_result.get("depressions", [])),
                "recommendation_count": len(result["recommendations"]),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        if include_leveling:
            event["summary"]["cut_volume_m3"] = leveling_result["earthwork"]["cut_volume_m3"]
            event["summary"]["fill_volume_m3"] = leveling_result["earthwork"]["fill_volume_m3"]
            event["summary"]["estimated_cost_sar"] = cost_result["total_cost_sar"]

        await self.nats_client.publish(
            f"sahool.{tenant_id}.terrain.analysis",
            json.dumps(event).encode(),
        )
        result["events_published"].append(event)

        result["completed_at"] = datetime.utcnow().isoformat()
        result["processing_time_ms"] = (datetime.utcnow() - start_time).total_seconds() * 1000

        return result


# =============================================================================
# Integration Tests
# =============================================================================


class TestTerrainPipelineIntegration:
    """Integration tests for the complete terrain pipeline."""

    @pytest.mark.asyncio
    async def test_complete_terrain_pipeline(
        self,
        sample_field_geometry: dict[str, Any],
        sample_weather_context: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test complete terrain analysis pipeline."""
        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            weather_context=sample_weather_context,
            include_leveling=True,
        )

        # Verify pipeline completed
        assert result["pipeline_id"] is not None
        assert result["field_id"] == sample_field_geometry["properties"]["field_id"]

        # Verify all analyses completed
        assert "terrain" in result["analyses"]
        assert "drainage" in result["analyses"]
        assert "waterlogging" in result["analyses"]
        assert "leveling" in result["analyses"]

        # Verify recommendations generated
        assert len(result["recommendations"]) > 0

        # Verify event published
        assert len(mock_nats_client.published_events) == 1

    @pytest.mark.asyncio
    async def test_terrain_analysis_results(
        self,
        sample_field_geometry: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test terrain analysis results structure."""
        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            include_leveling=False,
        )

        terrain = result["analyses"]["terrain"]

        # Verify elevation data
        assert "elevation" in terrain
        assert terrain["elevation"]["min_m"] < terrain["elevation"]["max_m"]

        # Verify slope data
        assert "slope" in terrain
        assert terrain["slope"]["mean_degrees"] >= 0

        # Verify aspect data
        assert "aspect" in terrain
        assert terrain["aspect"]["dominant_direction"] in [
            "N",
            "NE",
            "E",
            "SE",
            "S",
            "SW",
            "W",
            "NW",
        ]

        # Verify TWI data
        assert "twi" in terrain
        assert terrain["twi"]["mean"] > 0

    @pytest.mark.asyncio
    async def test_hydrology_analysis_results(
        self,
        sample_field_geometry: dict[str, Any],
        sample_weather_context: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test hydrology analysis results structure."""
        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            weather_context=sample_weather_context,
            include_leveling=False,
        )

        drainage = result["analyses"]["drainage"]
        waterlogging = result["analyses"]["waterlogging"]

        # Verify drainage data
        assert "drainage_network" in drainage
        assert "statistics" in drainage
        assert drainage["statistics"]["drainage_density_km_per_km2"] > 0

        # Verify depressions identified
        assert "depressions" in drainage

        # Verify waterlogging prediction
        assert waterlogging["current_risk"] >= 0
        assert waterlogging["current_risk"] <= 1
        assert waterlogging["risk_level"] in ["low", "moderate", "high", "critical"]
        assert "temporal_forecast" in waterlogging

    @pytest.mark.asyncio
    async def test_leveling_analysis_results(
        self,
        sample_field_geometry: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test leveling analysis results structure."""
        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            include_leveling=True,
        )

        leveling = result["analyses"]["leveling"]
        cost = result["analyses"]["leveling_cost"]
        equipment = result["analyses"]["equipment"]

        # Verify leveling calculations
        assert "earthwork" in leveling
        assert leveling["earthwork"]["cut_volume_m3"] > 0
        assert leveling["earthwork"]["fill_volume_m3"] > 0
        assert 0 < leveling["earthwork"]["balance_ratio"] <= 1

        # Verify cost estimate
        assert cost["total_cost_sar"] > 0
        assert cost["cost_per_hectare_sar"] > 0
        assert cost["estimated_duration_days"] > 0

        # Verify equipment recommendations
        assert len(equipment["recommended_equipment"]) > 0
        assert len(equipment["project_phases"]) > 0

    @pytest.mark.asyncio
    async def test_pipeline_without_leveling(
        self,
        sample_field_geometry: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test pipeline without leveling analysis."""
        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            include_leveling=False,
        )

        # Verify leveling not included
        assert "leveling" not in result["analyses"]
        assert "leveling_cost" not in result["analyses"]
        assert "equipment" not in result["analyses"]

        # Terrain and hydrology should still be present
        assert "terrain" in result["analyses"]
        assert "drainage" in result["analyses"]

    @pytest.mark.asyncio
    async def test_pipeline_without_weather_context(
        self,
        sample_field_geometry: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test pipeline without weather context."""
        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            weather_context=None,
            include_leveling=True,
        )

        # Waterlogging prediction should not be present without weather
        assert "waterlogging" not in result["analyses"]

        # Other analyses should still be present
        assert "terrain" in result["analyses"]
        assert "drainage" in result["analyses"]
        assert "leveling" in result["analyses"]

    @pytest.mark.asyncio
    async def test_recommendations_generated(
        self,
        sample_field_geometry: dict[str, Any],
        sample_weather_context: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test that appropriate recommendations are generated."""
        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            weather_context=sample_weather_context,
            include_leveling=True,
        )

        recommendations = result["recommendations"]

        # Should have at least leveling recommendation
        assert len(recommendations) >= 1

        # Each recommendation should have required fields
        for rec in recommendations:
            assert "category" in rec
            assert "category_ar" in rec
            assert "action" in rec
            assert "action_ar" in rec
            assert "priority" in rec

    @pytest.mark.asyncio
    async def test_event_publishing(
        self,
        sample_field_geometry: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test that pipeline publishes events correctly."""
        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            include_leveling=True,
        )

        # Verify event published
        assert len(mock_nats_client.published_events) == 1

        event = mock_nats_client.published_events[0]
        tenant_id = sample_field_geometry["properties"]["tenant_id"]

        # Verify event subject
        assert event["subject"] == f"sahool.{tenant_id}.terrain.analysis"

        # Verify event content
        event_data = event["data"]
        assert event_data["event_type"] == "terrain.analysis.completed"
        assert event_data["pipeline_id"] == result["pipeline_id"]
        assert "summary" in event_data


class TestTerrainPipelineDataFlow:
    """Tests for data flow through the terrain pipeline."""

    @pytest.mark.asyncio
    async def test_field_properties_preserved(
        self,
        sample_field_geometry: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test that field properties are preserved through pipeline."""
        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        result = await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            include_leveling=True,
        )

        props = sample_field_geometry["properties"]

        # Verify field properties in result
        assert result["field_id"] == props["field_id"]
        assert result["tenant_id"] == props["tenant_id"]
        assert result["field_name"] == props["name"]
        assert result["field_name_ar"] == props["name_ar"]
        assert result["area_hectares"] == props["area_hectares"]

    @pytest.mark.asyncio
    async def test_service_call_sequence(
        self,
        sample_field_geometry: dict[str, Any],
        sample_weather_context: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test that services are called in correct sequence."""
        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            weather_context=sample_weather_context,
            include_leveling=True,
        )

        # Verify all services were called
        mock_terrain_service.analyze_terrain.assert_called_once()
        mock_hydrology_service.analyze_drainage.assert_called_once()
        mock_hydrology_service.predict_waterlogging.assert_called_once()
        mock_leveling_service.calculate_leveling.assert_called_once()
        mock_leveling_service.estimate_cost.assert_called_once()
        mock_leveling_service.recommend_equipment.assert_called_once()


class TestTerrainPipelinePerformance:
    """Performance tests for the terrain pipeline."""

    @pytest.mark.asyncio
    async def test_pipeline_processing_time(
        self,
        sample_field_geometry: dict[str, Any],
        mock_terrain_service,
        mock_hydrology_service,
        mock_leveling_service,
        mock_nats_client,
    ):
        """Test pipeline completes within acceptable time."""
        import time

        pipeline = TerrainPipeline(
            terrain_service=mock_terrain_service,
            hydrology_service=mock_hydrology_service,
            leveling_service=mock_leveling_service,
            nats_client=mock_nats_client,
        )

        start_time = time.time()
        result = await pipeline.analyze_field(
            field_geometry=sample_field_geometry,
            include_leveling=True,
        )
        elapsed_time = time.time() - start_time

        # Should complete within 10 seconds (with mocks)
        assert elapsed_time < 10.0
        assert result["processing_time_ms"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
