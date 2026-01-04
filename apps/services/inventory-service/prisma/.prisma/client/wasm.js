
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

exports.Prisma.InventoryItemScalarFieldEnum = {
  id: 'id',
  tenantId: 'tenantId',
  name: 'name',
  nameAr: 'nameAr',
  sku: 'sku',
  category: 'category',
  description: 'description',
  descriptionAr: 'descriptionAr',
  quantity: 'quantity',
  unit: 'unit',
  reorderLevel: 'reorderLevel',
  reorderPoint: 'reorderPoint',
  maxStock: 'maxStock',
  unitCost: 'unitCost',
  sellingPrice: 'sellingPrice',
  location: 'location',
  batchNumber: 'batchNumber',
  expiryDate: 'expiryDate',
  minTemperature: 'minTemperature',
  maxTemperature: 'maxTemperature',
  minHumidity: 'minHumidity',
  maxHumidity: 'maxHumidity',
  supplier: 'supplier',
  barcode: 'barcode',
  imageUrl: 'imageUrl',
  notes: 'notes',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt',
  lastRestocked: 'lastRestocked'
};

exports.Prisma.InventoryMovementScalarFieldEnum = {
  id: 'id',
  itemId: 'itemId',
  tenantId: 'tenantId',
  type: 'type',
  quantity: 'quantity',
  unitCost: 'unitCost',
  referenceId: 'referenceId',
  referenceType: 'referenceType',
  fromLocation: 'fromLocation',
  toLocation: 'toLocation',
  notes: 'notes',
  notesAr: 'notesAr',
  performedBy: 'performedBy',
  createdAt: 'createdAt'
};

exports.Prisma.InventoryAlertScalarFieldEnum = {
  id: 'id',
  alertType: 'alertType',
  priority: 'priority',
  status: 'status',
  itemId: 'itemId',
  itemName: 'itemName',
  itemNameAr: 'itemNameAr',
  titleEn: 'titleEn',
  titleAr: 'titleAr',
  messageEn: 'messageEn',
  messageAr: 'messageAr',
  currentValue: 'currentValue',
  thresholdValue: 'thresholdValue',
  recommendedActionEn: 'recommendedActionEn',
  recommendedActionAr: 'recommendedActionAr',
  actionUrl: 'actionUrl',
  createdAt: 'createdAt',
  acknowledgedAt: 'acknowledgedAt',
  acknowledgedBy: 'acknowledgedBy',
  resolvedAt: 'resolvedAt',
  resolvedBy: 'resolvedBy',
  resolutionNotes: 'resolutionNotes',
  snoozeUntil: 'snoozeUntil'
};

