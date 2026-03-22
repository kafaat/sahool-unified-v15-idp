"""
Extended tests for billing-core main.py.
Covers: API endpoints, scheduled jobs, startup initialization, payment processing.
"""

import sys
import os
import json
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"


# ============================================================
# Helpers
# ============================================================

def _mock_plan(plan_id="starter", tier="starter", pricing=None):
    plan = MagicMock()
    plan.plan_id = plan_id
    plan.name = "Starter"
    plan.name_ar = "المبتدئ"
    plan.description = "desc"
    plan.description_ar = "وصف"
    plan.tier = MagicMock(value=tier)
    plan.pricing = pricing or {"monthly_usd": "29", "quarterly_usd": "79", "yearly_usd": "290"}
    plan.features = {}
    plan.limits = {"fields": 10}
    plan.is_active = True
    plan.trial_days = 14
    plan.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return plan


def _mock_subscription(tenant_id="t-001", plan_id="starter", status="active"):
    sub = MagicMock()
    sub.id = uuid.uuid4()
    sub.tenant_id = tenant_id
    sub.plan_id = plan_id
    sub.status = MagicMock(value=status)
    sub.billing_cycle = MagicMock(value="monthly")
    sub.currency = MagicMock(value="USD")
    sub.start_date = date(2025, 1, 1)
    sub.end_date = date(2025, 1, 31)
    sub.next_billing_date = date(2025, 1, 31)
    sub.trial_end_date = None
    sub.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    sub.canceled_at = None
    return sub


def _mock_tenant(tenant_id="t-001"):
    t = MagicMock()
    t.tenant_id = tenant_id
    t.name = "Test Farm"
    t.name_ar = "مزرعة"
    t.contact = {"email": "test@example.com"}
    t.tax_id = None
    t.is_active = True
    t.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return t


def _mock_invoice(status="pending", total=Decimal("29.00")):
    inv = MagicMock()
    inv.id = uuid.uuid4()
    inv.invoice_number = "SAH-2025-0001"
    inv.tenant_id = "t-001"
    inv.subscription_id = uuid.uuid4()
    inv.status = MagicMock(value=status)
    inv.currency = MagicMock(value="USD")
    inv.issue_date = date(2025, 1, 1)
    inv.due_date = date(2025, 1, 8)
    inv.paid_date = None
    inv.subtotal = total
    inv.tax_amount = Decimal("0")
    inv.discount_amount = Decimal("0")
    inv.total = total
    inv.amount_paid = Decimal("0")
    inv.amount_due = total
    inv.line_items = []
    inv.notes = None
    inv.notes_ar = None
    inv.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return inv


def _mock_payment(status="pending"):
    from src.models import PaymentStatus, PaymentMethod, Currency
    p = MagicMock()
    p.id = uuid.uuid4()
    p.invoice_id = uuid.uuid4()
    p.tenant_id = "t-001"
    p.amount = Decimal("29.00")
    p.currency = MagicMock(value="USD")
    p.status = MagicMock(value=status)
    p.method = MagicMock(value="credit_card")
    p.paid_at = None
    p.stripe_payment_id = None
    p.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return p


# ============================================================
# Test init_nats
# ============================================================


class TestInitNats:
    """Test NATS initialization"""

    @pytest.mark.asyncio
    async def test_init_nats_success(self):
        from src.main import init_nats

        mock_nc = AsyncMock()
        mock_js = AsyncMock()
        mock_nc.jetstream.return_value = mock_js

        with patch("src.main.nats") as mock_nats_mod:
            mock_nats_mod.connect = AsyncMock(return_value=mock_nc)
            await init_nats()

        # Restore globals
        import src.main
        src.main.nats_client = None
        src.main.js = None

    @pytest.mark.asyncio
    async def test_init_nats_failure(self):
        from src.main import init_nats

        with patch("src.main.nats") as mock_nats_mod:
            mock_nats_mod.connect = AsyncMock(side_effect=Exception("Connection refused"))
            await init_nats()  # Should not raise

        import src.main
        src.main.nats_client = None
        src.main.js = None


# ============================================================
# Test Scheduled Jobs
# ============================================================


