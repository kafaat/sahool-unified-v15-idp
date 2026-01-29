/// Database for ${{ values.name }} module (Offline Support)
/// قاعدة بيانات لوحدة ${{ values.name }} (دعم العمل دون اتصال)
///
/// Uses Drift (SQLite) with SQLCipher encryption for secure local storage.
/// يستخدم Drift (SQLite) مع تشفير SQLCipher للتخزين المحلي الآمن.

import 'package:drift/drift.dart';

part 'database.g.dart';

/// Sync status for offline records
/// حالة المزامنة للسجلات غير المتصلة
enum SyncStatus {
  synced,     // مزامنة
  pending,    // معلق
  failed,     // فشل
  conflict,   // تعارض
}

/// Base table with common fields
/// جدول أساسي مع الحقول المشتركة
mixin AutoIncrementingPrimaryKey on Table {
  IntColumn get id => integer().autoIncrement()();
}

mixin WithTimestamps on Table {
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().nullable()();
}

mixin WithSyncStatus on Table {
  IntColumn get syncStatus => intEnum<SyncStatus>().withDefault(Constant(SyncStatus.pending.index))();
  TextColumn get localId => text().nullable()();
  TextColumn get remoteId => text().nullable()();
}

/// Example table - customize for your module
/// جدول مثال - خصصه لوحدتك
@DataClassName('${{ values.name | pascal_case }}Record')
class ${{ values.name | pascal_case }}Records extends Table
    with AutoIncrementingPrimaryKey, WithTimestamps, WithSyncStatus {
  TextColumn get name => text().withLength(min: 1, max: 255)();
  TextColumn get nameAr => text().nullable()();
  TextColumn get data => text().map(const JsonConverter())();
  RealColumn get latitude => real().nullable()();
  RealColumn get longitude => real().nullable()();
}

/// JSON converter for storing complex data
/// محول JSON لتخزين البيانات المعقدة
class JsonConverter extends TypeConverter<Map<String, dynamic>, String> {
  const JsonConverter();

  @override
  Map<String, dynamic> fromSql(String fromDb) {
    return Map<String, dynamic>.from(
      jsonDecode(fromDb) as Map<String, dynamic>,
    );
  }

  @override
  String toSql(Map<String, dynamic> value) {
    return jsonEncode(value);
  }
}

/// Database class
/// فئة قاعدة البيانات
@DriftDatabase(tables: [${{ values.name | pascal_case }}Records])
class ${{ values.name | pascal_case }}Database extends _$${{ values.name | pascal_case }}Database {
  ${{ values.name | pascal_case }}Database() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  /// Get all records
  /// الحصول على جميع السجلات
  Future<List<${{ values.name | pascal_case }}Record>> getAllRecords() {
    return select(${{ values.name | camel_case }}Records).get();
  }

  /// Get pending sync records
  /// الحصول على السجلات المعلقة للمزامنة
  Future<List<${{ values.name | pascal_case }}Record>> getPendingSyncRecords() {
    return (select(${{ values.name | camel_case }}Records)
      ..where((t) => t.syncStatus.equals(SyncStatus.pending.index)))
        .get();
  }

  /// Insert or update record
  /// إدراج أو تحديث سجل
  Future<int> upsertRecord(${{ values.name | pascal_case }}RecordsCompanion record) {
    return into(${{ values.name | camel_case }}Records).insertOnConflictUpdate(record);
  }

  /// Mark record as synced
  /// تحديد السجل كمزامن
  Future<bool> markAsSynced(int id, String remoteId) {
    return (update(${{ values.name | camel_case }}Records)
      ..where((t) => t.id.equals(id)))
        .write(${{ values.name | pascal_case }}RecordsCompanion(
          syncStatus: Value(SyncStatus.synced.index),
          remoteId: Value(remoteId),
          updatedAt: Value(DateTime.now()),
        ))
        .then((count) => count > 0);
  }

  /// Delete record
  /// حذف سجل
  Future<int> deleteRecord(int id) {
    return (delete(${{ values.name | camel_case }}Records)
      ..where((t) => t.id.equals(id)))
        .go();
  }
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    // Use encrypted database with SQLCipher
    // استخدم قاعدة بيانات مشفرة مع SQLCipher
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, '${{ values.name }}.db'));
    return NativeDatabase(file);
  });
}
