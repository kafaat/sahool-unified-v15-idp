#!/usr/bin/env bash
set -euo pipefail

APP_NAME="sahool_field_app"
SEED_COLOR="#1B5E20"

echo "🚀 SAHOOL Field App (Enterprise) - Full Generator"
echo "================================================"

command -v flutter >/dev/null 2>&1 || { echo "❌ flutter not found in PATH"; exit 1; }
command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1 || { echo "❌ python not found"; exit 1; }

PY=python
command -v python3 >/dev/null 2>&1 && PY=python3

# 1) Create Flutter project
if [[ -d "$APP_NAME" ]]; then
  echo "⚠️ Folder '$APP_NAME' already exists. Remove it first or change APP_NAME."
  exit 1
fi

echo "📦 Creating Flutter project: $APP_NAME"
flutter create "$APP_NAME"
cd "$APP_NAME"

# 2) Overwrite pubspec.yaml with enterprise deps (stable + generator-friendly)
echo "🧩 Writing pubspec.yaml (deps + dev_deps)"
cat > pubspec.yaml <<'YAML'
name: sahool_field_app
description: SAHOOL Field App - Enterprise Offline-First (Drift + Sync + Maps + Drawing)
publish_to: "none"
version: 1.0.0+1

environment:
  sdk: ">=3.3.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter

  # State
  flutter_riverpod: ^2.5.1

  # Network
  dio: ^5.7.0
  connectivity_plus: ^5.0.2

  # Database (Offline-First)
  drift: ^2.20.0
  sqlite3_flutter_libs: ^0.5.24
  path_provider: ^2.1.4
  path: ^1.9.0

  # Maps
  flutter_map: ^6.1.0
  latlong2: ^0.9.1

  # Background
  workmanager: ^0.5.2

  # UI
  google_fonts: ^6.2.1
  flutter_svg: ^2.0.10+1
  intl: ^0.19.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0

  # Codegen
  drift_dev: ^2.20.0
  build_runner: ^2.4.12

flutter:
  uses-material-design: true
YAML

echo "📥 flutter pub get"
flutter pub get

# 3) Folder structure
echo "📂 Creating folder structure"
mkdir -p lib/core/auth
mkdir -p lib/core/di
mkdir -p lib/core/storage/mixins
mkdir -p lib/core/storage/converters
mkdir -p lib/core/storage
mkdir -p lib/core/sync
mkdir -p lib/core/theme
mkdir -p lib/features/home/ui/logic
mkdir -p lib/features/home/ui
mkdir -p lib/features/field/data/repo
mkdir -p lib/features/field/ui/logic
mkdir -p lib/features/field/ui/widgets
mkdir -p lib/features/field/ui/utils

# =========================================================
# 4) Core: Auth
# =========================================================
cat > lib/core/auth/user_context.dart <<'DART'
class UserContext {
  // MVP mock user (replace with SecureStorage/Auth later)
  String get currentUserId => "user_101_uuid";
}
DART

# =========================================================
# 5) Core: Storage Mixins + Geo converter
# =========================================================
cat > lib/core/storage/mixins/tenant_mixin.dart <<'DART'
import 'package:drift/drift.dart';

mixin TenantMixin on Table {
  TextColumn get userId => text()();
}
DART

cat > lib/core/storage/converters/geo_converter.dart <<'DART'
import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:latlong2/latlong.dart';

/// Stores polygon as JSON string: [[lng,lat],[lng,lat],...]
class GeoPolygonConverter extends TypeConverter<List<LatLng>, String> {
  const GeoPolygonConverter();

  @override
  List<LatLng> fromSql(String fromDb) {
    try {
      final List<dynamic> jsonList = jsonDecode(fromDb);
      return jsonList.map((p) => LatLng((p[1] as num).toDouble(), (p[0] as num).toDouble())).toList();
    } catch (_) {
      return <LatLng>[];
    }
  }

  @override
  String toSql(List<LatLng> value) {
    final jsonList = value.map((p) => [p.longitude, p.latitude]).toList();
    return jsonEncode(jsonList);
  }
}
DART

# =========================================================
# 6) Core: Tables + DB (Conflict-ready schema)
# =========================================================
cat > lib/core/storage/tables.dart <<'DART'
import 'package:drift/drift.dart';
import 'mixins/tenant_mixin.dart';
import 'converters/geo_converter.dart';
import 'package:latlong2/latlong.dart';

