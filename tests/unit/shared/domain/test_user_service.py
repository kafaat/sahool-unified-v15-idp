"""
Tests for shared/domain/users/service.py
اختبارات خدمة المستخدمين

Tests cover:
- User creation and duplicate email handling
- User retrieval by ID and email
- Password verification
- Last login updates
- Role management
- User deactivation
- Tenant user listing
- Two-factor authentication methods
"""

import pytest
from datetime import UTC, datetime
from unittest.mock import patch, MagicMock

from shared.domain.users.service import UserService
from shared.domain.users.models import User


class TestUserServiceCreation:
    """Tests for user creation.
    اختبارات إنشاء المستخدمين"""

    def test_create_user_basic(self):
        """Test creating a user with minimal arguments."""
        svc = UserService()
        user = svc.create_user(
            tenant_id="t1",
            email="ahmed@example.com",
            name="Ahmed",
        )
        assert user.tenant_id == "t1"
        assert user.email == "ahmed@example.com"
        assert user.profile.name == "Ahmed"
        assert user.is_active is True
        assert user.roles == ["viewer"]
        assert user.password_hash is None

    def test_create_user_with_all_fields(self):
        """Test creating a user with all optional fields."""
        svc = UserService()
        user = svc.create_user(
            tenant_id="t2",
            email="sara@example.com",
            name="Sara",
            name_ar="سارة",
            password="secure123",
            roles=["admin", "editor"],
        )
        assert user.profile.name_ar == "سارة"
        assert user.roles == ["admin", "editor"]
        assert user.password_hash is not None
        assert "$" in user.password_hash  # PBKDF2 format: salt$hash

    def test_create_user_stored_in_memory(self):
        """Test that created user is stored internally."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        assert svc.get_user(user.id) is user

    def test_create_user_duplicate_email_raises(self):
        """Test that duplicate email raises ValueError."""
        svc = UserService()
        svc.create_user(tenant_id="t1", email="dup@example.com", name="First")
        with pytest.raises(ValueError, match="already exists"):
            svc.create_user(tenant_id="t1", email="dup@example.com", name="Second")

    def test_create_user_without_password(self):
        """Test creating a user without a password."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="nopass@b.com", name="NP")
        assert user.password_hash is None


class TestUserServiceRetrieval:
    """Tests for user retrieval.
    اختبارات استرجاع المستخدمين"""

    def test_get_user_found(self):
        """Test retrieving an existing user by ID."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        result = svc.get_user(user.id)
        assert result is user

    def test_get_user_not_found(self):
        """Test retrieving a non-existent user returns None."""
        svc = UserService()
        assert svc.get_user("nonexistent-id") is None

    def test_get_user_by_email_found(self):
        """Test retrieving user by email."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="find@me.com", name="Find")
        result = svc.get_user_by_email("find@me.com")
        assert result is user

    def test_get_user_by_email_not_found(self):
        """Test retrieving non-existent email returns None."""
        svc = UserService()
        assert svc.get_user_by_email("nobody@nowhere.com") is None


class TestUserServicePassword:
    """Tests for password verification.
    اختبارات التحقق من كلمة المرور"""

    def test_verify_password_correct(self):
        """Test verifying correct password returns user."""
        svc = UserService()
        svc.create_user(
            tenant_id="t1",
            email="pw@test.com",
            name="PW",
            password="mypassword",
        )
        result = svc.verify_user_password("pw@test.com", "mypassword")
        assert result is not None
        assert result.email == "pw@test.com"

    def test_verify_password_wrong(self):
        """Test verifying wrong password returns None."""
        svc = UserService()
        svc.create_user(
            tenant_id="t1",
            email="pw@test.com",
            name="PW",
            password="mypassword",
        )
        result = svc.verify_user_password("pw@test.com", "wrongpassword")
        assert result is None

    def test_verify_password_no_user(self):
        """Test verifying password for non-existent user returns None."""
        svc = UserService()
        result = svc.verify_user_password("ghost@test.com", "anypass")
        assert result is None

    def test_verify_password_no_password_set(self):
        """Test verifying password when user has no password returns None."""
        svc = UserService()
        svc.create_user(tenant_id="t1", email="nopw@test.com", name="NP")
        result = svc.verify_user_password("nopw@test.com", "anypass")
        assert result is None


