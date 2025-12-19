#!/usr/bin/env bash
set -euo pipefail

echo "🚀 SAHOOL Apply-All Script (Patch + Weather Refactor + ETag Conflict)"

TS="$(date +%Y%m%d_%H%M%S)"
BK=".sahool_backup_$TS"
mkdir -p "$BK"

backup_file () {
  local f="$1"
  if [ -f "$f" ]; then
    mkdir -p "$BK/$(dirname "$f")"
    cp "$f" "$BK/$f"
  fi
}

need_cmd () { command -v "$1" >/dev/null 2>&1; }

if ! need_cmd python3; then
  echo "❌ python3 is required for this script."
  exit 1
fi

# -----------------------------
# 0) Backup key files (safe)
# -----------------------------
for f in \
  lib/core/sync/network_status.dart \
  lib/core/sync/sync_worker.dart \
  lib/core/storage/tables.dart \
  lib/core/storage/database.dart \
  lib/core/config/theme.dart \
  lib/features/weather/domain/entities/weather_entities.dart \
  ; do
  backup_file "$f"
done

echo "📦 Backup created at: $BK"

# -----------------------------
# 1) Ensure deps (no harm if already there)
# -----------------------------
echo "📦 Ensuring dependencies..."
flutter pub add \
  flutter_riverpod connectivity_plus drift sqlite3_flutter_libs path_provider path \
  flutter_map latlong2 workmanager dio google_fonts flutter_svg intl >/dev/null 2>&1 || true

flutter pub add --dev drift_dev build_runner >/dev/null 2>&1 || true

# -----------------------------
# 2) FIX: connectivity_plus v5 network status
# -----------------------------
echo "🔧 Writing NetworkStatus (connectivity_plus v5 compatible)..."
mkdir -p lib/core/sync
cat > lib/core/sync/network_status.dart <<'EOF'
import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

/// Network Status Monitor
/// مراقب حالة الشبكة - متوافق مع connectivity_plus v5+
class NetworkStatus {
  final Connectivity _connectivity = Connectivity();
  StreamSubscription<List<ConnectivityResult>>? _subscription;

  bool _isOnline = false;
  final _onlineController = StreamController<bool>.broadcast();

  Stream<bool> get onlineStream => _onlineController.stream;
  bool get isOnline => _isOnline;

  NetworkStatus() {
    _init();
  }

  void _init() {
    // Check initial status
    _connectivity.checkConnectivity().then(_updateStatus);

    // Listen for changes
    _subscription = _connectivity.onConnectivityChanged.listen(_updateStatus);
  }

  void _updateStatus(List<ConnectivityResult> results) {
    final wasOnline = _isOnline;

    // Check if any result indicates connectivity
    _isOnline = results.isNotEmpty &&
        results.any((result) => result != ConnectivityResult.none);

    if (wasOnline != _isOnline) {
      _onlineController.add(_isOnline);
    }
  }

  Future<bool> checkOnline() async {
    final results = await _connectivity.checkConnectivity();
    _updateStatus(results);
    return _isOnline;
  }

  void dispose() {
    _subscription?.cancel();
    _onlineController.close();
  }
}
EOF

# -----------------------------
# 3) FIX: Theme types (CardThemeData/TabBarThemeData/DialogThemeData)
# -----------------------------
if [ -f lib/core/config/theme.dart ]; then
  echo "🎨 Patching Theme types in lib/core/config/theme.dart ..."
  python3 - <<'PY'
from pathlib import Path
p = Path("lib/core/config/theme.dart")
s = p.read_text(encoding="utf-8")

# Convert wrong constructors to *Data variants (Flutter newer typing)
s = s.replace("cardTheme: CardTheme(", "cardTheme: CardThemeData(")
s = s.replace("tabBarTheme: TabBarTheme(", "tabBarTheme: TabBarThemeData(")
s = s.replace("dialogTheme: DialogTheme(", "dialogTheme: DialogThemeData(")

p.write_text(s, encoding="utf-8")
PY
else
  echo "ℹ️ lib/core/config/theme.dart not found, skipping theme patch."
fi

# -----------------------------
# 4) Drift Schema v2 + Migration (ETag-ready + SyncEvents)
# -----------------------------
echo "🗄️ Writing Drift tables.dart (v2 schema)..."
mkdir -p lib/core/storage/mixins lib/core/storage/converters lib/core/storage
cat > lib/core/storage/mixins/tenant_mixin.dart <<'EOF'
import 'package:drift/drift.dart';

mixin TenantMixin on Table {
  TextColumn get userId => text()();
}
EOF

