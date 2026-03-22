"""
Tests for SAHOOL NATS Subject Constants
========================================
اختبارات ثوابت موضوعات NATS

Tests subject constant values, naming conventions, tenant-scoped subjects,
and builder classes.
"""

import pytest

from shared.events.subjects import (
    # Field subjects
    SAHOOL_FIELD_CREATED,
    SAHOOL_FIELD_UPDATED,
    SAHOOL_FIELD_DELETED,
    SAHOOL_FIELD_ALL,
    # Farm subjects
    SAHOOL_FARM_CREATED,
    SAHOOL_FARM_UPDATED,
    SAHOOL_FARM_DELETED,
    SAHOOL_FARM_ALL,
    # Weather subjects
    SAHOOL_WEATHER_FORECAST,
    SAHOOL_WEATHER_ALERT,
    SAHOOL_WEATHER_ALERT_FROST,
    SAHOOL_WEATHER_ALL,
    SAHOOL_WEATHER_ALERTS_ALL,
    # Satellite subjects
    SAHOOL_SATELLITE_DATA_READY,
    SAHOOL_SATELLITE_PROCESSING_STARTED,
    SAHOOL_SATELLITE_PROCESSING_COMPLETED,
    SAHOOL_SATELLITE_PROCESSING_FAILED,
    SAHOOL_NDVI_COMPUTED,
    SAHOOL_SATELLITE_ALL,
    # Crop health
    SAHOOL_HEALTH_DISEASE_DETECTED,
    SAHOOL_HEALTH_PEST_DETECTED,
    SAHOOL_HEALTH_STRESS_DETECTED,
    SAHOOL_HEALTH_ALL,
    # Billing
    SAHOOL_BILLING_SUBSCRIPTION_CREATED,
    SAHOOL_BILLING_PAYMENT_COMPLETED,
    SAHOOL_BILLING_ALL,
    # Inventory
    SAHOOL_INVENTORY_LOW_STOCK,
    SAHOOL_INVENTORY_ALL,
    # Agent
    SAHOOL_AGENT_EXECUTION_STARTED,
    SAHOOL_AGENT_ALL,
    # Calibration
    SAHOOL_CALIBRATION_RUN_QUEUED,
    SAHOOL_CALIBRATION_ALL,
    # Functions
    get_tenant_subject,
    get_tenant_wildcard,
    get_all_tenants_subject,
    # Builders
    TenantSubjectBuilder,
    DomainSubjectBuilder,
)

VALID_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


# ═══════════════════════════════════════════════════════════════════════════════
# Subject Constant Values
# ═══════════════════════════════════════════════════════════════════════════════


