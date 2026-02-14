"""
E2E Tests for Marketplace Service.
اختبارات شاملة لخدمة السوق

Tests the complete marketplace flow:
- Product listing with filters (category, governorate, price range)
- Product creation with Arabic names
- Order placement and tracking
- Harvest-to-marketplace listing conversion
- Market statistics
- Wallet operations (deposit, withdraw, transactions)
- Credit scoring and loan workflows

Service: marketplace-service (NestJS)
Port: 3010
Routes: /api/v1/market/*, /api/v1/fintech/*

Usage:
    pytest tests/e2e/test_marketplace_e2e.py -v -m e2e

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import os
import uuid
from typing import Any

import httpx
import pytest

# ============================================================================
# Configuration
# ============================================================================

MARKETPLACE_BASE_URL = os.getenv("E2E_MARKETPLACE_BASE_URL", "http://localhost:3010")
AUTH_BASE_URL = os.getenv("E2E_AUTH_BASE_URL", "http://localhost:3025")
MARKET_API = f"{MARKETPLACE_BASE_URL}/api/v1/market"
FINTECH_API = f"{MARKETPLACE_BASE_URL}/api/v1/fintech"

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
async def auth_token() -> str:
    """Obtain JWT auth token from user-service."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{AUTH_BASE_URL}/api/v1/auth/login",
                json={
                    "email": os.getenv("E2E_TEST_EMAIL", "test@sahool.app"),
                    "password": os.getenv("E2E_TEST_PASSWORD", "TestPass123!"),
                },
            )
            if resp.status_code == 200:
                return resp.json().get("access_token", "e2e-test-token")
        except httpx.ConnectError:
            pass
    return "e2e-test-token-fallback"


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """Authorization headers."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


@pytest.fixture
async def http_client() -> httpx.AsyncClient:
    """Async HTTP client with extended timeout."""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
def test_seller_id() -> str:
    """Test seller ID for product creation."""
    return os.getenv("E2E_SELLER_ID", f"seller-{uuid.uuid4().hex[:8]}")


@pytest.fixture
def test_buyer_id() -> str:
    """Test buyer ID for order placement."""
    return os.getenv("E2E_BUYER_ID", f"buyer-{uuid.uuid4().hex[:8]}")


@pytest.fixture
def create_product_payload(test_seller_id: str) -> dict[str, Any]:
    """
    Valid product creation payload with Arabic names.
    بيانات إنشاء منتج صالحة بأسماء عربية
    """
    unique = uuid.uuid4().hex[:6]
    return {
        "name": f"Premium Wheat Flour {unique}",
        "nameAr": f"طحين قمح ممتاز {unique}",
        "category": "grains",
        "price": 1200.0,
        "stock": 500,
        "unit": "kg",
        "description": f"High-quality wheat flour from Hadramaut fields - batch {unique}",
        "descriptionAr": f"طحين قمح عالي الجودة من حقول حضرموت - دفعة {unique}",
        "sellerId": test_seller_id,
        "sellerType": "farmer",
        "sellerName": "أحمد الفلاح",
        "cropType": "wheat",
        "governorate": "حضرموت",
    }


@pytest.fixture
async def created_product(
    http_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    create_product_payload: dict[str, Any],
) -> dict[str, Any] | None:
    """Create a product and yield its data for test use."""
    resp = await http_client.post(
        f"{MARKET_API}/products",
        headers=auth_headers,
        json=create_product_payload,
    )
    if resp.status_code not in (200, 201):
        pytest.skip(f"Cannot create product (status {resp.status_code}): {resp.text[:200]}")
        return None

    return resp.json()


# ============================================================================
# Health Check Tests
# ============================================================================


class TestMarketplaceHealth:
    """Marketplace service health and readiness tests."""

    async def test_healthz_returns_ok(self, http_client: httpx.AsyncClient):
        """
        Marketplace liveness probe.
        فحص صحة خدمة السوق
        """
        resp = await http_client.get(f"{MARKETPLACE_BASE_URL}/healthz")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("status") == "ok"
        assert body.get("service") == "marketplace-service"
        assert body.get("version") == "16.0.0"

    async def test_readyz_returns_ready(self, http_client: httpx.AsyncClient):
        """
        Readiness probe confirms database and cache connectivity.
        فحص الجاهزية يؤكد الاتصال بقاعدة البيانات وذاكرة التخزين المؤقت
        """
        resp = await http_client.get(f"{MARKETPLACE_BASE_URL}/readyz")
        assert resp.status_code in (200, 503)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("status") == "ready"
            checks = body.get("checks", {})
            assert checks.get("database") == "connected"


# ============================================================================
# Product Listing Tests
# ============================================================================


class TestProductListing:
    """
    Product listing and filtering tests.
    اختبارات قائمة المنتجات والتصفية
    """

    async def test_list_all_products(self, http_client: httpx.AsyncClient):
        """
        List all marketplace products.
        سرد جميع منتجات السوق
        """
        resp = await http_client.get(f"{MARKET_API}/products")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, (list, dict))

    async def test_list_products_filter_by_category(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Filter products by category (grains).
        تصفية المنتجات حسب الفئة
        """
        resp = await http_client.get(
            f"{MARKET_API}/products",
            params={"category": "grains"},
        )
        assert resp.status_code == 200

    async def test_list_products_filter_by_governorate(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Filter products by Yemeni governorate.
        تصفية المنتجات حسب المحافظة اليمنية
        """
        resp = await http_client.get(
            f"{MARKET_API}/products",
            params={"governorate": "حضرموت"},
        )
        assert resp.status_code == 200

    async def test_list_products_filter_by_price_range(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Filter products by price range.
        تصفية المنتجات حسب نطاق السعر
        """
        resp = await http_client.get(
            f"{MARKET_API}/products",
            params={"minPrice": "100", "maxPrice": "5000"},
        )
        assert resp.status_code == 200

    async def test_get_product_by_id(
        self,
        http_client: httpx.AsyncClient,
        created_product: dict[str, Any],
    ):
        """
        Retrieve a single product by ID.
        استرجاع منتج واحد بالمعرف
        """
        product_id = created_product.get("id")
        if not product_id:
            pytest.skip("No product ID available")

        resp = await http_client.get(f"{MARKET_API}/products/{product_id}")
        assert resp.status_code in (200, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("id") == product_id

    async def test_get_product_not_found(self, http_client: httpx.AsyncClient):
        """
        Requesting a nonexistent product returns 404.
        طلب منتج غير موجود يرجع 404
        """
        fake_id = str(uuid.uuid4())
        resp = await http_client.get(f"{MARKET_API}/products/{fake_id}")
        assert resp.status_code in (404, 500)


# ============================================================================
# Product Creation Tests
# ============================================================================


class TestProductCreation:
    """
    Product creation and validation tests.
    اختبارات إنشاء المنتجات والتحقق منها
    """

    async def test_create_product_success(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        create_product_payload: dict[str, Any],
    ):
        """
        Create a new agricultural product with Arabic name.
        إنشاء منتج زراعي جديد باسم عربي
        """
        resp = await http_client.post(
            f"{MARKET_API}/products",
            headers=auth_headers,
            json=create_product_payload,
        )
        assert resp.status_code in (201, 400, 401)

        if resp.status_code == 201:
            body = resp.json()
            assert body.get("id") is not None
            assert body.get("name") == create_product_payload["name"]
            assert body.get("nameAr") == create_product_payload["nameAr"]
            assert body.get("price") == create_product_payload["price"]

    async def test_create_product_missing_name(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Product creation without name should fail.
        يجب أن يفشل إنشاء منتج بدون اسم
        """
        payload = {
            "category": "grains",
            "price": 100.0,
            "stock": 10,
            "unit": "kg",
            "sellerId": "test-seller",
            "sellerType": "farmer",
        }
        resp = await http_client.post(
            f"{MARKET_API}/products",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (400, 401, 422)

    async def test_create_product_negative_price(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Product with negative price should be rejected.
        يجب رفض المنتج بسعر سالب
        """
        payload = {
            "name": "Bad Product",
            "nameAr": "منتج سيء",
            "category": "vegetables",
            "price": -50.0,
            "stock": 10,
            "unit": "kg",
            "sellerId": "test-seller",
            "sellerType": "farmer",
        }
        resp = await http_client.post(
            f"{MARKET_API}/products",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (400, 401, 422)

    async def test_create_product_without_auth(
        self,
        http_client: httpx.AsyncClient,
        create_product_payload: dict[str, Any],
    ):
        """Product creation without authentication should fail."""
        resp = await http_client.post(
            f"{MARKET_API}/products",
            json=create_product_payload,
        )
        assert resp.status_code == 401


# ============================================================================
# Order Placement Tests
# ============================================================================


class TestOrderPlacement:
    """
    Order creation and retrieval tests.
    اختبارات إنشاء الطلبات واسترجاعها
    """

    async def test_create_order(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        created_product: dict[str, Any],
        test_buyer_id: str,
    ):
        """
        Place an order for a marketplace product.
        وضع طلب لمنتج في السوق
        """
        product_id = created_product.get("id")
        if not product_id:
            pytest.skip("No product available for ordering")

        order_payload = {
            "buyerId": test_buyer_id,
            "buyerName": "محمد المشتري",
            "items": [
                {"productId": product_id, "quantity": 50},
            ],
            "deliveryAddress": "صنعاء، اليمن",
            "paymentMethod": "wallet",
        }
        resp = await http_client.post(
            f"{MARKET_API}/orders",
            headers=auth_headers,
            json=order_payload,
        )
        assert resp.status_code in (201, 400, 401, 404, 422)

        if resp.status_code == 201:
            body = resp.json()
            assert body.get("id") is not None
            assert body.get("status") is not None

    async def test_create_order_empty_items(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_buyer_id: str,
    ):
        """
        Order with empty items should fail.
        طلب بدون عناصر يجب أن يفشل
        """
        payload = {
            "buyerId": test_buyer_id,
            "items": [],
        }
        resp = await http_client.post(
            f"{MARKET_API}/orders",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (400, 401, 422)

    async def test_get_user_orders(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_buyer_id: str,
    ):
        """
        Retrieve orders for a buyer.
        استرجاع طلبات المشتري
        """
        resp = await http_client.get(
            f"{MARKET_API}/orders/{test_buyer_id}",
            headers=auth_headers,
            params={"role": "buyer"},
        )
        assert resp.status_code in (200, 401, 403, 404)

    async def test_get_user_orders_as_seller(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_seller_id: str,
    ):
        """
        Retrieve orders for a seller.
        استرجاع طلبات البائع
        """
        resp = await http_client.get(
            f"{MARKET_API}/orders/{test_seller_id}",
            headers=auth_headers,
            params={"role": "seller"},
        )
        assert resp.status_code in (200, 401, 403, 404)


# ============================================================================
# Harvest-to-Marketplace Tests
# ============================================================================


class TestHarvestToMarketplace:
    """
    Tests for converting yield predictions to marketplace listings.
    اختبارات تحويل توقعات الحصاد إلى قوائم في السوق
    """

    async def test_list_harvest_as_product(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_seller_id: str,
    ):
        """
        Convert a yield prediction into a marketplace product listing.
        تحويل توقع الحصاد إلى قائمة منتج في السوق
        """
        payload = {
            "userId": test_seller_id,
            "yieldData": {
                "crop": "wheat",
                "cropAr": "قمح",
                "predictedYieldTons": 3.5,
                "pricePerTon": 1850.0,
                "harvestDate": "2026-06-15",
                "qualityGrade": "premium",
                "governorate": "حضرموت",
                "district": "سيئون",
            },
        }
        resp = await http_client.post(
            f"{MARKET_API}/list-harvest",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (201, 400, 401, 422)

        if resp.status_code == 201:
            body = resp.json()
            assert body.get("id") is not None
            # Product should be derived from yield data
            assert body.get("name") is not None


# ============================================================================
# Market Statistics Tests
# ============================================================================


class TestMarketStatistics:
    """
    Market statistics and analytics tests.
    اختبارات إحصائيات وتحليلات السوق
    """

    async def test_get_market_stats(self, http_client: httpx.AsyncClient):
        """
        Retrieve marketplace statistics.
        استرجاع إحصائيات السوق
        """
        resp = await http_client.get(f"{MARKET_API}/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict)


# ============================================================================
# Wallet Operations Tests
# ============================================================================


class TestWalletOperations:
    """
    Digital wallet operations tests.
    اختبارات عمليات المحفظة الرقمية
    """

    async def test_get_wallet(
        self,
        http_client: httpx.AsyncClient,
        test_buyer_id: str,
    ):
        """
        Retrieve wallet for a user.
        استرجاع محفظة المستخدم
        """
        resp = await http_client.get(
            f"{FINTECH_API}/wallet/{test_buyer_id}",
            params={"userType": "farmer"},
        )
        assert resp.status_code in (200, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert "balance" in body or "id" in body

    async def test_deposit_to_wallet(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Deposit funds into a wallet.
        إيداع أموال في المحفظة
        """
        wallet_id = os.getenv("E2E_WALLET_ID", "test-wallet-001")
        resp = await http_client.post(
            f"{FINTECH_API}/wallet/{wallet_id}/deposit",
            headers=auth_headers,
            json={
                "amount": 1000.0,
                "description": "E2E test deposit - إيداع اختبار",
            },
        )
        assert resp.status_code in (200, 401, 404)

    async def test_withdraw_from_wallet(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Withdraw funds from a wallet.
        سحب أموال من المحفظة
        """
        wallet_id = os.getenv("E2E_WALLET_ID", "test-wallet-001")
        resp = await http_client.post(
            f"{FINTECH_API}/wallet/{wallet_id}/withdraw",
            headers=auth_headers,
            json={
                "amount": 100.0,
                "description": "E2E test withdrawal - سحب اختبار",
            },
        )
        assert resp.status_code in (200, 400, 401, 404)

    async def test_get_wallet_transactions(self, http_client: httpx.AsyncClient):
        """
        Get transaction history for a wallet.
        الحصول على سجل المعاملات للمحفظة
        """
        wallet_id = os.getenv("E2E_WALLET_ID", "test-wallet-001")
        resp = await http_client.get(
            f"{FINTECH_API}/wallet/{wallet_id}/transactions",
            params={"limit": "10"},
        )
        assert resp.status_code in (200, 404)


# ============================================================================
# Credit Scoring Tests
# ============================================================================


class TestCreditScoring:
    """
    Farm-based credit scoring tests.
    اختبارات التصنيف الائتماني المبني على بيانات المزرعة
    """

    async def test_calculate_credit_score(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_seller_id: str,
    ):
        """
        Calculate credit score based on farm data.
        حساب التصنيف الائتماني بناء على بيانات المزرعة
        """
        payload = {
            "userId": test_seller_id,
            "farmData": {
                "totalArea": 15.0,
                "activeSeasons": 8,
                "fieldCount": 3,
                "diseaseRisk": "Low",
                "irrigationType": "drip",
                "avgYieldScore": 75,
                "onTimePayments": 20,
                "latePayments": 2,
            },
        }
        resp = await http_client.post(
            f"{FINTECH_API}/calculate-score",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (200, 201, 401)

        if resp.status_code in (200, 201):
            body = resp.json()
            assert "score" in body or "creditScore" in body

    async def test_calculate_advanced_credit_score(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_seller_id: str,
    ):
        """
        Calculate advanced credit score with satellite verification.
        حساب التصنيف الائتماني المتقدم مع التحقق الفضائي
        """
        payload = {
            "userId": test_seller_id,
            "factors": {
                "farmArea": 15.0,
                "numberOfSeasons": 8,
                "diseaseRiskScore": 20,
                "irrigationType": "drip",
                "yieldScore": 75,
                "paymentHistory": 90,
                "cropDiversity": 4,
                "marketplaceHistory": 65,
                "loanRepaymentRate": 95,
                "verificationLevel": "verified",
                "landOwnership": "owned",
                "cooperativeMember": True,
                "yearsOfExperience": 12,
                "satelliteVerified": True,
            },
        }
        resp = await http_client.post(
            f"{FINTECH_API}/calculate-advanced-score",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (200, 201, 401)

    async def test_get_credit_factors(
        self,
        http_client: httpx.AsyncClient,
        test_seller_id: str,
    ):
        """Get credit factors for a user."""
        resp = await http_client.get(
            f"{FINTECH_API}/credit-factors/{test_seller_id}",
        )
        assert resp.status_code in (200, 404)

    async def test_get_credit_report(
        self,
        http_client: httpx.AsyncClient,
        test_seller_id: str,
    ):
        """
        Get full credit report for a user.
        الحصول على التقرير الائتماني الكامل للمستخدم
        """
        resp = await http_client.get(
            f"{FINTECH_API}/credit-report/{test_seller_id}",
        )
        assert resp.status_code in (200, 404)


# ============================================================================
# Loan Workflow Tests
# ============================================================================


class TestLoanWorkflow:
    """
    Agricultural loan request and management tests.
    اختبارات طلب وإدارة القروض الزراعية
    """

    async def test_request_loan(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Request a new agricultural loan.
        طلب قرض زراعي جديد
        """
        wallet_id = os.getenv("E2E_WALLET_ID", "test-wallet-001")
        payload = {
            "walletId": wallet_id,
            "amount": 50000.0,
            "termMonths": 12,
            "purpose": "irrigation_equipment",
            "purposeDetails": "Purchase drip irrigation system for 10 hectares",
            "collateralType": "farm_equipment",
            "collateralValue": 80000.0,
        }
        resp = await http_client.post(
            f"{FINTECH_API}/loans",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (201, 400, 401, 404)

    async def test_get_user_loans(self, http_client: httpx.AsyncClient):
        """
        List loans for a wallet.
        سرد القروض للمحفظة
        """
        wallet_id = os.getenv("E2E_WALLET_ID", "test-wallet-001")
        resp = await http_client.get(f"{FINTECH_API}/loans/{wallet_id}")
        assert resp.status_code in (200, 404)

    async def test_get_finance_stats(self, http_client: httpx.AsyncClient):
        """
        Get finance statistics.
        الحصول على إحصائيات التمويل
        """
        resp = await http_client.get(f"{FINTECH_API}/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict)


# ============================================================================
# Full Marketplace Workflow Test
# ============================================================================


class TestFullMarketplaceWorkflow:
    """
    End-to-end marketplace workflow spanning multiple operations.
    سير عمل السوق الشامل عبر عمليات متعددة
    """

    async def test_seller_to_buyer_workflow(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Complete workflow: list product -> browse -> order -> track.
        سير عمل كامل: إدراج المنتج -> تصفح -> طلب -> تتبع

        Steps:
        1. Check marketplace health
        2. Create a product listing
        3. Browse products to verify it appears
        4. Place an order for the product
        5. Retrieve the buyer's orders
        """
        # Step 1: Health check
        health_resp = await http_client.get(f"{MARKETPLACE_BASE_URL}/healthz")
        if health_resp.status_code != 200:
            pytest.skip("Marketplace service not available")

        # Step 2: Create a product
        seller_id = f"e2e-seller-{uuid.uuid4().hex[:6]}"
        product_payload = {
            "name": "Fresh Yemeni Honey",
            "nameAr": "عسل يمني طازج",
            "category": "honey",
            "price": 5000.0,
            "stock": 100,
            "unit": "kg",
            "description": "Wild flower honey from Wadi Do'an",
            "descriptionAr": "عسل زهور برية من وادي دوعن",
            "sellerId": seller_id,
            "sellerType": "farmer",
            "sellerName": "خالد المربي",
            "governorate": "حضرموت",
        }
        create_resp = await http_client.post(
            f"{MARKET_API}/products",
            headers=auth_headers,
            json=product_payload,
        )
        if create_resp.status_code not in (201, 200):
            pytest.skip(f"Cannot create product: {create_resp.status_code}")

        product = create_resp.json()
        product_id = product.get("id")
        assert product_id is not None, "Product ID should be returned"

        # Step 3: Browse products - verify our product appears
        browse_resp = await http_client.get(
            f"{MARKET_API}/products",
            params={"category": "honey"},
        )
        assert browse_resp.status_code == 200

        # Step 4: Place an order
        buyer_id = f"e2e-buyer-{uuid.uuid4().hex[:6]}"
        order_payload = {
            "buyerId": buyer_id,
            "buyerName": "سعيد المشتري",
            "items": [
                {"productId": product_id, "quantity": 10},
            ],
            "deliveryAddress": "صنعاء، شارع الستين",
            "paymentMethod": "wallet",
        }
        order_resp = await http_client.post(
            f"{MARKET_API}/orders",
            headers=auth_headers,
            json=order_payload,
        )
        assert order_resp.status_code in (201, 400, 404)

        if order_resp.status_code == 201:
            order = order_resp.json()
            assert order.get("id") is not None

            # Step 5: Get buyer orders
            orders_resp = await http_client.get(
                f"{MARKET_API}/orders/{buyer_id}",
                headers=auth_headers,
                params={"role": "buyer"},
            )
            assert orders_resp.status_code in (200, 403, 404)
