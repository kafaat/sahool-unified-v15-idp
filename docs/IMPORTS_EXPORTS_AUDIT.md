# SAHOOL Imports/Exports Audit Report

**Audit Date**: January 2026
**Platform Version**: 16.0.0
**Auditor**: Automated Code Analysis

---

## Executive Summary

This document provides a comprehensive audit of the SAHOOL platform's import/export structure across Python shared modules and TypeScript packages. The audit identifies structural issues, missing exports, version misalignments, and provides actionable recommendations.

### Key Findings

| Category | Status | Issues Found |
|----------|--------|--------------|
| Circular Imports | PASS | None detected |
| Root Module Exports | FAIL | Hollow `__init__.py` |
| Duplicate Locations | WARN | 2 shared directories |
| Missing Exports | FAIL | 3 modules affected |
| Version Alignment | WARN | 15.3.3 vs 16.0.0 mismatch |
| TypeScript Packages | PASS | All properly configured |

---

## 1. Summary Statistics

### Python Shared Modules

| Metric | Count |
|--------|-------|
| Total Modules | 50 |
| Modules with Exports | 47 |
| Hollow Modules | 3 |
| Version 16.0.0 | 50 |

**Module List** (`shared/`):

```
a2a/                    agri_calendar/          ai/
audit_trail/            auth/                   batch_operations/
cache/                  contracts/              cooperatives/
crop_insurance/         crop_rotation/          crm/
domain/                 drone_integration/      edge_cloud/
equipment_maintenance/  events/                 farm_documents/
fertilizer_management/  field_boundaries/       file_validation/
geofencing/             globalgap/              guardrails/
harvest_quality/        integrations/           irrigation/
labor_management/       learning_marketplace/   libs/
lowcode/                market_prices/          mcp/
middleware/             ml_irrigation/          mobile_sync/
monitoring/             notification_preferences/ observability/
pest_scouting/          pesticide_compliance/   secrets/
security/               smart_agriculture/      soil_sensors/
soil_testing/           telemetry/              traceability/
water_management/       weather_alerts/
```

### TypeScript Packages

| Metric | Count |
|--------|-------|
| Total Packages | 16 |
| Properly Configured | 16 |
| Version 16.0.0 | 16 |
| With exports map | 14 |

**Package List** (`packages/`):

| Package | Version | Exports |
|---------|---------|---------|
| @sahool/api-client | 16.0.0 | 3 entry points |
| @sahool/design-system | 16.0.0 | 1 entry point |
| @sahool/field-shared | 16.0.0 | 1 entry point |
| @sahool/i18n | 16.0.0 | 1 entry point |
| @sahool/mock-data | 16.0.0 | 1 entry point |
| @sahool/nestjs-auth | 16.0.0 | 1 entry point |
| @sahool/shared-audit | 16.0.0 | 1 entry point |
| @sahool/shared-crypto | 16.0.0 | 1 entry point |
| @sahool/shared-db | 16.0.0 | 1 entry point |
| @sahool/shared-events | 16.0.0 | 1 entry point |
| @sahool/shared-hooks | 16.0.0 | 1 entry point |
| @sahool/shared-types | 16.0.0 | 6 entry points |
| @sahool/shared-ui | 16.0.0 | 1 entry point |
| @sahool/shared-utils | 16.0.0 | 1 entry point |
| @sahool/tailwind-config | 16.0.0 | Config only |
| @sahool/typescript-config | 16.0.0 | Config only |

---

## 2. Python Shared Modules Analysis

### 2.1 Root `__init__.py` Issue (CRITICAL)

**Location**: `/shared/__init__.py`

**Current State** (Hollow):
```python
"""SAHOOL Shared Library - Common utilities and modules"""

__version__ = "16.0.0"
```

**Impact**:
- Cannot use `from shared import auth, cache, events`
- Forces verbose imports: `from shared.auth import get_current_user`
- Inconsistent with Python best practices