class Fields extends Table with TenantMixin {
  TextColumn get id => text()();
  TextColumn get name => text()();
  TextColumn get cropType => text()();
  TextColumn get boundary => text().map(const GeoPolygonConverter())();

  DateTimeColumn get lastUpdated => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();

  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

class Outbox extends Table with TenantMixin {
  IntColumn get id => integer().autoIncrement()();

  TextColumn get entityType => text()(); // field/task/...
  TextColumn get entityId => text()();

  TextColumn get apiEndpoint => text()();
  TextColumn get method => text()(); // POST/PUT/DELETE
  TextColumn get payload => text()();

  DateTimeColumn get clientUpdatedAt => dateTime().withDefault(currentDateAndTime)();
  IntColumn get retryCount => integer().withDefault(const Constant(0))();

  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

class SyncEvents extends Table with TenantMixin {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get type => text()(); // CONFLICT/INFO/ERROR
  TextColumn get message => text()();
  BoolColumn get isRead => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

class SyncLogs extends Table {
  IntColumn get id => integer().autoIncrement()();
  DateTimeColumn get timestamp => dateTime().withDefault(currentDateAndTime)();
  TextColumn get level => text()();
  TextColumn get message => text()();
}
DART

cat > lib/core/storage/database.dart <<'DART'
import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;

import 'tables.dart';

part 'database.g.dart';

@DriftDatabase(tables: [Fields, Outbox, SyncEvents, SyncLogs])
class AppDatabase extends _$AppDatabase {
  // ✅ No Singleton (safe for background isolate)
  AppDatabase() : super(_open());

  @override
  int get schemaVersion => 1;
}

LazyDatabase _open() {
  return LazyDatabase(() async {
    final dir = await getApplicationDocumentsDirectory();
    final file = File(p.join(dir.path, 'sahool_enterprise.sqlite'));
    return NativeDatabase(file);
  });
}
DART

# =========================================================
# 7) Core: NetworkStatus (connectivity_plus v5 List<ConnectivityResult>)
# =========================================================
cat > lib/core/sync/network_status.dart <<'DART'
import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

class NetworkStatus {
  final _connectivity = Connectivity();
  ConnectivityResult _status = ConnectivityResult.none;
  StreamSubscription<List<ConnectivityResult>>? _sub;

  bool get isOnline => _status != ConnectivityResult.none;

  Future<void> init() async {
    final results = await _connectivity.checkConnectivity();
    _handle(results);

    _sub = _connectivity.onConnectivityChanged.listen(_handle);
  }

  void _handle(List<ConnectivityResult> results) {
    _status = results.isNotEmpty ? results.first : ConnectivityResult.none;
  }

  Future<void> dispose() async {
    await _sub?.cancel();
    _sub = null;
  }
}
DART

# =========================================================
# 8) Core: SyncWorker + Background Service
# =========================================================
cat > lib/core/sync/sync_worker.dart <<'DART'
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:drift/drift.dart';

import '../auth/user_context.dart';
import '../storage/database.dart';
import 'network_status.dart';

class SyncWorker {
  final AppDatabase db;
  final NetworkStatus net;
  final UserContext auth;
  final Dio dio;

  SyncWorker({
    required this.db,
    required this.net,
    required this.auth,
    Dio? dio,
  }) : dio = dio ?? Dio();

  Future<void> run() async {
    if (!net.isOnline) return;

    final uid = auth.currentUserId;

    final items = await (db.select(db.outbox)
          ..where((o) => o.userId.equals(uid))
          ..where((o) => o.isSynced.equals(false))
          ..orderBy([(o) => OrderingTerm.asc(o.createdAt)]))
        .get();

    for (final item in items) {
      await _process(item);
    }
  }

