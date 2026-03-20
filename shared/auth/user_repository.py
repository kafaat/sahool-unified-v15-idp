"""
User Repository for JWT Authentication
مستودع المستخدمين للتحقق من JWT

Provides database access for user validation.
"""

from __future__ import annotations

import logging

try:
    from sqlalchemy import and_, select
    from sqlalchemy.ext.asyncio import AsyncSession

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    AsyncSession = None  # Type stub for when SQLAlchemy is not installed

logger = logging.getLogger(__name__)


class UserValidationData:
    """
    Data class for user validation.
    فئة البيانات للتحقق من المستخدم.
    """

    def __init__(
        self,
        user_id: str,
        email: str,
        is_active: bool,
        is_verified: bool,
        roles: list[str],
        tenant_id: str | None = None,
        is_deleted: bool = False,
        is_suspended: bool = False,
    ):
        self.user_id = user_id
        self.email = email
        self.is_active = is_active
        self.is_verified = is_verified
        self.roles = roles
        self.tenant_id = tenant_id
        self.is_deleted = is_deleted
        self.is_suspended = is_suspended

    @property
    def is_valid(self) -> bool:
        """Check if user is valid for authentication"""
        return self.is_active and self.is_verified and not self.is_deleted and not self.is_suspended

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "roles": self.roles,
            "tenant_id": self.tenant_id,
            "is_deleted": self.is_deleted,
            "is_suspended": self.is_suspended,
        }


class UserRepository:
    """
    Repository for user data access.
    مستودع للوصول إلى بيانات المستخدم.
    """

    def __init__(self, session: AsyncSession | None = None):
        """
        Initialize user repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def get_user_validation_data(self, user_id: str) -> UserValidationData | None:
        """
        Get user validation data from database.

        This method should be overridden in your implementation to query
        your actual user table. The example below shows the expected structure.

        Args:
            user_id: User identifier

        Returns:
            UserValidationData or None if user not found
        """
        if not self.session:
            logger.warning("No database session available for user validation")
            return None

        try:
            if SQLALCHEMY_AVAILABLE and self.session:
                try:
                    user_model = self._get_user_model()
                except NotImplementedError:
                    logger.warning(
                        "UserRepository._get_user_model() not implemented. "
                        "Subclass UserRepository and override _get_user_model()."
                    )
                    return None

                # SQLAlchemy async session query
                result = await self.session.execute(
                    select(user_model).where(user_model.id == user_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.warning(f"User {user_id} not found in database")
                    return None

                # Fail-closed: default to restrictive values when attributes
                # are missing, so an incomplete user model denies access
                # rather than silently granting it.
                return UserValidationData(
                    user_id=str(user.id),
                    email=getattr(user, "email", ""),
                    is_active=getattr(user, "is_active", False),
                    is_verified=getattr(user, "is_verified", False),
                    roles=getattr(user, "roles", []) or [],
                    tenant_id=getattr(user, "tenant_id", None),
                    is_deleted=getattr(user, "is_deleted", True),
                    is_suspended=getattr(user, "is_suspended", True),
                )

            logger.warning(
                "UserRepository.get_user_validation_data() - no session available. "
                "Override this method or provide a database session."
            )
            return None

        except Exception as e:
            logger.error(f"Error fetching user {user_id} from database: {e}")
            return None

    def _get_user_model(self):
        """
        Get the User model class. Override in subclass if your model
        has a different name or location.
        """
        raise NotImplementedError(
            "Subclass UserRepository and implement _get_user_model() "
            "to return your SQLAlchemy User model class."
        )

    async def update_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp.

        Args:
            user_id: User identifier

        Returns:
            True if updated successfully
        """
        if not self.session:
            return False

        try:
            # ============================================================
            # IMPORTANT: Replace this with your actual update query
            # ============================================================
            # Example implementation:
            #
            # from your_models import User
            # from datetime import datetime, timezone
            #
            # stmt = (
            #     update(User)
            #     .where(User.id == user_id)
            #     .values(last_login=datetime.now(timezone.utc))
            # )
            # await self.session.execute(stmt)
            # await self.session.commit()
            # return True
            # ============================================================

            logger.debug(f"Last login update for user {user_id} (not implemented)")
            return False

        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
            return False


# asyncpg-based implementation for FastAPI services using raw connection pools
class AsyncpgUserRepository(UserRepository):
    """
    User repository using asyncpg connection pool.
    مستودع المستخدمين باستخدام asyncpg.

    This is the recommended implementation for FastAPI services
    that use asyncpg directly (without SQLAlchemy).
    """

    def __init__(self, pool):
        """
        Initialize with an asyncpg connection pool.

        Args:
            pool: asyncpg Pool instance (from asyncpg.create_pool())
        """
        super().__init__(session=None)
        self._pool = pool

    async def get_user_validation_data(self, user_id: str) -> UserValidationData | None:
        """Get user from PostgreSQL via asyncpg pool"""
        if not self._pool:
            logger.warning("No asyncpg pool available for user validation")
            return None

        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT id, email, status, "emailVerified", role, "tenantId"
                    FROM "User"
                    WHERE id = $1
                    """,
                    user_id,
                )

            if not row:
                logger.warning(f"User {user_id} not found in database")
                return None

            status = row.get("status", "ACTIVE")
            return UserValidationData(
                user_id=str(row["id"]),
                email=row.get("email", ""),
                is_active=status == "ACTIVE",
                is_verified=bool(row.get("emailVerified", False)),
                roles=[row.get("role", "FARMER").lower()],
                tenant_id=row.get("tenantId"),
                is_deleted=status == "DELETED",
                is_suspended=status == "SUSPENDED",
            )

        except Exception as e:
            logger.error(f"Error fetching user {user_id} from database: {e}")
            return None

    async def update_last_login(self, user_id: str) -> bool:
        """Update last login timestamp via asyncpg"""
        if not self._pool:
            return False

        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    'UPDATE "User" SET "lastLoginAt" = NOW() WHERE id = $1',
                    user_id,
                )
            return True
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
            return False


# In-memory fallback implementation (for development/testing)
class InMemoryUserRepository(UserRepository):
    """
    In-memory user repository for testing.
    مستودع المستخدمين في الذاكرة للاختبار.
    """

    def __init__(self):
        super().__init__(session=None)
        self._users: dict[str, UserValidationData] = {}

    def add_test_user(
        self,
        user_id: str,
        email: str,
        is_active: bool = True,
        is_verified: bool = True,
        roles: list[str] | None = None,
        tenant_id: str | None = None,
        is_deleted: bool = False,
        is_suspended: bool = False,
    ) -> None:
        """Add a test user"""
        self._users[user_id] = UserValidationData(
            user_id=user_id,
            email=email,
            is_active=is_active,
            is_verified=is_verified,
            roles=roles or ["user"],
            tenant_id=tenant_id,
            is_deleted=is_deleted,
            is_suspended=is_suspended,
        )

    async def get_user_validation_data(self, user_id: str) -> UserValidationData | None:
        """Get user from in-memory store"""
        return self._users.get(user_id)


# Global repository instance
_user_repository: UserRepository | None = None


def get_user_repository() -> UserRepository | None:
    """
    Get the global user repository instance.

    Returns:
        UserRepository instance or None
    """
    global _user_repository
    return _user_repository


def set_user_repository(repository: UserRepository) -> None:
    """
    Set the global user repository instance.

    Args:
        repository: UserRepository instance to use
    """
    global _user_repository
    _user_repository = repository
    logger.info(f"User repository set to {type(repository).__name__}")