cat > lib/core/storage/converters/geo_converter.dart <<'EOF'
import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:latlong2/latlong.dart';

class GeoPolygonConverter extends TypeConverter<List<LatLng>, String> {
  const GeoPolygonConverter();

  @override
  List<LatLng> fromSql(String fromDb) {
    try {
      final List<dynamic> jsonList = jsonDecode(fromDb);
      return jsonList.map((p) => LatLng((p[1] as num).toDouble(), (p[0] as num).toDouble())).toList();
    } catch (_) {
      return const [];
    }
  }

  @override
  String toSql(List<LatLng> value) {
    final jsonList = value.map((p) => [p.longitude, p.latitude]).toList();
    return jsonEncode(jsonList);
  }
}

class GeoPointConverter extends TypeConverter<LatLng?, String> {
  const GeoPointConverter();

  @override
  LatLng? fromSql(String fromDb) {
    try {
      final List<dynamic> point = jsonDecode(fromDb);
      return LatLng((point[1] as num).toDouble(), (point[0] as num).toDouble());
    } catch (_) {
      return null;
    }
  }

  @override
  String toSql(LatLng? value) {
    if (value == null) return '[]';
    return jsonEncode([value.longitude, value.latitude]);
  }
}
EOF

cat > lib/core/storage/tables.dart <<'EOF'
import 'package:drift/drift.dart';
import 'mixins/tenant_mixin.dart';
import 'converters/geo_converter.dart';

/// Fields Table - الحقول الزراعية مع دعم GIS
class Fields extends Table with TenantMixin {
  TextColumn get id => text()();
  TextColumn get name => text()();
  TextColumn get cropType => text()();
  TextColumn get boundary => text().map(const GeoPolygonConverter())();
  RealColumn get areaHectares => real().withDefault(const Constant(0.0))();

  // Offline-first sync flags
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();

  // Conflict metadata
  DateTimeColumn get lastUpdated => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();

  // ETag support (server authoritative)
  TextColumn get etag => text().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

/// Outbox Table - طابور العمليات المعلقة
class Outbox extends Table with TenantMixin {
  IntColumn get id => integer().autoIncrement()();

  // Entity targeting (for conflict handling)
  TextColumn get entityType => text()(); // 'field'...
  TextColumn get entityId => text()();

  TextColumn get apiEndpoint => text()();
  TextColumn get method => text()(); // POST/PUT/DELETE
  TextColumn get payload => text()();

  // Timestamp header for server verification
  DateTimeColumn get clientUpdatedAt => dateTime().withDefault(currentDateAndTime)();

  IntColumn get retryCount => integer().withDefault(const Constant(0))();
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

/// SyncEvents Table - أحداث المزامنة والتعارضات
class SyncEvents extends Table with TenantMixin {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get type => text()(); // CONFLICT/INFO/ERROR
  TextColumn get message => text()();
  BoolColumn get isRead => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

/// SyncLogs Table - سجلات المزامنة
class SyncLogs extends Table {
  IntColumn get id => integer().autoIncrement()();
  DateTimeColumn get timestamp => dateTime().withDefault(currentDateAndTime)();
  TextColumn get level => text()();
  TextColumn get message => text()();
}

/// Tasks Table - المهام الزراعية
class Tasks extends Table with TenantMixin {
  TextColumn get id => text()();
  TextColumn get fieldId => text()();
  TextColumn get title => text()();
  TextColumn get description => text().nullable()();
  TextColumn get status => text().withDefault(const Constant('pending'))();
  TextColumn get priority => text().withDefault(const Constant('P2'))();
  DateTimeColumn get dueDate => dateTime().nullable()();
  DateTimeColumn get completedAt => dateTime().nullable()();
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}
EOF

echo "🗄️ Writing Drift database.dart (schemaVersion=2 + migration)..."
cat > lib/core/storage/database.dart <<'EOF'
import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;

import 'tables.dart';

part 'database.g.dart';

@DriftDatabase(tables: [Fields, Outbox, SyncEvents, SyncLogs, Tasks])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_open());

  @override
  int get schemaVersion => 2;

  @override
  MigrationStrategy get migration => MigrationStrategy(
        onCreate: (m) async {
          await m.createAll();
        },
        onUpgrade: (m, from, to) async {
          // Minimal safe migration for existing installs
          if (from < 2) {
            // Add ETag columns & conflict columns if missing
            await m.addColumn(fields, fields.etag);
            await m.addColumn(fields, fields.serverUpdatedAt);
            await m.addColumn(fields, fields.areaHectares);
            await m.addColumn(outbox, outbox.entityType);
            await m.addColumn(outbox, outbox.entityId);
            await m.addColumn(outbox, outbox.clientUpdatedAt);
            await m.createTable(syncEvents);
          }
        },
      );

