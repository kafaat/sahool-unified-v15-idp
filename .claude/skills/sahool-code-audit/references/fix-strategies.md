# Fix Strategies Reference

The SAHOOL `FixOps` engine (see `shared/ai/auto_fix/engine.py`) supports 4 strategies. Pick one per audit pass. SAFE is the default — do not escalate without explicit user approval.

## Decision Tree

```
Is the finding a security issue (CRITICAL)?
├─ Yes → Manual Edit with user approval, never auto-apply
└─ No → Is the finding auto-fixable by the tool (ruff/eslint reports autofix=true)?
        ├─ Yes → Is there risk of semantic change?
        │       ├─ No → SAFE
        │       └─ Yes (renames, complex refactors) → Need user approval → COMPREHENSIVE
        └─ No → Manual Edit per audit recommendation
```

## Strategies

### MINIMAL

**What it does**: Fixes only errors that block CI (`ruff check --select E` level, mypy errors, failing tests). Leaves warnings and style alone.

**When to use**: Hot-patching prod, time-critical merge, `main` branch hardening.

**SAHOOL invocation**:
```bash
make fixops FIX_STRATEGY=MINIMAL
# or
python -m shared.ai.auto_fix --strategy MINIMAL --paths <paths>
```

### SAFE (default)

**What it does**: Applies all tool-reported auto-fixes that do not change runtime semantics. Includes:
- Unused imports removed
- Formatting normalized (ruff format, prettier)
- Import order fixed
- Trailing whitespace cleaned
- Simple lint rules (F401, E501, I001)

**Does NOT do**:
- Rename symbols
- Extract functions
- Change type annotations
- Modify control flow

**When to use**: Pre-merge cleanup, PR review autofix, routine maintenance.

**SAHOOL invocation**:
```bash
/fixops-run              # slash command
make fixops-run          # Make target
```

### COMPREHENSIVE

**What it does**: SAFE + semantic improvements that are tool-suggested:
- Pydantic v1 → v2 migration (`class Config` → `model_config`)
- `@app.on_event` → `lifespan`
- `print()` → `logger.info(...)` with keyword args
- Typing upgrades (`Dict` → `dict`, Python 3.11+ syntax)
- Dead code removal (behind feature flags not set)

**Does NOT do**:
- Architectural refactors
- Database migrations
- API breaking changes

**When to use**: Dev branch, dedicated cleanup sprint, `make fixops-comprehensive`. Always review diff before committing.

**SAHOOL invocation**:
```bash
make fixops-comprehensive
# Review diff, then:
git add -p
```

### REFACTOR

**What it does**: COMPREHENSIVE + structural changes:
- Extract method / extract class
- Split long files
- Rename for clarity (cross-file)
- Consolidate duplicate code
- Introduce abstractions when justified by >3 call sites

**Preconditions**:
- Tests exist for the target module (coverage > 30%)
- Explicit user approval per affected file
- Dedicated refactor branch

**When to use**: Planned refactor task, tech debt sprint.

**SAHOOL invocation**:
```bash
# No automated mode — always interactive
python -m shared.ai.auto_fix --strategy REFACTOR --interactive --paths <paths>
```

## Multi-file and multi-service fixes

When findings span 3+ services or 20+ files:

1. Run SAFE per-service first (parallel)
2. Run COMPREHENSIVE per-service (one at a time, verify each)
3. Refactor: **never** cross-service in one pass

## Verification after fix

Every strategy must be followed by:

```bash
# Python service
make test-unit SERVICE=<name>

# Node.js service
npm run test -w <package>

# Full Python CI
make ci

# Flutter
flutter test
```

If tests fail post-fix, revert with `git restore` (or `git reset --hard HEAD` if uncommitted) and escalate to user. Never leave the repo in a broken state.

## Audit log

Every FixOps run writes an audit entry to `shared/audit_trail/`. The entry records:
- Strategy used
- Files modified
- Findings resolved (by severity)
- Test results
- Commit SHA (if applied in git)

Retain for compliance (tenant-scoped, see `shared/audit_trail/README.md`).