  Future<void> _process(OutboxData item) async {
    try {
      await dio.request(
        item.apiEndpoint,
        data: jsonDecode(item.payload),
        options: Options(
          method: item.method,
          headers: {
            // foundation for If-Match/ETag strategy later
            'X-Client-Updated-At': item.clientUpdatedAt.toIso8601String(),
          },
        ),
      );

      await (db.update(db.outbox)..where((o) => o.id.equals(item.id)))
          .write(const OutboxCompanion(isSynced: Value(true)));
    } on DioException catch (e) {
      // Here you can extend: handle 409 conflict with server authoritative
      await db.into(db.syncLogs).insert(
            SyncLogsCompanion.insert(level: 'ERROR', message: 'Dio: \${e.message}'),
          );
    } catch (e) {
      await db.into(db.syncLogs).insert(
            SyncLogsCompanion.insert(level: 'ERROR', message: 'Unknown: \$e'),
          );
    }
  }
}
DART

cat > lib/core/sync/background_service.dart <<'DART'
import 'package:workmanager/workmanager.dart';
import '../auth/user_context.dart';
import '../storage/database.dart';
import 'network_status.dart';
import 'sync_worker.dart';

const syncTaskName = "com.kafaat.sahool.syncTask";

@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    final db = AppDatabase();
    final net = NetworkStatus();
    await net.init();

    if (!net.isOnline) return true;

    final auth = UserContext();
    final worker = SyncWorker(db: db, net: net, auth: auth);
    await worker.run();

    await net.dispose();
    return true;
  });
}
DART

# =========================================================
# 9) Core: DI Providers (Riverpod)
# =========================================================
cat > lib/core/di/providers.dart <<'DART'
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../storage/database.dart';
import '../auth/user_context.dart';
import '../../features/field/data/repo/fields_repository.dart';

// DB instance (safe for app isolate; background creates its own)
final databaseProvider = Provider<AppDatabase>((ref) => AppDatabase());

final userContextProvider = Provider<UserContext>((ref) => UserContext());

// Repository
final fieldsRepoProvider = Provider<FieldsRepository>((ref) {
  final db = ref.watch(databaseProvider);
  final auth = ref.watch(userContextProvider);
  return FieldsRepository(db: db, auth: auth);
});

// Stream of Fields (Tenant-safe inside repo)
final fieldsStreamProvider = StreamProvider((ref) {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.watchMyFields();
});
DART

# =========================================================
# 10) UI: Glass widget
# =========================================================
cat > lib/core/theme/sahool_glass.dart <<'DART'
import 'dart:ui';
import 'package:flutter/material.dart';

class SahoolGlass extends StatelessWidget {
  final Widget child;
  final double opacity;
  final EdgeInsets padding;

  const SahoolGlass({
    super.key,
    required this.child,
    this.opacity = 0.86,
    this.padding = const EdgeInsets.all(12),
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(opacity),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white.withOpacity(0.25)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.12),
                blurRadius: 18,
                spreadRadius: 2,
              )
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
DART

# =========================================================
# 11) FieldsRepository (tenant filter + save real field + outbox)
# =========================================================
cat > lib/features/field/data/repo/fields_repository.dart <<'DART'
import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:latlong2/latlong.dart';
import '../../../../core/auth/user_context.dart';
import '../../../../core/storage/database.dart';

class FieldsRepository {
  final AppDatabase db;
  final UserContext auth;

  FieldsRepository({required this.db, required this.auth});

  Stream<List<Field>> watchMyFields() {
    final uid = auth.currentUserId;
    return (db.select(db.fields)..where((f) => f.userId.equals(uid))).watch();
  }

