# Sync Status Widgets Documentation

## Overview

This module provides comprehensive sync status UI components for the Sahool Field App. The widgets are designed to give users clear, real-time feedback about their data synchronization status.

## Architecture

```
features/sync/
├── widgets/
│   ├── sync_status_indicator.dart    # Main status indicator with 4 styles
│   ├── sync_status_banner.dart       # Full-width banners for alerts
│   └── sync_widgets.dart              # Export file
├── screens/
│   └── sync_details_screen.dart      # Detailed sync history & management
└── providers/
    └── sync_events_provider.dart     # Enhanced with additional providers
```

## Components

### 1. SyncStatusIndicator

A versatile widget that displays sync status with multiple style options.

#### Styles Available:

- **Compact**: Small pill-shaped indicator for app bars
- **Expanded**: Medium card with detailed info
- **Minimal**: Just an icon with badge
- **Detailed**: Full information card

#### Usage:

```dart
// Compact style (default)
SyncStatusIndicator(
  style: SyncIndicatorStyle.compact,
  onTap: () => context.push('/sync-details'),
  showLastSyncTime: true,
  showPendingCount: true,
)

// Expanded style
SyncStatusIndicator(
  style: SyncIndicatorStyle.expanded,
  onTap: () => context.push('/sync-details'),
)

// Minimal style (for app bar)
SyncStatusIndicator(
  style: SyncIndicatorStyle.minimal,
)

// Detailed style (for dashboard)
SyncStatusIndicator(
  style: SyncIndicatorStyle.detailed,
  onTap: () => context.push('/sync-details'),
)
```

#### Features:

- ✅ Animated sync icon when syncing
- ✅ Color-coded status (green=synced, blue=syncing, red=offline, yellow=conflicts)
- ✅ Pending items count badge
- ✅ Last sync time display
- ✅ Conflict indicators
- ✅ Automatic state updates via Riverpod

### 2. SyncStatusBanner

Full-width banners for important sync notifications.

#### Banner Types:

- **Offline Mode**: Shows when device is offline
- **Error**: Displays sync errors
- **Conflicts**: Alerts about data conflicts
- **Warning**: General warnings

#### Usage:

```dart
// Static banner (always visible when conditions met)
SyncStatusBanner(
  onRetryTap: () => ref.read(syncStatusProvider.notifier).syncNow(),
  onDismiss: () => setState(() => dismissed = true),
  dismissible: true,
)

// Animated banner (slides in/out)
AnimatedSyncStatusBanner(
  onRetryTap: () async {
    await ref.read(syncStatusProvider.notifier).syncNow();
  },
  dismissible: true,
)

// Floating banner (Snackbar-style)
FloatingSyncStatusBanner.showOffline(
  context,
  onRetry: () => ref.read(syncStatusProvider.notifier).syncNow(),
)

FloatingSyncStatusBanner.showSuccess(
  context,
  message: 'تمت المزامنة بنجاح',
)

FloatingSyncStatusBanner.showError(
  context,
  'فشل في المزامنة',
  onRetry: () => handleRetry(),
)
```

#### Features:

- ✅ Auto-detection of sync state
- ✅ Priority-based display (offline > error > conflicts)
- ✅ Retry action button
- ✅ Dismissible banners
- ✅ Smooth animations
- ✅ Multiple presentation styles

### 3. SyncDetailsScreen

A comprehensive screen for viewing sync history and managing pending items.

#### Features:

- ✅ Three tabs: Status, Pending Items, History
- ✅ Quick statistics dashboard
- ✅ Recent events display
- ✅ Pending items list with priority indicators
- ✅ Full sync log history
- ✅ Manual sync trigger
- ✅ Quick actions (retry failed, cleanup)
- ✅ Pull-to-refresh support

#### Usage:

```dart
// Navigate to sync details
context.push('/sync-details')

// Or use GoRouter configuration
GoRoute(
  path: '/sync-details',
  builder: (context, state) => const SyncDetailsScreen(),
)
```

#### Tab Contents:

**Status Tab:**
- Main sync status indicator
- Quick statistics cards
- Recent events
- Quick actions

**Pending Items Tab:**
- List of all pending items
- Priority badges
- Method indicators (POST/PUT/DELETE)
- Retry count for failed items

**History Tab:**
- Full sync log history
- Success/error indicators
- Timestamps
- Detailed messages

## Providers

### Enhanced Providers (sync_events_provider.dart)

```dart
// Existing providers:
syncStatusProvider          // Main sync status state
syncEventsProvider          // Sync events (conflicts, etc.)
queueManagerProvider        // Queue management
isSyncingProvider          // Boolean: is currently syncing
pendingItemsCountProvider  // Count of pending items
syncHealthProvider         // Queue health status

// New enhanced providers:
lastSyncTimeProvider       // DateTime? of last successful sync
isFullySyncedProvider      // Boolean: fully synced with no pending items
syncErrorProvider          // String? of last error message
networkStatusProvider      // Boolean: online/offline status
manualSyncTriggerProvider  // Function to trigger manual sync
```

### Provider Usage Examples:

