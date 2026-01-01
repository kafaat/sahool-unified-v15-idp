"""Initial billing schema

Revision ID: 001
Revises:
Create Date: 2025-12-27

Creates the initial database schema for SAHOOL Billing Core:
- subscriptions table
- invoices table
- payments table
- usage_records table
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create initial billing schema
    إنشاء مخطط الفوترة الأولي
    """

    # Create enum types
    op.execute(
        """
        CREATE TYPE subscription_status_enum AS ENUM (
            'active', 'trial', 'past_due', 'canceled', 'suspended', 'expired'
        );
    """
    )

    op.execute(
        """
        CREATE TYPE billing_cycle_enum AS ENUM ('monthly', 'quarterly', 'yearly');
    """
    )

    op.execute(
        """
        CREATE TYPE currency_enum AS ENUM ('USD', 'YER');
    """
    )

    op.execute(
        """
        CREATE TYPE invoice_status_enum AS ENUM (
            'draft', 'pending', 'paid', 'overdue', 'canceled', 'refunded'
        );
    """
    )

    op.execute(
        """
        CREATE TYPE payment_method_enum AS ENUM (
            'credit_card', 'bank_transfer', 'mobile_money', 'cash', 'tharwatt'
        );
    """
    )

    op.execute(
        """
        CREATE TYPE payment_status_enum AS ENUM (
            'pending', 'processing', 'succeeded', 'failed', 'refunded'
        );
    """
    )

    # Create subscriptions table
    op.create_table(
        "subscriptions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            sa.String(length=255),
            nullable=False,
            comment="المستأجر/العميل",
        ),
        sa.Column(
            "plan_id", sa.String(length=255), nullable=False, comment="معرف الخطة"
        ),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "trial",
                "past_due",
                "canceled",
                "suspended",
                "expired",
                name="subscription_status_enum",
            ),
            nullable=False,
            comment="حالة الاشتراك",
        ),
        sa.Column(
            "billing_cycle",
            sa.Enum("monthly", "quarterly", "yearly", name="billing_cycle_enum"),
            nullable=False,
            comment="دورة الفوترة",
        ),
        sa.Column(
            "currency",
            sa.Enum("USD", "YER", name="currency_enum"),
            nullable=False,
            comment="العملة",
        ),
        sa.Column("start_date", sa.Date(), nullable=False, comment="تاريخ البدء"),
        sa.Column("end_date", sa.Date(), nullable=False, comment="تاريخ الانتهاء"),
        sa.Column(
            "trial_end_date",
            sa.Date(),
            nullable=True,
            comment="تاريخ انتهاء الفترة التجريبية",
        ),
        sa.Column(
            "canceled_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="تاريخ الإلغاء",
        ),
        sa.Column(
            "next_billing_date",
            sa.Date(),
            nullable=False,
            comment="تاريخ الفوترة التالي",
        ),
        sa.Column(
            "last_billing_date", sa.Date(), nullable=True, comment="تاريخ آخر فوترة"
        ),
        sa.Column(
            "payment_method",
            sa.Enum(
                "credit_card",
                "bank_transfer",
                "mobile_money",
                "cash",
                "tharwatt",
                name="payment_method_enum",
            ),
            nullable=True,
            comment="طريقة الدفع",
        ),
        sa.Column(
            "stripe_subscription_id",
            sa.String(length=255),
            nullable=True,
            comment="معرف الاشتراك في Stripe",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
            comment="بيانات إضافية",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="تاريخ الإنشاء",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="تاريخ آخر تحديث",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for subscriptions
    op.create_index(
        "idx_subscription_tenant_status", "subscriptions", ["tenant_id", "status"]
    )
    op.create_index(
        "idx_subscription_next_billing",
        "subscriptions",
        ["next_billing_date", "status"],
    )
    op.create_index(op.f("ix_subscriptions_plan_id"), "subscriptions", ["plan_id"])
    op.create_index(op.f("ix_subscriptions_status"), "subscriptions", ["status"])
    op.create_index(
        op.f("ix_subscriptions_stripe_subscription_id"),
        "subscriptions",
        ["stripe_subscription_id"],
    )
    op.create_index(op.f("ix_subscriptions_tenant_id"), "subscriptions", ["tenant_id"])

    # Create invoices table
    op.create_table(
        "invoices",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "invoice_number",
            sa.String(length=50),
            nullable=False,
            comment="رقم الفاتورة (SAH-2025-0001)",
        ),
        sa.Column(
            "tenant_id",
            sa.String(length=255),
            nullable=False,
            comment="المستأجر/العميل",
        ),
        sa.Column(
            "subscription_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="معرف الاشتراك",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "pending",
                "paid",
                "overdue",
                "canceled",
                "refunded",
                name="invoice_status_enum",
            ),
            nullable=False,
            comment="حالة الفاتورة",
        ),
        sa.Column(
            "currency",
            sa.Enum("USD", "YER", name="currency_enum"),
            nullable=False,
            comment="العملة",
        ),
        sa.Column("issue_date", sa.Date(), nullable=False, comment="تاريخ الإصدار"),
        sa.Column("due_date", sa.Date(), nullable=False, comment="تاريخ الاستحقاق"),
        sa.Column("paid_date", sa.Date(), nullable=True, comment="تاريخ الدفع"),
        sa.Column(
            "subtotal",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
            comment="المجموع الفرعي",
        ),
        sa.Column(
            "tax_rate",
            sa.Numeric(precision=5, scale=2),
            server_default="0",
            nullable=False,
            comment="معدل الضريبة",
        ),
        sa.Column(
            "tax_amount",
            sa.Numeric(precision=12, scale=2),
            server_default="0",
            nullable=False,
            comment="مبلغ الضريبة",
        ),
        sa.Column(
            "discount_amount",
            sa.Numeric(precision=12, scale=2),
            server_default="0",
            nullable=False,
            comment="مبلغ الخصم",
        ),
        sa.Column(
            "total",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
            comment="المجموع الكلي",
        ),
        sa.Column(
            "amount_paid",
            sa.Numeric(precision=12, scale=2),
            server_default="0",
            nullable=False,
            comment="المبلغ المدفوع",
        ),
        sa.Column(
            "amount_due",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
            comment="المبلغ المستحق",
        ),
        sa.Column(
            "line_items",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
            comment="بنود الفاتورة",
        ),
        sa.Column("notes", sa.Text(), nullable=True, comment="ملاحظات (EN)"),
        sa.Column("notes_ar", sa.Text(), nullable=True, comment="ملاحظات (AR)"),
        sa.Column(
            "stripe_invoice_id",
            sa.String(length=255),
            nullable=True,
            comment="معرف الفاتورة في Stripe",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
            comment="بيانات إضافية",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="تاريخ الإنشاء",
        ),
        sa.CheckConstraint("subtotal >= 0", name="check_subtotal_positive"),
        sa.CheckConstraint("total >= 0", name="check_total_positive"),
        sa.CheckConstraint("amount_paid >= 0", name="check_amount_paid_positive"),
        sa.CheckConstraint("amount_due >= 0", name="check_amount_due_positive"),
        sa.ForeignKeyConstraint(
            ["subscription_id"], ["subscriptions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number"),
    )

    # Create indexes for invoices
    op.create_index("idx_invoice_due_date_status", "invoices", ["due_date", "status"])
    op.create_index("idx_invoice_tenant_status", "invoices", ["tenant_id", "status"])
    op.create_index(op.f("ix_invoices_due_date"), "invoices", ["due_date"])
    op.create_index(op.f("ix_invoices_invoice_number"), "invoices", ["invoice_number"])
    op.create_index(op.f("ix_invoices_issue_date"), "invoices", ["issue_date"])
    op.create_index(op.f("ix_invoices_status"), "invoices", ["status"])
    op.create_index(
        op.f("ix_invoices_stripe_invoice_id"), "invoices", ["stripe_invoice_id"]
    )
    op.create_index(
        op.f("ix_invoices_subscription_id"), "invoices", ["subscription_id"]
    )
    op.create_index(op.f("ix_invoices_tenant_id"), "invoices", ["tenant_id"])

    # Create payments table
    op.create_table(
        "payments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "invoice_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="معرف الفاتورة",
        ),
        sa.Column(
            "tenant_id",
            sa.String(length=255),
            nullable=False,
            comment="المستأجر/العميل",
        ),
        sa.Column(
            "amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
            comment="المبلغ",
        ),
        sa.Column(
            "currency",
            sa.Enum("USD", "YER", name="currency_enum"),
            nullable=False,
            comment="العملة",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "processing",
                "succeeded",
                "failed",
                "refunded",
                name="payment_status_enum",
            ),
            nullable=False,
            comment="حالة الدفعة",
        ),
        sa.Column(
            "method",
            sa.Enum(
                "credit_card",
                "bank_transfer",
                "mobile_money",
                "cash",
                "tharwatt",
                name="payment_method_enum",
            ),
            nullable=False,
            comment="طريقة الدفع",
        ),
        sa.Column(
            "paid_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="تاريخ الدفع الفعلي",
        ),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="تاريخ المعالجة",
        ),
        sa.Column("failure_reason", sa.Text(), nullable=True, comment="سبب الفشل"),
        sa.Column(
            "stripe_payment_id",
            sa.String(length=255),
            nullable=True,
            comment="معرف الدفعة في Stripe",
        ),
        sa.Column(
            "tharwatt_transaction_id",
            sa.String(length=255),
            nullable=True,
            comment="معرف المعاملة في ثروات",
        ),
        sa.Column(
            "receipt_url", sa.String(length=500), nullable=True, comment="رابط الإيصال"
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
            comment="بيانات إضافية",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="تاريخ الإنشاء",
        ),
        sa.CheckConstraint("amount > 0", name="check_payment_amount_positive"),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for payments
    op.create_index("idx_payment_created", "payments", ["created_at"])
    op.create_index("idx_payment_tenant_status", "payments", ["tenant_id", "status"])
    op.create_index(op.f("ix_payments_invoice_id"), "payments", ["invoice_id"])
    op.create_index(op.f("ix_payments_status"), "payments", ["status"])
    op.create_index(
        op.f("ix_payments_stripe_payment_id"), "payments", ["stripe_payment_id"]
    )
    op.create_index(op.f("ix_payments_tenant_id"), "payments", ["tenant_id"])
    op.create_index(
        op.f("ix_payments_tharwatt_transaction_id"),
        "payments",
        ["tharwatt_transaction_id"],
    )

    # Create usage_records table
    op.create_table(
        "usage_records",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "subscription_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="معرف الاشتراك",
        ),
        sa.Column(
            "tenant_id",
            sa.String(length=255),
            nullable=False,
            comment="المستأجر/العميل",
        ),
        sa.Column(
            "metric_type",
            sa.String(length=100),
            nullable=False,
            comment="نوع المقياس (e.g., satellite_analyses, api_calls)",
        ),
        sa.Column("quantity", sa.Integer(), nullable=False, comment="الكمية"),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="تاريخ التسجيل",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
            comment="بيانات إضافية (e.g., resource_id, user_id)",
        ),
        sa.CheckConstraint("quantity > 0", name="check_quantity_positive"),
        sa.ForeignKeyConstraint(
            ["subscription_id"], ["subscriptions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for usage_records
    op.create_index("idx_usage_recorded_at", "usage_records", ["recorded_at"])
    op.create_index(
        "idx_usage_subscription_metric",
        "usage_records",
        ["subscription_id", "metric_type"],
    )
    op.create_index(
        "idx_usage_tenant_metric_date",
        "usage_records",
        ["tenant_id", "metric_type", "recorded_at"],
    )
    op.create_index(
        op.f("ix_usage_records_metric_type"), "usage_records", ["metric_type"]
    )
    op.create_index(
        op.f("ix_usage_records_recorded_at"), "usage_records", ["recorded_at"]
    )
    op.create_index(
        op.f("ix_usage_records_subscription_id"), "usage_records", ["subscription_id"]
    )
    op.create_index(op.f("ix_usage_records_tenant_id"), "usage_records", ["tenant_id"])


def downgrade() -> None:
    """
    Drop all billing tables and enums
    حذف جميع الجداول والأنواع
    """
    # Drop tables (in reverse order due to foreign keys)
    op.drop_table("usage_records")
    op.drop_table("payments")
    op.drop_table("invoices")
    op.drop_table("subscriptions")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS payment_status_enum")
    op.execute("DROP TYPE IF EXISTS payment_method_enum")
    op.execute("DROP TYPE IF EXISTS invoice_status_enum")
    op.execute("DROP TYPE IF EXISTS currency_enum")
    op.execute("DROP TYPE IF EXISTS billing_cycle_enum")
    op.execute("DROP TYPE IF EXISTS subscription_status_enum")