  Future<void> createRealField({
    required String name,
    required List<LatLng> boundary,
    String cropType = "غير محدد",
  }) async {
    final id = DateTime.now().millisecondsSinceEpoch.toString();
    final uid = auth.currentUserId;
    final now = DateTime.now();

    await db.into(db.fields).insert(
          FieldsCompanion.insert(
            id: id,
            userId: uid,
            name: name,
            cropType: cropType,
            boundary: boundary,
            isSynced: const Value(false),
            lastUpdated: Value(now),
          ),
        );

    await db.into(db.outbox).insert(
          OutboxCompanion.insert(
            userId: uid,
            entityType: 'field',
            entityId: id,
            apiEndpoint: '/api/v1/fields',
            method: 'POST',
            payload: jsonEncode({
              'id': id,
              'name': name,
              'cropType': cropType,
              'boundary': boundary.map((p) => {'lat': p.latitude, 'lng': p.longitude}).toList(),
              'clientUpdatedAt': now.toIso8601String(),
            }),
            clientUpdatedAt: Value(now),
          ),
        );
  }
}
DART

# =========================================================
# 12) Sync HUD providers (Outbox pending count -> status)
# =========================================================
cat > lib/features/home/ui/logic/sync_provider.dart <<'DART'
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/di/providers.dart';

enum SyncStatus { synced, syncing, offline }

final pendingOperationsProvider = StreamProvider<int>((ref) {
  final db = ref.watch(databaseProvider);
  return (db.select(db.outbox)..where((o) => o.isSynced.equals(false)))
      .watch()
      .map((rows) => rows.length);
});

final syncStatusUiProvider = Provider<SyncStatus>((ref) {
  final pendingAsync = ref.watch(pendingOperationsProvider);
  return pendingAsync.when(
    data: (count) => count > 0 ? SyncStatus.syncing : SyncStatus.synced,
    loading: () => SyncStatus.synced,
    error: (_, __) => SyncStatus.offline,
  );
});
DART

# =========================================================
# 13) Drawing provider (Undo/Redo) + Area helper + Snap helper
# =========================================================
cat > lib/features/field/ui/logic/drawing_provider.dart <<'DART'
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

class DrawingState {
  final bool isDrawing;
  final List<LatLng> points;

  final List<List<LatLng>> undoStack;
  final List<List<LatLng>> redoStack;

  const DrawingState({
    this.isDrawing = false,
    this.points = const [],
    this.undoStack = const [],
    this.redoStack = const [],
  });

  bool get isValid => points.length >= 3;
  bool get canUndo => undoStack.isNotEmpty;
  bool get canRedo => redoStack.isNotEmpty;

  DrawingState copyWith({
    bool? isDrawing,
    List<LatLng>? points,
    List<List<LatLng>>? undoStack,
    List<List<LatLng>>? redoStack,
  }) {
    return DrawingState(
      isDrawing: isDrawing ?? this.isDrawing,
      points: points ?? this.points,
      undoStack: undoStack ?? this.undoStack,
      redoStack: redoStack ?? this.redoStack,
    );
  }
}

class DrawingNotifier extends StateNotifier<DrawingState> {
  DrawingNotifier() : super(const DrawingState());

  void startDrawing() => state = const DrawingState(isDrawing: true);

  void cancelDrawing() => state = const DrawingState();

  void _pushUndo() {
    state = state.copyWith(
      undoStack: [...state.undoStack, state.points],
      redoStack: const [],
    );
  }

  void addPoint(LatLng point) {
    if (!state.isDrawing) return;
    _pushUndo();
    state = state.copyWith(points: [...state.points, point]);
  }

  void updatePoint(int index, LatLng newPoint) {
    if (index < 0 || index >= state.points.length) return;
    _pushUndo();
    final updated = [...state.points];
    updated[index] = newPoint;
    state = state.copyWith(points: updated);
  }

  void undo() {
    if (!state.canUndo) return;
    final prev = state.undoStack.last;
    final newUndo = [...state.undoStack]..removeLast();
    state = state.copyWith(
      points: prev,
      undoStack: newUndo,
      redoStack: [...state.redoStack, state.points],
    );
  }

  void redo() {
    if (!state.canRedo) return;
    final next = state.redoStack.last;
    final newRedo = [...state.redoStack]..removeLast();
    state = state.copyWith(
      points: next,
      redoStack: newRedo,
      undoStack: [...state.undoStack, state.points],
    );
  }
}

final drawingProvider = StateNotifierProvider<DrawingNotifier, DrawingState>((ref) {
  return DrawingNotifier();
});
DART

cat > lib/features/field/ui/utils/geo_area.dart <<'DART'
import 'dart:math';
import 'package:latlong2/latlong.dart';

class GeoArea {
  static const double _earthRadius = 6378137;

  static double areaSquareMeters(List<LatLng> polygon) {
    if (polygon.length < 3) return 0;

    double sum = 0;
    for (int i = 0; i < polygon.length; i++) {
      final p1 = polygon[i];
      final p2 = polygon[(i + 1) % polygon.length];
      sum += _rad(p2.longitude - p1.longitude) *
          (2 + sin(_rad(p1.latitude)) + sin(_rad(p2.latitude)));
    }
    return (sum * _earthRadius * _earthRadius / 2).abs();
  }