**Recommended Fix**:
```python
"""SAHOOL Shared Library - Common utilities and modules"""

__version__ = "16.0.0"

# Core Authentication
from shared import auth
from shared import cache
from shared import events
from shared import domain
from shared import contracts
from shared import middleware
from shared import monitoring
from shared import observability
from shared import security
from shared import telemetry

# Convenience re-exports for common patterns
from shared.auth import (
    get_current_user,
    get_current_active_user,
    create_access_token,
    verify_token,
)
from shared.cache import CacheManager, get_cache_manager
from shared.events import EventPublisher, EventConsumer

__all__ = [
    # Modules
    "auth",
    "cache",
    "events",
    "domain",
    "contracts",
    "middleware",
    "monitoring",
    "observability",
    "security",
    "telemetry",
    # Common exports
    "get_current_user",
    "get_current_active_user",
    "create_access_token",
    "verify_token",
    "CacheManager",
    "get_cache_manager",
    "EventPublisher",
    "EventConsumer",
]
```

### 2.2 Well-Configured Module Example

**Location**: `/shared/auth/__init__.py`

This module demonstrates proper export configuration with 76 exports:

```python
from .config import JWTConfig, config
from .dependencies import (
    get_current_active_user,
    get_current_user,
    get_optional_user,
    # ... more exports
)
from .jwt_handler import (
    create_access_token,
    create_refresh_token,
    # ... more exports
)

__all__ = [
    "JWTConfig",
    "config",
    "get_current_user",
    "get_current_active_user",
    # ... 72 more items
]
```

**Best Practices Demonstrated**:
- Explicit imports from submodules
- Comprehensive `__all__` list
- Logical grouping with comments
- Version included

### 2.3 Hollow Module: `shared/libs/__init__.py` (NEEDS FIX)

**Location**: `/shared/libs/__init__.py`

**Current State**:
```python
"""
SAHOOL Shared Libraries
Common libraries used across domains
"""

__version__ = "16.0.0"
```

**Available Files Not Exported**:
- `caching.py` - CacheConfig, CacheManager, InMemoryCache, RedisCache, cached decorator
- `database.py` - Database utilities
- `pagination.py` - Pagination utilities

**Recommended Fix**:
```python
"""
SAHOOL Shared Libraries
Common libraries used across domains
"""

__version__ = "16.0.0"

from .caching import (
    CacheConfig,
    CacheManager,
    InMemoryCache,
    RedisCache,
    cached,
    get_cache_manager,
    invalidate_field_cache,
    invalidate_tenant_cache,
    invalidate_user_cache,
)
from .database import (
    # Add database exports
)
from .pagination import (
    # Add pagination exports
)

__all__ = [
    # Caching
    "CacheConfig",
    "CacheManager",
    "InMemoryCache",
    "RedisCache",
    "cached",
    "get_cache_manager",
    "invalidate_field_cache",
    "invalidate_tenant_cache",
    "invalidate_user_cache",
    # Database
    # Pagination
]
```

### 2.4 Hollow Module: `shared/domain/__init__.py` (NEEDS FIX)

**Location**: `/shared/domain/__init__.py`

**Current State**:
```python
"""
SAHOOL Kernel Domain
Core platform capabilities: Identity, Auth, Tenancy, Users

Architecture Rules:
- kernel_domain can import from: shared
- kernel_domain CANNOT import from: field_suite, advisor
"""

__version__ = "16.0.0"
```

**Impact**: Module exists but exports nothing. Services cannot import domain models.

**Action Required**:
1. Identify domain model files within `shared/domain/`
2. Create proper exports for domain entities
3. Document import rules in exports

### 2.5 Partial Exports: `shared/contracts/__init__.py` (NEEDS FIX)

**Location**: `/shared/contracts/__init__.py`

**Current State**:
```python
from shared.contracts.events import *
from shared.contracts.actions import *

__all__ = [
    "events",
    "actions",
]
```

**Issue**: `__all__` exports module names ("events", "actions") but not actual objects. The star imports (`*`) bring in the objects, but they're not listed in `__all__`.

