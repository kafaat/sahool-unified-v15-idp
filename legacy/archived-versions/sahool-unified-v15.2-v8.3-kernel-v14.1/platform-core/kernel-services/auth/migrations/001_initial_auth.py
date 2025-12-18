"""
Auth Service Database Migrations
================================
Initial migration for authentication tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = "001_initial_auth"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create auth tables"""

    # Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        # Authentication
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("phone", sa.String(20), unique=True, nullable=True, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        # Profile
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("full_name_ar", sa.String(255), nullable=True),
        sa.Column("preferred_language", sa.String(10), default="ar"),
        sa.Column("timezone", sa.String(50), default="Asia/Aden"),
        # Status
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_verified", sa.Boolean, default=False),
        sa.Column("is_locked", sa.Boolean, default=False),
        sa.Column("locked_until", sa.DateTime, nullable=True),
        sa.Column("failed_login_attempts", sa.Integer, default=0),
        # MFA
        sa.Column("mfa_enabled", sa.Boolean, default=False),
        sa.Column("mfa_secret", sa.String(255), nullable=True),
        sa.Column("mfa_backup_codes", postgresql.JSON, nullable=True),
        # Metadata
        sa.Column("last_login", sa.DateTime, nullable=True),
        sa.Column("last_password_change", sa.DateTime, nullable=True),
        sa.Column("password_reset_token", sa.String(255), nullable=True),
        sa.Column("password_reset_expires", sa.DateTime, nullable=True),
        sa.Column("verification_token", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Roles table
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("name_ar", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("description_ar", sa.Text, nullable=True),
        sa.Column("is_system", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Permissions table
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("resource", sa.String(100), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("resource", "action", name="uq_permission_resource_action"),
    )

    # User-Role association table
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # Role-Permission association table
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "permission_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # User Sessions table
    op.create_table(
        "user_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("refresh_token_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("device_info", postgresql.JSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("last_used", sa.DateTime, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])
    op.create_index("ix_user_sessions_is_active", "user_sessions", ["is_active"])

    # API Keys table
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("key_prefix", sa.String(10), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False),
        sa.Column("scopes", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("rate_limit", sa.Integer, default=1000),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("last_used", sa.DateTime, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Auth Audit Log table
    op.create_table(
        "auth_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_status", sa.String(20), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("details", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_auth_audit_logs_user_id", "auth_audit_logs", ["user_id"])
    op.create_index("ix_auth_audit_logs_tenant_id", "auth_audit_logs", ["tenant_id"])
    op.create_index("ix_auth_audit_logs_event_type", "auth_audit_logs", ["event_type"])
    op.create_index("ix_auth_audit_logs_created_at", "auth_audit_logs", ["created_at"])


def downgrade():
    """Drop auth tables"""
    op.drop_table("auth_audit_logs")
    op.drop_table("api_keys")
    op.drop_table("user_sessions")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
