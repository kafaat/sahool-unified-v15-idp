# Deprecated Services Archive

This directory contains services pending final removal. All others have been fully deleted.

**Last Updated**: 2026-05-13
**Version**: 16.0.0

## Remaining in Archive

| Service | Replacement Service | Port | Status |
|---------|---------------------|------|--------|
| `ndvi-processor` | `vegetation-analysis-service` | 8090 | Pending Phase 7 removal |

## Fully Deleted Services

The following services were archived and have been completely removed (passed sunset date):

| Service | Replacement | Deleted |
|---------|-------------|---------|
| `satellite-service` | `vegetation-analysis-service` | 2026-05-13 |
| `weather-advanced` | `weather-service` | 2026-05-13 |
| `crop-health-ai` | `crop-intelligence-service` | 2026-05-13 |
| `crop-health` | `crop-intelligence-service` | 2026-05-13 |
| `fertilizer-advisor` | `advisory-service` | 2026-05-13 |
| `field-ops` | `field-management-service` | 2026-05-13 |
| `field-core` | `field-management-service` | 2026-05-13 |
| `field-service` | `field-management-service` | 2026-05-13 |
| `agro-advisor` | `advisory-service` | 2026-05-13 |
| `ndvi-engine` | `vegetation-analysis-service` | 2026-05-13 |
| `weather-core` | `weather-service` | 2026-05-13 |
| `community-chat` | `chat-service` | 2026-05-13 |
| `field-chat` | `chat-service` | 2026-05-13 |
| `yield-engine` | `yield-prediction-service` | 2026-05-13 |
| `wechat-service` | Reactivated as active service | 2026-05-13 |

## Why Archived

These services were archived as part of the SAHOOL platform consolidation effort:

1. **Reduce duplication**: Multiple services provided overlapping functionality
2. **Simplify maintenance**: Fewer services means easier deployment and monitoring
3. **Improve consistency**: Unified APIs and data models
4. **Better resource utilization**: Consolidated services are more efficient

## Safe to Delete?

These services can be safely deleted after:

1. Verifying no active deployments reference them
2. Ensuring all CI/CD pipelines use the replacement services
3. Confirming all client applications have migrated to new service names

## Migration Notes

- All API endpoints have been migrated to the replacement services
- Data migrations were completed before archiving
- Configuration files (Kong, Helm, etc.) have been updated

## Contact

For questions about these deprecated services, contact the SAHOOL platform team.
