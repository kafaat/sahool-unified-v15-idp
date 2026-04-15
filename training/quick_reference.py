"""
SAHOOL Quick Reference — Print and keep handy!

┌─────────────────────────────────────────────────────────────────────────────┐
│                    SAHOOL PLATFORM — QUICK REFERENCE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  IMPORT EVERYTHING:                                                         │
│  from shared.platform import *                                              │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  CONTEXT ACCESS                                                             │
│  ─────────────────                                                          │
│  get_current_context()     → Full RequestContext                            │
│  get_current_tenant_id()   → Tenant ID string                               │
│  has_context()             → Boolean check                                  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  DATABASE                                                                   │
│  ─────────                                                                  │
│  async with tenant_db() as conn:                                            │
│      rows = await conn.fetch("SELECT * FROM fields")                        │
│                                                                             │
│  class MyRepo(TenantRepository):                                            │
│      _table = 'my_table'                                                    │
│      _model_class = MyModel                                                 │
│                                                                             │
│  repo = MyRepo()                                                            │
│  item = await repo.create({'name': 'X'})  # tenant_id auto                 │
│  items = await repo.find_many()            # RLS filtered                   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  REDIS                                                                      │
│  ─────                                                                      │
│  redis = TenantRedis(client, 'my-service')                                  │
│  await redis.set('session', '123', data, ttl=3600)                          │
│  data = await redis.get('session', '123')                                   │
│                                                                             │
│  cache = TenantCache(redis)                                                 │
│  data = await cache.get_or_set('key', factory, ttl=300)                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  STORAGE                                                                    │
│  ───────                                                                    │
│  storage = TenantStorage(endpoint, key, secret)                             │
│  result = await storage.upload('path/file.jpg', data)                       │
│  url = await storage.get_url('path/file.jpg', expires=3600)                 │
│  data = await storage.download('path/file.jpg')                             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  EVENTS                                                                     │
│  ──────                                                                     │
│  publisher = TenantNATSPublisher(nc, 'my-service')                          │
│  await publisher.publish('event.type', {'id': '123'})                       │
│                                                                             │
│  subject = SubjectBuilder.build('domain', 'resource', 'action')             │
│  # → sahool.domain.t_123abc.resource.action                                │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  DECORATORS                                                                 │
│  ──────────                                                                 │
│  @require_context()                    # Any authenticated user             │
│  @require_context(allowed_roles=[ADMIN])  # Admin only                      │
│  @require_quota('api_calls', 1)        # Rate limit                         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  SYSTEM OPERATIONS                                                          │
│  ────────────────                                                           │
│  ctx = create_system_context('background-job')                              │
│  with ContextManager(ctx):                                                  │
│      # Run background task                                                  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  CLI COMMANDS                                                               │
│  ────────────                                                               │
│  sahool-cli deploy --service X --version Y --environment prod               │
│  sahool-cli load-test --environment prod --tenants 50                       │
│  sahool-cli analyze-performance --environment prod                          │
│  sahool-cli rollback --service X --to-version Y                             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  EMERGENCY                                                                  │
│  ─────────                                                                  │
│  # Enable read-only mode                                                    │
│  kubectl apply -f k8s/emergency/read-only-mode.yaml                         │
│                                                                             │
│  # Rollback immediately                                                     │
│  sahool-cli rollback --service X --to-version PREVIOUS                      │
│                                                                             │
│  # Verify isolation                                                         │
│  python scripts/verify-isolation.py --environment production                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
"""

if __name__ == "__main__":
    print(__doc__)
