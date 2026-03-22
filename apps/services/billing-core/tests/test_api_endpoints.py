"""
Tests for billing-core API endpoints using FastAPI TestClient.
Covers: health endpoints, plans, tenants, subscriptions, usage, invoices, payments.
All database and external dependencies are mocked.
"""

import os
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
def _make_mock_plan(plan_id="starter", tier_value="starter"):
    """Create a mock plan object."""
    plan = MagicMock()
    plan.plan_id = plan_id
    plan.name = "Starter"
    plan.name_ar = "المبتدئ"
    plan.description = "Starter plan"
    plan.description_ar = "خطة المبتدئ"
    plan.tier = MagicMock(value=tier_value)
    plan.pricing = {"monthly_usd": "29", "quarterly_usd": "79", "yearly_usd": "290"}
    plan.features = {"fields": {"name": "Fields", "included": True, "limit": 10}}
    plan.limits = {"fields": 10, "api_calls_per_day": 500}
    plan.is_active = True
    plan.trial_days = 14
    plan.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return plan
def _make_mock_subscription(tenant_id="t-001", plan_id="starter"):
    """Create a mock subscription object."""
    sub = MagicMock()
    sub.id = uuid.uuid4()
    sub.tenant_id = tenant_id
    sub.plan_id = plan_id
    sub.status = MagicMock(value="active")
    sub.billing_cycle = MagicMock(value="monthly")
    sub.currency = MagicMock(value="USD")
    sub.start_date = date(2025, 1, 1)
    sub.end_date = date(2025, 1, 31)
    sub.next_billing_date = date(2025, 1, 31)
    sub.trial_end_date = None
    sub.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return sub
def _make_mock_tenant(tenant_id="t-001"):
    """Create a mock tenant object."""
    tenant = MagicMock()
    tenant.tenant_id = tenant_id
    tenant.name = "Test Farm"
    tenant.name_ar = "مزرعة تجريبية"
    tenant.contact = {"email": "test@example.com", "phone": "+967123456"}
    tenant.tax_id = None
    tenant.is_active = True
    tenant.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return tenant
def _make_mock_invoice():
    """Create a mock invoice object."""
    inv = MagicMock()
    inv.id = uuid.uuid4()
    inv.invoice_number = "SAH-2025-0001"
    inv.tenant_id = "t-001"
    inv.subscription_id = uuid.uuid4()
    inv.status = MagicMock(value="pending")
    inv.currency = MagicMock(value="USD")
    inv.issue_date = date(2025, 1, 1)
    inv.due_date = date(2025, 1, 8)
    inv.paid_date = None
    inv.subtotal = Decimal("29.00")
    inv.tax_amount = Decimal("0")
    inv.discount_amount = Decimal("0")
    inv.total = Decimal("29.00")
    inv.amount_paid = Decimal("0")
    inv.amount_due = Decimal("29.00")
    inv.line_items = [{"description": "Starter - Monthly", "amount": 29.0}]
    inv.notes = None
    inv.notes_ar = "شكرا"
    inv.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return inv
# ============================================================
# Test Health Endpoints
# ============================================================
class TestHealthEndpoints:
    """Test /healthz and /readyz endpoints"""

    def test_healthz(self):
        from fastapi.testclient import TestClient
        from src.main import app

        # Override all dependencies
        with patch("src.main.get_db", return_value=AsyncMock()):
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/healthz")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["service"] == "billing-core"
            assert data["version"] == "16.0.0"
# ============================================================
# Test NATS Event Publishing
# ============================================================
class TestNatsPublishing:
    """Test NATS event publishing function"""

    @pytest.mark.asyncio
    async def test_publish_event_with_jetstream(self):
        from src.main import publish_event

        mock_js = AsyncMock()
        with patch("src.main.js", mock_js):
            await publish_event("sahool.billing.test", {"key": "value"})
            mock_js.publish.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_publish_event_without_jetstream(self):
        from src.main import publish_event

        with patch("src.main.js", None):
            # Should not raise, just log
            await publish_event("sahool.billing.test", {"key": "value"})

    @pytest.mark.asyncio
    async def test_publish_event_jetstream_error(self):
        from src.main import publish_event

        mock_js = AsyncMock()
        mock_js.publish.side_effect = Exception("NATS down")
        with patch("src.main.js", mock_js):
            # Should not raise
            await publish_event("sahool.billing.test", {"key": "value"})
