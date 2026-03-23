"""
Tests for shared/domain/tenancy/models.py module
اختبارات وحدة نماذج المستأجرين
"""

from datetime import UTC, datetime

import pytest


class TestTenantStatus:
    """Tests for TenantStatus enum"""

    def test_status_values(self):
        """Test all status values exist"""
        from shared.domain.tenancy.models import TenantStatus

        assert TenantStatus.ACTIVE == "active"
        assert TenantStatus.SUSPENDED == "suspended"
        assert TenantStatus.TRIAL == "trial"
        assert TenantStatus.EXPIRED == "expired"

    def test_status_is_string_enum(self):
        """Test TenantStatus is a string enum"""
        from shared.domain.tenancy.models import TenantStatus

        assert isinstance(TenantStatus.ACTIVE, str)
        assert TenantStatus.ACTIVE.value == "active"


class TestTenantPlan:
    """Tests for TenantPlan enum"""

    def test_plan_values(self):
        """Test all plan values exist"""
        from shared.domain.tenancy.models import TenantPlan

        assert TenantPlan.FREE == "free"
        assert TenantPlan.BASIC == "basic"
        assert TenantPlan.PRO == "pro"
        assert TenantPlan.ENTERPRISE == "enterprise"

    def test_plan_is_string_enum(self):
        """Test TenantPlan is a string enum"""
        from shared.domain.tenancy.models import TenantPlan

        assert isinstance(TenantPlan.FREE, str)


class TestTenantSettings:
    """Tests for TenantSettings dataclass"""

    def test_default_values(self):
        """Test default settings values"""
        from shared.domain.tenancy.models import TenantSettings

        settings = TenantSettings()

        assert settings.max_users == 10
        assert settings.max_fields == 50
        assert settings.max_storage_gb == 5
        assert settings.features == {}
        assert settings.locale == "ar"
        assert settings.timezone == "Asia/Aden"

    def test_custom_values(self):
        """Test custom settings values"""
        from shared.domain.tenancy.models import TenantSettings

        settings = TenantSettings(
            max_users=100,
            max_fields=500,
            max_storage_gb=50,
            features={"advanced_analytics": True},
            locale="en",
            timezone="UTC",
        )

        assert settings.max_users == 100
        assert settings.max_fields == 500
        assert settings.max_storage_gb == 50
        assert settings.features == {"advanced_analytics": True}
        assert settings.locale == "en"
        assert settings.timezone == "UTC"

    def test_to_dict(self):
        """Test settings serialization to dict"""
        from shared.domain.tenancy.models import TenantSettings

        settings = TenantSettings(max_users=25, features={"feature1": True})
        result = settings.to_dict()

        assert result["max_users"] == 25
        assert result["max_fields"] == 50
        assert result["features"] == {"feature1": True}
        assert result["locale"] == "ar"

    def test_from_dict(self):
        """Test settings deserialization from dict"""
        from shared.domain.tenancy.models import TenantSettings

        data = {
            "max_users": 50,
            "max_fields": 200,
            "max_storage_gb": 20,
            "features": {"irrigation": True},
            "locale": "en",
            "timezone": "Asia/Riyadh",
        }

        settings = TenantSettings.from_dict(data)

        assert settings.max_users == 50
        assert settings.max_fields == 200
        assert settings.features == {"irrigation": True}
        assert settings.timezone == "Asia/Riyadh"

    def test_roundtrip_serialization(self):
        """Test settings roundtrip through dict"""
        from shared.domain.tenancy.models import TenantSettings

        original = TenantSettings(max_users=75, features={"ndvi": True, "weather": True})

        data = original.to_dict()
        restored = TenantSettings.from_dict(data)

        assert restored.max_users == original.max_users
        assert restored.features == original.features