class TestUserServiceUpdates:
    """Tests for user updates.
    اختبارات تحديث المستخدمين"""

    def test_update_last_login(self):
        """Test updating last login timestamp."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        assert user.last_login is None

        before = datetime.now(UTC)
        result = svc.update_last_login(user.id)
        assert result is not None
        assert result.last_login is not None
        assert result.last_login >= before
        assert result.updated_at >= before

    def test_update_last_login_nonexistent(self):
        """Test updating last login for non-existent user returns None."""
        svc = UserService()
        assert svc.update_last_login("fake-id") is None

    def test_update_user_roles(self):
        """Test updating user roles."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        assert user.roles == ["viewer"]

        result = svc.update_user_roles(user.id, ["admin", "editor"])
        assert result is not None
        assert result.roles == ["admin", "editor"]

    def test_update_user_roles_nonexistent(self):
        """Test updating roles for non-existent user returns None."""
        svc = UserService()
        assert svc.update_user_roles("fake-id", ["admin"]) is None

    def test_deactivate_user(self):
        """Test deactivating a user."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        assert user.is_active is True

        result = svc.deactivate_user(user.id)
        assert result is not None
        assert result.is_active is False

    def test_deactivate_nonexistent(self):
        """Test deactivating non-existent user returns None."""
        svc = UserService()
        assert svc.deactivate_user("fake-id") is None


class TestUserServiceTenantListing:
    """Tests for tenant user listing.
    اختبارات سرد مستخدمي المستأجر"""

    def test_list_tenant_users(self):
        """Test listing users for a specific tenant."""
        svc = UserService()
        svc.create_user(tenant_id="t1", email="a@t1.com", name="A")
        svc.create_user(tenant_id="t1", email="b@t1.com", name="B")
        svc.create_user(tenant_id="t2", email="c@t2.com", name="C")

        users = svc.list_tenant_users("t1")
        assert len(users) == 2
        assert all(u.tenant_id == "t1" for u in users)

    def test_list_tenant_users_active_only(self):
        """Test listing only active users."""
        svc = UserService()
        u1 = svc.create_user(tenant_id="t1", email="active@t1.com", name="Active")
        u2 = svc.create_user(tenant_id="t1", email="inactive@t1.com", name="Inactive")
        svc.deactivate_user(u2.id)

        active_users = svc.list_tenant_users("t1", active_only=True)
        assert len(active_users) == 1
        assert active_users[0].id == u1.id

    def test_list_tenant_users_all(self):
        """Test listing all users including inactive."""
        svc = UserService()
        svc.create_user(tenant_id="t1", email="active@t1.com", name="Active")
        u2 = svc.create_user(tenant_id="t1", email="inactive@t1.com", name="Inactive")
        svc.deactivate_user(u2.id)

        all_users = svc.list_tenant_users("t1", active_only=False)
        assert len(all_users) == 2

    def test_list_empty_tenant(self):
        """Test listing users for a tenant with no users."""
        svc = UserService()
        assert svc.list_tenant_users("empty-tenant") == []


class TestUserServiceTwoFA:
    """Tests for two-factor authentication methods.
    اختبارات المصادقة الثنائية"""

    def test_update_twofa_secret(self):
        """Test updating 2FA secret."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        result = svc.update_twofa_secret(user.id, "TOTP_SECRET_123")
        assert result is not None
        assert result.twofa_secret == "TOTP_SECRET_123"

    def test_update_twofa_secret_nonexistent(self):
        """Test updating 2FA secret for non-existent user."""
        svc = UserService()
        assert svc.update_twofa_secret("fake-id", "secret") is None

    def test_enable_twofa(self):
        """Test enabling 2FA with backup codes."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        codes = ["code1", "code2", "code3"]
        result = svc.enable_twofa(user.id, codes)
        assert result is not None
        assert result.twofa_enabled is True
        assert result.twofa_backup_codes == codes

    def test_enable_twofa_nonexistent(self):
        """Test enabling 2FA for non-existent user."""
        svc = UserService()
        assert svc.enable_twofa("fake-id", ["code"]) is None

    def test_disable_twofa(self):
        """Test disabling 2FA clears all 2FA data."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        svc.update_twofa_secret(user.id, "secret")
        svc.enable_twofa(user.id, ["code1"])

        result = svc.disable_twofa(user.id)
        assert result is not None
        assert result.twofa_enabled is False
        assert result.twofa_secret is None
        assert result.twofa_backup_codes is None

    def test_disable_twofa_nonexistent(self):
        """Test disabling 2FA for non-existent user."""
        svc = UserService()
        assert svc.disable_twofa("fake-id") is None

    def test_update_backup_codes(self):
        """Test updating backup codes."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        new_codes = ["new1", "new2"]
        result = svc.update_backup_codes(user.id, new_codes)
        assert result is not None
        assert result.twofa_backup_codes == new_codes

    def test_update_backup_codes_nonexistent(self):
        """Test updating backup codes for non-existent user."""
        svc = UserService()
        assert svc.update_backup_codes("fake-id", ["code"]) is None

    def test_remove_backup_code(self):
        """Test removing a single backup code."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        svc.update_backup_codes(user.id, ["code1", "code2", "code3"])

        result = svc.remove_backup_code(user.id, "code2")
        assert result is not None
        assert "code2" not in result.twofa_backup_codes
        assert len(result.twofa_backup_codes) == 2

    def test_remove_backup_code_nonexistent_user(self):
        """Test removing backup code for non-existent user."""
        svc = UserService()
        assert svc.remove_backup_code("fake-id", "code") is None

    def test_remove_backup_code_no_codes(self):
        """Test removing backup code when no codes exist."""
        svc = UserService()
        user = svc.create_user(tenant_id="t1", email="a@b.com", name="A")
        # No backup codes set, should not error
        result = svc.remove_backup_code(user.id, "code")
        assert result is not None
