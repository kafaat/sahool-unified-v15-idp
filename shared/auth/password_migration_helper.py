"""
Password Migration Helper
مساعد ترحيل كلمات المرور

Helper functions to integrate password migration into authentication flows.
دوال مساعدة لدمج ترحيل كلمات المرور في تدفقات المصادقة.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from .password_hasher import get_password_hasher

logger = logging.getLogger(__name__)


@dataclass
class AuthenticationResult:
    """Result of authentication attempt"""

    success: bool
    user_id: str | None = None
    needs_password_update: bool = False
    new_password_hash: str | None = None
    error_message: str | None = None


class UserRepository(Protocol):
    """Protocol for user repository operations"""

    def get_user_by_email(self, email: str) -> dict | None:
        """Get user by email"""
        ...

    def update_password_hash(self, user_id: str, password_hash: str) -> bool:
        """Update user's password hash"""
        ...

    def mark_password_migrated(self, user_id: str) -> bool:
        """Mark user's password as migrated (clear migration flag)"""
        ...


class PasswordMigrationHelper:
    """
    Helper class to handle password verification with automatic migration

    Usage in login endpoint:
        helper = PasswordMigrationHelper(user_repository)
        result = await helper.authenticate_and_migrate(email, password)

        if result.success:
            if result.needs_password_update:
                # Password was migrated, update in database
                user_repository.update_password_hash(
                    result.user_id,
                    result.new_password_hash
                )
            # Proceed with login...
        else:
            # Invalid credentials
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize helper

        Args:
            user_repository: Repository for user operations
        """
        self.user_repo = user_repository
        self.hasher = get_password_hasher()

    async def authenticate_and_migrate(self, email: str, password: str) -> AuthenticationResult:
        """
        Authenticate user and migrate password if needed

        This is the main method to use in your login endpoints.
        It handles:
        1. Finding the user
        2. Verifying the password
        3. Detecting if migration is needed
        4. Generating new hash if migration is needed

        Args:
            email: User's email
            password: Plain text password

        Returns:
            AuthenticationResult with migration info
        """
        try:
            # Get user from database
            user = self.user_repo.get_user_by_email(email)
            if not user:
                logger.warning(f"Authentication failed: User not found for email {email}")
                return AuthenticationResult(success=False, error_message="Invalid credentials")

            user_id = user.get("id")
            stored_hash = user.get("password_hash")

            if not stored_hash:
                logger.error(f"User {user_id} has no password hash")
                return AuthenticationResult(success=False, error_message="Invalid credentials")

            # Verify password and check if rehash is needed
            is_valid, needs_rehash = self.hasher.verify_password(password, stored_hash)

            if not is_valid:
                logger.warning(f"Authentication failed: Invalid password for user {user_id}")
                return AuthenticationResult(success=False, error_message="Invalid credentials")

            # Password is valid
            logger.info(f"Authentication successful for user {user_id}")

            # Check if we need to migrate the password
            if needs_rehash:
                logger.info(f"Password migration needed for user {user_id}")
                try:
                    # Generate new Argon2id hash
                    new_hash = self.hasher.hash_password(password)

                    return AuthenticationResult(
                        success=True,
                        user_id=user_id,
                        needs_password_update=True,
                        new_password_hash=new_hash,
                    )
                except Exception as e:
                    logger.error(f"Error generating new hash for user {user_id}: {e}")
                    # Still allow login, but don't migrate
                    return AuthenticationResult(
                        success=True, user_id=user_id, needs_password_update=False
                    )
            else:
                # Password is valid and already using current algorithm
                return AuthenticationResult(
                    success=True, user_id=user_id, needs_password_update=False
                )

        except Exception as e:
            logger.error(f"Authentication error for email {email}: {e}")
            return AuthenticationResult(success=False, error_message="Authentication error")

    async def complete_migration(self, user_id: str, new_password_hash: str) -> bool:
        """
        Complete password migration by updating database

        Args:
            user_id: User ID
            new_password_hash: New Argon2id hash

        Returns:
            True if successful
        """
        try:
            # Update password hash
            success = self.user_repo.update_password_hash(user_id, new_password_hash)

            if success:
                # Mark as migrated (clear migration flag)
                self.user_repo.mark_password_migrated(user_id)
                logger.info(f"Password migration completed for user {user_id}")
                return True
            else:
                logger.error(f"Failed to update password hash for user {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error completing migration for user {user_id}: {e}")
            return False


# Example integration for FastAPI
"""
Example FastAPI Integration:

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from shared.auth.password_migration_helper import PasswordMigrationHelper, AuthenticationResult
from shared.auth.password_hasher import hash_password

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    user_id: str

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    # Create migration helper
    helper = PasswordMigrationHelper(user_repo)

    # Authenticate and get migration info
    result = await helper.authenticate_and_migrate(
        request.email,
        request.password
    )

    if not result.success:
        raise HTTPException(
            status_code=401,
            detail=result.error_message or "Invalid credentials"
        )

    # If password needs migration, update it
    if result.needs_password_update and result.new_password_hash:
        await helper.complete_migration(
            result.user_id,
            result.new_password_hash
        )

    # Generate access token
    access_token = generate_jwt_token(result.user_id)

    return LoginResponse(
        access_token=access_token,
        user_id=result.user_id
    )


@router.post("/register")
async def register(
    email: str,
    password: str,
    user_repo: UserRepository = Depends(get_user_repository)
):
    # For new registrations, always use Argon2id
    password_hash = hash_password(password)

    user = await user_repo.create_user(
        email=email,
        password_hash=password_hash
    )

    return {"user_id": user.id}
"""

# Example integration for SQLAlchemy
"""
Example SQLAlchemy Repository:

from sqlalchemy.orm import Session
from sqlalchemy import select, update
from models import User

class SQLAlchemyUserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str) -> Optional[dict]:
        stmt = select(User).where(User.email == email)
        user = self.session.execute(stmt).scalar_one_or_none()

        if user:
            return {
                'id': str(user.id),
                'email': user.email,
                'password_hash': user.password_hash,
            }
        return None

    def update_password_hash(self, user_id: str, password_hash: str) -> bool:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                password_hash=password_hash,
                password_algorithm='argon2id'
            )
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def mark_password_migrated(self, user_id: str) -> bool:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(password_needs_migration=False)
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0
"""
