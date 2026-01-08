"""
═══════════════════════════════════════════════════════════════════════════════
SAHOOL - Provider Configuration Database Models
نماذج قاعدة بيانات تكوين المزودين
═══════════════════════════════════════════════════════════════════════════════
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


# ═══════════════════════════════════════════════════════════════════════════════
# PROVIDER CONFIGURATION MODEL
# ═══════════════════════════════════════════════════════════════════════════════


class ProviderConfig(Base):
    """
    Provider Configuration Model
    Stores tenant-specific provider configurations with API keys and settings

    يخزن تكوينات المزود الخاصة بكل مستأجر مع مفاتيح API والإعدادات
    """

    __tablename__ = "provider_configs"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant Information
    tenant_id = Column(String(255), nullable=False, index=True)

    # Provider Information
    provider_type = Column(
        String(50), nullable=False, index=True
    )  # map, weather, satellite, payment, sms, notification
    provider_name = Column(
        String(100), nullable=False, index=True
    )  # openstreetmap, google_maps, etc.

    # Configuration
    api_key = Column(Text, nullable=True)  # Encrypted in production
    api_secret = Column(Text, nullable=True)  # Encrypted in production
    priority = Column(String(20), nullable=False, default="primary")  # primary, secondary, tertiary
    enabled = Column(Boolean, nullable=False, default=True)

    # Additional Settings (JSON)
    config_data = Column(JSON, nullable=True)  # Additional provider-specific settings

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    # Versioning
    version = Column(Integer, nullable=False, default=1)

    # Indexes for performance
    __table_args__ = (
        Index("idx_tenant_provider_type", "tenant_id", "provider_type"),
        Index("idx_tenant_provider_name", "tenant_id", "provider_name"),
        Index(
            "idx_tenant_type_enabled", "tenant_id", "provider_type", "enabled"
        ),  # For active providers query
        Index(
            "idx_tenant_type_priority",
            "tenant_id",
            "provider_type",
            "priority",
        ),  # For failover chain
    )

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "tenant_id": self.tenant_id,
            "provider_type": self.provider_type,
            "provider_name": self.provider_name,
            "priority": self.priority,
            "enabled": self.enabled,
            "config_data": self.config_data or {},
            "has_api_key": bool(self.api_key),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION VERSION HISTORY MODEL
# ═══════════════════════════════════════════════════════════════════════════════


class ConfigVersion(Base):
    """
    Configuration Version History
    Tracks all changes to provider configurations for audit and rollback

    يتتبع جميع التغييرات في تكوينات المزود للمراجعة والاستعادة
    """

    __tablename__ = "config_versions"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Reference to ProviderConfig
    config_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Tenant Information (denormalized for faster queries)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Snapshot of configuration at this version
    provider_type = Column(String(50), nullable=False)
    provider_name = Column(String(100), nullable=False)
    api_key = Column(Text, nullable=True)  # Encrypted in production
    api_secret = Column(Text, nullable=True)  # Encrypted in production
    priority = Column(String(20), nullable=False)
    enabled = Column(Boolean, nullable=False)
    config_data = Column(JSON, nullable=True)

    # Version Information
    version = Column(Integer, nullable=False)
    change_type = Column(String(20), nullable=False)  # created, updated, deleted, enabled, disabled

    # Change Metadata
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    changed_by = Column(String(255), nullable=True)
    change_reason = Column(Text, nullable=True)  # Optional reason for change

    # Indexes for performance
    __table_args__ = (
        Index("idx_config_version", "config_id", "version"),
        Index("idx_tenant_changed_at", "tenant_id", "changed_at"),
        Index("idx_tenant_provider_changed", "tenant_id", "provider_type", "changed_at"),
    )

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "config_id": str(self.config_id),
            "tenant_id": self.tenant_id,
            "provider_type": self.provider_type,
            "provider_name": self.provider_name,
            "priority": self.priority,
            "enabled": self.enabled,
            "config_data": self.config_data or {},
            "version": self.version,
            "change_type": self.change_type,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
            "changed_by": self.changed_by,
            "change_reason": self.change_reason,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════


class Database:
    """Database connection manager"""

    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """Get database session"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
