---
description: Run SAHOOL FixOps auto-fix engine with safe strategy and audit log
argument-hint: [dry-run|safe|comprehensive]
---

Run the SAHOOL FixOps auto-fix engine (from `shared/ai/auto_fix/`) to diagnose and repair code issues.

## Arguments
- `$1` — strategy: `dry-run` (preview only), `safe` (default), `comprehensive` (all fixes).

## Steps

### 1. Preflight
- Confirm git working tree is clean OR all uncommitted changes are related to the current task.
  Reason: FixOps may touch many files; a dirty tree makes review hard.
- Confirm we are NOT on `main` / `master` — refuse to run FixOps directly on protected branches.

### 2. Diagnose first
Run with the appropriate Makefile target:
```
# Preview only - always run this first
make fixops            # dry-run
```

Report the diagnostic summary:
- Total diagnostics
- Auto-fixable count
- Breakdown by category: STYLE, SECURITY, PERFORMANCE, TYPE, BUG
- Breakdown by severity: ERROR, WARNING, INFO, HINT
- Breakdown by tool: ruff, eslint, mypy, bandit, dart analyze

### 3. Apply fixes (if user approves)
Based on `$1`:
- `dry-run` → stop after diagnose, show proposed fixes without applying
- `safe` → `make fixops-run` (FixStrategy.SAFE)
- `comprehensive` → `make fixops-comprehensive` (FixStrategy.COMPREHENSIVE) — **requires explicit user confirmation**

### 4. Post-fix validation
After fixes are applied, run in parallel:
- `ruff check apps/ shared/` — verify no new Python issues
- `npm run lint` — verify no new JS/TS issues
- `make test-unit` — fast unit tests must still pass

If anything regresses, **do not commit** — revert the FixOps changes with `git restore .` and report the failing files to the user.

### 5. Audit trail
The audit entries are written automatically via `shared/ai/auto_fix/engine.py`. Report the audit entry IDs so the user can look them up later.

## Safety rules

- **Never** run FixOps on `archive/deprecated-services/` — those services are frozen.
- **Never** run FixOps on `idp/templates/` — those are templates, not production code.
- **Never** run FixOps on `legacy/` — preserved for compatibility.
- **Never** auto-commit FixOps results — always leave them staged for human review.
