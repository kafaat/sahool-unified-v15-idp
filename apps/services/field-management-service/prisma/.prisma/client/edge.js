
Object.defineProperty(exports, "__esModule", { value: true });

const {
  PrismaClientKnownRequestError,
  PrismaClientUnknownRequestError,
  PrismaClientRustPanicError,
  PrismaClientInitializationError,
  PrismaClientValidationError,
  NotFoundError,
  getPrismaClient,
  sqltag,
  empty,
  join,
  raw,
  skip,
  Decimal,
  Debug,
  objectEnumValues,
  makeStrictEnum,
  Extensions,
  warnOnce,
  defineDmmfProperty,
  Public,
  getRuntime
} = require('./runtime/edge.js')


const Prisma = {}

exports.Prisma = Prisma
exports.$Enums = {}

/**
 * Prisma Client JS version: 5.22.0
 * Query Engine version: 605197351a3c8bdd595af2d2a9bc3025bca48ea2
 */
Prisma.prismaVersion = {
  client: "5.22.0",
  engine: "605197351a3c8bdd595af2d2a9bc3025bca48ea2"
}

Prisma.PrismaClientKnownRequestError = PrismaClientKnownRequestError;
Prisma.PrismaClientUnknownRequestError = PrismaClientUnknownRequestError
Prisma.PrismaClientRustPanicError = PrismaClientRustPanicError
Prisma.PrismaClientInitializationError = PrismaClientInitializationError
Prisma.PrismaClientValidationError = PrismaClientValidationError
Prisma.NotFoundError = NotFoundError
Prisma.Decimal = Decimal

/**
 * Re-export of sql-template-tag
 */
Prisma.sql = sqltag
Prisma.empty = empty
Prisma.join = join
Prisma.raw = raw
Prisma.validator = Public.validator

/**
* Extensions
*/
Prisma.getExtensionContext = Extensions.getExtensionContext
Prisma.defineExtension = Extensions.defineExtension

/**
 * Shorthand utilities for JSON filtering
 */
Prisma.DbNull = objectEnumValues.instances.DbNull
Prisma.JsonNull = objectEnumValues.instances.JsonNull
Prisma.AnyNull = objectEnumValues.instances.AnyNull

Prisma.NullTypes = {
  DbNull: objectEnumValues.classes.DbNull,
  JsonNull: objectEnumValues.classes.JsonNull,
  AnyNull: objectEnumValues.classes.AnyNull
}





/**
 * Enums
 */
exports.Prisma.TransactionIsolationLevel = makeStrictEnum({
  ReadUncommitted: 'ReadUncommitted',
  ReadCommitted: 'ReadCommitted',
  RepeatableRead: 'RepeatableRead',
  Serializable: 'Serializable'
});