exports.Prisma.AlertSettingsScalarFieldEnum = {
  id: 'id',
  tenantId: 'tenantId',
  expiryWarningDays: 'expiryWarningDays',
  expiryCriticalDays: 'expiryCriticalDays',
  defaultReorderLevel: 'defaultReorderLevel',
  enableEmailAlerts: 'enableEmailAlerts',
  enablePushAlerts: 'enablePushAlerts',
  enableSmsAlerts: 'enableSmsAlerts',
  alertCheckInterval: 'alertCheckInterval',
  maxAlertsPerDay: 'maxAlertsPerDay',
  autoResolveOnRestock: 'autoResolveOnRestock',
  autoResolveExpired: 'autoResolveExpired',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.WarehouseScalarFieldEnum = {
  id: 'id',
  name: 'name',
  nameAr: 'nameAr',
  warehouseType: 'warehouseType',
  latitude: 'latitude',
  longitude: 'longitude',
  address: 'address',
  governorate: 'governorate',
  capacityValue: 'capacityValue',
  capacityUnit: 'capacityUnit',
  currentUsage: 'currentUsage',
  storageCondition: 'storageCondition',
  tempMin: 'tempMin',
  tempMax: 'tempMax',
  humidityMin: 'humidityMin',
  humidityMax: 'humidityMax',
  isActive: 'isActive',
  managerId: 'managerId',
  managerName: 'managerName',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ZoneScalarFieldEnum = {
  id: 'id',
  warehouseId: 'warehouseId',
  name: 'name',
  nameAr: 'nameAr',
  capacity: 'capacity',
  currentUsage: 'currentUsage',
  condition: 'condition',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.StorageLocationScalarFieldEnum = {
  id: 'id',
  zoneId: 'zoneId',
  aisle: 'aisle',
  shelf: 'shelf',
  bin: 'bin',
  locationCode: 'locationCode',
  capacity: 'capacity',
  isOccupied: 'isOccupied',
  currentItemId: 'currentItemId',
  currentQty: 'currentQty',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.StockTransferScalarFieldEnum = {
  id: 'id',
  itemId: 'itemId',
  fromWarehouseId: 'fromWarehouseId',
  toWarehouseId: 'toWarehouseId',
  quantity: 'quantity',
  unitCost: 'unitCost',
  totalCost: 'totalCost',
  transferType: 'transferType',
  status: 'status',
  requestedBy: 'requestedBy',
  approvedBy: 'approvedBy',
  performedBy: 'performedBy',
  requestedAt: 'requestedAt',
  approvedAt: 'approvedAt',
  completedAt: 'completedAt',
  notes: 'notes'
};

exports.Prisma.SortOrder = {
  asc: 'asc',
  desc: 'desc'
};

exports.Prisma.QueryMode = {
  default: 'default',
  insensitive: 'insensitive'
};

exports.Prisma.NullsOrder = {
  first: 'first',
  last: 'last'
};
exports.ItemCategory = exports.$Enums.ItemCategory = {
  SEEDS: 'SEEDS',
  FERTILIZER: 'FERTILIZER',
  PESTICIDE: 'PESTICIDE',
  HERBICIDE: 'HERBICIDE',
  FUNGICIDE: 'FUNGICIDE',
  INSECTICIDE: 'INSECTICIDE',
  EQUIPMENT: 'EQUIPMENT',
  TOOLS: 'TOOLS',
  IRRIGATION: 'IRRIGATION',
  PACKAGING: 'PACKAGING',
  FUEL: 'FUEL',
  OTHER: 'OTHER'
};

exports.MovementType = exports.$Enums.MovementType = {
  PURCHASE: 'PURCHASE',
  SALE: 'SALE',
  RETURN: 'RETURN',
  ADJUSTMENT: 'ADJUSTMENT',
  TRANSFER: 'TRANSFER',
  WASTE: 'WASTE',
  USAGE: 'USAGE',
  PRODUCTION: 'PRODUCTION',
  RESTOCK: 'RESTOCK'
};

exports.AlertType = exports.$Enums.AlertType = {
  LOW_STOCK: 'LOW_STOCK',
  OUT_OF_STOCK: 'OUT_OF_STOCK',
  EXPIRING_SOON: 'EXPIRING_SOON',
  EXPIRED: 'EXPIRED',
  REORDER_POINT: 'REORDER_POINT',
  OVERSTOCK: 'OVERSTOCK',
  STORAGE_CONDITION: 'STORAGE_CONDITION'
};

exports.AlertPriority = exports.$Enums.AlertPriority = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL'
};

exports.AlertStatus = exports.$Enums.AlertStatus = {
  ACTIVE: 'ACTIVE',
  ACKNOWLEDGED: 'ACKNOWLEDGED',
  RESOLVED: 'RESOLVED',
  SNOOZED: 'SNOOZED'
};

exports.WarehouseType = exports.$Enums.WarehouseType = {
  MAIN: 'MAIN',
  FIELD: 'FIELD',
  COLD: 'COLD',
  CHEMICAL: 'CHEMICAL',
  SEED: 'SEED',
  FUEL: 'FUEL'
};

exports.StorageCondition = exports.$Enums.StorageCondition = {
  AMBIENT: 'AMBIENT',
  COOL: 'COOL',
  COLD: 'COLD',
  FROZEN: 'FROZEN',
  DRY: 'DRY',
  CONTROLLED: 'CONTROLLED'
};

exports.TransferType = exports.$Enums.TransferType = {
  INTER_WAREHOUSE: 'INTER_WAREHOUSE',
  RECEIVING: 'RECEIVING',
  DISPATCH: 'DISPATCH'
};

exports.TransferStatus = exports.$Enums.TransferStatus = {
  PENDING: 'PENDING',
  APPROVED: 'APPROVED',
  IN_TRANSIT: 'IN_TRANSIT',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED'
};

exports.Prisma.ModelName = {
  InventoryItem: 'InventoryItem',
  InventoryMovement: 'InventoryMovement',
  InventoryAlert: 'InventoryAlert',
  AlertSettings: 'AlertSettings',
  Warehouse: 'Warehouse',
  Zone: 'Zone',
  StorageLocation: 'StorageLocation',
  StockTransfer: 'StockTransfer'
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