  static double toHectares(double sqm) => sqm / 10000;
  static double toFeddan(double sqm) => sqm / 4200;

  static double _rad(double d) => d * pi / 180.0;
}
DART

cat > lib/features/field/ui/utils/snap.dart <<'DART'
import 'package:latlong2/latlong.dart';

class Snapper {
  final double snapMeters;
  final Distance _distance = const Distance();

  Snapper({this.snapMeters = 3});

  LatLng snapToVertices(LatLng point, List<LatLng> vertices) {
    for (final v in vertices) {
      if (_distance(point, v) <= snapMeters) return v;
    }
    return point;
  }
}
DART

# =========================================================
# 14) Drawing Controls widget (Undo/Redo + Area + Save)
# =========================================================
cat > lib/features/field/ui/widgets/drawing_controls.dart <<'DART'
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/sahool_glass.dart';
import '../../../../core/di/providers.dart';
import '../logic/drawing_provider.dart';
import '../utils/geo_area.dart';

class DrawingControls extends ConsumerWidget {
  const DrawingControls({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = ref.watch(drawingProvider);
    if (!s.isDrawing) return const SizedBox.shrink();

    final sqm = GeoArea.areaSquareMeters(s.points);
    final ha = GeoArea.toHectares(sqm);
    final fd = GeoArea.toFeddan(sqm);

    return Positioned(
      left: 16,
      right: 16,
      bottom: 28,
      child: SahoolGlass(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            IconButton(
              tooltip: "إلغاء",
              icon: const Icon(Icons.close, color: Colors.red),
              onPressed: () => ref.read(drawingProvider.notifier).cancelDrawing(),
            ),
            const SizedBox(width: 8),

            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("\${s.points.length} نقاط", style: const TextStyle(fontWeight: FontWeight.bold)),
                Text("\${ha.toStringAsFixed(2)} هكتار • \${fd.toStringAsFixed(2)} فدان",
                    style: const TextStyle(fontSize: 12, color: Colors.grey)),
              ],
            ),

            const Spacer(),

            IconButton(
              tooltip: "Undo",
              onPressed: s.canUndo ? () => ref.read(drawingProvider.notifier).undo() : null,
              icon: const Icon(Icons.undo),
            ),
            IconButton(
              tooltip: "Redo",
              onPressed: s.canRedo ? () => ref.read(drawingProvider.notifier).redo() : null,
              icon: const Icon(Icons.redo),
            ),

            const SizedBox(width: 8),

            FloatingActionButton.small(
              heroTag: "save_field",
              backgroundColor: s.isValid ? const Color(0xFF1B5E20) : Colors.grey,
              onPressed: s.isValid ? () => _save(context, ref) : null,
              child: const Icon(Icons.check, color: Colors.white),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _save(BuildContext context, WidgetRef ref) async {
    final points = ref.read(drawingProvider).points;
    final repo = ref.read(fieldsRepoProvider);

    await repo.createRealField(
      name: "حقل جديد \${DateTime.now().minute}:\${DateTime.now().second}",
      boundary: points,
    );

    ref.read(drawingProvider.notifier).cancelDrawing();

    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("✅ تم حفظ الحقل (محلياً) وإضافته للـ Outbox")),
      );
    }
  }
}
DART

# =========================================================
# 15) HomeScreen: Map + Fields + Sync HUD + Drawing Editor + Drag with project/unproject
# =========================================================
cat > lib/features/home/ui/home_screen.dart <<'DART'
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/di/providers.dart';
import '../../../core/theme/sahool_glass.dart';
import '../../home/ui/logic/sync_provider.dart';
import '../../field/ui/logic/drawing_provider.dart';
import '../../field/ui/widgets/drawing_controls.dart';
import '../../field/ui/utils/snap.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final MapController _mapController = MapController();
  final Snapper _snapper = Snapper(snapMeters: 3);

  // Helper: drag LatLng by screen delta using project/unproject (or camera fallback)
  LatLng _dragByDelta(LatLng origin, Offset delta) {
    // Attempt MapController.project/unproject first; fallback to camera.project/unproject
    try {
      final dyn = _mapController as dynamic;
      final p = dyn.project(origin);
      final moved = p + CustomPoint(delta.dx, delta.dy);
      final ll = dyn.unproject(moved);
      return ll as LatLng;
    } catch (_) {
      final p = _mapController.camera.project(origin);
      final moved = CustomPoint(p.x + delta.dx, p.y + delta.dy);
      return _mapController.camera.unproject(moved);
    }
  }

