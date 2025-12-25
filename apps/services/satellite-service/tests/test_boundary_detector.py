"""
Unit tests for Field Boundary Detector
"""

import pytest
from datetime import datetime
from src.field_boundary_detector import (
    FieldBoundaryDetector,
    FieldBoundary,
    BoundaryChange,
    DetectionMethod
)


class TestFieldBoundaryDetector:
    """Test suite for FieldBoundaryDetector"""

    def setup_method(self):
        """Set up test fixtures"""
        self.detector = FieldBoundaryDetector()

    def test_initialization(self):
        """Test detector initialization"""
        assert self.detector is not None
        assert self.detector.ndvi_threshold == 0.25
        assert self.detector.edge_sensitivity == 0.15
        assert self.detector.min_area_hectares == 0.1
        assert self.detector.max_area_hectares == 500.0

    def test_calculate_area_rectangle(self):
        """Test area calculation for a rectangle"""
        # ~100m x 100m rectangle at equator
        coords = [
            (0.0, 0.0),
            (0.0009, 0.0),
            (0.0009, 0.0009),
            (0.0, 0.0009)
        ]
        area = self.detector.calculate_area(coords)
        # Should be approximately 1 hectare
        assert 0.9 < area < 1.1

    def test_calculate_area_triangle(self):
        """Test area calculation for a triangle"""
        # Simple triangle
        coords = [
            (0.0, 0.0),
            (0.001, 0.0),
            (0.0005, 0.001)
        ]
        area = self.detector.calculate_area(coords)
        assert area > 0

    def test_calculate_perimeter_square(self):
        """Test perimeter calculation for a square"""
        # ~100m x 100m square at equator
        coords = [
            (0.0, 0.0),
            (0.0009, 0.0),
            (0.0009, 0.0009),
            (0.0, 0.0009)
        ]
        perimeter = self.detector.calculate_perimeter(coords)
        # Should be approximately 400 meters
        assert 350 < perimeter < 450

    def test_haversine_distance(self):
        """Test Haversine distance calculation"""
        # Distance from equator to 1 degree north (should be ~111 km)
        distance = self.detector._haversine_distance(0.0, 0.0, 1.0, 0.0)
        assert 111000 < distance < 112000

    def test_calculate_centroid(self):
        """Test centroid calculation"""
        coords = [
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0)
        ]
        centroid = self.detector._calculate_centroid(coords)
        assert centroid == (0.5, 0.5)

    def test_calculate_centroid_triangle(self):
        """Test centroid of a triangle"""
        coords = [
            (0.0, 0.0),
            (3.0, 0.0),
            (0.0, 3.0)
        ]
        centroid = self.detector._calculate_centroid(coords)
        assert centroid == (1.0, 1.0)

    def test_simplify_boundary_no_change(self):
        """Test boundary simplification with high tolerance"""
        coords = [
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0)
        ]
        simplified = self.detector.simplify_boundary(coords, tolerance=0.0001)
        # Square should remain mostly unchanged
        assert len(simplified) >= 3

    def test_simplify_boundary_reduction(self):
        """Test that simplification reduces points"""
        # Create a line with many collinear points
        coords = [(i * 0.0001, 0.0) for i in range(100)]
        coords.append((0.01, 0.01))  # Add corner
        coords.extend([(0.0, i * 0.0001) for i in range(100, 0, -1)])

        simplified = self.detector.simplify_boundary(coords, tolerance=0.001)
        # Should have fewer points
        assert len(simplified) < len(coords)

    def test_calculate_average_radius(self):
        """Test average radius calculation"""
        # Square centered at (0.5, 0.5)
        coords = [
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0)
        ]
        centroid = (0.5, 0.5)
        radius = self.detector._calculate_average_radius(coords, centroid)
        assert radius > 0

    @pytest.mark.asyncio
    async def test_detect_boundary_simulated(self):
        """Test boundary detection (simulated)"""
        boundaries = await self.detector.detect_boundary(
            latitude=15.5527,
            longitude=44.2075,
            radius_meters=500
        )

        # Should return at least one boundary (simulated)
        assert len(boundaries) > 0
        boundary = boundaries[0]

        # Check boundary properties
        assert isinstance(boundary, FieldBoundary)
        assert boundary.area_hectares > 0
        assert boundary.perimeter_meters > 0
        assert 0 <= boundary.detection_confidence <= 1
        assert boundary.method == DetectionMethod.NDVI_EDGE.value

    @pytest.mark.asyncio
    async def test_refine_boundary_simulated(self):
        """Test boundary refinement (simulated)"""
        initial_coords = [
            (44.207, 15.552),
            (44.208, 15.552),
            (44.208, 15.553),
            (44.207, 15.553)
        ]

        refined = await self.detector.refine_boundary(
            initial_coords=initial_coords,
            buffer_meters=50
        )

        # Check refined boundary
        assert isinstance(refined, FieldBoundary)
        assert refined.area_hectares > 0
        assert refined.method == DetectionMethod.REFINED.value

    @pytest.mark.asyncio
    async def test_detect_boundary_change_simulated(self):
        """Test boundary change detection (simulated)"""
        previous_coords = [
            (44.207, 15.552),
            (44.208, 15.552),
            (44.208, 15.553),
            (44.207, 15.553)
        ]

        change = await self.detector.detect_boundary_change(
            field_id="test_field_123",
            previous_coords=previous_coords,
            current_date=datetime.now()
        )

        # Check change result
        assert isinstance(change, BoundaryChange)
        assert change.change_type in ["stable", "expansion", "contraction"]
        assert change.previous_area > 0

    def test_field_boundary_to_geojson(self):
        """Test FieldBoundary to GeoJSON conversion"""
        boundary = FieldBoundary(
            field_id="test_field",
            coordinates=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],
            area_hectares=100.5,
            perimeter_meters=4000.0,
            centroid=(0.5, 0.5),
            detection_confidence=0.85,
            detection_date=datetime(2024, 1, 15),
            method="ndvi_edge",
            mean_ndvi=0.65,
            quality_score=0.80
        )

        geojson = boundary.to_geojson()

        # Check GeoJSON structure
        assert geojson["type"] == "Feature"
        assert geojson["geometry"]["type"] == "Polygon"
        assert len(geojson["geometry"]["coordinates"][0]) == 4
        assert geojson["properties"]["field_id"] == "test_field"
        assert geojson["properties"]["area_hectares"] == 100.5
        assert geojson["properties"]["detection_confidence"] == 0.85

    def test_calculate_confidence(self):
        """Test confidence calculation"""
        # Regular square
        coords = [
            (0.0, 0.0),
            (0.001, 0.0),
            (0.001, 0.001),
            (0.0, 0.001)
        ]
        area = self.detector.calculate_area(coords)
        perimeter = self.detector.calculate_perimeter(coords)
        confidence = self.detector._calculate_confidence(coords, area, perimeter)

        # Should have reasonable confidence
        assert 0.5 < confidence <= 1.0

    def test_calculate_quality_score(self):
        """Test quality score calculation"""
        # Regular square
        coords = [
            (0.0, 0.0),
            (0.001, 0.0),
            (0.001, 0.001),
            (0.0, 0.001)
        ]
        area = self.detector.calculate_area(coords)
        perimeter = self.detector.calculate_perimeter(coords)
        quality = self.detector._calculate_quality_score(coords, area, perimeter)

        # Should have good quality score
        assert 0.5 < quality <= 1.0

    def test_edge_cases(self):
        """Test edge cases"""
        # Empty coordinates
        assert self.detector.calculate_area([]) == 0.0
        assert self.detector.calculate_perimeter([]) == 0.0
        assert self.detector._calculate_centroid([]) == (0.0, 0.0)

        # Single point
        assert self.detector.calculate_area([(0.0, 0.0)]) == 0.0

        # Two points (line)
        assert self.detector.calculate_area([(0.0, 0.0), (1.0, 1.0)]) == 0.0

    def test_detection_parameters(self):
        """Test parameter configuration"""
        detector = FieldBoundaryDetector()

        # Modify parameters
        detector.ndvi_threshold = 0.3
        detector.edge_sensitivity = 0.2
        detector.min_area_hectares = 0.5
        detector.max_area_hectares = 100.0

        assert detector.ndvi_threshold == 0.3
        assert detector.edge_sensitivity == 0.2
        assert detector.min_area_hectares == 0.5
        assert detector.max_area_hectares == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