class TestTenant:
    """Tests for Tenant dataclass"""

    def test_create_tenant_free_plan(self):
        """Test creating tenant with free plan defaults to trial status"""
        from shared.domain.tenancy.models import Tenant, TenantPlan, TenantStatus

        tenant = Tenant.create(name="Test Farm")

        assert tenant.name == "Test Farm"
        assert tenant.status == TenantStatus.TRIAL
        assert tenant.plan == TenantPlan.FREE
        assert tenant.id is not None
        assert len(tenant.id) == 36  # UUID length

    def test_create_tenant_paid_plan(self):
        """Test creating tenant with paid plan defaults to active status"""
        from shared.domain.tenancy.models import Tenant, TenantPlan, TenantStatus

        tenant = Tenant.create(name="Enterprise Farm", plan=TenantPlan.ENTERPRISE)

        assert tenant.name == "Enterprise Farm"
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.plan == TenantPlan.ENTERPRISE

    def test_create_tenant_with_arabic_name(self):
        """Test creating tenant with Arabic name"""
        from shared.domain.tenancy.models import Tenant, TenantPlan

        tenant = Tenant.create(name="Al Rashid Farm", name_ar="مزرعة الراشد", plan=TenantPlan.PRO)

        assert tenant.name == "Al Rashid Farm"
        assert tenant.name_ar == "مزرعة الراشد"

    def test_create_tenant_with_owner(self):
        """Test creating tenant with owner ID"""
        from shared.domain.tenancy.models import Tenant

        tenant = Tenant.create(name="Owned Farm", owner_id="user-123")

        assert tenant.owner_id == "user-123"

    def test_create_tenant_timestamps(self):
        """Test tenant timestamps are set correctly"""
        from shared.domain.tenancy.models import Tenant

        before = datetime.now(UTC)
        tenant = Tenant.create(name="Timestamp Test")
        after = datetime.now(UTC)

        assert before <= tenant.created_at <= after
        assert before <= tenant.updated_at <= after
        assert tenant.created_at == tenant.updated_at

    def test_create_tenant_default_settings(self):
        """Test tenant has default settings"""
        from shared.domain.tenancy.models import Tenant, TenantSettings

        tenant = Tenant.create(name="Settings Test")

        assert isinstance(tenant.settings, TenantSettings)
        assert tenant.settings.max_users == 10
        assert tenant.settings.locale == "ar"

    def test_tenant_to_dict(self):
        """Test tenant serialization to dict"""
        from shared.domain.tenancy.models import Tenant, TenantPlan

        tenant = Tenant.create(
            name="Serialization Test",
            name_ar="اختبار التسلسل",
            plan=TenantPlan.BASIC,
            owner_id="owner-456",
        )

        result = tenant.to_dict()

        assert result["name"] == "Serialization Test"
        assert result["name_ar"] == "اختبار التسلسل"
        assert result["status"] == "active"  # BASIC plan = active
        assert result["plan"] == "basic"
        assert result["owner_id"] == "owner-456"
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "settings" in result

    def test_tenant_to_dict_settings_included(self):
        """Test tenant dict includes settings as dict"""
        from shared.domain.tenancy.models import Tenant

        tenant = Tenant.create(name="Settings Dict Test")
        result = tenant.to_dict()

        assert isinstance(result["settings"], dict)
        assert result["settings"]["max_users"] == 10
        assert result["settings"]["locale"] == "ar"

    def test_tenant_id_is_uuid(self):
        """Test tenant ID is valid UUID format"""
        import re

        from shared.domain.tenancy.models import Tenant

        tenant = Tenant.create(name="UUID Test")

        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        assert re.match(uuid_pattern, tenant.id)

    def test_multiple_tenants_unique_ids(self):
        """Test multiple tenants get unique IDs"""
        from shared.domain.tenancy.models import Tenant

        tenants = [Tenant.create(name=f"Tenant {i}") for i in range(5)]
        ids = [t.id for t in tenants]

        assert len(ids) == len(set(ids))  # All unique

    def test_tenant_without_arabic_name(self):
        """Test tenant can be created without Arabic name"""
        from shared.domain.tenancy.models import Tenant

        tenant = Tenant.create(name="English Only")

        assert tenant.name_ar is None

    def test_tenant_status_values_in_dict(self):
        """Test all tenant statuses serialize correctly"""
        from datetime import UTC, datetime

        from shared.domain.tenancy.models import Tenant, TenantPlan, TenantSettings, TenantStatus

        now = datetime.now(UTC)

        for status in TenantStatus:
            tenant = Tenant(
                id="test-id",
                name="Status Test",
                name_ar=None,
                status=status,
                plan=TenantPlan.BASIC,
                settings=TenantSettings(),
                owner_id=None,
                created_at=now,
                updated_at=now,
            )
            result = tenant.to_dict()
            assert result["status"] == status.value


