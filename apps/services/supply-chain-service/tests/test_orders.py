"""Tests for order endpoints in Supply Chain Service."""

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_healthz(self, test_client: TestClient) -> None:
        """Test liveness probe endpoint."""
        response = test_client.get("/healthz")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "supply-chain-service"
        assert "version" in data

    def test_readyz(self, test_client: TestClient) -> None:
        """Test readiness probe endpoint."""
        response = test_client.get("/readyz")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "dependencies" in data
        assert "database" in data["dependencies"]
        assert "nats" in data["dependencies"]
        assert "redis" in data["dependencies"]

    def test_health(self, test_client: TestClient) -> None:
        """Test combined health endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "ready" in data
        assert "dependencies" in data

    def test_root(self, test_client: TestClient) -> None:
        """Test root endpoint."""
        response = test_client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "supply-chain-service"
        assert "service_ar" in data
        assert data["docs"] == "/docs"


class TestProductEndpoints:
    """Tests for product endpoints."""

    def test_list_products(self, test_client: TestClient) -> None:
        """Test listing products."""
        response = test_client.get("/api/v1/products")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_list_products_with_category_filter(self, test_client: TestClient) -> None:
        """Test listing products with category filter."""
        response = test_client.get("/api/v1/products?category=fertilizers")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        for item in data["items"]:
            assert item["category"] == "fertilizers"

    def test_search_products(self, test_client: TestClient) -> None:
        """Test searching products."""
        response = test_client.get("/api/v1/products/search?q=urea")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_search_products_requires_query(self, test_client: TestClient) -> None:
        """Test that search requires a query parameter."""
        response = test_client.get("/api/v1/products/search")
        assert response.status_code == 422  # Validation error


class TestSupplierEndpoints:
    """Tests for supplier endpoints."""

    def test_list_suppliers(self, test_client: TestClient) -> None:
        """Test listing suppliers."""
        response = test_client.get("/api/v1/suppliers")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_suppliers_with_rating_filter(self, test_client: TestClient) -> None:
        """Test listing suppliers with minimum rating filter."""
        response = test_client.get("/api/v1/suppliers?min_rating=4.5")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        for item in data["items"]:
            assert item["rating"] >= 4.5

    def test_find_nearby_suppliers(self, test_client: TestClient) -> None:
        """Test finding nearby suppliers."""
        response = test_client.get("/api/v1/suppliers/nearby?latitude=24.7136&longitude=46.6753")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data

    def test_nearby_requires_coordinates(self, test_client: TestClient) -> None:
        """Test that nearby search requires coordinates."""
        response = test_client.get("/api/v1/suppliers/nearby")
        assert response.status_code == 422  # Validation error


class TestOrderEndpoints:
    """Tests for order endpoints."""

    def test_create_order(self, test_client: TestClient, sample_order_data: dict) -> None:
        """Test creating an order."""
        response = test_client.post("/api/v1/orders", json=sample_order_data)
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        assert "items" in data
        assert len(data["items"]) > 0
        assert "total" in data
        assert data["payment_method"] == "cash_on_delivery"

    def test_create_order_validates_items(self, test_client: TestClient) -> None:
        """Test that order creation validates items."""
        invalid_data = {
            "supplier_id": "12345678-1234-1234-1234-123456789abc",
            "items": [],  # Empty items
            "delivery_address": "Test Address",
            "payment_method": "cash_on_delivery",
        }
        response = test_client.post("/api/v1/orders", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_list_orders(self, test_client: TestClient) -> None:
        """Test listing orders."""
        response = test_client.get("/api/v1/orders")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    def test_get_order_not_found(self, test_client: TestClient) -> None:
        """Test getting non-existent order."""
        response = test_client.get("/api/v1/orders/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

        data = response.json()
        assert "message" in data["detail"]
        assert "message_ar" in data["detail"]

    def test_cancel_order_not_found(self, test_client: TestClient) -> None:
        """Test cancelling non-existent order."""
        response = test_client.post("/api/v1/orders/00000000-0000-0000-0000-000000000000/cancel")
        assert response.status_code == 404

    def test_track_order_not_found(self, test_client: TestClient) -> None:
        """Test tracking non-existent order."""
        response = test_client.get("/api/v1/orders/00000000-0000-0000-0000-000000000000/track")
        assert response.status_code == 404


class TestAutoPurchaseEndpoints:
    """Tests for auto-purchase endpoints."""

    def test_compare_suppliers(self, test_client: TestClient, sample_product_id: str) -> None:
        """Test comparing suppliers for a product."""
        response = test_client.post(f"/api/v1/auto-purchase/compare?product_id={sample_product_id}&quantity=100")
        assert response.status_code == 200

        data = response.json()
        assert "quotes" in data
        assert "product_id" in data
        assert len(data["quotes"]) > 0

    def test_bulk_purchase(self, test_client: TestClient, sample_bulk_purchase_data: dict) -> None:
        """Test bulk purchase."""
        response = test_client.post("/api/v1/auto-purchase/bulk", json=sample_bulk_purchase_data)
        assert response.status_code == 201

        data = response.json()
        assert "orders" in data
        assert "total_cost" in data
        assert "estimated_savings" in data
        assert "optimization_applied" in data

    def test_bulk_purchase_validates_items(self, test_client: TestClient) -> None:
        """Test that bulk purchase validates items."""
        invalid_data = {
            "items": [],  # Empty items
            "delivery_address": "Test Address",
            "payment_method": "cash_on_delivery",
            "optimize_for": "price",
        }
        response = test_client.post("/api/v1/auto-purchase/bulk", json=invalid_data)
        assert response.status_code == 422


class TestBilingualResponses:
    """Tests for bilingual (Arabic/English) responses."""

    def test_health_has_arabic(self, test_client: TestClient) -> None:
        """Test that health endpoint includes Arabic."""
        response = test_client.get("/healthz")
        data = response.json()
        assert "service_ar" in data

    def test_readiness_has_arabic(self, test_client: TestClient) -> None:
        """Test that readiness endpoint includes Arabic."""
        response = test_client.get("/readyz")
        data = response.json()
        assert "status_ar" in data

    def test_products_have_arabic_names(self, test_client: TestClient) -> None:
        """Test that products have Arabic names."""
        response = test_client.get("/api/v1/products")
        data = response.json()

        if data["items"]:
            item = data["items"][0]
            assert "name_ar" in item
            assert "unit_ar" in item

    def test_suppliers_have_arabic_names(self, test_client: TestClient) -> None:
        """Test that suppliers have Arabic names."""
        response = test_client.get("/api/v1/suppliers")
        data = response.json()

        if data["items"]:
            item = data["items"][0]
            assert "name_ar" in item
            assert "location_ar" in item

    def test_error_responses_are_bilingual(self, test_client: TestClient) -> None:
        """Test that error responses include Arabic messages."""
        response = test_client.get("/api/v1/orders/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

        data = response.json()
        assert "message" in data["detail"]
        assert "message_ar" in data["detail"]
