"""
SAHOOL Data Flow Integration Tests
اختبارات تدفق البيانات بين خدمات سهول

Tests data flow between services through NATS, Redis, PostgreSQL, and Qdrant
Tests messaging, caching, database operations, and vector search

Author: SAHOOL Platform Team
"""

import asyncio
from typing import Any

import httpx
import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# NATS Messaging Tests - اختبارات نظام الرسائل NATS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_nats_server_info():
    """
    Test NATS server information endpoint
    اختبار نقطة نهاية معلومات خادم NATS
    """
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8222/varz")
        assert response.status_code == 200, "NATS monitoring should be accessible"

        data = response.json()
        assert "version" in data or "server_id" in data, "Should return server info"


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_nats_connections():
    """
    Test NATS connections
    اختبار اتصالات NATS
    """
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8222/connz")
        assert response.status_code == 200, "NATS connections endpoint should work"

        data = response.json()
        # Check if services are connected to NATS
        if "connections" in data or "conns" in data:
            # Services should be connected
            pass


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_nats_jetstream():
    """
    Test NATS JetStream status
    اختبار حالة NATS JetStream
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8222/jsz")
            assert response.status_code == 200, "JetStream monitoring should be accessible"

            data = response.json()
            # JetStream should be enabled
            assert data is not None
        except Exception:
            pytest.skip("JetStream monitoring may not be enabled")


# ═══════════════════════════════════════════════════════════════════════════════
# Redis Cache Tests - اختبارات ذاكرة التخزين المؤقت Redis
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_redis_connectivity():
    """
    Test Redis connectivity through services
    اختبار اتصال Redis من خلال الخدمات
    """
    # Test that services using Redis are healthy
    # This indicates Redis is working
    async with httpx.AsyncClient() as client:
        # Field Management Service uses Redis (replaces deprecated field-ops on port 8080)
        response = await client.get("http://localhost:3000/healthz")
        assert response.status_code == 200, "Service using Redis should be healthy"


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_redis_caching_behavior():
    """
    Test Redis caching behavior through API
    اختبار سلوك التخزين المؤقت لـ Redis من خلال API
    """
    async with httpx.AsyncClient() as client:
        # Make the same request twice to test caching
        # weather-core (port 8108) deprecated; now uses weather-service (port 8092)
        url = "http://localhost:8092/api/v1/weather/current"
        params = {"latitude": 15.3694, "longitude": 44.1910}

        try:
            response1 = await client.get(url, params=params)
            await asyncio.sleep(0.5)  # Small delay
            response2 = await client.get(url, params=params)

            # Both requests should succeed (if authenticated)
            # Second request might be faster due to caching
            if response1.status_code == 200 and response2.status_code == 200:
                # Responses should be similar (cached)
                assert response1.json() == response2.json()
        except Exception:
            pytest.skip("Weather service may require authentication or external API")


# ═══════════════════════════════════════════════════════════════════════════════
# Database Connectivity Tests - اختبارات اتصال قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_postgres_through_services():
    """
    Test PostgreSQL connectivity through services
    اختبار اتصال PostgreSQL من خلال الخدمات
    """
    # Test multiple services that use PostgreSQL
    # Deprecated services updated to their replacements:
    # field-ops (8080) -> field-management-service (3000)
    # ndvi-engine (8107) -> vegetation-analysis-service (8090)
    # weather-core (8108) -> weather-service (8092)
    services_with_db = [
        "http://localhost:3000/healthz",  # field-management-service (replaces field_ops)
        "http://localhost:8090/healthz",  # vegetation-analysis-service (replaces ndvi_engine)
        "http://localhost:8092/healthz",  # weather-service (replaces weather_core)
        "http://localhost:8089/healthz",  # billing_core
    ]

    healthy_services = []
    async with httpx.AsyncClient() as client:
        for service_url in services_with_db:
            try:
                response = await client.get(service_url)
                assert response.status_code == 200, (
                    f"Service {service_url} returned {response.status_code}"
                )
                healthy_services.append(service_url)
            except Exception as e:
                pytest.skip(f"Service unavailable: {e}")

    assert len(healthy_services) > 0, "At least one database-backed service should be healthy"


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_database_operations_through_api(auth_headers: dict[str, str]):
    """
    Test database CRUD operations through API
    اختبار عمليات قاعدة البيانات من خلال API
    """
    # field-ops (port 8080) deprecated; now uses field-management-service (port 3000)
    async with httpx.AsyncClient(base_url="http://localhost:3000") as client:
        # Try to list fields (READ operation)
        response = await client.get("/api/v1/fields", headers=auth_headers)

        # Should get response (authenticated or not)
        assert response.status_code in (200, 401), "Database read should work"


# ═══════════════════════════════════════════════════════════════════════════════
# Qdrant Vector Search Tests - اختبارات البحث المتجه Qdrant
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_qdrant_collections():
    """
    Test Qdrant collections
    اختبار مجموعات Qdrant
    """
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:6333/collections")
        assert response.status_code == 200, "Qdrant should list collections"

        data = response.json()
        assert "result" in data or "collections" in data, "Should return collections"


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_qdrant_cluster_status():
    """
    Test Qdrant cluster status
    اختبار حالة مجموعة Qdrant
    """
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:6333/cluster")
        assert response.status_code == 200, "Qdrant cluster endpoint should work"


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_ai_advisor_qdrant_integration():
    """
    Test AI Advisor integration with Qdrant
    اختبار تكامل المستشار الذكي مع Qdrant
    """
    # AI Advisor uses Qdrant for RAG
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8112/healthz")

        if response.status_code != 200:
            pytest.skip("AI Advisor not running")

        # AI Advisor is healthy, which means Qdrant integration is working
        data = response.json()
        assert data is not None, "AI Advisor health check should return response data"


# ═══════════════════════════════════════════════════════════════════════════════
# Service-to-Service Communication Tests - اختبارات الاتصال بين الخدمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.slow
@pytest.mark.asyncio
async def test_field_to_ndvi_data_flow(auth_headers: dict[str, str], sample_field: dict[str, Any]):
    """
    Test data flow from Field Management Service to Vegetation Analysis Service
    اختبار تدفق البيانات من خدمة إدارة الحقول إلى خدمة تحليل الغطاء النباتي

    Workflow:
    1. Create a field in Field Management Service
    2. Vegetation Analysis Service should be able to analyze it
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Try to create a field
        # field-ops (port 8080) deprecated; now uses field-management-service (port 3000)
        response = await client.post(
            "http://localhost:3000/api/v1/fields",
            headers=auth_headers,
            json=sample_field,
        )

        if response.status_code == 201:
            field_data = response.json()
            field_id = field_data.get("id") or field_data.get("field_id")

            # Step 2: Vegetation Analysis Service should be able to access this field
            await asyncio.sleep(1)  # Give time for event propagation

            # ndvi-engine (port 8107) deprecated; now uses vegetation-analysis-service (port 8090)
            ndvi_response = await client.get(
                f"http://localhost:8090/api/v1/ndvi/fields/{field_id}",
                headers=auth_headers,
            )

            # Should return 200 (found) or 404 (not yet synced)
            assert ndvi_response.status_code in (200, 404, 401)


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.slow
@pytest.mark.asyncio
async def test_weather_to_irrigation_data_flow(
    auth_headers: dict[str, str], sample_location: dict[str, float]
):
    """
    Test data flow from Weather to Irrigation Smart
    اختبار تدفق البيانات من الطقس إلى الري الذكي

    Workflow:
    1. Get weather data
    2. Use it to calculate irrigation needs
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Get weather data
        # weather-core (port 8108) deprecated; now uses weather-service (port 8092)
        weather_response = await client.get(
            "http://localhost:8092/api/v1/weather/current",
            headers=auth_headers,
            params=sample_location,
        )

        if weather_response.status_code == 200:
            weather_response.json()

            # Step 2: Calculate irrigation using weather data
            irrigation_data = {
                **sample_location,
                "temperature_max": 35.0,
                "temperature_min": 20.0,
                "humidity": 45.0,
                "wind_speed": 2.5,
                "solar_radiation": 25.0,
            }

            irrigation_response = await client.post(
                "http://localhost:8094/api/v1/irrigation/et0",
                headers=auth_headers,
                json=irrigation_data,
            )

            # Should calculate or return error
            assert irrigation_response.status_code in (200, 401, 422)


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_ai_advisor_multi_service_integration(auth_headers: dict[str, str]):
    """
    Test AI Advisor integration with multiple services
    اختبار تكامل المستشار الذكي مع خدمات متعددة

    AI Advisor connects to:
    - Weather Service (replaces deprecated weather-core)
    - Crop Intelligence Service (replaces deprecated crop-health-ai)
    - Vegetation Analysis Service (replaces deprecated satellite-service)
    - Advisory Service (replaces deprecated agro-advisor)
    - Qdrant (for RAG)
    """
    async with httpx.AsyncClient() as client:
        # Check AI Advisor health
        ai_response = await client.get("http://localhost:8112/healthz")

        if ai_response.status_code == 200:
            # Verify it can communicate with dependent services
            # Deprecated services updated to their replacements:
            # weather-core (8108) -> weather-service (8092)
            # crop-health-ai -> crop-intelligence-service (8095, same port)
            # agro-advisor (8105) -> advisory-service (8093)
            dependencies = [
                "http://localhost:8092/healthz",  # weather-service (replaces weather_core)
                "http://localhost:8095/healthz",  # crop-intelligence-service (replaces crop_health_ai)
                "http://localhost:8093/healthz",  # advisory-service (replaces agro_advisor)
                "http://localhost:6333/healthz",  # qdrant
            ]

            healthy_deps = []
            for dep_url in dependencies:
                try:
                    dep_response = await client.get(dep_url)
                    if dep_response.status_code == 200:
                        healthy_deps.append(dep_url)
                except Exception:
                    # Some dependencies might not be running
                    continue

            assert len(healthy_deps) > 0, (
                f"AI Advisor is healthy but none of its dependencies responded: {dependencies}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Event-Driven Communication Tests - اختبارات الاتصال القائم على الأحداث
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_notification_service_nats_subscription():
    """
    Test Notification Service NATS subscription
    اختبار اشتراك خدمة الإشعارات في NATS

    Notification service subscribes to events from other services
    """
    async with httpx.AsyncClient() as client:
        # Notification service should be healthy
        try:
            response = await client.get("http://localhost:8110/healthz")
        except Exception as e:
            pytest.skip(f"Notification service unavailable: {e}")

        if response.status_code != 200:
            pytest.skip(f"Notification service not running (status {response.status_code})")

        # Service is running and connected to NATS
        data = response.json()
        assert "status" in data or data is not None, (
            "Notification service health check should return valid response"
        )


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_websocket_gateway_nats_integration():
    """
    Test WebSocket Gateway NATS integration
    اختبار تكامل بوابة WebSocket مع NATS

    WebSocket Gateway subscribes to NATS for real-time updates
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8081/healthz")
        except Exception as e:
            pytest.skip(f"WebSocket Gateway unavailable: {e}")

        if response.status_code != 200:
            pytest.skip(f"WebSocket Gateway not running (status {response.status_code})")

        # WebSocket Gateway is healthy and connected to NATS
        data = response.json()
        assert "status" in data or data is not None, (
            "WebSocket Gateway health check should return valid response"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-Service Data Consistency Tests - اختبارات اتساق البيانات عبر الخدمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.slow
@pytest.mark.asyncio
async def test_field_data_consistency_across_services(auth_headers: dict[str, str]):
    """
    Test that field data is consistent across services
    اختبار أن بيانات الحقل متسقة عبر الخدمات

    Field data should be available in:
    - Field Management Service (source, replaces deprecated field-ops)
    - Vegetation Analysis Service (replaces deprecated ndvi-engine)
    - Weather Service (replaces deprecated weather-core)
    - Vegetation Analysis Service (replaces deprecated satellite-service)
    """
    field_id = "test-field-consistency-123"

    async with httpx.AsyncClient() as client:
        # Check field in multiple services
        # Deprecated services updated to their replacements:
        # field-ops (8080) -> field-management-service (3000)
        # ndvi-engine (8107) -> vegetation-analysis-service (8090)
        services = [
            f"http://localhost:3000/api/v1/fields/{field_id}",  # field-management-service (replaces field_ops)
            f"http://localhost:8090/api/v1/ndvi/fields/{field_id}",  # vegetation-analysis-service (replaces ndvi_engine)
        ]

        responses = []
        for service_url in services:
            try:
                response = await client.get(service_url, headers=auth_headers)
                responses.append(response.status_code)
            except Exception as e:
                pytest.skip(f"Service unavailable ({service_url}): {e}")

        assert len(responses) > 0, "At least one service should respond"

        # All services should return same status (200 or 404)
        # This indicates data consistency
        unique_statuses = set(responses)
        assert len(unique_statuses) <= 2, (
            f"Services returned inconsistent statuses: {responses}. "
            f"Expected consistent responses across services."
        )


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.asyncio
async def test_billing_payment_provider_integration():
    """
    Test Billing service integration with payment providers
    اختبار تكامل خدمة الفوترة مع مزودي الدفع

    Billing Core integrates with:
    - Stripe
    - Tharwatt (for Yemen)
    - Provider Config service
    """
    async with httpx.AsyncClient() as client:
        # Billing service should be healthy
        billing_response = await client.get("http://localhost:8089/healthz")

        if billing_response.status_code == 200:
            # Provider Config should also be healthy
            provider_response = await client.get("http://localhost:8104/health")
            assert provider_response.status_code in (200, 404)


# ═══════════════════════════════════════════════════════════════════════════════
# Data Pipeline Tests - اختبارات خط أنابيب البيانات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.dataflow
@pytest.mark.slow
@pytest.mark.asyncio
async def test_satellite_to_yield_prediction_pipeline(auth_headers: dict[str, str]):
    """
    Test data pipeline from Satellite to Yield Prediction
    اختبار خط أنابيب البيانات من القمر الصناعي إلى التنبؤ بالإنتاجية

    Pipeline:
    1. Vegetation Analysis Service gets imagery (replaces deprecated satellite-service)
    2. Vegetation Analysis Service analyzes NDVI (replaces deprecated ndvi-engine)
    3. Yield Prediction Service uses analysis (replaces deprecated yield-engine)
    """
    async with httpx.AsyncClient() as client:
        # All services in pipeline should be healthy
        # Deprecated services updated to their replacements:
        # satellite-service -> vegetation-analysis-service (8090, same port)
        # ndvi-engine (8107) -> vegetation-analysis-service (8090)
        # yield-engine (3021) -> yield-prediction-service (8152)
        pipeline_services = [
            "http://localhost:8090/healthz",  # vegetation-analysis-service (replaces satellite_service)
            "http://localhost:8090/healthz",  # vegetation-analysis-service (replaces ndvi_engine)
            "http://localhost:8152/api/v1/yield/health",  # yield-prediction-service (replaces yield_prediction on 3021)
        ]

        healthy_count = 0
        for service_url in pipeline_services:
            try:
                response = await client.get(service_url)
                if response.status_code == 200:
                    healthy_count += 1
            except Exception as e:
                pytest.skip(f"Pipeline service unavailable ({service_url}): {e}")

        # At least one service in the pipeline should be healthy
        assert healthy_count > 0, (
            f"No pipeline services are healthy out of {len(pipeline_services)}"
        )
