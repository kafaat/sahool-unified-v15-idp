"""
Sprint 4: Create outbox_events table

Revision ID: s4_0001
Create Date: 2025-12-17
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = "s4_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create outbox_events table for transactional outbox pattern"""
    op.create_table(
        "outbox_events",
        # Primary key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            comment="Unique event identifier",
        ),
        # Event metadata
        sa.Column(
            "event_type",
            sa.String(length=200),
            nullable=False,
            comment="Event type (e.g., 'field.created')",
        ),
        sa.Column(
            "event_version",
            sa.Integer(),
            nullable=False,
            server_default="1",
            comment="Event schema version",
        ),
        sa.Column(
            "schema_ref",
            sa.String(length=240),
            nullable=False,
            comment="Schema reference (e.g., 'events.field.created:v1')",
        ),
        # Multi-tenancy and tracing
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="Tenant that owns this event",
        ),
        sa.Column(
            "correlation_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="Correlation ID for request tracing",
        ),
        # Payload
        sa.Column(
            "payload_json",
            sa.Text(),
            nullable=False,
            comment="Full event envelope as JSON",
        ),
        # Publishing status
        sa.Column(
            "published",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Whether the event has been published",
        ),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When the event was published",
        ),
        # Retry tracking
        sa.Column(
            "retry_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Number of publish attempts",
        ),
        sa.Column(
            "last_error",
            sa.Text(),
            nullable=True,
            comment="Last error message if publish failed",
        ),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="When the event was created",
        ),
    )

    # Create indexes for efficient querying
    op.create_index(
        "ix_outbox_published_created",
        "outbox_events",
        ["published", "created_at"],
        comment="Index for polling unpublished events",
    )
    op.create_index(
        "ix_outbox_tenant_created",
        "outbox_events",
        ["tenant_id", "created_at"],
        comment="Index for tenant-specific queries",
    )


def downgrade() -> None:
    """Drop outbox_events table"""
    op.drop_index("ix_outbox_tenant_created", table_name="outbox_events")
    op.drop_index("ix_outbox_published_created", table_name="outbox_events")
    op.drop_table("outbox_events")
