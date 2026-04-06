# DEPRECATED - React Native Mobile App

**Status**: Archived (incomplete)
**Moved from**: `apps/mobile/sahool-mobile/`
**Date**: 2026-04-06
**Reason**: Only the sync manager (~1,432 lines) was implemented. Missing: app shell, UI components, navigation, API client, platform setup. The primary mobile stack is Flutter (`apps/mobile/sahool_field_app/`).

## Salvageable Code

- `src/services/syncManager.ts` - Offline-first sync manager with conflict resolution
- `src/models/syncTypes.ts` - Sync type definitions

Consider extracting the sync manager logic into a shared package if React Native support is revisited.
