
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
} = require('./runtime/library.js')


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




  const path = require('path')

/**
 * Enums
 */
exports.Prisma.TransactionIsolationLevel = makeStrictEnum({
  ReadUncommitted: 'ReadUncommitted',
  ReadCommitted: 'ReadCommitted',
  RepeatableRead: 'RepeatableRead',
  Serializable: 'Serializable'
});

exports.Prisma.FarmScalarFieldEnum = {
  id: 'id',
  version: 'version',
  name: 'name',
  tenantId: 'tenantId',
  ownerId: 'ownerId',
  totalAreaHectares: 'totalAreaHectares',
  address: 'address',
  phone: 'phone',
  email: 'email',
  metadata: 'metadata',
  isDeleted: 'isDeleted',
  serverUpdatedAt: 'serverUpdatedAt',
  etag: 'etag',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.FieldScalarFieldEnum = {
  id: 'id',
  version: 'version',
  name: 'name',
  tenantId: 'tenantId',
  cropType: 'cropType',
  ownerId: 'ownerId',
  farmId: 'farmId',
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

exports.Prisma.PestIncidentScalarFieldEnum = {
  id: 'id',
  fieldId: 'fieldId',
  cropSeasonId: 'cropSeasonId',
  tenantId: 'tenantId',
  pestType: 'pestType',
  pestName: 'pestName',
  severityLevel: 'severityLevel',
  affectedArea: 'affectedArea',
  status: 'status',
  detectedAt: 'detectedAt',
  reportedBy: 'reportedBy',
  location: 'location',
  photos: 'photos',
  notes: 'notes',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.PestTreatmentScalarFieldEnum = {
  id: 'id',
  incidentId: 'incidentId',
  tenantId: 'tenantId',
  treatmentDate: 'treatmentDate',
  method: 'method',
  productUsed: 'productUsed',
  productId: 'productId',
  quantity: 'quantity',
  unit: 'unit',
  appliedBy: 'appliedBy',
  effectiveness: 'effectiveness',
  cost: 'cost',
  notes: 'notes',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
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

exports.PestType = exports.$Enums.PestType = {
  INSECT: 'INSECT',
  FUNGUS: 'FUNGUS',
  BACTERIA: 'BACTERIA',
  VIRUS: 'VIRUS',
  WEED: 'WEED',
  RODENT: 'RODENT',
  BIRD: 'BIRD',
  NEMATODE: 'NEMATODE',
  OTHER: 'OTHER'
};

exports.IncidentStatus = exports.$Enums.IncidentStatus = {
  DETECTED: 'DETECTED',
  MONITORING: 'MONITORING',
  TREATING: 'TREATING',
  RESOLVED: 'RESOLVED',
  RECURRING: 'RECURRING'
};

exports.Prisma.ModelName = {
  Farm: 'Farm',
  Field: 'Field',
  FieldBoundaryHistory: 'FieldBoundaryHistory',
  SyncStatus: 'SyncStatus',
  Task: 'Task',
  NdviReading: 'NdviReading',
  PestIncident: 'PestIncident',
  PestTreatment: 'PestTreatment'
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
      "value": "/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/services/field-core/prisma/.prisma/client",
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
    "sourceFilePath": "/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/services/field-core/prisma/schema.prisma",
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
  "inlineSchema": "// ═══════════════════════════════════════════════════════════════════════════\n// SAHOOL Field Core - Prisma Schema\n// Database: PostgreSQL with PostGIS Extension\n// ═══════════════════════════════════════════════════════════════════════════\n\ngenerator client {\n  provider        = \"prisma-client-js\"\n  output          = \".prisma/client\"\n  previewFeatures = [\"postgresqlExtensions\"]\n  binaryTargets   = [\"native\", \"linux-musl-openssl-3.0.x\", \"debian-openssl-3.0.x\"]\n}\n\ndatasource db {\n  url        = env(\"DATABASE_URL\")\n  provider   = \"postgresql\"\n  extensions = [postgis]\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Farm Entity - المزارع\n// Farm locations and boundaries with geospatial support\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel Farm {\n  id      String @id @default(uuid()) @db.Uuid\n  version Int    @default(1) // Optimistic locking\n\n  // Basic Info\n  name     String @db.VarChar(255)\n  tenantId String @map(\"tenant_id\") @db.VarChar(100)\n  ownerId  String @map(\"owner_id\") @db.VarChar(100)\n\n  // Geospatial (PostGIS)\n  location Unsupported(\"geometry(Point, 4326)\")? // Farm headquarters\n  boundary Unsupported(\"geometry(Polygon, 4326)\")? // Farm boundary\n\n  // Calculated Fields\n  totalAreaHectares Decimal? @map(\"total_area_hectares\") @db.Decimal(10, 4)\n\n  // Contact & Address\n  address String? @db.VarChar(500)\n  phone   String? @db.VarChar(50)\n  email   String? @db.VarChar(255)\n\n  // Flexible Metadata\n  metadata Json? @db.JsonB\n\n  // Sync Metadata\n  isDeleted       Boolean  @default(false) @map(\"is_deleted\")\n  serverUpdatedAt DateTime @default(now()) @map(\"server_updated_at\") @db.Timestamptz\n  etag            String?  @default(uuid()) @db.VarChar(64)\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n  updatedAt DateTime @updatedAt @map(\"updated_at\") @db.Timestamptz\n\n  // Relations\n  fields Field[]\n\n  // Indexes\n  @@index([tenantId], name: \"idx_farm_tenant\")\n  @@index([ownerId], name: \"idx_farm_owner\")\n  @@index([serverUpdatedAt], name: \"idx_farm_sync\")\n  @@map(\"farms\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Field Entity - الحقول الزراعية\n// Core geospatial entity with sync support\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel Field {\n  id      String @id @default(uuid()) @db.Uuid\n  version Int    @default(1) // Optimistic locking\n\n  // Basic Info\n  name     String  @db.VarChar(255)\n  tenantId String  @map(\"tenant_id\") @db.VarChar(100)\n  cropType String  @map(\"crop_type\") @db.VarChar(100)\n  ownerId  String? @map(\"owner_id\") @db.Uuid\n\n  // Farm Reference\n  farmId String? @map(\"farm_id\") @db.Uuid\n  farm   Farm?   @relation(fields: [farmId], references: [id], onDelete: SetNull)\n\n  // Geospatial (PostGIS) - handled via raw SQL\n  // boundary: geometry(Polygon, 4326)\n  // centroid: geometry(Point, 4326)\n  boundary Unsupported(\"geometry(Polygon, 4326)\")?\n  centroid Unsupported(\"geometry(Point, 4326)\")?\n\n  // Calculated Fields\n  areaHectares Decimal? @map(\"area_hectares\") @db.Decimal(10, 4)\n\n  // Health & Analysis\n  healthScore Decimal? @map(\"health_score\") @db.Decimal(3, 2)\n  ndviValue   Decimal? @map(\"ndvi_value\") @db.Decimal(4, 3)\n\n  // Status & Dates\n  status          FieldStatus @default(active)\n  plantingDate    DateTime?   @map(\"planting_date\") @db.Date\n  expectedHarvest DateTime?   @map(\"expected_harvest\") @db.Date\n\n  // Agricultural Info\n  irrigationType String? @map(\"irrigation_type\") @db.VarChar(50)\n  soilType       String? @map(\"soil_type\") @db.VarChar(100)\n\n  // Flexible Metadata (JSONB)\n  metadata Json? @db.JsonB\n\n  // Sync Metadata\n  isDeleted       Boolean  @default(false) @map(\"is_deleted\")\n  serverUpdatedAt DateTime @default(now()) @map(\"server_updated_at\") @db.Timestamptz\n  etag            String?  @default(uuid()) @db.VarChar(64)\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n  updatedAt DateTime @updatedAt @map(\"updated_at\") @db.Timestamptz\n\n  // Relations\n  boundaryHistory FieldBoundaryHistory[]\n  tasks           Task[]\n  ndviReadings    NdviReading[]\n\n  // Indexes\n  @@index([tenantId], name: \"idx_field_tenant\")\n  @@index([serverUpdatedAt], name: \"idx_field_sync\")\n  @@index([status], name: \"idx_field_status\")\n  @@index([cropType], name: \"idx_field_crop\")\n  @@map(\"fields\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Field Boundary History - سجل تغييرات الحدود\n// Audit trail for boundary changes (for rollback support)\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel FieldBoundaryHistory {\n  id String @id @default(uuid()) @db.Uuid\n\n  // Field Reference\n  fieldId         String @map(\"field_id\") @db.Uuid\n  versionAtChange Int    @map(\"version_at_change\")\n\n  // Boundary Snapshots (PostGIS)\n  previousBoundary Unsupported(\"geometry(Polygon, 4326)\")? @map(\"previous_boundary\")\n  newBoundary      Unsupported(\"geometry(Polygon, 4326)\")? @map(\"new_boundary\")\n\n  // Change Metrics\n  areaChangeHectares Decimal? @map(\"area_change_hectares\") @db.Decimal(10, 4)\n\n  // Change Metadata\n  changedBy    String?      @map(\"changed_by\") @db.VarChar(255)\n  changeReason String?      @map(\"change_reason\") @db.VarChar(500)\n  changeSource ChangeSource @default(api) @map(\"change_source\")\n  deviceId     String?      @map(\"device_id\") @db.VarChar(100)\n\n  // Timestamp\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n\n  // Relations\n  field Field @relation(fields: [fieldId], references: [id], onDelete: Cascade)\n\n  // Indexes\n  @@index([fieldId], name: \"idx_history_field\")\n  @@index([createdAt], name: \"idx_history_date\")\n  @@map(\"field_boundary_history\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Sync Status - حالة المزامنة للأجهزة\n// Tracks mobile device sync status\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel SyncStatus {\n  id String @id @default(uuid()) @db.Uuid\n\n  // Device Identification\n  deviceId String @map(\"device_id\") @db.VarChar(100)\n  userId   String @map(\"user_id\") @db.VarChar(100)\n  tenantId String @map(\"tenant_id\") @db.VarChar(100)\n\n  // Sync State\n  lastSyncAt      DateTime? @map(\"last_sync_at\") @db.Timestamptz\n  lastSyncVersion BigInt    @default(0) @map(\"last_sync_version\")\n  status          SyncState @default(idle)\n\n  // Pending Operations\n  pendingUploads   Int @default(0) @map(\"pending_uploads\")\n  pendingDownloads Int @default(0) @map(\"pending_downloads\")\n  conflictsCount   Int @default(0) @map(\"conflicts_count\")\n\n  // Error Tracking\n  lastError String? @map(\"last_error\") @db.Text\n\n  // Device Info (JSONB)\n  deviceInfo Json? @map(\"device_info\") @db.JsonB\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n  updatedAt DateTime @updatedAt @map(\"updated_at\") @db.Timestamptz\n\n  // Indexes\n  @@unique([deviceId, userId], name: \"idx_sync_device_user\")\n  @@index([tenantId], name: \"idx_sync_tenant\")\n  @@map(\"sync_status\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Task - المهام الزراعية\n// Tasks linked to fields\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel Task {\n  id String @id @default(uuid()) @db.Uuid\n\n  // Task Info\n  title       String    @db.VarChar(255)\n  titleAr     String?   @map(\"title_ar\") @db.VarChar(255)\n  description String?   @db.Text\n  taskType    TaskType  @default(other) @map(\"task_type\")\n  priority    Priority  @default(medium)\n  status      TaskState @default(pending)\n\n  // Scheduling\n  dueDate       DateTime? @map(\"due_date\") @db.Timestamptz\n  scheduledTime String?   @map(\"scheduled_time\") @db.VarChar(10) // HH:MM\n  completedAt   DateTime? @map(\"completed_at\") @db.Timestamptz\n\n  // Assignment\n  assignedTo String? @map(\"assigned_to\") @db.VarChar(100)\n  createdBy  String  @map(\"created_by\") @db.VarChar(100)\n\n  // Field Reference\n  fieldId String? @map(\"field_id\") @db.Uuid\n  field   Field?  @relation(fields: [fieldId], references: [id], onDelete: SetNull)\n\n  // Duration\n  estimatedMinutes Int? @map(\"estimated_minutes\")\n  actualMinutes    Int? @map(\"actual_minutes\")\n\n  // Completion Evidence\n  completionNotes String? @map(\"completion_notes\") @db.Text\n  evidence        Json?   @db.JsonB // Array of {type, url, capturedAt}\n\n  // Sync\n  serverUpdatedAt DateTime @default(now()) @map(\"server_updated_at\") @db.Timestamptz\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n  updatedAt DateTime @updatedAt @map(\"updated_at\") @db.Timestamptz\n\n  // Indexes\n  @@index([fieldId], name: \"idx_task_field\")\n  @@index([status], name: \"idx_task_status\")\n  @@index([dueDate], name: \"idx_task_due\")\n  @@map(\"tasks\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// NDVI Reading - قراءات NDVI\n// Historical NDVI values for fields\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel NdviReading {\n  id String @id @default(uuid()) @db.Uuid\n\n  // Field Reference\n  fieldId String @map(\"field_id\") @db.Uuid\n  field   Field  @relation(fields: [fieldId], references: [id], onDelete: Cascade)\n\n  // NDVI Data\n  value      Decimal  @db.Decimal(4, 3) // -1.000 to 1.000\n  capturedAt DateTime @map(\"captured_at\") @db.Timestamptz\n  source     String   @default(\"satellite\") @db.VarChar(50) // satellite, drone, manual\n  cloudCover Decimal? @map(\"cloud_cover\") @db.Decimal(5, 2) // 0-100%\n  quality    String?  @db.VarChar(20) // good, moderate, poor\n\n  // Satellite Info\n  satelliteName String? @map(\"satellite_name\") @db.VarChar(50)\n  bandInfo      Json?   @map(\"band_info\") @db.JsonB\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n\n  // Indexes\n  @@index([fieldId, capturedAt], name: \"idx_ndvi_field_date\")\n  @@map(\"ndvi_readings\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Pest Incident - حوادث الآفات\n// Tracks pest detection and monitoring\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel PestIncident {\n  id String @id @default(uuid()) @db.Uuid\n\n  // References\n  fieldId      String  @map(\"field_id\") @db.Uuid\n  cropSeasonId String? @map(\"crop_season_id\") @db.Uuid\n  tenantId     String  @map(\"tenant_id\") @db.VarChar(100)\n\n  // Pest Information\n  pestType      PestType       @map(\"pest_type\")\n  pestName      String         @map(\"pest_name\") @db.VarChar(255)\n  severityLevel Int            @map(\"severity_level\") // 1-5 scale\n  affectedArea  Decimal        @map(\"affected_area\") @db.Decimal(10, 4) // hectares\n  status        IncidentStatus @default(DETECTED)\n\n  // Detection Details\n  detectedAt DateTime @map(\"detected_at\") @db.Timestamptz\n  reportedBy String   @map(\"reported_by\") @db.VarChar(255)\n\n  // Location & Evidence\n  location Json?   @db.JsonB // {lat, lng, coordinates}\n  photos   Json?   @db.JsonB // Array of photo URLs\n  notes    String? @db.Text\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n  updatedAt DateTime @updatedAt @map(\"updated_at\") @db.Timestamptz\n\n  // Relations\n  treatments PestTreatment[]\n\n  // Indexes\n  @@index([fieldId], name: \"idx_pest_incident_field\")\n  @@index([tenantId], name: \"idx_pest_incident_tenant\")\n  @@index([status], name: \"idx_pest_incident_status\")\n  @@index([detectedAt], name: \"idx_pest_incident_date\")\n  @@map(\"pest_incidents\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Pest Treatment - علاجات الآفات\n// Records treatment actions taken for pest incidents\n// ─────────────────────────────────────────────────────────────────────────────\n\nmodel PestTreatment {\n  id String @id @default(uuid()) @db.Uuid\n\n  // References\n  incidentId String @map(\"incident_id\") @db.Uuid\n  tenantId   String @map(\"tenant_id\") @db.VarChar(100)\n\n  // Treatment Details\n  treatmentDate DateTime @map(\"treatment_date\") @db.Timestamptz\n  method        String   @db.VarChar(255)\n  productUsed   String   @map(\"product_used\") @db.VarChar(255)\n  productId     String?  @map(\"product_id\") @db.Uuid\n\n  // Application Details\n  quantity  Decimal @db.Decimal(10, 3)\n  unit      String  @db.VarChar(50)\n  appliedBy String  @map(\"applied_by\") @db.VarChar(255)\n\n  // Results\n  effectiveness Int?     @db.SmallInt // 1-5 scale\n  cost          Decimal? @db.Decimal(10, 2)\n  notes         String?  @db.Text\n\n  // Timestamps\n  createdAt DateTime @default(now()) @map(\"created_at\") @db.Timestamptz\n  updatedAt DateTime @updatedAt @map(\"updated_at\") @db.Timestamptz\n\n  // Relations\n  incident PestIncident @relation(fields: [incidentId], references: [id], onDelete: Cascade)\n\n  // Indexes\n  @@index([incidentId], name: \"idx_pest_treatment_incident\")\n  @@index([tenantId], name: \"idx_pest_treatment_tenant\")\n  @@index([treatmentDate], name: \"idx_pest_treatment_date\")\n  @@map(\"pest_treatments\")\n}\n\n// ─────────────────────────────────────────────────────────────────────────────\n// Enums\n// ─────────────────────────────────────────────────────────────────────────────\n\nenum FieldStatus {\n  active\n  fallow\n  harvested\n  preparing\n  inactive\n\n  @@map(\"field_status\")\n}\n\nenum ChangeSource {\n  mobile\n  web\n  api\n  system\n\n  @@map(\"change_source\")\n}\n\nenum SyncState {\n  idle\n  syncing\n  error\n  conflict\n\n  @@map(\"sync_state\")\n}\n\nenum TaskType {\n  irrigation\n  fertilization\n  spraying\n  scouting\n  maintenance\n  sampling\n  harvest\n  planting\n  other\n\n  @@map(\"task_type\")\n}\n\nenum Priority {\n  low\n  medium\n  high\n  urgent\n\n  @@map(\"priority\")\n}\n\nenum TaskState {\n  pending\n  in_progress\n  completed\n  cancelled\n  overdue\n\n  @@map(\"task_state\")\n}\n\nenum PestType {\n  INSECT\n  FUNGUS\n  BACTERIA\n  VIRUS\n  WEED\n  RODENT\n  BIRD\n  NEMATODE\n  OTHER\n\n  @@map(\"pest_type\")\n}\n\nenum IncidentStatus {\n  DETECTED\n  MONITORING\n  TREATING\n  RESOLVED\n  RECURRING\n\n  @@map(\"incident_status\")\n}\n",
  "inlineSchemaHash": "cc037cccdf848db87e501b1feec94b0c1485b73f8b4a026df7e331cfbfb482d2",
  "copyEngine": true
}

const fs = require('fs')

config.dirname = __dirname
if (!fs.existsSync(path.join(__dirname, 'schema.prisma'))) {
  const alternativePaths = [
    "prisma/.prisma/client",
    ".prisma/client",
  ]
  
  const alternativePath = alternativePaths.find((altPath) => {
    return fs.existsSync(path.join(process.cwd(), altPath, 'schema.prisma'))
  }) ?? alternativePaths[0]

  config.dirname = path.join(process.cwd(), alternativePath)
  config.isBundled = true
}

config.runtimeDataModel = JSON.parse("{\"models\":{\"Farm\":{\"dbName\":\"farms\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"version\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":1,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"ownerId\",\"dbName\":\"owner_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"totalAreaHectares\",\"dbName\":\"total_area_hectares\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"address\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"phone\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"email\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"metadata\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"isDeleted\",\"dbName\":\"is_deleted\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":false,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"serverUpdatedAt\",\"dbName\":\"server_updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"etag\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"fields\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Field\",\"relationName\":\"FarmToField\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"Field\":{\"dbName\":\"fields\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"version\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":1,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"cropType\",\"dbName\":\"crop_type\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"ownerId\",\"dbName\":\"owner_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"farmId\",\"dbName\":\"farm_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"farm\",\"kind\":\"object\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Farm\",\"relationName\":\"FarmToField\",\"relationFromFields\":[\"farmId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"SetNull\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"areaHectares\",\"dbName\":\"area_hectares\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"healthScore\",\"dbName\":\"health_score\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"ndviValue\",\"dbName\":\"ndvi_value\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"FieldStatus\",\"default\":\"active\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"plantingDate\",\"dbName\":\"planting_date\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"expectedHarvest\",\"dbName\":\"expected_harvest\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"irrigationType\",\"dbName\":\"irrigation_type\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"soilType\",\"dbName\":\"soil_type\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"metadata\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"isDeleted\",\"dbName\":\"is_deleted\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":false,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"serverUpdatedAt\",\"dbName\":\"server_updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"etag\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"boundaryHistory\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"FieldBoundaryHistory\",\"relationName\":\"FieldToFieldBoundaryHistory\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tasks\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Task\",\"relationName\":\"FieldToTask\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"ndviReadings\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"NdviReading\",\"relationName\":\"FieldToNdviReading\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"FieldBoundaryHistory\":{\"dbName\":\"field_boundary_history\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fieldId\",\"dbName\":\"field_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"versionAtChange\",\"dbName\":\"version_at_change\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Int\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"areaChangeHectares\",\"dbName\":\"area_change_hectares\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"changedBy\",\"dbName\":\"changed_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"changeReason\",\"dbName\":\"change_reason\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"changeSource\",\"dbName\":\"change_source\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"ChangeSource\",\"default\":\"api\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceId\",\"dbName\":\"device_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"field\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Field\",\"relationName\":\"FieldToFieldBoundaryHistory\",\"relationFromFields\":[\"fieldId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"SyncStatus\":{\"dbName\":\"sync_status\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceId\",\"dbName\":\"device_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"userId\",\"dbName\":\"user_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastSyncAt\",\"dbName\":\"last_sync_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastSyncVersion\",\"dbName\":\"last_sync_version\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"BigInt\",\"default\":\"0\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"SyncState\",\"default\":\"idle\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"pendingUploads\",\"dbName\":\"pending_uploads\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"pendingDownloads\",\"dbName\":\"pending_downloads\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"conflictsCount\",\"dbName\":\"conflicts_count\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastError\",\"dbName\":\"last_error\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceInfo\",\"dbName\":\"device_info\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[[\"deviceId\",\"userId\"]],\"uniqueIndexes\":[{\"name\":\"idx_sync_device_user\",\"fields\":[\"deviceId\",\"userId\"]}],\"isGenerated\":false},\"Task\":{\"dbName\":\"tasks\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"title\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"titleAr\",\"dbName\":\"title_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"description\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"taskType\",\"dbName\":\"task_type\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"TaskType\",\"default\":\"other\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"priority\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Priority\",\"default\":\"medium\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"TaskState\",\"default\":\"pending\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"dueDate\",\"dbName\":\"due_date\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"scheduledTime\",\"dbName\":\"scheduled_time\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"completedAt\",\"dbName\":\"completed_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"assignedTo\",\"dbName\":\"assigned_to\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdBy\",\"dbName\":\"created_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fieldId\",\"dbName\":\"field_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"field\",\"kind\":\"object\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Field\",\"relationName\":\"FieldToTask\",\"relationFromFields\":[\"fieldId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"SetNull\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"estimatedMinutes\",\"dbName\":\"estimated_minutes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Int\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"actualMinutes\",\"dbName\":\"actual_minutes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Int\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"completionNotes\",\"dbName\":\"completion_notes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"evidence\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"serverUpdatedAt\",\"dbName\":\"server_updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"NdviReading\":{\"dbName\":\"ndvi_readings\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fieldId\",\"dbName\":\"field_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"field\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Field\",\"relationName\":\"FieldToNdviReading\",\"relationFromFields\":[\"fieldId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"value\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"capturedAt\",\"dbName\":\"captured_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"source\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":\"satellite\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"cloudCover\",\"dbName\":\"cloud_cover\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"quality\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"satelliteName\",\"dbName\":\"satellite_name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"bandInfo\",\"dbName\":\"band_info\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"PestIncident\":{\"dbName\":\"pest_incidents\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fieldId\",\"dbName\":\"field_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"cropSeasonId\",\"dbName\":\"crop_season_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"pestType\",\"dbName\":\"pest_type\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"PestType\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"pestName\",\"dbName\":\"pest_name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"severityLevel\",\"dbName\":\"severity_level\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Int\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"affectedArea\",\"dbName\":\"affected_area\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"IncidentStatus\",\"default\":\"DETECTED\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"detectedAt\",\"dbName\":\"detected_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"reportedBy\",\"dbName\":\"reported_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"location\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"photos\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"notes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"treatments\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"PestTreatment\",\"relationName\":\"PestIncidentToPestTreatment\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"PestTreatment\":{\"dbName\":\"pest_treatments\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"incidentId\",\"dbName\":\"incident_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"treatmentDate\",\"dbName\":\"treatment_date\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"method\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"productUsed\",\"dbName\":\"product_used\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"productId\",\"dbName\":\"product_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"quantity\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"unit\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"appliedBy\",\"dbName\":\"applied_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"effectiveness\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Int\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"cost\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Decimal\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"notes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"incident\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"PestIncident\",\"relationName\":\"PestIncidentToPestTreatment\",\"relationFromFields\":[\"incidentId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false}},\"enums\":{\"FieldStatus\":{\"values\":[{\"name\":\"active\",\"dbName\":null},{\"name\":\"fallow\",\"dbName\":null},{\"name\":\"harvested\",\"dbName\":null},{\"name\":\"preparing\",\"dbName\":null},{\"name\":\"inactive\",\"dbName\":null}],\"dbName\":\"field_status\"},\"ChangeSource\":{\"values\":[{\"name\":\"mobile\",\"dbName\":null},{\"name\":\"web\",\"dbName\":null},{\"name\":\"api\",\"dbName\":null},{\"name\":\"system\",\"dbName\":null}],\"dbName\":\"change_source\"},\"SyncState\":{\"values\":[{\"name\":\"idle\",\"dbName\":null},{\"name\":\"syncing\",\"dbName\":null},{\"name\":\"error\",\"dbName\":null},{\"name\":\"conflict\",\"dbName\":null}],\"dbName\":\"sync_state\"},\"TaskType\":{\"values\":[{\"name\":\"irrigation\",\"dbName\":null},{\"name\":\"fertilization\",\"dbName\":null},{\"name\":\"spraying\",\"dbName\":null},{\"name\":\"scouting\",\"dbName\":null},{\"name\":\"maintenance\",\"dbName\":null},{\"name\":\"sampling\",\"dbName\":null},{\"name\":\"harvest\",\"dbName\":null},{\"name\":\"planting\",\"dbName\":null},{\"name\":\"other\",\"dbName\":null}],\"dbName\":\"task_type\"},\"Priority\":{\"values\":[{\"name\":\"low\",\"dbName\":null},{\"name\":\"medium\",\"dbName\":null},{\"name\":\"high\",\"dbName\":null},{\"name\":\"urgent\",\"dbName\":null}],\"dbName\":\"priority\"},\"TaskState\":{\"values\":[{\"name\":\"pending\",\"dbName\":null},{\"name\":\"in_progress\",\"dbName\":null},{\"name\":\"completed\",\"dbName\":null},{\"name\":\"cancelled\",\"dbName\":null},{\"name\":\"overdue\",\"dbName\":null}],\"dbName\":\"task_state\"},\"PestType\":{\"values\":[{\"name\":\"INSECT\",\"dbName\":null},{\"name\":\"FUNGUS\",\"dbName\":null},{\"name\":\"BACTERIA\",\"dbName\":null},{\"name\":\"VIRUS\",\"dbName\":null},{\"name\":\"WEED\",\"dbName\":null},{\"name\":\"RODENT\",\"dbName\":null},{\"name\":\"BIRD\",\"dbName\":null},{\"name\":\"NEMATODE\",\"dbName\":null},{\"name\":\"OTHER\",\"dbName\":null}],\"dbName\":\"pest_type\"},\"IncidentStatus\":{\"values\":[{\"name\":\"DETECTED\",\"dbName\":null},{\"name\":\"MONITORING\",\"dbName\":null},{\"name\":\"TREATING\",\"dbName\":null},{\"name\":\"RESOLVED\",\"dbName\":null},{\"name\":\"RECURRING\",\"dbName\":null}],\"dbName\":\"incident_status\"}},\"types\":{}}")
defineDmmfProperty(exports.Prisma, config.runtimeDataModel)
config.engineWasm = undefined


const { warnEnvConflicts } = require('./runtime/library.js')

warnEnvConflicts({
    rootEnvPath: config.relativeEnvPaths.rootEnvPath && path.resolve(config.dirname, config.relativeEnvPaths.rootEnvPath),
    schemaEnvPath: config.relativeEnvPaths.schemaEnvPath && path.resolve(config.dirname, config.relativeEnvPaths.schemaEnvPath)
})

const PrismaClient = getPrismaClient(config)
exports.PrismaClient = PrismaClient
Object.assign(exports, Prisma)

// file annotations for bundling tools to include these files
path.join(__dirname, "libquery_engine-debian-openssl-3.0.x.so.node");
path.join(process.cwd(), "prisma/.prisma/client/libquery_engine-debian-openssl-3.0.x.so.node")

// file annotations for bundling tools to include these files
path.join(__dirname, "libquery_engine-linux-musl-openssl-3.0.x.so.node");
path.join(process.cwd(), "prisma/.prisma/client/libquery_engine-linux-musl-openssl-3.0.x.so.node")
// file annotations for bundling tools to include these files
path.join(__dirname, "schema.prisma");
path.join(process.cwd(), "prisma/.prisma/client/schema.prisma")
