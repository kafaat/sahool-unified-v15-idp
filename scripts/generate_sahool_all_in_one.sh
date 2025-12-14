#!/usr/bin/env bash
set -euo pipefail

APP_NAME="sahool_field_app"
BACKEND_DIR="backend"
OVERRIDE_COMPOSE="docker-compose.sahool-fields.yml"

echo "===================================================="
echo "🚀 SAHOOL ALL-IN-ONE (Mobile + Backend + PostGIS)"
echo "===================================================="

# --------------------------
# 0) Preconditions
# --------------------------
if ! command -v flutter >/dev/null 2>&1; then
  echo "❌ Flutter not found in PATH"
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Docker not found in PATH"
  exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
  echo "❌ docker-compose.yml not found in current directory"
  echo "👉 شغّل السكربت من جذر المشروع الذي يحتوي docker-compose.yml"
  exit 1
fi

# --------------------------
# 1) Backend (Node + PostGIS + ETag/If-Match/409)
# --------------------------
echo "🧱 Creating backend in ./$BACKEND_DIR ..."

mkdir -p "$BACKEND_DIR/src"/{db,utils,services,routes}
mkdir -p "$BACKEND_DIR/migrations"

cat <<'EOF' > "$BACKEND_DIR/package.json"
{
  "name": "sahool-backend",
  "type": "module",
  "scripts": {
    "start": "node src/server.js"
  },
  "dependencies": {
    "express": "^4.19.2",
    "pg": "^8.11.5",
    "cors": "^2.8.5"
  }
}
EOF

cat <<'EOF' > "$BACKEND_DIR/Dockerfile"
FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY src ./src
EXPOSE 8080
CMD ["npm","start"]
EOF

