"""
Integration Tests for SAHOOL Professional Package
اختبارات التكامل لحزمة سهول الاحترافية

Tests for professional package services:
- Satellite Service: Imagery retrieval - صور الأقمار الصناعية
- NDVI Engine: Vegetation index analysis - تحليل NDVI
- Crop Health AI: Disease detection - كشف أمراض المحاصيل
- Irrigation Smart: Recommendations - توصيات الري
- Inventory Service: Stock management - إدارة المخزون

Author: SAHOOL Platform Team
"""

import httpx
import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Satellite Imagery Tests - اختبارات صور الأقمار الصناعية
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestSatelliteImagery:
    """Test satellite imagery retrieval - اختبار استرجاع صور الأقمار الصناعية"""

    async def test_get_satellite_imagery(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test retrieving satellite imagery for a field
        اختبار استرجاع صور الأقمار الصناعية لحقل
        """
        # Arrange
        url = f"{service_urls['satellite_service']}/api/v1/imagery"
        query = {
            "bbox": [44.0, 15.0, 44.1, 15.1],  # Bounding box for Yemen
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "cloud_cover_max": 20,
        }

        # Act
        response = await http_client.post(url, json=query, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
            202,
        ), f"Failed to get satellite imagery: {response.text}"
        data = response.json()
        assert isinstance(data, list | dict)

    async def test_get_available_imagery_dates(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test retrieving available imagery dates
        اختبار استرجاع التواريخ المتاحة للصور
        """
        # Arrange
        url = f"{service_urls['satellite_service']}/api/v1/imagery/dates"
        params = {
            "bbox": "44.0,15.0,44.1,15.1",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        }

        # Act
        response = await http_client.get(url, params=params, headers=auth_headers)

        # Assert
        assert response.status_code == 200, f"Failed to get imagery dates: {response.text}"
        data = response.json()
        assert isinstance(data, list | dict)


# ═══════════════════════════════════════════════════════════════════════════════
# NDVI Analysis Tests - اختبارات تحليل NDVI
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestNDVIAnalysis:
    """Test NDVI analysis - اختبار تحليل NDVI"""

    async def test_calculate_ndvi(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test calculating NDVI for a field
        اختبار حساب NDVI لحقل
        """
        # Arrange
        url = f"{service_urls['ndvi_engine']}/api/v1/ndvi/calculate"
        query = {
            "field_id": "test-field-123",
            "date": "2024-06-15",
            "bbox": [44.0, 15.0, 44.1, 15.1],
        }

        # Act
        response = await http_client.post(url, json=query, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
            202,
        ), f"Failed to calculate NDVI: {response.text}"
        data = response.json()
        assert "ndvi" in data or "value" in data or "status" in data

    async def test_get_ndvi_timeseries(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test getting NDVI time series data
        اختبار الحصول على بيانات NDVI عبر الزمن
        """
        # Arrange
        url = f"{service_urls['ndvi_engine']}/api/v1/ndvi/timeseries"
        params = {
            "field_id": "test-field-123",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        }

        # Act
        response = await http_client.get(url, params=params, headers=auth_headers)

        # Assert
        assert response.status_code == 200, f"Failed to get NDVI timeseries: {response.text}"
        data = response.json()
        assert isinstance(data, list | dict)

    async def test_get_vegetation_health_score(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test getting vegetation health score
        اختبار الحصول على درجة صحة النباتات
        """
        # Arrange
        url = f"{service_urls['ndvi_engine']}/api/v1/ndvi/health"
        params = {"field_id": "test-field-123"}

        # Act
        response = await http_client.get(url, params=params, headers=auth_headers)

        # Assert
        assert response.status_code == 200, f"Failed to get health score: {response.text}"
        data = response.json()
        assert "health_score" in data or "score" in data or "status" in data


# ═══════════════════════════════════════════════════════════════════════════════
# Crop Health AI Tests - اختبارات الذكاء الاصطناعي لصحة المحاصيل
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestCropHealthAI:
    """Test crop health AI detection - اختبار كشف أمراض المحاصيل بالذكاء الاصطناعي"""

    async def test_detect_disease_from_image(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test detecting disease from crop image
        اختبار كشف المرض من صورة المحصول
        """
        # Arrange - Create a dummy image (1x1 pixel red image)
        import io

        from PIL import Image

        img = Image.new("RGB", (100, 100), color="green")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="JPEG")
        img_bytes = img_buffer.getvalue()

        url = f"{service_urls['crop_health_ai']}/api/v1/detect"

        # Prepare multipart/form-data
        files = {"image": ("test_crop.jpg", img_bytes, "image/jpeg")}

        # Act
        response = await http_client.post(
            url,
            files=files,
            headers={
                "Authorization": auth_headers["Authorization"]
            },  # Don't include Content-Type for multipart
        )

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to detect disease: {response.text}"
        data = response.json()
        assert "disease" in data or "prediction" in data or "class" in data

    async def test_get_disease_treatment(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test getting disease treatment recommendations
        اختبار الحصول على توصيات علاج المرض
        """
        # Arrange
        url = f"{service_urls['crop_health_ai']}/api/v1/treatment"
        query = {"disease": "leaf_spot", "crop_type": "wheat", "severity": "moderate"}

        # Act
        response = await http_client.post(url, json=query, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to get treatment: {response.text}"
        data = response.json()
        assert isinstance(data, list | dict)


# ═══════════════════════════════════════════════════════════════════════════════
# Irrigation Smart Tests - اختبارات الري الذكي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestIrrigationSmart:
    """Test smart irrigation recommendations - اختبار توصيات الري الذكي"""

    async def test_get_irrigation_recommendation(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test getting irrigation recommendations
        اختبار الحصول على توصيات الري
        """
        # Arrange
        url = f"{service_urls['irrigation_smart']}/api/v1/recommendations"
        query = {
            "field_id": "test-field-123",
            "crop_type": "wheat",
            "soil_moisture": 45.0,
            "weather_forecast": {
                "temperature": 28.0,
                "humidity": 60.0,
                "rainfall_probability": 20.0,
            },
        }

        # Act
        response = await http_client.post(url, json=query, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to get irrigation recommendation: {response.text}"
        data = response.json()
        assert "recommendation" in data or "should_irrigate" in data or "amount" in data

    async def test_calculate_water_requirement(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test calculating water requirement
        اختبار حساب احتياجات المياه
        """
        # Arrange
        url = f"{service_urls['irrigation_smart']}/api/v1/water-requirement"
        query = {
            "crop_type": "wheat",
            "growth_stage": "flowering",
            "area_hectares": 10.5,
            "soil_type": "loamy",
        }

        # Act
        response = await http_client.post(url, json=query, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to calculate water requirement: {response.text}"
        data = response.json()
        assert "water_requirement" in data or "liters" in data or "amount" in data


# ═══════════════════════════════════════════════════════════════════════════════
# Inventory Management Tests - اختبارات إدارة المخزون
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestInventoryManagement:
    """Test inventory management - اختبار إدارة المخزون"""

    async def test_create_inventory_item(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        inventory_factory,
        auth_headers: dict[str, str],
    ):
        """
        Test creating an inventory item
        اختبار إنشاء عنصر مخزون
        """
        # Arrange
        item_data = inventory_factory.create(item_type="fertilizer")
        url = f"{service_urls['inventory_service']}/api/v1/inventory"

        # Act
        response = await http_client.post(url, json=item_data, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to create inventory item: {response.text}"
        data = response.json()
        assert "id" in data or "item_id" in data

    async def test_update_inventory_quantity(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        inventory_factory,
        auth_headers: dict[str, str],
    ):
        """
        Test updating inventory quantity
        اختبار تحديث كمية المخزون
        """
        # Arrange - Create item first
        item_data = inventory_factory.create()
        create_url = f"{service_urls['inventory_service']}/api/v1/inventory"
        create_response = await http_client.post(create_url, json=item_data, headers=auth_headers)

        if create_response.status_code not in (200, 201):
            pytest.skip("Inventory item creation failed")

        created_item = create_response.json()
        item_id = created_item.get("id") or created_item.get("item_id")

        # Act - Update quantity
        update_url = f"{service_urls['inventory_service']}/api/v1/inventory/{item_id}/quantity"
        update_data = {"quantity": 500, "reason": "restock"}
        response = await http_client.put(update_url, json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            204,
        ), f"Failed to update inventory: {response.text}"

    async def test_get_low_stock_items(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
    ):
        """
        Test retrieving low stock items
        اختبار استرجاع العناصر منخفضة المخزون
        """
        # Arrange
        url = f"{service_urls['inventory_service']}/api/v1/inventory/low-stock"

        # Act
        response = await http_client.get(url, headers=auth_headers)

        # Assert
        assert response.status_code == 200, f"Failed to get low stock items: {response.text}"
        data = response.json()
        assert isinstance(data, list | dict)


# ═══════════════════════════════════════════════════════════════════════════════
# Service Health Tests - اختبارات صحة الخدمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestProfessionalPackageHealth:
    """Test health endpoints of professional package services - اختبار نقاط صحة خدمات الحزمة الاحترافية"""

    @pytest.mark.parametrize(
        "service_name",
        [
            "satellite_service",
            "ndvi_engine",
            "crop_health_ai",
            "irrigation_smart",
            "inventory_service",
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

        url = f"{base_url}/healthz"

        # Act
        response = await http_client.get(url, timeout=10)

        # Assert
        assert response.status_code in (
            200,
            204,
        ), f"Service {service_name} is not healthy: {response.text}"
