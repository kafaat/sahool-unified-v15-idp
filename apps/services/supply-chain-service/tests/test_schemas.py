"""Tests for Pydantic schemas in Supply Chain Service."""

from datetime import datetime
from uuid import UUID, uuid4

import pytest


class TestProductCategory:
    """Tests for ProductCategory enum."""

    def test_all_categories_exist(self):
        from src.api.schemas import ProductCategory

        expected = ["seeds", "fertilizers", "pesticides", "herbicides", "equipment", "irrigation", "tools", "other"]
        for cat in expected:
            assert cat in [c.value for c in ProductCategory]

    def test_category_is_string(self):
        from src.api.schemas import ProductCategory

        assert isinstance(ProductCategory.SEEDS.value, str)
        assert ProductCategory.SEEDS == "seeds"
class TestOrderStatus:
    """Tests for OrderStatus enum."""

    def test_all_statuses_exist(self):
        from src.api.schemas import OrderStatus

        expected = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
        for s in expected:
            assert s in [st.value for st in OrderStatus]

    def test_status_values(self):
        from src.api.schemas import OrderStatus

        assert OrderStatus.PENDING == "pending"
        assert OrderStatus.CANCELLED == "cancelled"
class TestDeliveryStatusEnum:
    """Tests for DeliveryStatusEnum."""

    def test_all_delivery_statuses(self):
        from src.api.schemas import DeliveryStatusEnum

        expected = ["preparing", "picked_up", "in_transit", "out_for_delivery", "delivered", "failed"]
        for s in expected:
            assert s in [ds.value for ds in DeliveryStatusEnum]
class TestPaymentMethod:
    """Tests for PaymentMethod enum."""

    def test_all_payment_methods(self):
        from src.api.schemas import PaymentMethod

        assert PaymentMethod.CASH_ON_DELIVERY == "cash_on_delivery"
        assert PaymentMethod.CREDIT_CARD == "credit_card"
        assert PaymentMethod.BANK_TRANSFER == "bank_transfer"
        assert PaymentMethod.DIGITAL_WALLET == "digital_wallet"
class TestProductSchema:
    """Tests for Product schema."""

    def test_create_valid_product(self):
        from src.api.schemas import Product, ProductCategory

        product = Product(
            id=uuid4(),
            name="Wheat Seeds",
            name_ar="بذور القمح",
            category=ProductCategory.SEEDS,
            unit="kg",
            unit_ar="كجم",
            price_min=25.0,
            price_max=35.0,
        )
        assert product.name == "Wheat Seeds"
        assert product.is_available is True
        assert product.image_url is None

    def test_product_price_must_be_non_negative(self):
        from pydantic import ValidationError
        from src.api.schemas import Product, ProductCategory

        with pytest.raises(ValidationError):
            Product(
                id=uuid4(),
                name="Bad Product",
                name_ar="منتج سيء",
                category=ProductCategory.SEEDS,
                unit="kg",
                unit_ar="كجم",
                price_min=-5.0,
                price_max=10.0,
            )

    def test_product_name_min_length(self):
        from pydantic import ValidationError
        from src.api.schemas import Product, ProductCategory

        with pytest.raises(ValidationError):
            Product(
                id=uuid4(),
                name="",
                name_ar="بذور",
                category=ProductCategory.SEEDS,
                unit="kg",
                unit_ar="كجم",
                price_min=10.0,
                price_max=20.0,
            )
class TestProductCreate:
    """Tests for ProductCreate schema."""

    def test_create_valid(self):
        from src.api.schemas import ProductCategory, ProductCreate

        pc = ProductCreate(
            name="Test",
            name_ar="اختبار",
            category=ProductCategory.FERTILIZERS,
            unit="kg",
            unit_ar="كجم",
            price_min=0,
            price_max=100,
        )
        assert pc.description is None

    def test_invalid_missing_required(self):
        from pydantic import ValidationError
        from src.api.schemas import ProductCreate

        with pytest.raises(ValidationError):
            ProductCreate(name="Test", name_ar="اختبار")
class TestSupplierSchema:
    """Tests for Supplier schema."""

    def test_create_valid_supplier(self):
        from src.api.schemas import Supplier

        supplier = Supplier(
            id=uuid4(),
            name="Test Supplier",
            name_ar="مورد اختبار",
            location="Riyadh",
            location_ar="الرياض",
            latitude=24.7,
            longitude=46.7,
            rating=4.5,
            delivery_time_days=2,
        )
        assert supplier.is_verified is False
        assert supplier.is_active is True
        assert supplier.total_reviews == 0
        assert supplier.products == []

    def test_supplier_rating_bounds(self):
        from pydantic import ValidationError
        from src.api.schemas import Supplier

        with pytest.raises(ValidationError):
            Supplier(
                id=uuid4(),
                name="Bad",
                name_ar="سيء",
                location="X",
                location_ar="X",
                latitude=24.0,
                longitude=46.0,
                rating=6.0,  # exceeds max 5
                delivery_time_days=1,
            )

    def test_supplier_latitude_bounds(self):
        from pydantic import ValidationError
        from src.api.schemas import Supplier

        with pytest.raises(ValidationError):
            Supplier(
                id=uuid4(),
                name="Bad",
                name_ar="سيء",
                location="X",
                location_ar="X",
                latitude=100.0,  # out of range
                longitude=46.0,
                rating=4.0,
                delivery_time_days=1,
            )