cat <<'EOF' > "$BACKEND_DIR/migrations/001_init.sql"
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS fields (
  id          TEXT PRIMARY KEY,
  tenant_id   TEXT NOT NULL,
  name        TEXT NOT NULL,
  crop_type   TEXT NOT NULL DEFAULT 'unknown',
  boundary    geometry(Polygon, 4326) NOT NULL,
  version     BIGINT NOT NULL DEFAULT 1,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fields_tenant ON fields(tenant_id);
EOF

cat <<'EOF' > "$BACKEND_DIR/src/db/pool.js"
import pg from "pg";
export default new pg.Pool({ connectionString: process.env.DATABASE_URL });
EOF

cat <<'EOF' > "$BACKEND_DIR/src/utils/etag.js"
import crypto from "crypto";
export const etagOf = (r) =>
  crypto.createHash("sha1")
    .update(`${r.id}:${r.version}:${r.updated_at}`)
    .digest("hex");
EOF

cat <<'EOF' > "$BACKEND_DIR/src/services/fields.service.js"
import db from "../db/pool.js";

export async function get(tenantId, id) {
  const { rows } = await db.query(
    "SELECT id, tenant_id, name, crop_type, version, updated_at, " +
    "ST_AsGeoJSON(boundary)::json AS boundary_geojson " +
    "FROM fields WHERE tenant_id=$1 AND id=$2",
    [tenantId, id]
  );
  return rows[0];
}

export async function list(tenantId) {
  const { rows } = await db.query(
    "SELECT id, tenant_id, name, crop_type, version, updated_at, " +
    "ST_AsGeoJSON(boundary)::json AS boundary_geojson " +
    "FROM fields WHERE tenant_id=$1 ORDER BY updated_at DESC",
    [tenantId]
  );
  return rows;
}

// boundary: [{lat,lng}, ...]
function toWktPolygon(boundary) {
  if (!Array.isArray(boundary) || boundary.length < 3) {
    throw new Error("Invalid boundary: need at least 3 points");
  }
  const pts = boundary.map(p => `${p.lng} ${p.lat}`);
  // close polygon
  if (pts[0] !== pts[pts.length - 1]) pts.push(pts[0]);
  return `POLYGON((${pts.join(",")}))`;
}

export async function create({ tenantId, id, name, cropType, boundary }) {
  const wkt = toWktPolygon(boundary);
  const { rows } = await db.query(
    "INSERT INTO fields(id, tenant_id, name, crop_type, boundary) " +
    "VALUES ($1,$2,$3,$4, ST_GeomFromText($5,4326)) " +
    "RETURNING id, tenant_id, name, crop_type, version, updated_at, " +
    "ST_AsGeoJSON(boundary)::json AS boundary_geojson",
    [id, tenantId, name, cropType ?? "unknown", wkt]
  );
  return rows[0];
}

export async function update(tenantId, id, { name, cropType, boundary }) {
  const wkt = boundary ? toWktPolygon(boundary) : null;

  const { rows } = await db.query(
    "UPDATE fields SET " +
    "name = COALESCE($1, name), " +
    "crop_type = COALESCE($2, crop_type), " +
    "boundary = COALESCE(ST_GeomFromText($3,4326), boundary), " +
    "version = version + 1, " +
    "updated_at = now() " +
    "WHERE tenant_id=$4 AND id=$5 " +
    "RETURNING id, tenant_id, name, crop_type, version, updated_at, " +
    "ST_AsGeoJSON(boundary)::json AS boundary_geojson",
    [name ?? null, cropType ?? null, wkt, tenantId, id]
  );
  return rows[0];
}
EOF

cat <<'EOF' > "$BACKEND_DIR/src/routes/fields.routes.js"
import { Router } from "express";
import * as s from "../services/fields.service.js";
import { etagOf } from "../utils/etag.js";

const r = Router();

// Multi-tenant via header (MVP): X-Tenant-Id
function tenant(req) {
  const t = req.header("X-Tenant-Id");
  if (!t) return null;
  return t;
}

r.get("/", async (req, res) => {
  const t = tenant(req);
  if (!t) return res.status(400).json({ error: "Missing X-Tenant-Id" });
  const rows = await s.list(t);
  res.json(rows);
});

r.post("/", async (req, res) => {
  const t = tenant(req);
  if (!t) return res.status(400).json({ error: "Missing X-Tenant-Id" });

  const body = req.body || {};
  const row = await s.create({
    tenantId: t,
    id: body.id,
    name: body.name,
    cropType: body.cropType,
    boundary: body.boundary
  });

  res.status(201).set("ETag", etagOf(row)).json(row);
});

r.get("/:id", async (req, res) => {
  const t = tenant(req);
  if (!t) return res.status(400).json({ error: "Missing X-Tenant-Id" });

  const row = await s.get(t, req.params.id);
  if (!row) return res.sendStatus(404);

  res.set("ETag", etagOf(row)).json(row);
});

r.put("/:id", async (req, res) => {
  const t = tenant(req);
  if (!t) return res.status(400).json({ error: "Missing X-Tenant-Id" });

  const cur = await s.get(t, req.params.id);
  if (!cur) return res.sendStatus(404);

  const ifMatch = req.header("If-Match");
  const curEtag = etagOf(cur);

  // 409 Conflict (Server authoritative)
  if (!ifMatch || ifMatch !== curEtag) {
    return res.status(409).json({ server: cur, etag: curEtag });
  }

  const up = await s.update(t, req.params.id, req.body || {});
  res.set("ETag", etagOf(up)).json(up);
});

export default r;
EOF

cat <<'EOF' > "$BACKEND_DIR/src/app.js"
import express from "express";
import cors from "cors";
import fields from "./routes/fields.routes.js";

const app = express();
app.use(cors());
app.use(express.json({ limit: "2mb" }));
app.get("/health", (_, res) => res.json({ ok: true }));
app.use("/api/v1/fields", fields);

export default app;
EOF

cat <<'EOF' > "$BACKEND_DIR/src/server.js"
import app from "./app.js";
const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`SAHOOL Backend listening on :${port}`));
EOF

# --------------------------
# 2) Docker compose override (PostGIS + Backend)
# --------------------------
echo "🐳 Writing Docker Compose override: $OVERRIDE_COMPOSE"

cat <<'EOF' > "$OVERRIDE_COMPOSE"
services:
  sahool_postgis:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: sahool
      POSTGRES_USER: sahool
      POSTGRES_PASSWORD: sahool
    ports:
      - "5436:5432"
    volumes:
      - sahool_postgis_data:/var/lib/postgresql/data
      - ./backend/migrations:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sahool -d sahool"]
      interval: 5s
      timeout: 3s
      retries: 30

  sahool_backend:
    build:
      context: ./backend
    environment:
      PORT: 8080
      DATABASE_URL: postgres://sahool:sahool@sahool_postgis:5432/sahool
    ports:
      - "8080:8080"
    depends_on:
      sahool_postgis:
        condition: service_healthy

volumes:
  sahool_postgis_data:
EOF

# --------------------------
# 3) Flutter app (Drift + Riverpod + Map + Drawing + Drag + Undo + Snap + Area + HUD + Sync)
# --------------------------
echo "📱 Creating Flutter app: $APP_NAME ..."

if [ ! -d "$APP_NAME" ]; then
  flutter create "$APP_NAME"
fi

cd "$APP_NAME"

echo "📦 Adding dependencies..."
flutter pub add flutter_riverpod dio drift sqlite3_flutter_libs path_provider path flutter_map latlong2 workmanager connectivity_plus
flutter pub add --dev drift_dev build_runner

