"""
Field Service Tests
اختبارات خدمة الحقول
"""

from datetime import datetime
from uuid import uuid4

import pytest


class TestFieldCreation:
    """Test suite for field creation."""

    def test_create_field_with_valid_data(self):
        """Test creating a field with valid data."""
        field_data = {
            "name": "حقل القمح الشمالي",
            "area_hectares": 15.5,
            "crop_type": "wheat",
            "location": {
                "lat": 24.7136,
                "lng": 46.6753,
            },
            "boundary": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [46.67, 24.71],
                        [46.68, 24.71],
                        [46.68, 24.72],
                        [46.67, 24.72],
                        [46.67, 24.71],
                    ]
                ],
            },
        }

        field = self._create_field(field_data, tenant_id="tenant-123")

        assert field["id"] is not None
        assert field["name"] == "حقل القمح الشمالي"
        assert field["area_hectares"] == 15.5
        assert field["tenant_id"] == "tenant-123"

    def test_create_field_validates_area(self):
        """Test field creation validates area."""
        field_data = {
            "name": "Small Field",
            "area_hectares": -5,  # Invalid
        }

        with pytest.raises(ValueError, match="area"):
            self._create_field(field_data, tenant_id="tenant-1")

    def test_create_field_validates_boundary(self):
        """Test field creation validates boundary polygon."""
        field_data = {
            "name": "Invalid Field",
            "area_hectares": 10,
            "boundary": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 1]]],  # Not enough points
            },
        }

        with pytest.raises(ValueError, match="boundary"):
            self._create_field(field_data, tenant_id="tenant-1")

    def test_create_field_sets_defaults(self):
        """Test field creation sets default values."""
        field_data = {
            "name": "Test Field",
            "area_hectares": 10,
        }

        field = self._create_field(field_data, tenant_id="tenant-1")

        assert field["status"] == "active"
        assert field["created_at"] is not None
        assert field["ndvi_history"] == []

    @staticmethod
    def _create_field(data: dict, tenant_id: str) -> dict:
        """Create a new field."""
        if data.get("area_hectares", 0) <= 0:
            raise ValueError("Invalid area: must be positive")

        boundary = data.get("boundary")
        if boundary:
            coords = boundary.get("coordinates", [[]])[0]
            if len(coords) < 4:
                raise ValueError(
                    "Invalid boundary: polygon must have at least 4 points"
                )

        return {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "name": data["name"],
            "area_hectares": data["area_hectares"],
            "crop_type": data.get("crop_type"),
            "location": data.get("location"),
            "boundary": boundary,
            "status": "active",
            "created_at": datetime.utcnow(),
            "ndvi_history": [],
        }


class TestFieldBoundary:
    """Test suite for field boundary operations."""

    def test_calculate_centroid(self):
        """Test calculating field centroid from boundary."""
        boundary = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
        }

        centroid = self._calculate_centroid(boundary)

        assert centroid["lat"] == pytest.approx(5, rel=0.1)
        assert centroid["lng"] == pytest.approx(5, rel=0.1)

    def test_calculate_area_from_boundary(self):
        """Test calculating area from boundary coordinates."""
        # Simple 10x10 square at equator
        boundary = {
            "type": "Polygon",
            "coordinates": [
                [[0, 0], [0.0001, 0], [0.0001, 0.0001], [0, 0.0001], [0, 0]]
            ],
        }

        # At equator, 0.0001 degrees ≈ 11 meters
        area = self._calculate_area(boundary)

        assert area > 0

    def test_validate_boundary_is_closed(self):
        """Test boundary validation ensures polygon is closed."""
        # First and last point must be the same
        boundary = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1]]],  # Not closed
        }

        is_valid = self._is_valid_boundary(boundary)

        assert is_valid is False

    def test_valid_boundary(self):
        """Test valid boundary passes validation."""
        boundary = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],  # Closed
        }

        is_valid = self._is_valid_boundary(boundary)

        assert is_valid is True

    @staticmethod
    def _calculate_centroid(boundary: dict) -> dict:
        """Calculate centroid of polygon."""
        coords = boundary["coordinates"][0]
        n = len(coords) - 1  # Exclude closing point

        lat_sum = sum(c[1] for c in coords[:n])
        lng_sum = sum(c[0] for c in coords[:n])

        return {
            "lat": lat_sum / n,
            "lng": lng_sum / n,
        }

    @staticmethod
    def _calculate_area(boundary: dict) -> float:
        """Calculate area of polygon using Shoelace formula."""
        coords = boundary["coordinates"][0]
        n = len(coords) - 1

        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]

        return abs(area) / 2

    @staticmethod
    def _is_valid_boundary(boundary: dict) -> bool:
        """Validate boundary polygon."""
        coords = boundary.get("coordinates", [[]])[0]

        if len(coords) < 4:
            return False

        # Check if polygon is closed
        return coords[0] == coords[-1]


