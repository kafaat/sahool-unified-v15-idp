import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../storage/database.dart';
import '../../features/field/data/repo/fields_repo.dart';
import '../../features/field/data/remote/fields_api.dart';
import '../sync/network_status.dart';
import '../http/api_client.dart';
import '../security/signing_key_service.dart';

// Re-export database provider from main.dart
// Note: databaseProvider is defined in main.dart and overridden at runtime

/// API Client Provider
/// Automatically configures certificate pinning and request signing based on build mode:
/// - Debug builds: Certificate pinning disabled (for local development)
/// - Release builds: Certificate pinning and request signing enabled (for production security)
final apiClientProvider = Provider<ApiClient>((ref) {
  final signingKeyService = ref.watch(signingKeyServiceProvider);
  return ApiClient(
    signingKeyService: signingKeyService,
    enableRequestSigning: true,
  );
  // Note: ApiClient automatically uses SecurityConfig.fromBuildMode()
  // which enables certificate pinning in release builds
});

/// Fields API Provider
final fieldsApiProvider = Provider<FieldsApi>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return FieldsApi(apiClient);
});

/// Fields Repository Provider
final fieldsRepoProvider = Provider<FieldsRepo>((ref) {
  final db = ref.watch(databaseProvider);
  final api = ref.watch(fieldsApiProvider);
  return FieldsRepo(
    database: db,
    api: api,
  );
});

/// Fields Stream Provider - Live updates from database
final fieldsStreamProvider =
    StreamProvider.family<List<Field>, String>((ref, tenantId) {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.watchAllFields(tenantId);
});

/// All Fields Provider (for current tenant)
final allFieldsProvider =
    FutureProvider.family<List<Field>, String>((ref, tenantId) async {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.getAllFields(tenantId);
});

/// Unsynced Fields Provider
final unsyncedFieldsProvider = FutureProvider<List<Field>>((ref) async {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.getUnsyncedFields();
});

// Import databaseProvider from main.dart
// This is a workaround since we can't export from main.dart
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('Database provider must be overridden in main.dart');
});
