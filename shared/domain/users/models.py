"""
SAHOOL User Models
Data models for user management
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4


@dataclass
class UserProfile:
    """User profile information"""

    name: str
    name_ar: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    language: str = "ar"
    notifications_enabled: bool = True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "name_ar": self.name_ar,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "language": self.language,
            "notifications_enabled": self.notifications_enabled,
        }


@dataclass
class User:
    """User entity"""

    id: str
    tenant_id: str
    email: str
    profile: UserProfile
    roles: list[str]
    is_active: bool
    is_verified: bool
    password_hash: str | None
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime
    # Two-Factor Authentication fields
    twofa_secret: str | None = None
    twofa_enabled: bool = False
    twofa_backup_codes: list[str] | None = None

    @classmethod
    def create(
        cls,
        tenant_id: str,
        email: str,
        name: str,
        name_ar: str | None = None,
        roles: list[str] | None = None,
        password_hash: str | None = None,
    ) -> User:
        """Factory method to create a new user"""
        now = datetime.now(UTC)
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            email=email,
            profile=UserProfile(name=name, name_ar=name_ar),
            roles=roles or ["viewer"],
            is_active=True,
            is_verified=False,
            password_hash=password_hash,
            last_login=None,
            created_at=now,
            updated_at=now,
        )

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        return role in self.roles

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert to dictionary"""
        data = {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "email": self.email,
            "profile": self.profile.to_dict(),
            "roles": self.roles,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "twofa_enabled": self.twofa_enabled,
        }
        if include_sensitive:
            data["password_hash"] = self.password_hash
            data["twofa_secret"] = self.twofa_secret
            data["twofa_backup_codes"] = self.twofa_backup_codes
        return data
