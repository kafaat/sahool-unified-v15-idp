import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../storage/database.dart';
import '../sync/sync_engine.dart';

/// Single source of truth for the database provider.
/// Defined here so both main.dart and providers.dart import the same instance,
/// ensuring the ProviderScope override in main.dart takes effect everywhere.
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('Database not initialized — override in ProviderScope');
});

final syncEngineProvider = Provider<SyncEngine>((ref) {
  throw UnimplementedError('SyncEngine not initialized — override in ProviderScope');
});
