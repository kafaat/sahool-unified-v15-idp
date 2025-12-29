/// Example usage of EcologicalSyncHandler
/// مثال على استخدام معالج مزامنة السجلات البيئية
///
/// This file demonstrates how to use the ecological sync handler
/// in different scenarios within the Sahool Field mobile app.

import 'package:uuid/uuid.dart';
import '../../../../core/storage/database.dart';
import '../../../../core/http/api_client.dart';
import '../../domain/entities/ecological_entities.dart';
import '../repositories/ecological_repository.dart';
import 'ecological_sync_handler.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Example 1: Automatic Sync through Repository Pattern
// مثال 1: المزامنة التلقائية عبر نمط المستودع
// ═══════════════════════════════════════════════════════════════════════════

Future<void> exampleSaveRecordWithAutoSync(
  EcologicalRepository repository,
  String tenantId,
  String fieldId,
) async {
  // إنشاء سجل جديد | Create a new record
  final biodiversityRecord = BiodiversityRecord(
    id: const Uuid().v4(),
    farmId: 'farm-123',
    tenantId: tenantId,
    surveyDate: DateTime.now(),
    surveyType: BiodiversitySurveyType.speciesCount,
    speciesCount: 15,
    beneficialInsectCount: 8,
    pollinatorCount: 12,
    speciesObserved: ['نحل', 'فراشات', 'خنافس'],
    habitatFeatures: ['تحوطات', 'أزهار برية'],
    diversityIndex: 0.75,
    habitatQualityScore: 85,
    notes: 'Survey conducted in morning',
    notesAr: 'تم المسح في الصباح',
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );

  // حفظ محلياً وإضافة للطابور
  // Save locally and queue for sync
  await repository.saveBiodiversityRecordOfflineFirst(biodiversityRecord);

  print('✅ Record saved locally and queued for sync');
  // السجل سيتم مزامنته تلقائياً في الدورة التالية للمزامنة
  // Record will be synced automatically in the next sync cycle
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 2: Manual Batch Sync
// مثال 2: المزامنة الجماعية اليدوية
// ═══════════════════════════════════════════════════════════════════════════

Future<void> exampleManualBatchSync(
  EcologicalSyncHandler handler,
) async {
  print('🔄 Starting manual batch sync...');

  // مزامنة جميع السجلات البيئية المعلقة
  // Sync all pending ecological records
  final result = await handler.syncAllPending(batchSize: 50);

  // عرض النتائج | Display results
  print('📊 Sync Results:');
  print('   Synced: ${result.synced}');
  print('   Failed: ${result.failed}');
  print('   Conflicts: ${result.conflicts}');
  print('   Total: ${result.totalProcessed}');

  // عرض الرسالة بالعربية | Display Arabic message
  print('   Status: ${result.statusMessageAr}');

  // التحقق من النجاح | Check if successful
  if (result.isSuccess) {
    print('✅ All records synced successfully');
  } else if (result.hasConflicts) {
    print('⚠️ Some conflicts were resolved');
  } else {
    print('❌ Some records failed to sync');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 3: Pull Latest Data from Server
// مثال 3: سحب أحدث البيانات من الخادم
// ═══════════════════════════════════════════════════════════════════════════

Future<void> examplePullFromServer(
  EcologicalSyncHandler handler,
  String tenantId,
) async {
  print('⬇️ Pulling ecological records from server...');

  try {
    // سحب جميع السجلات البيئية من الخادم
    // Pull all ecological records from server
    await handler.pullFromServer(tenantId);

    print('✅ Successfully pulled ecological records from server');
  } catch (e) {
    print('❌ Failed to pull from server: $e');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 4: Custom Sync Handler
// مثال 4: معالج مزامنة مخصص
// ═══════════════════════════════════════════════════════════════════════════

Future<void> exampleCustomSyncHandler(
  AppDatabase db,
  ApiClient apiClient,
) async {
  // إنشاء معالج مزامنة مخصص
  // Create custom sync handler
  final handler = EcologicalSyncHandler(
    db: db,
    apiClient: apiClient,
  );

  // الوصول إلى معالجات محددة
  // Access specific handlers
  final biodiversityHandler = handler.handlers['biodiversity_record']!;
  final soilHealthHandler = handler.handlers['soil_health_record']!;

  print('✅ Custom sync handler created with ${handler.handlers.length} record types');
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 5: Integration with SyncEngine
// مثال 5: التكامل مع محرك المزامنة
// ═══════════════════════════════════════════════════════════════════════════

Future<void> exampleSyncEngineIntegration(
  AppDatabase database,
) async {
  // Note: The SyncEngine automatically includes the EcologicalSyncHandler
  // ملاحظة: محرك المزامنة يتضمن تلقائياً معالج السجلات البيئية

  // When SyncEngine is initialized, it creates an EcologicalSyncHandler
  // عند تهيئة محرك المزامنة، يتم إنشاء معالج السجلات البيئية

  // In sync_engine.dart:
  // _ecologicalHandler = EcologicalSyncHandler(
  //   db: database,
  //   apiClient: _apiClient,
  // );

  print('ℹ️ EcologicalSyncHandler is automatically integrated with SyncEngine');
  print('ℹ️ معالج السجلات البيئية متكامل تلقائياً مع محرك المزامنة');
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 6: Monitoring Sync Status
// مثال 6: مراقبة حالة المزامنة
// ═══════════════════════════════════════════════════════════════════════════

Future<void> exampleMonitorSyncStatus(
  AppDatabase db,
  String tenantId,
) async {
  // التحقق من السجلات المعلقة
  // Check pending records
  final pendingItems = await db.getPendingOutbox();
  final ecologicalPending = pendingItems.where((item) {
    return [
      'biodiversity_record',
      'soil_health_record',
      'water_conservation_record',
      'farm_practice_record',
    ].contains(item.entityType);
  }).toList();

  print('📊 Sync Status:');
  print('   Total pending: ${pendingItems.length}');
  print('   Ecological pending: ${ecologicalPending.length}');

  // التحقق من أحداث المزامنة
  // Check sync events
  final unreadEvents = await db.getUnreadSyncEvents(tenantId);
  final conflictEvents = unreadEvents.where((e) => e.type == 'CONFLICT').toList();

  print('   Unread events: ${unreadEvents.length}');
  print('   Conflicts: ${conflictEvents.length}');

  // عرض التعارضات
  // Display conflicts
  for (final event in conflictEvents) {
    print('   ⚠️ ${event.message}');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 7: Error Handling Best Practices
// مثال 7: أفضل ممارسات معالجة الأخطاء
// ═══════════════════════════════════════════════════════════════════════════

Future<void> exampleErrorHandling(
  EcologicalRepository repository,
  String tenantId,
  String fieldId,
) async {
  try {
    // محاولة حفظ السجل
    // Try to save record
    final record = SoilHealthRecord(
      id: const Uuid().v4(),
      fieldId: fieldId,
      tenantId: tenantId,
      sampleDate: DateTime.now(),
      sampleDepthCm: 15.0,
      organicMatterPercent: 3.5,
      phLevel: 6.8,
      healthScore: 75,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );

    await repository.saveSoilHealthRecordOfflineFirst(record);
    print('✅ Record saved successfully');
  } catch (e) {
    // معالجة الأخطاء المحلية
    // Handle local errors
    print('❌ Failed to save record: $e');

    // تسجيل الخطأ
    // Log error
    // await db.logSync(
    //   type: 'save_error',
    //   status: 'error',
    //   message: 'Failed to save soil health record: $e',
    // );

    // إعلام المستخدم
    // Notify user
    // showErrorDialog('فشل حفظ السجل');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Example Runner
// مثال رئيسي للتشغيل
// ═══════════════════════════════════════════════════════════════════════════

Future<void> main() async {
  print('🌱 Ecological Sync Handler Examples');
  print('════════════════════════════════════════════════════════════════════');

  // Note: In real app, get these from dependency injection
  // ملاحظة: في التطبيق الحقيقي، احصل على هذه من حقن التبعية
  final db = AppDatabase();
  final apiClient = ApiClient();
  final repository = EcologicalRepository(database: db);
  final handler = EcologicalSyncHandler(db: db, apiClient: apiClient);

  const tenantId = 'tenant-123';
  const fieldId = 'field-456';

  // Run examples
  print('\n📝 Example 1: Save Record with Auto Sync');
  await exampleSaveRecordWithAutoSync(repository, tenantId, fieldId);

  print('\n📝 Example 2: Manual Batch Sync');
  await exampleManualBatchSync(handler);

  print('\n📝 Example 3: Pull from Server');
  await examplePullFromServer(handler, tenantId);

  print('\n📝 Example 6: Monitor Sync Status');
  await exampleMonitorSyncStatus(db, tenantId);

  print('\n✅ All examples completed');
}