mkdir -p lib/core/{auth,di,storage/{mixins,converters},sync,theme,geo}
mkdir -p lib/features/{home/ui/{logic,widgets},field/{data/repo,ui/{logic,widgets}}}

# --- User Context ---
cat <<'EOF' > lib/core/auth/user_context.dart
class UserContext {
  // MVP (Production: SecureStorage + Token)
  String get currentUserId => "user_101_uuid";
  String get currentTenantId => "tenant_101";
}
EOF

# --- Tenant Mixin ---
cat <<'EOF' > lib/core/storage/mixins/tenant_mixin.dart
import 'package:drift/drift.dart';

mixin TenantMixin on Table {
  TextColumn get userId => text()(); // Row-level isolation (app-side RLS)
}
EOF

# --- Geo Converter (LatLng list <-> JSON string) ---
cat <<'EOF' > lib/core/storage/converters/geo_converter.dart
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

# --- Tables ---
cat <<'EOF' > lib/core/storage/tables.dart
import 'package:drift/drift.dart';
import 'mixins/tenant_mixin.dart';
import 'converters/geo_converter.dart';

class Fields extends Table with TenantMixin {
  TextColumn get id => text()();
  TextColumn get name => text()();
  TextColumn get cropType => text().withDefault(const Constant('unknown'))();
  TextColumn get boundary => text().map(const GeoPolygonConverter())();

  // Sync status + server authority metadata
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  TextColumn get serverEtag => text().nullable()();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();
  DateTimeColumn get lastUpdated => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

class Outbox extends Table with TenantMixin {
  IntColumn get id => integer().autoIncrement()();

  TextColumn get entityType => text()(); // 'field'
  TextColumn get entityId => text()();

  TextColumn get apiEndpoint => text()();
  TextColumn get method => text()();
  TextColumn get payload => text()();

  TextColumn get ifMatch => text().nullable()(); // for PUT If-Match
  IntColumn get retryCount => integer().withDefault(const Constant(0))();
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

class SyncEvents extends Table with TenantMixin {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get type => text()(); // INFO, ERROR, CONFLICT
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
EOF

# --- Database (NO singleton: safe for isolates) ---
cat <<'EOF' > lib/core/storage/database.dart
import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'tables.dart';

part 'database.g.dart';

@DriftDatabase(tables: [Fields, Outbox, SyncEvents, SyncLogs])
class AppDatabase extends _\$AppDatabase {
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
EOF

# --- Glass widget ---
cat <<'EOF' > lib/core/theme/sahool_glass.dart
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
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(opacity),
            border: Border.all(color: Colors.white.withOpacity(0.25)),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.10), blurRadius: 18)],
          ),
          child: child,
        ),
      ),
    );
  }
}
EOF

# --- NetworkStatus (supports both old/new connectivity_plus signatures) ---
cat <<'EOF' > lib/core/sync/network_status.dart
import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

class NetworkStatus {
  final _c = Connectivity();
  ConnectivityResult _status = ConnectivityResult.none;
  StreamSubscription? _sub;

  bool get isOnline => _status != ConnectivityResult.none;

  Future<void> init() async {
    final r = await _c.checkConnectivity();
    _handle(r);
    _sub?.cancel();
    _sub = _c.onConnectivityChanged.listen((r) => _handle(r));
  }

  void _handle(dynamic r) {
    if (r is List<ConnectivityResult>) {
      _status = r.isNotEmpty ? r.first : ConnectivityResult.none;
      return;
    }
    if (r is ConnectivityResult) {
      _status = r;
      return;
    }
    _status = ConnectivityResult.none;
  }

  void dispose() {
    _sub?.cancel();
  }
}
EOF

# --- FieldsRepository (create + edit + apply server) ---
cat <<'EOF' > lib/features/field/data/repo/fields_repository.dart
import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:latlong2/latlong.dart';
import '../../../../core/storage/database.dart';
import '../../../../core/auth/user_context.dart';

class FieldsRepository {
  final AppDatabase _db;
  final UserContext _auth;

  FieldsRepository(this._db, this._auth);

  Stream<List<Field>> watchMyFields() {
    final uid = _auth.currentUserId;
    return (_db.select(_db.fields)..where((f) => f.userId.equals(uid))).watch();
  }

