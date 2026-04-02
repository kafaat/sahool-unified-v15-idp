"""
SAHOOL Platform Training — Module 1: Introduction

Welcome to SAHOOL Platform Training!

This interactive module teaches the fundamentals of building
tenant-aware services on the SAHOOL platform.

PREREQUISITES:
- Python 3.11+
- Docker & Docker Compose
- Basic knowledge of FastAPI/PostgreSQL

LEARNING OBJECTIVES:
By the end of this module, you will:
1. Understand multi-tenant architecture
2. Use the SAHOOL SDK correctly
3. Avoid common anti-patterns
4. Deploy your first service
"""

# ═══════════════════════════════════════════════════════════════════════════════
# LESSON 1: What is Multi-Tenant Architecture?
# ═══════════════════════════════════════════════════════════════════════════════

# In a multi-tenant SaaS platform:
# - Multiple customers (tenants) share the same infrastructure
# - Each tenant's data must be completely isolated
# - Tenants cannot see or access each other's data
#
# SAHOOL uses "tenant isolation at the database level" via PostgreSQL RLS.

# EXERCISE 1.1: Understanding Tenant Context
#
# from shared.platform import RequestContext, UserRole
#
# context = RequestContext(
#     tenant_id="tenant-abc123xyz",
#     user_id="user-789",
#     role=UserRole.USER,
#     service_name="training-service"
# )
#
# print(f"Tenant ID: {context.tenant_id}")
# print(f"User ID: {context.user_id}")
# print(f"Role: {context.role}")


# ═══════════════════════════════════════════════════════════════════════════════
# LESSON 2: The Golden Rule — Never Handle tenant_id Manually
# ═══════════════════════════════════════════════════════════════════════════════

# ❌ ANTI-PATTERN (NEVER DO THIS):
#
# async def wrong_way(conn, tenant_id):
#     # Problem 1: Manual parameter
#     # Problem 2: Manual WHERE clause
#     # Problem 3: Risk of forgetting tenant filter
#     rows = await conn.fetch(
#         "SELECT * FROM fields WHERE tenant_id = $1",
#         tenant_id
#     )
#     return rows

# ✅ CORRECT WAY (ALWAYS DO THIS):
#
# from shared.platform import tenant_db
#
# async def correct_way():
#     # Context automatically set by middleware
#     async with tenant_db() as conn:
#         # RLS automatically filters by tenant
#         rows = await conn.fetch("SELECT * FROM fields")
#         return rows


# ═══════════════════════════════════════════════════════════════════════════════
# LESSON 3: Building Your First Service
# ═══════════════════════════════════════════════════════════════════════════════

# Step 1: Add middleware (MUST be first!)
#
# from fastapi import FastAPI
# from shared.platform import ContextMiddleware
#
# app = FastAPI()
# app.add_middleware(ContextMiddleware, service_name='my-first-service')

# Step 2: Define your data model
#
# from pydantic import BaseModel
#
# class FieldCreate(BaseModel):
#     name: str
#     area: float

# Step 3: Define repository
#
# from shared.platform import TenantRepository
#
# class FieldRepository(TenantRepository):
#     _table = 'fields'
#     _model_class = FieldModel

# Step 4: Create endpoints
#
# @app.post("/fields")
# async def create_field(data: FieldCreate):
#     """Create a field — tenant_id automatically injected!"""
#     repo = FieldRepository()
#     field = await repo.create({
#         'name': data.name,
#         'area': data.area
#         # tenant_id added automatically by repository
#     })
#     return field
#
# @app.get("/fields")
# async def list_fields():
#     """List fields — only current tenant's fields returned!"""
#     repo = FieldRepository()
#     return await repo.find_many()


# ═══════════════════════════════════════════════════════════════════════════════
# LESSON 4: Testing Tenant Isolation
# ═══════════════════════════════════════════════════════════════════════════════

