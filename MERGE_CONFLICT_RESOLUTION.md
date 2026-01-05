# Merge Conflict Resolution for PR #388 & PR #390

## Summary
Successfully resolved all merge conflicts between PR branch `claude/create-auto-audit-tools-qTNzb` and `main` branch.

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

### 4. infra/kong/kong.yml
**Conflict:** API route paths for astronomical calendar service

**Resolution:** Support BOTH paths for backward compatibility
```yaml
paths:
  - /api/v1/astronomical
  - /api/v1/calendar
```

**Rationale:** Allows both old and new API paths to work, preventing breaking changes for existing clients.

### 5. infrastructure/gateway/kong/kong.yml
**Conflict:** Same as infra/kong/kong.yml

**Resolution:** Support BOTH paths for backward compatibility
```yaml
paths:
  - /api/v1/astronomical
  - /api/v1/calendar
```

**Rationale:** Consistency with infra/kong/kong.yml and backward compatibility.

## Resolution Strategy
All conflicts were resolved by keeping the **HEAD** (PR branch) version, which uses the modern `EnvConfig` approach instead of the deprecated `AppConfig`.

## Verification

After applying the changes:
1. ✅ No conflict markers remain in any files
2. ✅ All imports are consistent (using EnvConfig)
3. ✅ Both API paths are supported in Kong configuration
4. ✅ Weather service URL is configurable via environment variable

## Testing Recommendations

1. **Mobile App**: Verify that the API client connects properly using EnvConfig
2. **Astronomical Service**: Test that the weather integration works with the configurable URL
3. **API Gateway**: Verify both `/api/v1/astronomical` and `/api/v1/calendar` routes work

## Merge History
- Original PR: #388 (claude/create-auto-audit-tools-qTNzb)
- Conflict Resolution PR: #390 (copilot/fix-pull-request-conflicts)
- Final merge into: main
