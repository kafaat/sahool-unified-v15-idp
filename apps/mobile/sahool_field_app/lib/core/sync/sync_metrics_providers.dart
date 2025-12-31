import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'sync_metrics_service.dart';
import '../storage/database.dart';
import 'sync_engine.dart';
import 'queue_manager.dart';

/// Initialize SharedPreferences for metrics service
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError(
    'sharedPreferencesProvider must be overridden in main.dart with actual SharedPreferences instance',
  );
});

/// Provide SyncMetricsService instance
final syncMetricsServiceProviderImpl = Provider<SyncMetricsService>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return SyncMetricsService(prefs);
});

/// Provide SyncEngine with metrics integration
final syncEngineWithMetricsProvider = Provider<SyncEngine>((ref) {
  final database = ref.watch(databaseProvider);
  final metricsService = ref.watch(syncMetricsServiceProviderImpl);

  return SyncEngine(
    database: database,
    metricsService: metricsService,
  );
});

/// Provide QueueManager with metrics integration
final queueManagerWithMetricsProvider = Provider<QueueManager>((ref) {
  final database = ref.watch(databaseProvider);
  final metricsService = ref.watch(syncMetricsServiceProviderImpl);

  return QueueManager(
    database: database,
    metricsService: metricsService,
  );
});

/// Database provider (must be overridden in app)
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError(
    'databaseProvider must be overridden in main.dart with actual AppDatabase instance',
  );
});
