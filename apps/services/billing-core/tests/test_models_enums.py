"""
Tests for billing-core models and enums.
Covers: Pydantic models, StrEnum classes, feature translations, helper functions.
"""

import sys
import os
import uuid
import warnings
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# We need to mock external dependencies before importing main
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"


# ============================================================
# Test Enums
# ============================================================


class TestEnums:
    """Test all StrEnum classes defined in main.py"""

    def test_plan_tier_values(self):
        from src.main import PlanTier

        assert PlanTier.FREE == "free"
        assert PlanTier.STARTER == "starter"
        assert PlanTier.PROFESSIONAL == "professional"
        assert PlanTier.ENTERPRISE == "enterprise"

    def test_billing_cycle_values(self):
        from src.main import BillingCycle

        assert BillingCycle.MONTHLY == "monthly"
        assert BillingCycle.QUARTERLY == "quarterly"
        assert BillingCycle.YEARLY == "yearly"

    def test_subscription_status_values(self):
        from src.main import SubscriptionStatus

        assert SubscriptionStatus.ACTIVE == "active"
        assert SubscriptionStatus.TRIAL == "trial"
        assert SubscriptionStatus.PAST_DUE == "past_due"
        assert SubscriptionStatus.CANCELED == "canceled"
        assert SubscriptionStatus.SUSPENDED == "suspended"
        assert SubscriptionStatus.EXPIRED == "expired"

    def test_invoice_status_values(self):
        from src.main import InvoiceStatus

        assert InvoiceStatus.DRAFT == "draft"
        assert InvoiceStatus.PENDING == "pending"
        assert InvoiceStatus.PAID == "paid"
        assert InvoiceStatus.OVERDUE == "overdue"
        assert InvoiceStatus.CANCELED == "canceled"
        assert InvoiceStatus.REFUNDED == "refunded"

    def test_payment_method_values(self):
        from src.main import PaymentMethod

        assert PaymentMethod.CREDIT_CARD == "credit_card"
        assert PaymentMethod.BANK_TRANSFER == "bank_transfer"
        assert PaymentMethod.MOBILE_MONEY == "mobile_money"
        assert PaymentMethod.CASH == "cash"
        assert PaymentMethod.THARWATT == "tharwatt"

    def test_payment_status_values(self):
        from src.main import PaymentStatus

        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.PROCESSING == "processing"
        assert PaymentStatus.SUCCEEDED == "succeeded"
        assert PaymentStatus.FAILED == "failed"
        assert PaymentStatus.REFUNDED == "refunded"

    def test_currency_values(self):
        from src.main import Currency

        assert Currency.USD == "USD"
        assert Currency.YER == "YER"


# ============================================================
# Test Pydantic Models
# ============================================================


