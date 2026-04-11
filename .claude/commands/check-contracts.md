---
description: Validate SAHOOL API contracts (ports, error codes, endpoints) for drift and breaking changes
---

Validate the unified API contracts defined in `packages/shared-types/src/contracts/` against the rest of the monorepo.

## What to check

### 1. Source files
Read these contract files:
- `packages/shared-types/src/contracts/index.ts` — `CONTRACT_VERSION`
- `packages/shared-types/src/contracts/service-ports.ts` — `SERVICE_PORTS`, `SERVICE_PORT_ALIASES`
- `packages/shared-types/src/contracts/error-codes.ts` — `ERROR_CODES`, `ERROR_MESSAGES`
- `packages/shared-types/src/contracts/api-endpoints.ts` — `*_ENDPOINTS`, `buildUrl()`
- `packages/shared-types/src/contracts/api-responses.ts` — response shapes

### 2. Drift detection

Use Grep to find any **hardcoded** references that should be importing from contracts:

- Hardcoded ports (e.g. `localhost:3025`, `:8150`) in `apps/services/`, `apps/web/`, `apps/admin/`
- Local `const AUTH_PORT = 3025` style constants — flag as violations of the ESLint `no-restricted-imports` rule
- Error code strings (e.g. `"E1001"`, `"E2003"`) defined outside `error-codes.ts`
- Endpoint path literals (e.g. `"/api/v1/auth/login"`) that are not using `AUTH_ENDPOINTS.LOGIN`

### 3. Dart synchronization

Compare `packages/shared-types/src/contracts/` (TypeScript source) with `apps/mobile/lib/core/contracts/` (generated Dart). If any constants differ, remind the user to run:

```
npx tsx scripts/sync-contracts-to-dart.ts
```

### 4. Deprecation policy

For any constant marked `@deprecated`:
- Verify the deprecation JSDoc includes both the replacement and the removal version
- Verify the deprecated constant is present in the corresponding alias map (`SERVICE_PORT_ALIASES`, etc.)
- Flag any deprecated constant whose sunset version is `<=` the current `CONTRACT_VERSION` — it is overdue for removal

### 5. CI guard parity

The `api-contracts-guard.yml` workflow flags removed exports as breaking changes. Run the same check locally:
- Compare current git branch against `main` to find removed exports
- Any removed export without a 2-minor-version deprecation window is a breaking change

## Output

Report under these headings:

```
## CONTRACT_VERSION
(current version + whether it needs a bump)

## Port drift
(hardcoded ports found outside contracts)

## Error-code drift
(hardcoded error strings found outside contracts)

## Endpoint drift
(hardcoded endpoint paths found outside contracts)

## Dart sync status
(in-sync | out-of-sync — with the delta)

## Deprecation status
(overdue / upcoming deprecations)

## Breaking changes
(removed exports, if any)

## Recommended version bump
(patch | minor | major, with reasoning)
```

**Do not modify** any files — this is a read-only audit command.
