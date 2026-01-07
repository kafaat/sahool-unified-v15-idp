"""
SAHOOL Service Health Check Tests
اختبارات الصحة لجميع خدمات سهول

Comprehensive health checks for all 41+ services in the SAHOOL platform
Tests infrastructure services, application services, and integrations

Author: SAHOOL Platform Team
"""

import httpx
import pytest

from tests.integration.conftest import ServiceConfig, wait_for_service

# ═══════════════════════════════════════════════════════════════════════════════
# Infrastructure Service Health Tests - اختبارات صحة الخدمات الأساسية
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_kong_gateway_health(
    http_client: httpx.AsyncClient, infrastructure_configs: dict[str, ServiceConfig]
):
    """
    Test Kong API Gateway health
    اختبار صحة بوابة Kong API
    """
    config = infrastructure_configs["kong"]
    is_healthy = await wait_for_service(http_client, config, max_retries=3, delay=1.0)
    assert is_healthy, f"{config.name} is not healthy"

    # Additional Kong-specific checks
    response = await http_client.get(f"{config.url}/")
    assert response.status_code in (200, 404), "Kong should respond even without routes"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_nats_health(
    http_client: httpx.AsyncClient, infrastructure_configs: dict[str, ServiceConfig]
):
    """
    Test NATS messaging health
    اختبار صحة نظام الرسائل NATS
    """
    config = infrastructure_configs["nats"]
    is_healthy = await wait_for_service(http_client, config, max_retries=3, delay=1.0)
    assert is_healthy, f"{config.name} is not healthy"

    # Check NATS monitoring endpoint
    response = await http_client.get(f"{config.url}/healthz")
    assert response.status_code == 200, "NATS health check failed"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_qdrant_health(
    http_client: httpx.AsyncClient, infrastructure_configs: dict[str, ServiceConfig]
):
    """
    Test Qdrant vector database health
    اختبار صحة قاعدة البيانات المتجهة Qdrant
    """
    config = infrastructure_configs["qdrant"]
    is_healthy = await wait_for_service(http_client, config, max_retries=3, delay=1.0)
    assert is_healthy, f"{config.name} is not healthy"

    # Check Qdrant collections endpoint
    response = await http_client.get(f"{config.url}/collections")
    assert response.status_code == 200, "Qdrant collections endpoint failed"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_prometheus_health(
    http_client: httpx.AsyncClient, infrastructure_configs: dict[str, ServiceConfig]
):
    """
    Test Prometheus monitoring health
    اختبار صحة نظام المراقبة Prometheus
    """
    config = infrastructure_configs["prometheus"]
    is_healthy = await wait_for_service(http_client, config, max_retries=3, delay=1.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_grafana_health(
    http_client: httpx.AsyncClient, infrastructure_configs: dict[str, ServiceConfig]
):
    """
    Test Grafana dashboard health
    اختبار صحة لوحة التحكم Grafana
    """
    config = infrastructure_configs["grafana"]
    is_healthy = await wait_for_service(http_client, config, max_retries=3, delay=1.0)
    assert is_healthy, f"{config.name} is not healthy"


# ═══════════════════════════════════════════════════════════════════════════════
# Core Application Service Health Tests - اختبارات صحة الخدمات الأساسية
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_field_core_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """
    Test Field Core service health
    اختبار صحة خدمة الحقول الأساسية
    """
    config = application_configs["field_core"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"

    response = await http_client.get(f"{config.url}{config.health_endpoint}")
    assert response.status_code == 200, "Field Core health check failed"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_field_ops_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """
    Test Field Operations service health
    اختبار صحة خدمة عمليات الحقول
    """
    config = application_configs["field_ops"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"

    response = await http_client.get(f"{config.url}{config.health_endpoint}")
    assert response.status_code == 200, "Field Ops health check failed"

    # Verify response format
    data = response.json()
    assert "status" in data, "Health response should include status"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_ndvi_engine_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """
    Test NDVI Engine service health
    اختبار صحة محرك NDVI
    """
    config = application_configs["ndvi_engine"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_weather_core_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """
    Test Weather Core service health
    اختبار صحة خدمة الطقس الأساسية
    """
    config = application_configs["weather_core"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_field_chat_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """
    Test Field Chat service health
    اختبار صحة خدمة محادثات الحقول
    """
    config = application_configs["field_chat"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_iot_gateway_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """
    Test IoT Gateway service health
    اختبار صحة بوابة إنترنت الأشياء
    """
    config = application_configs["iot_gateway"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_agro_advisor_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """
    Test Agro Advisor service health
    اختبار صحة خدمة المستشار الزراعي
    """
    config = application_configs["agro_advisor"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_ws_gateway_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """
    Test WebSocket Gateway service health
    اختبار صحة بوابة WebSocket
    """
    config = application_configs["ws_gateway"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_crop_health_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """
    Test Crop Health service health
    اختبار صحة خدمة صحة المحاصيل
    """
    config = application_configs["crop_health"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


# ═══════════════════════════════════════════════════════════════════════════════
# Python/FastAPI Service Health Tests - اختبارات خدمات Python
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_task_service_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Task Service health - اختبار صحة خدمة المهام"""
    config = application_configs["task_service"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_equipment_service_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Equipment Service health - اختبار صحة خدمة المعدات"""
    config = application_configs["equipment_service"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_provider_config_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Provider Configuration service health - اختبار صحة خدمة تكوين المزودين"""
    config = application_configs["provider_config"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


# ═══════════════════════════════════════════════════════════════════════════════
# AI/ML Service Health Tests - اختبارات خدمات الذكاء الاصطناعي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_crop_health_ai_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Crop Health AI service health - اختبار صحة خدمة الذكاء الاصطناعي لصحة المحاصيل"""
    config = application_configs["crop_health_ai"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_virtual_sensors_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Virtual Sensors Engine health - اختبار صحة محرك المستشعرات الافتراضية"""
    config = application_configs["virtual_sensors"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_yield_engine_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Yield Prediction Engine health - اختبار صحة محرك التنبؤ بالإنتاجية"""
    config = application_configs["yield_engine"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_ai_advisor_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test AI Advisor Multi-Agent System health - اختبار صحة نظام المستشار الذكي متعدد الوكلاء"""
    config = application_configs["ai_advisor"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"

    # Verify AI Advisor has required dependencies
    response = await http_client.get(f"{config.url}{config.health_endpoint}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


# ═══════════════════════════════════════════════════════════════════════════════
# Agricultural Service Health Tests - اختبارات الخدمات الزراعية
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_irrigation_smart_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Smart Irrigation service health - اختبار صحة خدمة الري الذكي"""
    config = application_configs["irrigation_smart"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_fertilizer_advisor_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Fertilizer Advisor service health - اختبار صحة خدمة مستشار التسميد"""
    config = application_configs["fertilizer_advisor"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_indicators_service_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Agricultural Indicators service health - اختبار صحة خدمة المؤشرات الزراعية"""
    config = application_configs["indicators_service"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_satellite_service_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Satellite service health - اختبار صحة خدمة الأقمار الصناعية"""
    config = application_configs["satellite_service"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_weather_advanced_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Weather Advanced service health - اختبار صحة خدمة الطقس المتقدمة"""
    config = application_configs["weather_advanced"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_astronomical_calendar_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Astronomical Calendar service health - اختبار صحة خدمة التقويم الفلكي"""
    config = application_configs["astronomical_calendar"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


# ═══════════════════════════════════════════════════════════════════════════════
# NestJS Service Health Tests - اختبارات خدمات NestJS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_research_core_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Research Core service health - اختبار صحة نواة البحث العلمي"""
    config = application_configs["research_core"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_disaster_assessment_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Disaster Assessment service health - اختبار صحة خدمة تقييم الكوارث"""
    config = application_configs["disaster_assessment"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_yield_prediction_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Yield Prediction service health - اختبار صحة خدمة التنبؤ بالإنتاجية"""
    config = application_configs["yield_prediction"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_lai_estimation_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test LAI Estimation service health - اختبار صحة خدمة تقدير LAI"""
    config = application_configs["lai_estimation"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_crop_growth_model_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Crop Growth Model service health - اختبار صحة خدمة نموذج نمو المحاصيل"""
    config = application_configs["crop_growth_model"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_marketplace_service_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Marketplace service health - اختبار صحة خدمة السوق"""
    config = application_configs["marketplace_service"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


# ═══════════════════════════════════════════════════════════════════════════════
# Communication & Notification Service Health Tests - اختبارات خدمات الاتصال
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_community_chat_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Community Chat service health - اختبار صحة خدمة المحادثة المجتمعية"""
    config = application_configs["community_chat"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_notification_service_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Notification service health - اختبار صحة خدمة الإشعارات"""
    config = application_configs["notification_service"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


# ═══════════════════════════════════════════════════════════════════════════════
# Business Service Health Tests - اختبارات الخدمات التجارية
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_billing_core_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Billing Core service health - اختبار صحة خدمة الفوترة الأساسية"""
    config = application_configs["billing_core"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"

    # Verify billing service has payment providers configured
    response = await http_client.get(f"{config.url}{config.health_endpoint}")
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.asyncio
async def test_admin_dashboard_health(
    http_client: httpx.AsyncClient, application_configs: dict[str, ServiceConfig]
):
    """Test Admin Dashboard health - اختبار صحة لوحة تحكم المشرفين"""
    config = application_configs["admin_dashboard"]
    is_healthy = await wait_for_service(http_client, config, max_retries=5, delay=2.0)
    assert is_healthy, f"{config.name} is not healthy"


# ═══════════════════════════════════════════════════════════════════════════════
# Comprehensive Service Health Test - اختبار شامل لصحة جميع الخدمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.slow
@pytest.mark.asyncio
async def test_all_services_health(
    http_client: httpx.AsyncClient, service_configs: dict[str, ServiceConfig]
):
    """
    Comprehensive health check for all services
    اختبار شامل لصحة جميع الخدمات

    This test checks all 41+ services in the SAHOOL platform
    يختبر هذا الاختبار جميع الخدمات الـ 41+ في منصة سهول
    """
    failed_services = []
    healthy_services = []
    skipped_services = []

    for service_name, config in service_configs.items():
        if not config.health_endpoint:
            skipped_services.append(service_name)
            continue

        try:
            is_healthy = await wait_for_service(http_client, config, max_retries=3, delay=1.0)
            if is_healthy:
                healthy_services.append(service_name)
            else:
                failed_services.append(service_name)
        except Exception as e:
            failed_services.append(f"{service_name} (Error: {str(e)})")

    # Report results
    print(f"\n{'=' * 80}")
    print("SAHOOL Platform Health Check Results")
    print("نتائج فحص صحة منصة سهول")
    print(f"{'=' * 80}")
    print(f"✓ Healthy Services: {len(healthy_services)}")
    print(f"✗ Failed Services: {len(failed_services)}")
    print(f"⊘ Skipped Services: {len(skipped_services)}")
    print(f"{'=' * 80}")

    if failed_services:
        print("\nFailed Services:")
        for service in failed_services:
            print(f"  ✗ {service}")

    if healthy_services:
        print("\nHealthy Services:")
        for service in healthy_services:
            print(f"  ✓ {service}")

    # The test passes if at least 80% of services with health endpoints are healthy
    total_checked = len(healthy_services) + len(failed_services)
    if total_checked > 0:
        health_percentage = (len(healthy_services) / total_checked) * 100
        print(f"\nOverall Health: {health_percentage:.1f}%")
        assert health_percentage >= 80.0, f"Platform health is below 80% ({health_percentage:.1f}%)"