class TestPydanticModels:
    """Test Pydantic request/response models"""

    def test_plan_feature_model(self):
        from src.main import PlanFeature

        feature = PlanFeature(name="Fields", name_ar="الحقول", included=True, limit=10)
        assert feature.name == "Fields"
        assert feature.name_ar == "الحقول"
        assert feature.included is True
        assert feature.limit == 10

    def test_plan_feature_unlimited(self):
        from src.main import PlanFeature

        feature = PlanFeature(name="Weather", name_ar="الطقس", included=True, limit=None)
        assert feature.limit is None

    def test_plan_pricing_model(self):
        from src.main import PlanPricing

        pricing = PlanPricing(
            monthly_usd=Decimal("29"),
            quarterly_usd=Decimal("79"),
            yearly_usd=Decimal("290"),
        )
        assert pricing.monthly_usd == Decimal("29")
        assert pricing.setup_fee_usd == Decimal("0")

    def test_create_plan_request(self):
        from src.main import CreatePlanRequest, PlanTier

        req = CreatePlanRequest(
            name="Test Plan",
            name_ar="خطة تجريبية",
            description="A test plan",
            description_ar="خطة تجريبية",
            tier=PlanTier.STARTER,
            monthly_price_usd=Decimal("29"),
            features={"fields": True, "satellite": True},
            limits={"fields": 10},
            trial_days=14,
        )
        assert req.tier == PlanTier.STARTER
        assert req.trial_days == 14

    def test_create_tenant_request(self):
        from src.main import CreateTenantRequest, BillingCycle

        req = CreateTenantRequest(
            name="Test Farm",
            name_ar="مزرعة تجريبية",
            email="test@example.com",
            phone="+967123456789",
            plan_id="starter",
            billing_cycle=BillingCycle.MONTHLY,
        )
        assert req.plan_id == "starter"
        assert req.billing_cycle == BillingCycle.MONTHLY

    def test_update_subscription_request(self):
        from src.main import UpdateSubscriptionRequest, BillingCycle, PaymentMethod

        req = UpdateSubscriptionRequest(
            plan_id="professional",
            billing_cycle=BillingCycle.YEARLY,
            payment_method=PaymentMethod.CREDIT_CARD,
        )
        assert req.plan_id == "professional"

    def test_record_usage_request(self):
        from src.main import RecordUsageRequest

        req = RecordUsageRequest(metric="api_calls", quantity=5, metadata={"endpoint": "/fields"})
        assert req.quantity == 5
        assert req.metadata == {"endpoint": "/fields"}

    def test_record_usage_request_defaults(self):
        from src.main import RecordUsageRequest

        req = RecordUsageRequest(metric="api_calls")
        assert req.quantity == 1
        assert req.metadata == {}

    def test_create_payment_request(self):
        from src.main import CreatePaymentRequest, PaymentMethod

        req = CreatePaymentRequest(
            invoice_id=str(uuid.uuid4()),
            amount=Decimal("99.00"),
            method=PaymentMethod.THARWATT,
            phone_number="+967123456789",
        )
        assert req.method == PaymentMethod.THARWATT
        assert req.phone_number == "+967123456789"

    def test_invoice_line_item_model(self):
        from src.main import InvoiceLineItem

        item = InvoiceLineItem(
            description="Starter Plan - Monthly",
            description_ar="المبتدئ - شهري",
            quantity=1,
            unit_price=Decimal("29.00"),
            amount=Decimal("29.00"),
        )
        assert item.is_usage_based is False
        assert item.quantity == 1

    def test_refund_request(self):
        from src.main import RefundRequest

        req = RefundRequest(
            payment_id=str(uuid.uuid4()),
            amount=Decimal("50.00"),
            reason="Customer request",
            reason_ar="طلب العميل",
        )
        assert req.amount == Decimal("50.00")

    def test_refund_request_full_refund(self):
        from src.main import RefundRequest

        req = RefundRequest(
            payment_id=str(uuid.uuid4()),
            reason="Full refund",
        )
        assert req.amount is None

    def test_tharwatt_webhook_payload(self):
        from src.main import TharwattWebhookPayload

        payload = TharwattWebhookPayload(
            transaction_id="TXN-123",
            status="completed",
            amount=Decimal("25000"),
            currency="YER",
            phone_number="+967123456789",
            reference="payment-uuid",
        )
        assert payload.status == "completed"
        assert payload.currency == "YER"


# ============================================================
# Test Helper Functions
# ============================================================


