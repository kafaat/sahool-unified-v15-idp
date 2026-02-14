# Deprecated Services Archive

This directory contains services that have been deprecated and replaced by newer implementations.

**Archive Date**: 2026-01-25
**Version**: 16.0.0

## Service Migration Map

| Deprecated Service | Replacement Service | Port | Archive Date |
|-------------------|---------------------|------|--------------|
| `satellite-service` | `vegetation-analysis-service` | 8090 | 2026-01-25 |
| `weather-advanced` | `weather-service` | 8092 | 2026-01-25 |
| `crop-health-ai` | `crop-intelligence-service` | 8095 | 2026-01-25 |
| `crop-health` | `crop-intelligence-service` | 8095 | 2026-01-25 |
| `fertilizer-advisor` | `advisory-service` | 8093 | 2026-01-25 |
| `field-ops` | `field-management-service` | 3000 | 2026-01-25 |
| `field-core` | `field-management-service` | 3000 | 2026-01-25 |
| `field-service` | `field-management-service` | 3000 | 2026-01-25 |
| `agro-advisor` | `advisory-service` | 8093 | 2026-02-14 |
| `ndvi-engine` | `vegetation-analysis-service` | 8090 | 2026-02-14 |
| `weather-core` | `weather-service` | 8092 | 2026-02-14 |

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