  Future<void> createField(String name, List<LatLng> boundary) async {
    final id = DateTime.now().millisecondsSinceEpoch.toString();
    final uid = _auth.currentUserId;

    await _db.into(_db.fields).insert(FieldsCompanion.insert(
      id: id,
      userId: uid,
      name: name,
      cropType: 'unknown',
      boundary: boundary,
      isSynced: const Value(false),
      lastUpdated: Value(DateTime.now()),
    ));

    // Outbox POST
    final payload = jsonEncode({
      "id": id,
      "name": name,
      "cropType": "unknown",
      "boundary": boundary.map((p) => {"lat": p.latitude, "lng": p.longitude}).toList(),
    });

    await _db.into(_db.outbox).insert(OutboxCompanion.insert(
      userId: uid,
      entityType: 'field',
      entityId: id,
      apiEndpoint: '/api/v1/fields',
      method: 'POST',
      payload: payload,
    ));
  }

  Future<void> updateFieldBoundary(String id, List<LatLng> boundary) async {
    final uid = _auth.currentUserId;

    // read current etag
    final row = await (_db.select(_db.fields)..where((f) => f.userId.equals(uid) & f.id.equals(id))).getSingleOrNull();
    final etag = row?.serverEtag;

    await (_db.update(_db.fields)..where((f) => f.userId.equals(uid) & f.id.equals(id))).write(
      FieldsCompanion(
        boundary: Value(boundary),
        isSynced: const Value(false),
        lastUpdated: Value(DateTime.now()),
      ),
    );

    // Outbox PUT with If-Match
    final payload = jsonEncode({
      "name": row?.name,
      "cropType": row?.cropType,
      "boundary": boundary.map((p) => {"lat": p.latitude, "lng": p.longitude}).toList(),
    });

    await _db.into(_db.outbox).insert(OutboxCompanion.insert(
      userId: uid,
      entityType: 'field',
      entityId: id,
      apiEndpoint: '/api/v1/fields/\$id',
      method: 'PUT',
      payload: payload,
      ifMatch: etag == null ? const Value.absent() : Value(etag),
    ));
  }

  Future<void> applyServerVersion(Map<String, dynamic> server, String etag) async {
    final uid = _auth.currentUserId;
    final id = server['id'] as String;

    final boundaryGeo = server['boundary_geojson'];
    // boundary_geojson: GeoJSON polygon -> coordinates[0] -> [lng,lat]
    List<LatLng> boundary = [];
    try {
      final coords = (boundaryGeo['coordinates'][0] as List);
      boundary = coords.map((p) => LatLng((p[1] as num).toDouble(), (p[0] as num).toDouble())).toList();
    } catch (_) {}

    await (_db.update(_db.fields)..where((f) => f.userId.equals(uid) & f.id.equals(id))).write(
      FieldsCompanion(
        name: Value(server['name'] as String),
        cropType: Value(server['crop_type'] as String),
        boundary: Value(boundary),
        isSynced: const Value(true),
        serverEtag: Value(etag),
        serverUpdatedAt: Value(DateTime.tryParse(server['updated_at']?.toString() ?? '') ?? DateTime.now()),
      ),
    );

    await _db.into(_db.syncEvents).insert(SyncEventsCompanion.insert(
      userId: uid,
      type: 'CONFLICT',
      message: 'تم تطبيق نسخة السيرفر بسبب تعارض (409).',
    ));
  }

  Future<void> markFieldSynced(String id, String etag, DateTime updatedAt) async {
    final uid = _auth.currentUserId;
    await (_db.update(_db.fields)..where((f) => f.userId.equals(uid) & f.id.equals(id))).write(
      FieldsCompanion(
        isSynced: const Value(true),
        serverEtag: Value(etag),
        serverUpdatedAt: Value(updatedAt),
      ),
    );
  }
}
EOF

# --- DI providers ---
cat <<'EOF' > lib/core/di/providers.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../storage/database.dart';
import '../auth/user_context.dart';
import '../../features/field/data/repo/fields_repository.dart';

final databaseProvider = Provider<AppDatabase>((ref) => AppDatabase());
final userContextProvider = Provider<UserContext>((ref) => UserContext());

final fieldsRepoProvider = Provider<FieldsRepository>((ref) {
  final db = ref.watch(databaseProvider);
  final auth = ref.watch(userContextProvider);
  return FieldsRepository(db, auth);
});

final fieldsStreamProvider = StreamProvider((ref) {
  final repo = ref.watch(fieldsRepoProvider);
  return repo.watchMyFields();
});
EOF

# --- Sync providers (HUD) ---
cat <<'EOF' > lib/features/home/ui/logic/sync_provider.dart
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
  final pending = ref.watch(pendingOperationsProvider);
  return pending.when(
    data: (c) => c > 0 ? SyncStatus.syncing : SyncStatus.synced,
    loading: () => SyncStatus.synced,
    error: (_, __) => SyncStatus.offline,
  );
});
EOF

# --- Drawing provider (points + dragging index + undo history) ---
cat <<'EOF' > lib/features/field/ui/logic/drawing_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

