"""
Tests for shared/domain/users/models.py
اختبارات نماذج المستخدمين

Tests cover:
- UserProfile dataclass creation and serialization
- User entity creation via factory method
- Role checking
- Serialization with/without sensitive data
"""

import pytest
from datetime import UTC, datetime

from shared.domain.users.models import User, UserProfile


class TestUserProfile:
    """Tests for UserProfile dataclass.
    اختبارات بيانات الملف الشخصي للمستخدم"""

    def test_create_profile_defaults(self):
        """Test creating a profile with default values."""
        profile = UserProfile(name="Ahmed")
        assert profile.name == "Ahmed"
        assert profile.name_ar is None
        assert profile.phone is None
        assert profile.avatar_url is None
        assert profile.language == "ar"
        assert profile.notifications_enabled is True

    def test_create_profile_full(self):
        """Test creating a profile with all fields."""
        profile = UserProfile(
            name="Ahmed",
            name_ar="أحمد",
            phone="+966500000000",
            avatar_url="https://example.com/avatar.png",
            language="en",
            notifications_enabled=False,
        )
        assert profile.name == "Ahmed"
        assert profile.name_ar == "أحمد"
        assert profile.phone == "+966500000000"
        assert profile.language == "en"
        assert profile.notifications_enabled is False

    def test_profile_to_dict(self):
        """Test profile serialization to dictionary."""
        profile = UserProfile(name="Ahmed", name_ar="أحمد")
        data = profile.to_dict()
        assert data["name"] == "Ahmed"
        assert data["name_ar"] == "أحمد"
        assert data["phone"] is None
        assert data["language"] == "ar"
        assert data["notifications_enabled"] is True
        assert len(data) == 6


class TestUser:
    """Tests for User entity.
    اختبارات كيان المستخدم"""

    def test_create_user_factory_defaults(self):
        """Test User.create factory with minimal arguments."""
        user = User.create(
            tenant_id="tenant-1",
            email="ahmed@example.com",
            name="Ahmed",
        )
        assert user.tenant_id == "tenant-1"
        assert user.email == "ahmed@example.com"
        assert user.profile.name == "Ahmed"
        assert user.profile.name_ar is None
        assert user.roles == ["viewer"]
        assert user.is_active is True
        assert user.is_verified is False
        assert user.password_hash is None
        assert user.last_login is None
        assert user.twofa_enabled is False
        assert user.twofa_secret is None
        assert user.twofa_backup_codes is None
        assert user.id  # UUID generated
        assert user.created_at <= datetime.now(UTC)
        assert user.updated_at <= datetime.now(UTC)

    def test_create_user_factory_full(self):
        """Test User.create factory with all arguments."""
        user = User.create(
            tenant_id="tenant-2",
            email="sara@example.com",
            name="Sara",
            name_ar="سارة",
            roles=["admin", "editor"],
            password_hash="hashed_pw",
        )
        assert user.profile.name_ar == "سارة"
        assert user.roles == ["admin", "editor"]
        assert user.password_hash == "hashed_pw"

    def test_has_role_true(self):
        """Test has_role returns True when user has the role."""
        user = User.create(
            tenant_id="t1", email="a@b.com", name="A", roles=["admin", "viewer"]
        )
        assert user.has_role("admin") is True
        assert user.has_role("viewer") is True

    def test_has_role_false(self):
        """Test has_role returns False when user lacks the role."""
        user = User.create(tenant_id="t1", email="a@b.com", name="A")
        assert user.has_role("admin") is False

    def test_to_dict_without_sensitive(self):
        """Test to_dict excludes sensitive data by default."""
        user = User.create(
            tenant_id="t1",
            email="a@b.com",
            name="A",
            password_hash="secret",
        )
        user.twofa_secret = "totp-secret"
        data = user.to_dict()
        assert "password_hash" not in data
        assert "twofa_secret" not in data
        assert "twofa_backup_codes" not in data
        assert data["email"] == "a@b.com"
        assert data["twofa_enabled"] is False

    def test_to_dict_with_sensitive(self):
        """Test to_dict includes sensitive data when requested."""
        user = User.create(
            tenant_id="t1",
            email="a@b.com",
            name="A",
            password_hash="secret",
        )
        user.twofa_secret = "totp-secret"
        user.twofa_backup_codes = ["code1", "code2"]
        data = user.to_dict(include_sensitive=True)
        assert data["password_hash"] == "secret"
        assert data["twofa_secret"] == "totp-secret"
        assert data["twofa_backup_codes"] == ["code1", "code2"]

    def test_to_dict_with_last_login(self):
        """Test to_dict serializes last_login when set."""
        user = User.create(tenant_id="t1", email="a@b.com", name="A")
        user.last_login = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)
        data = user.to_dict()
        assert data["last_login"] is not None
        assert "2026-01-15" in data["last_login"]

    def test_to_dict_without_last_login(self):
        """Test to_dict returns None for last_login when not set."""
        user = User.create(tenant_id="t1", email="a@b.com", name="A")
        data = user.to_dict()
        assert data["last_login"] is None

    def test_user_ids_are_unique(self):
        """Test that factory creates unique IDs."""
        u1 = User.create(tenant_id="t1", email="a@b.com", name="A")
        u2 = User.create(tenant_id="t1", email="b@b.com", name="B")
        assert u1.id != u2.id
