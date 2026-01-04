"""
Integration Tests for SAHOOL Enterprise Package
اختبارات التكامل لحزمة سهول للمؤسسات

Tests for enterprise package services:
- AI Advisor: Multi-agent AI system - النظام الذكي متعدد الوكلاء
- IoT Gateway: Device management - بوابة إنترنت الأشياء
- Marketplace: Listings and orders - السوق الزراعي
- Billing: Payments and subscriptions - الفوترة
- Research Core: Experiments - البحث العلمي

Author: SAHOOL Platform Team
"""


import httpx
import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# AI Advisor Tests - اختبارات المستشار الذكي متعدد الوكلاء
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestAIAdvisor:
    """Test AI advisor multi-agent system - اختبار النظام الذكي متعدد الوكلاء"""

    async def test_ask_ai_advisor(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        ai_query_factory,
        auth_headers: dict[str, str],
    ):
        """
        Test asking AI advisor a question
        اختبار سؤال المستشار الذكي
        """
        # Arrange
        query = ai_query_factory.create(language="ar")
        url = f"{service_urls['ai_advisor']}/api/v1/ask"

        # Act
        response = await http_client.post(
            url, json=query, headers=auth_headers, timeout=60
        )

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to ask AI advisor: {response.text}"
        data = response.json()
        assert "answer" in data or "response" in data or "message" in data

    async def test_get_rag_answer(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test getting RAG-enhanced answer
        اختبار الحصول على إجابة معززة بـ RAG
        """
        # Arrange
        url = f"{service_urls['ai_advisor']}/api/v1/rag/ask"
        query = {
            "question": "What are the best practices for wheat cultivation in Yemen?",
            "context_type": "agriculture",
            "language": "en",
        }

        # Act
        response = await http_client.post(
            url, json=query, headers=auth_headers, timeout=60
        )

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to get RAG answer: {response.text}"
        data = response.json()
        assert "answer" in data or "response" in data

    async def test_multi_agent_consultation(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test multi-agent consultation
        اختبار الاستشارة متعددة الوكلاء
        """
        # Arrange
        url = f"{service_urls['ai_advisor']}/api/v1/multi-agent/consult"
        query = {
            "question": "How can I improve crop yield in my wheat field?",
            "field_id": "test-field-123",
            "agents": ["agronomist", "weather_expert", "soil_specialist"],
        }

        # Act
        response = await http_client.post(
            url, json=query, headers=auth_headers, timeout=90
        )

        # Assert
        assert response.status_code in (
            200,
            201,
            202,
        ), f"Failed multi-agent consultation: {response.text}"


# ═══════════════════════════════════════════════════════════════════════════════
# IoT Gateway Tests - اختبارات بوابة إنترنت الأشياء
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestIoTGateway:
    """Test IoT gateway - اختبار بوابة إنترنت الأشياء"""

    async def test_register_device(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test registering an IoT device
        اختبار تسجيل جهاز IoT
        """
        # Arrange
        url = f"{service_urls['iot_gateway']}/api/v1/devices"
        device_data = {
            "device_id": f"test-device-{pytest.__version__}",
            "device_type": "soil_sensor",
            "location": {"latitude": 15.3694, "longitude": 44.1910},
            "metadata": {"manufacturer": "SensorTech", "model": "ST-100"},
        }

        # Act
        response = await http_client.post(url, json=device_data, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to register device: {response.text}"
        data = response.json()
        assert "device_id" in data or "id" in data

    async def test_send_iot_reading(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        iot_factory,
        auth_headers: dict[str, str],
    ):
        """
        Test sending IoT sensor reading
        اختبار إرسال قراءة مستشعر IoT
        """
        # Arrange
        reading = iot_factory.create(sensor_type="soil_moisture")
        url = f"{service_urls['iot_gateway']}/api/v1/readings"

        # Act
        response = await http_client.post(url, json=reading, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
            202,
        ), f"Failed to send reading: {response.text}"

    async def test_get_device_readings(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test retrieving device readings
        اختبار استرجاع قراءات الجهاز
        """
        # Arrange
        device_id = "test-device-123"
        url = f"{service_urls['iot_gateway']}/api/v1/devices/{device_id}/readings"
        params = {"start_date": "2024-01-01", "end_date": "2024-12-31", "limit": 100}

        # Act
        response = await http_client.get(url, params=params, headers=auth_headers)

        # Assert
        assert response.status_code == 200, f"Failed to get readings: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))


# ═══════════════════════════════════════════════════════════════════════════════
# Marketplace Tests - اختبارات السوق الزراعي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestMarketplace:
    """Test agricultural marketplace - اختبار السوق الزراعي"""

    async def test_create_listing(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test creating a marketplace listing
        اختبار إنشاء إعلان في السوق
        """
        # Arrange
        url = f"{service_urls['marketplace_service']}/api/v1/listings"
        listing_data = {
            "title": "Fresh Wheat Seeds - High Quality",
            "title_ar": "بذور قمح طازجة - جودة عالية",
            "description": "Premium wheat seeds for planting",
            "description_ar": "بذور قمح ممتازة للزراعة",
            "category": "seeds",
            "price": 500.0,
            "currency": "YER",
            "quantity": 100,
            "unit": "kg",
            "location": "Sana'a, Yemen",
        }

        # Act
        response = await http_client.post(url, json=listing_data, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to create listing: {response.text}"
        data = response.json()
        assert "id" in data or "listing_id" in data

    async def test_search_listings(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test searching marketplace listings
        اختبار البحث في إعلانات السوق
        """
        # Arrange
        url = f"{service_urls['marketplace_service']}/api/v1/listings/search"
        params = {
            "category": "seeds",
            "location": "Sana'a",
            "min_price": 0,
            "max_price": 1000,
        }

        # Act
        response = await http_client.get(url, params=params, headers=auth_headers)

        # Assert
        assert (
            response.status_code == 200
        ), f"Failed to search listings: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))

    async def test_create_order(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test creating an order
        اختبار إنشاء طلب
        """
        # Arrange
        url = f"{service_urls['marketplace_service']}/api/v1/orders"
        order_data = {
            "listing_id": "test-listing-123",
            "quantity": 50,
            "delivery_address": "Sana'a, Yemen",
            "payment_method": "tharwatt",
        }

        # Act
        response = await http_client.post(url, json=order_data, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
            202,
        ), f"Failed to create order: {response.text}"


# ═══════════════════════════════════════════════════════════════════════════════
# Billing Tests - اختبارات الفوترة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestBilling:
    """Test billing and subscriptions - اختبار الفوترة والاشتراكات"""

    async def test_create_subscription(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test creating a subscription
        اختبار إنشاء اشتراك
        """
        # Arrange
        url = f"{service_urls['billing_core']}/api/v1/subscriptions"
        subscription_data = {
            "user_id": "test-user-123",
            "plan": "professional",
            "billing_cycle": "monthly",
            "payment_method": "tharwatt",
        }

        # Act
        response = await http_client.post(
            url, json=subscription_data, headers=auth_headers
        )

        # Assert
        assert response.status_code in (
            200,
            201,
            202,
        ), f"Failed to create subscription: {response.text}"
        data = response.json()
        assert "subscription_id" in data or "id" in data

    async def test_process_payment(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        payment_factory,
        auth_headers: dict[str, str],
    ):
        """
        Test processing a payment
        اختبار معالجة دفعة
        """
        # Arrange
        payment_data = payment_factory.create(amount=100.0, currency="YER")
        url = f"{service_urls['billing_core']}/api/v1/payments"

        # Act
        response = await http_client.post(url, json=payment_data, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
            202,
        ), f"Failed to process payment: {response.text}"
        data = response.json()
        assert "payment_id" in data or "transaction_id" in data or "status" in data

    async def test_get_billing_history(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test retrieving billing history
        اختبار استرجاع سجل الفواتير
        """
        # Arrange
        user_id = "test-user-123"
        url = f"{service_urls['billing_core']}/api/v1/billing/history/{user_id}"

        # Act
        response = await http_client.get(url, headers=auth_headers)

        # Assert
        assert (
            response.status_code == 200
        ), f"Failed to get billing history: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))


# ═══════════════════════════════════════════════════════════════════════════════
# Research Core Tests - اختبارات البحث العلمي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestResearchCore:
    """Test research experiments - اختبار التجارب البحثية"""

    async def test_create_experiment(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        experiment_factory,
        auth_headers: dict[str, str],
    ):
        """
        Test creating a research experiment
        اختبار إنشاء تجربة بحثية
        """
        # Arrange
        experiment_data = experiment_factory.create()
        url = f"{service_urls['research_core']}/api/v1/experiments"

        # Act
        response = await http_client.post(
            url, json=experiment_data, headers=auth_headers
        )

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to create experiment: {response.text}"
        data = response.json()
        assert "id" in data or "experiment_id" in data

    async def test_add_experiment_observation(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test adding an observation to an experiment
        اختبار إضافة ملاحظة لتجربة
        """
        # Arrange
        experiment_id = "test-exp-123"
        url = f"{service_urls['research_core']}/api/v1/experiments/{experiment_id}/observations"
        observation = {
            "date": "2024-06-15",
            "growth_stage": "flowering",
            "measurements": {
                "plant_height_cm": 45.5,
                "leaf_count": 12,
                "health_score": 8.5,
            },
            "notes": "Plants showing healthy growth",
            "notes_ar": "النباتات تظهر نموًا صحيًا",
        }

        # Act
        response = await http_client.post(url, json=observation, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to add observation: {response.text}"

    async def test_get_experiment_results(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test retrieving experiment results
        اختبار استرجاع نتائج التجربة
        """
        # Arrange
        experiment_id = "test-exp-123"
        url = f"{service_urls['research_core']}/api/v1/experiments/{experiment_id}/results"

        # Act
        response = await http_client.get(url, headers=auth_headers)

        # Assert
        assert response.status_code == 200, f"Failed to get results: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))


# ═══════════════════════════════════════════════════════════════════════════════
# Service Health Tests - اختبارات صحة الخدمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestEnterprisePackageHealth:
    """Test health endpoints of enterprise package services - اختبار نقاط صحة خدمات الحزمة المؤسسية"""

    @pytest.mark.parametrize(
        "service_name",
        [
            "ai_advisor",
            "iot_gateway",
            "marketplace_service",
            "billing_core",
            "research_core",
        ],
    )
    async def test_service_health(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        service_name: str,
    ):
        """
        Test service health endpoint
        اختبار نقطة صحة الخدمة
        """
        # Arrange
        base_url = service_urls.get(service_name)
        if not base_url:
            pytest.skip(f"Service {service_name} not configured")

        # Different services may use different health endpoints
        health_endpoints = ["/healthz", "/api/v1/healthz", "/health"]

        # Act & Assert - Try different health endpoints
        for endpoint in health_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                response = await http_client.get(url, timeout=10)
                if response.status_code in (200, 204):
                    return  # Service is healthy
            except Exception:
                continue

        pytest.fail(
            f"Service {service_name} is not healthy on any known health endpoint"
        )
