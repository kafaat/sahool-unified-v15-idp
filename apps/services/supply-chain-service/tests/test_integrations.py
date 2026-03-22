"""Tests for supplier integrations in Supply Chain Service."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")

import pytest
from uuid import uuid4, UUID


class TestSupplierIntegrationBase:
    """Tests for SupplierIntegration base class."""

    def test_init(self):
        from src.suppliers.integrations import SupplierIntegration

        sid = uuid4()
        integration = SupplierIntegration(supplier_id=sid, api_key="test-key")
        assert integration.supplier_id == sid
        assert integration.api_key == "test-key"
        assert integration.timeout == 30

    def test_init_without_api_key(self):
        from src.suppliers.integrations import SupplierIntegration

        integration = SupplierIntegration(supplier_id=uuid4())
        assert integration.api_key is None

    @pytest.mark.asyncio
    async def test_get_product_catalog(self):
        from src.suppliers.integrations import SupplierIntegration

        integration = SupplierIntegration(supplier_id=uuid4())
        catalog = await integration.get_product_catalog()
        assert isinstance(catalog, list)
        assert len(catalog) == 2
        for item in catalog:
            assert "sku" in item
            assert "name" in item
            assert "name_ar" in item
            assert "price" in item
            assert "currency" in item
            assert item["currency"] == "SAR"

    @pytest.mark.asyncio
    async def test_check_stock(self):
        from src.suppliers.integrations import SupplierIntegration

        integration = SupplierIntegration(supplier_id=uuid4())
        result = await integration.check_stock("UREA-46-50KG", 10)
        assert "sku" in result
        assert result["sku"] == "UREA-46-50KG"
        assert "requested" in result
        assert result["requested"] == 10
        assert "available" in result
        assert "is_available" in result
        assert isinstance(result["is_available"], bool)

    @pytest.mark.asyncio
    async def test_request_quote(self):
        from src.suppliers.integrations import SupplierIntegration

        integration = SupplierIntegration(supplier_id=uuid4())
        items = [{"sku": "UREA-46-50KG", "quantity": 10}]
        result = await integration.request_quote(items, "Farm Address, Riyadh")
        assert "quote_id" in result
        assert "supplier_id" in result
        assert "items" in result
        assert "subtotal" in result
        assert "delivery_fee" in result
        assert "tax" in result
        assert "total" in result
        assert result["currency"] == "SAR"

    @pytest.mark.asyncio
    async def test_request_quote_delivery_fee_threshold(self):
        from src.suppliers.integrations import SupplierIntegration

        integration = SupplierIntegration(supplier_id=uuid4())
        # With small quantity, subtotal could be < 1000, delivery_fee = 100
        # or >= 1000, delivery_fee = 0
        items = [{"sku": "TEST", "quantity": 1}]
        result = await integration.request_quote(items, "Address")
        if result["subtotal"] < 1000:
            assert result["delivery_fee"] == 100.0
        else:
            assert result["delivery_fee"] == 0.0

    @pytest.mark.asyncio
    async def test_place_order(self):
        from src.suppliers.integrations import SupplierIntegration

        integration = SupplierIntegration(supplier_id=uuid4())
        result = await integration.place_order("quote-123", "cash_on_delivery")
        assert "order_id" in result
        assert "supplier_order_ref" in result
        assert result["quote_id"] == "quote-123"
        assert result["status"] == "confirmed"
        assert result["payment_status"] == "pending"
        assert result["tracking_available"] is True

    @pytest.mark.asyncio
    async def test_place_order_non_cod_payment(self):
        from src.suppliers.integrations import SupplierIntegration

        integration = SupplierIntegration(supplier_id=uuid4())
        result = await integration.place_order("quote-123", "credit_card")
        assert result["payment_status"] == "processing"

    @pytest.mark.asyncio
    async def test_get_order_status(self):
        from src.suppliers.integrations import SupplierIntegration

        integration = SupplierIntegration(supplier_id=uuid4())
        result = await integration.get_order_status("ORD-20260201-ABC123")
        assert "order_ref" in result
        assert result["order_ref"] == "ORD-20260201-ABC123"
        assert "status" in result
        assert "status_ar" in result
        assert result["status"] in ("processing", "shipped", "out_for_delivery", "delivered")
        assert "tracking_url" in result

    @pytest.mark.asyncio
    async def test_get_delivery_tracking(self):
        from src.suppliers.integrations import SupplierIntegration

        integration = SupplierIntegration(supplier_id=uuid4())
        result = await integration.get_delivery_tracking("TRK-001")
        assert result["tracking_id"] == "TRK-001"
        assert result["status"] == "in_transit"
        assert result["status_ar"] == "في الطريق"
        assert "events" in result
        assert len(result["events"]) == 2


class TestAlRashidIntegration:
    """Tests for AlRashidIntegration."""

    def test_init(self):
        from src.suppliers.integrations import AlRashidIntegration

        integration = AlRashidIntegration()
        assert integration.supplier_id == UUID("11111111-1111-1111-1111-111111111111")
        assert integration.base_url == "https://api.alrashid-agri.sa/v1"
        assert integration.api_key is None

    def test_init_with_api_key(self):
        from src.suppliers.integrations import AlRashidIntegration

        integration = AlRashidIntegration(api_key="test-key")
        assert integration.api_key == "test-key"


class TestGreenFieldsIntegration:
    """Tests for GreenFieldsIntegration."""

    def test_init(self):
        from src.suppliers.integrations import GreenFieldsIntegration

        integration = GreenFieldsIntegration()
        assert integration.supplier_id == UUID("22222222-2222-2222-2222-222222222222")
        assert integration.base_url == "https://api.greenfields.sa/v1"


class TestSaharaAgroIntegration:
    """Tests for SaharaAgroIntegration."""

    def test_init(self):
        from src.suppliers.integrations import SaharaAgroIntegration

        integration = SaharaAgroIntegration()
        assert integration.supplier_id == UUID("33333333-3333-3333-3333-333333333333")
        assert integration.base_url == "https://api.sahara-agro.sa/v1"


class TestGetSupplierIntegration:
    """Tests for get_supplier_integration factory."""

    def test_al_rashid(self):
        from src.suppliers.integrations import get_supplier_integration, AlRashidIntegration

        result = get_supplier_integration(UUID("11111111-1111-1111-1111-111111111111"))
        assert isinstance(result, AlRashidIntegration)

    def test_green_fields(self):
        from src.suppliers.integrations import get_supplier_integration, GreenFieldsIntegration

        result = get_supplier_integration(UUID("22222222-2222-2222-2222-222222222222"))
        assert isinstance(result, GreenFieldsIntegration)

    def test_sahara_agro(self):
        from src.suppliers.integrations import get_supplier_integration, SaharaAgroIntegration

        result = get_supplier_integration(UUID("33333333-3333-3333-3333-333333333333"))
        assert isinstance(result, SaharaAgroIntegration)

    def test_unknown_supplier_returns_generic(self):
        from src.suppliers.integrations import get_supplier_integration, SupplierIntegration

        result = get_supplier_integration(uuid4())
        assert isinstance(result, SupplierIntegration)
        assert not isinstance(result, type(None))
