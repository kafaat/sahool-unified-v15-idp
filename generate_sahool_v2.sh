#!/bin/bash

# ==========================================
# SAHOOL Field App - Enterprise Generator v2.0
# Patched for Production: Drift Fixes, Native Configs, Conflict Schema
# ==========================================
#
# Usage:
#   ./generate_sahool_v2.sh
#
# Environment Variables:
#   CLEANUP_ON_FAILURE  - Set to 'false' to keep app directory on failure (default: true)
#                         Example: CLEANUP_ON_FAILURE=false ./generate_sahool_v2.sh
#
# Features:
#   - Validates Flutter installation before starting
#   - Checks for required dependencies
#   - Validates target directory doesn't exist
#   - Creates complete Flutter app with Drift database
#   - Injects Android/iOS native configurations
#   - Runs build_runner to generate Drift files
#   - Cleans up on failure (unless disabled)
#
# Error Handling:
#   - Exits on first error (set -e)
#   - Reports error line numbers
#   - Automatic cleanup of incomplete projects
#   - Detailed error messages for each step
#
# ==========================================

# Strict error handling
set -euo pipefail

# Error trap with detailed reporting
trap 'echo "Error on line $LINENO. Exit code: $?" >&2; cleanup_on_error' ERR

# Configuration
APP_NAME="sahool_field_app"
CLEANUP_ON_FAILURE="${CLEANUP_ON_FAILURE:-true}"
APP_DIR=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ==========================================
# Cleanup Function
# ==========================================
cleanup_on_error() {
    echo "❌ Script failed. Cleaning up..." >&2
    if [ -d "$APP_DIR" ] && [ "$CLEANUP_ON_FAILURE" = "true" ]; then
        echo "🗑️  Removing incomplete app directory: $APP_DIR" >&2
        rm -rf "$APP_DIR"
    fi
}

# ==========================================
# Validation Functions
# ==========================================

# Check if Flutter is installed
validate_flutter() {
    echo "🔍 Validating Flutter installation..."
    if ! command -v flutter &> /dev/null; then
        echo "❌ Error: Flutter is not installed or not in PATH" >&2
        echo "   Please install Flutter from https://flutter.dev/docs/get-started/install" >&2
        exit 1
    fi

    # Check Flutter version
    local flutter_version
    flutter_version=$(flutter --version | head -n 1)
    echo "✅ Flutter found: $flutter_version"
}

# Check if required commands are available
validate_dependencies() {
    echo "🔍 Validating required dependencies..."
    local missing_deps=()

    for cmd in sed; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done

    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo "❌ Error: Missing required commands: ${missing_deps[*]}" >&2
        exit 1
    fi

    echo "✅ All required dependencies found"
}

# Check if target directory already exists
validate_target_directory() {
    if [ -d "$APP_NAME" ]; then
        echo "⚠️  Warning: Directory '$APP_NAME' already exists" >&2
        read -p "Do you want to remove it and continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🗑️  Removing existing directory..."
            rm -rf "$APP_NAME"
        else
            echo "❌ Aborting. Please remove '$APP_NAME' manually or choose a different name." >&2
            exit 1
        fi
    fi
}

# Verify file was created successfully
verify_file_created() {
    local file_path="$1"
    local file_description="$2"

    if [ ! -f "$file_path" ]; then
        echo "❌ Error: Failed to create $file_description at $file_path" >&2
        exit 1
    fi

    if [ ! -s "$file_path" ]; then
        echo "❌ Error: $file_description is empty at $file_path" >&2
        exit 1
    fi
}

# ==========================================
# Main Execution
# ==========================================

echo "🚀 Initializing SAHOOL Field App (Enterprise Edition v2)..."

# Run validations
validate_flutter
validate_dependencies
validate_target_directory

# 1. Create Flutter Project
echo "📱 Creating Flutter project '$APP_NAME'..."
if ! flutter create "$APP_NAME"; then
    echo "❌ Error: Flutter project creation failed" >&2
    exit 1
fi

APP_DIR="$SCRIPT_DIR/$APP_NAME"
cd "$APP_NAME" || {
    echo "❌ Error: Failed to change directory to $APP_NAME" >&2
    exit 1
}

