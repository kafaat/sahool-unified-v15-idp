import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/sync/sync_engine.dart';
import 'core/storage/database.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize database
  final database = AppDatabase();

  // Initialize sync engine
  final syncEngine = SyncEngine(database: database);

  runApp(
    ProviderScope(
      overrides: [
        databaseProvider.overrideWithValue(database),
        syncEngineProvider.overrideWithValue(syncEngine),
      ],
      child: const SahoolFieldApp(),
    ),
  );

  // Start background sync
  syncEngine.startPeriodic();
}

// Global providers
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('Database not initialized');
});

final syncEngineProvider = Provider<SyncEngine>((ref) {
  throw UnimplementedError('SyncEngine not initialized');
});
