"""
SAHOOL Tenant Service
Business logic for tenant management
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .models import Tenant, TenantPlan, TenantSettings, TenantStatus


class TenantService:
    """Service for tenant operations"""

    def __init__(self):
        # In-memory store for now (replace with repository)
        self._tenants: dict[str, Tenant] = {}

    def create_tenant(
        self,
        name: str,
        name_ar: Optional[str] = None,
        plan: TenantPlan = TenantPlan.FREE,
        owner_id: Optional[str] = None,
    ) -> Tenant:
        """Create a new tenant"""
        tenant = Tenant.create(
            name=name,
            name_ar=name_ar,
            plan=plan,
            owner_id=owner_id,
        )
        self._tenants[tenant.id] = tenant
        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self._tenants.get(tenant_id)

    def update_tenant_status(
        self,
        tenant_id: str,
        status: TenantStatus,
    ) -> Optional[Tenant]:
        """Update tenant status"""
        tenant = self._tenants.get(tenant_id)
        if tenant:
            tenant.status = status
            tenant.updated_at = datetime.now(timezone.utc)
        return tenant

    def update_tenant_plan(
        self,
        tenant_id: str,
        plan: TenantPlan,
    ) -> Optional[Tenant]:
        """Upgrade or downgrade tenant plan"""
        tenant = self._tenants.get(tenant_id)
        if tenant:
            tenant.plan = plan
            # Update settings based on plan
            tenant.settings = self._get_plan_settings(plan)
            tenant.updated_at = datetime.now(timezone.utc)
        return tenant

    def _get_plan_settings(self, plan: TenantPlan) -> TenantSettings:
        """Get default settings for a plan"""
        settings_map = {
            TenantPlan.FREE: TenantSettings(
                max_users=5,
                max_fields=10,
                max_storage_gb=1,
            ),
            TenantPlan.BASIC: TenantSettings(
                max_users=20,
                max_fields=50,
                max_storage_gb=10,
            ),
            TenantPlan.PRO: TenantSettings(
                max_users=100,
                max_fields=200,
                max_storage_gb=50,
            ),
            TenantPlan.ENTERPRISE: TenantSettings(
                max_users=1000,
                max_fields=1000,
                max_storage_gb=500,
            ),
        }
        return settings_map.get(plan, TenantSettings())

    def list_tenants(
        self,
        status: Optional[TenantStatus] = None,
    ) -> list[Tenant]:
        """List all tenants, optionally filtered by status"""
        tenants = list(self._tenants.values())
        if status:
            tenants = [t for t in tenants if t.status == status]
        return tenants