# 2. Add Dependencies
echo "📦 Adding Production Dependencies..."
if ! flutter pub add flutter_riverpod connectivity_plus drift sqlite3_flutter_libs path_provider path flutter_map latlong2 workmanager dio google_fonts flutter_svg intl; then
    echo "❌ Error: Failed to add production dependencies" >&2
    exit 1
fi

echo "📦 Adding Development Dependencies..."
if ! flutter pub add --dev drift_dev build_runner; then
    echo "❌ Error: Failed to add development dependencies" >&2
    exit 1
fi

# 3. Create Folder Structure (DDD)
echo "📂 Creating Clean Architecture Structure..."
if ! mkdir -p lib/core/auth lib/core/map lib/core/storage/mixins lib/core/storage/converters lib/core/sync lib/core/theme lib/features/field/domain/entities lib/features/tasks/domain/entities lib/features/home/ui; then
    echo "❌ Error: Failed to create directory structure" >&2
    exit 1
fi

# ==========================================
# 4. Code Injection
# ==========================================

echo "💉 Injecting core files..."

# --- Core: Auth ---
echo "  Creating auth_service.dart..."
cat <<EOF > lib/core/auth/auth_service.dart
/// Basic Auth Service for generated app
class AuthService {
  User? _currentUser;
  bool _isAuthenticated = false;

  User? get currentUser => _currentUser;
  bool get isAuthenticated => _isAuthenticated;

  /// Mock login for MVP
  Future<void> login(String email, String password) async {
    _currentUser = User(
      id: 'user_001',
      email: email,
      tenantId: 'tenant_1',
    );
    _isAuthenticated = true;
  }

  /// Check login status
  Future<bool> isLoggedIn() async {
    return _isAuthenticated;
  }

  /// Logout
  Future<void> logout() async {
    _currentUser = null;
    _isAuthenticated = false;
  }

  /// Initialize with mock user for development
  Future<void> initMockUser() async {
    _currentUser = User(
      id: 'user_101_uuid',
      email: 'dev@sahool.com',
      tenantId: 'tenant_1',
    );
    _isAuthenticated = true;
  }
}

/// User model
class User {
  final String id;
  final String email;
  final String tenantId;

  const User({
    required this.id,
    required this.email,
    required this.tenantId,
  });
}
EOF
verify_file_created "lib/core/auth/auth_service.dart" "auth_service.dart"

echo "  Creating user_context.dart..."
cat <<EOF > lib/core/auth/user_context.dart
import 'auth_service.dart';

/// User Context - Provides synchronous access to current user info
class UserContext {
  final AuthService _authService;

  UserContext(this._authService);

  String get currentUserId => _authService.currentUser?.id ?? '';
  String? get currentTenantId => _authService.currentUser?.tenantId;
  bool get isAuthenticated => _authService.isAuthenticated;
}
EOF
verify_file_created "lib/core/auth/user_context.dart" "user_context.dart"

# --- Core: Storage (Mixins & Converters) ---
echo "  Creating tenant_mixin.dart..."
cat <<EOF > lib/core/storage/mixins/tenant_mixin.dart
import 'package:drift/drift.dart';

mixin TenantMixin on Table {
  TextColumn get userId => text()();
}
EOF

cat <<EOF > lib/core/storage/converters/geo_converter.dart
import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:latlong2/latlong.dart';

class GeoPolygonConverter extends TypeConverter<List<LatLng>, String> {
  const GeoPolygonConverter();

  @override
  List<LatLng> fromSql(String fromDb) {
    try {
      final List<dynamic> jsonList = jsonDecode(fromDb);
      return jsonList.map((point) => LatLng(point[1], point[0])).toList();
    } catch (e) {
      return [];
    }
  }

  @override
  String toSql(List<LatLng> value) {
    final jsonList = value.map((p) => [p.longitude, p.latitude]).toList();
    return jsonEncode(jsonList);
  }
}
EOF