exports.Prisma.FieldScalarFieldEnum = {
  id: 'id',
  version: 'version',
  name: 'name',
  tenantId: 'tenantId',
  cropType: 'cropType',
  ownerId: 'ownerId',
  areaHectares: 'areaHectares',
  healthScore: 'healthScore',
  ndviValue: 'ndviValue',
  status: 'status',
  plantingDate: 'plantingDate',
  expectedHarvest: 'expectedHarvest',
  irrigationType: 'irrigationType',
  soilType: 'soilType',
  metadata: 'metadata',
  isDeleted: 'isDeleted',
  serverUpdatedAt: 'serverUpdatedAt',
  etag: 'etag',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.FieldBoundaryHistoryScalarFieldEnum = {
  id: 'id',
  fieldId: 'fieldId',
  versionAtChange: 'versionAtChange',
  areaChangeHectares: 'areaChangeHectares',
  changedBy: 'changedBy',
  changeReason: 'changeReason',
  changeSource: 'changeSource',
  deviceId: 'deviceId',
  createdAt: 'createdAt'
};

exports.Prisma.SyncStatusScalarFieldEnum = {
  id: 'id',
  deviceId: 'deviceId',
  userId: 'userId',
  tenantId: 'tenantId',
  lastSyncAt: 'lastSyncAt',
  lastSyncVersion: 'lastSyncVersion',
  status: 'status',
  pendingUploads: 'pendingUploads',
  pendingDownloads: 'pendingDownloads',
  conflictsCount: 'conflictsCount',
  lastError: 'lastError',
  deviceInfo: 'deviceInfo',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.TaskScalarFieldEnum = {
  id: 'id',
  title: 'title',
  titleAr: 'titleAr',
  description: 'description',
  taskType: 'taskType',
  priority: 'priority',
  status: 'status',
  dueDate: 'dueDate',
  scheduledTime: 'scheduledTime',
  completedAt: 'completedAt',
  assignedTo: 'assignedTo',
  createdBy: 'createdBy',
  fieldId: 'fieldId',
  estimatedMinutes: 'estimatedMinutes',
  actualMinutes: 'actualMinutes',
  completionNotes: 'completionNotes',
  evidence: 'evidence',
  serverUpdatedAt: 'serverUpdatedAt',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.NdviReadingScalarFieldEnum = {
  id: 'id',
  fieldId: 'fieldId',
  value: 'value',
  capturedAt: 'capturedAt',
  source: 'source',
  cloudCover: 'cloudCover',
  quality: 'quality',
  satelliteName: 'satelliteName',
  bandInfo: 'bandInfo',
  createdAt: 'createdAt'
};

exports.Prisma.SortOrder = {
  asc: 'asc',
  desc: 'desc'
};

exports.Prisma.NullableJsonNullValueInput = {
  DbNull: Prisma.DbNull,
  JsonNull: Prisma.JsonNull
};

exports.Prisma.QueryMode = {
  default: 'default',
  insensitive: 'insensitive'
};

exports.Prisma.JsonNullValueFilter = {
  DbNull: Prisma.DbNull,
  JsonNull: Prisma.JsonNull,
  AnyNull: Prisma.AnyNull
};

exports.Prisma.NullsOrder = {
  first: 'first',
  last: 'last'
};
exports.FieldStatus = exports.$Enums.FieldStatus = {
  active: 'active',
  fallow: 'fallow',
  harvested: 'harvested',
  preparing: 'preparing',
  inactive: 'inactive'
};

exports.ChangeSource = exports.$Enums.ChangeSource = {
  mobile: 'mobile',
  web: 'web',
  api: 'api',
  system: 'system'
};

exports.SyncState = exports.$Enums.SyncState = {
  idle: 'idle',
  syncing: 'syncing',
  error: 'error',
  conflict: 'conflict'
};

exports.TaskType = exports.$Enums.TaskType = {
  irrigation: 'irrigation',
  fertilization: 'fertilization',
  spraying: 'spraying',
  scouting: 'scouting',
  maintenance: 'maintenance',
  sampling: 'sampling',
  harvest: 'harvest',
  planting: 'planting',
  other: 'other'
};

exports.Priority = exports.$Enums.Priority = {
  low: 'low',
  medium: 'medium',
  high: 'high',
  urgent: 'urgent'
};

exports.TaskState = exports.$Enums.TaskState = {
  pending: 'pending',
  in_progress: 'in_progress',
  completed: 'completed',
  cancelled: 'cancelled',
  overdue: 'overdue'
};

exports.Prisma.ModelName = {
  Field: 'Field',
  FieldBoundaryHistory: 'FieldBoundaryHistory',
  SyncStatus: 'SyncStatus',
  Task: 'Task',
  NdviReading: 'NdviReading'
};
/**
 * Create the Client
 */
const config = {
  "generator": {
    "name": "client",
    "provider": {
      "fromEnvVar": null,
      "value": "prisma-client-js"
    },
    "output": {
      "value": "/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/services/field-management-service/prisma/.prisma/client",
      "fromEnvVar": null
    },
    "config": {
      "engineType": "library"
    },
    "binaryTargets": [
      {
        "fromEnvVar": null,
        "value": "debian-openssl-3.0.x",
        "native": true
      },
      {
        "fromEnvVar": null,
        "value": "linux-musl-openssl-3.0.x"
      },
      {
        "fromEnvVar": null,
        "value": "debian-openssl-3.0.x"
      }
    ],
    "previewFeatures": [
      "postgresqlExtensions"
    ],
    "sourceFilePath": "/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/services/field-management-service/prisma/schema.prisma",
    "isCustomOutput": true
  },
  "relativeEnvPaths": {
    "rootEnvPath": null
  },
  "relativePath": "../..",
  "clientVersion": "5.22.0",
  "engineVersion": "605197351a3c8bdd595af2d2a9bc3025bca48ea2",
  "datasourceNames": [
    "db"
  ],
  "activeProvider": "postgresql",
  "postinstall": false,
  "ciName": "GitHub Actions",
  "inlineDatasources": {
    "db": {
      "url": {
        "fromEnvVar": "DATABASE_URL",
        "value": null
      }
    }
  },
  "inlineSchema": "// ═══════════════════════════════════════════════════════════════════════════\n// SAHOOL Field Core - Prisma Schema\n// Database: PostgreSQL with PostGIS Extension\n// ═══════════════════════════════════════════════════════════════════════════\n\ngenerator client {\n  provider        = \"prisma-client-js\"\n  output          = \".prisma/client\"\n  previewFeatures = [\"postgresqlExtensions\"]\n  binaryTargets   = [\"native\", \"linux-musl-openssl-3.0.x\", \"debian-openssl-3.0.x\"]\n}\n\ndatasource db {\n  url        = env(\"DATABASE_URL\")\n  provider   = \"postgresql\"\n  extensions = [postgis]\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Field Entity - الحقول الزراعية\n// Core geospatial entity with sync support\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel Field {\n  id      String @id @default(uuid()) @db.Uuid\n  version Int    @default(1) // Optimistic locking\n\n  // Basic Info\n  name     String  @db.VarChar(255)\n  tenantId String  @map(\"tenant_id\") @db.VarChar(100)\n  cropType String  @map(\"crop_type\") @db.VarChar(100)\n  ownerId  String? @map(\"owner_id\") @db.Uuid\n\n  // Geospatial (PostGIS) - handled via raw SQL\n  // boundary: geometry(Polygon, 4326)\n  // centroid: geometry(Point, 4326)\n  boundary Unsupported(\"geometry(Polygon, 4326)\")?\n  centroid Unsupported(\"geometry(Point, 4326)\")?\n\n  // Calculated Fields\n  areaHectares Decimal? @map(\"area_hectares\") @db.Decimal(10, 4)\n\n  // Health & Analysis\n  healthScore Decimal? @map(\"health_score\") @db.Decimal(3, 2)\n  ndviValue   Decimal? @map(\"ndvi_value\") @db.Decimal(4, 3)\n\n  // Status & Dates\n  status          FieldStatus @default(active)\n  plantingDate    DateTime?   @map(\"planting_date\") @db.Date\n  expectedHarvest DateTime?   @map(\"expected_harvest\") @db.Date\n\n  // Agricultural Info\n  irrigationType String? @map(\"irrigation_type\") @db.VarChar(50)\n  soilType       String? @map(\"soil_type\") @db.VarChar(100)\n\n  // Flexible Metadata (JSONB)\n  metadata Json? @db.JsonB\n\n  // Sync Metadata\n  isDeleted       Boolean  @default(false) @map(\"is_deleted\")\n  serverUpdatedAt DateTime @default(now()) @map(\"server_updated_at\") @db.Timestamptz\n  etag            String?  @default(uuid()) @db.VarChar(64)\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n  updatedAt DateTime @updatedAt @map(\"updated_at\") @db.Timestamptz\n\n  // Relations\n  boundaryHistory FieldBoundaryHistory[]\n  tasks           Task[]\n  ndviReadings    NdviReading[]\n\n  // Indexes\n  @@index([tenantId], name: \"idx_field_tenant\")\n  @@index([serverUpdatedAt], name: \"idx_field_sync\")\n  @@index([status], name: \"idx_field_status\")\n  @@index([cropType], name: \"idx_field_crop\")\n  @@map(\"fields\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Field Boundary History - سجل تغييرات الحدود\n// Audit trail for boundary changes (for rollback support)\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel FieldBoundaryHistory {\n  id String @id @default(uuid()) @db.Uuid\n\n  // Field Reference\n  fieldId         String @map(\"field_id\") @db.Uuid\n  versionAtChange Int    @map(\"version_at_change\")\n\n  // Boundary Snapshots (PostGIS)\n  previousBoundary Unsupported(\"geometry(Polygon, 4326)\")? @map(\"previous_boundary\")\n  newBoundary      Unsupported(\"geometry(Polygon, 4326)\")? @map(\"new_boundary\")\n\n  // Change Metrics\n  areaChangeHectares Decimal? @map(\"area_change_hectares\") @db.Decimal(10, 4)\n\n  // Change Metadata\n  changedBy    String?      @map(\"changed_by\") @db.VarChar(255)\n  changeReason String?      @map(\"change_reason\") @db.VarChar(500)\n  changeSource ChangeSource @default(api) @map(\"change_source\")\n  deviceId     String?      @map(\"device_id\") @db.VarChar(100)\n\n  // Timestamp\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n\n  // Relations\n  field Field @relation(fields: [fieldId], references: [id], onDelete: Cascade)\n\n  // Indexes\n  @@index([fieldId], name: \"idx_history_field\")\n  @@index([createdAt], name: \"idx_history_date\")\n  @@map(\"field_boundary_history\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Sync Status - حالة المزامنة للأجهزة\n// Tracks mobile device sync status\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel SyncStatus {\n  id String @id @default(uuid()) @db.Uuid\n\n  // Device Identification\n  deviceId String @map(\"device_id\") @db.VarChar(100)\n  userId   String @map(\"user_id\") @db.VarChar(100)\n  tenantId String @map(\"tenant_id\") @db.VarChar(100)\n\n  // Sync State\n  lastSyncAt      DateTime? @map(\"last_sync_at\") @db.Timestamptz\n  lastSyncVersion BigInt    @default(0) @map(\"last_sync_version\")\n  status          SyncState @default(idle)\n\n  // Pending Operations\n  pendingUploads   Int @default(0) @map(\"pending_uploads\")\n  pendingDownloads Int @default(0) @map(\"pending_downloads\")\n  conflictsCount   Int @default(0) @map(\"conflicts_count\")\n\n  // Error Tracking\n  lastError String? @map(\"last_error\") @db.Text\n\n  // Device Info (JSONB)\n  deviceInfo Json? @map(\"device_info\") @db.JsonB\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n  updatedAt DateTime @updatedAt @map(\"updated_at\") @db.Timestamptz\n\n  // Indexes\n  @@unique([deviceId, userId], name: \"idx_sync_device_user\")\n  @@index([tenantId], name: \"idx_sync_tenant\")\n  @@map(\"sync_status\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Task - المهام الزراعية\n// Tasks linked to fields\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel Task {\n  id String @id @default(uuid()) @db.Uuid\n\n  // Task Info\n  title       String    @db.VarChar(255)\n  titleAr     String?   @map(\"title_ar\") @db.VarChar(255)\n  description String?   @db.Text\n  taskType    TaskType  @default(other) @map(\"task_type\")\n  priority    Priority  @default(medium)\n  status      TaskState @default(pending)\n\n  // Scheduling\n  dueDate       DateTime? @map(\"due_date\") @db.Timestamptz\n  scheduledTime String?   @map(\"scheduled_time\") @db.VarChar(10) // HH:MM\n  completedAt   DateTime? @map(\"completed_at\") @db.Timestamptz\n\n  // Assignment\n  assignedTo String? @map(\"assigned_to\") @db.VarChar(100)\n  createdBy  String  @map(\"created_by\") @db.VarChar(100)\n\n  // Field Reference\n  fieldId String? @map(\"field_id\") @db.Uuid\n  field   Field?  @relation(fields: [fieldId], references: [id], onDelete: SetNull)\n\n  // Duration\n  estimatedMinutes Int? @map(\"estimated_minutes\")\n  actualMinutes    Int? @map(\"actual_minutes\")\n\n  // Completion Evidence\n  completionNotes String? @map(\"completion_notes\") @db.Text\n  evidence        Json?   @db.JsonB // Array of {type, url, capturedAt}\n\n  // Sync\n  serverUpdatedAt DateTime @default(now()) @map(\"server_updated_at\") @db.Timestamptz\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n  updatedAt DateTime @updatedAt @map(\"updated_at\") @db.Timestamptz\n\n  // Indexes\n  @@index([fieldId], name: \"idx_task_field\")\n  @@index([status], name: \"idx_task_status\")\n  @@index([dueDate], name: \"idx_task_due\")\n  @@map(\"tasks\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// NDVI Reading - قراءات NDVI\n// Historical NDVI values for fields\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel NdviReading {\n  id String @id @default(uuid()) @db.Uuid\n\n  // Field Reference\n  fieldId String @map(\"field_id\") @db.Uuid\n  field   Field  @relation(fields: [fieldId], references: [id], onDelete: Cascade)\n\n  // NDVI Data\n  value      Decimal  @db.Decimal(4, 3) // -1.000 to 1.000\n  capturedAt DateTime @map(\"captured_at\") @db.Timestamptz\n  source     String   @default(\"satellite\") @db.VarChar(50) // satellite, drone, manual\n  cloudCover Decimal? @map(\"cloud_cover\") @db.Decimal(5, 2) // 0-100%\n  quality    String?  @db.VarChar(20) // good, moderate, poor\n\n  // Satellite Info\n  satelliteName String? @map(\"satellite_name\") @db.VarChar(50)\n  bandInfo      Json?   @map(\"band_info\") @db.JsonB\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n\n  // Indexes\n  @@index([fieldId, capturedAt], name: \"idx_ndvi_field_date\")\n  @@map(\"ndvi_readings\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Enums\n// ─────────────────────────────────────────────────────────────────────────────\n\nenum FieldStatus {\n  active\n  fallow\n  harvested\n  preparing\n  inactive\n\n  @@map(\"field_status\")\n}\n\nenum ChangeSource {\n  mobile\n  web\n  api\n  system\n\n  @@map(\"change_source\")\n}\n\nenum SyncState {\n  idle\n  syncing\n  error\n  conflict\n\n  @@map(\"sync_state\")\n}\n\nenum TaskType {\n  irrigation\n  fertilization\n  spraying\n  scouting\n  maintenance\n  sampling\n  harvest\n  planting\n  other\n\n  @@map(\"task_type\")\n}\n\nenum Priority {\n  low\n  medium\n  high\n  urgent\n\n  @@map(\"priority\")\n}\n\nenum TaskState {\n  pending\n  in_progress\n  completed\n  cancelled\n  overdue\n\n  @@map(\"task_state\")\n}\n",
  "inlineSchemaHash": "64f25286096ceb02a2008db37c015f8832ef4aab8ac8d6830b5c7ae8ee961c79",
  "copyEngine": true
}
config.dirname = '/'

config.runtimeDataModel = JSON.parse("{\"models\":{\"Field\":{\"dbName\":\"fields\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"version\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":1,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"cropType\",\"dbName\":\"crop_type\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"ownerId\",\"dbName\":\"owner_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"areaHectares\",\"dbName\":\"area_hectares\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"healthScore\",\"dbName\":\"health_score\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"ndviValue\",\"dbName\":\"ndvi_value\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"FieldStatus\",\"default\":\"active\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"plantingDate\",\"dbName\":\"planting_date\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"expectedHarvest\",\"dbName\":\"expected_harvest\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"irrigationType\",\"dbName\":\"irrigation_type\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"soilType\",\"dbName\":\"soil_type\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"metadata\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"isDeleted\",\"dbName\":\"is_deleted\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":false,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"serverUpdatedAt\",\"dbName\":\"server_updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"etag\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"boundaryHistory\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"FieldBoundaryHistory\",\"relationName\":\"FieldToFieldBoundaryHistory\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tasks\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Task\",\"relationName\":\"FieldToTask\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"ndviReadings\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"NdviReading\",\"relationName\":\"FieldToNdviReading\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"FieldBoundaryHistory\":{\"dbName\":\"field_boundary_history\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fieldId\",\"dbName\":\"field_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"versionAtChange\",\"dbName\":\"version_at_change\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Int\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"areaChangeHectares\",\"dbName\":\"area_change_hectares\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"changedBy\",\"dbName\":\"changed_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"changeReason\",\"dbName\":\"change_reason\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"changeSource\",\"dbName\":\"change_source\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"ChangeSource\",\"default\":\"api\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceId\",\"dbName\":\"device_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"field\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Field\",\"relationName\":\"FieldToFieldBoundaryHistory\",\"relationFromFields\":[\"fieldId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"SyncStatus\":{\"dbName\":\"sync_status\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceId\",\"dbName\":\"device_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"userId\",\"dbName\":\"user_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastSyncAt\",\"dbName\":\"last_sync_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastSyncVersion\",\"dbName\":\"last_sync_version\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"BigInt\",\"default\":\"0\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"SyncState\",\"default\":\"idle\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"pendingUploads\",\"dbName\":\"pending_uploads\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"pendingDownloads\",\"dbName\":\"pending_downloads\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"conflictsCount\",\"dbName\":\"conflicts_count\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastError\",\"dbName\":\"last_error\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceInfo\",\"dbName\":\"device_info\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[[\"deviceId\",\"userId\"]],\"uniqueIndexes\":[{\"name\":\"idx_sync_device_user\",\"fields\":[\"deviceId\",\"userId\"]}],\"isGenerated\":false},\"Task\":{\"dbName\":\"tasks\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"title\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"titleAr\",\"dbName\":\"title_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"description\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"taskType\",\"dbName\":\"task_type\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"TaskType\",\"default\":\"other\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"priority\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Priority\",\"default\":\"medium\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"TaskState\",\"default\":\"pending\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"dueDate\",\"dbName\":\"due_date\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"scheduledTime\",\"dbName\":\"scheduled_time\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"completedAt\",\"dbName\":\"completed_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"assignedTo\",\"dbName\":\"assigned_to\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdBy\",\"dbName\":\"created_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fieldId\",\"dbName\":\"field_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"field\",\"kind\":\"object\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Field\",\"relationName\":\"FieldToTask\",\"relationFromFields\":[\"fieldId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"SetNull\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"estimatedMinutes\",\"dbName\":\"estimated_minutes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Int\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"actualMinutes\",\"dbName\":\"actual_minutes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Int\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"completionNotes\",\"dbName\":\"completion_notes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"evidence\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"serverUpdatedAt\",\"dbName\":\"server_updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"NdviReading\":{\"dbName\":\"ndvi_readings\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fieldId\",\"dbName\":\"field_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"field\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Field\",\"relationName\":\"FieldToNdviReading\",\"relationFromFields\":[\"fieldId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"value\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"capturedAt\",\"dbName\":\"captured_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"source\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":\"satellite\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"cloudCover\",\"dbName\":\"cloud_cover\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"quality\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"satelliteName\",\"dbName\":\"satellite_name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"bandInfo\",\"dbName\":\"band_info\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false}},\"enums\":{\"FieldStatus\":{\"values\":[{\"name\":\"active\",\"dbName\":null},{\"name\":\"fallow\",\"dbName\":null},{\"name\":\"harvested\",\"dbName\":null},{\"name\":\"preparing\",\"dbName\":null},{\"name\":\"inactive\",\"dbName\":null}],\"dbName\":\"field_status\"},\"ChangeSource\":{\"values\":[{\"name\":\"mobile\",\"dbName\":null},{\"name\":\"web\",\"dbName\":null},{\"name\":\"api\",\"dbName\":null},{\"name\":\"system\",\"dbName\":null}],\"dbName\":\"change_source\"},\"SyncState\":{\"values\":[{\"name\":\"idle\",\"dbName\":null},{\"name\":\"syncing\",\"dbName\":null},{\"name\":\"error\",\"dbName\":null},{\"name\":\"conflict\",\"dbName\":null}],\"dbName\":\"sync_state\"},\"TaskType\":{\"values\":[{\"name\":\"irrigation\",\"dbName\":null},{\"name\":\"fertilization\",\"dbName\":null},{\"name\":\"spraying\",\"dbName\":null},{\"name\":\"scouting\",\"dbName\":null},{\"name\":\"maintenance\",\"dbName\":null},{\"name\":\"sampling\",\"dbName\":null},{\"name\":\"harvest\",\"dbName\":null},{\"name\":\"planting\",\"dbName\":null},{\"name\":\"other\",\"dbName\":null}],\"dbName\":\"task_type\"},\"Priority\":{\"values\":[{\"name\":\"low\",\"dbName\":null},{\"name\":\"medium\",\"dbName\":null},{\"name\":\"high\",\"dbName\":null},{\"name\":\"urgent\",\"dbName\":null}],\"dbName\":\"priority\"},\"TaskState\":{\"values\":[{\"name\":\"pending\",\"dbName\":null},{\"name\":\"in_progress\",\"dbName\":null},{\"name\":\"completed\",\"dbName\":null},{\"name\":\"cancelled\",\"dbName\":null},{\"name\":\"overdue\",\"dbName\":null}],\"dbName\":\"task_state\"}},\"types\":{}}")
defineDmmfProperty(exports.Prisma, config.runtimeDataModel)
config.engineWasm = undefined

config.injectableEdgeEnv = () => ({
  parsed: {
    DATABASE_URL: typeof globalThis !== 'undefined' && globalThis['DATABASE_URL'] || typeof process !== 'undefined' && process.env && process.env.DATABASE_URL || undefined
  }
})

if (typeof globalThis !== 'undefined' && globalThis['DEBUG'] || typeof process !== 'undefined' && process.env && process.env.DEBUG || undefined) {
  Debug.enable(typeof globalThis !== 'undefined' && globalThis['DEBUG'] || typeof process !== 'undefined' && process.env && process.env.DEBUG || undefined)
}

const PrismaClient = getPrismaClient(config)
exports.PrismaClient = PrismaClient
Object.assign(exports, Prisma)