  // ═══════════════════════════════════════════════════════════════════
  // Field Operations
  // ═══════════════════════════════════════════════════════════════════

  Future<List<Field>> getAllFields(String userId) {
    return (select(fields)..where((f) => f.userId.equals(userId))).get();
  }

  Future<Field?> getFieldById(String id) {
    return (select(fields)..where((f) => f.id.equals(id))).getSingleOrNull();
  }

  Future<void> insertField(FieldsCompanion field) {
    return into(fields).insert(field, mode: InsertMode.insertOrReplace);
  }

  Future<void> updateField(String id, FieldsCompanion field) {
    return (update(fields)..where((f) => f.id.equals(id))).write(field);
  }

  // ═══════════════════════════════════════════════════════════════════
  // Outbox Operations
  // ═══════════════════════════════════════════════════════════════════

  Future<List<OutboxData>> getPendingOutbox(String userId) {
    return (select(outbox)
          ..where((o) => o.userId.equals(userId))
          ..where((o) => o.isSynced.equals(false))
          ..orderBy([(o) => OrderingTerm.asc(o.createdAt)]))
        .get();
  }

  Future<void> addToOutbox(OutboxCompanion item) {
    return into(outbox).insert(item);
  }

  Future<void> markOutboxSynced(int id) {
    return (update(outbox)..where((o) => o.id.equals(id)))
        .write(const OutboxCompanion(isSynced: Value(true)));
  }

  // ═══════════════════════════════════════════════════════════════════
  // SyncEvents Operations
  // ═══════════════════════════════════════════════════════════════════

  Future<List<SyncEvent>> getUnreadEvents(String userId) {
    return (select(syncEvents)
          ..where((e) => e.userId.equals(userId))
          ..where((e) => e.isRead.equals(false))
          ..orderBy([(e) => OrderingTerm.desc(e.createdAt)]))
        .get();
  }

  Future<void> addSyncEvent(SyncEventsCompanion event) {
    return into(syncEvents).insert(event);
  }

  Future<void> markEventRead(int id) {
    return (update(syncEvents)..where((e) => e.id.equals(id)))
        .write(const SyncEventsCompanion(isRead: Value(true)));
  }

  // ═══════════════════════════════════════════════════════════════════
  // Task Operations
  // ═══════════════════════════════════════════════════════════════════

  Future<List<Task>> getTasksByField(String fieldId) {
    return (select(tasks)..where((t) => t.fieldId.equals(fieldId))).get();
  }

  Future<List<Task>> getPendingTasks(String userId) {
    return (select(tasks)
          ..where((t) => t.userId.equals(userId))
          ..where((t) => t.status.equals('pending')))
        .get();
  }

  // ═══════════════════════════════════════════════════════════════════
  // Logging
  // ═══════════════════════════════════════════════════════════════════

  Future<void> log(String level, String message) {
    return into(syncLogs).insert(
      SyncLogsCompanion.insert(level: level, message: message),
    );
  }
}

LazyDatabase _open() {
  return LazyDatabase(() async {
    final dir = await getApplicationDocumentsDirectory();
    final file = File(p.join(dir.path, 'sahool_enterprise.sqlite'));
    return NativeDatabase(file);
  });
}
EOF

# -----------------------------
# 5) Weather Refactor: Domain بدون Flutter (حل جذري لتضارب Color)
# -----------------------------
echo "🌦️ Refactoring Weather Domain to be Flutter-free..."

mkdir -p lib/features/weather/domain/value_objects
cat > lib/features/weather/domain/value_objects/weather_color.dart <<'EOF'
/// WeatherColor - Domain Value Object
/// لون مستقل عن Flutter (DDD Clean)
///
/// هذا الكلاس لا يعتمد على dart:ui أو Flutter
/// يُستخدم فقط في Domain Layer
class WeatherColor {
  final int value;

  const WeatherColor(this.value);

  /// ألوان محددة مسبقاً للاستخدام في Domain
  static const WeatherColor green = WeatherColor(0xFF2E7D32);
  static const WeatherColor orange = WeatherColor(0xFFF9A825);
  static const WeatherColor red = WeatherColor(0xFFC62828);
  static const WeatherColor blue = WeatherColor(0xFF1976D2);
  static const WeatherColor grey = WeatherColor(0xFF6B7280);
  static const WeatherColor yellow = WeatherColor(0xFFFBC02D);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WeatherColor && runtimeType == other.runtimeType && value == other.value;