# ============================================================
# Test DB Model Enums (from models.py)
# ============================================================
class TestDbModelEnums:
    """Test SQLAlchemy model enums from models.py"""

    def test_subscription_status_enum(self):
        from src.models import SubscriptionStatus

        assert SubscriptionStatus.ACTIVE == "active"
        assert SubscriptionStatus.TRIAL == "trial"
        assert SubscriptionStatus.PAST_DUE == "past_due"

    def test_invoice_status_enum(self):
        from src.models import InvoiceStatus

        assert InvoiceStatus.DRAFT == "draft"
        assert InvoiceStatus.PAID == "paid"
        assert InvoiceStatus.REFUNDED == "refunded"

    def test_payment_method_enum(self):
        from src.models import PaymentMethod

        assert PaymentMethod.THARWATT == "tharwatt"
        assert PaymentMethod.CASH == "cash"

    def test_payment_status_enum(self):
        from src.models import PaymentStatus

        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.SUCCEEDED == "succeeded"

    def test_currency_enum(self):
        from src.models import Currency

        assert Currency.USD == "USD"
        assert Currency.YER == "YER"

    def test_billing_cycle_enum(self):
        from src.models import BillingCycle

        assert BillingCycle.MONTHLY == "monthly"
        assert BillingCycle.QUARTERLY == "quarterly"
        assert BillingCycle.YEARLY == "yearly"

    def test_plan_tier_enum(self):
        from src.models import PlanTier

        assert PlanTier.FREE == "free"
        assert PlanTier.ENTERPRISE == "enterprise"
# ============================================================
# Test DB Model __repr__
# ============================================================
class TestDbModelRepr:
    """Test __repr__ methods on SQLAlchemy models using MagicMock"""

    def test_plan_repr(self):
        from src.models import Plan

        mock = MagicMock(spec=Plan)
        mock.id = uuid.uuid4()
        mock.plan_id = "starter"
        mock.name = "Starter"
        mock.tier = "starter"
        mock.__repr__ = Plan.__repr__
        r = repr(mock)
        assert "Plan" in r
        assert "starter" in r

    def test_tenant_repr(self):
        from src.models import Tenant

        mock = MagicMock(spec=Tenant)
        mock.id = uuid.uuid4()
        mock.tenant_id = "t-001"
        mock.name = "Test"
        mock.__repr__ = Tenant.__repr__
        r = repr(mock)
        assert "Tenant" in r
        assert "t-001" in r

    def test_subscription_repr(self):
        from src.models import Subscription

        mock = MagicMock(spec=Subscription)
        mock.id = uuid.uuid4()
        mock.tenant_id = "t-001"
        mock.plan_id = "starter"
        mock.status = "active"
        mock.__repr__ = Subscription.__repr__
        r = repr(mock)
        assert "Subscription" in r
        assert "active" in r

    def test_invoice_repr(self):
        from src.models import Invoice

        mock = MagicMock(spec=Invoice)
        mock.id = uuid.uuid4()
        mock.invoice_number = "SAH-2025-0001"
        mock.total = Decimal("29.00")
        mock.status = "pending"
        mock.__repr__ = Invoice.__repr__
        r = repr(mock)
        assert "Invoice" in r
        assert "SAH-2025-0001" in r

    def test_payment_repr(self):
        from src.models import Payment

        mock = MagicMock(spec=Payment)
        mock.id = uuid.uuid4()
        mock.amount = Decimal("29.00")
        mock.method = "credit_card"
        mock.status = "pending"
        mock.__repr__ = Payment.__repr__
        r = repr(mock)
        assert "Payment" in r
        assert "credit_card" in r

    def test_usage_record_repr(self):
        from src.models import UsageRecord

        mock = MagicMock(spec=UsageRecord)
        mock.id = uuid.uuid4()
        mock.metric_type = "api_calls"
        mock.quantity = 5
        mock.recorded_at = datetime.now()
        mock.__repr__ = UsageRecord.__repr__
        r = repr(mock)
        assert "UsageRecord" in r
        assert "api_calls" in r
# ============================================================
# Test Init Module
# ============================================================
class TestInitModule:
    """Test __init__.py"""

    def test_version(self):
        from src import __version__

        assert __version__ == "15.6.0"
