/// Example: How to integrate Sync Metrics into your app
///
/// This file demonstrates how to set up and use the sync metrics monitoring system.
/// DO NOT import this file directly - it's for reference only.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/storage/database.dart';
import '../../core/sync/sync_metrics_service.dart';
import '../../core/sync/sync_metrics_providers.dart';
import 'ui/sync_metrics_widget.dart';

/// ═══════════════════════════════════════════════════════════════════════════
/// STEP 1: Initialize in main.dart
/// ═══════════════════════════════════════════════════════════════════════════

void mainExample() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize SharedPreferences
  final sharedPreferences = await SharedPreferences.getInstance();

  // Initialize database
  final database = AppDatabase();

  runApp(
    ProviderScope(
      overrides: [
        // Override the providers with actual instances
        sharedPreferencesProvider.overrideWithValue(sharedPreferences),
        databaseProvider.overrideWithValue(database),
        // The syncMetricsServiceProvider will be automatically created
        // from sharedPreferencesProvider
        syncMetricsServiceProvider.overrideWith((ref) {
          return ref.watch(syncMetricsServiceProviderImpl);
        }),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SAHOOL Field App',
      home: const HomeScreen(),
    );
  }
}

/// ═══════════════════════════════════════════════════════════════════════════
/// STEP 2: Display Metrics in Your UI
/// ═══════════════════════════════════════════════════════════════════════════

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('الرئيسية'),
        actions: [
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
          ),
        ],
      ),
      body: Column(
        children: [
          // Compact metrics widget in dashboard
          const SyncMetricsWidget(isCompact: true),
          // ... rest of your home screen content
        ],
      ),
    );
  }
}

/// ═══════════════════════════════════════════════════════════════════════════
/// STEP 3: Full Metrics Screen
/// ═══════════════════════════════════════════════════════════════════════════

class SyncMetricsScreen extends StatelessWidget {
  const SyncMetricsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('إحصائيات المزامنة'),
      ),
      body: const SyncMetricsWidget(
        showDebugInfo: true, // Show debug info in dedicated screen
      ),
    );
  }
}

/// ═══════════════════════════════════════════════════════════════════════════
/// STEP 4: Using Metrics in Your Sync Logic
/// ═══════════════════════════════════════════════════════════════════════════

class ExampleSyncService extends ConsumerWidget {
  const ExampleSyncService({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Get the sync engine with metrics
    final syncEngine = ref.watch(syncEngineWithMetricsProvider);

    return ElevatedButton(
      onPressed: () async {
        // The sync engine will automatically record metrics
        await syncEngine.runOnce();
      },
      child: const Text('تشغيل المزامنة'),
    );
  }
}

/// ═══════════════════════════════════════════════════════════════════════════
/// STEP 5: Monitoring Queue Health
/// ═══════════════════════════════════════════════════════════════════════════

class QueueHealthIndicator extends ConsumerWidget {
  const QueueHealthIndicator({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final metricsAsync = ref.watch(syncMetricsProvider);

    return metricsAsync.when(
      data: (metrics) {
        final queueDepth = metrics.currentQueueDepth;
        final color = queueDepth > 10 ? Colors.red : Colors.green;

        return Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.queue, color: color),
              const SizedBox(width: 8),
              Text(
                '$queueDepth عنصر في قائمة الانتظار',
                style: TextStyle(color: color),
              ),
            ],
          ),
        );
      },
      loading: () => const CircularProgressIndicator(),
      error: (_, __) => const Icon(Icons.error, color: Colors.red),
    );
  }
}

/// ═══════════════════════════════════════════════════════════════════════════
/// STEP 6: Export Metrics for Support
/// ═══════════════════════════════════════════════════════════════════════════

class ExportMetricsButton extends ConsumerWidget {
  const ExportMetricsButton({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final metricsService = ref.watch(syncMetricsServiceProvider);

    return ElevatedButton.icon(
      onPressed: () async {
        // Export metrics as JSON
        final json = metricsService.exportMetricsAsString();

        // You can save to file, share, or send to support
        // Example: Share or save the JSON
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('تصدير الإحصائيات'),
            content: SingleChildScrollView(
              child: SelectableText(json),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('إغلاق'),
              ),
            ],
          ),
        );
      },
      icon: const Icon(Icons.file_download),
      label: const Text('تصدير للدعم الفني'),
    );
  }
}