class DrawingState {
  final bool isDrawing;
  final String? editingFieldId; // null => create new
  final List<LatLng> points;
  final List<List<LatLng>> history;

  const DrawingState({
    this.isDrawing = false,
    this.editingFieldId,
    this.points = const [],
    this.history = const [],
  });

  bool get isValid => points.length >= 3;

  DrawingState copyWith({
    bool? isDrawing,
    String? editingFieldId,
    List<LatLng>? points,
    List<List<LatLng>>? history,
  }) {
    return DrawingState(
      isDrawing: isDrawing ?? this.isDrawing,
      editingFieldId: editingFieldId,
      points: points ?? this.points,
      history: history ?? this.history,
    );
  }
}

class DrawingNotifier extends StateNotifier<DrawingState> {
  DrawingNotifier() : super(const DrawingState());

  void startNew() => state = const DrawingState(isDrawing: true, editingFieldId: null, points: [], history: []);
  void startEdit(String fieldId, List<LatLng> existing) =>
      state = DrawingState(isDrawing: true, editingFieldId: fieldId, points: existing, history: [existing]);

  void _snapshot(List<LatLng> next) {
    final h = [...state.history, List<LatLng>.from(next)];
    state = state.copyWith(points: next, history: h);
  }

  void addPoint(LatLng p) {
    if (!state.isDrawing) return;
    _snapshot([...state.points, p]);
  }

  void updatePoint(int idx, LatLng p) {
    if (!state.isDrawing) return;
    if (idx < 0 || idx >= state.points.length) return;
    final next = List<LatLng>.from(state.points);
    next[idx] = p;
    _snapshot(next);
  }

  void undo() {
    if (state.history.length <= 1) return;
    final h = List<List<LatLng>>.from(state.history)..removeLast();
    state = state.copyWith(points: h.last, history: h);
  }

  void cancel() => state = const DrawingState(isDrawing: false, points: [], history: []);
}

final drawingProvider = StateNotifierProvider<DrawingNotifier, DrawingState>((ref) => DrawingNotifier());
EOF

# --- Geo helpers: area + snap ---
cat <<'EOF' > lib/core/geo/geo_tools.dart
import 'dart:math';
import 'package:latlong2/latlong.dart';

double _mercY(double lat) {
  final rad = lat * pi / 180.0;
  return log(tan(pi / 4 + rad / 2));
}

double polygonAreaMeters2(List<LatLng> pts) {
  if (pts.length < 3) return 0;
  // WebMercator-ish planar approx (good for field sizes)
  final R = 6378137.0;
  final proj = pts.map((p) {
    final x = R * (p.longitude * pi / 180.0);
    final y = R * _mercY(p.latitude);
    return Point<double>(x, y);
  }).toList();

  double sum = 0;
  for (int i = 0; i < proj.length; i++) {
    final a = proj[i];
    final b = proj[(i + 1) % proj.length];
    sum += (a.x * b.y) - (b.x * a.y);
  }
  return sum.abs() / 2.0;
}

double polygonAreaHa(List<LatLng> pts) => polygonAreaMeters2(pts) / 10000.0;

LatLng snapToNearestVertex(LatLng p, List<LatLng> vertices, {double thresholdMeters = 6}) {
  if (vertices.isEmpty) return p;
  const dist = Distance();
  LatLng best = p;
  double bestD = double.infinity;
  for (final v in vertices) {
    final d = dist(p, v);
    if (d < bestD) {
      bestD = d;
      best = v;
    }
  }
  return bestD <= thresholdMeters ? best : p;
}
EOF

# --- Drawing controls (save/cancel/undo + area display) ---
cat <<'EOF' > lib/features/field/ui/widgets/drawing_controls.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_glass.dart';
import '../logic/drawing_provider.dart';
import '../../../../core/di/providers.dart';
import '../../../../core/geo/geo_tools.dart';