class TestScheduledJobs:
    """Test scheduled billing jobs"""

    @pytest.mark.asyncio
    async def test_job_generate_invoices_no_due(self):
        from src.main import job_generate_invoices

        mock_db = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.subscriptions.get_due_for_billing = AsyncMock(return_value=[])

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            with patch("src.main.BillingRepository", return_value=mock_repo):
                await job_generate_invoices()

    @pytest.mark.asyncio
    async def test_job_generate_invoices_with_subs(self):
        from src.main import job_generate_invoices

        mock_sub = _mock_subscription()
        mock_invoice = _mock_invoice()

        mock_db = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.subscriptions.get_due_for_billing = AsyncMock(return_value=[mock_sub])
        mock_repo.subscriptions.update = AsyncMock()

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            with patch("src.main.BillingRepository", return_value=mock_repo):
                with patch("src.main.generate_invoice_for_subscription", new_callable=AsyncMock, return_value=mock_invoice):
                    with patch("src.main.get_billing_period_end", return_value=date(2025, 3, 1)):
                        with patch("src.main.publish_event", new_callable=AsyncMock):
                            await job_generate_invoices()

    @pytest.mark.asyncio
    async def test_job_generate_invoices_error_handling(self):
        from src.main import job_generate_invoices

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(side_effect=Exception("DB error"))
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            await job_generate_invoices()  # Should not raise

    @pytest.mark.asyncio
    async def test_job_mark_overdue_invoices(self):
        from src.main import job_mark_overdue_invoices
        from src.models import InvoiceStatus

        mock_inv = _mock_invoice(status="pending")
        mock_inv.status = InvoiceStatus.PENDING

        mock_db = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.invoices.get_overdue = AsyncMock(return_value=[mock_inv])
        mock_repo.invoices.update = AsyncMock()

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            with patch("src.main.BillingRepository", return_value=mock_repo):
                with patch("src.main.publish_event", new_callable=AsyncMock):
                    await job_mark_overdue_invoices()

    @pytest.mark.asyncio
    async def test_job_mark_overdue_error(self):
        from src.main import job_mark_overdue_invoices

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(side_effect=Exception("DB down"))
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            await job_mark_overdue_invoices()  # Should not raise

    @pytest.mark.asyncio
    async def test_job_handle_trial_expiry_no_trials(self):
        from src.main import job_handle_trial_expiry

        mock_db = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.subscriptions.count_by_status = AsyncMock(return_value={})

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            with patch("src.main.BillingRepository", return_value=mock_repo):
                await job_handle_trial_expiry()

    @pytest.mark.asyncio
    async def test_job_handle_trial_expiry_error(self):
        from src.main import job_handle_trial_expiry

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(side_effect=Exception("DB error"))
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            await job_handle_trial_expiry()  # Should not raise

    @pytest.mark.asyncio
    async def test_job_suspend_past_due(self):
        from src.main import job_suspend_past_due

        mock_db = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.invoices.get_overdue = AsyncMock(return_value=[])

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            with patch("src.main.BillingRepository", return_value=mock_repo):
                with patch("src.main.publish_event", new_callable=AsyncMock):
                    await job_suspend_past_due()

    @pytest.mark.asyncio
    async def test_job_suspend_past_due_with_overdue_tenants(self):
        from src.main import job_suspend_past_due
        from src.models import SubscriptionStatus

        mock_inv = _mock_invoice()
        mock_inv.tenant_id = "t-001"

        mock_sub = _mock_subscription()
        mock_sub.status = SubscriptionStatus.ACTIVE

        mock_db = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.invoices.get_overdue = AsyncMock(return_value=[mock_inv])
        mock_repo.subscriptions.get_by_tenant = AsyncMock(return_value=mock_sub)
        mock_repo.subscriptions.update = AsyncMock()

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            with patch("src.main.BillingRepository", return_value=mock_repo):
                with patch("src.main.publish_event", new_callable=AsyncMock):
                    await job_suspend_past_due()

    @pytest.mark.asyncio
    async def test_job_suspend_past_due_error(self):
        from src.main import job_suspend_past_due

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(side_effect=Exception("DB error"))
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            await job_suspend_past_due()  # Should not raise