class TestTenantPlanBehavior:
    """Tests for plan-based behavior"""

    def test_free_plan_trial_status(self):
        """Test FREE plan creates TRIAL status"""
        from shared.domain.tenancy.models import Tenant, TenantPlan, TenantStatus

        tenant = Tenant.create(name="Free Test", plan=TenantPlan.FREE)
        assert tenant.status == TenantStatus.TRIAL

    def test_basic_plan_active_status(self):
        """Test BASIC plan creates ACTIVE status"""
        from shared.domain.tenancy.models import Tenant, TenantPlan, TenantStatus

        tenant = Tenant.create(name="Basic Test", plan=TenantPlan.BASIC)
        assert tenant.status == TenantStatus.ACTIVE

    def test_pro_plan_active_status(self):
        """Test PRO plan creates ACTIVE status"""
        from shared.domain.tenancy.models import Tenant, TenantPlan, TenantStatus

        tenant = Tenant.create(name="Pro Test", plan=TenantPlan.PRO)
        assert tenant.status == TenantStatus.ACTIVE

    def test_enterprise_plan_active_status(self):
        """Test ENTERPRISE plan creates ACTIVE status"""
        from shared.domain.tenancy.models import Tenant, TenantPlan, TenantStatus

        tenant = Tenant.create(name="Enterprise Test", plan=TenantPlan.ENTERPRISE)
        assert tenant.status == TenantStatus.ACTIVE


class TestTenantSettingsFeatures:
    """Tests for tenant settings features"""

    def test_empty_features_default(self):
        """Test features default to empty dict"""
        from shared.domain.tenancy.models import TenantSettings

        settings = TenantSettings()
        assert settings.features == {}
        assert isinstance(settings.features, dict)

    def test_features_with_boolean_values(self):
        """Test features with boolean values"""
        from shared.domain.tenancy.models import TenantSettings

        settings = TenantSettings(features={"ndvi_analysis": True, "weather_alerts": True, "marketplace": False})

        assert settings.features["ndvi_analysis"] is True
        assert settings.features["marketplace"] is False

    def test_features_with_mixed_values(self):
        """Test features with mixed value types"""
        from shared.domain.tenancy.models import TenantSettings

        settings = TenantSettings(features={"enabled": True, "max_alerts": 100, "channels": ["email", "sms"]})

        assert settings.features["enabled"] is True
        assert settings.features["max_alerts"] == 100
        assert settings.features["channels"] == ["email", "sms"]

    def test_features_preserved_in_serialization(self):
        """Test complex features are preserved in serialization"""
        from shared.domain.tenancy.models import TenantSettings

        original_features = {
            "irrigation": {"enabled": True, "sensors": 5},
            "alerts": ["email", "sms", "push"],
        }

        settings = TenantSettings(features=original_features)
        data = settings.to_dict()
        restored = TenantSettings.from_dict(data)

        assert restored.features == original_features


class TestTenantTimezones:
    """Tests for tenant timezone settings"""

    def test_default_timezone(self):
        """Test default timezone is Asia/Aden"""
        from shared.domain.tenancy.models import TenantSettings

        settings = TenantSettings()
        assert settings.timezone == "Asia/Aden"

    def test_custom_timezone(self):
        """Test custom timezone can be set"""
        from shared.domain.tenancy.models import TenantSettings

        timezones = ["Asia/Riyadh", "Asia/Dubai", "Africa/Cairo", "UTC", "Europe/London"]

        for tz in timezones:
            settings = TenantSettings(timezone=tz)
            assert settings.timezone == tz


class TestTenantLocale:
    """Tests for tenant locale settings"""

    def test_default_locale_arabic(self):
        """Test default locale is Arabic"""
        from shared.domain.tenancy.models import TenantSettings

        settings = TenantSettings()
        assert settings.locale == "ar"

    def test_english_locale(self):
        """Test English locale can be set"""
        from shared.domain.tenancy.models import TenantSettings

        settings = TenantSettings(locale="en")
        assert settings.locale == "en"

    def test_locale_preserved_in_serialization(self):
        """Test locale is preserved in serialization"""
        from shared.domain.tenancy.models import TenantSettings

        settings = TenantSettings(locale="en")
        data = settings.to_dict()

        assert data["locale"] == "en"

        restored = TenantSettings.from_dict(data)
        assert restored.locale == "en"
