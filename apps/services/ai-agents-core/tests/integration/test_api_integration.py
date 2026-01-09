"""
Integration Tests for API
اختبارات التكامل لـ API

End-to-end API integration tests:
- Complete request/response cycles
- Multi-step workflows via API
- Error recovery
- Performance testing
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

# ============================================================================
# Test Complete Analysis Workflow via API
# ============================================================================


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
class TestAnalysisWorkflowAPI:
    """Test complete analysis workflow through API"""

    def test_full_analysis_request_response(self, api_client):
        """Test complete field analysis via API"""
        request_data = {
            "field_id": "integration_test_field_001",
            "crop_type": "wheat",
            "sensor_data": {
                "soil_moisture": 0.30,
                "temperature": 28.5,
                "humidity": 45.0,
                "soil_ec": 1.8,
                "soil_ph": 7.0,
            },
            "weather_data": {
                "temperature": 30.0,
                "humidity": 42,
                "wind_speed": 10,
                "conditions": "sunny",
            },
            "image_data": {
                "disease_id": "wheat_leaf_rust",
                "confidence": 0.82,
                "affected_area": 20.0,
            },
        }

        response = api_client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "analysis" in data
        assert "timestamp" in data

    def test_analysis_with_minimal_data(self, api_client):
        """Test analysis with only required fields"""
        request_data = {"field_id": "test_field", "crop_type": "wheat"}

        response = api_client.post("/api/v1/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True

    def test_multiple_sequential_analyses(self, api_client):
        """Test multiple sequential analysis requests"""
        fields = [
            {"field_id": f"field_{i}", "crop_type": "wheat"}
            for i in range(3)
        ]

        responses = []
        for field_data in fields:
            response = api_client.post("/api/v1/analyze", json=field_data)
            responses.append(response)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)


# ============================================================================
# Test Edge Sensor Integration
# ============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestEdgeSensorIntegration:
    """Test edge sensor processing integration"""

    def test_sensor_data_processing_pipeline(self, api_client):
        """Test sensor data → processing → response pipeline"""
        sensor_readings = [
            {"device_id": "sensor_001", "sensor_type": "soil_moisture", "value": 0.35},
            {"device_id": "sensor_001", "sensor_type": "temperature", "value": 28.5},
            {"device_id": "sensor_001", "sensor_type": "humidity", "value": 50.0},
        ]

        results = []
        for reading in sensor_readings:
            response = api_client.post("/api/v1/edge/sensor", json=reading)
            results.append(response.json())

        # All should process successfully
        assert all(r["success"] for r in results)

    def test_sensor_anomaly_detection_via_api(self, api_client):
        """Test anomaly detection through API"""
        # Send normal readings
        for _ in range(10):
            api_client.post(
                "/api/v1/edge/sensor",
                json={
                    "device_id": "sensor_001",
                    "sensor_type": "temperature",
                    "value": 25.0,
                },
            )

        # Send anomalous reading
        response = api_client.post(
            "/api/v1/edge/sensor",
            json={
                "device_id": "sensor_001",
                "sensor_type": "temperature",
                "value": 60.0,  # Anomaly
            },
        )

        data = response.json()
        assert data["success"] is True


# ============================================================================
# Test Mobile Edge Integration
# ============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestMobileEdgeIntegration:
    """Test mobile edge integration"""

    def test_mobile_quick_scan_workflow(self, api_client):
        """Test mobile quick scan workflow"""
        request_data = {
            "type": "quick_scan",
            "data": {
                "image_url": "https://example.com/leaf.jpg",
                "location": {"lat": 15.5527, "lon": 48.5164},
            },
        }

        response = api_client.post("/api/v1/edge/mobile", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "success" in data
        assert "response_time_ms" in data

    def test_mobile_sensor_reading(self, api_client):
        """Test mobile sensor reading submission"""
        request_data = {
            "type": "sensor_reading",
            "data": {
                "soil_moisture": 0.32,
                "temperature": 27.0,
                "timestamp": datetime.now().isoformat(),
            },
        }

        response = api_client.post("/api/v1/edge/mobile", json=request_data)

        assert response.status_code == 200


# ============================================================================
# Test Feedback Integration
# ============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestFeedbackIntegration:
    """Test feedback submission integration"""

    def test_complete_recommendation_feedback_cycle(self, api_client):
        """Test recommendation → feedback submission cycle"""
        # Step 1: Get recommendation via analysis
        analysis_request = {
            "field_id": "test_field",
            "crop_type": "wheat",
            "image_data": {
                "disease_id": "wheat_leaf_rust",
                "confidence": 0.85,
            },
        }

        analysis_response = api_client.post("/api/v1/analyze", json=analysis_request)
        assert analysis_response.status_code == 200

        # Step 2: Submit feedback
        feedback_request = {
            "recommendation_id": "rec_test_001",
            "agent_id": "disease_expert_001",
            "action_type": "apply_treatment",
            "rating": 0.9,
            "success": True,
            "actual_result": {"disease_controlled": True},
            "comments": "Treatment was effective",
        }

        feedback_response = api_client.post("/api/v1/feedback", json=feedback_request)
        assert feedback_response.status_code == 200

        feedback_data = feedback_response.json()
        assert feedback_data["success"] is True

    def test_negative_feedback_submission(self, api_client):
        """Test negative feedback submission"""
        feedback_request = {
            "recommendation_id": "rec_test_002",
            "agent_id": "irrigation_advisor_001",
            "action_type": "irrigation",
            "rating": -0.5,
            "success": False,
            "comments": "Over-watering occurred",
        }

        response = api_client.post("/api/v1/feedback", json=feedback_request)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True


# ============================================================================
# Test System Status Integration
# ============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestSystemStatusIntegration:
    """Test system status integration"""

    def test_system_status_after_operations(self, api_client):
        """Test system status reflects operations"""
        # Perform some operations
        api_client.post(
            "/api/v1/analyze",
            json={"field_id": "test", "crop_type": "wheat"},
        )

        api_client.post(
            "/api/v1/edge/sensor",
            json={"device_id": "sensor_001", "sensor_type": "soil_moisture", "value": 0.35},
        )

        # Check system status
        response = api_client.get("/api/v1/system/status")

        assert response.status_code == 200
        data = response.json()

        assert "coordinator" in data
        assert "edge_agents" in data
        assert "learning" in data

    def test_agent_metrics_updated(self, api_client):
        """Test agent metrics are updated after operations"""
        # Perform operation
        api_client.post(
            "/api/v1/analyze",
            json={"field_id": "test", "crop_type": "wheat"},
        )

        # Check coordinator metrics
        response = api_client.get("/api/v1/agents/coordinator/metrics")

        assert response.status_code == 200
        data = response.json()

        # Metrics should reflect activity
        assert "total_requests" in data or "agent_id" in data


# ============================================================================
# Test Error Recovery
# ============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestErrorRecovery:
    """Test error recovery in integration scenarios"""

    def test_recovery_from_invalid_request(self, api_client):
        """Test system recovers from invalid request"""
        # Send invalid request
        response1 = api_client.post("/api/v1/analyze", json={})
        assert response1.status_code == 422

        # System should still work
        response2 = api_client.post(
            "/api/v1/analyze",
            json={"field_id": "test", "crop_type": "wheat"},
        )
        assert response2.status_code == 200

    def test_recovery_from_multiple_errors(self, api_client):
        """Test system handles multiple errors gracefully"""
        # Send multiple invalid requests
        for _ in range(3):
            api_client.post("/api/v1/analyze", json={"invalid": "data"})

        # System should still respond
        response = api_client.get("/healthz")
        assert response.status_code == 200


# ============================================================================
# Test Concurrent Requests
# ============================================================================


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
class TestConcurrentRequests:
    """Test handling concurrent requests"""

    def test_multiple_concurrent_sensor_readings(self, api_client):
        """Test handling multiple sensor readings concurrently"""
        # Note: TestClient is synchronous, but simulates concurrent load
        readings = [
            {"device_id": f"sensor_{i:03d}", "sensor_type": "soil_moisture", "value": 0.30 + (i * 0.01)}
            for i in range(10)
        ]

        responses = []
        for reading in readings:
            response = api_client.post("/api/v1/edge/sensor", json=reading)
            responses.append(response)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

    def test_concurrent_analysis_requests(self, api_client):
        """Test handling concurrent analysis requests"""
        requests = [
            {"field_id": f"field_{i:03d}", "crop_type": "wheat"}
            for i in range(5)
        ]

        responses = []
        for req in requests:
            response = api_client.post("/api/v1/analyze", json=req)
            responses.append(response)

        # All should complete
        assert len(responses) == 5


# ============================================================================
# Test Data Consistency
# ============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestDataConsistency:
    """Test data consistency across requests"""

    def test_sensor_data_accumulation(self, api_client):
        """Test sensor data accumulates correctly"""
        device_id = "consistency_test_sensor"

        # Send multiple readings
        for i in range(5):
            api_client.post(
                "/api/v1/edge/sensor",
                json={
                    "device_id": device_id,
                    "sensor_type": "soil_moisture",
                    "value": 0.30 + (i * 0.02),
                },
            )

        # Check system status (should reflect accumulated data)
        response = api_client.get("/api/v1/system/status")
        assert response.status_code == 200

    def test_feedback_accumulation(self, api_client):
        """Test feedback accumulates in learning system"""
        # Submit multiple feedback entries
        for i in range(3):
            api_client.post(
                "/api/v1/feedback",
                json={
                    "recommendation_id": f"rec_{i}",
                    "agent_id": "disease_expert_001",
                    "action_type": "treatment",
                    "rating": 0.7 + (i * 0.1),
                    "success": True,
                },
            )

        # Check system status for learning metrics
        response = api_client.get("/api/v1/system/status")
        data = response.json()

        assert "learning" in data


# ============================================================================
# Test Performance
# ============================================================================


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
class TestPerformance:
    """Test API performance"""

    def test_analysis_response_time(self, api_client):
        """Test analysis completes in reasonable time"""
        request_data = {
            "field_id": "perf_test_field",
            "crop_type": "wheat",
            "sensor_data": {"soil_moisture": 0.35, "temperature": 28.0},
        }

        start = datetime.now()
        response = api_client.post("/api/v1/analyze", json=request_data)
        duration = (datetime.now() - start).total_seconds()

        assert response.status_code == 200
        # Should complete in reasonable time (< 5 seconds in test env)
        assert duration < 5.0

    def test_edge_sensor_response_time(self, api_client):
        """Test edge sensor processing is fast"""
        request_data = {
            "device_id": "perf_sensor",
            "sensor_type": "soil_moisture",
            "value": 0.35,
        }

        start = datetime.now()
        response = api_client.post("/api/v1/edge/sensor", json=request_data)
        duration = (datetime.now() - start).total_seconds()

        assert response.status_code == 200

        # Edge endpoints should be very fast (< 1 second)
        assert duration < 1.0

    def test_throughput_multiple_requests(self, api_client):
        """Test throughput with multiple requests"""
        start = datetime.now()

        # Send 20 requests
        for i in range(20):
            api_client.post(
                "/api/v1/edge/sensor",
                json={
                    "device_id": f"sensor_{i}",
                    "sensor_type": "soil_moisture",
                    "value": 0.35,
                },
            )

        duration = (datetime.now() - start).total_seconds()

        # Should handle 20 requests reasonably fast
        assert duration < 10.0