# ============================================================
# Test Scheduler
# ============================================================


class TestScheduler:
    """Test scheduler initialization"""

    def test_start_scheduler_no_apscheduler(self):
        from src.main import start_scheduler

        with patch.dict("sys.modules", {"apscheduler": None, "apscheduler.schedulers": None, "apscheduler.schedulers.asyncio": None}):
            # Should handle ImportError gracefully
            start_scheduler()

    def test_start_scheduler_with_apscheduler(self):
        from src.main import start_scheduler

        mock_scheduler_cls = MagicMock()
        mock_scheduler = MagicMock()
        mock_scheduler_cls.return_value = mock_scheduler

        mock_trigger_cls = MagicMock()

        with patch.dict("sys.modules", {
            "apscheduler": MagicMock(),
            "apscheduler.schedulers": MagicMock(),
            "apscheduler.schedulers.asyncio": MagicMock(AsyncIOScheduler=mock_scheduler_cls),
            "apscheduler.triggers": MagicMock(),
            "apscheduler.triggers.cron": MagicMock(CronTrigger=mock_trigger_cls),
        }):
            start_scheduler()
            mock_scheduler.start.assert_called_once()

        # Cleanup
        import src.main
        src.main.scheduler = None


# ============================================================
# Test Invoice Generation
# ============================================================


class TestInvoiceGeneration:
    """Test generate_invoice_for_subscription"""

    @pytest.mark.asyncio
    async def test_generate_invoice_plan_not_found(self):
        from src.main import generate_invoice_for_subscription

        mock_db = AsyncMock()
        mock_sub = _mock_subscription()

        with patch("src.main.BillingRepository") as MockRepo:
            repo = MagicMock()
            repo.plans.get_by_plan_id = AsyncMock(return_value=None)
            MockRepo.return_value = repo

            result = await generate_invoice_for_subscription(mock_db, mock_sub)
            assert result is None

    @pytest.mark.asyncio
    async def test_generate_invoice_success(self):
        from src.main import generate_invoice_for_subscription
        import src.models as db_models

        mock_db = AsyncMock()
        mock_sub = _mock_subscription()
        mock_sub.billing_cycle = db_models.BillingCycle.MONTHLY
        mock_sub.currency = db_models.Currency.USD

        mock_plan = _mock_plan()
        mock_invoice = _mock_invoice()

        with patch("src.main.BillingRepository") as MockRepo:
            repo = MagicMock()
            repo.plans.get_by_plan_id = AsyncMock(return_value=mock_plan)
            repo.invoices.create = AsyncMock(return_value=mock_invoice)
            repo.usage_records.get_metric_count = AsyncMock(return_value=0)
            MockRepo.return_value = repo

            with patch("src.main.get_next_invoice_number", new_callable=AsyncMock, return_value="SAH-2025-0001"):
                result = await generate_invoice_for_subscription(mock_db, mock_sub)
                assert result is not None


# ============================================================
# Test Invoice Sequence
# ============================================================


class TestInvoiceSequence:
    """Test invoice number sequence"""

    @pytest.mark.asyncio
    async def test_init_invoice_sequence(self):
        from src.main import init_invoice_sequence

        import src.main
        src.main._invoice_sequence_initialized = False

        mock_db = AsyncMock()
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            await init_invoice_sequence()
            assert src.main._invoice_sequence_initialized is True

        # Cleanup
        src.main._invoice_sequence_initialized = False

    @pytest.mark.asyncio
    async def test_init_invoice_sequence_already_initialized(self):
        from src.main import init_invoice_sequence

        import src.main
        src.main._invoice_sequence_initialized = True

        # Should return immediately
        await init_invoice_sequence()

        # Cleanup
        src.main._invoice_sequence_initialized = False

    @pytest.mark.asyncio
    async def test_init_invoice_sequence_error(self):
        from src.main import init_invoice_sequence

        import src.main
        src.main._invoice_sequence_initialized = False

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(side_effect=Exception("DB error"))
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            await init_invoice_sequence()  # Should not raise
            assert src.main._invoice_sequence_initialized is False

    @pytest.mark.asyncio
    async def test_get_next_invoice_number_success(self):
        from src.main import get_next_invoice_number

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 42
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            result = await get_next_invoice_number()
            year = datetime.now(UTC).year
            assert result == f"SAH-{year}-0042"

    @pytest.mark.asyncio
    async def test_get_next_invoice_number_fallback(self):
        from src.main import get_next_invoice_number

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(side_effect=Exception("Sequence error"))
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            result = await get_next_invoice_number()
            year = datetime.now(UTC).year
            assert result.startswith(f"SAH-{year}-")
            # Fallback uses 8-char hex suffix
            suffix = result.split("-", 2)[2]
            assert len(suffix) == 8