class TestHelperFunctions:
    """Test utility/helper functions"""

    def test_convert_to_yer(self):
        from src.main import convert_to_yer

        result = convert_to_yer(Decimal("100"))
        assert result == Decimal("25000.0")

    def test_convert_to_yer_zero(self):
        from src.main import convert_to_yer

        result = convert_to_yer(Decimal("0"))
        assert result == Decimal("0")

    def test_get_plan_price_monthly(self):
        from src.main import get_plan_price, BillingCycle

        pricing = {"monthly_usd": "29", "quarterly_usd": "79", "yearly_usd": "290"}
        result = get_plan_price(pricing, BillingCycle.MONTHLY)
        assert result == Decimal("29")

    def test_get_plan_price_quarterly(self):
        from src.main import get_plan_price, BillingCycle

        pricing = {"monthly_usd": "29", "quarterly_usd": "79", "yearly_usd": "290"}
        result = get_plan_price(pricing, BillingCycle.QUARTERLY)
        assert result == Decimal("79")

    def test_get_plan_price_yearly(self):
        from src.main import get_plan_price, BillingCycle

        pricing = {"monthly_usd": "29", "quarterly_usd": "79", "yearly_usd": "290"}
        result = get_plan_price(pricing, BillingCycle.YEARLY)
        assert result == Decimal("290")

    def test_get_plan_price_missing_key(self):
        from src.main import get_plan_price, BillingCycle

        pricing = {}
        result = get_plan_price(pricing, BillingCycle.MONTHLY)
        assert result == Decimal("0")

    def test_get_billing_period_end_monthly(self):
        from src.main import get_billing_period_end, BillingCycle

        start = date(2025, 1, 1)
        end = get_billing_period_end(start, BillingCycle.MONTHLY)
        assert end == date(2025, 1, 31)

    def test_get_billing_period_end_quarterly(self):
        from src.main import get_billing_period_end, BillingCycle

        start = date(2025, 1, 1)
        end = get_billing_period_end(start, BillingCycle.QUARTERLY)
        assert end == date(2025, 4, 1)

    def test_get_billing_period_end_yearly(self):
        from src.main import get_billing_period_end, BillingCycle

        start = date(2025, 1, 1)
        end = get_billing_period_end(start, BillingCycle.YEARLY)
        assert end == date(2026, 1, 1)

    def test_generate_invoice_number_format(self):
        from src.main import generate_invoice_number

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            number = generate_invoice_number()

        year = datetime.now(UTC).year
        assert number.startswith(f"SAH-{year}-")
        # UUID suffix should be 8 chars uppercase
        suffix = number.split("-", 2)[2]
        assert len(suffix) == 8
        assert suffix == suffix.upper()

    def test_generate_invoice_number_deprecation_warning(self):
        from src.main import generate_invoice_number

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            generate_invoice_number()
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()

    def test_sanitize_log(self):
        from src.main import _sanitize_log

        result = _sanitize_log("line1\nline2\rline3\r\nline4")
        assert "\n" not in result
        assert "\r" not in result

    def test_sanitize_log_normal_string(self):
        from src.main import _sanitize_log

        result = _sanitize_log("normal text")
        assert result == "normal text"


# ============================================================
# Test Feature Translations
# ============================================================


class TestFeatureTranslations:
    """Test Arabic translation of feature names"""

    def test_translate_known_feature(self):
        from src.main import translate_feature_name

        assert translate_feature_name("fields") == "الحقول"

    def test_translate_known_feature_satellite(self):
        from src.main import translate_feature_name

        assert translate_feature_name("satellite_analysis") == "تحليل الأقمار الصناعية"

    def test_translate_feature_with_spaces(self):
        from src.main import translate_feature_name

        result = translate_feature_name("ai diagnosis")
        assert result == "تشخيص المحاصيل بالذكاء الاصطناعي"

    def test_translate_feature_with_hyphens(self):
        from src.main import translate_feature_name

        result = translate_feature_name("ai-diagnosis")
        assert result == "تشخيص المحاصيل بالذكاء الاصطناعي"

    def test_translate_unknown_feature_fallback(self):
        from src.main import translate_feature_name

        result = translate_feature_name("unknown_feature_xyz")
        # Should return a formatted English name
        assert "Unknown Feature Xyz" in result

    def test_translate_partial_match(self):
        from src.main import translate_feature_name

        # "fields_limit" should match partial key "fields"
        result = translate_feature_name("fields_limit")
        assert result == "الحقول"


# ============================================================
# Test Constants and Config
# ============================================================


class TestConstants:
    """Test module-level constants"""

    def test_overage_rates_exist(self):
        from src.main import OVERAGE_RATES

        assert "fields" in OVERAGE_RATES
        assert OVERAGE_RATES["fields"] == Decimal("5.00")
        assert "storage_gb" in OVERAGE_RATES

    def test_plan_limits_exist(self):
        from src.main import PLAN_LIMITS

        assert "free" in PLAN_LIMITS
        assert "starter" in PLAN_LIMITS
        assert "professional" in PLAN_LIMITS
        assert "enterprise" in PLAN_LIMITS

    def test_plan_limits_free_fields(self):
        from src.main import PLAN_LIMITS

        assert PLAN_LIMITS["free"]["fields"] == 3

    def test_plan_limits_enterprise_unlimited(self):
        from src.main import PLAN_LIMITS

        assert PLAN_LIMITS["enterprise"]["fields"] == -1

    def test_feature_translations_ar_populated(self):
        from src.main import FEATURE_TRANSLATIONS_AR

        assert len(FEATURE_TRANSLATIONS_AR) > 50
        assert "irrigation" in FEATURE_TRANSLATIONS_AR


