"""
Tests for shared/domain/tenancy/service.py
اختبارات خدمة المستأجرين

Tests cover:
- Tenant creation with various plans
- Tenant retrieval
- Status updates
- Plan upgrades/downgrades and associated settings
- Tenant listing with status filtering
- Plan settings defaults
"""

import pytest
from datetime import UTC, datetime

from shared.domain.tenancy.service import TenantService
from shared.domain.tenancy.models import Tenant, TenantPlan, TenantSettings, TenantStatus


class TestTenantServiceCreation:
    """Tests for tenant creation.
    اختبارات إنشاء المستأجرين"""

    def test_create_tenant_defaults(self):
        """Test creating a tenant with default plan (FREE)."""
        svc = TenantService()
        tenant = svc.create_tenant(name="Test Farm")
        assert tenant.name == "Test Farm"
        assert tenant.name_ar is None
        assert tenant.plan == TenantPlan.FREE
        assert tenant.status == TenantStatus.TRIAL  # FREE plan -> TRIAL status
        assert tenant.owner_id is None
        assert tenant.id is not None

    def test_create_tenant_with_all_fields(self):
        """Test creating a tenant with all fields specified."""
        svc = TenantService()
        tenant = svc.create_tenant(
            name="Al-Rashid Farm",
            name_ar="مزرعة الراشد",
            plan=TenantPlan.PRO,
            owner_id="owner-123",
        )
        assert tenant.name == "Al-Rashid Farm"
        assert tenant.name_ar == "مزرعة الراشد"
        assert tenant.plan == TenantPlan.PRO
        assert tenant.status == TenantStatus.ACTIVE  # Non-FREE -> ACTIVE
        assert tenant.owner_id == "owner-123"

    def test_create_tenant_stored(self):
        """Test that created tenant is stored and retrievable."""
        svc = TenantService()
        tenant = svc.create_tenant(name="Stored Farm")
        assert svc.get_tenant(tenant.id) is tenant

    def test_create_multiple_tenants_unique_ids(self):
        """Test that each tenant gets a unique ID."""
        svc = TenantService()
        t1 = svc.create_tenant(name="Farm 1")
        t2 = svc.create_tenant(name="Farm 2")
        assert t1.id != t2.id


class TestTenantServiceRetrieval:
    """Tests for tenant retrieval.
    اختبارات استرجاع المستأجرين"""

    def test_get_tenant_found(self):
        """Test retrieving an existing tenant."""
        svc = TenantService()
        tenant = svc.create_tenant(name="Find Me")
        result = svc.get_tenant(tenant.id)
        assert result is tenant
        assert result.name == "Find Me"

    def test_get_tenant_not_found(self):
        """Test retrieving a non-existent tenant returns None."""
        svc = TenantService()
        assert svc.get_tenant("nonexistent-id") is None


class TestTenantServiceStatusUpdate:
    """Tests for tenant status updates.
    اختبارات تحديث حالة المستأجر"""

    def test_update_status(self):
        """Test updating tenant status."""
        svc = TenantService()
        tenant = svc.create_tenant(name="Farm", plan=TenantPlan.BASIC)
        assert tenant.status == TenantStatus.ACTIVE

        result = svc.update_tenant_status(tenant.id, TenantStatus.SUSPENDED)
        assert result is not None
        assert result.status == TenantStatus.SUSPENDED

    def test_update_status_updates_timestamp(self):
        """Test that status update modifies updated_at."""
        svc = TenantService()
        tenant = svc.create_tenant(name="Farm")
        original_updated = tenant.updated_at

        result = svc.update_tenant_status(tenant.id, TenantStatus.EXPIRED)
        assert result.updated_at >= original_updated

    def test_update_status_nonexistent(self):
        """Test updating status for non-existent tenant returns None."""
        svc = TenantService()
        assert svc.update_tenant_status("fake-id", TenantStatus.ACTIVE) is None


