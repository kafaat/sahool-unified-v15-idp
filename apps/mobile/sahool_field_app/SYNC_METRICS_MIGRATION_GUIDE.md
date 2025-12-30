# Sync Metrics Migration Guide

## Overview
This guide helps you integrate the new sync metrics monitoring system into your existing SAHOOL Field App.

## Prerequisites

Ensure you have these dependencies in `pubspec.yaml` (already present):
```yaml
dependencies:
  shared_preferences: ^2.3.3
  flutter_riverpod: ^2.6.1
  fl_chart: ^0.69.2
  intl: ^0.19.0
```

## Migration Steps

### Step 1: Update main.dart (5 minutes)

**Before:**
```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final database = AppDatabase();

  runApp(
    ProviderScope(
      child: const MyApp(),
    ),
  );
}
```

**After:**
```dart
import 'package:shared_preferences/shared_preferences.dart';
import 'core/sync/sync_metrics_providers.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize SharedPreferences for metrics
  final sharedPreferences = await SharedPreferences.getInstance();
  final database = AppDatabase();

  runApp(
    ProviderScope(
      overrides: [
        // Override providers with actual instances
        sharedPreferencesProvider.overrideWithValue(sharedPreferences),
        databaseProvider.overrideWithValue(database),
        syncMetricsServiceProvider.overrideWith((ref) {
          return ref.watch(syncMetricsServiceProviderImpl);
        }),
      ],
      child: const MyApp(),
    ),
  );
}
```

### Step 2: Update SyncEngine Initialization (2 minutes)

**Before:**
```dart
final syncEngine = SyncEngine(database: database);
```

**After:**
```dart
// Option A: Use the provider (recommended)
final syncEngine = ref.watch(syncEngineWithMetricsProvider);

// Option B: Manual initialization
final metricsService = ref.watch(syncMetricsServiceProvider);
final syncEngine = SyncEngine(
  database: database,
  metricsService: metricsService,
);
```

### Step 3: Update QueueManager Initialization (2 minutes)

**Before:**
```dart
final queueManager = QueueManager(database: database);
```

**After:**
```dart
// Option A: Use the provider (recommended)
final queueManager = ref.watch(queueManagerWithMetricsProvider);

// Option B: Manual initialization
final metricsService = ref.watch(syncMetricsServiceProvider);
final queueManager = QueueManager(
  database: database,
  metricsService: metricsService,
);
```

### Step 4: Add Metrics Widget to UI (10 minutes)

#### Option A: Compact View in Dashboard

Add to your home screen:
```dart
import 'features/sync/ui/sync_metrics_widget.dart';

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Add compact metrics widget
          const SyncMetricsWidget(isCompact: true),

          // Your existing widgets
          // ...
        ],
      ),
    );
  }
}
```

#### Option B: Full Metrics Screen

Create a new screen:
```dart
import 'package:flutter/material.dart';
import 'features/sync/ui/sync_metrics_widget.dart';

class SyncMetricsScreen extends StatelessWidget {
  const SyncMetricsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('إحصائيات المزامنة'),
      ),
      body: const SyncMetricsWidget(
        showDebugInfo: true,
      ),
    );
  }
}
```

Add navigation to this screen:
```dart
// In your settings or sync screen
IconButton(
  icon: const Icon(Icons.analytics),
  onPressed: () {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const SyncMetricsScreen(),
      ),
    );
  },
)
```

### Step 5: Test the Integration (15 minutes)

1. **Run the app**:
```bash
cd /apps/mobile/sahool_field_app
flutter run
```

2. **Verify metrics are tracking**:
   - Perform a sync operation
   - Check the metrics widget
   - Should see operation count increase

3. **Test persistence**:
   - Restart the app
   - Metrics should be retained

4. **Use the demo screen** (optional):
```dart
// Add to your debug menu or settings
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => const SyncMetricsDemoScreen(),
  ),
);
```

## Verification Checklist

- [ ] SharedPreferences initialized in main.dart
- [ ] Providers overridden in ProviderScope
- [ ] SyncEngine uses metricsService parameter
- [ ] QueueManager uses metricsService parameter
- [ ] Metrics widget displays in UI
- [ ] Sync operations increment metrics
- [ ] Metrics persist across app restarts
- [ ] Charts display historical data
- [ ] Export functionality works
- [ ] No compilation errors
- [ ] No runtime errors

## Common Issues & Solutions