# async def test_tenant_isolation():
#     """Verify that tenant isolation is working correctly."""
#     from shared.platform import ContextManager, RequestContext, UserRole
#
#     tenant_a = RequestContext(
#         tenant_id="tenant-a-123456",
#         user_id="user-a",
#         role=UserRole.USER,
#         service_name='test'
#     )
#
#     tenant_b = RequestContext(
#         tenant_id="tenant-b-789012",
#         user_id="user-b",
#         role=UserRole.USER,
#         service_name='test'
#     )
#
#     # Create data as tenant A
#     with ContextManager(tenant_a):
#         field_a = await FieldRepository().create({'name': 'Field A', 'area': 100})
#         print(f"Tenant A created: {field_a.id}")
#
#     # Create data as tenant B
#     with ContextManager(tenant_b):
#         field_b = await FieldRepository().create({'name': 'Field B', 'area': 200})
#         print(f"Tenant B created: {field_b.id}")
#
#     # Verify isolation: Tenant A should only see Field A
#     with ContextManager(tenant_a):
#         fields = await FieldRepository().find_many()
#         assert len(fields) == 1
#         assert fields[0].name == 'Field A'
#         print("✅ Tenant isolation verified: A sees only A's data")
#
#     # Verify isolation: Tenant B should only see Field B
#     with ContextManager(tenant_b):
#         fields = await FieldRepository().find_many()
#         assert len(fields) == 1
#         assert fields[0].name == 'Field B'
#         print("✅ Tenant isolation verified: B sees only B's data")
#
#     print("\n🎉 All tests passed! Tenant isolation is working correctly.")


# ═══════════════════════════════════════════════════════════════════════════════
# LESSON 5: Common Mistakes & How to Avoid Them
# ═══════════════════════════════════════════════════════════════════════════════

# MISTAKE 1: Using raw database connections
# ❌  conn = await asyncpg.connect(DATABASE_URL)  # Bypasses all isolation!
# ✅  async with tenant_db() as conn: ...          # Isolation enforced

# MISTAKE 2: Passing tenant_id in API parameters
# ❌  @app.get("/fields/{tenant_id}")  # Never accept tenant_id from client!
# ✅  @app.get("/fields")              # Tenant from JWT/context

# MISTAKE 3: Caching without tenant prefix
# ❌  await redis.set("user:123", data)                     # Shared across tenants!
# ✅  await tenant_redis.set('user', '123', data)           # Prefixed per tenant

# MISTAKE 4: Publishing events without context
# ❌  await nats.publish("field.updated", data)              # No tenant info!
# ✅  await publisher.publish("field.updated", data)         # Headers auto-injected


# ═══════════════════════════════════════════════════════════════════════════════
# EXERCISES
# ═══════════════════════════════════════════════════════════════════════════════

# EXERCISE 1: Create a complete service
#   Build a service with:
#   - 3 endpoints (GET list, POST create, GET single)
#   - TenantRepository for database access
#   - TenantCache for caching
#   - TenantNATSPublisher for events
#   Test with 2 different tenants and verify isolation.

# EXERCISE 2: Find the bug
#   The following code has a tenant isolation bug. Find and fix it:
#
#   @app.get("/admin/all-fields")
#   async def get_all_fields():
#       async with tenant_db() as conn:
#           rows = await conn.fetch("SELECT * FROM fields")
#           return rows
#
#   Answer: Use require_context(allowed_roles=[UserRole.SUPER_ADMIN])

# EXERCISE 3: Load test your service
#   Use the load tester to verify your service handles 1000 requests/minute
#   without breaking tenant isolation.

if __name__ == "__main__":
    print("SAHOOL Platform Training — Module 1: Introduction")
    print("=" * 50)
    print()
    print("This module contains commented examples to study.")
    print("Uncomment and run sections as you progress through the lessons.")
    print()
    print("Lessons:")
    print("  1. What is Multi-Tenant Architecture?")
    print("  2. The Golden Rule — Never Handle tenant_id Manually")
    print("  3. Building Your First Service")
    print("  4. Testing Tenant Isolation")
    print("  5. Common Mistakes & How to Avoid Them")
    print()
    print("Next: training/quick_reference.py")