class TestTenantServicePlanUpdate:
    """Tests for tenant plan upgrades and downgrades.
    اختبارات ترقية وتخفيض خطة المستأجر"""

    def test_upgrade_plan(self):
        """Test upgrading a tenant plan."""
        svc = TenantService()
        tenant = svc.create_tenant(name="Farm", plan=TenantPlan.FREE)
        result = svc.update_tenant_plan(tenant.id, TenantPlan.PRO)
        assert result is not None
        assert result.plan == TenantPlan.PRO

    def test_plan_update_changes_settings(self):
        """Test that plan update changes settings accordingly."""
        svc = TenantService()
        tenant = svc.create_tenant(name="Farm", plan=TenantPlan.FREE)
        result = svc.update_tenant_plan(tenant.id, TenantPlan.ENTERPRISE)
        assert result.settings.max_users == 1000
        assert result.settings.max_fields == 1000
        assert result.settings.max_storage_gb == 500

    def test_plan_settings_free(self):
        """Test FREE plan settings."""
        svc = TenantService()
        settings = svc._get_plan_settings(TenantPlan.FREE)
        assert settings.max_users == 5
        assert settings.max_fields == 10
        assert settings.max_storage_gb == 1

    def test_plan_settings_basic(self):
        """Test BASIC plan settings."""
        svc = TenantService()
        settings = svc._get_plan_settings(TenantPlan.BASIC)
        assert settings.max_users == 20
        assert settings.max_fields == 50
        assert settings.max_storage_gb == 10

    def test_plan_settings_pro(self):
        """Test PRO plan settings."""
        svc = TenantService()
        settings = svc._get_plan_settings(TenantPlan.PRO)
        assert settings.max_users == 100
        assert settings.max_fields == 200
        assert settings.max_storage_gb == 50

    def test_plan_settings_enterprise(self):
        """Test ENTERPRISE plan settings."""
        svc = TenantService()
        settings = svc._get_plan_settings(TenantPlan.ENTERPRISE)
        assert settings.max_users == 1000
        assert settings.max_fields == 1000
        assert settings.max_storage_gb == 500

    def test_update_plan_nonexistent(self):
        """Test updating plan for non-existent tenant returns None."""
        svc = TenantService()
        assert svc.update_tenant_plan("fake-id", TenantPlan.PRO) is None

    def test_downgrade_plan(self):
        """Test downgrading a tenant plan."""
        svc = TenantService()
        tenant = svc.create_tenant(name="Farm", plan=TenantPlan.ENTERPRISE)
        result = svc.update_tenant_plan(tenant.id, TenantPlan.BASIC)
        assert result.plan == TenantPlan.BASIC
        assert result.settings.max_users == 20


class TestTenantServiceListing:
    """Tests for tenant listing.
    اختبارات سرد المستأجرين"""

    def test_list_all_tenants(self):
        """Test listing all tenants without filter."""
        svc = TenantService()
        svc.create_tenant(name="Farm 1", plan=TenantPlan.FREE)
        svc.create_tenant(name="Farm 2", plan=TenantPlan.PRO)
        tenants = svc.list_tenants()
        assert len(tenants) == 2

    def test_list_tenants_by_status(self):
        """Test listing tenants filtered by status."""
        svc = TenantService()
        t1 = svc.create_tenant(name="Trial Farm", plan=TenantPlan.FREE)  # TRIAL status
        t2 = svc.create_tenant(name="Active Farm", plan=TenantPlan.PRO)  # ACTIVE status

        trial_tenants = svc.list_tenants(status=TenantStatus.TRIAL)
        assert len(trial_tenants) == 1
        assert trial_tenants[0].id == t1.id

        active_tenants = svc.list_tenants(status=TenantStatus.ACTIVE)
        assert len(active_tenants) == 1
        assert active_tenants[0].id == t2.id

    def test_list_tenants_empty(self):
        """Test listing tenants when none exist."""
        svc = TenantService()
        assert svc.list_tenants() == []

    def test_list_tenants_no_match(self):
        """Test listing tenants with status filter that matches none."""
        svc = TenantService()
        svc.create_tenant(name="Farm", plan=TenantPlan.FREE)
        assert svc.list_tenants(status=TenantStatus.EXPIRED) == []
