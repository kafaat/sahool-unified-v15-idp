"""
Tests for Two-Factor Authentication Configuration
اختبارات إعدادات المصادقة الثنائية
"""

import pytest
from datetime import datetime, timedelta, UTC


class TestTwoFAEnforcementLevel:
    """Tests for TwoFAEnforcementLevel enum"""

    def test_optional_value(self):
        """Test OPTIONAL enforcement level"""
        # Import directly to avoid jwt dependency chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "twofa_config",
            "/home/user/sahool-unified-v15-idp/shared/auth/twofa_config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert module.TwoFAEnforcementLevel.OPTIONAL.value == "optional"

    def test_recommended_value(self):
        """Test RECOMMENDED enforcement level"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "twofa_config",
            "/home/user/sahool-unified-v15-idp/shared/auth/twofa_config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert module.TwoFAEnforcementLevel.RECOMMENDED.value == "recommended"

    def test_required_for_admin_value(self):
        """Test REQUIRED_FOR_ADMIN enforcement level"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "twofa_config",
            "/home/user/sahool-unified-v15-idp/shared/auth/twofa_config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert module.TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN.value == "required_for_admin"

    def test_required_for_all_value(self):
        """Test REQUIRED_FOR_ALL enforcement level"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "twofa_config",
            "/home/user/sahool-unified-v15-idp/shared/auth/twofa_config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert module.TwoFAEnforcementLevel.REQUIRED_FOR_ALL.value == "required_for_all"


class TestTwoFAConfig:
    """Tests for TwoFAConfig dataclass"""

    @pytest.fixture
    def module(self):
        """Load module directly to avoid import chain"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "twofa_config",
            "/home/user/sahool-unified-v15-idp/shared/auth/twofa_config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_default_enforcement_is_required_for_admin(self, module):
        """Test default enforcement is REQUIRED_FOR_ADMIN (security priority)"""
        config = module.TwoFAConfig()
        assert config.enforcement_level == module.TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN

    def test_default_grace_period_is_7_days(self, module):
        """Test default grace period is 7 days"""
        config = module.TwoFAConfig()
        assert config.grace_period_days == 7

    def test_default_totp_settings(self, module):
        """Test default TOTP settings"""
        config = module.TwoFAConfig()
        assert config.totp_issuer == "SAHOOL Agricultural Platform"
        assert config.totp_algorithm == "SHA1"
        assert config.totp_digits == 6
        assert config.totp_interval == 30

    def test_default_backup_codes(self, module):
        """Test default backup codes settings"""
        config = module.TwoFAConfig()
        assert config.backup_codes_count == 10
        assert config.backup_code_length == 8

    def test_default_security_settings(self, module):
        """Test default security settings"""
        config = module.TwoFAConfig()
        assert config.max_2fa_attempts == 5
        assert config.lockout_duration_minutes == 15

    def test_is_2fa_required_optional(self, module):
        """Test is_2fa_required_for_user with OPTIONAL enforcement"""
        config = module.TwoFAConfig(
            enforcement_level=module.TwoFAEnforcementLevel.OPTIONAL
        )
        assert config.is_2fa_required_for_user(["admin"]) is False
        assert config.is_2fa_required_for_user(["user"]) is False

    def test_is_2fa_required_for_admin_with_admin_role(self, module):
        """Test is_2fa_required_for_user with REQUIRED_FOR_ADMIN for admin"""
        config = module.TwoFAConfig(
            enforcement_level=module.TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN
        )
        assert config.is_2fa_required_for_user(["admin"]) is True
        assert config.is_2fa_required_for_user(["supervisor"]) is True

    def test_is_2fa_required_for_admin_with_regular_user(self, module):
        """Test is_2fa_required_for_user with REQUIRED_FOR_ADMIN for regular user"""
        config = module.TwoFAConfig(
            enforcement_level=module.TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN
        )
        assert config.is_2fa_required_for_user(["user"]) is False
        assert config.is_2fa_required_for_user(["farmer"]) is False

    def test_is_2fa_required_for_all(self, module):
        """Test is_2fa_required_for_user with REQUIRED_FOR_ALL"""
        config = module.TwoFAConfig(
            enforcement_level=module.TwoFAEnforcementLevel.REQUIRED_FOR_ALL
        )
        assert config.is_2fa_required_for_user(["admin"]) is True
        assert config.is_2fa_required_for_user(["user"]) is True
        assert config.is_2fa_required_for_user(["farmer"]) is True

    def test_is_within_grace_period_new_user(self, module):
        """Test is_within_grace_period for newly created user"""
        config = module.TwoFAConfig(grace_period_days=7)
        user_created = datetime.now(UTC) - timedelta(days=1)
        assert config.is_within_grace_period(user_created) is True

    def test_is_within_grace_period_old_user(self, module):
        """Test is_within_grace_period for user beyond grace period"""
        config = module.TwoFAConfig(grace_period_days=7)
        user_created = datetime.now(UTC) - timedelta(days=10)
        assert config.is_within_grace_period(user_created) is False

    def test_is_within_grace_period_zero_days(self, module):
        """Test is_within_grace_period with zero grace period"""
        config = module.TwoFAConfig(grace_period_days=0)
        user_created = datetime.now(UTC)
        assert config.is_within_grace_period(user_created) is False


class TestConfigPresets:
    """Tests for configuration presets"""

    @pytest.fixture
    def module(self):
        """Load module directly"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "twofa_config",
            "/home/user/sahool-unified-v15-idp/shared/auth/twofa_config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_production_config(self, module):
        """Test get_production_config returns correct settings"""
        config = module.get_production_config()
        assert config.enforcement_level == module.TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN
        assert config.grace_period_days == 7
        assert config.max_2fa_attempts == 3
        assert config.lockout_duration_minutes == 30
        assert config.require_2fa_for_api_access is True

    def test_development_config(self, module):
        """Test get_development_config returns correct settings"""
        config = module.get_development_config()
        assert config.enforcement_level == module.TwoFAEnforcementLevel.OPTIONAL
        assert config.grace_period_days == 365
        assert config.max_2fa_attempts == 10
        assert config.require_2fa_for_api_access is False

    def test_strict_config(self, module):
        """Test get_strict_config returns correct settings"""
        config = module.get_strict_config()
        assert config.enforcement_level == module.TwoFAEnforcementLevel.REQUIRED_FOR_ALL
        assert config.grace_period_days == 0
        assert config.max_2fa_attempts == 3
        assert config.lockout_duration_minutes == 60
