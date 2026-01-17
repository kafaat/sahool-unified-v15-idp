# ADR-001: Offline-First Mobile Architecture

## Status

Accepted

## Context

SAHOOL is an agricultural platform serving farmers in Yemen, where:

1. **Unreliable connectivity**: Rural areas have intermittent or no internet
2. **Field operations**: Farmers need to record data while in the field
3. **Critical timing**: Agricultural decisions are time-sensitive
4. **Data integrity**: Collected data must not be lost

We needed an architecture that allows the mobile app to function fully without internet connectivity.

## Decision

We adopted an **Offline-First Architecture** with the following components:

### 1. Local Database (Drift/SQLite)

- All data stored locally first
- Full CRUD operations available offline
- Automatic schema migrations

### 2. Sync Engine with Outbox Pattern

- Changes queued in outbox table
- Background sync when online
- Conflict resolution strategies

### 3. Conflict Resolution

- Last-write-wins for non-critical data
- Server-wins for financial/official data
- User-choice for complex conflicts

### 4. Optimistic UI

- UI updates immediately on local change
- Rollback on sync failure
- Clear sync status indicators

## Consequences

### Positive

- **100% offline functionality** for core features
- **Zero data loss** - changes persist locally
- **Fast user experience** - no network latency for UI
- **Resilient operations** - works in poor connectivity
- **Reduced server load** - batch sync vs real-time

### Negative

- **Increased complexity** - sync logic is complex
- **Storage requirements** - full dataset stored locally
- **Conflict handling** - edge cases in resolution
- **Testing overhead** - need to test online/offline scenarios
- **Data staleness** - local data may be outdated

### Neutral

- Requires user education on sync status
- Mobile app size increased by ~5MB for local DB

## Alternatives Considered

### Alternative 1: Online-Only

**Rejected because:**

- Unusable in rural Yemen (60%+ of target users)
- Data loss during connectivity issues
- Poor UX with loading states

### Alternative 2: Cache-First (Read Offline, Write Online)

**Rejected because:**

- Cannot record field data offline
- Partial functionality frustrates users
- Complex UX for explaining limitations

### Alternative 3: PWA with Service Workers

**Rejected because:**

- Limited offline storage (quota issues)
- Less reliable on Android (target platform)
- Harder to implement complex sync

## Implementation Details

```dart
// Outbox pattern implementation
class SyncOutbox {
  Future<void> queueChange(OutboxEntry entry) async {
    await database.outbox.insert(entry);
    _scheduleSyncIfOnline();
  }

  Future<void> processOutbox() async {
    final pending = await database.outbox.getPending();
    for (final entry in pending) {
      try {
        await _syncEntry(entry);
        await database.outbox.markSynced(entry.id);
      } catch (e) {
        await database.outbox.incrementRetry(entry.id);
      }
    }
  }
}
```

## References

- [Offline-First Design Patterns](https://offlinefirst.org/)
- [SAHOOL Sync Architecture](../architecture/SYNC.md)
- [Drift Documentation](https://drift.simonbinder.eu/)
