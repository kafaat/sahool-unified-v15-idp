import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/field/data/repo/fields_repo.dart';
import '../../features/field/data/remote/fields_api.dart';
import '../../features/field/domain/entities/field.dart';
import '../http/api_client.dart';
import '../security/signing_key_service.dart';
import '../auth/token_manager.dart';
import '../auth/secure_storage_service.dart';
import 'database_provider.dart';

export 'database_provider.dart' show databaseProvider, syncEngineProvider;

/// API Client Provider
/// Automatically configures certificate pinning, request signing, and token management based on build mode:
/// - Debug builds: Certificate pinning disabled (for local development)
/// - Release builds: Certificate pinning and request signing enabled (for production security)
/// - Token interceptor: Configured for proactive refresh, retry logic, and request queueing
final apiClientProvider = Provider<ApiClient>((ref) {
  final signingKeyService = ref.watch(signingKeyServiceProvider);
  final tokenManager = ref.read(tokenManagerProvider);
  final secureStorage = ref.read(secureStorageProvider);

  final apiClient = ApiClient(
    signingKeyService: signingKeyService,
    enableRequestSigning: true,
    enableSecurityHeaderValidation: false,  // Backend doesn't send security headers in dev
  );

  // Configure advanced token interceptor for:
  // - Proactive refresh before token expiration (5 min buffer)
  // - Exponential backoff retry on refresh failures
  // - Request queueing during refresh
  // - Mutex lock to prevent concurrent refreshes
  apiClient.configureTokenInterceptor(
    tokenManager: tokenManager,
    secureStorage: secureStorage,
  );

  // Note: ApiClient automatically uses SecurityConfig.fromBuildMode()
  // which enables certificate pinning in release builds
  return apiClient;
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

