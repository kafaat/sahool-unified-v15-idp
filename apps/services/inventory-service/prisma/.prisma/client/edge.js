
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
      "value": "/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/services/inventory-service/prisma/.prisma/client",
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
    "previewFeatures": [],
    "sourceFilePath": "/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/services/inventory-service/prisma/schema.prisma",
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
  "inlineSchema": "// SAHOOL Inventory Service Schema\n// مخطط قاعدة بيانات خدمة المخزون\n\ndatasource db {\n  url      = env(\"DATABASE_URL\")\n  provider = \"postgresql\"\n}\n\ngenerator client {\n  provider      = \"prisma-client-js\"\n  output        = \".prisma/client\"\n  binaryTargets = [\"native\", \"linux-musl-openssl-3.0.x\", \"debian-openssl-3.0.x\"]\n}\n\n// ═══════════════════════════════════════════════════════════════════════════════\n// 1. Inventory Items - عناصر المخزون\n// ═══════════════════════════════════════════════════════════════════════════════\n\nmodel InventoryItem {\n  id       String @id @default(uuid())\n  tenantId String @map(\"tenant_id\")\n\n  // Basic info\n  name          String\n  nameAr        String       @map(\"name_ar\")\n  sku           String?      @unique\n  category      ItemCategory\n  description   String?\n  descriptionAr String?      @map(\"description_ar\")\n\n  // Quantities\n  quantity     Float  @default(0)\n  unit         String // kg, liter, bag, bottle, etc.\n  reorderLevel Float  @default(0) @map(\"reorder_level\")\n  reorderPoint Float? @map(\"reorder_point\")\n  maxStock     Float? @map(\"max_stock\")\n\n  // Pricing\n  unitCost     Float? @map(\"unit_cost\")\n  sellingPrice Float? @map(\"selling_price\")\n\n  // Storage\n  location    String? // Warehouse location\n  batchNumber String?   @map(\"batch_number\")\n  expiryDate  DateTime? @map(\"expiry_date\")\n\n  // Storage conditions\n  minTemperature Float? @map(\"min_temperature\")\n  maxTemperature Float? @map(\"max_temperature\")\n  minHumidity    Float? @map(\"min_humidity\")\n  maxHumidity    Float? @map(\"max_humidity\")\n\n  // Metadata\n  supplier String?\n  barcode  String?\n  imageUrl String? @map(\"image_url\")\n  notes    String?\n\n  // Tracking\n  createdAt     DateTime  @default(now()) @map(\"created_at\")\n  updatedAt     DateTime  @updatedAt @map(\"updated_at\")\n  lastRestocked DateTime? @map(\"last_restocked\")\n\n  // Relations\n  movements InventoryMovement[]\n  alerts    InventoryAlert[]\n\n  @@index([tenantId])\n  @@index([category])\n  @@index([quantity])\n  @@index([expiryDate])\n  @@map(\"inventory_items\")\n}\n\nenum ItemCategory {\n  SEEDS // بذور\n  FERTILIZER // أسمدة\n  PESTICIDE // مبيدات\n  HERBICIDE // مبيدات أعشاب\n  FUNGICIDE // مبيدات فطرية\n  INSECTICIDE // مبيدات حشرية\n  EQUIPMENT // معدات\n  TOOLS // أدوات\n  IRRIGATION // معدات الري\n  PACKAGING // مواد التعبئة\n  FUEL // وقود\n  OTHER // أخرى\n}\n\n// ═══════════════════════════════════════════════════════════════════════════════\n// 2. Inventory Movements - حركات المخزون\n// ═══════════════════════════════════════════════════════════════════════════════\n\nmodel InventoryMovement {\n  id       String @id @default(uuid())\n  itemId   String @map(\"item_id\")\n  tenantId String @map(\"tenant_id\")\n\n  // Movement details\n  type     MovementType\n  quantity Float\n  unitCost Float?       @map(\"unit_cost\")\n\n  // Reference\n  referenceId   String? @map(\"reference_id\")\n  referenceType String? @map(\"reference_type\") // purchase_order, sale, waste, adjustment\n\n  // Location\n  fromLocation String? @map(\"from_location\")\n  toLocation   String? @map(\"to_location\")\n\n  // Notes\n  notes   String?\n  notesAr String? @map(\"notes_ar\")\n\n  // Tracking\n  performedBy String   @map(\"performed_by\")\n  createdAt   DateTime @default(now()) @map(\"created_at\")\n\n  // Relations\n  item InventoryItem @relation(fields: [itemId], references: [id])\n\n  @@index([itemId])\n  @@index([tenantId])\n  @@index([type])\n  @@index([createdAt])\n  @@map(\"inventory_movements\")\n}\n\nenum MovementType {\n  PURCHASE // شراء\n  SALE // بيع\n  RETURN // إرجاع\n  ADJUSTMENT // تعديل\n  TRANSFER // نقل\n  WASTE // هدر\n  USAGE // استخدام\n  PRODUCTION // إنتاج\n  RESTOCK // إعادة تخزين\n}\n\n// ═══════════════════════════════════════════════════════════════════════════════\n// 3. Inventory Alerts - تنبيهات المخزون\n// ═══════════════════════════════════════════════════════════════════════════════\n\nmodel InventoryAlert {\n  id        String        @id @default(uuid())\n  alertType AlertType     @map(\"alert_type\")\n  priority  AlertPriority\n  status    AlertStatus   @default(ACTIVE)\n\n  // Item reference\n  itemId     String @map(\"item_id\")\n  itemName   String @map(\"item_name\")\n  itemNameAr String @map(\"item_name_ar\")\n\n  // Alert content\n  titleEn   String @map(\"title_en\")\n  titleAr   String @map(\"title_ar\")\n  messageEn String @map(\"message_en\")\n  messageAr String @map(\"message_ar\")\n\n  // Thresholds\n  currentValue   Float @map(\"current_value\")\n  thresholdValue Float @map(\"threshold_value\")\n\n  // Recommended actions\n  recommendedActionEn String  @map(\"recommended_action_en\")\n  recommendedActionAr String  @map(\"recommended_action_ar\")\n  actionUrl           String? @map(\"action_url\")\n\n  // Timing\n  createdAt       DateTime  @default(now()) @map(\"created_at\")\n  acknowledgedAt  DateTime? @map(\"acknowledged_at\")\n  acknowledgedBy  String?   @map(\"acknowledged_by\")\n  resolvedAt      DateTime? @map(\"resolved_at\")\n  resolvedBy      String?   @map(\"resolved_by\")\n  resolutionNotes String?   @map(\"resolution_notes\")\n  snoozeUntil     DateTime? @map(\"snooze_until\")\n\n  // Relations\n  item InventoryItem @relation(fields: [itemId], references: [id])\n\n  @@index([status, priority])\n  @@index([itemId])\n  @@index([alertType])\n  @@index([createdAt])\n  @@map(\"inventory_alerts\")\n}\n\nenum AlertType {\n  LOW_STOCK\n  OUT_OF_STOCK\n  EXPIRING_SOON\n  EXPIRED\n  REORDER_POINT\n  OVERSTOCK\n  STORAGE_CONDITION\n}\n\nenum AlertPriority {\n  LOW\n  MEDIUM\n  HIGH\n  CRITICAL\n}\n\nenum AlertStatus {\n  ACTIVE\n  ACKNOWLEDGED\n  RESOLVED\n  SNOOZED\n}\n\n// ═══════════════════════════════════════════════════════════════════════════════\n// 4. Alert Settings - إعدادات التنبيهات\n// ═══════════════════════════════════════════════════════════════════════════════\n\nmodel AlertSettings {\n  id       String @id @default(uuid())\n  tenantId String @unique @map(\"tenant_id\")\n\n  // Expiry warnings\n  expiryWarningDays  Int @default(30) @map(\"expiry_warning_days\")\n  expiryCriticalDays Int @default(7) @map(\"expiry_critical_days\")\n\n  // Stock thresholds\n  defaultReorderLevel Float @default(10) @map(\"default_reorder_level\")\n\n  // Notification preferences\n  enableEmailAlerts Boolean @default(true) @map(\"enable_email_alerts\")\n  enablePushAlerts  Boolean @default(true) @map(\"enable_push_alerts\")\n  enableSmsAlerts   Boolean @default(false) @map(\"enable_sms_alerts\")\n\n  // Alert frequency\n  alertCheckInterval Int @default(60) @map(\"alert_check_interval\") // minutes\n  maxAlertsPerDay    Int @default(100) @map(\"max_alerts_per_day\")\n\n  // Auto-resolve settings\n  autoResolveOnRestock Boolean @default(true) @map(\"auto_resolve_on_restock\")\n  autoResolveExpired   Boolean @default(false) @map(\"auto_resolve_expired\")\n\n  createdAt DateTime @default(now()) @map(\"created_at\")\n  updatedAt DateTime @updatedAt @map(\"updated_at\")\n\n  @@map(\"alert_settings\")\n}\n\n// ═══════════════════════════════════════════════════════════════════════════════\n// 5. Warehouse Management - إدارة المستودعات\n// ═══════════════════════════════════════════════════════════════════════════════\n\nmodel Warehouse {\n  id            String        @id @default(uuid())\n  name          String\n  nameAr        String        @map(\"name_ar\")\n  warehouseType WarehouseType @map(\"warehouse_type\")\n  latitude      Float?\n  longitude     Float?\n  address       String?\n  governorate   String?\n\n  // Capacity\n  capacityValue Float  @map(\"capacity_value\")\n  capacityUnit  String @default(\"cubic_meter\") @map(\"capacity_unit\")\n  currentUsage  Float  @default(0) @map(\"current_usage\")\n\n  // Conditions\n  storageCondition StorageCondition @default(AMBIENT) @map(\"storage_condition\")\n  tempMin          Float?           @map(\"temp_min\")\n  tempMax          Float?           @map(\"temp_max\")\n  humidityMin      Float?           @map(\"humidity_min\")\n  humidityMax      Float?           @map(\"humidity_max\")\n\n  // Status\n  isActive    Boolean @default(true) @map(\"is_active\")\n  managerId   String? @map(\"manager_id\")\n  managerName String? @map(\"manager_name\")\n\n  zones         Zone[]\n  transfersFrom StockTransfer[] @relation(\"FromWarehouse\")\n  transfersTo   StockTransfer[] @relation(\"ToWarehouse\")\n  createdAt     DateTime        @default(now()) @map(\"created_at\")\n  updatedAt     DateTime        @updatedAt @map(\"updated_at\")\n\n  @@map(\"warehouses\")\n}\n\nenum WarehouseType {\n  MAIN // مستودع رئيسي\n  FIELD // مخزن حقلي\n  COLD // تخزين بارد\n  CHEMICAL // مخزن كيماويات\n  SEED // بنك بذور\n  FUEL // مخزن وقود\n}\n\nenum StorageCondition {\n  AMBIENT // درجة حرارة الغرفة\n  COOL // بارد 10-15°C\n  COLD // بارد 2-8°C\n  FROZEN // مجمد\n  DRY // جاف\n  CONTROLLED // محكم التحكم\n}\n\n// Zone within a warehouse\nmodel Zone {\n  id           String            @id @default(uuid())\n  warehouseId  String            @map(\"warehouse_id\")\n  warehouse    Warehouse         @relation(fields: [warehouseId], references: [id], onDelete: Cascade)\n  name         String\n  nameAr       String?           @map(\"name_ar\")\n  capacity     Float\n  currentUsage Float             @default(0) @map(\"current_usage\")\n  condition    StorageCondition?\n\n  locations StorageLocation[]\n  createdAt DateTime          @default(now()) @map(\"created_at\")\n  updatedAt DateTime          @updatedAt @map(\"updated_at\")\n\n  @@index([warehouseId])\n  @@map(\"zones\")\n}\n\n// Storage Location (specific bin/shelf)\nmodel StorageLocation {\n  id            String  @id @default(uuid())\n  zoneId        String  @map(\"zone_id\")\n  zone          Zone    @relation(fields: [zoneId], references: [id], onDelete: Cascade)\n  aisle         String\n  shelf         String\n  bin           String\n  locationCode  String  @unique @map(\"location_code\") // A-01-03-B\n  capacity      Float\n  isOccupied    Boolean @default(false) @map(\"is_occupied\")\n  currentItemId String? @map(\"current_item_id\")\n  currentQty    Float   @default(0) @map(\"current_qty\")\n\n  createdAt DateTime @default(now()) @map(\"created_at\")\n  updatedAt DateTime @updatedAt @map(\"updated_at\")\n\n  @@index([zoneId])\n  @@index([locationCode])\n  @@map(\"storage_locations\")\n}\n\n// Stock Transfer between warehouses\nmodel StockTransfer {\n  id              String     @id @default(uuid())\n  itemId          String     @map(\"item_id\")\n  fromWarehouseId String?    @map(\"from_warehouse_id\")\n  fromWarehouse   Warehouse? @relation(\"FromWarehouse\", fields: [fromWarehouseId], references: [id])\n  toWarehouseId   String     @map(\"to_warehouse_id\")\n  toWarehouse     Warehouse  @relation(\"ToWarehouse\", fields: [toWarehouseId], references: [id])\n\n  quantity  Float\n  unitCost  Float? @map(\"unit_cost\")\n  totalCost Float? @map(\"total_cost\")\n\n  transferType TransferType   @map(\"transfer_type\")\n  status       TransferStatus @default(PENDING)\n\n  // Tracking\n  requestedBy String  @map(\"requested_by\")\n  approvedBy  String? @map(\"approved_by\")\n  performedBy String? @map(\"performed_by\")\n\n  // Dates\n  requestedAt DateTime  @default(now()) @map(\"requested_at\")\n  approvedAt  DateTime? @map(\"approved_at\")\n  completedAt DateTime? @map(\"completed_at\")\n\n  notes String?\n\n  @@index([itemId])\n  @@index([fromWarehouseId])\n  @@index([toWarehouseId])\n  @@index([status])\n  @@map(\"stock_transfers\")\n}\n\nenum TransferType {\n  INTER_WAREHOUSE // نقل بين المستودعات\n  RECEIVING // استلام من المورد\n  DISPATCH // إرسال للحقل/العميل\n}\n\nenum TransferStatus {\n  PENDING // معلق\n  APPROVED // موافق عليه\n  IN_TRANSIT // قيد النقل\n  COMPLETED // مكتمل\n  CANCELLED // ملغي\n}\n",
  "inlineSchemaHash": "905531dc07c7fa946589325defcb2fd630251b2fa17ed6b9a7acc1a7955c002a",
  "copyEngine": true
}
config.dirname = '/'