# ============================================================
# Test init_default_plans_in_db
# ============================================================


class TestInitDefaultPlans:
    """Test default plans initialization"""

    @pytest.mark.asyncio
    async def test_init_default_plans_success(self):
        from src.main import init_default_plans_in_db

        mock_db = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.plans.upsert = AsyncMock(return_value=_mock_plan())

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            with patch("src.main.BillingRepository", return_value=mock_repo):
                await init_default_plans_in_db()
                # Should have called upsert 4 times (free, starter, pro, enterprise)
                assert mock_repo.plans.upsert.await_count == 4

    @pytest.mark.asyncio
    async def test_init_default_plans_partial_failure(self):
        from src.main import init_default_plans_in_db

        mock_db = AsyncMock()
        mock_repo = MagicMock()
        call_count = 0

        async def mock_upsert(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("DB constraint error")
            return _mock_plan()

        mock_repo.plans.upsert = mock_upsert

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            with patch("src.main.BillingRepository", return_value=mock_repo):
                await init_default_plans_in_db()  # Should not raise

    @pytest.mark.asyncio
    async def test_init_default_plans_db_error(self):
        from src.main import init_default_plans_in_db

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(side_effect=Exception("Connection refused"))
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("src.database.get_db_context", return_value=mock_ctx):
            await init_default_plans_in_db()  # Should not raise


# ============================================================
# Test call_tharwatt_api
# ============================================================


class TestTharwattApi:
    """Test Tharwatt payment gateway"""

    @pytest.mark.asyncio
    async def test_call_tharwatt_api_success(self):
        from src.main import call_tharwatt_api

        mock_payment = MagicMock()
        mock_payment.payment_id = "pay-001"
        mock_payment.amount = Decimal("25000")
        mock_payment.invoice_id = "inv-001"

        mock_response = MagicMock()
        mock_response.json.return_value = {"transaction_id": "TXN-001", "status": "pending"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await call_tharwatt_api(mock_payment, "+967123456789")
            assert result["transaction_id"] == "TXN-001"

    @pytest.mark.asyncio
    async def test_call_tharwatt_api_error(self):
        from src.main import call_tharwatt_api
        from fastapi import HTTPException
        import httpx

        mock_payment = MagicMock()
        mock_payment.payment_id = "pay-001"
        mock_payment.amount = Decimal("25000")
        mock_payment.invoice_id = "inv-001"

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=httpx.HTTPError("timeout"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await call_tharwatt_api(mock_payment, "+967123456789")
            assert exc_info.value.status_code == 502


# ============================================================
# Test call_stripe_api
# ============================================================


class TestStripeApi:
    """Test Stripe payment API"""

    @pytest.mark.asyncio
    async def test_call_stripe_api_error(self):
        from src.main import call_stripe_api
        from fastapi import HTTPException

        mock_payment = MagicMock()
        mock_payment.amount = Decimal("29.00")
        mock_payment.currency = MagicMock(value="usd")
        mock_payment.payment_id = "pay-001"
        mock_payment.invoice_id = "inv-001"
        mock_payment.tenant_id = "t-001"

        mock_stripe = MagicMock()
        mock_stripe.Charge.create.side_effect = Exception("Card declined")

        with patch.dict("sys.modules", {"stripe": mock_stripe}):
            with patch("src.main.STRIPE_API_KEY", "sk_test_123"):
                with pytest.raises(HTTPException) as exc_info:
                    await call_stripe_api(mock_payment, "tok_123")
                assert exc_info.value.status_code == 502


# ============================================================
# Test publish_event edge cases
# ============================================================


class TestPublishEventEdgeCases:
    """Test publish_event with various data types"""

    @pytest.mark.asyncio
    async def test_publish_event_with_non_dict_data(self):
        from src.main import publish_event

        with patch("src.main.js", None):
            # Should handle non-dict data gracefully
            await publish_event("sahool.test", "simple string data")

    @pytest.mark.asyncio
    async def test_publish_event_with_datetime_data(self):
        from src.main import publish_event

        mock_js = AsyncMock()
        with patch("src.main.js", mock_js):
            await publish_event("sahool.test", {
                "timestamp": datetime.now(UTC),
                "amount": Decimal("29.00"),
                "id": uuid.uuid4(),
            })
            mock_js.publish.assert_awaited_once()


# ============================================================
# Test DB Model Table Args
# ============================================================


class TestDbModelTableArgs:
    """Test DB model table configurations"""

    def test_plan_tablename(self):
        from src.models import Plan
        assert Plan.__tablename__ == "plans"

    def test_tenant_tablename(self):
        from src.models import Tenant
        assert Tenant.__tablename__ == "tenants"

    def test_subscription_tablename(self):
        from src.models import Subscription
        assert Subscription.__tablename__ == "subscriptions"

    def test_invoice_tablename(self):
        from src.models import Invoice
        assert Invoice.__tablename__ == "invoices"

    def test_payment_tablename(self):
        from src.models import Payment
        assert Payment.__tablename__ == "payments"

    def test_usage_record_tablename(self):
        from src.models import UsageRecord
        assert UsageRecord.__tablename__ == "usage_records"


# ============================================================
# Test check_usage_limit_db - plan not found
# ============================================================


class TestCheckUsageLimitPlanNotFound:
    """Test check_usage_limit_db when plan is not found"""

    @pytest.mark.asyncio
    async def test_plan_not_found(self):
        from src.main import check_usage_limit_db

        mock_db = AsyncMock()
        with patch("src.main.BillingRepository") as MockRepo:
            repo = MagicMock()
            repo.tenants.get_by_tenant_id = AsyncMock(return_value=_mock_tenant())
            repo.subscriptions.get_by_tenant = AsyncMock(return_value=_mock_subscription())
            repo.plans.get_by_plan_id = AsyncMock(return_value=None)
            MockRepo.return_value = repo

            result = await check_usage_limit_db(mock_db, "t-001", "fields")
            assert result["allowed"] is False
            assert "Plan not found" in result["reason"]


# ============================================================
# Test Subscription get_by_tenant with status filter
# ============================================================


class TestSubscriptionGetByTenant:
    """Test subscription get_by_tenant with various params"""

    @pytest.mark.asyncio
    async def test_get_by_tenant_with_status(self):
        from src.repository import SubscriptionRepository
        from src.models import SubscriptionStatus

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = _mock_subscription()
        mock_db.execute.return_value = mock_result

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_by_tenant("t-001", status=SubscriptionStatus.ACTIVE)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_by_tenant_no_status(self):
        from src.repository import SubscriptionRepository

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_by_tenant("t-001")
        assert result is None


# ============================================================
# Test Invoice list_by_tenant with various filters
# ============================================================


class TestInvoiceListFilters:
    """Test invoice listing with various filters"""

    @pytest.mark.asyncio
    async def test_list_by_tenant_all(self):
        from src.repository import InvoiceRepository

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [_mock_invoice()]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo = InvoiceRepository(mock_db)
        result = await repo.list_by_tenant(None)  # All tenants
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_by_tenant_with_status(self):
        from src.repository import InvoiceRepository
        from src.models import InvoiceStatus

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo = InvoiceRepository(mock_db)
        result = await repo.list_by_tenant("t-001", status=InvoiceStatus.PAID)
        assert result == []

    @pytest.mark.asyncio
    async def test_list_by_subscription(self):
        from src.repository import InvoiceRepository

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        repo = InvoiceRepository(mock_db)
        result = await repo.list_by_subscription(uuid.uuid4())
        assert result == []
