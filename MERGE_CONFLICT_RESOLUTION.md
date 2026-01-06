# Merge Conflict Resolution for PR #390

## Summary
Successfully resolved all merge conflicts between PR branch `copilot/fix-pull-request-conflicts` and `main` branch (which includes updates from PRs #388, #394, #395, #397).

## Conflicts Resolved

### 1. apps/mobile/lib/core/http/api_client.dart
**Conflict:** Choice between `AppConfig` (from main) vs `EnvConfig` (from PR branch)

**Resolution:** Kept `EnvConfig` for consistency with the rest of the codebase
- Import: Added `dart:convert` and kept `env_config.dart`
- Tenant ID: `EnvConfig.defaultTenantId`
- Base URL: `EnvConfig.apiBaseUrl`
- Connect Timeout: `EnvConfig.connectTimeout`

**Rationale:** The PR branch uses `EnvConfig` throughout, which is the more recent and dynamic configuration approach.

### 2. apps/mobile/lib/features/astronomical/providers/astronomical_providers.dart
**Conflict:** Configuration approach for Dio timeouts and base URL

**Resolution:** Kept `EnvConfig` usage
- Connect timeout: `env.EnvConfig.connectTimeout`
- Receive timeout: `env.EnvConfig.receiveTimeout`
- Base URL: `env.EnvConfig.apiBaseUrl`

**Rationale:** Maintains consistency with the dynamic configuration pattern used throughout the application.

### 3. apps/services/astronomical-calendar/src/main.py
**Conflict:** Weather service URL configuration

**Resolution:** Kept configurable `WEATHER_SERVICE_URL` environment variable
```python
WEATHER_SERVICE_URL = os.getenv(
    "WEATHER_SERVICE_URL",
    "http://weather-service:8092",
)
```

**Rationale:** Provides flexibility for different deployment environments (development, staging, production).

### 4. infra/kong/kong.yml & infrastructure/gateway/kong/kong.yml
**Conflict:** API route paths for astronomical calendar service

**Resolution:** Support BOTH paths for backward compatibility
```yaml
paths:
  - /api/v1/astronomical
  - /api/v1/calendar
```

**Rationale:** Allows both old and new API paths to work, preventing breaking changes for existing clients.

### 5. docker-compose.yml
**Resolution:** Virtual-sensors port migration: 8096 → 8119

**Rationale:** Resolves port conflict with code-review-service.

### 6. shared/middleware/__init__.py
**Resolution:** Combined security headers middleware exports with rate limiting exports

**Rationale:** Preserves security headers feature from PR branch while maintaining main branch structure.

### 7. apps/services/task-service (README.md & src/main.py)
**Resolution:** Keep PR branch's full astronomical calendar integration and NDVI automation features

**Rationale:** Preserves advanced features including:
- Astronomical calendar integration for optimal task scheduling
- NDVI-based task automation
- Best day recommendations based on lunar cycles
- Task validation against astronomical data

### 8. apps/web/src/features/fields (multiple files)
**Resolution:** Keep PR branch's field intelligence features

**Rationale:** Preserves advanced features including:
- AstralFieldWidget for astronomical recommendations
- Living Field Score and health monitoring
- Field zones and alerts
- Weather overlays and task markers

## Verification

✅ All conflicts resolved
✅ EnvConfig used consistently  
✅ Both API paths supported (backward compatible)
✅ Weather service URL configurable
✅ Port conflicts resolved (virtual-sensors: 8119)
✅ Astronomical calendar integration preserved
✅ NDVI automation features preserved
✅ Field intelligence features preserved
✅ Security headers middleware preserved

## Merge History
- PR #388: Task-astronomical calendar integration (grafted into main)
- PR #390: This PR - comprehensive merge conflict resolution
- PR #394, #395, #397: Previous merges into main branch
- Current merge: Prioritizing PR branch features while preserving main branch stability

## Testing Recommendations

1. **Mobile App**: Verify that the API client connects properly using EnvConfig
2. **Astronomical Service**: Test that the weather integration works with the configurable URL  
3. **API Gateway**: Verify both `/api/v1/astronomical` and `/api/v1/calendar` routes work
4. **Task Service**: Test astronomical-based task creation and NDVI alert integration
5. **Web App**: Verify field intelligence widgets and astronomical features render correctly
6. **Port Configuration**: Verify virtual-sensors runs on 8119 without conflicts
