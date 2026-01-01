"""
SAHOOL User Service
Business logic for user management
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from kernel_domain.auth.passwords import hash_password, verify_password

from .models import User


class UserService:
    """Service for user operations"""

    def __init__(self):
        # In-memory store (replace with repository)
        self._users: dict[str, User] = {}
        self._email_index: dict[str, str] = {}  # email -> user_id

    def create_user(
        self,
        tenant_id: str,
        email: str,
        name: str,
        name_ar: Optional[str] = None,
        password: Optional[str] = None,
        roles: Optional[list[str]] = None,
    ) -> User:
        """Create a new user"""
        # Check email uniqueness
        if email in self._email_index:
            raise ValueError(f"Email {email} already exists")

        password_hash = None
        if password:
            password_hash = hash_password(password)

        user = User.create(
            tenant_id=tenant_id,
            email=email,
            name=name,
            name_ar=name_ar,
            roles=roles,
            password_hash=password_hash,
        )

        self._users[user.id] = user
        self._email_index[email] = user.id

        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_id = self._email_index.get(email)
        if user_id:
            return self._users.get(user_id)
        return None

    def verify_user_password(self, email: str, password: str) -> Optional[User]:
        """Verify user credentials and return user if valid"""
        user = self.get_user_by_email(email)
        if user and user.password_hash:
            if verify_password(password, user.password_hash):
                return user
        return None

    def update_last_login(self, user_id: str) -> Optional[User]:
        """Update user's last login timestamp"""
        user = self._users.get(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)
        return user

    def update_user_roles(
        self,
        user_id: str,
        roles: list[str],
    ) -> Optional[User]:
        """Update user roles"""
        user = self._users.get(user_id)
        if user:
            user.roles = roles
            user.updated_at = datetime.now(timezone.utc)
        return user

    def deactivate_user(self, user_id: str) -> Optional[User]:
        """Deactivate a user"""
        user = self._users.get(user_id)
        if user:
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
        return user

    def list_tenant_users(
        self,
        tenant_id: str,
        active_only: bool = True,
    ) -> list[User]:
        """List all users for a tenant"""
        users = [u for u in self._users.values() if u.tenant_id == tenant_id]
        if active_only:
            users = [u for u in users if u.is_active]
        return users

    # ═══════════════════════════════════════════════════════════════════════════
    # Two-Factor Authentication Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def update_twofa_secret(self, user_id: str, secret: str) -> Optional[User]:
        """Update user's 2FA secret (during setup)"""
        user = self._users.get(user_id)
        if user:
            user.twofa_secret = secret
            user.updated_at = datetime.now(timezone.utc)
        return user

    def enable_twofa(self, user_id: str, backup_codes: list[str]) -> Optional[User]:
        """Enable 2FA for user and store backup codes"""
        user = self._users.get(user_id)
        if user:
            user.twofa_enabled = True
            user.twofa_backup_codes = backup_codes
            user.updated_at = datetime.now(timezone.utc)
        return user

    def disable_twofa(self, user_id: str) -> Optional[User]:
        """Disable 2FA for user"""
        user = self._users.get(user_id)
        if user:
            user.twofa_enabled = False
            user.twofa_secret = None
            user.twofa_backup_codes = None
            user.updated_at = datetime.now(timezone.utc)
        return user

    def update_backup_codes(
        self, user_id: str, backup_codes: list[str]
    ) -> Optional[User]:
        """Update user's backup codes"""
        user = self._users.get(user_id)
        if user:
            user.twofa_backup_codes = backup_codes
            user.updated_at = datetime.now(timezone.utc)
        return user

    def remove_backup_code(self, user_id: str, code_hash: str) -> Optional[User]:
        """Remove a used backup code"""
        user = self._users.get(user_id)
        if user and user.twofa_backup_codes:
            user.twofa_backup_codes = [
                c for c in user.twofa_backup_codes if c != code_hash
            ]
            user.updated_at = datetime.now(timezone.utc)
        return user
