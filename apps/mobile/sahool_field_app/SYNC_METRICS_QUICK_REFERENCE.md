# Sync Metrics Quick Reference Card

## Quick Setup (Copy & Paste)

### 1. main.dart
```dart
import 'package:shared_preferences/shared_preferences.dart';
import 'core/sync/sync_metrics_providers.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final database = AppDatabase();

  runApp(
    ProviderScope(
      overrides: [
        sharedPreferencesProvider.overrideWithValue(prefs),
        databaseProvider.overrideWithValue(database),
        syncMetricsServiceProvider.overrideWith((ref) =>
          ref.watch(syncMetricsServiceProviderImpl)),
      ],
      child: const MyApp(),
    ),
  );
}
```

### 2. Compact Widget (Dashboard)
```dart
import 'features/sync/ui/sync_metrics_widget.dart';

const SyncMetricsWidget(isCompact: true)
```

### 3. Full Screen (Dedicated Page)
```dart
import 'features/sync/ui/sync_metrics_widget.dart';

Scaffold(
  appBar: AppBar(title: const Text('Metrics')),
  body: const SyncMetricsWidget(showDebugInfo: true),
)
```

## Key Metrics At-a-Glance

| Metric | Formula | Good | Warning | Bad |
|--------|---------|------|---------|-----|
| **Success Rate** | successful / total | >90% | 80-90% | <80% |
| **Queue Depth** | pending items | <5 | 5-10 | >10 |
| **Avg Duration** | total ms / count | <2s | 2-5s | >5s |
| **Conflicts/Day** | daily conflicts | <2 | 2-5 | >5 |

## Common Code Snippets

### Track Manual Sync Operation
```dart
final service = ref.watch(syncMetricsServiceProvider);

final opId = service.startSyncOperation(
  type: SyncOperationType.upload,
  entityType: 'task',
  estimatedPayloadSize: 1024,
);

// ... do sync work ...

await service.completeSyncOperation(
  operationId: opId,
  success: true,
  actualPayloadSize: 1024,
);
```

### Track with Conflict
```dart
await service.completeSyncOperation(
  operationId: opId,
  success: true,
  wasConflict: true,
  conflictResolution: ConflictResolution.serverWins,
);
```

### Track with Retry
```dart
await service.recordRetry(
  operationId: opId,
  attemptNumber: 2,
  backoffDelay: Duration(seconds: 4),
);
```

### Export for Debugging
```dart
final json = service.exportMetricsAsString();
Clipboard.setData(ClipboardData(text: json));
```

### Reset Metrics
```dart
await service.resetMetrics();
```

## Widget Modes

### Compact Mode (Small Space)
```dart
SyncMetricsWidget(isCompact: true)
```
Shows: Health badge, 4 key metrics, last sync time

### Full Mode (Dedicated Screen)
```dart
SyncMetricsWidget(showDebugInfo: false)
```
Shows: All cards except debug info

### Debug Mode (For Developers)
```dart
SyncMetricsWidget(showDebugInfo: true)
```
Shows: Everything including debug card with export/reset

## File Locations

```
lib/
├── core/sync/
│   ├── sync_metrics_service.dart     ← Core service
│   ├── sync_metrics_providers.dart   ← Providers
│   ├── sync_engine.dart              ← (Updated)
│   └── queue_manager.dart            ← (Updated)
│
└── features/sync/
    ├── ui/
    │   └── sync_metrics_widget.dart  ← UI widget
    ├── sync_metrics_example.dart     ← Examples
    ├── sync_metrics_demo.dart        ← Demo/testing
    └── SYNC_METRICS_README.md        ← Full docs
```

## Data Models Quick Ref

### SyncMetrics
```dart
.totalOperations        // int
.successfulOperations   // int
.failedOperations       // int
.successRate            // double (0.0-1.0)
.averageDuration        // double (ms)
.averagePayloadSize     // double (bytes)
.conflictCount          // int
.currentQueueDepth      // int
.averageQueueDepth      // double
.peakQueueDepth         // int
.lastSyncTime           // DateTime?
```

### DailyMetrics
```dart
.date                   // DateTime
.totalOperations        // int
.successfulOperations   // int
.failedOperations       // int
.successRate            // double
.averageDuration        // double
.totalBandwidthBytes    // int
```

## Providers Quick Ref

```dart
// Main service
ref.watch(syncMetricsServiceProvider)

// Real-time stream
ref.watch(syncMetricsProvider)  // AsyncValue<SyncMetrics>

// Current snapshot
ref.watch(currentSyncMetricsProvider)  // SyncMetrics

// Last 7 days
ref.watch(dailyMetricsProvider)  // List<DailyMetrics>

// Integrated sync engine
ref.watch(syncEngineWithMetricsProvider)

// Integrated queue manager
ref.watch(queueManagerWithMetricsProvider)
```

## Enums Quick Ref

### SyncOperationType
- `upload` - Uploading to server
- `download` - Downloading from server
- `conflict` - Conflict resolution

