/// Sync Metrics Demo - Demonstrates how metrics are recorded
///
/// This file shows how sync operations are tracked and can be used for testing.
/// Run this in a test environment to see metrics in action.

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/sync/sync_metrics_service.dart';
import 'ui/sync_metrics_widget.dart';

/// Demo screen showing how to use sync metrics
class SyncMetricsDemoScreen extends ConsumerStatefulWidget {
  const SyncMetricsDemoScreen({super.key});

  @override
  ConsumerState<SyncMetricsDemoScreen> createState() => _SyncMetricsDemoScreenState();
}

class _SyncMetricsDemoScreenState extends ConsumerState<SyncMetricsDemoScreen> {
  bool _isSimulating = false;

  @override
  Widget build(BuildContext context) {
    final metricsService = ref.watch(syncMetricsServiceProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('عرض توضيحي لإحصائيات المزامنة'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () async {
              await metricsService.resetMetrics();
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('تم إعادة تعيين الإحصائيات')),
                );
              }
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Control Panel
          Card(
            margin: const EdgeInsets.all(16),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'لوحة التحكم',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: _isSimulating ? null : () => _simulateSuccessfulSync(),
                    icon: const Icon(Icons.check_circle),
                    label: const Text('محاكاة مزامنة ناجحة'),
                  ),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: _isSimulating ? null : () => _simulateFailedSync(),
                    icon: const Icon(Icons.error),
                    label: const Text('محاكاة مزامنة فاشلة'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: _isSimulating ? null : () => _simulateConflict(),
                    icon: const Icon(Icons.warning),
                    label: const Text('محاكاة تعارض'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      foregroundColor: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: _isSimulating ? null : () => _simulateMultipleOperations(),
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('محاكاة عمليات متعددة (10)'),
                  ),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: _isSimulating ? null : () => _simulateQueueBuildup(),
                    icon: const Icon(Icons.queue),
                    label: const Text('محاكاة تراكم قائمة الانتظار'),
                  ),
                  if (_isSimulating)
                    const Padding(
                      padding: EdgeInsets.only(top: 16),
                      child: Center(child: CircularProgressIndicator()),
                    ),
                ],
              ),
            ),
          ),

          // Metrics Display
          const Expanded(
            child: SyncMetricsWidget(showDebugInfo: true),
          ),
        ],
      ),
    );
  }

  /// Simulate a successful sync operation
  Future<void> _simulateSuccessfulSync() async {
    setState(() => _isSimulating = true);

    final metricsService = ref.read(syncMetricsServiceProvider);

    // Start operation
    final operationId = metricsService.startSyncOperation(
      type: SyncOperationType.upload,
      entityType: 'task',
      estimatedPayloadSize: 1024,
    );

    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    // Complete successfully
    await metricsService.completeSyncOperation(
      operationId: operationId,
      success: true,
      actualPayloadSize: 1024,
    );

    setState(() => _isSimulating = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ مزامنة ناجحة'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  /// Simulate a failed sync operation
  Future<void> _simulateFailedSync() async {
    setState(() => _isSimulating = true);

    final metricsService = ref.read(syncMetricsServiceProvider);

    final operationId = metricsService.startSyncOperation(
      type: SyncOperationType.upload,
      entityType: 'field',
      estimatedPayloadSize: 2048,
    );

    await Future.delayed(const Duration(milliseconds: 300));

    // Complete with failure
    await metricsService.completeSyncOperation(
      operationId: operationId,
      success: false,
      errorMessage: 'Network timeout',
    );

    // Record retry
    await metricsService.recordRetry(
      operationId: operationId,
      attemptNumber: 1,
      backoffDelay: const Duration(seconds: 2),
    );

    setState(() => _isSimulating = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('❌ فشلت المزامنة'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  /// Simulate a conflict during sync
  Future<void> _simulateConflict() async {
    setState(() => _isSimulating = true);

    final metricsService = ref.read(syncMetricsServiceProvider);

    final operationId = metricsService.startSyncOperation(
      type: SyncOperationType.upload,
      entityType: 'task',
      estimatedPayloadSize: 1536,
    );

    await Future.delayed(const Duration(milliseconds: 400));

    // Complete with conflict
    await metricsService.completeSyncOperation(
      operationId: operationId,
      success: true,
      actualPayloadSize: 1536,
      wasConflict: true,
      conflictResolution: ConflictResolution.serverWins,
    );

    setState(() => _isSimulating = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('⚠️ تم حل التعارض - السيرفر يفوز'),
          backgroundColor: Colors.orange,
        ),
      );
    }
  }

  /// Simulate multiple sync operations
  Future<void> _simulateMultipleOperations() async {
    setState(() => _isSimulating = true);

    final metricsService = ref.read(syncMetricsServiceProvider);

    for (int i = 0; i < 10; i++) {
      final type = i.isEven ? SyncOperationType.upload : SyncOperationType.download;
      final entityType = i % 3 == 0 ? 'task' : 'field';
      final success = i != 5; // Make 6th operation fail

      final operationId = metricsService.startSyncOperation(
        type: type,
        entityType: entityType,
        estimatedPayloadSize: 512 + (i * 100),
      );

      // Random delay
      await Future.delayed(Duration(milliseconds: 100 + (i * 50)));

      await metricsService.completeSyncOperation(
        operationId: operationId,
        success: success,
        actualPayloadSize: 512 + (i * 100),
        errorMessage: success ? null : 'Simulated error',
      );

      // Update queue depth
      await metricsService.updateQueueDepth(10 - i);
    }

    setState(() => _isSimulating = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ اكتملت 10 عمليات (1 فشلت)'),
          backgroundColor: Colors.blue,
        ),
      );
    }
  }

  /// Simulate queue building up and then being processed
  Future<void> _simulateQueueBuildup() async {
    setState(() => _isSimulating = true);

    final metricsService = ref.read(syncMetricsServiceProvider);

    // Build up queue
    for (int i = 0; i < 20; i++) {
      await metricsService.updateQueueDepth(i);
      await Future.delayed(const Duration(milliseconds: 100));
    }

    // Process queue down
    for (int i = 20; i >= 0; i--) {
      await metricsService.updateQueueDepth(i);
      await Future.delayed(const Duration(milliseconds: 100));

      // Simulate some operations
      if (i % 3 == 0) {
        final operationId = metricsService.startSyncOperation(
          type: SyncOperationType.upload,
          entityType: 'task',
          estimatedPayloadSize: 512,
        );

        await Future.delayed(const Duration(milliseconds: 50));

        await metricsService.completeSyncOperation(
          operationId: operationId,
          success: true,
          actualPayloadSize: 512,
        );
      }
    }

    setState(() => _isSimulating = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ محاكاة قائمة الانتظار مكتملة'),
          backgroundColor: Colors.purple,
        ),
      );
    }
  }
}