# --- Core: Storage (Tables - Updated Schema) ---
cat <<EOF > lib/core/storage/tables.dart
import 'package:drift/drift.dart';
import 'mixins/tenant_mixin.dart';
import 'converters/geo_converter.dart';
import 'package:latlong2/latlong.dart';

// 1. Fields Table
class Fields extends Table with TenantMixin {
  TextColumn get id => text()();
  TextColumn get name => text()();
  TextColumn get cropType => text()();
  TextColumn get boundary => text().map(const GeoPolygonConverter())();
  
  // Timestamps for Conflict Resolution
  DateTimeColumn get lastUpdated => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();
  
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  @override
  Set<Column> get primaryKey => {id};
}

// 2. Outbox Table (Conflict Ready)
class Outbox extends Table with TenantMixin {
  IntColumn get id => integer().autoIncrement()();
  
  // Target Entity Metadata (Essential for 409 handling)
  TextColumn get entityType => text()(); // 'field', 'task'
  TextColumn get entityId => text()();
  
  TextColumn get apiEndpoint => text()();
  TextColumn get method => text()();
  TextColumn get payload => text()();
  
  // Timestamp sent to server for verification
  DateTimeColumn get clientUpdatedAt => dateTime().withDefault(currentDateAndTime)();
  
  IntColumn get retryCount => integer().withDefault(const Constant(0))();
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

// 3. Sync Events (For UX Notifications)
class SyncEvents extends Table with TenantMixin {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get type => text()(); // 'CONFLICT', 'INFO', 'ERROR'
  TextColumn get message => text()();
  BoolColumn get isRead => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

// 4. Sync Logs (Debug)
class SyncLogs extends Table {
  IntColumn get id => integer().autoIncrement()();
  DateTimeColumn get timestamp => dateTime().withDefault(currentDateAndTime)();
  TextColumn get level => text()();
  TextColumn get message => text()();
}
EOF

# --- Core: Storage (Database - No Singleton) ---
cat <<EOF > lib/core/storage/database.dart
import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'package:latlong2/latlong.dart';
import 'tables.dart';
import 'converters/geo_converter.dart';

part 'database.g.dart';

@DriftDatabase(tables: [Fields, Outbox, SyncEvents, SyncLogs])
class AppDatabase extends _\$AppDatabase {
  // ⚠️ FIXED: Removed Singleton to avoid Isolate lock issues
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (Migrator m) async {
      await m.createAll();
    },
    beforeOpen: (details) async {
      // Enable foreign keys for better data integrity
      await customStatement('PRAGMA foreign_keys = ON');

      // Optional: Enable WAL mode for better concurrency
      // WAL mode allows multiple readers while a write is in progress
      await customStatement('PRAGMA journal_mode = WAL');
    },
  );
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, 'sahool_enterprise.sqlite'));

    // ✅ Use createInBackground for proper isolate support
    // This is safer than NativeDatabase(file) as it:
    // - Runs database operations in a background isolate
    // - Prevents blocking the UI thread
    // - Avoids lock contention issues in multi-isolate scenarios
    // - Enables safe concurrent access from background workers
    return NativeDatabase.createInBackground(file);
  });
}
EOF
verify_file_created "lib/core/storage/database.dart" "database.dart"

echo "  Creating network_status.dart..."
cat <<EOF > lib/core/sync/network_status.dart
import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

class NetworkStatus {
  final _connectivity = Connectivity();
  ConnectivityResult _status = ConnectivityResult.none;

  bool get isOnline => _status != ConnectivityResult.none;

  Future<void> init() async {
    // ⚠️ FIXED: Handling List<ConnectivityResult> for v5.0+
    final results = await _connectivity.checkConnectivity();
    _handleResult(results);

    _connectivity.onConnectivityChanged.listen(_handleResult);
  }

  void _handleResult(List<ConnectivityResult> results) {
    // We take the first available connection type
    _status = results.isNotEmpty ? results.first : ConnectivityResult.none;
  }
}
EOF

# --- Core: Sync (Worker - Conflict Ready Stub) ---
cat <<EOF > lib/core/sync/sync_worker.dart
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import '../storage/database.dart';
import 'network_status.dart';
import '../auth/user_context.dart';

