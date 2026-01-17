# FROZEN - DO NOT MODIFY

> **Status**: FROZEN as of 2024-12-19
> **Reason**: Superseded by `kernel-services-v15.3/`
> **Migration**: In progress - see `governance/DEDUP_MATRIX.md`

## Warning

This directory is **frozen** and should not receive new features or modifications.

All new development should happen in:

```
kernel-services-v15.3/
```

## Services Still in Use (docker-compose.yml)

These services are still referenced by `docker-compose.yml` and will be migrated in v16:

| Service           | Status     | v15.3 Equivalent   |
| ----------------- | ---------- | ------------------ |
| field_core        | Active     | TBD                |
| field_ops         | Active     | TBD                |
| ndvi_engine       | Active     | satellite-service  |
| weather_core      | Active     | weather-advanced   |
| field_chat        | Deprecated | community-chat     |
| iot_gateway       | Active     | iot-service        |
| agro_advisor      | Deprecated | fertilizer-advisor |
| ws_gateway        | Active     | TBD                |
| crop_health       | Deprecated | crop-health-ai     |
| agro_rules        | Active     | TBD                |
| task_service      | Active     | TBD                |
| equipment_service | Active     | TBD                |
| community_service | Deprecated | community-chat     |
| provider_config   | Active     | TBD                |

## Next Steps

1. Create v15.3 equivalents for services marked "TBD"
2. Update docker-compose.yml to use v15.3 paths
3. Move this directory to `archive/kernel-legacy/`

---

**Do not add new code here. All changes go to kernel-services-v15.3/**