class TestSubjectConstants:
    """Test that subject constants follow the naming convention."""

    def test_field_subjects_start_with_sahool(self):
        assert SAHOOL_FIELD_CREATED == "sahool.field.created"
        assert SAHOOL_FIELD_UPDATED == "sahool.field.updated"
        assert SAHOOL_FIELD_DELETED == "sahool.field.deleted"

    def test_field_wildcard(self):
        assert SAHOOL_FIELD_ALL == "sahool.field.>"

    def test_farm_subjects(self):
        assert SAHOOL_FARM_CREATED == "sahool.farm.created"
        assert SAHOOL_FARM_UPDATED == "sahool.farm.updated"
        assert SAHOOL_FARM_DELETED == "sahool.farm.deleted"
        assert SAHOOL_FARM_ALL == "sahool.farm.*"

    def test_weather_subjects(self):
        assert SAHOOL_WEATHER_FORECAST == "sahool.weather.forecast"
        assert SAHOOL_WEATHER_ALERT == "sahool.weather.alert"
        assert SAHOOL_WEATHER_ALERT_FROST == "sahool.weather.alert.frost"
        assert SAHOOL_WEATHER_ALL == "sahool.weather.>"
        assert SAHOOL_WEATHER_ALERTS_ALL == "sahool.weather.alert.*"

    def test_satellite_subjects(self):
        assert SAHOOL_SATELLITE_DATA_READY == "sahool.satellite.data.ready"
        assert SAHOOL_SATELLITE_PROCESSING_STARTED == "sahool.satellite.processing.started"
        assert SAHOOL_SATELLITE_PROCESSING_COMPLETED == "sahool.satellite.processing.completed"
        assert SAHOOL_SATELLITE_PROCESSING_FAILED == "sahool.satellite.processing.failed"
        assert SAHOOL_NDVI_COMPUTED == "sahool.satellite.ndvi.computed"
        assert SAHOOL_SATELLITE_ALL == "sahool.satellite.>"

    def test_health_subjects(self):
        assert SAHOOL_HEALTH_DISEASE_DETECTED == "sahool.health.disease.detected"
        assert SAHOOL_HEALTH_PEST_DETECTED == "sahool.health.pest.detected"
        assert SAHOOL_HEALTH_STRESS_DETECTED == "sahool.health.stress.detected"
        assert SAHOOL_HEALTH_ALL == "sahool.health.>"

    def test_billing_subjects(self):
        assert SAHOOL_BILLING_SUBSCRIPTION_CREATED == "sahool.billing.subscription.created"
        assert SAHOOL_BILLING_PAYMENT_COMPLETED == "sahool.billing.payment.completed"
        assert SAHOOL_BILLING_ALL == "sahool.billing.>"

    def test_inventory_subjects(self):
        assert SAHOOL_INVENTORY_LOW_STOCK == "sahool.inventory.low_stock"
        assert SAHOOL_INVENTORY_ALL == "sahool.inventory.>"

    def test_agent_subjects(self):
        assert SAHOOL_AGENT_EXECUTION_STARTED == "sahool.agent.execution.started"
        assert SAHOOL_AGENT_ALL == "sahool.agent.>"

    def test_calibration_subjects(self):
        assert SAHOOL_CALIBRATION_RUN_QUEUED == "sahool.calibration.run.queued.v1"
        assert SAHOOL_CALIBRATION_ALL == "sahool.calibration.>"

    def test_all_subjects_start_with_sahool_prefix(self):
        """All subject constants should start with 'sahool.'."""
        import shared.events.subjects as mod

        for name in dir(mod):
            if name.startswith("SAHOOL_") and isinstance(getattr(mod, name), str):
                value = getattr(mod, name)
                assert value.startswith("sahool."), (
                    f"{name}={value!r} does not start with 'sahool.'"
                )


# ═══════════════════════════════════════════════════════════════════════════════
# get_tenant_subject()
# ═══════════════════════════════════════════════════════════════════════════════


class TestGetTenantSubject:
    """Test tenant-scoped subject generation."""

    def test_basic_tenant_subject(self):
        result = get_tenant_subject(VALID_UUID, "field", "created")
        assert result == f"sahool.tenant.{VALID_UUID}.field.created"

    def test_different_domains(self):
        assert get_tenant_subject(VALID_UUID, "weather", "alert") == (
            f"sahool.tenant.{VALID_UUID}.weather.alert"
        )
        assert get_tenant_subject(VALID_UUID, "billing", "payment.completed") == (
            f"sahool.tenant.{VALID_UUID}.billing.payment.completed"
        )

    def test_empty_tenant_id_raises(self):
        with pytest.raises(ValueError, match="tenant_id is required"):
            get_tenant_subject("", "field", "created")

    def test_none_tenant_id_raises(self):
        with pytest.raises((ValueError, TypeError)):
            get_tenant_subject(None, "field", "created")

    def test_invalid_uuid_format_raises(self):
        with pytest.raises(ValueError, match="valid UUID"):
            get_tenant_subject("not-a-uuid", "field", "created")

    def test_wildcard_in_tenant_id_raises(self):
        """Prevent NATS subject injection via wildcard characters."""
        with pytest.raises(ValueError):
            get_tenant_subject("a1b2c3d4-e5f6-7890-abcd-ef1234567890*", "field", "created")

    def test_uppercase_uuid_accepted(self):
        upper_uuid = VALID_UUID.upper()
        result = get_tenant_subject(upper_uuid, "field", "created")
        assert result == f"sahool.tenant.{upper_uuid}.field.created"


# ═══════════════════════════════════════════════════════════════════════════════
# get_tenant_wildcard()
# ═══════════════════════════════════════════════════════════════════════════════