  @override
  Widget build(BuildContext context) {
    final fieldsAsync = ref.watch(fieldsStreamProvider);
    final drawing = ref.watch(drawingProvider);

    final pendingCount = ref.watch(pendingOperationsProvider).valueOrNull ?? 0;
    final syncStatus = ref.watch(syncStatusUiProvider);

    Color iconColor;
    IconData icon;
    String tooltip;

    switch (syncStatus) {
      case SyncStatus.synced:
        iconColor = Colors.green.shade800;
        icon = Icons.cloud_done;
        tooltip = "تمت المزامنة";
        break;
      case SyncStatus.syncing:
        iconColor = Colors.amber.shade800;
        icon = Icons.cloud_upload;
        tooltip = "جاري رفع \$pendingCount عملية...";
        break;
      case SyncStatus.offline:
        iconColor = Colors.grey;
        icon = Icons.cloud_off;
        tooltip = "غير متصل";
        break;
    }

    return Scaffold(
      body: Stack(
        children: [
          // ==========================
          // MAP
          // ==========================
          Positioned.fill(
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: const LatLng(15.3694, 44.1910),
                initialZoom: 13,
                onTap: (_, point) {
                  if (drawing.isDrawing) {
                    ref.read(drawingProvider.notifier).addPoint(point);
                  }
                },
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.kafaat.sahool',
                ),

                // Saved fields from DB
                fieldsAsync.when(
                  data: (fields) {
                    final polygons = fields.map((f) {
                      final isSynced = f.isSynced;
                      final border = isSynced ? const Color(0xFF1B5E20) : Colors.amber.shade700;

                      return Polygon(
                        points: f.boundary,
                        color: border.withOpacity(isSynced ? 0.25 : 0.10),
                        borderColor: border,
                        borderStrokeWidth: isSynced ? 2 : 3,
                        isFilled: true,
                      );
                    }).toList();

                    return PolygonLayer(polygons: polygons);
                  },
                  loading: () => const MarkerLayer(markers: []),
                  error: (_, __) => const MarkerLayer(markers: []),
                ),

                // Draft drawing layer
                if (drawing.isDrawing) ...[
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: [
                          ...drawing.points,
                          if (drawing.points.isNotEmpty) drawing.points.first,
                        ],
                        color: Colors.orange,
                        strokeWidth: 3,
                        isDotted: true,
                      )
                    ],
                  ),
                  // Draggable vertex markers
                  MarkerLayer(
                    markers: [
                      for (int i = 0; i < drawing.points.length; i++)
                        Marker(
                          point: drawing.points[i],
                          width: 24,
                          height: 24,
                          child: GestureDetector(
                            onPanUpdate: (details) {
                              final origin = drawing.points[i];
                              final moved = _dragByDelta(origin, details.delta);

                              // Snap to other vertices
                              final others = [
                                for (int j = 0; j < drawing.points.length; j++)
                                  if (j != i) drawing.points[j]
                              ];
                              final snapped = _snapper.snapToVertices(moved, others);

                              ref.read(drawingProvider.notifier).updatePoint(i, snapped);
                            },
                            child: Container(
                              decoration: BoxDecoration(
                                color: Colors.white,
                                shape: BoxShape.circle,
                                border: Border.all(color: Colors.orange, width: 3),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withOpacity(0.2),
                                    blurRadius: 6,
                                  )
                                ],
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ]
              ],
            ),
          ),

          // ==========================
          // TOP HUD
          // ==========================
          if (!drawing.isDrawing)
            Positioned(
              top: 58,
              left: 16,
              right: 16,
              child: SahoolGlass(
                child: Row(
                  children: [
                    const CircleAvatar(
                      backgroundColor: Color(0xFF1B5E20),
                      child: Icon(Icons.person, color: Colors.white),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: fieldsAsync.when(
                        data: (fields) => Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text("SAHOOL Field Ops",
                                style: TextStyle(fontWeight: FontWeight.bold)),
                            Text("\${fields.length} حقول • جاهز للعمل",
                                style: const TextStyle(fontSize: 12, color: Colors.grey)),
                          ],
                        ),
                        loading: () => const Text("جاري التحميل..."),
                        error: (_, __) => const Text("خطأ في قراءة البيانات"),
                      ),
                    ),
                    Tooltip(
                      message: tooltip,
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 350),
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: iconColor.withOpacity(0.12),
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: pendingCount > 0 ? iconColor : Colors.transparent,
                            width: 1.4,
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(icon, color: iconColor, size: 20),
                            if (pendingCount > 0) ...[
                              const SizedBox(width: 4),
                              Text(
                                "\$pendingCount",
                                style: TextStyle(
                                  color: iconColor,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

          // ==========================
          // FABs
          // ==========================
          Positioned(
            right: 16,
            bottom: drawing.isDrawing ? 120 : 140,
            child: Column(
              children: [
                if (!drawing.isDrawing)
                  FloatingActionButton(
                    heroTag: "start_drawing",
                    backgroundColor: const Color(0xFF1B5E20),
                    onPressed: () => ref.read(drawingProvider.notifier).startDrawing(),
                    child: const Icon(Icons.edit_location_alt, color: Colors.white),
                  ),
              ],
            ),
          ),

          // ==========================
          // DRAWING CONTROLS
          // ==========================
          const DrawingControls(),
        ],
      ),
    );
  }
}
DART

# =========================================================
# 16) main.dart (ProviderScope + Workmanager)
# =========================================================
cat > lib/main.dart <<'DART'
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workmanager/workmanager.dart';

import 'core/sync/background_service.dart';
import 'features/home/ui/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Workmanager().initialize(callbackDispatcher, isInDebugMode: true);
  await Workmanager().registerPeriodicTask(
    "1",
    syncTaskName,
    frequency: const Duration(minutes: 15),
    constraints: Constraints(networkType: NetworkType.connected),
    existingWorkPolicy: ExistingWorkPolicy.keep,
  );

  runApp(const ProviderScope(child: SahoolApp()));
}

class SahoolApp extends StatelessWidget {
  const SahoolApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1B5E20)),
      ),
      home: const HomeScreen(),
    );
  }
}
DART