class TestSupplierSummary:
    """Tests for SupplierSummary schema."""

    def test_create_summary(self):
        from src.api.schemas import SupplierSummary

        summary = SupplierSummary(
            id=uuid4(),
            name="Test",
            name_ar="اختبار",
            location="Riyadh",
            rating=4.0,
            delivery_time_days=3,
            is_verified=True,
        )
        assert summary.is_verified is True
class TestOrderSchemas:
    """Tests for Order-related schemas."""

    def test_order_item_create(self):
        from src.api.schemas import OrderItemCreate

        item = OrderItemCreate(product_id=uuid4(), quantity=10.0)
        assert item.quantity == 10.0

    def test_order_item_create_quantity_must_be_positive(self):
        from pydantic import ValidationError
        from src.api.schemas import OrderItemCreate

        with pytest.raises(ValidationError):
            OrderItemCreate(product_id=uuid4(), quantity=0)

    def test_order_create_min_items(self):
        from pydantic import ValidationError
        from src.api.schemas import OrderCreate, OrderItemCreate, PaymentMethod

        with pytest.raises(ValidationError):
            OrderCreate(
                supplier_id=uuid4(),
                items=[],
                delivery_address="Test address here",
                payment_method=PaymentMethod.CASH_ON_DELIVERY,
            )

    def test_order_create_delivery_address_min_length(self):
        from pydantic import ValidationError
        from src.api.schemas import OrderCreate, OrderItemCreate, PaymentMethod

        with pytest.raises(ValidationError):
            OrderCreate(
                supplier_id=uuid4(),
                items=[OrderItemCreate(product_id=uuid4(), quantity=1)],
                delivery_address="AB",  # too short, min_length=5
                payment_method=PaymentMethod.CASH_ON_DELIVERY,
            )

    def test_order_schema(self):
        from src.api.schemas import Order, OrderItem, OrderStatus, PaymentMethod

        order = Order(
            id=uuid4(),
            farmer_id=uuid4(),
            supplier_id=uuid4(),
            supplier_name="Test",
            supplier_name_ar="اختبار",
            status=OrderStatus.PENDING,
            items=[
                OrderItem(
                    product_id=uuid4(),
                    product_name="Prod",
                    product_name_ar="منتج",
                    quantity=5.0,
                    unit="kg",
                    unit_price=10.0,
                    total_price=50.0,
                )
            ],
            subtotal=50.0,
            total=57.5,
            delivery_address="Test Address Here",
            payment_method=PaymentMethod.CASH_ON_DELIVERY,
        )
        assert order.delivery_fee == 0
        assert order.tax == 0
        assert order.payment_status == "pending"
class TestPurchaseRecommendation:
    """Tests for PurchaseRecommendation schema."""

    def test_valid_recommendation(self):
        from src.api.schemas import PurchaseRecommendation

        rec = PurchaseRecommendation(
            id=uuid4(),
            product_id=uuid4(),
            product_name="Urea",
            product_name_ar="يوريا",
            quantity=100,
            unit="kg",
            field_id=uuid4(),
            reason="Low nitrogen",
            reason_ar="نقص نيتروجين",
            priority="high",
            valid_until=datetime.utcnow(),
        )
        assert rec.recommended_by == "advisory-service"

    def test_invalid_priority(self):
        from pydantic import ValidationError
        from src.api.schemas import PurchaseRecommendation

        with pytest.raises(ValidationError):
            PurchaseRecommendation(
                id=uuid4(),
                product_id=uuid4(),
                product_name="X",
                product_name_ar="X",
                quantity=1,
                unit="kg",
                field_id=uuid4(),
                reason="reason",
                reason_ar="سبب",
                priority="invalid_priority",
                valid_until=datetime.utcnow(),
            )
