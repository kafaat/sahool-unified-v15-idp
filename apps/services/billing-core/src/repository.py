"""
🗂️ SAHOOL Billing Core - Repository Layer
طبقة المستودع - CRUD Operations with Async SQLAlchemy

This module provides database operations for:
- Subscriptions
- Invoices
- Payments
- Usage Records
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, asc, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import (
    BillingCycle,
    Currency,
    Invoice,
    InvoiceStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Plan,
    PlanTier,
    Subscription,
    SubscriptionStatus,
    Tenant,
    UsageRecord,
)

# =============================================================================
# Plan Repository
# =============================================================================


class PlanRepository:
    """
    Repository for Plan operations
    مستودع عمليات الخطط
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        plan_id: str,
        name: str,
        name_ar: str,
        description: str,
        description_ar: str,
        tier: PlanTier,
        pricing: dict[str, Any],
        features: dict[str, Any],
        limits: dict[str, Any],
        trial_days: int = 14,
        is_active: bool = True,
    ) -> Plan:
        """Create a new plan - إنشاء خطة جديدة"""
        plan = Plan(
            plan_id=plan_id,
            name=name,
            name_ar=name_ar,
            description=description,
            description_ar=description_ar,
            tier=tier,
            pricing=pricing,
            features=features,
            limits=limits,
            trial_days=trial_days,
            is_active=is_active,
        )

        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)

        return plan

    async def get_by_id(self, plan_id: uuid.UUID) -> Plan | None:
        """Get plan by UUID - الحصول على خطة بواسطة المعرف UUID"""
        result = await self.db.execute(select(Plan).where(Plan.id == plan_id))
        return result.scalar_one_or_none()

    async def get_by_plan_id(self, plan_id: str) -> Plan | None:
        """Get plan by plan_id - الحصول على خطة بواسطة معرف الخطة"""
        result = await self.db.execute(select(Plan).where(Plan.plan_id == plan_id))
        return result.scalar_one_or_none()

    async def list_all(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Plan]:
        """List all plans - قائمة جميع الخطط"""
        query = select(Plan)

        if active_only:
            query = query.where(Plan.is_active == True)

        query = query.order_by(asc(Plan.tier)).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        plan_id: str,
        **kwargs,
    ) -> Plan | None:
        """Update plan - تحديث الخطة"""
        kwargs["updated_at"] = datetime.utcnow()

        await self.db.execute(
            update(Plan).where(Plan.plan_id == plan_id).values(**kwargs)
        )
        await self.db.commit()

        return await self.get_by_plan_id(plan_id)

    async def delete(self, plan_id: str) -> bool:
        """Delete plan (soft delete by setting is_active=False) - حذف خطة"""
        result = await self.db.execute(
            update(Plan)
            .where(Plan.plan_id == plan_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await self.db.commit()

        return result.rowcount > 0

    async def upsert(
        self,
        plan_id: str,
        name: str,
        name_ar: str,
        description: str,
        description_ar: str,
        tier: PlanTier,
        pricing: dict[str, Any],
        features: dict[str, Any],
        limits: dict[str, Any],
        trial_days: int = 14,
        is_active: bool = True,
    ) -> Plan:
        """Create or update plan - إنشاء أو تحديث خطة"""
        existing = await self.get_by_plan_id(plan_id)

        if existing:
            return await self.update(
                plan_id=plan_id,
                name=name,
                name_ar=name_ar,
                description=description,
                description_ar=description_ar,
                tier=tier,
                pricing=pricing,
                features=features,
                limits=limits,
                trial_days=trial_days,
                is_active=is_active,
            )
        else:
            return await self.create(
                plan_id=plan_id,
                name=name,
                name_ar=name_ar,
                description=description,
                description_ar=description_ar,
                tier=tier,
                pricing=pricing,
                features=features,
                limits=limits,
                trial_days=trial_days,
                is_active=is_active,
            )


# =============================================================================
# Tenant Repository
# =============================================================================


class TenantRepository:
    """
    Repository for Tenant operations
    مستودع عمليات المستأجرين
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id: str,
        name: str,
        name_ar: str,
        contact: dict[str, Any],
        tax_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        is_active: bool = True,
    ) -> Tenant:
        """Create a new tenant - إنشاء مستأجر جديد"""
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            name_ar=name_ar,
            contact=contact,
            tax_id=tax_id,
            extra_metadata=metadata or {},
            is_active=is_active,
        )

        self.db.add(tenant)
        await self.db.commit()
        await self.db.refresh(tenant)

        return tenant

    async def get_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        """Get tenant by UUID - الحصول على مستأجر بواسطة المعرف UUID"""
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        return result.scalar_one_or_none()

    async def get_by_tenant_id(self, tenant_id: str) -> Tenant | None:
        """Get tenant by tenant_id - الحصول على مستأجر بواسطة معرف المستأجر"""
        result = await self.db.execute(
            select(Tenant).where(Tenant.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Tenant]:
        """List all tenants - قائمة جميع المستأجرين"""
        query = select(Tenant)

        if active_only:
            query = query.where(Tenant.is_active == True)

        query = query.order_by(desc(Tenant.created_at)).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        tenant_id: str,
        **kwargs,
    ) -> Tenant | None:
        """Update tenant - تحديث المستأجر"""
        kwargs["updated_at"] = datetime.utcnow()

        await self.db.execute(
            update(Tenant).where(Tenant.tenant_id == tenant_id).values(**kwargs)
        )
        await self.db.commit()

        return await self.get_by_tenant_id(tenant_id)

    async def delete(self, tenant_id: str) -> bool:
        """Delete tenant (soft delete by setting is_active=False) - حذف مستأجر"""
        result = await self.db.execute(
            update(Tenant)
            .where(Tenant.tenant_id == tenant_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await self.db.commit()

        return result.rowcount > 0

    async def count_total(self, active_only: bool = True) -> int:
        """Count total tenants - عد إجمالي المستأجرين"""
        query = select(func.count(Tenant.id))

        if active_only:
            query = query.where(Tenant.is_active == True)

        result = await self.db.execute(query)
        return result.scalar_one()


# =============================================================================
# Subscription Repository
# =============================================================================


class SubscriptionRepository:
    """
    Repository for Subscription operations
    مستودع عمليات الاشتراكات
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id: str,
        plan_id: str,
        billing_cycle: BillingCycle,
        start_date: date,
        end_date: date,
        status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
        currency: Currency = Currency.USD,
        trial_end_date: date | None = None,
        payment_method: PaymentMethod | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Subscription:
        """Create a new subscription - إنشاء اشتراك جديد"""
        subscription = Subscription(
            tenant_id=tenant_id,
            plan_id=plan_id,
            billing_cycle=billing_cycle,
            status=status,
            currency=currency,
            start_date=start_date,
            end_date=end_date,
            trial_end_date=trial_end_date,
            next_billing_date=trial_end_date or end_date,
            payment_method=payment_method,
            extra_metadata=metadata or {},
        )

        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def get_by_id(self, subscription_id: uuid.UUID) -> Subscription | None:
        """Get subscription by ID - الحصول على اشتراك بواسطة المعرف"""
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tenant(
        self,
        tenant_id: str,
        status: SubscriptionStatus | None = None,
    ) -> Subscription | None:
        """Get active subscription for tenant - الحصول على اشتراك نشط للمستأجر"""
        query = select(Subscription).where(Subscription.tenant_id == tenant_id)

        if status:
            query = query.where(Subscription.status == status)
        else:
            # Get active or trial subscriptions
            query = query.where(
                Subscription.status.in_(
                    [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]
                )
            )

        query = query.order_by(desc(Subscription.created_at))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Subscription]:
        """List all subscriptions for tenant - قائمة جميع اشتراكات المستأجر"""
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.tenant_id == tenant_id)
            .order_by(desc(Subscription.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update(
        self,
        subscription_id: uuid.UUID,
        **kwargs,
    ) -> Subscription | None:
        """Update subscription - تحديث الاشتراك"""
        # Add updated_at timestamp
        kwargs["updated_at"] = datetime.utcnow()

        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(**kwargs)
        )
        await self.db.commit()

        return await self.get_by_id(subscription_id)

    async def cancel(
        self,
        subscription_id: uuid.UUID,
        immediate: bool = False,
    ) -> Subscription | None:
        """Cancel subscription - إلغاء الاشتراك"""
        subscription = await self.get_by_id(subscription_id)
        if not subscription:
            return None

        update_data = {
            "canceled_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        if immediate:
            update_data["status"] = SubscriptionStatus.CANCELED
            update_data["end_date"] = date.today()

        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(**update_data)
        )
        await self.db.commit()

        return await self.get_by_id(subscription_id)

    async def get_due_for_billing(
        self,
        billing_date: date = None,
    ) -> list[Subscription]:
        """Get subscriptions due for billing - الحصول على الاشتراكات المستحقة للفوترة"""
        if billing_date is None:
            billing_date = date.today()

        result = await self.db.execute(
            select(Subscription).where(
                and_(
                    Subscription.next_billing_date <= billing_date,
                    Subscription.status.in_(
                        [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]
                    ),
                )
            )
        )
        return list(result.scalars().all())

    async def count_by_status(self) -> dict[str, int]:
        """Count subscriptions by status - عد الاشتراكات حسب الحالة"""
        result = await self.db.execute(
            select(Subscription.status, func.count(Subscription.id)).group_by(
                Subscription.status
            )
        )

        return {status.value: count for status, count in result.all()}

    async def count_by_plan(self) -> dict[str, int]:
        """Count subscriptions by plan - عد الاشتراكات حسب الخطة"""
        result = await self.db.execute(
            select(Subscription.plan_id, func.count(Subscription.id)).group_by(
                Subscription.plan_id
            )
        )

        return dict(result.all())


# =============================================================================
# Invoice Repository
# =============================================================================


class InvoiceRepository:
    """
    Repository for Invoice operations
    مستودع عمليات الفواتير
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        invoice_number: str,
        tenant_id: str,
        subscription_id: uuid.UUID,
        currency: Currency,
        issue_date: date,
        due_date: date,
        subtotal: Decimal,
        total: Decimal,
        amount_due: Decimal,
        line_items: list[dict[str, Any]],
        status: InvoiceStatus = InvoiceStatus.DRAFT,
        tax_rate: Decimal = Decimal("0"),
        tax_amount: Decimal = Decimal("0"),
        discount_amount: Decimal = Decimal("0"),
        notes: str | None = None,
        notes_ar: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Invoice:
        """Create a new invoice - إنشاء فاتورة جديدة"""
        invoice = Invoice(
            invoice_number=invoice_number,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            status=status,
            currency=currency,
            issue_date=issue_date,
            due_date=due_date,
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total=total,
            amount_due=amount_due,
            line_items=line_items,
            notes=notes,
            notes_ar=notes_ar,
            extra_metadata=metadata or {},
        )

        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def get_by_id(
        self,
        invoice_id: uuid.UUID,
        include_payments: bool = False,
    ) -> Invoice | None:
        """Get invoice by ID - الحصول على فاتورة بواسطة المعرف"""
        query = select(Invoice).where(Invoice.id == invoice_id)

        if include_payments:
            query = query.options(selectinload(Invoice.payments))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_invoice_number(self, invoice_number: str) -> Invoice | None:
        """Get invoice by invoice number - الحصول على فاتورة بواسطة رقم الفاتورة"""
        result = await self.db.execute(
            select(Invoice).where(Invoice.invoice_number == invoice_number)
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: InvoiceStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Invoice]:
        """List invoices for tenant - قائمة فواتير المستأجر"""
        query = select(Invoice).where(Invoice.tenant_id == tenant_id)

        if status:
            query = query.where(Invoice.status == status)

        query = query.order_by(desc(Invoice.issue_date)).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_by_subscription(
        self,
        subscription_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Invoice]:
        """List invoices for subscription - قائمة فواتير الاشتراك"""
        result = await self.db.execute(
            select(Invoice)
            .where(Invoice.subscription_id == subscription_id)
            .order_by(desc(Invoice.issue_date))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update(
        self,
        invoice_id: uuid.UUID,
        **kwargs,
    ) -> Invoice | None:
        """Update invoice - تحديث الفاتورة"""
        await self.db.execute(
            update(Invoice).where(Invoice.id == invoice_id).values(**kwargs)
        )
        await self.db.commit()

        return await self.get_by_id(invoice_id)

    async def mark_paid(
        self,
        invoice_id: uuid.UUID,
        amount: Decimal,
    ) -> Invoice | None:
        """Mark invoice as paid - تحديد الفاتورة كمدفوعة"""
        invoice = await self.get_by_id(invoice_id)
        if not invoice:
            return None

        new_amount_paid = invoice.amount_paid + amount
        new_amount_due = invoice.total - new_amount_paid

        update_data = {
            "amount_paid": new_amount_paid,
            "amount_due": new_amount_due,
        }

        # Mark as paid if fully paid
        if new_amount_due <= 0:
            update_data["status"] = InvoiceStatus.PAID
            update_data["paid_date"] = date.today()

        await self.db.execute(
            update(Invoice).where(Invoice.id == invoice_id).values(**update_data)
        )
        await self.db.commit()

        return await self.get_by_id(invoice_id)

    async def get_overdue(
        self,
        as_of_date: date = None,
    ) -> list[Invoice]:
        """Get overdue invoices - الحصول على الفواتير المتأخرة"""
        if as_of_date is None:
            as_of_date = date.today()

        result = await self.db.execute(
            select(Invoice).where(
                and_(
                    Invoice.due_date < as_of_date,
                    Invoice.status.in_([InvoiceStatus.PENDING, InvoiceStatus.OVERDUE]),
                    Invoice.amount_due > 0,
                )
            )
        )
        return list(result.scalars().all())

    async def get_total_revenue(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        currency: Currency | None = None,
    ) -> Decimal:
        """Calculate total revenue - حساب إجمالي الإيرادات"""
        query = select(func.sum(Invoice.total)).where(
            Invoice.status == InvoiceStatus.PAID
        )

        if start_date:
            query = query.where(Invoice.paid_date >= start_date)

        if end_date:
            query = query.where(Invoice.paid_date <= end_date)

        if currency:
            query = query.where(Invoice.currency == currency)

        result = await self.db.execute(query)
        total = result.scalar_one_or_none()

        return total or Decimal("0")


# =============================================================================
# Payment Repository
# =============================================================================


class PaymentRepository:
    """
    Repository for Payment operations
    مستودع عمليات المدفوعات
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        invoice_id: uuid.UUID,
        tenant_id: str,
        amount: Decimal,
        currency: Currency,
        method: PaymentMethod,
        status: PaymentStatus = PaymentStatus.PENDING,
        metadata: dict[str, Any] | None = None,
    ) -> Payment:
        """Create a new payment - إنشاء دفعة جديدة"""
        payment = Payment(
            invoice_id=invoice_id,
            tenant_id=tenant_id,
            amount=amount,
            currency=currency,
            method=method,
            status=status,
            extra_metadata=metadata or {},
        )

        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        """Get payment by ID - الحصول على دفعة بواسطة المعرف"""
        result = await self.db.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()

    async def list_by_invoice(
        self,
        invoice_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Payment]:
        """List payments for invoice - قائمة دفعات الفاتورة"""
        result = await self.db.execute(
            select(Payment)
            .where(Payment.invoice_id == invoice_id)
            .order_by(desc(Payment.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: PaymentStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Payment]:
        """List payments for tenant - قائمة دفعات المستأجر"""
        query = select(Payment).where(Payment.tenant_id == tenant_id)

        if status:
            query = query.where(Payment.status == status)

        query = query.order_by(desc(Payment.created_at)).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        payment_id: uuid.UUID,
        **kwargs,
    ) -> Payment | None:
        """Update payment - تحديث الدفعة"""
        await self.db.execute(
            update(Payment).where(Payment.id == payment_id).values(**kwargs)
        )
        await self.db.commit()

        return await self.get_by_id(payment_id)

    async def mark_succeeded(
        self,
        payment_id: uuid.UUID,
        processed_at: datetime | None = None,
        external_id: str | None = None,
    ) -> Payment | None:
        """Mark payment as succeeded - تحديد الدفعة كناجحة"""
        update_data = {
            "status": PaymentStatus.SUCCEEDED,
            "paid_at": processed_at or datetime.utcnow(),
            "processed_at": processed_at or datetime.utcnow(),
        }

        if external_id:
            update_data["stripe_payment_id"] = external_id

        await self.db.execute(
            update(Payment).where(Payment.id == payment_id).values(**update_data)
        )
        await self.db.commit()

        return await self.get_by_id(payment_id)

    async def mark_failed(
        self,
        payment_id: uuid.UUID,
        failure_reason: str,
    ) -> Payment | None:
        """Mark payment as failed - تحديد الدفعة كفاشلة"""
        await self.db.execute(
            update(Payment)
            .where(Payment.id == payment_id)
            .values(
                status=PaymentStatus.FAILED,
                failure_reason=failure_reason,
            )
        )
        await self.db.commit()

        return await self.get_by_id(payment_id)

    async def get_total_by_method(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict[str, Decimal]:
        """Get total payments by method - إجمالي المدفوعات حسب الطريقة"""
        query = select(Payment.method, func.sum(Payment.amount)).where(
            Payment.status == PaymentStatus.SUCCEEDED
        )

        if start_date:
            query = query.where(Payment.paid_at >= start_date)

        if end_date:
            query = query.where(Payment.paid_at <= end_date)

        query = query.group_by(Payment.method)

        result = await self.db.execute(query)
        return {method.value: total for method, total in result.all()}


# =============================================================================
# Usage Record Repository
# =============================================================================


class UsageRecordRepository:
    """
    Repository for Usage Record operations
    مستودع عمليات سجلات الاستخدام
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        subscription_id: uuid.UUID,
        tenant_id: str,
        metric_type: str,
        quantity: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> UsageRecord:
        """Create a new usage record - إنشاء سجل استخدام جديد"""
        record = UsageRecord(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            metric_type=metric_type,
            quantity=quantity,
            extra_metadata=metadata or {},
        )

        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        return record

    async def get_by_id(self, record_id: uuid.UUID) -> UsageRecord | None:
        """Get usage record by ID - الحصول على سجل استخدام بواسطة المعرف"""
        result = await self.db.execute(
            select(UsageRecord).where(UsageRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def list_by_subscription(
        self,
        subscription_id: uuid.UUID,
        metric_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[UsageRecord]:
        """List usage records for subscription - قائمة سجلات استخدام الاشتراك"""
        query = select(UsageRecord).where(
            UsageRecord.subscription_id == subscription_id
        )

        if metric_type:
            query = query.where(UsageRecord.metric_type == metric_type)

        if start_date:
            query = query.where(UsageRecord.recorded_at >= start_date)

        if end_date:
            query = query.where(UsageRecord.recorded_at <= end_date)

        query = (
            query.order_by(desc(UsageRecord.recorded_at)).limit(limit).offset(offset)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_by_tenant(
        self,
        tenant_id: str,
        metric_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[UsageRecord]:
        """List usage records for tenant - قائمة سجلات استخدام المستأجر"""
        query = select(UsageRecord).where(UsageRecord.tenant_id == tenant_id)

        if metric_type:
            query = query.where(UsageRecord.metric_type == metric_type)

        if start_date:
            query = query.where(UsageRecord.recorded_at >= start_date)

        if end_date:
            query = query.where(UsageRecord.recorded_at <= end_date)

        query = (
            query.order_by(desc(UsageRecord.recorded_at)).limit(limit).offset(offset)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_usage_summary(
        self,
        tenant_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, int]:
        """Get usage summary by metric - ملخص الاستخدام حسب المقياس"""
        query = select(UsageRecord.metric_type, func.sum(UsageRecord.quantity)).where(
            UsageRecord.tenant_id == tenant_id
        )

        if start_date:
            query = query.where(UsageRecord.recorded_at >= start_date)

        if end_date:
            query = query.where(UsageRecord.recorded_at <= end_date)

        query = query.group_by(UsageRecord.metric_type)

        result = await self.db.execute(query)
        return {metric: int(total) for metric, total in result.all()}

    async def get_metric_count(
        self,
        tenant_id: str,
        metric_type: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """Get total count for specific metric - إجمالي العدد لمقياس محدد"""
        query = select(func.sum(UsageRecord.quantity)).where(
            and_(
                UsageRecord.tenant_id == tenant_id,
                UsageRecord.metric_type == metric_type,
            )
        )

        if start_date:
            query = query.where(UsageRecord.recorded_at >= start_date)

        if end_date:
            query = query.where(UsageRecord.recorded_at <= end_date)

        result = await self.db.execute(query)
        total = result.scalar_one_or_none()

        return int(total) if total else 0


# =============================================================================
# Combined Repository (Facade Pattern)
# =============================================================================


class BillingRepository:
    """
    Combined repository providing access to all billing operations
    مستودع شامل يوفر الوصول إلى جميع عمليات الفوترة

    This class acts as a facade, providing a single entry point
    for all database operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.plans = PlanRepository(db)
        self.tenants = TenantRepository(db)
        self.subscriptions = SubscriptionRepository(db)
        self.invoices = InvoiceRepository(db)
        self.payments = PaymentRepository(db)
        self.usage_records = UsageRecordRepository(db)

    async def commit(self) -> None:
        """Commit the current transaction - تنفيذ المعاملة الحالية"""
        await self.db.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction - التراجع عن المعاملة الحالية"""
        await self.db.rollback()

    async def refresh(self, instance) -> None:
        """Refresh an instance from the database - تحديث مثيل من قاعدة البيانات"""
        await self.db.refresh(instance)