/// ═══════════════════════════════════════════════════════════════════════════
/// STEP 7: Real-time Metrics Updates
/// ═══════════════════════════════════════════════════════════════════════════

class RealtimeMetricsDisplay extends ConsumerWidget {
  const RealtimeMetricsDisplay({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // This will automatically update when metrics change
    final metricsAsync = ref.watch(syncMetricsProvider);

    return metricsAsync.when(
      data: (metrics) {
        return Card(
          child: ListTile(
            leading: const Icon(Icons.sync),
            title: const Text('حالة المزامنة'),
            subtitle: Text(
              'النجاح: ${(metrics.successRate * 100).toStringAsFixed(1)}%',
            ),
            trailing: Text(
              '${metrics.totalOperations} عملية',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(child: Text('خطأ: $error')),
    );
  }
}

/// ═══════════════════════════════════════════════════════════════════════════
/// STEP 8: Daily Metrics Trend Widget
/// ═══════════════════════════════════════════════════════════════════════════

class DailyMetricsTrendWidget extends ConsumerWidget {
  const DailyMetricsTrendWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dailyMetrics = ref.watch(dailyMetricsProvider);

    if (dailyMetrics.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text('لا توجد بيانات تاريخية بعد'),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'الأيام السبعة الماضية',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...dailyMetrics.map((day) {
              return ListTile(
                title: Text(
                  '${day.date.day}/${day.date.month}/${day.date.year}',
                ),
                subtitle: Text(
                  'عمليات: ${day.totalOperations}, '
                  'نجاح: ${(day.successRate * 100).toStringAsFixed(0)}%',
                ),
                trailing: Icon(
                  day.successRate > 0.9 ? Icons.check_circle : Icons.warning,
                  color: day.successRate > 0.9 ? Colors.green : Colors.orange,
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
}

/// ═══════════════════════════════════════════════════════════════════════════
/// NOTES AND BEST PRACTICES
/// ═══════════════════════════════════════════════════════════════════════════

/*
1. INITIALIZATION:
   - Always initialize SharedPreferences and Database before creating ProviderScope
   - Override the providers in main.dart as shown above

2. AUTOMATIC TRACKING:
   - Once integrated, SyncEngine and QueueManager automatically track metrics
   - No manual tracking needed in most cases

3. PERFORMANCE:
   - Metrics are persisted to SharedPreferences automatically
   - Queue depth is sampled every 30 seconds
   - Operation history is limited to last 100 operations
   - Queue depth history is limited to last 1000 samples

4. DEBUGGING:
   - Use showDebugInfo: true in SyncMetricsWidget for full debug view
   - Export metrics as JSON for support tickets
   - Reset metrics if needed using the debug card

5. UI INTEGRATION:
   - Use isCompact: true for dashboard/home screen
   - Use full widget for dedicated metrics screen
   - Metrics update in real-time via StreamProvider

6. MONITORING BEST PRACTICES:
   - Monitor success rate (should be > 90%)
   - Watch for increasing queue depth (potential sync issues)
   - Check conflict count (high conflicts may indicate data issues)
   - Review retry statistics (high retries indicate network problems)

7. BANDWIDTH TRACKING:
   - Payload sizes are estimated from JSON encoding
   - Actual network usage may be higher due to headers
   - Use for trend analysis, not exact measurements

8. CONFLICT RESOLUTION:
   - Metrics track how conflicts were resolved
   - Review conflict patterns to improve sync logic
   - High manual conflicts may need UX improvements

9. MAINTENANCE:
   - Metrics persist across app restarts
   - Consider periodic cleanup (resetMetrics) in production
   - Export metrics before major app updates

10. TESTING:
    - Use resetMetrics() to clear data between test runs
    - Mock SyncMetricsService for unit tests
    - Test with various network conditions to validate metrics
*/