# ============================================================
# Test Webhook Signature Verification
# ============================================================


class TestWebhookSignatures:
    """Test webhook signature verification"""

    def test_verify_tharwatt_signature_no_secret(self):
        from src.main import verify_tharwatt_signature

        with patch("src.main.THARWATT_WEBHOOK_SECRET", ""):
            result = verify_tharwatt_signature(b"payload", "signature")
            assert result is False

    def test_verify_tharwatt_signature_no_signature(self):
        from src.main import verify_tharwatt_signature

        with patch("src.main.THARWATT_WEBHOOK_SECRET", "secret"):
            result = verify_tharwatt_signature(b"payload", "")
            assert result is False

    def test_verify_tharwatt_signature_valid(self):
        import hashlib
        import hmac as hmac_mod

        from src.main import verify_tharwatt_signature

        secret = "test-secret"
        payload = b'{"transaction_id": "123"}'
        expected = hmac_mod.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        with patch("src.main.THARWATT_WEBHOOK_SECRET", secret):
            result = verify_tharwatt_signature(payload, expected)
            assert result is True

    def test_verify_tharwatt_signature_invalid(self):
        from src.main import verify_tharwatt_signature

        with patch("src.main.THARWATT_WEBHOOK_SECRET", "secret"):
            result = verify_tharwatt_signature(b"payload", "bad-signature")
            assert result is False

    def test_verify_stripe_signature_no_secret(self):
        from src.main import verify_stripe_signature

        with patch("src.main.STRIPE_WEBHOOK_SECRET", ""):
            result = verify_stripe_signature(b"payload", "signature")
            assert result is False

    def test_verify_stripe_signature_no_signature(self):
        from src.main import verify_stripe_signature

        with patch("src.main.STRIPE_WEBHOOK_SECRET", "secret"):
            result = verify_stripe_signature(b"payload", "")
            assert result is False


# ============================================================
# Test Auth Helpers
# ============================================================


class TestAuthHelpers:
    """Test authentication helper functions"""

    def test_verify_tenant_access_dev_mode_no_auth(self):
        from src.main import verify_tenant_access

        with patch("src.main.AUTH_AVAILABLE", False):
            with patch.dict(os.environ, {"ENVIRONMENT": "test"}):
                result = verify_tenant_access(None, "any-tenant")
                assert result is True

    def test_verify_tenant_access_production_no_auth(self):
        from src.main import verify_tenant_access

        with patch("src.main.AUTH_AVAILABLE", False):
            with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
                result = verify_tenant_access(None, "any-tenant")
                assert result is False

    def test_verify_tenant_access_same_tenant(self):
        from src.main import verify_tenant_access

        user = MagicMock()
        user.tenant_id = "tenant-001"
        user.has_any_role = MagicMock(return_value=False)

        with patch("src.main.AUTH_AVAILABLE", True):
            result = verify_tenant_access(user, "tenant-001")
            assert result is True

    def test_verify_tenant_access_different_tenant(self):
        from src.main import verify_tenant_access

        user = MagicMock()
        user.tenant_id = "tenant-001"
        user.has_any_role = MagicMock(return_value=False)

        with patch("src.main.AUTH_AVAILABLE", True):
            result = verify_tenant_access(user, "tenant-002")
            assert result is False

    def test_verify_tenant_access_super_admin(self):
        from src.main import verify_tenant_access

        user = MagicMock()
        user.has_any_role = MagicMock(return_value=True)

        with patch("src.main.AUTH_AVAILABLE", True):
            result = verify_tenant_access(user, "any-tenant")
            assert result is True

    def test_require_tenant_or_admin_raises_403(self):
        from fastapi import HTTPException

        from src.main import require_tenant_or_admin

        with patch("src.main.verify_tenant_access", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                require_tenant_or_admin(None, "tenant-001")
            assert exc_info.value.status_code == 403