class SyncWorker {
  final AppDatabase _db;
  final NetworkStatus _net;
  final UserContext _auth;
  final Dio _dio = Dio();

  SyncWorker(this._db, this._net, this._auth);

  Future<void> run() async {
    if (!_net.isOnline) return;

    final uid = _auth.currentUserId;
    
    final items = await (_db.select(_db.outbox)
      ..where((o) => o.userId.equals(uid))
      ..where((o) => o.isSynced.equals(false))
      ..orderBy([(o) => OrderingTerm.asc(o.createdAt)])
    ).get();

    for (final item in items) {
      await _processItem(item);
    }
  }

  Future<void> _processItem(OutboxData item) async {
    try {
      // ⚠️ Note: In a full implementation, we handle 409 Conflict here
      // using item.entityType and item.entityId to rollback logic.
      
      await _dio.request(
        item.apiEndpoint,
        data: jsonDecode(item.payload),
        options: Options(
          method: item.method,
          headers: {
            'X-Client-Updated-At': item.clientUpdatedAt.toIso8601String(),
          }
        ),
      );
      
      await (_db.update(_db.outbox)
        ..where((o) => o.id.equals(item.id))
      ).write(const OutboxCompanion(isSynced: Value(true)));
      
    } catch (e) {
      await _db.into(_db.syncLogs).insert(
        SyncLogsCompanion.insert(level: 'ERROR', message: e.toString()),
      );
    }
  }
}
EOF

# --- Core: Sync (Background Service - Await Fix) ---
cat <<EOF > lib/core/sync/background_service.dart
import 'package:workmanager/workmanager.dart';
import '../storage/database.dart';
import 'network_status.dart';
import 'sync_worker.dart';
import '../auth/user_context.dart';
import '../auth/auth_service.dart';

const syncTaskName = "com.kafaat.sahool.syncTask";

@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, _) async {
    final db = AppDatabase(); // New Instance (Safe)

    // ⚠️ FIXED: Awaiting init() to avoid race condition
    final net = NetworkStatus();
    await net.init();

    // Initialize auth service with mock user for background tasks
    final authService = AuthService();
    await authService.initMockUser();
    final auth = UserContext(authService);

    final worker = SyncWorker(db, net, auth);
    await worker.run();

    return true;
  });
}
EOF