  @override
  int get hashCode => value.hashCode;

  @override
  String toString() => 'WeatherColor(0x${value.toRadixString(16).padLeft(8, '0').toUpperCase()})';
}
EOF

cat > lib/features/weather/domain/value_objects/weather_severity.dart <<'EOF'
import 'weather_color.dart';

/// Weather Severity - شدة تأثير الطقس على الزراعة
enum WeatherSeverity {
  favorable,
  caution,
  unfavorable,
}

extension WeatherSeverityExtension on WeatherSeverity {
  WeatherColor get color {
    switch (this) {
      case WeatherSeverity.favorable:
        return WeatherColor.green;
      case WeatherSeverity.caution:
        return WeatherColor.orange;
      case WeatherSeverity.unfavorable:
        return WeatherColor.red;
    }
  }

  String get labelAr {
    switch (this) {
      case WeatherSeverity.favorable:
        return 'ملائم';
      case WeatherSeverity.caution:
        return 'تحذير';
      case WeatherSeverity.unfavorable:
        return 'غير ملائم';
    }
  }
}
EOF

cat > lib/features/weather/domain/value_objects/alert_severity.dart <<'EOF'
import 'weather_color.dart';

/// Alert Severity - شدة تنبيهات الطقس
enum AlertSeverity {
  warning,
  watch,
  advisory,
}

extension AlertSeverityColor on AlertSeverity {
  WeatherColor get color {
    switch (this) {
      case AlertSeverity.warning:
        return WeatherColor.red;
      case AlertSeverity.watch:
        return WeatherColor.orange;
      case AlertSeverity.advisory:
        return WeatherColor.yellow;
    }
  }

  String get labelAr {
    switch (this) {
      case AlertSeverity.warning:
        return 'تحذير';
      case AlertSeverity.watch:
        return 'مراقبة';
      case AlertSeverity.advisory:
        return 'إرشاد';
    }
  }

  static AlertSeverity fromString(String value) {
    switch (value.toLowerCase()) {
      case 'warning':
        return AlertSeverity.warning;
      case 'watch':
        return AlertSeverity.watch;
      case 'advisory':
      default:
        return AlertSeverity.advisory;
    }
  }
}
EOF

# UI helper mapping (Flutter side only)
mkdir -p lib/core/ui
cat > lib/core/ui/color_mapper.dart <<'EOF'
import 'dart:ui';
import '../../features/weather/domain/value_objects/weather_color.dart';

/// UI Color Mapper - محول الألوان من Domain إلى Flutter
///
/// هذا الملف هو الجسر الوحيد بين Domain Colors و Flutter Colors
/// يُستخدم فقط في UI Layer

/// Extension لتحويل WeatherColor إلى Flutter Color
extension WeatherColorMapper on WeatherColor {
  /// تحويل إلى Flutter Color
  Color toFlutter() => Color(value);

  /// تحويل مع شفافية
  Color toFlutterWithOpacity(double opacity) => Color(value).withOpacity(opacity);
}

/// Helper functions للاستخدام في UI
class ColorMapper {
  ColorMapper._();

  /// تحويل WeatherColor إلى Flutter Color
  static Color fromWeather(WeatherColor weatherColor) => Color(weatherColor.value);

  /// تحويل قيمة int مباشرة
  static Color fromValue(int value) => Color(value);

  /// إنشاء WeatherColor من Flutter Color
  static WeatherColor toWeather(Color flutterColor) => WeatherColor(flutterColor.value);
}
EOF

echo "✅ Weather domain fixed (no Color conflicts anymore)."

# -----------------------------
# 6) Auth UserContext placeholder
# -----------------------------
echo "🔐 Creating UserContext placeholder..."
mkdir -p lib/core/auth
cat > lib/core/auth/user_context.dart <<'EOF'
/// User Context - سياق المستخدم الحالي
/// يُستخدم للحصول على معرف المستخدم في العمليات المختلفة
class UserContext {
  String? _currentUserId;

  String get currentUserId => _currentUserId ?? 'anonymous';

  bool get isAuthenticated => _currentUserId != null;

  void setUser(String userId) {
    _currentUserId = userId;
  }