# ============================================================
# Test Async Helper Functions
# ============================================================
class TestAsyncHelpers:
    """Test async helper functions from main.py"""

    @pytest.mark.asyncio
    async def test_check_usage_limit_db_tenant_not_found(self):
        from src.main import check_usage_limit_db

        mock_db = AsyncMock()
        mock_repo_cls = MagicMock()

        # Tenant not found
        with patch("src.main.BillingRepository") as MockRepo:
            repo_instance = MagicMock()
            repo_instance.tenants.get_by_tenant_id = AsyncMock(return_value=None)
            MockRepo.return_value = repo_instance

            result = await check_usage_limit_db(mock_db, "t-001", "fields")
            assert result["allowed"] is False
            assert "Tenant not found" in result["reason"]

    @pytest.mark.asyncio
    async def test_check_usage_limit_db_no_subscription(self):
        from src.main import check_usage_limit_db

        mock_db = AsyncMock()

        with patch("src.main.BillingRepository") as MockRepo:
            repo_instance = MagicMock()
            repo_instance.tenants.get_by_tenant_id = AsyncMock(return_value=_make_mock_tenant())
            repo_instance.subscriptions.get_by_tenant = AsyncMock(return_value=None)
            MockRepo.return_value = repo_instance

            result = await check_usage_limit_db(mock_db, "t-001", "fields")
            assert result["allowed"] is False
            assert "No active subscription" in result["reason"]

    @pytest.mark.asyncio
    async def test_check_usage_limit_db_unlimited(self):
        from src.main import check_usage_limit_db

        mock_db = AsyncMock()
        mock_plan = _make_mock_plan()
        mock_plan.limits = {"fields": -1}

        with patch("src.main.BillingRepository") as MockRepo:
            repo_instance = MagicMock()
            repo_instance.tenants.get_by_tenant_id = AsyncMock(return_value=_make_mock_tenant())
            repo_instance.subscriptions.get_by_tenant = AsyncMock(return_value=_make_mock_subscription())
            repo_instance.plans.get_by_plan_id = AsyncMock(return_value=mock_plan)
            MockRepo.return_value = repo_instance

            result = await check_usage_limit_db(mock_db, "t-001", "fields")
            assert result["allowed"] is True
            assert result["remaining"] == "unlimited"

    @pytest.mark.asyncio
    async def test_check_usage_limit_db_within_limit(self):
        from src.main import check_usage_limit_db

        mock_db = AsyncMock()
        mock_plan = _make_mock_plan()
        mock_plan.limits = {"fields": 10}

        with patch("src.main.BillingRepository") as MockRepo:
            repo_instance = MagicMock()
            repo_instance.tenants.get_by_tenant_id = AsyncMock(return_value=_make_mock_tenant())
            repo_instance.subscriptions.get_by_tenant = AsyncMock(return_value=_make_mock_subscription())
            repo_instance.plans.get_by_plan_id = AsyncMock(return_value=mock_plan)
            repo_instance.usage_records.get_metric_count = AsyncMock(return_value=5)
            MockRepo.return_value = repo_instance

            result = await check_usage_limit_db(mock_db, "t-001", "fields")
            assert result["allowed"] is True
            assert result["used"] == 5
            assert result["remaining"] == 5

    @pytest.mark.asyncio
    async def test_check_usage_limit_db_exceeded(self):
        from src.main import check_usage_limit_db

        mock_db = AsyncMock()
        mock_plan = _make_mock_plan()
        mock_plan.limits = {"fields": 10}

        with patch("src.main.BillingRepository") as MockRepo:
            repo_instance = MagicMock()
            repo_instance.tenants.get_by_tenant_id = AsyncMock(return_value=_make_mock_tenant())
            repo_instance.subscriptions.get_by_tenant = AsyncMock(return_value=_make_mock_subscription())
            repo_instance.plans.get_by_plan_id = AsyncMock(return_value=mock_plan)
            repo_instance.usage_records.get_metric_count = AsyncMock(return_value=15)
            MockRepo.return_value = repo_instance

            result = await check_usage_limit_db(mock_db, "t-001", "fields")
            assert result["allowed"] is False
            assert result["used"] == 15

    @pytest.mark.asyncio
    async def test_calculate_overage_charges_empty_limits(self):
        from src.main import calculate_overage_charges_db

        mock_db = AsyncMock()
        result = await calculate_overage_charges_db(mock_db, "t-001", {})
        assert result == []

    @pytest.mark.asyncio
    async def test_calculate_overage_charges_no_overage(self):
        from src.main import calculate_overage_charges_db

        mock_db = AsyncMock()

        with patch("src.main.BillingRepository") as MockRepo:
            repo_instance = MagicMock()
            repo_instance.usage_records.get_metric_count = AsyncMock(return_value=3)
            MockRepo.return_value = repo_instance

            result = await calculate_overage_charges_db(mock_db, "t-001", {"fields": 10})
            assert result == []

    @pytest.mark.asyncio
    async def test_calculate_overage_charges_with_overage(self):
        from src.main import calculate_overage_charges_db

        mock_db = AsyncMock()

        with patch("src.main.BillingRepository") as MockRepo:
            repo_instance = MagicMock()
            repo_instance.usage_records.get_metric_count = AsyncMock(return_value=15)
            MockRepo.return_value = repo_instance

            result = await calculate_overage_charges_db(mock_db, "t-001", {"fields": 10})
            assert len(result) == 1
            assert result[0].quantity == 5  # 15 - 10 = 5 excess
            assert result[0].is_usage_based is True

    @pytest.mark.asyncio
    async def test_calculate_overage_charges_unlimited_skipped(self):
        from src.main import calculate_overage_charges_db

        mock_db = AsyncMock()

        with patch("src.main.BillingRepository") as MockRepo:
            repo_instance = MagicMock()
            MockRepo.return_value = repo_instance

            result = await calculate_overage_charges_db(mock_db, "t-001", {"fields": -1})
            assert result == []
            # get_metric_count should NOT have been called for unlimited
            repo_instance.usage_records.get_metric_count.assert_not_called()