config.runtimeDataModel = JSON.parse("{\"models\":{\"InventoryItem\":{\"dbName\":\"inventory_items\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"nameAr\",\"dbName\":\"name_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"sku\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":true,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"category\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"ItemCategory\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"description\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"descriptionAr\",\"dbName\":\"description_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"quantity\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Float\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"unit\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"reorderLevel\",\"dbName\":\"reorder_level\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Float\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"reorderPoint\",\"dbName\":\"reorder_point\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"maxStock\",\"dbName\":\"max_stock\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"unitCost\",\"dbName\":\"unit_cost\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"sellingPrice\",\"dbName\":\"selling_price\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"location\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"batchNumber\",\"dbName\":\"batch_number\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"expiryDate\",\"dbName\":\"expiry_date\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"minTemperature\",\"dbName\":\"min_temperature\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"maxTemperature\",\"dbName\":\"max_temperature\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"minHumidity\",\"dbName\":\"min_humidity\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"maxHumidity\",\"dbName\":\"max_humidity\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"supplier\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"barcode\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"imageUrl\",\"dbName\":\"image_url\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"notes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"lastRestocked\",\"dbName\":\"last_restocked\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"movements\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"InventoryMovement\",\"relationName\":\"InventoryItemToInventoryMovement\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"alerts\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"InventoryAlert\",\"relationName\":\"InventoryAlertToInventoryItem\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"InventoryMovement\":{\"dbName\":\"inventory_movements\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"itemId\",\"dbName\":\"item_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"type\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"MovementType\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"quantity\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"unitCost\",\"dbName\":\"unit_cost\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"referenceId\",\"dbName\":\"reference_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"referenceType\",\"dbName\":\"reference_type\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fromLocation\",\"dbName\":\"from_location\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"toLocation\",\"dbName\":\"to_location\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"notes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"notesAr\",\"dbName\":\"notes_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"performedBy\",\"dbName\":\"performed_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"item\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"InventoryItem\",\"relationName\":\"InventoryItemToInventoryMovement\",\"relationFromFields\":[\"itemId\"],\"relationToFields\":[\"id\"],\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"InventoryAlert\":{\"dbName\":\"inventory_alerts\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"alertType\",\"dbName\":\"alert_type\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"AlertType\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"priority\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"AlertPriority\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"AlertStatus\",\"default\":\"ACTIVE\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"itemId\",\"dbName\":\"item_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"itemName\",\"dbName\":\"item_name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"itemNameAr\",\"dbName\":\"item_name_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"titleEn\",\"dbName\":\"title_en\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"titleAr\",\"dbName\":\"title_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"messageEn\",\"dbName\":\"message_en\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"messageAr\",\"dbName\":\"message_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"currentValue\",\"dbName\":\"current_value\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"thresholdValue\",\"dbName\":\"threshold_value\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"recommendedActionEn\",\"dbName\":\"recommended_action_en\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"recommendedActionAr\",\"dbName\":\"recommended_action_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"actionUrl\",\"dbName\":\"action_url\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"acknowledgedAt\",\"dbName\":\"acknowledged_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"acknowledgedBy\",\"dbName\":\"acknowledged_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"resolvedAt\",\"dbName\":\"resolved_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"resolvedBy\",\"dbName\":\"resolved_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"resolutionNotes\",\"dbName\":\"resolution_notes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"snoozeUntil\",\"dbName\":\"snooze_until\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"item\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"InventoryItem\",\"relationName\":\"InventoryAlertToInventoryItem\",\"relationFromFields\":[\"itemId\"],\"relationToFields\":[\"id\"],\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"AlertSettings\":{\"dbName\":\"alert_settings\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":true,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"expiryWarningDays\",\"dbName\":\"expiry_warning_days\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":30,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"expiryCriticalDays\",\"dbName\":\"expiry_critical_days\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":7,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"defaultReorderLevel\",\"dbName\":\"default_reorder_level\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Float\",\"default\":10,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"enableEmailAlerts\",\"dbName\":\"enable_email_alerts\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":true,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"enablePushAlerts\",\"dbName\":\"enable_push_alerts\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":true,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"enableSmsAlerts\",\"dbName\":\"enable_sms_alerts\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":false,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"alertCheckInterval\",\"dbName\":\"alert_check_interval\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":60,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"maxAlertsPerDay\",\"dbName\":\"max_alerts_per_day\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":100,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"autoResolveOnRestock\",\"dbName\":\"auto_resolve_on_restock\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":true,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"autoResolveExpired\",\"dbName\":\"auto_resolve_expired\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":false,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"Warehouse\":{\"dbName\":\"warehouses\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"nameAr\",\"dbName\":\"name_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"warehouseType\",\"dbName\":\"warehouse_type\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"WarehouseType\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"latitude\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"longitude\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"address\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"governorate\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"capacityValue\",\"dbName\":\"capacity_value\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"capacityUnit\",\"dbName\":\"capacity_unit\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":\"cubic_meter\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"currentUsage\",\"dbName\":\"current_usage\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Float\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"storageCondition\",\"dbName\":\"storage_condition\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"StorageCondition\",\"default\":\"AMBIENT\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tempMin\",\"dbName\":\"temp_min\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tempMax\",\"dbName\":\"temp_max\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"humidityMin\",\"dbName\":\"humidity_min\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"humidityMax\",\"dbName\":\"humidity_max\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"isActive\",\"dbName\":\"is_active\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":true,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"managerId\",\"dbName\":\"manager_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"managerName\",\"dbName\":\"manager_name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"zones\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Zone\",\"relationName\":\"WarehouseToZone\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"transfersFrom\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"StockTransfer\",\"relationName\":\"FromWarehouse\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"transfersTo\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"StockTransfer\",\"relationName\":\"ToWarehouse\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"Zone\":{\"dbName\":\"zones\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"warehouseId\",\"dbName\":\"warehouse_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"warehouse\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Warehouse\",\"relationName\":\"WarehouseToZone\",\"relationFromFields\":[\"warehouseId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"nameAr\",\"dbName\":\"name_ar\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"capacity\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"currentUsage\",\"dbName\":\"current_usage\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Float\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"condition\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"StorageCondition\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"locations\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"StorageLocation\",\"relationName\":\"StorageLocationToZone\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"StorageLocation\":{\"dbName\":\"storage_locations\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"zoneId\",\"dbName\":\"zone_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"zone\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Zone\",\"relationName\":\"StorageLocationToZone\",\"relationFromFields\":[\"zoneId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"aisle\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"shelf\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"bin\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"locationCode\",\"dbName\":\"location_code\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":true,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"capacity\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"isOccupied\",\"dbName\":\"is_occupied\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":false,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"currentItemId\",\"dbName\":\"current_item_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"currentQty\",\"dbName\":\"current_qty\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Float\",\"default\":0,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"StockTransfer\":{\"dbName\":\"stock_transfers\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"itemId\",\"dbName\":\"item_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fromWarehouseId\",\"dbName\":\"from_warehouse_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fromWarehouse\",\"kind\":\"object\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Warehouse\",\"relationName\":\"FromWarehouse\",\"relationFromFields\":[\"fromWarehouseId\"],\"relationToFields\":[\"id\"],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"toWarehouseId\",\"dbName\":\"to_warehouse_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"toWarehouse\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Warehouse\",\"relationName\":\"ToWarehouse\",\"relationFromFields\":[\"toWarehouseId\"],\"relationToFields\":[\"id\"],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"quantity\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"unitCost\",\"dbName\":\"unit_cost\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"totalCost\",\"dbName\":\"total_cost\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"transferType\",\"dbName\":\"transfer_type\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"TransferType\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"TransferStatus\",\"default\":\"PENDING\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"requestedBy\",\"dbName\":\"requested_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"approvedBy\",\"dbName\":\"approved_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"performedBy\",\"dbName\":\"performed_by\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"requestedAt\",\"dbName\":\"requested_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"approvedAt\",\"dbName\":\"approved_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"completedAt\",\"dbName\":\"completed_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"notes\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false}},\"enums\":{\"ItemCategory\":{\"values\":[{\"name\":\"SEEDS\",\"dbName\":null},{\"name\":\"FERTILIZER\",\"dbName\":null},{\"name\":\"PESTICIDE\",\"dbName\":null},{\"name\":\"HERBICIDE\",\"dbName\":null},{\"name\":\"FUNGICIDE\",\"dbName\":null},{\"name\":\"INSECTICIDE\",\"dbName\":null},{\"name\":\"EQUIPMENT\",\"dbName\":null},{\"name\":\"TOOLS\",\"dbName\":null},{\"name\":\"IRRIGATION\",\"dbName\":null},{\"name\":\"PACKAGING\",\"dbName\":null},{\"name\":\"FUEL\",\"dbName\":null},{\"name\":\"OTHER\",\"dbName\":null}],\"dbName\":null},\"MovementType\":{\"values\":[{\"name\":\"PURCHASE\",\"dbName\":null},{\"name\":\"SALE\",\"dbName\":null},{\"name\":\"RETURN\",\"dbName\":null},{\"name\":\"ADJUSTMENT\",\"dbName\":null},{\"name\":\"TRANSFER\",\"dbName\":null},{\"name\":\"WASTE\",\"dbName\":null},{\"name\":\"USAGE\",\"dbName\":null},{\"name\":\"PRODUCTION\",\"dbName\":null},{\"name\":\"RESTOCK\",\"dbName\":null}],\"dbName\":null},\"AlertType\":{\"values\":[{\"name\":\"LOW_STOCK\",\"dbName\":null},{\"name\":\"OUT_OF_STOCK\",\"dbName\":null},{\"name\":\"EXPIRING_SOON\",\"dbName\":null},{\"name\":\"EXPIRED\",\"dbName\":null},{\"name\":\"REORDER_POINT\",\"dbName\":null},{\"name\":\"OVERSTOCK\",\"dbName\":null},{\"name\":\"STORAGE_CONDITION\",\"dbName\":null}],\"dbName\":null},\"AlertPriority\":{\"values\":[{\"name\":\"LOW\",\"dbName\":null},{\"name\":\"MEDIUM\",\"dbName\":null},{\"name\":\"HIGH\",\"dbName\":null},{\"name\":\"CRITICAL\",\"dbName\":null}],\"dbName\":null},\"AlertStatus\":{\"values\":[{\"name\":\"ACTIVE\",\"dbName\":null},{\"name\":\"ACKNOWLEDGED\",\"dbName\":null},{\"name\":\"RESOLVED\",\"dbName\":null},{\"name\":\"SNOOZED\",\"dbName\":null}],\"dbName\":null},\"WarehouseType\":{\"values\":[{\"name\":\"MAIN\",\"dbName\":null},{\"name\":\"FIELD\",\"dbName\":null},{\"name\":\"COLD\",\"dbName\":null},{\"name\":\"CHEMICAL\",\"dbName\":null},{\"name\":\"SEED\",\"dbName\":null},{\"name\":\"FUEL\",\"dbName\":null}],\"dbName\":null},\"StorageCondition\":{\"values\":[{\"name\":\"AMBIENT\",\"dbName\":null},{\"name\":\"COOL\",\"dbName\":null},{\"name\":\"COLD\",\"dbName\":null},{\"name\":\"FROZEN\",\"dbName\":null},{\"name\":\"DRY\",\"dbName\":null},{\"name\":\"CONTROLLED\",\"dbName\":null}],\"dbName\":null},\"TransferType\":{\"values\":[{\"name\":\"INTER_WAREHOUSE\",\"dbName\":null},{\"name\":\"RECEIVING\",\"dbName\":null},{\"name\":\"DISPATCH\",\"dbName\":null}],\"dbName\":null},\"TransferStatus\":{\"values\":[{\"name\":\"PENDING\",\"dbName\":null},{\"name\":\"APPROVED\",\"dbName\":null},{\"name\":\"IN_TRANSIT\",\"dbName\":null},{\"name\":\"COMPLETED\",\"dbName\":null},{\"name\":\"CANCELLED\",\"dbName\":null}],\"dbName\":null}},\"types\":{}}")
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