**Recommended Fix**:
```python
"""
SAHOOL Contracts Module - API contracts and schemas
"""

from shared.contracts.actions import (
    ActionStatus,
    ActionStep,
    ActionTemplate,
    ActionTemplateFactory,
    ActionType,
    Resource,
    ResourceType,
    TimeWindow,
    UrgencyLevel,
)
from shared.contracts.events import (
    BaseEvent,
    CropDiseaseDetectedEvent,
    CropHarvestedEvent,
    CropPlantedEvent,
    EventConsumer,
    EventMetadata,
    EventPublisher,
    EventRegistry,
    FieldCreatedEvent,
    FieldUpdatedEvent,
    NDVICalculatedEvent,
    SensorAlertEvent,
    SensorReadingEvent,
    WeatherAlertIssuedEvent,
    WeatherForecastUpdatedEvent,
    YieldPredictedEvent,
)

__all__ = [
    # Events
    "BaseEvent",
    "EventMetadata",
    "FieldCreatedEvent",
    "FieldUpdatedEvent",
    "CropPlantedEvent",
    "CropDiseaseDetectedEvent",
    "CropHarvestedEvent",
    "WeatherForecastUpdatedEvent",
    "WeatherAlertIssuedEvent",
    "SensorReadingEvent",
    "SensorAlertEvent",
    "NDVICalculatedEvent",
    "YieldPredictedEvent",
    "EventPublisher",
    "EventConsumer",
    "EventRegistry",
    # Actions
    "ActionType",
    "ActionStatus",
    "UrgencyLevel",
    "ResourceType",
    "ActionTemplate",
    "ActionStep",
    "Resource",
    "TimeWindow",
    "ActionTemplateFactory",
]

__version__ = "16.0.0"
```

---

## 3. TypeScript Packages Analysis

### 3.1 Package Export Configuration

All TypeScript packages follow proper export patterns:

**Example: @sahool/shared-types**

```json
{
  "name": "@sahool/shared-types",
  "version": "16.0.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "require": "./dist/index.js",
      "types": "./dist/index.d.ts"
    },
    "./auth": { /* subpath export */ },
    "./api": { /* subpath export */ },
    "./express": { /* subpath export */ },
    "./websocket": { /* subpath export */ },
    "./monitoring": { /* subpath export */ },
    "./field": { /* subpath export */ }
  }
}
```

**Best Practices Followed**:
- Dual CJS/ESM support
- TypeScript declaration files
- Subpath exports for tree-shaking
- Consistent versioning

### 3.2 Package Index Files

**Example: @sahool/shared-types/src/index.ts**

```typescript
/**
 * SAHOOL Shared Types Package
 * @version 16.0.0
 */

// Auth types
export * from "./auth";

// API types
export * from "./api";

// Express types
export * from "./express";

// WebSocket types
export * from "./websocket";

// Monitoring types
export * from "./monitoring";

// Field types
export * from "./field";
```

**Example: @sahool/shared-events/src/index.ts**

```typescript
// Named exports for NATS client
export {
  NatsClient,
  NatsClientConfig,
  initializeNatsClient,
  getNatsConnection,
} from "./nats-client";

// Named exports for event types
export {
  BaseEvent,
  FieldCreatedEvent,
  // ... 20+ event types
} from "./events";

// Named exports for publishers
export {
  publishEvent,
  publishFieldCreated,
  // ... 15+ publisher functions
} from "./publisher";

// Named exports for subscribers
export {
  subscribe,
  subscribePattern,
  // ... 10+ subscriber utilities
} from "./subscriber";
```

---

## 4. Duplicate Shared Locations (WARNING)

### 4.1 Issue Description

Two `shared/` directories exist with overlapping functionality:

| Location | Purpose | Modules |
|----------|---------|---------|
| `/shared/` | Root shared library | 50 modules |
| `/apps/services/shared/` | Services-specific shared | 26 modules |

### 4.2 Duplicate Module Comparison