class TestFieldNDVIHistory:
    """Test suite for field NDVI history operations."""

    @pytest.fixture
    def field_with_history(self):
        """Create a field with NDVI history."""
        return {
            "id": "field-1",
            "name": "Test Field",
            "ndvi_history": [
                {"date": "2024-01-01", "mean": 0.65, "min": 0.45, "max": 0.80},
                {"date": "2024-01-15", "mean": 0.68, "min": 0.50, "max": 0.82},
                {"date": "2024-02-01", "mean": 0.55, "min": 0.35, "max": 0.70},
                {"date": "2024-02-15", "mean": 0.60, "min": 0.40, "max": 0.75},
            ],
        }

    def test_add_ndvi_record(self, field_with_history):
        """Test adding NDVI record to history."""
        new_record = {"date": "2024-03-01", "mean": 0.70, "min": 0.55, "max": 0.85}

        updated = self._add_ndvi_record(field_with_history, new_record)

        assert len(updated["ndvi_history"]) == 5
        assert updated["ndvi_history"][-1]["date"] == "2024-03-01"

    def test_get_ndvi_trend(self, field_with_history):
        """Test calculating NDVI trend."""
        trend = self._calculate_trend(field_with_history["ndvi_history"])

        assert "direction" in trend
        assert "change_percent" in trend
        assert trend["direction"] in ["increasing", "decreasing", "stable"]

    def test_get_latest_ndvi(self, field_with_history):
        """Test getting latest NDVI value."""
        latest = self._get_latest_ndvi(field_with_history)

        assert latest["date"] == "2024-02-15"
        assert latest["mean"] == 0.60

    def test_get_ndvi_average(self, field_with_history):
        """Test calculating average NDVI over period."""
        avg = self._calculate_average(field_with_history["ndvi_history"])

        expected_avg = (0.65 + 0.68 + 0.55 + 0.60) / 4
        assert avg == pytest.approx(expected_avg, rel=0.01)

    @staticmethod
    def _add_ndvi_record(field: dict, record: dict) -> dict:
        """Add NDVI record to field history."""
        return {**field, "ndvi_history": [*field["ndvi_history"], record]}

    @staticmethod
    def _calculate_trend(history: list) -> dict:
        """Calculate NDVI trend from history."""
        if len(history) < 2:
            return {"direction": "stable", "change_percent": 0}

        first = history[0]["mean"]
        last = history[-1]["mean"]
        change = (last - first) / first * 100

        if change > 5:
            direction = "increasing"
        elif change < -5:
            direction = "decreasing"
        else:
            direction = "stable"

        return {"direction": direction, "change_percent": change}

    @staticmethod
    def _get_latest_ndvi(field: dict) -> dict:
        """Get most recent NDVI record."""
        return field["ndvi_history"][-1] if field["ndvi_history"] else None

    @staticmethod
    def _calculate_average(history: list) -> float:
        """Calculate average NDVI from history."""
        if not history:
            return 0
        return sum(r["mean"] for r in history) / len(history)


class TestFieldCropRotation:
    """Test suite for field crop rotation."""

    def test_update_crop_type(self):
        """Test updating field crop type."""
        field = {
            "id": "field-1",
            "crop_type": "wheat",
            "crop_history": [
                {"crop": "barley", "start": "2023-01-01", "end": "2023-06-01"}
            ],
        }

        updated = self._update_crop(field, "corn", "2024-03-01")

        assert updated["crop_type"] == "corn"
        assert len(updated["crop_history"]) == 2
        assert updated["crop_history"][-1]["crop"] == "wheat"

    def test_get_crop_history(self):
        """Test retrieving crop rotation history."""
        field = {
            "id": "field-1",
            "crop_history": [
                {"crop": "wheat", "start": "2023-01", "end": "2023-06"},
                {"crop": "corn", "start": "2023-07", "end": "2023-12"},
            ],
        }

        history = self._get_crop_history(field)

        assert len(history) == 2
        assert history[0]["crop"] == "wheat"

    @staticmethod
    def _update_crop(field: dict, new_crop: str, start_date: str) -> dict:
        """Update field crop type and record history."""
        current_crop = field.get("crop_type")
        crop_history = field.get("crop_history", [])

        if current_crop:
            crop_history.append(
                {
                    "crop": current_crop,
                    "start": crop_history[-1]["end"] if crop_history else None,
                    "end": start_date,
                }
            )

        return {
            **field,
            "crop_type": new_crop,
            "crop_history": crop_history,
        }

    @staticmethod
    def _get_crop_history(field: dict) -> list:
        """Get crop rotation history."""
        return field.get("crop_history", [])