class DrawingControls extends ConsumerWidget {
  const DrawingControls({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final st = ref.watch(drawingProvider);
    if (!st.isDrawing) return const SizedBox.shrink();

    final area = polygonAreaHa(st.points);

    return Positioned(
      left: 16,
      right: 16,
      bottom: 26,
      child: SahoolGlass(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        child: Row(
          children: [
            IconButton(
              onPressed: () => ref.read(drawingProvider.notifier).cancel(),
              icon: const Icon(Icons.close, color: Colors.red),
              tooltip: "إلغاء",
            ),
            const SizedBox(width: 8),
            Text("\${st.points.length} نقاط • \${area.toStringAsFixed(2)} هكتار",
                style: const TextStyle(fontWeight: FontWeight.w700)),
            const Spacer(),
            IconButton(
              onPressed: st.history.length <= 1 ? null : () => ref.read(drawingProvider.notifier).undo(),
              icon: const Icon(Icons.undo),
              tooltip: "تراجع",
            ),
            const SizedBox(width: 10),
            FilledButton.icon(
              onPressed: st.isValid ? () async => _save(context, ref) : null,
              icon: const Icon(Icons.check),
              label: const Text("حفظ"),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _save(BuildContext context, WidgetRef ref) async {
    final st = ref.read(drawingProvider);
    final repo = ref.read(fieldsRepoProvider);

    if (st.editingFieldId == null) {
      await repo.createField("حقل جديد", st.points);
    } else {
      await repo.updateFieldBoundary(st.editingFieldId!, st.points);
    }

    ref.read(drawingProvider.notifier).cancel();
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("✅ تم الحفظ محلياً + تمت الجدولة للمزامنة")));
    }
  }
}
EOF

# --- Sync Worker (ETag/If-Match + 409 Conflict apply server) ---
cat <<'EOF' > lib/core/sync/sync_worker.dart
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import '../storage/database.dart';
import '../auth/user_context.dart';
import 'network_status.dart';
import '../../features/field/data/repo/fields_repository.dart';

class SyncWorker {
  final AppDatabase db;
  final UserContext auth;
  final NetworkStatus net;
  final FieldsRepository fieldsRepo;
  final Dio dio;

  SyncWorker({
    required this.db,
    required this.auth,
    required this.net,
    required this.fieldsRepo,
    Dio? dioClient,
  }) : dio = dioClient ?? Dio(BaseOptions(baseUrl: "http://10.0.2.2:8080"));

  Future<void> run() async {
    if (!net.isOnline) return;

    final uid = auth.currentUserId;
    final tenant = auth.currentTenantId;

    final items = await (db.select(db.outbox)
          ..where((o) => o.userId.equals(uid))
          ..where((o) => o.isSynced.equals(false))
          ..orderBy([(o) => OrderingTerm.asc(o.createdAt)]))
        .get();

    for (final item in items) {
      await _processItem(item, tenant);
    }
  }

  Future<void> _processItem(OutboxData item, String tenantId) async {
    try {
      final headers = <String, dynamic>{
        "X-Tenant-Id": tenantId,
      };

      if (item.ifMatch != null && item.ifMatch!.isNotEmpty) {
        headers["If-Match"] = item.ifMatch;
      }

      final res = await dio.request(
        item.apiEndpoint,
        data: jsonDecode(item.payload),
        options: Options(method: item.method, headers: headers),
      );

      final etag = (res.headers.map["etag"]?.isNotEmpty ?? false) ? res.headers.map["etag"]!.first : null;
      final data = res.data;

      if (item.entityType == 'field' && etag != null && data is Map<String, dynamic>) {
        final updatedAt = DateTime.tryParse(data['updated_at']?.toString() ?? '') ?? DateTime.now();
        await fieldsRepo.markFieldSynced(item.entityId, etag, updatedAt);
      }

      await (db.update(db.outbox)..where((o) => o.id.equals(item.id)))
          .write(const OutboxCompanion(isSynced: Value(true)));

    } on DioException catch (e) {
      if (e.response?.statusCode == 409) {
        final body = e.response?.data;
        if (body is Map) {
          final server = Map<String, dynamic>.from(body['server'] as Map);
          final etag = body['etag']?.toString() ?? '';
          if (etag.isNotEmpty) {
            await fieldsRepo.applyServerVersion(server, etag);
          }
        }
        await (db.update(db.outbox)..where((o) => o.id.equals(item.id)))
            .write(const OutboxCompanion(isSynced: Value(true)));
        return;
      }

      await db.into(db.syncLogs).insert(
        SyncLogsCompanion.insert(level: 'ERROR', message: e.toString()),
      );
    } catch (e) {
      await db.into(db.syncLogs).insert(
        SyncLogsCompanion.insert(level: 'ERROR', message: e.toString()),
      );
    }
  }
}
EOF

# --- Background Service (await init + safe db instance) ---
cat <<'EOF' > lib/core/sync/background_service.dart
import 'package:workmanager/workmanager.dart';
import '../auth/user_context.dart';
import '../storage/database.dart';
import 'network_status.dart';
import 'sync_worker.dart';
import '../../features/field/data/repo/fields_repository.dart';

const syncTaskName = "com.kafaat.sahool.syncTask";

@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, _) async {
    final db = AppDatabase();
    final net = NetworkStatus();
    await net.init();

    // Use simple manual wiring (no ProviderContainer in isolate)
    final auth = UserContext();
    final repo = FieldsRepository(db, auth);

    final worker = SyncWorker(
      db: db,
      auth: auth,
      net: net,
      fieldsRepo: repo,
    );

    await worker.run();
    return true;
  });
}
EOF

# --- Home Screen (HUD + map + polygons + drawing + drag using project/unproject) ---
cat <<'EOF' > lib/features/home/ui/home_screen.dart
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/di/providers.dart';
import '../../../core/theme/sahool_glass.dart';
import '../../home/ui/logic/sync_provider.dart';
import '../../field/ui/logic/drawing_provider.dart';
import '../../field/ui/widgets/drawing_controls.dart';
import '../../../core/geo/geo_tools.dart';
import '../../../core/sync/network_status.dart';
import '../../../core/sync/sync_worker.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});
  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final MapController _map = MapController();