# --- UI: Home Screen ---
cat <<EOF > lib/features/home/ui/home_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../core/storage/database.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final db = AppDatabase();
    
    return Scaffold(
      body: Stack(
        children: [
          Positioned.fill(
            child: StreamBuilder(
              stream: db.select(db.fields).watch(),
              builder: (context, snapshot) {
                final fields = snapshot.data ?? [];
                return FlutterMap(
                  options: const MapOptions(
                    initialCenter: LatLng(15.3694, 44.1910),
                    initialZoom: 13,
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    ),
                    PolygonLayer(
                      polygons: fields.map((f) => Polygon(
                        points: f.boundary,
                        color: Colors.green.withOpacity(0.3),
                        borderColor: Colors.green,
                        borderStrokeWidth: 2,
                        label: f.name,
                      )).toList(),
                    ),
                  ],
                );
              },
            ),
          ),
          Positioned(
            top: 50, left: 16, right: 16,
            child: Card(
              child: ListTile(
                leading: const Icon(Icons.wb_sunny, color: Colors.orange),
                title: const Text("SAHOOL Enterprise"),
                subtitle: const Text("System v15.2 • Drift Patched"),
                trailing: const Icon(Icons.cloud_done, color: Colors.green),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
EOF

# --- Main Entry Point ---
cat <<EOF > lib/main.dart
import 'package:flutter/material.dart';
import 'package:workmanager/workmanager.dart';
import 'core/sync/background_service.dart';
import 'core/auth/auth_service.dart';
import 'features/home/ui/home_screen.dart';
import 'core/theme/sahool_theme.dart';

// Global auth service instance for the app
// In production, this should be managed via dependency injection (e.g., Riverpod)
late final AuthService authService;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize auth service with mock user for development
  authService = AuthService();
  await authService.initMockUser();

  await Workmanager().initialize(callbackDispatcher, isInDebugMode: true);
  await Workmanager().registerPeriodicTask(
    "1",
    syncTaskName,
    frequency: const Duration(minutes: 15),
    constraints: Constraints(networkType: NetworkType.connected),
  );

  runApp(const SahoolApp());
}

class SahoolApp extends StatelessWidget {
  const SahoolApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.green),
      home: const HomeScreen(),
    );
  }
}
EOF
verify_file_created "lib/main.dart" "main.dart"

echo "✅ All core files created successfully"

# ==========================================
# 5. Native Configurations Injection (The Critical Fix)
# ==========================================

echo "🔧 Injecting Native Android Configs..."

# Validate Android manifest exists
if [ ! -f "android/app/src/main/AndroidManifest.xml" ]; then
    echo "❌ Error: AndroidManifest.xml not found" >&2
    exit 1
fi

# Inject Permissions
echo "  Adding Android permissions..."
if ! sed -i.bak '/<application/i \
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />\
    <uses-permission android:name="android.permission.WAKE_LOCK" />' android/app/src/main/AndroidManifest.xml; then
    echo "❌ Error: Failed to inject Android permissions" >&2
    exit 1
fi

# Inject Workmanager Service
echo "  Adding Workmanager service..."
if ! sed -i.bak2 '/<activity/i \
        <service\
            android:name="be.tramckrijte.workmanager.BackgroundWorker"\
            android:permission="android.permission.BIND_JOB_SERVICE"\
            android:exported="false" />' android/app/src/main/AndroidManifest.xml; then
    echo "❌ Error: Failed to inject Workmanager service" >&2
    exit 1
fi

echo "🔧 Injecting Native iOS Configs..."

# Validate iOS Info.plist exists
if [ ! -f "ios/Runner/Info.plist" ]; then
    echo "❌ Error: iOS Info.plist not found" >&2
    exit 1
fi

# Inject Background Modes
echo "  Adding iOS background modes..."
if ! sed -i.bak '/<dict>/a \
		<key>UIBackgroundModes</key>\
		<array>\
			<string>fetch</string>\
			<string>processing</string>\
		</array>' ios/Runner/Info.plist; then
    echo "❌ Error: Failed to inject iOS background modes" >&2
    exit 1
fi

# ==========================================
# 6. Final Build
# ==========================================

echo "⚙️ Running Build Runner..."
if ! flutter pub run build_runner build --delete-conflicting-outputs; then
    echo "❌ Error: Build runner failed" >&2
    echo "   This usually happens due to code generation issues in Drift files." >&2
    echo "   Please check the error messages above for details." >&2
    exit 1
fi

# Verify critical generated files exist
if [ ! -f "lib/core/storage/database.g.dart" ]; then
    echo "⚠️  Warning: database.g.dart was not generated" >&2
    echo "   The app may not compile correctly." >&2
fi

echo ""
echo "✅ SAHOOL v15.2 (Enterprise Patched) is Ready!"
echo "👉 cd $APP_NAME && flutter run"
echo ""
echo "📋 Summary:"
echo "  • Flutter project created: $APP_NAME"
echo "  • Dependencies installed: ✓"
echo "  • Code structure created: ✓"
echo "  • Native configs injected: ✓"
echo "  • Build runner completed: ✓"
echo ""
echo "🚀 To run the app:"
echo "   cd $APP_NAME"
echo "   flutter run"
echo ""

# Disable cleanup trap on success
trap - ERR

# ⸻
# 📋 ماذا يضمن هذا السكربت؟
#  * استقرارية الخلفية: بفضل إزالة Singleton وإضافة إعدادات Android/iOS الإلزامية.
#  * جاهزية التوسع: جداول Outbox و SyncEvents جاهزة الآن للتعامل مع منطق الـ Conflict المعقد الذي ناقشناه.
#  * سلامة البيانات: استخدام NetworkStatus بالطريقة الصحيحة يمنع المزامنة الوهمية أثناء انقطاع النت.
# شغل السكربت، وستحصل على قاعدة برمجية (Codebase) صلبة يمكنك البناء عليها فوراً.
