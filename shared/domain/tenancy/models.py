"""
SAHOOL Tenant Models
Data models for multi-tenancy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


class TenantStatus(str, Enum):
    """Tenant status"""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"


class TenantPlan(str, Enum):
    """Tenant subscription plan"""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TenantSettings:
    """Tenant-specific settings"""

    max_users: int = 10
    max_fields: int = 50
    max_storage_gb: int = 5
    features: dict = field(default_factory=dict)
    locale: str = "ar"
    timezone: str = "Asia/Aden"

    def to_dict(self) -> dict:
        return {
            "max_users": self.max_users,
            "max_fields": self.max_fields,
            "max_storage_gb": self.max_storage_gb,
            "features": self.features,
            "locale": self.locale,
            "timezone": self.timezone,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TenantSettings:
        return cls(**data)


@dataclass
class Tenant:
    """Tenant entity"""

    id: str
    name: str
    name_ar: Optional[str]
    status: TenantStatus
    plan: TenantPlan
    settings: TenantSettings
    owner_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        name: str,
        name_ar: Optional[str] = None,
        plan: TenantPlan = TenantPlan.FREE,
        owner_id: Optional[str] = None,
    ) -> Tenant:
        """Factory method to create a new tenant"""
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid4()),
            name=name,
            name_ar=name_ar,
            status=TenantStatus.TRIAL if plan == TenantPlan.FREE else TenantStatus.ACTIVE,
            plan=plan,
            settings=TenantSettings(),
            owner_id=owner_id,
            created_at=now,
            updated_at=now,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "status": self.status.value,
            "plan": self.plan.value,
            "settings": self.settings.to_dict(),
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
