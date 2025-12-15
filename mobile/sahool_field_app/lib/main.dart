import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/sync/sync_engine.dart';
import 'core/sync/background_sync_task.dart';
import 'core/storage/database.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize database
  final database = AppDatabase();

  // Initialize sync engine
  final syncEngine = SyncEngine(database: database);

  // Initialize background sync with Workmanager
  await BackgroundSyncManager.initialize();
  await BackgroundSyncManager.registerPeriodicSync();

  runApp(
    ProviderScope(
      overrides: [
        databaseProvider.overrideWithValue(database),
        syncEngineProvider.overrideWithValue(syncEngine),
      ],
      child: const SahoolFieldApp(),
    ),
  );

  // Start foreground sync when app is active
  syncEngine.startPeriodic();
}

// Global providers
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('Database not initialized');
});

final syncEngineProvider = Provider<SyncEngine>((ref) {
  throw UnimplementedError('SyncEngine not initialized');
});