### Issue 1: Provider Not Found Error

**Error:**
```
ProviderNotFoundException: Error: Could not find the correct Provider<SyncMetricsService>
```

**Solution:**
Ensure you've overridden the provider in main.dart:
```dart
syncMetricsServiceProvider.overrideWith((ref) {
  return ref.watch(syncMetricsServiceProviderImpl);
}),
```

### Issue 2: Metrics Not Updating

**Error:** Metrics widget shows zeros or doesn't update

**Solution:**
1. Check that SyncEngine has metricsService parameter set
2. Verify sync operations are actually running
3. Check for null metricsService (it's optional, should handle null safely)

### Issue 3: SharedPreferences Error

**Error:**
```
MissingPluginException(No implementation found for method getAll)
```

**Solution:**
Ensure SharedPreferences is initialized before creating ProviderScope:
```dart
final sharedPreferences = await SharedPreferences.getInstance();
```

### Issue 4: Charts Not Displaying

**Error:** Empty space where charts should be

**Solution:**
1. Ensure daily metrics have data (run some sync operations)
2. Check that fl_chart dependency is installed
3. Try running demo to populate data

## Rollback Plan

If you need to rollback the changes:

1. **Remove provider overrides** from main.dart:
```dart
runApp(
  ProviderScope(
    child: const MyApp(),
  ),
);
```

2. **Remove metricsService** from SyncEngine:
```dart
final syncEngine = SyncEngine(database: database);
```

3. **Remove metricsService** from QueueManager:
```dart
final queueManager = QueueManager(database: database);
```

4. **Remove metrics widgets** from UI

The existing sync functionality will continue to work without metrics.

## Performance Impact

Expected impact after migration:

| Metric | Impact | Notes |
|--------|--------|-------|
| App Size | +80KB | New code added |
| Memory | +100KB | Metrics in memory |
| Storage | +50-100KB | SharedPreferences data |
| Startup Time | +50-100ms | Load metrics from storage |
| Battery | Negligible | Queue check every 30s |
| Network | None | All local processing |

## Post-Migration

### Recommended Next Steps

1. **Monitor for a week**:
   - Watch for any performance issues
   - Verify metrics are accurate
   - Check storage usage

2. **Customize UI**:
   - Adjust colors to match your theme
   - Modify Arabic translations if needed
   - Add/remove metrics as needed

3. **Set up alerts** (optional):
   - Add notifications for critical metrics
   - Email reports for support team

4. **Training**:
   - Show team how to use metrics screen
   - Explain export functionality for support
   - Document troubleshooting procedures

### Health Monitoring

After migration, monitor these metrics:

1. **Success Rate**: Should be > 90%
   - If lower, investigate network issues

2. **Queue Depth**: Should stay < 10
   - If higher, sync frequency may need adjustment

3. **Conflicts**: Should be < 2 per day
   - If higher, review concurrent editing patterns

4. **Retry Count**: Should be low
   - If high, check network stability

## Support

If you encounter issues during migration:

1. **Check the documentation**:
   - `/lib/features/sync/SYNC_METRICS_README.md`
   - `/lib/features/sync/sync_metrics_example.dart`

2. **Run the demo**:
   - `/lib/features/sync/sync_metrics_demo.dart`
   - Verify metrics work in isolation

3. **Export metrics**:
   - Use export functionality to capture current state
   - Share with development team

4. **Check logs**:
   - Look for errors related to SharedPreferences
   - Verify sync operations are completing

## Timeline

Estimated migration time:

| Task | Time | Difficulty |
|------|------|------------|
| Update main.dart | 5 min | Easy |
| Update SyncEngine | 2 min | Easy |
| Update QueueManager | 2 min | Easy |
| Add UI widgets | 10 min | Easy |
| Testing | 15 min | Easy |
| **Total** | **~35 min** | **Easy** |

## Success Criteria

Migration is successful when:

✅ App compiles without errors
✅ App runs without crashes
✅ Metrics widget displays
✅ Sync operations increment metrics
✅ Metrics persist across restarts
✅ Charts display (after some sync operations)
✅ Export functionality works
✅ No performance degradation

---

**Migration Difficulty**: ⭐ Easy (Beginner-friendly)
**Estimated Time**: 35 minutes
**Risk Level**: Low (backwards compatible)
**Rollback Difficulty**: Very Easy

**Last Updated**: 2025-12-30
