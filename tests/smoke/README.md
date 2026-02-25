# Smoke Tests

Fast import-verification tests that confirm the platform's modules load correctly and have no circular dependencies. Smoke tests are the first line of CI defense — they run in seconds and catch broken imports before heavier test suites run.

## Running

```bash
# All smoke tests
pytest tests/smoke/ -v -m smoke

# Individual files
pytest tests/smoke/test_startup.py -v
pytest tests/smoke/test_arch_imports.py -v
pytest tests/smoke/test_fixops_smoke.py -v

# As part of CI pipeline
make ci
```

## Test Files

### `test_startup.py`

Verifies that core shared modules import cleanly:

- `shared.security.jwt` and `shared.security.rbac`
- `shared.events`
- `shared.monitoring.metrics`
- Service modules (gracefully skips if service path not found)

### `test_arch_imports.py`

Checks that all domain packages import without circular dependencies:

- `kernel_domain` — verifies `__version__` attribute present
- `field_suite` — verifies `__version__` attribute present
- `advisor` — verifies `__version__` attribute present
- Legacy compatibility shims (e.g., `kernel_domain.auth`)

### `test_fixops_smoke.py`

Verifies that the Auto-Fix (FixOps) subsystem imports are intact:

- `shared.ai.auto_fix` and its public API (`AutoFixEngine`, `FixStrategy`, etc.)
- `shared.ai.ollama_client`
- `shared.ai.model_training`
- Gracefully skips individual tests when optional dependencies (e.g., `torch`, `transformers`) are not installed

Marked with: `@pytest.mark.smoke` and `@pytest.mark.fixops`

## Behavior

- Tests use `pytest.skip()` rather than failing when optional service paths or heavy ML dependencies are absent. This allows the smoke suite to run in minimal CI environments.
- The `requires_dependency()` helper in `test_fixops_smoke.py` gates tests on optional packages at collection time.
- No environment variables, databases, or network connections are required.

## When to Add Smoke Tests

Add a smoke test when:
- You introduce a new top-level package under `shared/` or `packages/`
- You add a new service's `main.py` that should be importable
- You add a new optional dependency that should be gracefully skipped when absent
