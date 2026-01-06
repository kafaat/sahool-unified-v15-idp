# Kong Configuration Files Alignment

## Overview

This document describes the alignment between the two Kong API Gateway configuration files in the SAHOOL platform.

## Configuration Files

### Canonical Source (Single Source of Truth)
- **Location**: `/infra/kong/kong.yml`
- **Purpose**: Primary Kong configuration file for the platform
- **Status**: Active, authoritative configuration

### Mirror Configuration
- **Location**: `/infrastructure/gateway/kong/kong.yml`
- **Purpose**: Mirror of the canonical configuration for infrastructure deployment
- **Status**: Should always mirror the canonical file

## Alignment Summary

As of January 6, 2026, the following alignment has been completed:

### 1. **Healthcheck Configuration** ✅
All three upstreams now have consistent active healthcheck configurations:
- `marketplace-service-upstream`: Active healthchecks restored
- `billing-core-upstream`: Active healthchecks restored  
- `research-core-upstream`: Active healthchecks restored

### 2. **Service URL/Host Configurations** ✅
All service URLs and ports now match the canonical configuration:
- `agro-advisor`: Uses `url: http://advisory-service:8093`
- `ndvi-engine`: Uses `url: http://ndvi-processor:8118` (DEPRECATED service)
- `yield-engine`: Uses `url: http://yield-prediction-service:3021`
- `inventory-service`: Uses `url: http://inventory-service:8115`
- `iot-gateway`: Uses `host: iot-gateway-upstream`
- `weather-advanced`: Uses `url: http://weather-service:8108`

### 3. **Removed Services** ✅
The `auth-service` that was only in the infrastructure/ file has been removed to match the canonical configuration. Authentication endpoints should be implemented as a dedicated service when needed.

### 4. **Admin Dashboard Configuration** ✅
The admin-dashboard commented configuration now matches exactly between both files.

## Validation

Both configuration files have been validated:
- ✅ Valid YAML syntax
- ✅ CORS properly configured (no wildcards)
- ✅ 15 upstreams with healthchecks
- ✅ 38 Redis-based rate-limiting plugins
- ✅ Security headers configured
- ✅ RS256 JWT support enabled

## Service Port Reference

Based on the actual docker-compose.yml deployment configuration:

| Service | Container | Port | Status |
|---------|-----------|------|--------|
| advisory-service | sahool-advisory-service | 8093 | Active |
| weather-service | sahool-weather-service | 8092 | Active |
| iot-gateway | sahool-iot-gateway | 8106 | Active |
| inventory-service | sahool-inventory-service | 8116 | Active |
| yield-prediction-service | sahool-yield-prediction-service | 8098 | Active |
| ndvi-processor | sahool-ndvi-processor | 8118 | Deprecated |
| ndvi-engine | sahool-ndvi-engine | 8107 | Deprecated |

## Maintenance Guidelines

### For Future Updates

1. **Always update the canonical file first**: `/infra/kong/kong.yml`
2. **Then synchronize the mirror**: Copy changes to `/infrastructure/gateway/kong/kong.yml`
3. **Maintain the header comment** in the mirror file indicating it should mirror the canonical file
4. **Run validation**: Execute `scripts/validate-kong-config.sh` after changes
5. **Test both configurations** in their respective deployment scenarios

### Validation Commands

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('infra/kong/kong.yml'))"
python3 -c "import yaml; yaml.safe_load(open('infrastructure/gateway/kong/kong.yml'))"

# Run full validation
bash scripts/validate-kong-config.sh

# Compare files
diff -u infra/kong/kong.yml infrastructure/gateway/kong/kong.yml
```

## Known Differences

The **only** intentional difference between the two files is the header comment in the mirror file:
```yaml
# ============================================================================
# NOTE: This file should mirror /infra/kong/kong.yml
# The canonical configuration is in /infra/kong/kong.yml
# ============================================================================
```

## Related CI/CD

The infrastructure sync workflow (`.github/workflows/infra-sync.yml`) validates generated infrastructure files but does not currently validate Kong configuration alignment. Consider adding Kong configuration sync validation to this workflow.

## Next Steps

1. ✅ Configuration alignment completed
2. ⚠️ Consider adding IP restrictions to `billing-core` and `marketplace-service` for enhanced security
3. 🔄 Plan migration away from deprecated NDVI services (`ndvi-processor`, `ndvi-engine`) to consolidated `vegetation-analysis-service` (Port 8090)
4. 🔄 Implement dedicated authentication service to replace placeholder endpoints

## References

- Kong Configuration: `/infra/kong/kong.yml`
- Mirror Configuration: `/infrastructure/gateway/kong/kong.yml`
- Service Registry: `/governance/services.yaml`
- Docker Compose: `/docker-compose.yml`
- Validation Script: `/scripts/validate-kong-config.sh`
