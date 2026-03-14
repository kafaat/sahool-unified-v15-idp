# Deprecation Notice: wechat-service

**Status**: DEPRECATED
**Deprecation Date**: 2026-03-13
**Sunset Date**: 2026-06-01
**Replaced By**: `community-service` (Rocket.Chat integration)

## Summary

The `wechat-service` has been deprecated in favor of `community-service`, which provides unified community communication capabilities through Rocket.Chat integration. The new service consolidates messaging, farmer engagement, and social features into a single platform-agnostic service.

## Migration

All consumers of `wechat-service` APIs should migrate to `community-service` before the sunset date of 2026-06-01.

### Key Changes

- WeChat-specific messaging endpoints are replaced by the unified messaging API in `community-service`
- NATS event subjects previously published by `wechat-service` (e.g., `WeChatMessageReceived.v1`, `WeChatMessageSent.v1`) will be replaced by equivalent events from `community-service`
- Database schema `wechat` will be migrated to the `community-service` schema

## Timeline

| Date | Action |
|------|--------|
| 2026-03-13 | Service marked as deprecated; removed from default docker-compose profile |
| 2026-06-01 | Sunset: service will be fully removed; all clients must have migrated |

## Running for Migration Testing

The deprecated service can still be started for migration testing using the `deprecated` profile:

```bash
docker-compose --profile deprecated up wechat-service
```

## Contact

For questions about this deprecation, contact the SAHOOL platform team or `frontend-team@sahool.io`.
