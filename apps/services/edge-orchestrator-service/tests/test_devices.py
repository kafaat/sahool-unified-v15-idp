# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Tests for device management endpoints.

اختبارات لنقاط نهاية إدارة الأجهزة.
"""

from uuid import uuid4

import pytest

try:
    from fastapi.testclient import TestClient

    from src.main import app
except ImportError:
    pytest.skip("edge-orchestrator-service dependencies not installed", allow_module_level=True)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def tenant_id():
    """Default tenant ID for tests."""
    return "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def sample_device_data(tenant_id):
    """Sample device creation data."""
    return {
        "name": "Test Jetson Orin Nano",
        "name_ar": "جهاز جيتسون أورين نانو للاختبار",
        "description": "Test edge device for unit tests",
        "description_ar": "جهاز حافة للاختبار",
        "device_type": "jetson_orin_nano",
        "farm_id": str(uuid4()),
        "ip_address": "192.168.1.100",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "serial_number": "TEST-001",
        "tags": ["test", "development"],
    }


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_healthz(self, client):
        """Test liveness probe."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "edge-orchestrator-service"

    def test_readyz(self, client):
        """Test readiness probe."""
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert "nats" in data

    def test_health(self, client):
        """Test combined health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "connections" in data
        assert "devices" in data


class TestDeviceEndpoints:
    """Test device management endpoints."""

    def test_list_devices_empty(self, client, tenant_id):
        """Test listing devices when none exist."""
        response = client.get(
            "/api/v1/edge/devices",
            headers={"X-Tenant-ID": tenant_id},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 0
        assert "items" in data

    def test_create_device(self, client, tenant_id, sample_device_data):
        """Test creating a new device."""
        response = client.post(
            "/api/v1/edge/devices",
            json=sample_device_data,
            headers={"X-Tenant-ID": tenant_id},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_device_data["name"]
        assert data["device_type"] == sample_device_data["device_type"]
        assert "id" in data

    def test_get_device_not_found(self, client, tenant_id):
        """Test getting a non-existent device."""
        response = client.get(
            f"/api/v1/edge/devices/{uuid4()}",
            headers={"X-Tenant-ID": tenant_id},
        )
        assert response.status_code == 404

    def test_create_device_invalid_mac(self, client, tenant_id, sample_device_data):
        """Test creating device with invalid MAC address."""
        sample_device_data["mac_address"] = "invalid-mac"
        response = client.post(
            "/api/v1/edge/devices",
            json=sample_device_data,
            headers={"X-Tenant-ID": tenant_id},
        )
        assert response.status_code == 422  # Validation error


class TestJobEndpoints:
    """Test job management endpoints."""

    def test_list_jobs(self, client, tenant_id):
        """Test listing all jobs."""
        response = client.get(
            "/api/v1/edge/jobs",
            headers={"X-Tenant-ID": tenant_id},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_job_not_found(self, client, tenant_id):
        """Test getting a non-existent job."""
        response = client.get(
            f"/api/v1/edge/jobs/{uuid4()}",
            headers={"X-Tenant-ID": tenant_id},
        )
        assert response.status_code == 404


class TestSyncEndpoints:
    """Test sync and deploy endpoints."""

    def test_list_models(self, client):
        """Test listing available models."""
        response = client.get("/api/v1/edge/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "yolo26-s" in data["models"]
        assert "crop-disease-v3" in data["models"]

    def test_get_sync_not_found(self, client, tenant_id):
        """Test getting a non-existent sync operation."""
        response = client.get(
            f"/api/v1/edge/sync/{uuid4()}/status",
            headers={"X-Tenant-ID": tenant_id},
        )
        assert response.status_code == 404

    def test_get_deploy_not_found(self, client, tenant_id):
        """Test getting a non-existent deploy operation."""
        response = client.get(
            f"/api/v1/edge/deploy/{uuid4()}/status",
            headers={"X-Tenant-ID": tenant_id},
        )
        assert response.status_code == 404
