from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

SERVICE_NAME = "billing-core"
app = FastAPI(title=SERVICE_NAME, version="0.1.0")

class Plan(BaseModel):
    plan_id: str
    name: str
    limits: Dict[str, int]  # e.g. {"ndvi_jobs_per_day": 100, "fields": 500}

class Tenant(BaseModel):
    tenant_id: str
    name: str
    plan_id: str

# In-memory store for dev; replace with Postgres in prod
PLANS: Dict[str, Plan] = {}
TENANTS: Dict[str, Tenant] = {}
USAGE: Dict[str, Dict[str, int]] = {}  # tenant -> metric -> count

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": SERVICE_NAME}

@app.post("/plans")
def create_plan(plan: Plan):
    PLANS[plan.plan_id] = plan
    return plan

@app.post("/tenants")
def create_tenant(tenant: Tenant):
    if tenant.plan_id not in PLANS:
        raise HTTPException(400, "unknown plan_id")
    TENANTS[tenant.tenant_id] = tenant
    USAGE.setdefault(tenant.tenant_id, {})
    return tenant

@app.get("/tenants/{tenant_id}/quota")
def get_quota(tenant_id: str):
    t = TENANTS.get(tenant_id)
    if not t:
        raise HTTPException(404, "tenant not found")
    plan = PLANS[t.plan_id]
    usage = USAGE.get(tenant_id, {})
    return {"tenant_id": tenant_id, "plan": plan, "usage": usage}

class UsageSignal(BaseModel):
    metric: str
    value: int = 1

@app.post("/tenants/{tenant_id}/usage")
def add_usage(tenant_id: str, signal: UsageSignal):
    if tenant_id not in TENANTS:
        raise HTTPException(404, "tenant not found")
    USAGE.setdefault(tenant_id, {})
    USAGE[tenant_id][signal.metric] = USAGE[tenant_id].get(signal.metric, 0) + signal.value
    return {"ok": True, "tenant_id": tenant_id, "usage": USAGE[tenant_id]}

@app.get("/enforce")
def enforce(x_tenant_id: Optional[str] = Header(default=None)):
    # gateway can call this endpoint to check entitlements
    if not x_tenant_id:
        raise HTTPException(400, "missing x-tenant-id")
    t = TENANTS.get(x_tenant_id)
    if not t:
        raise HTTPException(404, "tenant not found")
    plan = PLANS[t.plan_id]
    usage = USAGE.get(x_tenant_id, {})
    return {"tenant_id": x_tenant_id, "limits": plan.limits, "usage": usage}
