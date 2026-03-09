"""
Tests for Two-Factor Authentication Configuration
اختبارات إعدادات المصادقة الثنائية
"""

from datetime import timezone, datetime, timedelta, UTC

import pytest

from shared.auth.twofa_config import (
    TwoFAConfig,
    TwoFAEnforcementLevel,
    get_production_config,
    get_development_config,
    get_strict_config,
)


class TestTwoFAEnforcementLevel:
    """Tests for TwoFAEnforcementLevel enum"""

    def test_optional_value(self):
        """Test OPTIONAL enforcement level"""
        assert TwoFAEnforcementLevel.OPTIONAL.value == "optional"

    def test_recommended_value(self):
        """Test RECOMMENDED enforcement level"""
        assert TwoFAEnforcementLevel.RECOMMENDED.value == "recommended"

    def test_required_for_admin_value(self):
        """Test REQUIRED_FOR_ADMIN enforcement level"""
        assert TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN.value == "required_for_admin"

    def test_required_for_all_value(self):
        """Test REQUIRED_FOR_ALL enforcement level"""
        assert TwoFAEnforcementLevel.REQUIRED_FOR_ALL.value == "required_for_all"


class TestTwoFAConfig:
    """Tests for TwoFAConfig dataclass"""

    def test_default_enforcement_is_required_for_admin(self):
        """Test default enforcement is REQUIRED_FOR_ADMIN (security priority)"""
        config = TwoFAConfig()
        assert config.enforcement_level == TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN

    def test_default_grace_period_is_7_days(self):
        """Test default grace period is 7 days"""
        config = TwoFAConfig()
        assert config.grace_period_days == 7

    def test_default_totp_settings(self):
        """Test default TOTP settings"""
        config = TwoFAConfig()
        assert config.totp_issuer == "SAHOOL Agricultural Platform"
        assert config.totp_algorithm == "SHA1"
        assert config.totp_digits == 6
        assert config.totp_interval == 30

    def test_default_backup_codes(self):
        """Test default backup codes settings"""
        config = TwoFAConfig()
        assert config.backup_codes_count == 10
        assert config.backup_code_length == 8

    def test_default_security_settings(self):
        """Test default security settings"""
        config = TwoFAConfig()
        assert config.max_2fa_attempts == 5
        assert config.lockout_duration_minutes == 15

    def test_is_2fa_required_optional(self):
        """Test is_2fa_required_for_user with OPTIONAL enforcement"""
        config = TwoFAConfig(enforcement_level=TwoFAEnforcementLevel.OPTIONAL)
        assert config.is_2fa_required_for_user(["admin"]) is False
        assert config.is_2fa_required_for_user(["user"]) is False

    def test_is_2fa_required_for_admin_with_admin_role(self):
        """Test is_2fa_required_for_user with REQUIRED_FOR_ADMIN for admin"""
        config = TwoFAConfig(enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN)
        assert config.is_2fa_required_for_user(["admin"]) is True
        assert config.is_2fa_required_for_user(["supervisor"]) is True

    def test_is_2fa_required_for_admin_with_regular_user(self):
        """Test is_2fa_required_for_user with REQUIRED_FOR_ADMIN for regular user"""
        config = TwoFAConfig(enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN)
        assert config.is_2fa_required_for_user(["user"]) is False
        assert config.is_2fa_required_for_user(["farmer"]) is False

    def test_is_2fa_required_for_all(self):
        """Test is_2fa_required_for_user with REQUIRED_FOR_ALL"""
        config = TwoFAConfig(enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ALL)
        assert config.is_2fa_required_for_user(["admin"]) is True
        assert config.is_2fa_required_for_user(["user"]) is True
        assert config.is_2fa_required_for_user(["farmer"]) is True

    def test_is_within_grace_period_new_user(self):
        """Test is_within_grace_period for newly created user"""
        config = TwoFAConfig(grace_period_days=7)
        user_created = datetime.now(UTC) - timedelta(days=1)
        assert config.is_within_grace_period(user_created) is True

    def test_is_within_grace_period_old_user(self):
        """Test is_within_grace_period for user beyond grace period"""
        config = TwoFAConfig(grace_period_days=7)
        user_created = datetime.now(UTC) - timedelta(days=10)
        assert config.is_within_grace_period(user_created) is False

    def test_is_within_grace_period_zero_days(self):
        """Test is_within_grace_period with zero grace period"""
        config = TwoFAConfig(grace_period_days=0)
        user_created = datetime.now(UTC)
        assert config.is_within_grace_period(user_created) is False


class TestConfigPresets:
    """Tests for configuration presets"""

    def test_production_config(self):
        """Test get_production_config returns correct settings"""
        config = get_production_config()
        assert config.enforcement_level == TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN
        assert config.grace_period_days == 7
        assert config.max_2fa_attempts == 3
        assert config.lockout_duration_minutes == 30
        assert config.require_2fa_for_api_access is True

    def test_development_config(self):
        """Test get_development_config returns correct settings"""
        config = get_development_config()
        assert config.enforcement_level == TwoFAEnforcementLevel.OPTIONAL
        assert config.grace_period_days == 365
        assert config.max_2fa_attempts == 10
        assert config.require_2fa_for_api_access is False

    def test_strict_config(self):
        """Test get_strict_config returns correct settings"""
        config = get_strict_config()
        assert config.enforcement_level == TwoFAEnforcementLevel.REQUIRED_FOR_ALL
        assert config.grace_period_days == 0
        assert config.max_2fa_attempts == 3
        assert config.lockout_duration_minutes == 60
