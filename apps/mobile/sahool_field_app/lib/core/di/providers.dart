import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/field/data/repo/fields_repo.dart';
import '../../features/field/data/remote/fields_api.dart';
import '../../features/field/domain/entities/field.dart' as domain;
import '../http/api_client.dart';
import '../security/signing_key_service.dart';

// Import canonical databaseProvider from main.dart
// This is overridden at runtime with the actual database instance
import '../../main.dart' show databaseProvider;
export '../../main.dart' show databaseProvider;

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
/// Exposes domain.Field entities for UI consumption
final fieldsStreamProvider =
    StreamProvider.family<List<domain.Field>, String>((ref, tenantId) {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.watchAllFields(tenantId);
});

/// All Fields Provider (for current tenant)
/// Exposes domain.Field entities for UI consumption
final allFieldsProvider =
    FutureProvider.family<List<domain.Field>, String>((ref, tenantId) async {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.getAllFields(tenantId);
});

/// Single Field Provider - Get field by ID
final fieldByIdProvider =
    FutureProvider.family<domain.Field?, String>((ref, fieldId) async {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.getFieldById(fieldId);
});

/// Fields for Farm Provider
final fieldsForFarmProvider =
    FutureProvider.family<List<domain.Field>, String>((ref, farmId) async {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.getFieldsForFarm(farmId);
});

/// Unsynced Fields Provider
final unsyncedFieldsProvider = FutureProvider<List<domain.Field>>((ref) async {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.getUnsyncedFields();
});

/// Unsynced Fields Count Provider
final unsyncedFieldsCountProvider = FutureProvider<int>((ref) async {
  final fields = await ref.watch(unsyncedFieldsProvider.future);
  return fields.length;
});

// Note: databaseProvider is exported from main.dart above
// All consumers should import from this file or main.dart