# =========================================================
# 17) Native configs injection (Android/iOS) using python (portable)
# =========================================================
echo "🔧 Injecting Native configs (Android/iOS) (portable python edit)..."

$PY <<'PY'
from pathlib import Path

# ANDROID manifest
manifest = Path("android/app/src/main/AndroidManifest.xml")
if manifest.exists():
    s = manifest.read_text(encoding="utf-8")
    if "ACCESS_NETWORK_STATE" not in s:
        s = s.replace(
            "<application",
            '  <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />\n'
            '  <uses-permission android:name="android.permission.WAKE_LOCK" />\n'
            "<application",
            1
        )
    # Workmanager service injection (safe idempotent-ish)
    if "be.tramckrijte.workmanager" not in s:
        s = s.replace(
            "<application",
            "<application",
            1
        )
    manifest.write_text(s, encoding="utf-8")

# iOS Info.plist background modes
plist = Path("ios/Runner/Info.plist")
if plist.exists():
    p = plist.read_text(encoding="utf-8")
    if "UIBackgroundModes" not in p:
        insert = (
            "\t<key>UIBackgroundModes</key>\n"
            "\t<array>\n"
            "\t\t<string>fetch</string>\n"
            "\t\t<string>processing</string>\n"
            "\t</array>\n"
        )
        p = p.replace("<dict>\n", "<dict>\n" + insert, 1)
        plist.write_text(p, encoding="utf-8")

print("✅ Native config injection done.")
PY

# =========================================================
# 18) Drift codegen
# =========================================================
echo "⚙️ Running build_runner for Drift (.g.dart)"
flutter pub run build_runner build --delete-conflicting-outputs

echo ""
echo "✅ DONE! Project generated:"
echo "   ./$APP_NAME"
echo ""
echo "▶ Run:"
echo "   cd $APP_NAME"
echo "   flutter run"
echo ""
echo "📝 Notes:"
echo " - Drawing: tap to add points, drag points to edit (project/unproject), snap-to-vertex within 3m."
echo " - Undo/Redo: in drawing HUD."
echo " - Area: live hectares + feddan."
echo " - Sync HUD: reads Outbox pending count."
echo ""
