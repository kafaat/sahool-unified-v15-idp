# Archived Helm Charts - Deprecated Services

These Helm charts were archived on **2026-02-27** as part of the SAHOOL platform cleanup. Each chart corresponds to a deprecated service that has been replaced by a modern equivalent.

Do NOT deploy these charts in production. They are retained for historical reference and migration testing only.

## Archived Charts

| Chart | Replaced By | Original Deprecation Date |
| ----- | ----------- | ------------------------- |
| `agro-advisor` | `advisory-service` | 2025-01-06 |
| `crop-health` | `crop-intelligence-service` | 2026-01-06 |
| `crop-health-ai` | `crop-intelligence-service` | 2025-01-01 |
| `field-ops` | `field-management-service` | 2026-01-06 |
| `ndvi-engine` | `vegetation-analysis-service` | 2026-01-06 |
| `satellite-service` | `vegetation-analysis-service` | 2025-01-01 |
| `weather-advanced` | `weather-service` | 2025-01-01 |
| `weather-core` | `weather-service` | Implicit |
| `yield-engine` | `yield-prediction-service` | 2026-01-15 |

## Deleted Duplicate Charts

The following charts were removed entirely from `helm/services/` because modern versions already exist in `helm/charts/`:

| Chart | Active Location |
| ----- | --------------- |
| `billing-core` | `helm/charts/billing-core` |
| `irrigation-smart` | `helm/charts/irrigation-smart` |

## References

- Service deprecation registry: `governance/services.yaml`
- Full deprecation summary: `apps/services/DEPRECATION_SUMMARY.md`
- Archived service code: `archive/deprecated-services/`
