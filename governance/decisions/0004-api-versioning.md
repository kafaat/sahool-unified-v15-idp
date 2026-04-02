# ADR-0004: API Versioning Strategy

- **Status**: Accepted
- **Date**: 2026-04-02
- **Deciders**: Platform Architecture Team

## Context

> السياق | Context

SAHOOL exposes REST APIs from 72+ microservices through Kong API Gateway (105+ routes). As the platform evolves, APIs change and we need a consistent versioning strategy that protects consumers while allowing innovation.

Key requirements:
1. **Backward compatibility** — Existing API consumers must not break on upgrades
2. **Breaking change detection** — CI must catch removed endpoints, changed types
3. **Unified contracts** — Single source of truth for ports, error codes, endpoints
4. **Mobile sync** — Dart contracts must stay in sync with TypeScript contracts
5. **Deprecation** — Clear lifecycle for deprecated endpoints

Options considered:
- **A) URL path versioning** — `/api/v1/`, `/api/v2/` (most common)
- **B) Header versioning** — `Accept: application/vnd.sahool.v2+json`
- **C) Query parameter** — `?version=2`
- **D) No versioning** — Only additive changes allowed

## Decision

> القرار | Decision

We adopt **Option A: URL path versioning** with unified contracts:

### URL Convention

```
/api/v1/{resource}    # Current stable version
/api/v2/{resource}    # Next version (when breaking changes needed)
```

### Unified Contract System

All API contracts are centralized in `packages/shared-types/src/contracts/`:

| File | Purpose |
|------|---------|
| `index.ts` | `CONTRACT_VERSION` (SemVer), barrel export |
| `service-ports.ts` | `SERVICE_PORTS` — all service port assignments |
| `error-codes.ts` | `ERROR_CODES`, `ERROR_MESSAGES` (bilingual EN/AR) |
| `api-endpoints.ts` | `*_ENDPOINTS` constants, `buildUrl()` helper |
| `api-responses.ts` | Unified response shapes (`ApiResponse`, `PaginatedResponse`) |

### CONTRACT_VERSION Bumping

| Change | Version Bump |
|--------|-------------|
| New additive constants (port, error code, endpoint) | **Patch** |
| New contract modules or structural additions | **Minor** |
| Removed or renamed exports (breaking) | **Major** |

### Deprecation Policy

1. Add to `SERVICE_PORT_ALIASES` (or equivalent) mapping old name → new name
2. Add `@deprecated` JSDoc tag with migration target and sunset version
3. Bump `CONTRACT_VERSION` minor version
4. Update Dart codegen to include deprecation annotations
5. Allow **2 minor versions** before removing the deprecated constant

### Breaking Change Enforcement (Updated)

CI workflow `api-contracts-guard.yml` now **blocks PRs** with breaking changes unless the commit message includes `BREAKING:` prefix:
- Detects removed service ports, error codes, and endpoints
- Validates `CONTRACT_VERSION` is bumped when contract files change
- Checks TypeScript ↔ Dart contract synchronization
- Validates port uniqueness against `governance/services.yaml`

### Import Convention

```typescript
// Correct — import from unified contracts
import { SERVICE_PORTS, AUTH_ENDPOINTS, buildUrl } from "@sahool/shared-types/contracts";

// Incorrect — do not define local port/error constants
const AUTH_PORT = 3025; // ❌ Use SERVICE_PORTS.AUTH instead
```

ESLint `no-restricted-imports` enforces this convention.

### Dart (Mobile) Contracts

Generated from TypeScript via `npx tsx scripts/sync-contracts-to-dart.ts`. Located in `apps/mobile/lib/core/contracts/`. Do NOT edit Dart files manually.

## Consequences

> النتائج | Consequences

### Positive

- **Single source of truth** — All ports, errors, endpoints in one package
- **CI enforcement** — Breaking changes caught before merge
- **Mobile sync** — Dart contracts auto-generated from TypeScript
- **Discoverable** — `buildUrl()` helper makes endpoint construction type-safe

### Negative

- **Coordination overhead** — Contract changes require touching shared-types package
- **Generation step** — Dart sync adds a build step to mobile development
- **Version management** — CONTRACT_VERSION must be manually bumped

### Mitigations

- CI guard reminds developers to bump version when contracts change
- Dart sync check runs automatically on PR
- ESLint prevents local constant definitions that bypass contracts

## Related

- [API Contracts Guard](../../.github/workflows/api-contracts-guard.yml)
- [Shared Types Package](../../packages/shared-types/)
- [Kong Gateway Config](../../infrastructure/gateway/kong/)
- [Dart Contracts](../../apps/mobile/lib/core/contracts/)
