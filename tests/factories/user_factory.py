"""
SAHOOL User Test Factory
Generates consistent test user data
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4


@dataclass
class TestUser:
    """Test user data model"""

    id: str
    email: str
    tenant_id: str
    name: str
    name_ar: str | None
    phone: str | None
    roles: list[str]
    is_active: bool
    created_at: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "phone": self.phone,
            "roles": self.roles,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


def make_user(**overrides) -> TestUser:
    """
    Create a test user with default values.
    Override any field by passing keyword arguments.

    Example:
        user = make_user(email="custom@test.com", roles=["admin"])
    """
    defaults = {
        "id": str(uuid4()),
        "email": "test@example.com",
        "tenant_id": "test-tenant-001",
        "name": "Test User",
        "name_ar": "مستخدم اختبار",
        "phone": "+967771234567",
        "roles": ["worker"],
        "is_active": True,
        "created_at": datetime.now(UTC),
    }

    defaults.update(overrides)
    return TestUser(**defaults)


def make_admin_user(**overrides) -> TestUser:
    """Create an admin test user"""
    defaults = {
        "email": "admin@example.com",
        "name": "Admin User",
        "roles": ["admin"],
    }
    defaults.update(overrides)
    return make_user(**defaults)


def make_super_admin_user(**overrides) -> TestUser:
    """Create a super admin test user"""
    defaults = {
        "email": "superadmin@example.com",
        "name": "Super Admin",
        "roles": ["super_admin"],
    }
    defaults.update(overrides)
    return make_user(**defaults)


def make_worker_user(**overrides) -> TestUser:
    """Create a field worker test user"""
    defaults = {
        "email": "worker@example.com",
        "name": "Field Worker",
        "name_ar": "عامل الحقل",
        "roles": ["worker"],
    }
    defaults.update(overrides)
    return make_user(**defaults)


def make_manager_user(**overrides) -> TestUser:
    """Create a manager test user"""
    defaults = {
        "email": "manager@example.com",
        "name": "Farm Manager",
        "name_ar": "مدير المزرعة",
        "roles": ["manager"],
    }
    defaults.update(overrides)
    return make_user(**defaults)