/// ═══════════════════════════════════════════════════════════════════════════
/// Usage Examples
/// ═══════════════════════════════════════════════════════════════════════════

/*
EXAMPLE 1: Basic Operation Tracking
```dart
final metricsService = ref.read(syncMetricsServiceProvider);

// Start tracking
final opId = metricsService.startSyncOperation(
  type: SyncOperationType.upload,
  entityType: 'task',
  estimatedPayloadSize: 1024,
);

// Do your sync work
final result = await uploadTask(task);

// Complete tracking
await metricsService.completeSyncOperation(
  operationId: opId,
  success: result.success,
  actualPayloadSize: result.payloadSize,
);
```

EXAMPLE 2: Conflict Handling
```dart
final opId = metricsService.startSyncOperation(
  type: SyncOperationType.upload,
  entityType: 'task',
);

try {
  await uploadTask(task);
  await metricsService.completeSyncOperation(
    operationId: opId,
    success: true,
  );
} catch (e) {
  if (e is ConflictException) {
    // Resolve conflict
    final resolution = await resolveConflict(e);

    await metricsService.completeSyncOperation(
      operationId: opId,
      success: true,
      wasConflict: true,
      conflictResolution: resolution,
    );
  } else {
    await metricsService.completeSyncOperation(
      operationId: opId,
      success: false,
      errorMessage: e.toString(),
    );
  }
}
```

EXAMPLE 3: Retry Tracking
```dart
final opId = metricsService.startSyncOperation(
  type: SyncOperationType.upload,
  entityType: 'task',
);

int attempt = 0;
while (attempt < 3) {
  try {
    await uploadTask(task);
    await metricsService.completeSyncOperation(
      operationId: opId,
      success: true,
    );
    break;
  } catch (e) {
    attempt++;
    if (attempt < 3) {
      final backoff = Duration(seconds: 1 << attempt);
      await metricsService.recordRetry(
        operationId: opId,
        attemptNumber: attempt,
        backoffDelay: backoff,
      );
      await Future.delayed(backoff);
    } else {
      await metricsService.completeSyncOperation(
        operationId: opId,
        success: false,
        errorMessage: e.toString(),
      );
    }
  }
}
```

EXAMPLE 4: Queue Depth Monitoring
```dart
// Update queue depth periodically
Timer.periodic(Duration(seconds: 30), (timer) async {
  final queueDepth = await getQueueDepth();
  await metricsService.updateQueueDepth(queueDepth);
});
```

EXAMPLE 5: Export for Debugging
```dart
// Export all metrics as JSON
final json = metricsService.exportMetricsAsString();
print(json);

// Or save to file
final file = File('sync_metrics.json');
await file.writeAsString(json);

// Or share with support
Share.share(json);
```
*/