### ConflictResolution
- `serverWins` - Server version kept
- `localWins` - Local version kept
- `merged` - Data merged
- `manual` - User resolved manually

## Troubleshooting Quick Fixes

### Provider Error
```dart
// Ensure in main.dart:
syncMetricsServiceProvider.overrideWith((ref) =>
  ref.watch(syncMetricsServiceProviderImpl)),
```

### Metrics Not Updating
```dart
// Check SyncEngine has metrics:
SyncEngine(
  database: database,
  metricsService: metricsService,  // ← Must be set
)
```

### Charts Empty
```dart
// Run some syncs first, then:
Navigator.push(context, MaterialPageRoute(
  builder: (_) => const SyncMetricsDemoScreen(),
));
```

### Export Not Working
```dart
// Must add permission for clipboard:
import 'package:flutter/services.dart';
Clipboard.setData(ClipboardData(text: json));
```

## Performance Tips

✅ **DO**:
- Use compact mode in dashboards
- Export metrics before major updates
- Monitor success rate weekly
- Reset metrics after testing

❌ **DON'T**:
- Show full mode in small spaces
- Keep debug mode on in production
- Ignore declining success rates
- Export metrics constantly (CPU cost)

## Health Check Commands

```dart
// Get current metrics
final metrics = ref.watch(currentSyncMetricsProvider);

// Check health
if (metrics.successRate < 0.9) {
  print('⚠️ Low success rate');
}
if (metrics.currentQueueDepth > 10) {
  print('⚠️ High queue depth');
}
if (metrics.conflictCount > 5) {
  print('⚠️ Many conflicts');
}
```

## Testing Commands

```dart
// 1. Simulate successful sync
final opId = service.startSyncOperation(
  type: SyncOperationType.upload,
  entityType: 'test',
);
await Future.delayed(Duration(milliseconds: 100));
await service.completeSyncOperation(
  operationId: opId,
  success: true,
);

// 2. Check metrics updated
final metrics = ref.read(currentSyncMetricsProvider);
assert(metrics.totalOperations > 0);
```

## API Method Summary

| Method | Purpose | Returns |
|--------|---------|---------|
| `startSyncOperation()` | Begin tracking | String (opId) |
| `completeSyncOperation()` | End tracking | Future<void> |
| `recordRetry()` | Log retry attempt | Future<void> |
| `updateQueueDepth()` | Update queue size | Future<void> |
| `exportMetrics()` | Get JSON data | Map<String, dynamic> |
| `exportMetricsAsString()` | Get formatted JSON | String |
| `resetMetrics()` | Clear all data | Future<void> |
| `getLastNDays()` | Get daily metrics | List<DailyMetrics> |
| `getDailyMetrics()` | Get specific day | DailyMetrics? |
| `getWeeklyMetrics()` | Get specific week | WeeklyMetrics? |

## Storage Keys

SharedPreferences keys used:
- `sync_metrics_current` - Current metrics
- `sync_metrics_daily` - Daily aggregates
- `sync_metrics_weekly` - Weekly aggregates

## Demo Screen Access

```dart
// For testing/debugging
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => const SyncMetricsDemoScreen(),
  ),
);
```

Provides:
- ✅ Simulate successful sync
- ❌ Simulate failed sync
- ⚠️ Simulate conflict
- 🔄 Simulate 10 operations
- 📊 Simulate queue buildup

## Chart Configuration

### Historical Trends Chart
- **Type**: Line chart
- **Lines**: 3 (total, success, failed)
- **Period**: Last 7 days
- **Colors**: Blue, Green, Red

### Queue Depth Chart
- **Type**: Line chart
- **Lines**: 1 (queue depth)
- **Samples**: Last 100
- **Color**: Purple

## Arabic Translations

| English | Arabic |
|---------|--------|
| Sync Status | حالة المزامنة |
| Operations | العمليات |
| Success | النجاح |
| Conflicts | التعارضات |
| Queue | قيد الانتظار |
| Last sync | آخر مزامنة |
| Healthy | صحي |
| Warning | تحذير |
| Needs attention | يحتاج انتباه |

## Quick Calculations

```dart
// Success percentage
(successful / total * 100).toStringAsFixed(1) + '%'

// Duration in seconds
(durationMs / 1000).toStringAsFixed(2) + 's'

// Bytes formatted
if (bytes < 1024) '$bytes B'
else if (bytes < 1024*1024) '${bytes/1024:0.2f} KB'
else '${bytes/(1024*1024):0.2f} MB'
```

## Memory Limits

| Data | Limit | Cleanup |
|------|-------|---------|
| Operation History | 100 ops | Auto (FIFO) |
| Queue Samples | 1000 samples | Auto (FIFO) |
| Daily Metrics | Unlimited | Manual |
| Weekly Metrics | Unlimited | Manual |

---

**Quick Ref Version**: 1.0.0
**Print This**: For easy desk reference
**Last Updated**: 2025-12-30