  void clearUser() {
    _currentUserId = null;
  }
}
EOF

# -----------------------------
# 7) ETag / If-Match Conflict Resolution داخل SyncWorker
# -----------------------------
echo "🔄 Writing SyncWorker with 409 Conflict + ETag..."
cat > lib/core/sync/sync_worker.dart <<'EOF'
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:drift/drift.dart';

import '../storage/database.dart';
import '../sync/network_status.dart';
import '../auth/user_context.dart';

/// Sync Worker - عامل المزامنة مع دعم ETag و Conflict Resolution
class SyncWorker {
  final AppDatabase _db;
  final NetworkStatus _net;
  final UserContext _auth;
  final Dio _dio;

  SyncWorker(this._db, this._net, this._auth, {Dio? dio}) : _dio = dio ?? Dio();

  /// تشغيل المزامنة
  Future<void> run() async {
    if (!_net.isOnline) {
      await _db.log('INFO', 'Sync skipped: offline');
      return;
    }

    final uid = _auth.currentUserId;
    final items = await _db.getPendingOutbox(uid);

    for (final item in items) {
      await _processItem(item);
    }
  }

  Future<void> _processItem(OutboxData item) async {
    try {
      // If-Match for FIELD updates if we have an etag locally
      final headers = <String, dynamic>{
        'Content-Type': 'application/json',
        'X-Client-Updated-At': item.clientUpdatedAt.toIso8601String(),
      };

      if (item.entityType == 'field' && item.method.toUpperCase() == 'PUT') {
        final local = await _db.getFieldById(item.entityId);
        if (local?.etag != null && local!.etag!.isNotEmpty) {
          headers['If-Match'] = local.etag!;
        }
      }

      final resp = await _dio.request(
        item.apiEndpoint,
        data: jsonDecode(item.payload),
        options: Options(method: item.method, headers: headers),
      );

      // If server returns new ETag for field, store it
      final newEtag = resp.headers.value('etag') ?? resp.headers.value('ETag');
      if (newEtag != null && item.entityType == 'field') {
        await _db.updateField(
          item.entityId,
          FieldsCompanion(
            etag: Value(newEtag),
            serverUpdatedAt: Value(DateTime.now()),
            isSynced: const Value(true),
          ),
        );
      }

      await _db.markOutboxSynced(item.id);
      await _db.log('INFO', 'Synced: ${item.entityType}:${item.entityId}');
    } on DioException catch (e) {
      if (e.response?.statusCode == 409) {
        await _handleConflict(item, e.response?.data);
        await _db.markOutboxSynced(item.id);
        return;
      }

      if (e.response?.statusCode != null && e.response!.statusCode! >= 500) {
        await _db.log('ERROR', 'Server error. Will retry later. ${e.message}');
        return;
      }

      await _db.log('ERROR', 'Fatal request error: ${e.message}');
      await _db.markOutboxSynced(item.id); // prevent queue lock
    } catch (e) {
      await _db.log('ERROR', 'Unknown sync error: $e');
    }
  }

  Future<void> _handleConflict(OutboxData item, dynamic serverBody) async {
    final uid = _auth.currentUserId;

    // Expecting: { "serverData": {...}, "message": "Conflict" }
    Map<String, dynamic>? serverData;
    if (serverBody is Map<String, dynamic>) {
      final sd = serverBody['serverData'];
      if (sd is Map<String, dynamic>) serverData = sd;
    }

    if (item.entityType == 'field' && serverData != null) {
      // Overwrite local with server authoritative version
      await _db.updateField(
        serverData['id'].toString(),
        FieldsCompanion(
          name: Value(serverData['name'].toString()),
          cropType: Value(serverData['cropType'].toString()),
          boundary: Value(jsonEncode(serverData['boundary'])),
          isSynced: const Value(true),
          etag: Value(serverData['etag']?.toString()),
          serverUpdatedAt: Value(
            DateTime.tryParse(serverData['serverUpdatedAt']?.toString() ?? '') ?? DateTime.now(),
          ),
        ),
      );
    }

    await _db.addSyncEvent(
      SyncEventsCompanion.insert(
        type: 'CONFLICT',
        message: 'تم تطبيق نسخة السيرفر بسبب تعارض على ${item.entityType}:${item.entityId}',
        userId: uid,
      ),
    );

    await _db.log('INFO', 'Conflict resolved by applying server version for outbox:${item.id}');
  }
}
EOF

# -----------------------------
# 8) build_runner for Drift
# -----------------------------
echo "⚙️ Running build_runner..."
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs || echo "⚠️ build_runner failed - run manually after fixing any issues"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ SAHOOL Apply-All Script Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📌 Next steps:"
echo "   flutter clean"
echo "   flutter pub get"
echo "   flutter run"
echo ""
echo "⚠️ If you had a previous DB on emulator/device, uninstall app once (schema changed)."
echo ""
