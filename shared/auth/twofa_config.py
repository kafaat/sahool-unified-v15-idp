"""
Two-Factor Authentication Configuration for SAHOOL Platform
إعدادات المصادقة الثنائية لمنصة سهول

Configuration for 2FA enforcement, grace periods, and security settings.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class TwoFAEnforcementLevel(str, Enum):
    """2FA enforcement levels"""

    OPTIONAL = "optional"  # 2FA is optional for all users
    RECOMMENDED = "recommended"  # 2FA is recommended but not required
    REQUIRED_FOR_ADMIN = "required_for_admin"  # 2FA required only for admin users
    REQUIRED_FOR_ALL = "required_for_all"  # 2FA required for all users


@dataclass
class TwoFAConfig:
    """Two-Factor Authentication configuration"""

    # Enforcement settings
    enforcement_level: TwoFAEnforcementLevel = TwoFAEnforcementLevel.OPTIONAL
    grace_period_days: int = 30  # Days to set up 2FA before enforcement

    # TOTP settings
    totp_issuer: str = "SAHOOL Agricultural Platform"
    totp_algorithm: str = "SHA1"
    totp_digits: int = 6
    totp_interval: int = 30  # seconds
    totp_valid_window: int = 1  # Accept codes from previous/next interval

    # Backup codes
    backup_codes_count: int = 10
    backup_code_length: int = 8

    # Security settings
    max_2fa_attempts: int = 5  # Max failed 2FA attempts before lockout
    lockout_duration_minutes: int = 15  # Lockout duration after max attempts
    require_2fa_for_api_access: bool = False  # Require 2FA for API token generation

    # Notification settings
    notify_on_2fa_setup: bool = True
    notify_on_2fa_disable: bool = True
    notify_on_backup_code_used: bool = True

    def is_2fa_required_for_user(self, user_roles: list[str]) -> bool:
        """
        Check if 2FA is required for a user based on their roles.

        Args:
            user_roles: List of user roles

        Returns:
            True if 2FA is required
        """
        if self.enforcement_level == TwoFAEnforcementLevel.OPTIONAL:
            return False

        if self.enforcement_level == TwoFAEnforcementLevel.RECOMMENDED:
            return False

        if self.enforcement_level == TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN:
            return "admin" in user_roles or "supervisor" in user_roles

        return self.enforcement_level == TwoFAEnforcementLevel.REQUIRED_FOR_ALL

    def is_within_grace_period(self, user_created_at: datetime) -> bool:
        """
        Check if user is within grace period for 2FA setup.

        Args:
            user_created_at: User creation timestamp

        Returns:
            True if within grace period
        """
        if self.grace_period_days <= 0:
            return False

        grace_period_end = user_created_at + timedelta(days=self.grace_period_days)
        return datetime.now(UTC) < grace_period_end


# Global configuration instance
_twofa_config: TwoFAConfig | None = None


def get_twofa_config() -> TwoFAConfig:
    """
    Get the global 2FA configuration.

    Returns:
        TwoFAConfig instance
    """
    global _twofa_config
    if _twofa_config is None:
        _twofa_config = TwoFAConfig()
    return _twofa_config


def set_twofa_config(config: TwoFAConfig) -> None:
    """
    Set the global 2FA configuration.

    Args:
        config: TwoFAConfig instance to use
    """
    global _twofa_config
    _twofa_config = config
    logger.info(f"2FA configuration updated: enforcement={config.enforcement_level}")


def configure_twofa(
    enforcement_level: TwoFAEnforcementLevel = TwoFAEnforcementLevel.OPTIONAL,
    grace_period_days: int = 30,
    **kwargs,
) -> TwoFAConfig:
    """
    Configure 2FA settings.

    Args:
        enforcement_level: Level of 2FA enforcement
        grace_period_days: Grace period for 2FA setup
        **kwargs: Additional configuration options

    Returns:
        Configured TwoFAConfig instance

    Example:
        ```python
        configure_twofa(
            enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN,
            grace_period_days=7,
            max_2fa_attempts=3
        )
        ```
    """
    config = TwoFAConfig(
        enforcement_level=enforcement_level,
        grace_period_days=grace_period_days,
        **kwargs,
    )
    set_twofa_config(config)
    return config


# ══════════════════════════════════════════════════════════════════════════════
# 2FA Enforcement Middleware
# ══════════════════════════════════════════════════════════════════════════════


class TwoFAEnforcementMiddleware:
    """
    Middleware to enforce 2FA requirements.

    This should be added to your FastAPI application after authentication.
    """

    def __init__(self, config: TwoFAConfig | None = None):
        self.config = config or get_twofa_config()

    async def check_2fa_requirement(
        self,
        user_id: str,
        user_roles: list[str],
        user_created_at: datetime,
        twofa_enabled: bool,
        exempt_paths: list[str] | None = None,
    ) -> tuple[bool, str | None]:
        """
        Check if 2FA is required for the user and if they comply.

        Args:
            user_id: User identifier
            user_roles: User roles
            user_created_at: User creation timestamp
            twofa_enabled: Whether user has 2FA enabled
            exempt_paths: List of paths exempt from 2FA requirement

        Returns:
            Tuple of (is_compliant, error_message)
        """
        # Check if 2FA is required for this user
        is_required = self.config.is_2fa_required_for_user(user_roles)

        if not is_required:
            return True, None

        # If 2FA is enabled, user is compliant
        if twofa_enabled:
            return True, None

        # Check if within grace period
        if self.config.is_within_grace_period(user_created_at):
            logger.warning(
                f"User {user_id} is within grace period for 2FA setup "
                f"({self.config.grace_period_days} days)"
            )
            return True, None

        # User is not compliant
        error_message = (
            f"Two-factor authentication is required for {user_roles[0]} users. "
            f"Please set up 2FA in your account settings."
        )
        logger.warning(f"User {user_id} failed 2FA requirement check")
        return False, error_message


# ══════════════════════════════════════════════════════════════════════════════
# Example Configuration Presets
# ══════════════════════════════════════════════════════════════════════════════


def get_production_config() -> TwoFAConfig:
    """
    Get production-ready 2FA configuration.

    - Required for admin and supervisor users
    - 7-day grace period
    - Strict security settings
    """
    return TwoFAConfig(
        enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN,
        grace_period_days=7,
        max_2fa_attempts=3,
        lockout_duration_minutes=30,
        require_2fa_for_api_access=True,
        notify_on_2fa_setup=True,
        notify_on_2fa_disable=True,
        notify_on_backup_code_used=True,
    )


def get_development_config() -> TwoFAConfig:
    """
    Get development 2FA configuration.

    - Optional for all users
    - Relaxed security settings
    """
    return TwoFAConfig(
        enforcement_level=TwoFAEnforcementLevel.OPTIONAL,
        grace_period_days=365,  # Very long grace period
        max_2fa_attempts=10,
        lockout_duration_minutes=5,
        require_2fa_for_api_access=False,
        notify_on_2fa_setup=False,
        notify_on_2fa_disable=False,
        notify_on_backup_code_used=False,
    )


def get_strict_config() -> TwoFAConfig:
    """
    Get strict 2FA configuration.

    - Required for all users
    - No grace period
    - Maximum security
    """
    return TwoFAConfig(
        enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ALL,
        grace_period_days=0,  # No grace period
        max_2fa_attempts=3,
        lockout_duration_minutes=60,
        require_2fa_for_api_access=True,
        notify_on_2fa_setup=True,
        notify_on_2fa_disable=True,
        notify_on_backup_code_used=True,
    )