  @override
  Widget build(BuildContext context) {
    final fieldsAsync = ref.watch(fieldsStreamProvider);
    final syncStatus = ref.watch(syncStatusUiProvider);
    final pendingCount = ref.watch(pendingOperationsProvider).valueOrNull ?? 0;
    final drawing = ref.watch(drawingProvider);

    Color iconColor;
    IconData iconData;
    String tip;
    switch (syncStatus) {
      case SyncStatus.synced:
        iconColor = Colors.green.shade800;
        iconData = Icons.cloud_done;
        tip = "تمت المزامنة";
        break;
      case SyncStatus.syncing:
        iconColor = Colors.amber.shade800;
        iconData = Icons.cloud_upload;
        tip = "جاري رفع \$pendingCount عملية...";
        break;
      case SyncStatus.offline:
        iconColor = Colors.grey;
        iconData = Icons.cloud_off;
        tip = "غير متصل";
        break;
    }

    return Scaffold(
      body: Stack(
        children: [
          Positioned.fill(
            child: FlutterMap(
              mapController: _map,
              options: MapOptions(
                initialCenter: const LatLng(15.3694, 44.1910),
                initialZoom: 13,
                onTap: (_, p) {
                  if (drawing.isDrawing && drawing.editingFieldId == null) {
                    ref.read(drawingProvider.notifier).addPoint(p);
                  }
                },
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.kafaat.sahool',
                ),

                // Saved fields
                fieldsAsync.when(
                  data: (fields) {
                    final polys = fields.map((f) {
                      final c = f.isSynced ? const Color(0xFF1B5E20) : Colors.amber.shade700;
                      return Polygon(
                        points: f.boundary,
                        color: c.withOpacity(f.isSynced ? 0.28 : 0.10),
                        borderColor: c,
                        borderStrokeWidth: f.isSynced ? 2 : 3,
                        isFilled: true,
                        isDotted: !f.isSynced,
                        label: f.name,
                        labelStyle: const TextStyle(fontWeight: FontWeight.bold),
                      );
                    }).toList();

                    // Tap-to-edit: choose nearest polygon by vertex snap (simple MVP)
                    final markers = <Marker>[];
                    for (final f in fields) {
                      if (f.boundary.isNotEmpty) {
                        markers.add(Marker(
                          point: f.boundary.first,
                          width: 1,
                          height: 1,
                          child: GestureDetector(
                            behavior: HitTestBehavior.translucent,
                            onLongPress: () {
                              // start edit on long press
                              ref.read(drawingProvider.notifier).startEdit(f.id, f.boundary);
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text("✏️ تعديل: \${f.name} (اسحب النقاط ثم حفظ)")),
                              );
                            },
                            child: const SizedBox.expand(),
                          ),
                        ));
                      }
                    }

                    return Stack(
                      children: [
                        PolygonLayer(polygons: polys),
                        MarkerLayer(markers: markers),
                      ],
                    );
                  },
                  loading: () => const SizedBox.shrink(),
                  error: (_, __) => const SizedBox.shrink(),
                ),

                // Draft layer (new or editing)
                if (drawing.isDrawing) ...[
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: drawing.points.isEmpty
                            ? const []
                            : [...drawing.points, drawing.points.first],
                        color: Colors.orange,
                        strokeWidth: 3,
                        isDotted: true,
                      ),
                    ],
                  ),

                  // Draggable vertices (Edit mode): project/unproject for accurate drag
                  MarkerLayer(
                    markers: List.generate(drawing.points.length, (i) {
                      final p = drawing.points[i];
                      return Marker(
                        point: p,
                        width: 32,
                        height: 32,
                        child: _DraggableVertex(
                          map: _map,
                          point: p,
                          onMoved: (newPoint) {
                            // Snap to nearest existing vertex for precision
                            final snapped = snapToNearestVertex(newPoint, drawing.points.where((e) => e != p).toList());
                            ref.read(drawingProvider.notifier).updatePoint(i, snapped);
                          },
                        ),
                      );
                    }),
                  ),
                ],
              ],
            ),
          ),

          // Header HUD
          Positioned(
            top: 56,
            left: 16,
            right: 16,
            child: SahoolGlass(
              child: Row(
                children: [
                  const CircleAvatar(
                    backgroundColor: Color(0xFF1B5E20),
                    child: Icon(Icons.agriculture, color: Colors.white),
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text("SAHOOL Field Ops", style: TextStyle(fontWeight: FontWeight.bold)),
                      Text(
                        fieldsAsync.valueOrNull != null
                            ? "\${fieldsAsync.value!.length} حقول"
                            : "تحميل...",
                        style: TextStyle(color: Colors.grey.shade700, fontSize: 12),
                      ),
                    ],
                  ),
                  const Spacer(),
                  Tooltip(
                    message: tip,
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: iconColor.withOpacity(0.15),
                        shape: BoxShape.circle,
                        border: Border.all(color: pendingCount > 0 ? iconColor : Colors.transparent),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(iconData, color: iconColor, size: 20),
                          if (pendingCount > 0) ...[
                            const SizedBox(width: 6),
                            Text("\$pendingCount", style: TextStyle(color: iconColor, fontWeight: FontWeight.bold)),
                          ]
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Controls (hide in drawing mode)
          if (!drawing.isDrawing)
            Positioned(
              right: 16,
              bottom: 140,
              child: Column(
                children: [
                  FloatingActionButton.small(
                    heroTag: "draw",
                    backgroundColor: const Color(0xFF1B5E20),
                    child: const Icon(Icons.edit_location_alt, color: Colors.white),
                    onPressed: () => ref.read(drawingProvider.notifier).startNew(),
                  ),
                  const SizedBox(height: 12),
                  FloatingActionButton.small(
                    heroTag: "syncNow",
                    backgroundColor: Colors.white,
                    child: const Icon(Icons.sync, color: Colors.black87),
                    onPressed: () async {
                      // manual sync trigger (debug)
                      final db = ref.read(databaseProvider);
                      final auth = ref.read(userContextProvider);
                      final repo = ref.read(fieldsRepoProvider);
                      final net = NetworkStatus();
                      await net.init();
                      final w = SyncWorker(db: db, auth: auth, net: net, fieldsRepo: repo);
                      await w.run();
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("🔄 Sync حاول التنفيذ")));
                      }
                    },
                  ),
                ],
              ),
            ),

          const DrawingControls(),
        ],
      ),
    );
  }
}

