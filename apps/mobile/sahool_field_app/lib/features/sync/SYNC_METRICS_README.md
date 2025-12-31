# Sync Metrics Monitoring System

## Overview

A comprehensive sync metrics monitoring system for the SAHOOL Field App that tracks, persists, and visualizes synchronization performance metrics.

## Features

### 1. Metrics Tracking
- **Total sync operations** (success/failure counts)
- **Average sync duration** (performance monitoring)
- **Bandwidth usage estimates** (payload size tracking)
- **Conflict count and resolution outcomes** (data consistency)
- **Retry statistics** (failure analysis)
- **Queue depth over time** (load monitoring)

### 2. Data Persistence
- Metrics stored in `SharedPreferences`
- Automatic save on every update
- Survives app restarts
- Efficient JSON serialization

### 3. Metrics Aggregation
- **Real-time metrics**: Current state
- **Daily metrics**: Last 7 days aggregated
- **Weekly metrics**: Long-term trends
- **Operation history**: Last 100 operations
- **Queue depth history**: Last 1000 samples

### 4. Export Functionality
- JSON export for debugging
- Copy to clipboard support
- Formatted output for support tickets
- Complete metrics snapshot

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    UI Layer                             │
│  ┌─────────────────────┐  ┌──────────────────────────┐ │
│  │ SyncMetricsWidget   │  │  Compact View / Full View│ │
│  └─────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 Providers Layer                         │
│  ┌─────────────────────┐  ┌──────────────────────────┐ │
│  │ syncMetricsProvider │  │  dailyMetricsProvider    │ │
│  └─────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 Service Layer                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │         SyncMetricsService                       │  │
│  │  - startSyncOperation()                          │  │
│  │  - completeSyncOperation()                       │  │
│  │  - recordRetry()                                 │  │
│  │  - updateQueueDepth()                            │  │
│  │  - exportMetrics()                               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 Persistence Layer                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │           SharedPreferences                      │  │
│  │  - sync_metrics_current                          │  │
│  │  - sync_metrics_daily                            │  │
│  │  - sync_metrics_weekly                           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Integration

### Step 1: Initialize in main.dart

```dart
import 'package:shared_preferences/shared_preferences.dart';
import 'core/sync/sync_metrics_providers.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final sharedPreferences = await SharedPreferences.getInstance();
  final database = AppDatabase();

  runApp(
    ProviderScope(
      overrides: [
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

### Step 2: Use in Your UI

**Compact View (Dashboard)**
```dart
class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const SyncMetricsWidget(isCompact: true),
          // ... other widgets
        ],
      ),
    );
  }
}
```

**Full View (Dedicated Screen)**
```dart
class MetricsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Sync Metrics')),
      body: const SyncMetricsWidget(showDebugInfo: true),
    );
  }
}
```

### Step 3: Automatic Tracking

Once integrated, metrics are automatically tracked by:
- `SyncEngine` - Records upload/download operations
- `QueueManager` - Monitors queue depth every 30 seconds

No manual tracking needed!

## API Reference

### SyncMetricsService

#### Methods

**startSyncOperation()**
```dart
String startSyncOperation({
  required SyncOperationType type,
  required String entityType,
  int? estimatedPayloadSize,
})
```
Starts tracking a sync operation. Returns operation ID.

**completeSyncOperation()**
```dart
Future<void> completeSyncOperation({
  required String operationId,
  required bool success,
  int? actualPayloadSize,
  String? errorMessage,
  bool wasConflict = false,
  ConflictResolution? conflictResolution,
})
```
Completes tracking and records results.

**recordRetry()**
```dart
Future<void> recordRetry({
  required String operationId,
  required int attemptNumber,
  required Duration backoffDelay,
})
```
Records a retry attempt.

**updateQueueDepth()**
```dart
Future<void> updateQueueDepth(int depth)
```
Updates current queue depth for monitoring.

**exportMetrics()**
```dart
Map<String, dynamic> exportMetrics()
String exportMetricsAsString()
```
Exports metrics as JSON for debugging.

**resetMetrics()**
```dart
Future<void> resetMetrics()
```
Clears all metrics (use with caution).

### SyncMetrics Model

```dart
class SyncMetrics {
  final int totalOperations;
  final int successfulOperations;
  final int failedOperations;
  final int totalDuration; // milliseconds
  final int totalBandwidthBytes;
  final int conflictCount;
  final Map<ConflictResolution, int> conflictResolutions;
  final RetryStatistics retryStatistics;
  final List<CompletedOperation> operationHistory;
  final List<QueueDepthSample> queueDepthHistory;

