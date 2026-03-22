"""
Tests for billing-core repository layer.
Covers: BillingRepository facade, all sub-repository classes.
All database calls are mocked via AsyncSession.
"""

import sys
import os
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = ""


def make_mock_session():
    """Create a mock AsyncSession with common behaviors."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()
    return session


# ============================================================
# Test BillingRepository Facade
# ============================================================


class TestBillingRepository:
    """Test the combined BillingRepository facade"""

    def test_billing_repository_init(self):
        from src.repository import BillingRepository

        mock_db = make_mock_session()
        repo = BillingRepository(mock_db)

        assert repo.db is mock_db
        assert repo.plans is not None
        assert repo.tenants is not None
        assert repo.subscriptions is not None
        assert repo.invoices is not None
        assert repo.payments is not None
        assert repo.usage_records is not None

    @pytest.mark.asyncio
    async def test_billing_repository_commit(self):
        from src.repository import BillingRepository

        mock_db = make_mock_session()
        repo = BillingRepository(mock_db)
        await repo.commit()
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_billing_repository_rollback(self):
        from src.repository import BillingRepository

        mock_db = make_mock_session()
        repo = BillingRepository(mock_db)
        await repo.rollback()
        mock_db.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_billing_repository_refresh(self):
        from src.repository import BillingRepository

        mock_db = make_mock_session()
        repo = BillingRepository(mock_db)
        mock_instance = MagicMock()
        await repo.refresh(mock_instance)
        mock_db.refresh.assert_awaited_once_with(mock_instance)


# ============================================================
# Test PlanRepository
# ============================================================


class TestPlanRepository:
    """Test PlanRepository CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_plan(self):
        from src.repository import PlanRepository
        from src.models import PlanTier

        mock_db = make_mock_session()
        repo = PlanRepository(mock_db)

        plan = await repo.create(
            plan_id="test",
            name="Test",
            name_ar="تجربة",
            description="Test plan",
            description_ar="خطة تجريبية",
            tier=PlanTier.STARTER,
            pricing={"monthly_usd": "29"},
            features={"fields": True},
            limits={"fields": 10},
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_id(self):
        from src.repository import PlanRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(plan_id="test")
        mock_db.execute.return_value = mock_result

        repo = PlanRepository(mock_db)
        result = await repo.get_by_id(uuid.uuid4())
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_by_plan_id(self):
        from src.repository import PlanRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(plan_id="starter")
        mock_db.execute.return_value = mock_result

        repo = PlanRepository(mock_db)
        result = await repo.get_by_plan_id("starter")
        assert result.plan_id == "starter"

    @pytest.mark.asyncio
    async def test_list_all(self):
        from src.repository import PlanRepository

        mock_db = make_mock_session()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo = PlanRepository(mock_db)
        plans = await repo.list_all(active_only=True)
        assert len(plans) == 2

    @pytest.mark.asyncio
    async def test_list_all_no_filter(self):
        from src.repository import PlanRepository

        mock_db = make_mock_session()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo = PlanRepository(mock_db)
        plans = await repo.list_all(active_only=False)
        assert plans == []

    @pytest.mark.asyncio
    async def test_update_plan(self):
        from src.repository import PlanRepository

        mock_db = make_mock_session()
        # First call for update, second call for get_by_plan_id
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(plan_id="test")
        mock_db.execute.return_value = mock_result

        repo = PlanRepository(mock_db)
        result = await repo.update("test", name="Updated")
        mock_db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_delete_plan(self):
        from src.repository import PlanRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_db.execute.return_value = mock_result

        repo = PlanRepository(mock_db)
        result = await repo.delete("test")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_plan_not_found(self):
        from src.repository import PlanRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_db.execute.return_value = mock_result

        repo = PlanRepository(mock_db)
        result = await repo.delete("nonexistent")
        assert result is False


# ============================================================
# Test TenantRepository
# ============================================================


class TestTenantRepository:
    """Test TenantRepository operations"""

    @pytest.mark.asyncio
    async def test_create_tenant(self):
        from src.repository import TenantRepository

        mock_db = make_mock_session()
        repo = TenantRepository(mock_db)

        await repo.create(
            tenant_id="t-001",
            name="Test Tenant",
            name_ar="مستأجر",
            contact={"email": "test@example.com"},
        )
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_count_total(self):
        from src.repository import TenantRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 42
        mock_db.execute.return_value = mock_result

        repo = TenantRepository(mock_db)
        count = await repo.count_total(active_only=True)
        assert count == 42

    @pytest.mark.asyncio
    async def test_count_total_all(self):
        from src.repository import TenantRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 50
        mock_db.execute.return_value = mock_result

        repo = TenantRepository(mock_db)
        count = await repo.count_total(active_only=False)
        assert count == 50

    @pytest.mark.asyncio
    async def test_delete_tenant(self):
        from src.repository import TenantRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_db.execute.return_value = mock_result

        repo = TenantRepository(mock_db)
        result = await repo.delete("t-001")
        assert result is True


# ============================================================
# Test SubscriptionRepository
# ============================================================


class TestSubscriptionRepository:
    """Test SubscriptionRepository operations"""

    @pytest.mark.asyncio
    async def test_create_subscription(self):
        from src.repository import SubscriptionRepository
        from src.models import BillingCycle

        mock_db = make_mock_session()
        repo = SubscriptionRepository(mock_db)

        await repo.create(
            tenant_id="t-001",
            plan_id="starter",
            billing_cycle=BillingCycle.MONTHLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cancel_subscription_not_found(self):
        from src.repository import SubscriptionRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        repo = SubscriptionRepository(mock_db)
        result = await repo.cancel(uuid.uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_cancel_subscription_immediate(self):
        from src.repository import SubscriptionRepository

        mock_db = make_mock_session()
        mock_sub = MagicMock(id=uuid.uuid4())
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_sub
        mock_db.execute.return_value = mock_result

        repo = SubscriptionRepository(mock_db)
        result = await repo.cancel(mock_sub.id, immediate=True)
        # Should have called execute for both get and update
        assert mock_db.execute.await_count >= 2

    @pytest.mark.asyncio
    async def test_get_due_for_billing_default_date(self):
        from src.repository import SubscriptionRepository

        mock_db = make_mock_session()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_due_for_billing()
        assert result == []

    @pytest.mark.asyncio
    async def test_count_by_status(self):
        from src.repository import SubscriptionRepository
        from src.models import SubscriptionStatus

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (SubscriptionStatus.ACTIVE, 10),
            (SubscriptionStatus.TRIAL, 3),
        ]
        mock_db.execute.return_value = mock_result

        repo = SubscriptionRepository(mock_db)
        counts = await repo.count_by_status()
        assert counts["active"] == 10
        assert counts["trial"] == 3

    @pytest.mark.asyncio
    async def test_count_by_plan(self):
        from src.repository import SubscriptionRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.all.return_value = [("starter", 5), ("professional", 3)]
        mock_db.execute.return_value = mock_result

        repo = SubscriptionRepository(mock_db)
        counts = await repo.count_by_plan()
        assert counts["starter"] == 5


# ============================================================
# Test InvoiceRepository
# ============================================================


class TestInvoiceRepository:
    """Test InvoiceRepository operations"""

    @pytest.mark.asyncio
    async def test_create_invoice(self):
        from src.repository import InvoiceRepository
        from src.models import Currency

        mock_db = make_mock_session()
        repo = InvoiceRepository(mock_db)

        await repo.create(
            invoice_number="SAH-2025-0001",
            tenant_id="t-001",
            subscription_id=uuid.uuid4(),
            currency=Currency.USD,
            issue_date=date(2025, 1, 1),
            due_date=date(2025, 1, 8),
            subtotal=Decimal("29.00"),
            total=Decimal("29.00"),
            amount_due=Decimal("29.00"),
            line_items=[{"description": "Test", "amount": 29.0}],
        )
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_paid_full(self):
        from src.repository import InvoiceRepository
        from src.models import InvoiceStatus

        mock_db = make_mock_session()
        invoice_id = uuid.uuid4()

        # First call: get_by_id returns invoice
        mock_invoice = MagicMock()
        mock_invoice.amount_paid = Decimal("0")
        mock_invoice.total = Decimal("29.00")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_invoice
        mock_db.execute.return_value = mock_result

        repo = InvoiceRepository(mock_db)
        result = await repo.mark_paid(invoice_id, Decimal("29.00"))

        # Should update with PAID status since full amount covered
        mock_db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_mark_paid_not_found(self):
        from src.repository import InvoiceRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        repo = InvoiceRepository(mock_db)
        result = await repo.mark_paid(uuid.uuid4(), Decimal("10"))
        assert result is None

    @pytest.mark.asyncio
    async def test_get_overdue_default_date(self):
        from src.repository import InvoiceRepository

        mock_db = make_mock_session()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo = InvoiceRepository(mock_db)
        result = await repo.get_overdue()
        assert result == []

    @pytest.mark.asyncio
    async def test_get_total_revenue(self):
        from src.repository import InvoiceRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = Decimal("1500.00")
        mock_db.execute.return_value = mock_result

        repo = InvoiceRepository(mock_db)
        total = await repo.get_total_revenue()
        assert total == Decimal("1500.00")

    @pytest.mark.asyncio
    async def test_get_total_revenue_none(self):
        from src.repository import InvoiceRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        repo = InvoiceRepository(mock_db)
        total = await repo.get_total_revenue()
        assert total == Decimal("0")

    @pytest.mark.asyncio
    async def test_get_total_revenue_with_filters(self):
        from src.repository import InvoiceRepository
        from src.models import Currency

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = Decimal("500.00")
        mock_db.execute.return_value = mock_result

        repo = InvoiceRepository(mock_db)
        total = await repo.get_total_revenue(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            currency=Currency.USD,
        )
        assert total == Decimal("500.00")


# ============================================================
# Test PaymentRepository
# ============================================================


class TestPaymentRepository:
    """Test PaymentRepository operations"""

    @pytest.mark.asyncio
    async def test_create_payment(self):
        from src.repository import PaymentRepository
        from src.models import Currency, PaymentMethod

        mock_db = make_mock_session()
        repo = PaymentRepository(mock_db)

        await repo.create(
            invoice_id=uuid.uuid4(),
            tenant_id="t-001",
            amount=Decimal("29.00"),
            currency=Currency.USD,
            method=PaymentMethod.CREDIT_CARD,
        )
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_succeeded(self):
        from src.repository import PaymentRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_result

        repo = PaymentRepository(mock_db)
        result = await repo.mark_succeeded(uuid.uuid4(), external_id="ch_123")
        mock_db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_mark_failed(self):
        from src.repository import PaymentRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_result

        repo = PaymentRepository(mock_db)
        result = await repo.mark_failed(uuid.uuid4(), "Insufficient funds")
        mock_db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_total_by_method(self):
        from src.repository import PaymentRepository
        from src.models import PaymentMethod

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (PaymentMethod.CREDIT_CARD, Decimal("500")),
            (PaymentMethod.THARWATT, Decimal("300")),
        ]
        mock_db.execute.return_value = mock_result

        repo = PaymentRepository(mock_db)
        totals = await repo.get_total_by_method()
        assert totals["credit_card"] == Decimal("500")
        assert totals["tharwatt"] == Decimal("300")

    @pytest.mark.asyncio
    async def test_get_total_by_method_with_dates(self):
        from src.repository import PaymentRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        repo = PaymentRepository(mock_db)
        totals = await repo.get_total_by_method(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        assert totals == {}


# ============================================================
# Test UsageRecordRepository
# ============================================================


class TestUsageRecordRepository:
    """Test UsageRecordRepository operations"""

    @pytest.mark.asyncio
    async def test_create_usage_record(self):
        from src.repository import UsageRecordRepository

        mock_db = make_mock_session()
        repo = UsageRecordRepository(mock_db)

        await repo.create(
            subscription_id=uuid.uuid4(),
            tenant_id="t-001",
            metric_type="api_calls",
            quantity=5,
        )
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_usage_summary(self):
        from src.repository import UsageRecordRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.all.return_value = [("api_calls", 100), ("satellite_analyses", 5)]
        mock_db.execute.return_value = mock_result

        repo = UsageRecordRepository(mock_db)
        summary = await repo.get_usage_summary("t-001")
        assert summary["api_calls"] == 100
        assert summary["satellite_analyses"] == 5

    @pytest.mark.asyncio
    async def test_get_usage_summary_with_dates(self):
        from src.repository import UsageRecordRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        repo = UsageRecordRepository(mock_db)
        summary = await repo.get_usage_summary(
            "t-001",
            start_date=datetime(2025, 1, 1, tzinfo=UTC),
            end_date=datetime(2025, 12, 31, tzinfo=UTC),
        )
        assert summary == {}

    @pytest.mark.asyncio
    async def test_get_metric_count(self):
        from src.repository import UsageRecordRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 42
        mock_db.execute.return_value = mock_result

        repo = UsageRecordRepository(mock_db)
        count = await repo.get_metric_count("t-001", "api_calls")
        assert count == 42

    @pytest.mark.asyncio
    async def test_get_metric_count_none(self):
        from src.repository import UsageRecordRepository

        mock_db = make_mock_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        repo = UsageRecordRepository(mock_db)
        count = await repo.get_metric_count("t-001", "api_calls")
        assert count == 0

    @pytest.mark.asyncio
    async def test_list_by_subscription_with_filters(self):
        from src.repository import UsageRecordRepository

        mock_db = make_mock_session()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo = UsageRecordRepository(mock_db)
        records = await repo.list_by_subscription(
            subscription_id=uuid.uuid4(),
            metric_type="api_calls",
            start_date=datetime(2025, 1, 1, tzinfo=UTC),
            end_date=datetime(2025, 12, 31, tzinfo=UTC),
        )
        assert len(records) == 2

    @pytest.mark.asyncio
    async def test_list_by_tenant_with_filters(self):
        from src.repository import UsageRecordRepository

        mock_db = make_mock_session()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo = UsageRecordRepository(mock_db)
        records = await repo.list_by_tenant(
            tenant_id="t-001",
            metric_type="fields",
            start_date=datetime(2025, 1, 1, tzinfo=UTC),
            end_date=datetime(2025, 12, 31, tzinfo=UTC),
        )
        assert records == []
