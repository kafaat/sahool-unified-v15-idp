/**
 * Minimal stub for @nestjs/cache-manager.
 *
 * keyv (a transitive dependency of @nestjs/cache-manager v3+) is not
 * installed in the dev environment, so the real module cannot be resolved
 * during Jest test runs.  The integration tests mock CacheService entirely;
 * this stub just makes `import { CACHE_MANAGER } from '@nestjs/cache-manager'`
 * succeed at module-resolution time without triggering any network or disk I/O.
 */

class CacheManagerStubModule {}

module.exports = {
  // CacheModule stub so NestJS module metadata resolves
  CacheModule: CacheManagerStubModule,
  // Token used by CacheService via @Inject(CACHE_MANAGER)
  CACHE_MANAGER: "CACHE_MANAGER",
  // Re-export anything else the real module exports that may be referenced
  Cache: class {},
  Store: class {},
};