class _DraggableVertex extends StatefulWidget {
  final MapController map;
  final LatLng point;
  final ValueChanged<LatLng> onMoved;

  const _DraggableVertex({
    required this.map,
    required this.point,
    required this.onMoved,
  });

  @override
  State<_DraggableVertex> createState() => _DraggableVertexState();
}

class _DraggableVertexState extends State<_DraggableVertex> {
  Offset? _startPx;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanStart: (_) {
        _startPx = widget.map.camera.project(widget.point).toOffset();
      },
      onPanUpdate: (d) {
        if (_startPx == null) return;
        final moved = _startPx! + d.delta;
        _startPx = moved;

        // ✅ professional: project/unproject for accurate drag
        final newPoint = widget.map.camera.unproject(CustomPoint(moved.dx, moved.dy));
        widget.onMoved(newPoint);
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          shape: BoxShape.circle,
          border: Border.all(color: Colors.orange, width: 3),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.15), blurRadius: 8)],
        ),
      ),
    );
  }
}
EOF

# --- Main (ProviderScope + Workmanager) ---
cat <<'EOF' > lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workmanager/workmanager.dart';

import 'core/sync/background_service.dart';
import 'features/home/ui/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Workmanager().initialize(callbackDispatcher, isInDebugMode: true);
  await Workmanager().registerPeriodicTask(
    "sahool_sync_task_1",
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
EOF

# --------------------------
# 4) Build Runner
# --------------------------
echo "⚙️ Running build_runner..."
flutter pub run build_runner build --delete-conflicting-outputs

cd ..

# --------------------------
# 5) Bring up backend + postgis
# --------------------------
echo "🐳 Starting backend + postgis (override compose)..."
docker compose -f docker-compose.yml -f "$OVERRIDE_COMPOSE" up -d --build

echo ""
echo "✅ DONE!"
echo "----------------------------------------------------"
echo "1) Backend: http://localhost:8080/health"
echo "2) PostGIS: localhost:5436 (db=sahool user=sahool pass=sahool)"
echo "3) Flutter: cd $APP_NAME && flutter run"
echo ""
echo "ℹ️ Android Emulator baseUrl already set to: http://10.0.2.2:8080"
echo "----------------------------------------------------"
