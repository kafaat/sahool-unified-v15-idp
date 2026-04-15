---
description: Regenerate Dart contract files from the TypeScript source of truth
---

Regenerate the Dart contract files under `apps/mobile/lib/core/contracts/` from the TypeScript source `packages/shared-types/src/contracts/`.

## Steps

1. Verify the TypeScript source compiles cleanly first:
   ```
   npx tsc --noEmit -p packages/shared-types/tsconfig.json
   ```

2. Run the sync script:
   ```
   npx tsx scripts/sync-contracts-to-dart.ts
   ```

3. Run `git diff apps/mobile/lib/core/contracts/` and summarize the delta:
   - Added constants
   - Removed constants (flag as potentially breaking)
   - Changed values

4. If any Dart file has been modified, run the Dart analyzer on the mobile project:
   ```
   cd apps/mobile && flutter analyze lib/core/contracts/
   ```

5. Stage only the regenerated Dart files — do NOT auto-commit.

## Warnings

- If the script does not exist (`scripts/sync-contracts-to-dart.ts` missing), abort and tell the user — this means the scaffold is incomplete.
- Dart contract files are **generated** and MUST NOT be hand-edited. If a diff shows manual edits upstream, warn the user before overwriting.
- If `CONTRACT_VERSION` has not been bumped but constants have changed, remind the user to bump it (patch for additive, minor for structural, major for breaking).