class TestGetTenantWildcard:
    """Test tenant wildcard subject generation."""

    def test_all_domains_wildcard(self):
        result = get_tenant_wildcard(VALID_UUID)
        assert result == f"sahool.tenant.{VALID_UUID}.>"

    def test_specific_domain_wildcard(self):
        result = get_tenant_wildcard(VALID_UUID, "field")
        assert result == f"sahool.tenant.{VALID_UUID}.field.>"

    def test_empty_tenant_id_raises(self):
        with pytest.raises(ValueError, match="tenant_id is required"):
            get_tenant_wildcard("")


# ═══════════════════════════════════════════════════════════════════════════════
# get_all_tenants_subject()
# ═══════════════════════════════════════════════════════════════════════════════


class TestGetAllTenantsSubject:
    """Test cross-tenant subject pattern."""

    def test_basic_cross_tenant(self):
        result = get_all_tenants_subject("billing", "payment.completed")
        assert result == "sahool.tenant.*.billing.payment.completed"

    def test_field_domain(self):
        result = get_all_tenants_subject("field", "created")
        assert result == "sahool.tenant.*.field.created"


# ═══════════════════════════════════════════════════════════════════════════════
# TenantSubjectBuilder
# ═══════════════════════════════════════════════════════════════════════════════


class TestTenantSubjectBuilder:
    """Test the builder pattern for tenant subjects."""

    def test_builder_subject(self):
        builder = TenantSubjectBuilder(VALID_UUID)
        result = builder.subject("field", "created")
        assert result == f"sahool.tenant.{VALID_UUID}.field.created"

    def test_builder_wildcard(self):
        builder = TenantSubjectBuilder(VALID_UUID)
        result = builder.wildcard("weather")
        assert result == f"sahool.tenant.{VALID_UUID}.weather.>"

    def test_builder_field_domain(self):
        builder = TenantSubjectBuilder(VALID_UUID)
        assert builder.field.created() == f"sahool.tenant.{VALID_UUID}.field.created"
        assert builder.field.updated() == f"sahool.tenant.{VALID_UUID}.field.updated"
        assert builder.field.deleted() == f"sahool.tenant.{VALID_UUID}.field.deleted"
        assert builder.field.all() == f"sahool.tenant.{VALID_UUID}.field.>"

    def test_builder_weather_domain(self):
        builder = TenantSubjectBuilder(VALID_UUID)
        assert builder.weather.created() == f"sahool.tenant.{VALID_UUID}.weather.created"

    def test_builder_billing_domain(self):
        builder = TenantSubjectBuilder(VALID_UUID)
        assert builder.billing.action("payment.completed") == (
            f"sahool.tenant.{VALID_UUID}.billing.payment.completed"
        )

    def test_builder_iot_domain(self):
        builder = TenantSubjectBuilder(VALID_UUID)
        assert builder.iot.created() == f"sahool.tenant.{VALID_UUID}.iot.created"

    def test_builder_notification_domain(self):
        builder = TenantSubjectBuilder(VALID_UUID)
        assert builder.notification.all() == f"sahool.tenant.{VALID_UUID}.notification.>"

    def test_builder_empty_tenant_id_raises(self):
        with pytest.raises(ValueError, match="tenant_id is required"):
            TenantSubjectBuilder("")


# ═══════════════════════════════════════════════════════════════════════════════
# DomainSubjectBuilder
# ═══════════════════════════════════════════════════════════════════════════════


class TestDomainSubjectBuilder:
    """Test the domain-level subject builder."""

    def test_crud_actions(self):
        builder = DomainSubjectBuilder("sahool.tenant.t1", "field")
        assert builder.created() == "sahool.tenant.t1.field.created"
        assert builder.updated() == "sahool.tenant.t1.field.updated"
        assert builder.deleted() == "sahool.tenant.t1.field.deleted"

    def test_custom_action(self):
        builder = DomainSubjectBuilder("sahool.tenant.t1", "billing")
        assert builder.action("payment.completed") == "sahool.tenant.t1.billing.payment.completed"

    def test_wildcard_all(self):
        builder = DomainSubjectBuilder("sahool.tenant.t1", "weather")
        assert builder.all() == "sahool.tenant.t1.weather.>"
