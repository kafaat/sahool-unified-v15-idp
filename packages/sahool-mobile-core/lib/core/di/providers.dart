// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Feature Providers (Fields)
// مزودات الميزات (الحقول)
// ═══════════════════════════════════════════════════════════════════════════
//
// Field-specific providers that depend on core providers defined in
// core_providers.dart. Import everything via di.dart barrel file.
// مزودات خاصة بالحقول تعتمد على المزودات الأساسية في core_providers.dart.
// ═══════════════════════════════════════════════════════════════════════════

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../storage/database.dart' hide Field;
import '../../features/field/data/repo/fields_repo.dart';
import '../../features/field/data/remote/fields_api.dart';
import '../../features/field/domain/entities/field.dart';
import '../http/api_client.dart';
import 'core_providers.dart';

// Re-export core providers so existing imports continue to work
// إعادة تصدير المزودات الأساسية للحفاظ على التوافق مع الاستيرادات الحالية
export 'core_providers.dart'
    show databaseProvider, coreApiClientProvider, syncEngineProvider;

/// API Client Provider
/// مزود عميل الطلبات
///
/// Delegates to [coreApiClientProvider] from core_providers.dart.
/// Certificate pinning, request signing, and token management are
/// automatically configured based on build mode.
/// يفوّض إلى coreApiClientProvider. يُهيئ تثبيت الشهادات، توقيع الطلبات،
/// وإدارة الرمز المميز تلقائياً حسب وضع البناء.
final apiClientProvider = Provider<ApiClient>((ref) {
  return ref.watch(coreApiClientProvider);
});

/// Fields API Provider
/// مزود واجهة الحقول
final fieldsApiProvider = Provider<FieldsApi>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return FieldsApi(apiClient);
});

/// Fields Repository Provider
/// مزود مستودع الحقول
final fieldsRepoProvider = Provider<FieldsRepo>((ref) {
  final db = ref.watch(databaseProvider);
  final api = ref.watch(fieldsApiProvider);
  return FieldsRepo(
    database: db,
    api: api,
  );
});

/// Fields Stream Provider - Live updates from database
/// مزود تدفق الحقول - تحديثات مباشرة من قاعدة البيانات
final fieldsStreamProvider =
    StreamProvider.family<List<Field>, String>((ref, tenantId) {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.watchAllFields(tenantId);
});

/// All Fields Provider (for current tenant)
/// مزود جميع الحقول (للمستأجر الحالي)
final allFieldsProvider =
    FutureProvider.family<List<Field>, String>((ref, tenantId) async {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.getAllFields(tenantId);
});

/// Unsynced Fields Provider
/// مزود الحقول غير المتزامنة
final unsyncedFieldsProvider = FutureProvider<List<Field>>((ref) async {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.getUnsyncedFields();
});