| Module | Root `/shared/` | `/apps/services/shared/` |
|--------|-----------------|-------------------------|
| auth | Yes | Yes |
| middleware | Yes | Yes |
| observability | Yes | Yes |
| mcp | Yes | Yes |
| file_validation | Yes | Yes |
| globalgap | Yes | Yes |
| libs | Yes | Yes |
| contracts | Yes (events, actions) | Yes (events, actions) |

### 4.3 Recommended Actions

1. **Consolidate to root `/shared/`**:
   - Root shared should be the single source of truth
   - Move unique modules from `apps/services/shared/` to root

2. **Create symlinks for backward compatibility**:
   ```bash
   # In apps/services/shared/
   ln -s ../../../shared/auth auth
   ln -s ../../../shared/middleware middleware
   ```

3. **Update import paths in services**:
   ```python
   # Before
   from apps.services.shared.auth import get_current_user

   # After
   from shared.auth import get_current_user
   ```

4. **Add path configuration in pyproject.toml**:
   ```toml
   [tool.pytest.ini_options]
   pythonpath = [".", "shared"]
   ```

---

## 5. Version Alignment Issues

### 5.1 Version Mismatch Summary

| Component | Expected | Actual | Status |
|-----------|----------|--------|--------|
| pyproject.toml | 16.0.0 | 16.0.0 | OK |
| shared/__init__.py | 16.0.0 | 16.0.0 | OK |
| TypeScript packages | 16.0.0 | 16.0.0 | OK |
| Python services | 16.0.0 | 15.3.3 | MISMATCH |
| Mobile app | 16.0.0 | 15.3.3 | MISMATCH |

### 5.2 Services Still at v15.3.3

**Active Services** (Priority: HIGH):

| Service | File | Current Version |
|---------|------|-----------------|
| weather-service | `apps/services/weather-service/src/__init__.py` | 15.3.3 |
| weather-core | `apps/services/weather-core/src/__init__.py` | 15.3.3 |
| field-management-service | `apps/services/field-management-service/src/__init__.py` | 15.3.3 |
| advisory-service | `apps/services/advisory-service/src/__init__.py` | 15.3.3 |
| agro-advisor | `apps/services/agro-advisor/src/__init__.py` | 15.3.3 |
| agro-rules | `apps/services/agro-rules/src/__init__.py` | 15.3.3 |
| iot-gateway | `apps/services/iot-gateway/src/__init__.py` | 15.3.3 |
| ndvi-engine | `apps/services/ndvi-engine/src/__init__.py` | 15.3.3 |
| field-ops | `apps/services/field-ops/src/__init__.py` | 15.3.3 |
| field-core | `apps/services/field-core/src/__init__.py` | 15.3.3 |
| field-chat | `apps/services/field-chat/src/__init__.py` | 15.3.3 |

**Mobile App**:

| File | Current Version |
|------|-----------------|
| `apps/mobile/lib/features/settings/ui/settings_screen.dart` | 15.3.3 |
| `apps/mobile/sahool_field_app/lib/features/settings/ui/settings_screen.dart` | 15.3.3 |

### 5.3 Recommended Version Update Script

```bash
#!/bin/bash
# update-versions.sh

OLD_VERSION="15.3.3"
NEW_VERSION="16.0.0"

# Update Python __init__.py files
find apps/services -name "__init__.py" -exec \
  sed -i "s/__version__ = \"$OLD_VERSION\"/__version__ = \"$NEW_VERSION\"/g" {} \;

# Update Python main.py files
find apps/services -name "main.py" -exec \
  sed -i "s/version=\"$OLD_VERSION\"/version=\"$NEW_VERSION\"/g" {} \;

# Update Dart files
find apps/mobile -name "*.dart" -exec \
  sed -i "s/الإصدار $OLD_VERSION/الإصدار $NEW_VERSION/g" {} \;

echo "Version update complete: $OLD_VERSION -> $NEW_VERSION"
```

---

## 6. Circular Import Analysis

### 6.1 Results: PASS

No circular imports were detected in the codebase. The dependency graph follows a clean hierarchy:

```
shared/
├── auth (no internal deps)
├── cache (no internal deps)
├── events (imports: auth for user context)
├── contracts
│   ├── events (imports: pydantic only)
│   └── actions (imports: pydantic only)
├── middleware (imports: auth, observability)
├── observability (no internal deps)
└── telemetry (imports: observability)
```

### 6.2 Import Best Practices

**DO**:
```python
# Explicit imports at top of file
from shared.auth import get_current_user
from shared.events import EventPublisher

# Type-only imports for circular prevention
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from shared.domain import User
```

**DON'T**:
```python
# Avoid star imports
from shared.auth import *

# Avoid runtime conditional imports
def get_user():
    from shared.auth import get_current_user  # Bad practice
    return get_current_user()
```

---

## 7. Recommendations Summary

### Priority 1: Critical (Fix Immediately)

| Issue | Action | Effort |
|-------|--------|--------|
| Hollow root `shared/__init__.py` | Populate with core exports | 2 hours |
| Missing exports in `shared/libs/` | Add exports for caching, database, pagination | 1 hour |
| Missing exports in `shared/domain/` | Identify and export domain models | 2 hours |

### Priority 2: High (Fix This Sprint)

| Issue | Action | Effort |
|-------|--------|--------|
| Version mismatch (15.3.3) | Run version update script | 1 hour |
| Incomplete `shared/contracts/` exports | Update `__all__` with actual exports | 30 min |

### Priority 3: Medium (Plan for Next Sprint)

| Issue | Action | Effort |
|-------|--------|--------|
| Duplicate shared directories | Consolidate to single location | 4 hours |
| Import path standardization | Update all services to use root shared | 8 hours |

### Priority 4: Low (Technical Debt Backlog)

| Issue | Action | Effort |
|-------|--------|--------|
| Documentation sync | Update README files with version | 2 hours |
| Add export validation CI | Create pre-commit hook | 3 hours |

---

## 8. Implementation Checklist

### 8.1 Python Shared Modules

- [ ] Update `/shared/__init__.py` with core exports
- [ ] Update `/shared/libs/__init__.py` with caching, database, pagination exports
- [ ] Update `/shared/domain/__init__.py` with domain model exports
- [ ] Update `/shared/contracts/__init__.py` with explicit exports
- [ ] Verify all 50 modules have proper `__all__` definitions

### 8.2 Version Alignment

- [ ] Run version update script for Python services
- [ ] Update mobile app version strings
- [ ] Verify all services report 16.0.0 on `/healthz`

### 8.3 Directory Consolidation

- [ ] Audit modules in `apps/services/shared/`
- [ ] Migrate unique modules to root `/shared/`
- [ ] Create backward compatibility symlinks
- [ ] Update service import paths

### 8.4 CI/CD Integration

- [ ] Add export validation to pre-commit hooks
- [ ] Add version consistency check to CI pipeline
- [ ] Create automated audit report generation

---

## Appendix A: Module Export Counts

| Module | Exports | Status |
|--------|---------|--------|
| shared.auth | 76 | Excellent |
| shared.events | TBD | Good |
| shared.cache | TBD | Good |
| shared.contracts | 2 (module refs) | Needs Fix |
| shared.libs | 0 | Needs Fix |
| shared.domain | 0 | Needs Fix |
| shared.middleware | TBD | Good |
| shared.monitoring | TBD | Good |
| shared.observability | TBD | Good |
| shared.security | TBD | Good |

---

## Appendix B: TypeScript Package Dependencies

```mermaid
graph TD
    A[@sahool/shared-types] --> B[@sahool/api-client]
    A --> C[@sahool/shared-hooks]
    A --> D[@sahool/shared-ui]
    E[@sahool/shared-utils] --> D
    F[@sahool/shared-events] --> G[Services]
    H[@sahool/nestjs-auth] --> G
    I[@sahool/shared-db] --> G
```

---

## Appendix C: Service Health Endpoint Versions

Expected response format after version update:

```json
{
  "status": "ok",
  "service": "service_name",
  "version": "16.0.0"
}
```

---

_Last Updated: January 2026_
_Next Review: February 2026_
