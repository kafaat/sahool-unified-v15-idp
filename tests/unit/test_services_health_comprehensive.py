"""
Comprehensive Service Health Tests for SAHOOL Platform
اختبارات شاملة لصحة الخدمات لمنصة سهول

Tests cover:
- FastAPI service health endpoint patterns
- Service startup patterns (lifespan)
- Error handler setup verification
- Service configuration patterns
"""

from __future__ import annotations

import importlib
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from shared.errors_py import (
    add_request_id_middleware,
    setup_exception_handlers,
)


@pytest.mark.unit
class TestHealthEndpointPattern:
    """Tests for standard health endpoint implementation"""

    def setup_method(self):
        """Create a service with standard health endpoints"""
        self.app = FastAPI(title="Test Service", version="16.0.0")
        setup_exception_handlers(self.app)
        add_request_id_middleware(self.app)

        @self.app.get("/healthz")
        def health():
            return {"status": "ok", "service": "test-service", "version": "16.0.0"}

        @self.app.get("/readyz")
        def readiness():
            return {
                "status": "ok",
                "database": True,
                "nats": True,
            }

        self.client = TestClient(self.app)

    def test_healthz_returns_200(self):
        """Test /healthz returns 200 OK"""
        response = self.client.get("/healthz")
        assert response.status_code == 200

    def test_healthz_response_format(self):
        """Test /healthz response contains required fields"""
        response = self.client.get("/healthz")
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data

    def test_readyz_returns_200(self):
        """Test /readyz returns 200 OK"""
        response = self.client.get("/readyz")
        assert response.status_code == 200

    def test_readyz_response_format(self):
        """Test /readyz response contains dependency status"""
        response = self.client.get("/readyz")
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert "nats" in data


@pytest.mark.unit
class TestServiceErrorHandlerSetup:
    """Tests for service error handler integration"""

    def setup_method(self):
        """Create a service with error handlers"""
        self.app = FastAPI()
        setup_exception_handlers(self.app)
        add_request_id_middleware(self.app)

        from shared.errors_py import NotFoundException, ValidationException

        @self.app.get("/api/v1/fields/{field_id}")
        async def get_field(field_id: str):
            if field_id == "not-found":
                raise NotFoundException(
                    message="Field not found",
                    message_ar="الحقل غير موجود",
                    resource_type="field",
                    resource_id=field_id,
                )
            return {"id": field_id, "name": "Test Field"}

        @self.app.post("/api/v1/fields")
        async def create_field():
            raise ValidationException(
                message="Field name required",
                message_ar="اسم الحقل مطلوب",
                details={"field": "name"},
            )

        self.client = TestClient(self.app)

    def test_not_found_error_format(self):
        """Test 404 error response matches platform standard"""
        response = self.client.get("/api/v1/fields/not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E1003"
        assert data["error"]["details"]["resource_type"] == "field"
        assert "request_id" in data

    def test_validation_error_format(self):
        """Test 422 validation error format"""
        response = self.client.post("/api/v1/fields")
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E1002"

    def test_successful_response_format(self):
        """Test successful response format"""
        response = self.client.get("/api/v1/fields/field-123")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "field-123"


@pytest.mark.unit
class TestServiceVersionConsistency:
    """Tests for service version consistency"""

    def test_version_format(self):
        """Test that version follows semver format"""
        version = "16.0.0"
        parts = version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_health_endpoint_version_matches(self):
        """Test that health endpoint version matches platform version"""
        app = FastAPI(version="16.0.0")

        @app.get("/healthz")
        def health():
            return {"status": "ok", "version": "16.0.0"}

        client = TestClient(app)
        response = client.get("/healthz")
        data = response.json()
        assert data["version"] == app.version


@pytest.mark.unit
class TestServicePatterns:
    """Tests for common service patterns"""

    def test_cors_middleware_configurable(self):
        """Test that CORS middleware can be configured"""
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://sahool.app"],
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
            allow_credentials=True,
        )

        @app.get("/test")
        def test_endpoint():
            return {"ok": True}

        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200

    def test_api_versioning_pattern(self):
        """Test API versioning with /api/v1/ prefix"""
        from fastapi import APIRouter

        app = FastAPI()
        router = APIRouter(prefix="/api/v1")

        @router.get("/fields")
        def list_fields():
            return {"fields": []}

        app.include_router(router)
        client = TestClient(app)

        response = client.get("/api/v1/fields")
        assert response.status_code == 200

    def test_multiple_error_types_handled(self):
        """Test that all error types are handled correctly"""
        from shared.errors_py import (
            ExternalServiceException,
            ForbiddenException,
            InternalServerException,
            UnauthorizedException,
        )

        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/401")
        async def e401():
            raise UnauthorizedException()

        @app.get("/403")
        async def e403():
            raise ForbiddenException()

        @app.get("/500")
        async def e500():
            raise InternalServerException()

        @app.get("/502")
        async def e502():
            raise ExternalServiceException()

        client = TestClient(app)

        assert client.get("/401").status_code == 401
        assert client.get("/403").status_code == 403
        assert client.get("/500").status_code == 500
        assert client.get("/502").status_code == 502