  // Computed properties
  double get successRate;
  double get averageDuration;
  double get averagePayloadSize;
  int get currentQueueDepth;
  double get averageQueueDepth;
  int get peakQueueDepth;
}
```

## UI Components

### SyncMetricsWidget

**Compact Mode**
- Overall health indicator
- Key metrics (operations, success rate, conflicts, queue depth)
- Last sync time
- Suitable for dashboard/home screen

**Full Mode**
- Overall health card
- Performance metrics (duration, bandwidth, queue stats)
- Historical trends chart (7 days)
- Conflict analysis breakdown
- Retry statistics
- Queue depth over time chart
- Recent operations list (last 10)
- Debug information (optional)

### Charts

**Historical Trends**
- Line chart showing daily metrics
- Three lines: total operations, successful, failed
- Last 7 days of data
- Interactive tooltips

**Queue Depth**
- Line chart showing queue depth over time
- Last 100 samples
- Helps identify sync bottlenecks

## Monitoring Best Practices

### Health Indicators

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Success Rate | > 90% | 80-90% | < 80% |
| Queue Depth | < 5 | 5-10 | > 10 |
| Conflicts | < 2/day | 2-5/day | > 5/day |
| Avg Duration | < 2s | 2-5s | > 5s |

### What to Monitor

1. **Success Rate**: Should remain above 90%
   - Low rate indicates network issues or server problems

2. **Queue Depth**: Should stay below 10
   - Rising queue indicates sync falling behind
   - May need to adjust sync frequency

3. **Conflict Count**: Should be minimal
   - High conflicts suggest concurrent editing issues
   - Review conflict resolution strategy

4. **Retry Statistics**: Track retry patterns
   - High retry count indicates unstable network
   - Check retry backoff strategy

5. **Bandwidth Usage**: Monitor data consumption
   - Optimize payload sizes if too high
   - Consider compression for large payloads

## Debugging

### Export Metrics for Support

```dart
final service = ref.watch(syncMetricsServiceProvider);
final json = service.exportMetricsAsString();
// Share or save JSON for support team
```

### Debug Information Includes

- Last sync timestamp
- Active operations count
- Operation history size
- Queue depth samples count
- Full metrics in JSON format

### Reset Metrics

```dart
await service.resetMetrics();
```

**Warning**: This clears all historical data. Use only for testing or maintenance.

## Performance Considerations

### Storage

- Metrics stored in SharedPreferences (lightweight)
- Automatic cleanup of old data:
  - Operation history: Last 100 operations
  - Queue depth: Last 1000 samples
  - Daily metrics: Keep all
  - Weekly metrics: Keep all

### Memory

- Metrics kept in memory for fast access
- Periodic persistence to disk
- Efficient JSON serialization

### Monitoring Overhead

- Queue depth sampled every 30 seconds
- Minimal impact on app performance
- Metrics calculated on-demand

## Troubleshooting

### Problem: Metrics Not Updating

**Solution**: Check provider initialization
```dart
// Ensure providers are properly overridden
ProviderScope(
  overrides: [
    sharedPreferencesProvider.overrideWithValue(prefs),
    // ...
  ],
  // ...
)
```

### Problem: High Memory Usage

**Solution**: Metrics history may be too large
- Check operation history size
- Consider more aggressive cleanup
- Reset metrics if needed

### Problem: Metrics Lost After Restart

**Solution**: Check SharedPreferences initialization
- Ensure prefs initialized before app start
- Check for storage permissions
- Verify JSON serialization works

## Future Enhancements

Potential improvements:
- [ ] Metrics database storage (for larger history)
- [ ] Advanced analytics (percentiles, distributions)
- [ ] Alerts/notifications for critical issues
- [ ] Network quality correlation
- [ ] Battery impact tracking
- [ ] Scheduled reports
- [ ] Cloud backup of metrics

## Related Files

- `lib/core/sync/sync_metrics_service.dart` - Core service
- `lib/core/sync/sync_metrics_providers.dart` - Riverpod providers
- `lib/features/sync/ui/sync_metrics_widget.dart` - UI components
- `lib/features/sync/sync_metrics_example.dart` - Integration examples
- `lib/core/sync/sync_engine.dart` - Integrated sync engine
- `lib/core/sync/queue_manager.dart` - Integrated queue manager

## Support

For issues or questions:
1. Check this documentation
2. Review example integration code
3. Export metrics JSON for debugging
4. Check operation history for patterns
5. Contact development team with metrics export

---

**Version**: 1.0.0
**Last Updated**: 2025-12-30
**Status**: Production Ready
