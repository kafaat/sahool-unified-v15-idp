# SAHOOL Architecture Rules

> **Version:** 16.0.0
> **Last Updated:** December 2025

## Domain Architecture

SAHOOL follows a domain-driven design with clear boundaries between domains.

### Domain Structure

```
sahool-unified/
├── kernel_domain/      # Core platform capabilities
│   ├── auth/           # Authentication & JWT
│   ├── tenancy/        # Multi-tenant management
│   └── users/          # User management
│
├── field_suite/        # Agricultural field management
│   ├── farms/          # Farm entities
│   ├── fields/         # Field entities
│   └── crops/          # Crop management
│
├── advisor/            # AI advisory system
│   ├── ai/             # AI engine
│   ├── rag/            # Retrieval-Augmented Generation
│   ├── context/        # Context building
│   └── feedback/       # User feedback
│
├── shared/             # Shared utilities (no domain logic)
│   ├── contracts/      # API contracts
│   └── security/       # Security utilities
│
└── legacy/             # Compatibility layer (deprecated)
```

## Import Rules

### Rule 1: No Cross-Domain Imports

Domains MUST NOT import from each other directly.

```python
# ❌ FORBIDDEN - Cross-domain import
from field_suite.fields import Field  # in advisor module

# ✅ ALLOWED - Import from shared
from shared.contracts import FieldContract
```

### Rule 2: Dependency Direction

```
┌─────────────────────────────────────────────────────┐
│                    Application Layer                 │
│                  (FastAPI routers, CLI)             │
└────────────────────────┬────────────────────────────┘
                         │ depends on
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ kernel   │  │  field   │  │ advisor  │
    │ domain   │  │  suite   │  │          │
    └────┬─────┘  └────┬─────┘  └────┬─────┘
         │             │             │
         └──────────┬──┴─────────────┘
                    ▼
              ┌──────────┐
              │  shared  │
              └──────────┘
```

- **Application layer** can import from any domain
- **Domains** can only import from `shared/`
- **Shared** has no dependencies on domains

### Rule 3: Legacy Layer Usage

The `legacy/` module provides backward compatibility during migration.

```python
# ⚠️ DEPRECATED - Will be removed in v17.0.0
from legacy.auth import create_access_token

# ✅ RECOMMENDED - Use new domain packages
from kernel_domain.auth import create_access_token
```

### Rule 4: Shared Contracts

Use contracts for cross-domain data exchange:

```python
# In shared/contracts/field_contract.py
@dataclass
class FieldContract:
    id: str
    name: str
    area_hectares: float

# In advisor (consumer)
from shared.contracts import FieldContract

def process_field(field: FieldContract):
    ...
```

## Module Structure

Each domain module follows this structure:

```
domain/
├── __init__.py      # Public API exports
├── module/
│   ├── __init__.py  # Module exports
│   ├── models.py    # Data models (dataclasses/Pydantic)
│   └── service.py   # Business logic
```

### Model Guidelines

1. Use `@dataclass` for domain entities
2. Provide `create()` factory methods
3. Include `to_dict()` for serialization
4. Support Arabic localization (`name_ar`, `title_ar`)

### Service Guidelines

1. Services are stateless handlers
2. Use in-memory stores as placeholders (marked for repository pattern)
3. Methods return `Optional[T]` for queries that may not find results
4. Raise `ValueError` for business rule violations

## Enforcement

### Automated Checks

Run architecture checks before committing:

```bash
# Check import rules
make arch-check

# Full pre-commit validation
make lint
```

### CI Pipeline

Architecture violations fail the CI pipeline:

```yaml
- name: Check Architecture
  run: make arch-check
```

### Smoke Tests

Import validation runs with tests:

```bash
pytest tests/smoke/test_arch_imports.py -v
```

## Migration Guide

### From Monolithic to Domain

1. Identify the domain for your code
2. Create module in appropriate domain package
3. Add re-exports in `legacy/` for backward compatibility
4. Update imports gradually
5. Remove legacy imports before v17.0.0

### Example Migration

```python
# Step 1: Old code
class UserAuth:
    def login(self, email, password):
        ...

# Step 2: Move to kernel_domain/auth/service.py
# Step 3: Add to legacy/auth.py:
from kernel_domain.auth import UserAuth

# Step 4: Update consumers to new imports
# Step 5: Remove legacy re-export
```

## FAQ

**Q: Can I import field_suite in advisor for field data?**

A: No. Use contracts or pass data through the application layer.

**Q: Where do utilities like logging go?**

A: In `shared/` if domain-agnostic, or in the specific domain if domain-specific.

**Q: How do I handle cross-domain transactions?**

A: Orchestrate at the application layer (routers/CLI), not within domains.
