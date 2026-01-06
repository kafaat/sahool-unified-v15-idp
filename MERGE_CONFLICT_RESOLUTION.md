# Merge Conflict Resolution Summary

## Summary
Successfully resolved all merge conflicts for PRs #388, #390, and #394.

## Conflicts Resolved

### 1. apps/mobile/lib/core/http/api_client.dart
**Resolution:** Kept `EnvConfig` for consistency
- Tenant ID: `EnvConfig.defaultTenantId`
- Base URL: `EnvConfig.apiBaseUrl`
- Connect Timeout: `EnvConfig.connectTimeout`

### 2. apps/mobile/lib/features/astronomical/providers/astronomical_providers.dart
**Resolution:** Kept `EnvConfig` usage
- Connect timeout: `env.EnvConfig.connectTimeout`
- Receive timeout: `env.EnvConfig.receiveTimeout`
- Base URL: `env.EnvConfig.apiBaseUrl`

### 3. apps/services/astronomical-calendar/src/main.py
**Resolution:** Configurable `WEATHER_SERVICE_URL` environment variable
```python
WEATHER_SERVICE_URL = os.getenv("WEATHER_SERVICE_URL", "http://weather-service:8092")
```

### 4. infra/kong/kong.yml & infrastructure/gateway/kong/kong.yml
**Resolution:** Support BOTH paths for backward compatibility
```yaml
paths:
  - /api/v1/astronomical
  - /api/v1/calendar
```

### 5. docker-compose.yml
**Resolution:** Virtual-sensors port migration: 8096 → 8119

### 6. shared/middleware/__init__.py
**Resolution:** Combined security headers with rate limiting exports

## Verification

✅ All conflicts resolved
✅ EnvConfig used consistently
✅ Both API paths supported (backward compatible)
✅ Weather service URL configurable
✅ Port conflicts resolved (virtual-sensors: 8119)

## Merge History
- PR #388: Task-astronomical calendar integration
- PR #390: Initial conflict resolution
- PR #394: Final comprehensive resolution
- PR #395: Merged into main
