"""${message}
${message_ar if message_ar else ''}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

Author: SAHOOL Migration System
نظام هجرة SAHOOL
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
${imports if imports else ""}

# معرفات المراجعة، تستخدم بواسطة Alembic
# Revision identifiers, used by Alembic
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """
    ترقية قاعدة البيانات
    Upgrade database schema
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    التراجع عن الترقية
    Downgrade database schema
    """
    ${downgrades if downgrades else "pass"}
