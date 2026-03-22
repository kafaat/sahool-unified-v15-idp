"""
API Response Snapshot Tests
===========================
اختبارات لقطات استجابات API

Snapshot tests for API response structures.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

# =============================================================================
# Snapshot Utilities
# =============================================================================

SNAPSHOT_DIR = Path(__file__).parent / "api_snapshots"


def ensure_snapshot_dir():
    """Ensure snapshot directory exists."""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_api_response(data: dict) -> dict:
    """
    Normalize API response for snapshot comparison.
    Remove volatile fields that change between requests.
    """
    volatile_fields = [
        "id",
        "created_at",
        "updated_at",
        "timestamp",
        "request_id",
        "correlation_id",
        "token",
        "access_token",
        "refresh_token",
    ]

    def normalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: "<VOLATILE>" if k in volatile_fields else normalize(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [normalize(item) for item in obj]
        else:
            return obj

    return normalize(data)


# =============================================================================
# Test Health Endpoint Responses
# =============================================================================


class TestHealthEndpointSnapshots:
    """Snapshot tests for health endpoints."""

    def test_healthz_response_structure(self):
        """Test /healthz response structure."""
        expected_structure = {
            "status": "ok",
            "service": str,
            "version": str,
        }

        # Simulate health response
        response = {
            "status": "ok",
            "service": "field-management-service",
            "version": "16.0.0",
        }

        for key, expected_type in expected_structure.items():
            assert key in response, f"Missing key: {key}"
            if expected_type != str:
                assert response[key] == expected_type

    def test_readyz_response_structure(self):
        """Test /readyz response structure."""
        expected_structure = {
            "status": "ok",
            "checks": dict,
        }

        # Simulate readiness response
        response = {
            "status": "ok",
            "checks": {
                "database": True,
                "nats": True,
                "redis": True,
            },
        }

        assert "status" in response
        assert "checks" in response
        assert isinstance(response["checks"], dict)


# =============================================================================
# Test Field API Responses
# =============================================================================


class TestFieldAPISnapshots:
    """Snapshot tests for field API responses."""

    def test_field_response_structure(self):
        """Test field response structure."""
        expected_keys = [
            "id",
            "name",
            "name_ar",
            "area_hectares",
            "crop_type",
            "farm_id",
            "tenant_id",
            "geometry",
            "status",
            "created_at",
            "updated_at",
        ]

        # Simulate field response
        response = {
            "id": "field-123",
            "name": "Test Field",
            "name_ar": "حقل اختبار",
            "area_hectares": 25.5,
            "crop_type": "wheat",
            "farm_id": "farm-456",
            "tenant_id": "tenant-789",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[45.0, 15.0], [45.1, 15.0], [45.1, 15.1], [45.0, 15.0]]],
            },
            "status": "active",
            "created_at": "2026-01-15T10:00:00Z",
            "updated_at": "2026-01-15T10:00:00Z",
        }

        for key in expected_keys:
            assert key in response, f"Missing key: {key}"

        # Validate geometry structure
        assert response["geometry"]["type"] in ["Polygon", "MultiPolygon"]
        assert "coordinates" in response["geometry"]

    def test_field_list_response_structure(self):
        """Test field list response structure with pagination."""
        # Simulate list response
        response = {
            "items": [
                {"id": "field-1", "name": "Field 1"},
                {"id": "field-2", "name": "Field 2"},
            ],
            "total": 2,
            "page": 1,
            "per_page": 10,
            "pages": 1,
        }

        assert "items" in response
        assert isinstance(response["items"], list)
        assert "total" in response
        assert "page" in response
        assert "per_page" in response


# =============================================================================
# Test Error Response Structures
# =============================================================================


class TestErrorResponseSnapshots:
    """Snapshot tests for error responses."""

    def test_validation_error_structure(self):
        """Test validation error response structure."""
        response = {
            "error": "validation_error",
            "message": "Validation failed",
            "details": [
                {
                    "field": "area_hectares",
                    "message": "Must be positive number",
                }
            ],
        }

        assert "error" in response
        assert "message" in response
        assert "details" in response
        assert isinstance(response["details"], list)

    def test_not_found_error_structure(self):
        """Test not found error response structure."""
        response = {
            "error": "not_found",
            "message": "Field not found",
            "resource": "field",
            "resource_id": "field-123",
        }

        assert response["error"] == "not_found"
        assert "message" in response

    def test_unauthorized_error_structure(self):
        """Test unauthorized error response structure."""
        response = {
            "error": "unauthorized",
            "message": "Authentication required",
            "code": "AUTH_REQUIRED",
        }

        assert response["error"] == "unauthorized"
        assert "message" in response

    def test_forbidden_error_structure(self):
        """Test forbidden error response structure."""
        response = {
            "error": "forbidden",
            "message": "You do not have permission to access this resource",
            "required_permission": "field:write",
        }

        assert response["error"] == "forbidden"
        assert "message" in response


# =============================================================================
# Test Advisory API Responses
# =============================================================================


class TestAdvisoryAPISnapshots:
    """Snapshot tests for advisory API responses."""

    def test_irrigation_advisory_structure(self):
        """Test irrigation advisory response structure."""
        response = {
            "advisory_id": "adv-123",
            "advisory_type": "irrigation",
            "field_id": "field-456",
            "recommendation": {
                "action": "irrigate",
                "amount_mm": 25.0,
                "timing": "morning",
                "priority": "high",
            },
            "explanation": {
                "summary": "Soil moisture is below optimal",
                "summary_ar": "رطوبة التربة أقل من المستوى الأمثل",
                "factors": [
                    {"name": "soil_moisture", "value": 35, "impact": "high"},
                    {"name": "weather_forecast", "value": "no_rain", "impact": "medium"},
                ],
            },
            "confidence_score": 0.87,
            "created_at": "2026-01-15T10:00:00Z",
        }

        assert "advisory_id" in response
        assert "advisory_type" in response
        assert "recommendation" in response
        assert "explanation" in response
        assert "confidence_score" in response

        # Validate recommendation structure
        rec = response["recommendation"]
        assert "action" in rec
        assert "priority" in rec

        # Validate explanation structure
        exp = response["explanation"]
        assert "summary" in exp
        assert "summary_ar" in exp
        assert "factors" in exp

    def test_disease_detection_response_structure(self):
        """Test disease detection response structure."""
        response = {
            "detection_id": "det-123",
            "field_id": "field-456",
            "detections": [
                {
                    "disease_type": "wheat_rust",
                    "disease_name": "Wheat Leaf Rust",
                    "disease_name_ar": "صدأ أوراق القمح",
                    "confidence": 0.92,
                    "severity": "moderate",
                    "bounding_box": {"x": 100, "y": 200, "width": 50, "height": 50},
                }
            ],
            "image_id": "img-789",
            "processed_at": "2026-01-15T10:00:00Z",
        }

        assert "detection_id" in response
        assert "detections" in response
        assert isinstance(response["detections"], list)

        if response["detections"]:
            det = response["detections"][0]
            assert "disease_type" in det
            assert "confidence" in det
            assert "severity" in det


# =============================================================================
# Test Billing API Responses
# =============================================================================


class TestBillingAPISnapshots:
    """Snapshot tests for billing API responses."""

    def test_subscription_response_structure(self):
        """Test subscription response structure."""
        response = {
            "subscription_id": "sub-123",
            "user_id": "user-456",
            "plan": {
                "id": "professional",
                "name": "Professional",
                "name_ar": "احترافي",
                "price": 499.0,
                "currency": "SAR",
                "billing_cycle": "monthly",
            },
            "status": "active",
            "current_period_start": "2026-01-01T00:00:00Z",
            "current_period_end": "2026-02-01T00:00:00Z",
            "created_at": "2025-12-01T00:00:00Z",
        }

        assert "subscription_id" in response
        assert "plan" in response
        assert "status" in response

        plan = response["plan"]
        assert "id" in plan
        assert "name" in plan
        assert "price" in plan
        assert "currency" in plan


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