class TestAutoPurchaseSchemas:
    """Tests for auto-purchase schemas."""

    def test_auto_purchase_request_defaults(self):
        from src.api.schemas import AutoPurchaseRequest, PaymentMethod

        req = AutoPurchaseRequest(recommendation_id=uuid4())
        assert req.supplier_id is None
        assert req.delivery_address is None
        assert req.payment_method == PaymentMethod.CASH_ON_DELIVERY

    def test_bulk_purchase_request(self):
        from src.api.schemas import BulkPurchaseItem, BulkPurchaseRequest, PaymentMethod

        req = BulkPurchaseRequest(
            items=[BulkPurchaseItem(product_id=uuid4(), quantity=50)],
            delivery_address="Test Address",
        )
        assert req.optimize_for == "price"
        assert req.payment_method == PaymentMethod.CASH_ON_DELIVERY

    def test_bulk_purchase_invalid_optimize(self):
        from pydantic import ValidationError
        from src.api.schemas import BulkPurchaseItem, BulkPurchaseRequest

        with pytest.raises(ValidationError):
            BulkPurchaseRequest(
                items=[BulkPurchaseItem(product_id=uuid4(), quantity=50)],
                delivery_address="Test",
                optimize_for="invalid",
            )
class TestDeliveryStatus:
    """Tests for DeliveryStatus schema."""

    def test_delivery_status(self):
        from src.api.schemas import DeliveryStatus, DeliveryStatusEnum

        ds = DeliveryStatus(
            order_id=uuid4(),
            status=DeliveryStatusEnum.IN_TRANSIT,
            status_ar="في الطريق",
        )
        assert ds.eta is None
        assert ds.tracking_url is None
        assert ds.driver_name is None
class TestFarmerProfile:
    """Tests for FarmerProfile schema."""

    def test_farmer_profile(self):
        from src.api.schemas import FarmerProfile

        fp = FarmerProfile(
            id=uuid4(),
            name="Ahmed",
            name_ar="أحمد",
            phone="+966123456789",
            address="Riyadh",
            address_ar="الرياض",
            latitude=24.7,
            longitude=46.7,
        )
        assert fp.total_orders == 0
        assert fp.preferred_suppliers == []
        assert fp.payment_methods == []
class TestResponseSchemas:
    """Tests for list response schemas."""

    def test_product_list_response(self):
        from src.api.schemas import ProductListResponse

        resp = ProductListResponse(items=[], total=0, page=1, page_size=20)
        assert resp.total == 0

    def test_supplier_list_response(self):
        from src.api.schemas import SupplierListResponse

        resp = SupplierListResponse(items=[], total=0, page=1, page_size=20)
        assert resp.page == 1

    def test_order_list_response(self):
        from src.api.schemas import OrderListResponse

        resp = OrderListResponse(items=[], total=0, page=1, page_size=20)
        assert resp.page_size == 20
class TestSupplierQuote:
    """Tests for SupplierQuote schema."""

    def test_valid_quote(self):
        from src.api.schemas import SupplierQuote

        quote = SupplierQuote(
            id=uuid4(),
            supplier_id=uuid4(),
            supplier_name="Test",
            supplier_name_ar="اختبار",
            product_id=uuid4(),
            product_name="Product",
            product_name_ar="منتج",
            quantity=100.0,
            unit_price=10.0,
            total_price=1000.0,
            delivery_days=3,
            availability="in_stock",
            valid_until=datetime.utcnow(),
        )
        assert quote.notes is None

    def test_invalid_availability(self):
        from pydantic import ValidationError
        from src.api.schemas import SupplierQuote

        with pytest.raises(ValidationError):
            SupplierQuote(
                id=uuid4(),
                supplier_id=uuid4(),
                supplier_name="T",
                supplier_name_ar="T",
                product_id=uuid4(),
                product_name="P",
                product_name_ar="P",
                quantity=1,
                unit_price=1,
                total_price=1,
                delivery_days=1,
                availability="invalid_status",
                valid_until=datetime.utcnow(),
            )
class TestQuoteRequest:
    """Tests for QuoteRequest schema."""

    def test_valid_quote_request(self):
        from src.api.schemas import QuoteRequest

        qr = QuoteRequest(product_id=uuid4(), quantity=50.0)
        assert qr.delivery_address is None

    def test_quantity_must_be_positive(self):
        from pydantic import ValidationError
        from src.api.schemas import QuoteRequest

        with pytest.raises(ValidationError):
            QuoteRequest(product_id=uuid4(), quantity=-10)
class TestSupplierComparison:
    """Tests for SupplierComparison schema."""

    def test_comparison_defaults(self):
        from src.api.schemas import SupplierComparison

        comp = SupplierComparison(
            product_id=uuid4(),
            product_name="Test",
            product_name_ar="اختبار",
            quantity=100.0,
            quotes=[],
        )
        assert comp.best_price_supplier_id is None
        assert comp.fastest_delivery_supplier_id is None
        assert comp.best_rated_supplier_id is None
class TestBulkPurchaseResult:
    """Tests for BulkPurchaseResult schema."""

    def test_result(self):
        from src.api.schemas import BulkPurchaseResult

        result = BulkPurchaseResult(
            orders=[],
            total_cost=500.0,
            estimated_savings=50.0,
            optimization_applied="price",
        )
        assert result.total_cost == 500.0
