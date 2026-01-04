
Object.defineProperty(exports, "__esModule", { value: true });

const {
  Decimal,
  objectEnumValues,
  makeStrictEnum,
  Public,
  getRuntime,
  skip
} = require('./runtime/index-browser.js')


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

Prisma.PrismaClientKnownRequestError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientKnownRequestError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)};
Prisma.PrismaClientUnknownRequestError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientUnknownRequestError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.PrismaClientRustPanicError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientRustPanicError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.PrismaClientInitializationError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientInitializationError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.PrismaClientValidationError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientValidationError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.NotFoundError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`NotFoundError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.Decimal = Decimal

/**
 * Re-export of sql-template-tag
 */
Prisma.sql = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`sqltag is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.empty = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`empty is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.join = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`join is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.raw = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`raw is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.validator = Public.validator

/**
* Extensions
*/
Prisma.getExtensionContext = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`Extensions.getExtensionContext is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.defineExtension = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`Extensions.defineExtension is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}

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
 * This is a stub Prisma Client that will error at runtime if called.
 */
class PrismaClient {
  constructor() {
    return new Proxy(this, {
      get(target, prop) {
        let message
        const runtime = getRuntime()
        if (runtime.isEdge) {
          message = `PrismaClient is not configured to run in ${runtime.prettyName}. In order to run Prisma Client on edge runtime, either:
- Use Prisma Accelerate: https://pris.ly/d/accelerate
- Use Driver Adapters: https://pris.ly/d/driver-adapters
`;
        } else {
          message = 'PrismaClient is unable to run in this browser environment, or has been bundled for the browser (running in `' + runtime.prettyName + '`).'
        }
        
        message += `
If this is unexpected, please open an issue: https://pris.ly/prisma-prisma-bug-report`

        throw new Error(message)
      }
    })
  }
}

exports.PrismaClient = PrismaClient

Object.assign(exports, Prisma)