```dart
// Watch sync status
final syncStatus = ref.watch(syncStatusProvider);
print('Pending: ${syncStatus.pendingCount}');
print('Is syncing: ${syncStatus.isSyncing}');
print('Is online: ${syncStatus.isOnline}');

// Trigger manual sync
final result = await ref.read(manualSyncTriggerProvider)();
if (result.success) {
  print('Synced: ${result.uploaded} uploaded, ${result.downloaded} downloaded');
}

// Check if fully synced
final isFullySynced = ref.watch(isFullySyncedProvider);

// Get last sync time
final lastSync = ref.watch(lastSyncTimeProvider);

// Get current error
final error = ref.watch(syncErrorProvider);

// Get conflicts count
final conflictsCount = ref.watch(unreadConflictsCountProvider);
```

## Integration Examples

### App Bar Integration

```dart
AppBar(
  title: const Text('الحقول'),
  actions: [
    // Minimal sync indicator
    Padding(
      padding: const EdgeInsets.only(left: 16),
      child: SyncStatusIndicator(
        style: SyncIndicatorStyle.minimal,
        onTap: () => context.push('/sync-details'),
      ),
    ),
  ],
)
```

### Dashboard Integration

```dart
// Home screen dashboard
Column(
  children: [
    // Banner at top (auto-shows when needed)
    const AnimatedSyncStatusBanner(),

    // Main content
    Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Detailed sync status card
          SyncStatusIndicator(
            style: SyncIndicatorStyle.detailed,
            onTap: () => context.push('/sync-details'),
          ),

          const SizedBox(height: 20),

          // Rest of dashboard...
        ],
      ),
    ),
  ],
)
```

### Form Integration

```dart
// In a form screen, show sync status during save
ElevatedButton(
  onPressed: () async {
    // Save form
    await saveForm();

    // Show sync feedback
    FloatingSyncStatusBanner.showSyncing(context);

    // Trigger sync
    final result = await ref.read(manualSyncTriggerProvider)();

    if (result.success) {
      FloatingSyncStatusBanner.showSuccess(context);
    } else {
      FloatingSyncStatusBanner.showError(
        context,
        result.message ?? 'فشل في المزامنة',
        onRetry: () => ref.read(manualSyncTriggerProvider)(),
      );
    }
  },
  child: const Text('حفظ'),
)
```

### List Screen Integration

```dart
Scaffold(
  appBar: AppBar(
    title: const Text('الحقول'),
    bottom: PreferredSize(
      preferredSize: const Size.fromHeight(60),
      child: SyncStatusIndicator(
        style: SyncIndicatorStyle.expanded,
        onTap: () => context.push('/sync-details'),
      ),
    ),
  ),
  body: RefreshIndicator(
    onRefresh: () async {
      await ref.read(manualSyncTriggerProvider)();
    },
    child: ListView(...),
  ),
)
```

## State Flow

```
┌─────────────────┐
│  Network Status │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│  Sync Engine    │────▶│ Queue Manager│
└────────┬────────┘     └──────┬───────┘
         │                      │
         ▼                      ▼
┌─────────────────┐     ┌──────────────┐
│ Sync Events     │     │ Queue Stats  │
└────────┬────────┘     └──────┬───────┘
         │                      │
         └──────────┬───────────┘
                    ▼
         ┌─────────────────────┐
         │ syncStatusProvider  │
         └──────────┬──────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Status Widgets  │   │ Status Banners  │
└─────────────────┘   └─────────────────┘
```

## Styling & Theming

All widgets use the Sahool Design System:

- **Colors**: `SahoolColors.*` (primary, success, danger, warning, info)
- **Shadows**: `SahoolShadows.*` (small, medium, large)
- **Radius**: `SahoolRadius.*` (small, medium, large)
- **Spacing**: `SahoolSpacing.*` (xs, sm, md, lg, xl)

## Best Practices

1. **Always use Riverpod providers** - Don't pass sync state manually
2. **Use appropriate style** - Minimal for app bars, Detailed for dashboards
3. **Show banners sparingly** - Only for important states (offline, errors)
4. **Provide retry actions** - Always give users a way to retry failed syncs
5. **Use animations** - AnimatedSyncStatusBanner for better UX
6. **Handle errors gracefully** - Show clear error messages with retry options

## Accessibility

- All icons have semantic labels
- Color-coding is supplemented with icons and text
- Touch targets meet minimum size requirements (44x44)
- RTL support for Arabic text

## Testing

```dart
// Widget tests
testWidgets('SyncStatusIndicator shows offline state', (tester) async {
  // Setup offline state in provider
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        syncStatusProvider.overrideWith((ref) => SyncStatusState(isOnline: false)),
      ],
      child: MaterialApp(
        home: SyncStatusIndicator(),
      ),
    ),
  );

  expect(find.text('غير متصل'), findsOneWidget);
  expect(find.byIcon(Icons.cloud_off), findsOneWidget);
});
```

## Troubleshooting

**Widget not updating:**
- Ensure you're using `ConsumerWidget` or `Consumer`
- Check that providers are properly watched with `ref.watch()`

**Sync not triggering:**
- Verify network connectivity
- Check queue manager for pending items
- Review sync logs in SyncDetailsScreen

**Banners not showing:**
- Check sync status state
- Verify banner conditions (offline, errors, etc.)
- Ensure AnimatedSyncStatusBanner is in widget tree

## Future Enhancements

- [ ] Sync progress percentage
- [ ] Detailed conflict resolution UI
- [ ] Sync scheduling controls
- [ ] Export sync logs
- [ ] Sync statistics charts
- [ ] Batch operations UI

---

**Created**: 2025-12-30
**Version**: 1.0.0
**Maintainer**: Sahool Development Team
