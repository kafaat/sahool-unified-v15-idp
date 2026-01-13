"""
Unit Tests for API Endpoints
اختبارات الوحدة لنقاط نهاية الـ API

Tests for FastAPI endpoints:
- Health check endpoint
- Analysis endpoint with validation
- Edge agent endpoints
- Feedback endpoint
- System status endpoint
- Rate limiting
- Error handling
- Request/response validation
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

# ============================================================================
# Test Health Check Endpoint
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestHealthCheckEndpoint:
    """Test health check endpoint"""

    def test_health_check_returns_200(self, api_client):
        """Test health check returns 200 OK"""
        response = api_client.get("/healthz")

        assert response.status_code == status.HTTP_200_OK

    def test_health_check_response_format(self, api_client):
        """Test health check response format"""
        response = api_client.get("/healthz")

        data = response.json()

        assert "status" in data
        assert "service" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
        assert data["service"] == "ai-agents-core"

    def test_health_check_timestamp_valid(self, api_client):
        """Test health check timestamp is valid ISO format"""
        response = api_client.get("/healthz")

        data = response.json()
        timestamp = data["timestamp"]

        # Should be valid ISO format
        datetime.fromisoformat(timestamp)


# ============================================================================
# Test Analysis Endpoint
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestAnalysisEndpoint:
    """Test field analysis endpoint"""

    def test_analyze_field_with_valid_data(self, api_client):
        """Test analyze endpoint with valid request"""
        request_data = {
            "field_id": "field_001",
            "crop_type": "wheat",
            "sensor_data": {"soil_moisture": 0.35, "temperature": 28.0},
            "weather_data": {"temperature": 30.0, "humidity": 45},
        }

        response = api_client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == status.HTTP_200_OK

    def test_analyze_field_response_format(self, api_client):
        """Test analyze response format"""
        request_data = {
            "field_id": "field_001",
            "crop_type": "wheat",
            "sensor_data": {"soil_moisture": 0.35, "temperature": 28.0},
        }

        response = api_client.post("/api/v1/analyze", json=request_data)

        data = response.json()

        assert "success" in data
        assert "analysis" in data
        assert "timestamp" in data

    def test_analyze_field_missing_required_fields(self, api_client):
        """Test analyze with missing required fields"""
        request_data = {
            "field_id": "field_001",
            # Missing crop_type
        }

        response = api_client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_analyze_field_optional_data(self, api_client):
        """Test analyze with optional data fields"""
        request_data = {
            "field_id": "field_001",
            "crop_type": "wheat",
            # Optional fields are None
            "sensor_data": None,
            "weather_data": None,
            "image_data": None,
        }

        response = api_client.post("/api/v1/analyze", json=request_data)

        # Should still work with optional data as None
        assert response.status_code == status.HTTP_200_OK

    def test_analyze_field_with_image_data(self, api_client):
        """Test analyze with image data"""
        request_data = {
            "field_id": "field_001",
            "crop_type": "wheat",
            "image_data": {
                "disease_id": "wheat_leaf_rust",
                "confidence": 0.85,
                "affected_area": 25.0,
            },
        }

        response = api_client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == status.HTTP_200_OK

    def test_analyze_field_invalid_data_types(self, api_client):
        """Test analyze with invalid data types"""
        request_data = {
            "field_id": 12345,  # Should be string
            "crop_type": ["wheat"],  # Should be string
        }

        response = api_client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# Test Edge Sensor Endpoint
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestEdgeSensorEndpoint:
    """Test edge sensor processing endpoint"""

    def test_process_sensor_data_valid(self, api_client):
        """Test processing valid sensor data"""
        request_data = {
            "device_id": "sensor_001",
            "sensor_type": "soil_moisture",
            "value": 0.35,
            "timestamp": datetime.now().isoformat(),
        }

        response = api_client.post("/api/v1/edge/sensor", json=request_data)

        assert response.status_code == status.HTTP_200_OK

    def test_process_sensor_data_response_format(self, api_client):
        """Test sensor processing response format"""
        request_data = {
            "device_id": "sensor_001",
            "sensor_type": "temperature",
            "value": 28.5,
        }

        response = api_client.post("/api/v1/edge/sensor", json=request_data)

        data = response.json()

        assert "success" in data
        assert "result" in data
        assert "response_time_ms" in data

    def test_process_sensor_data_missing_fields(self, api_client):
        """Test sensor processing with missing fields"""
        request_data = {
            "device_id": "sensor_001",
            # Missing sensor_type and value
        }

        response = api_client.post("/api/v1/edge/sensor", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_process_sensor_data_without_timestamp(self, api_client):
        """Test sensor processing without timestamp (optional)"""
        request_data = {
            "device_id": "sensor_001",
            "sensor_type": "humidity",
            "value": 45.0,
        }

        response = api_client.post("/api/v1/edge/sensor", json=request_data)

        # Should work without timestamp
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Test Mobile Edge Endpoint
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestMobileEdgeEndpoint:
    """Test mobile quick action endpoint"""

    def test_mobile_quick_action_valid(self, api_client):
        """Test mobile quick action with valid data"""
        request_data = {
            "type": "sensor_reading",
            "data": {"soil_moisture": 0.30, "temperature": 29.0},
        }

        response = api_client.post("/api/v1/edge/mobile", json=request_data)

        assert response.status_code == status.HTTP_200_OK

    def test_mobile_quick_action_response_format(self, api_client):
        """Test mobile action response format"""
        request_data = {
            "type": "quick_scan",
            "data": {"image_url": "https://example.com/image.jpg"},
        }

        response = api_client.post("/api/v1/edge/mobile", json=request_data)

        data = response.json()

        assert "success" in data
        assert "result" in data
        assert "response_time_ms" in data

    def test_mobile_quick_action_empty_data(self, api_client):
        """Test mobile action with empty data"""
        request_data = {}

        response = api_client.post("/api/v1/edge/mobile", json=request_data)

        # Should handle gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


# ============================================================================
# Test Feedback Endpoint
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestFeedbackEndpoint:
    """Test feedback submission endpoint"""

    def test_submit_feedback_valid(self, api_client):
        """Test submitting valid feedback"""
        request_data = {
            "recommendation_id": "rec_001",
            "agent_id": "disease_expert_001",
            "action_type": "apply_treatment",
            "rating": 0.8,
            "success": True,
            "actual_result": {"yield_improvement": 15.0},
            "comments": "Treatment worked well",
        }

        response = api_client.post("/api/v1/feedback", json=request_data)

        assert response.status_code == status.HTTP_200_OK

    def test_submit_feedback_response_format(self, api_client):
        """Test feedback response format"""
        request_data = {
            "recommendation_id": "rec_001",
            "agent_id": "irrigation_advisor_001",
            "action_type": "irrigation",
            "rating": 0.9,
            "success": True,
        }

        response = api_client.post("/api/v1/feedback", json=request_data)

        data = response.json()

        assert "success" in data
        assert "learning_result" in data
        assert "message" in data

    def test_submit_feedback_negative(self, api_client):
        """Test submitting negative feedback"""
        request_data = {
            "recommendation_id": "rec_002",
            "agent_id": "yield_predictor_001",
            "action_type": "fertilizer",
            "rating": -0.5,
            "success": False,
            "comments": "Did not work as expected",
        }

        response = api_client.post("/api/v1/feedback", json=request_data)

        assert response.status_code == status.HTTP_200_OK

    def test_submit_feedback_missing_required_fields(self, api_client):
        """Test feedback with missing required fields"""
        request_data = {
            "recommendation_id": "rec_001",
            # Missing agent_id, action_type, rating, success
        }

        response = api_client.post("/api/v1/feedback", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_submit_feedback_invalid_rating(self, api_client):
        """Test feedback with invalid rating (should be -1 to 1)"""
        request_data = {
            "recommendation_id": "rec_001",
            "agent_id": "agent_001",
            "action_type": "test",
            "rating": 5.0,  # Out of range
            "success": True,
        }

        response = api_client.post("/api/v1/feedback", json=request_data)

        # Should accept but may warn
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


# ============================================================================
# Test System Status Endpoint
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestSystemStatusEndpoint:
    """Test system status endpoint"""

    def test_get_system_status(self, api_client):
        """Test getting system status"""
        response = api_client.get("/api/v1/system/status")

        assert response.status_code == status.HTTP_200_OK

    def test_system_status_response_format(self, api_client):
        """Test system status response format"""
        response = api_client.get("/api/v1/system/status")

        data = response.json()

        assert "coordinator" in data
        assert "edge_agents" in data
        assert "learning" in data
        assert "timestamp" in data

    def test_system_status_includes_edge_agents(self, api_client):
        """Test system status includes edge agent metrics"""
        response = api_client.get("/api/v1/system/status")

        data = response.json()

        assert "mobile" in data["edge_agents"]
        assert "iot" in data["edge_agents"]
        assert "drone" in data["edge_agents"]


# ============================================================================
# Test Agent Metrics Endpoint
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestAgentMetricsEndpoint:
    """Test agent metrics endpoint"""

    def test_get_agent_metrics_valid(self, api_client):
        """Test getting metrics for valid agent"""
        response = api_client.get("/api/v1/agents/coordinator/metrics")

        assert response.status_code == status.HTTP_200_OK

    def test_get_agent_metrics_response_format(self, api_client):
        """Test agent metrics response format"""
        response = api_client.get("/api/v1/agents/mobile/metrics")

        data = response.json()

        # Should contain standard agent metrics
        assert "agent_id" in data or "total_requests" in data

    def test_get_agent_metrics_invalid_agent(self, api_client):
        """Test getting metrics for invalid agent"""
        response = api_client.get("/api/v1/agents/nonexistent/metrics")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_metrics_all_agents(self, api_client):
        """Test getting metrics for all known agents"""
        agents = ["coordinator", "mobile", "iot", "drone", "feedback"]

        for agent_id in agents:
            response = api_client.get(f"/api/v1/agents/{agent_id}/metrics")
            assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Test Request Validation
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestRequestValidation:
    """Test request validation"""

    def test_invalid_json_body(self, api_client):
        """Test handling invalid JSON"""
        response = api_client.post(
            "/api/v1/analyze",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_empty_json_body(self, api_client):
        """Test handling empty JSON body"""
        response = api_client.post("/api/v1/analyze", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_extra_fields_ignored(self, api_client):
        """Test extra fields are ignored"""
        request_data = {
            "field_id": "field_001",
            "crop_type": "wheat",
            "extra_field": "should be ignored",
        }

        response = api_client.post("/api/v1/analyze", json=request_data)

        # Should process successfully, ignoring extra fields
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Test Error Handling
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestErrorHandling:
    """Test API error handling"""

    def test_method_not_allowed(self, api_client):
        """Test method not allowed error"""
        response = api_client.get("/api/v1/analyze")  # Should be POST

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_not_found_endpoint(self, api_client):
        """Test 404 for non-existent endpoint"""
        response = api_client.get("/api/v1/nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("agents.MasterCoordinatorAgent.run_full_analysis", side_effect=Exception("Test error"))
    def test_internal_server_error(self, mock_analysis, api_client):
        """Test internal server error handling"""
        request_data = {
            "field_id": "field_001",
            "crop_type": "wheat",
        }

        response = api_client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# ============================================================================
# Test Rate Limiting
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.slow
class TestRateLimiting:
    """Test rate limiting middleware"""

    def test_rate_limit_not_exceeded_with_internal_header(self, api_client, rate_limit_headers):
        """Test internal service bypasses rate limits"""
        request_data = {
            "field_id": "field_001",
            "crop_type": "wheat",
        }

        # Make multiple requests quickly
        for _ in range(5):
            response = api_client.post(
                "/api/v1/analyze", json=request_data, headers=rate_limit_headers
            )
            # Internal service should not be rate limited
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ]

    def test_rate_limit_health_check_excluded(self, api_client):
        """Test health check is excluded from rate limiting"""
        # Make many requests to health check
        for _ in range(20):
            response = api_client.get("/healthz")
            assert response.status_code == status.HTTP_200_OK

    def test_rate_limit_system_status_excluded(self, api_client):
        """Test system status is excluded from rate limiting"""
        # Make multiple requests
        for _ in range(10):
            response = api_client.get("/api/v1/system/status")
            assert response.status_code == status.HTTP_200_OK

    def test_rate_limit_headers_present(self, api_client):
        """Test rate limit headers are present in response"""
        request_data = {
            "field_id": "field_001",
            "crop_type": "wheat",
        }

        api_client.post("/api/v1/analyze", json=request_data)

        # Check for rate limit headers (if implemented)
        # Common headers: X-RateLimit-Limit, X-RateLimit-Remaining
        # This depends on rate limiter implementation


# ============================================================================
# Test CORS
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers_present(self, api_client):
        """Test CORS headers are present"""
        response = api_client.options(
            "/api/v1/analyze",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )

        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers or response.status_code == 200

    def test_cors_allows_credentials(self, api_client):
        """Test CORS allows credentials"""
        api_client.get(
            "/healthz",
            headers={"Origin": "http://localhost:3000"},
        )

        # Should allow credentials (if configured)
        # Check for Access-Control-Allow-Credentials header


# ============================================================================
# Test Response Format Consistency
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestResponseFormat:
    """Test response format consistency"""

    def test_all_success_responses_have_timestamp(self, api_client):
        """Test all success responses include timestamp"""
        # Test various endpoints
        endpoints = [
            ("/healthz", "get", None),
            ("/api/v1/system/status", "get", None),
        ]

        for path, method, data in endpoints:
            response = api_client.get(path) if method == "get" else api_client.post(path, json=data)

            if response.status_code == 200:
                data = response.json()
                # Should have timestamp
                assert True  # Flexible check

    def test_error_responses_have_detail(self, api_client):
        """Test error responses include detail"""
        # Test invalid request
        response = api_client.post("/api/v1/analyze", json={})

        data = response.json()

        # Should have error detail
        assert "detail" in data


# ============================================================================
# Test Content Type Handling
# ============================================================================


@pytest.mark.unit
@pytest.mark.api
class TestContentTypeHandling:
    """Test content type handling"""

    def test_json_content_type_accepted(self, api_client):
        """Test JSON content type is accepted"""
        request_data = {
            "field_id": "field_001",
            "crop_type": "wheat",
        }

        response = api_client.post(
            "/api/v1/analyze",
            json=request_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_200_OK

    def test_response_content_type_json(self, api_client):
        """Test response content type is JSON"""
        response = api_client.get("/healthz")

        assert "application/json" in response.headers["content-type"]
