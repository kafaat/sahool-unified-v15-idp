/**
 * SAHOOL Field & Farm Types
 * أنواع الحقول والمزارع
 *
 * Comprehensive type definitions for field management,
 * geospatial data, and agricultural operations.
 */

// ═══════════════════════════════════════════════════════════════════════════
// Geographic Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * GeoJSON Point geometry
 */
export interface GeoJSONPoint {
  type: "Point";
  coordinates: [number, number]; // [longitude, latitude]
}

/**
 * GeoJSON Polygon geometry
 */
export interface GeoJSONPolygon {
  type: "Polygon";
  coordinates: Array<Array<[number, number]>>;
}

/**
 * GeoJSON MultiPolygon geometry
 */
export interface GeoJSONMultiPolygon {
  type: "MultiPolygon";
  coordinates: Array<Array<Array<[number, number]>>>;
}

export type FieldGeometry = GeoJSONPolygon | GeoJSONMultiPolygon;

// ═══════════════════════════════════════════════════════════════════════════
// Farm Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Farm status
 */
export type FarmStatus = "active" | "inactive" | "pending" | "archived";

/**
 * Water source types
 */
export type WaterSource =
  | "well"          // بئر
  | "canal"         // قناة
  | "river"         // نهر
  | "rainwater"     // مياه أمطار
  | "dam"           // سد
  | "spring"        // ينبوع
  | "municipal";    // مياه بلدية

/**
 * Farm entity
 */
export interface Farm {
  id: string;
  name: string;
  nameAr: string;
  ownerId: string;
  tenantId: string;
  status: FarmStatus;
  totalAreaHectares: number;
  location: GeoJSONPoint;
  address?: string;
  addressAr?: string;
  governorate?: string;
  governorateAr?: string;
  district?: string;
  districtAr?: string;
  waterSources: WaterSource[];
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, unknown>;
}

/**
 * Farm creation payload
 */
export interface CreateFarmPayload {
  name: string;
  nameAr?: string;
  location: GeoJSONPoint;
  totalAreaHectares?: number;
  address?: string;
  addressAr?: string;
  governorate?: string;
  governorateAr?: string;
  district?: string;
  districtAr?: string;
  waterSources?: WaterSource[];
}

/**
 * Farm update payload
 */
export interface UpdateFarmPayload extends Partial<CreateFarmPayload> {
  status?: FarmStatus;
}

// ═══════════════════════════════════════════════════════════════════════════
// Field Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Field status
 */
export type FieldStatus =
  | "active"        // نشط - قيد الاستخدام
  | "fallow"        // بور - في راحة
  | "preparing"     // معد - جاهز للزراعة
  | "harvested"     // محصود
  | "inactive"      // غير نشط
  | "deleted";      // محذوف (soft delete)

/**
 * Soil type classification
 */
export type SoilType =
  | "clay"          // طيني
  | "sandy"         // رملي
  | "loamy"         // طميي
  | "silty"         // غريني
  | "peaty"         // خثي
  | "chalky"        // طباشيري
  | "mixed";        // مختلط

/**
 * Irrigation type
 */
export type IrrigationType =
  | "drip"          // تنقيط
  | "sprinkler"     // رش
  | "flood"         // غمر
  | "pivot"         // محوري
  | "furrow"        // أخدود
  | "rainfed"       // بعلي
  | "subsurface";   // تحت السطح

/**
 * Soil analysis data
 */
export interface SoilAnalysis {
  ph: number;
  organicMatter: number;           // percentage
  nitrogen: number;                 // ppm
  phosphorus: number;               // ppm
  potassium: number;                // ppm
  calcium?: number;                 // ppm
  magnesium?: number;               // ppm
  sulfur?: number;                  // ppm
  electricalConductivity?: number;  // dS/m
  cec?: number;                     // Cation Exchange Capacity (meq/100g)
  texture?: {
    sand: number;
    silt: number;
    clay: number;
  };
  sampleDate: string;
  labName?: string;
}

/**
 * Field entity
 *
 * Source of truth: field-management-service Prisma schema
 * All services should reference this type for Field operations
 */
export interface Field {
  id: string;
  version: number;                 // Optimistic locking (ETag-based conflict resolution)
  farmId?: string;                 // UUID reference to Farm
  name: string;
  nameAr?: string;
  tenantId: string;
  cropType?: string;               // Current crop type
  ownerId?: string;                // UUID of field owner
  status: FieldStatus;
  areaHectares?: number;           // Calculated from boundary (DECIMAL 10,4)
  geometry?: FieldGeometry;        // PostGIS boundary - Polygon SRID 4326
  centroid?: GeoJSONPoint;         // PostGIS centroid - Point SRID 4326
  boundingBox?: {                  // Computed from geometry
    minLon: number;
    minLat: number;
    maxLon: number;
    maxLat: number;
  };

  // Health & Analysis (updated by NDVI Engine)
  healthScore?: number;            // 0.0 - 1.0 (DECIMAL 3,2)
  ndviValue?: number;              // -1.0 to 1.0 (DECIMAL 4,3)

  // Terrain (optional, from terrain-core-service)
  elevation?: number;              // meters
  slope?: number;                  // percentage
  aspect?: number;                 // degrees

  // Agricultural Info
  soilType?: SoilType;
  irrigationType?: IrrigationType;
  lastSoilAnalysis?: SoilAnalysis;
  currentCropId?: string;
  plantingDate?: string;
  expectedHarvestDate?: string;
  tags?: string[];

  // Sync Metadata (offline-first support)
  isDeleted?: boolean;             // Soft delete flag
  serverUpdatedAt?: string;        // Server-side last update (ISO 8601)
  etag?: string;                   // ETag for conflict resolution

  // Timestamps
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, unknown>;
}

/**
 * Field creation payload
 */
export interface CreateFieldPayload {
  farmId: string;
  name: string;
  nameAr?: string;
  geometry: FieldGeometry;
  areaHectares?: number;           // Will be calculated from geometry if not provided
  soilType?: SoilType;
  irrigationType?: IrrigationType;
  tags?: string[];
}

/**
 * Field update payload
 */
export interface UpdateFieldPayload extends Partial<CreateFieldPayload> {
  status?: FieldStatus;
  currentCropId?: string;
  plantingDate?: string;
  expectedHarvestDate?: string;
}

/**
 * Field filters for list queries
 */
export interface FieldFilters {
  farmId?: string;
  status?: FieldStatus | FieldStatus[];
  soilType?: SoilType | SoilType[];
  irrigationType?: IrrigationType | IrrigationType[];
  cropId?: string;
  tags?: string[];
  minArea?: number;
  maxArea?: number;
  search?: string;
  page?: number;
  limit?: number;
  sortBy?: "name" | "areaHectares" | "createdAt" | "updatedAt";
  sortOrder?: "asc" | "desc";
}

// ═══════════════════════════════════════════════════════════════════════════
// Crop Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Crop growth stage
 */
export type CropStage =
  | "germination"       // إنبات
  | "seedling"          // شتلة
  | "vegetative"        // نمو خضري
  | "tillering"         // تفريع
  | "stem_elongation"   // استطالة الساق
  | "booting"           // انتفاخ الغمد
  | "heading"           // طرد السنابل
  | "flowering"         // إزهار
  | "pollination"       // تلقيح
  | "grain_fill"        // امتلاء الحبوب
  | "ripening"          // نضج
  | "maturity"          // اكتمال النضج
  | "harvest";          // حصاد

/**
 * Crop category
 */
export type CropCategory =
  | "cereals"           // حبوب
  | "legumes"           // بقوليات
  | "vegetables"        // خضروات
  | "fruits"            // فواكه
  | "oilseeds"          // بذور زيتية
  | "fiber"             // ألياف
  | "fodder"            // أعلاف
  | "cash_crops"        // محاصيل نقدية
  | "spices";           // توابل

/**
 * Crop entity
 */
export interface Crop {
  id: string;
  name: string;
  nameAr: string;
  scientificName: string;
  category: CropCategory;
  variety?: string;
  varietyAr?: string;
  growthDurationDays: number;
  waterRequirementMmPerDay: number;
  optimalTemperature: {
    min: number;
    max: number;
  };
  stages: Array<{
    stage: CropStage;
    stageAr: string;
    durationDays: number;
    waterMultiplier: number;
    nutrientRequirements?: {
      nitrogen: "low" | "medium" | "high";
      phosphorus: "low" | "medium" | "high";
      potassium: "low" | "medium" | "high";
    };
  }>;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

/**
 * Field crop planting record
 */
export interface FieldCrop {
  id: string;
  fieldId: string;
  cropId: string;
  crop?: Crop;
  plantingDate: string;
  expectedHarvestDate: string;
  actualHarvestDate?: string;
  currentStage: CropStage;
  stageStartDate: string;
  seedRate: number;                // kg/ha
  rowSpacing?: number;             // cm
  plantSpacing?: number;           // cm
  seedVariety?: string;
  seedSource?: string;
  notes?: string;
  notesAr?: string;
  yieldEstimate?: number;          // tons/ha
  actualYield?: number;            // tons/ha
  status: "growing" | "harvested" | "failed";
  createdAt: string;
  updatedAt: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Field Operations Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Operation type
 */
export type OperationType =
  | "irrigation"        // ري
  | "fertilization"     // تسميد
  | "spraying"          // رش
  | "tillage"           // حراثة
  | "planting"          // زراعة
  | "harvesting"        // حصاد
  | "scouting"          // استكشاف
  | "pruning"           // تقليم
  | "weeding"           // إزالة الأعشاب
  | "mulching"          // تغطية
  | "soil_sampling"     // أخذ عينات التربة
  | "other";            // أخرى

/**
 * Operation status
 */
export type OperationStatus =
  | "planned"           // مخطط
  | "in_progress"       // قيد التنفيذ
  | "completed"         // مكتمل
  | "cancelled"         // ملغي
  | "failed";           // فشل

/**
 * Field operation record
 */
export interface FieldOperation {
  id: string;
  fieldId: string;
  operationType: OperationType;
  status: OperationStatus;
  plannedDate: string;
  actualDate?: string;
  completedDate?: string;
  description?: string;
  descriptionAr?: string;
  operatorId?: string;
  operatorName?: string;
  equipmentUsed?: string[];
  inputs?: Array<{
    type: string;
    name: string;
    quantity: number;
    unit: string;
    cost?: number;
  }>;
  outputQuantity?: number;
  outputUnit?: string;
  areaCoveredHectares?: number;
  durationMinutes?: number;
  cost?: number;
  notes?: string;
  notesAr?: string;
  weatherConditions?: {
    temperature?: number;
    humidity?: number;
    windSpeed?: number;
    rainfall?: number;
  };
  attachments?: Array<{
    id: string;
    type: "image" | "document" | "video";
    url: string;
    name: string;
  }>;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Field Health & NDVI Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Health score category
 */
export type HealthCategory =
  | "excellent"     // ممتاز (80-100)
  | "good"          // جيد (60-79)
  | "moderate"      // متوسط (40-59)
  | "poor"          // ضعيف (20-39)
  | "critical";     // حرج (0-19)

/**
 * Field health snapshot
 */
export interface FieldHealth {
  fieldId: string;
  observationDate: string;
  ndvi: number;
  ndviCategory: HealthCategory;
  lai?: number;
  chlorophyllIndex?: number;
  waterStressIndex?: number;
  soilMoisturePercent?: number;
  healthScore: number;
  healthCategory: HealthCategory;
  anomalies?: Array<{
    type: string;
    location: GeoJSONPoint;
    severity: "low" | "medium" | "high";
    description: string;
    descriptionAr: string;
  }>;
  recommendations?: string[];
  recommendationsAr?: string[];
  dataSource: string;
  cloudCoverPercent?: number;
}

/**
 * NDVI time series point
 */
export interface NDVITimePoint {
  date: string;
  ndvi: number;
  source: string;
  quality: "high" | "medium" | "low";
}

/**
 * NDVI summary for a field
 */
export interface NDVISummary {
  fieldId: string;
  currentNdvi: number;
  averageNdvi: number;
  minNdvi: number;
  maxNdvi: number;
  trend: "improving" | "stable" | "declining";
  trendPercentChange: number;
  lastObservation: string;
  observationCount: number;
  timeSeries: NDVITimePoint[];
}

// ═══════════════════════════════════════════════════════════════════════════
// API Response Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Field-specific paginated response with hasMore indicator
 * Use this for field/farm list endpoints that need hasMore functionality
 */
export interface FieldPaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasMore: boolean;
  };
}

/**
 * Field list response
 */
export type FieldListResponse = FieldPaginatedResponse<Field>;

/**
 * Farm list response
 */
export type FarmListResponse = FieldPaginatedResponse<Farm>;

/**
 * Field with relations
 */
export interface FieldWithRelations extends Field {
  farm?: Farm;
  currentCrop?: FieldCrop;
  latestHealth?: FieldHealth;
  recentOperations?: FieldOperation[];
}

/**
 * Farm with fields
 */
export interface FarmWithFields extends Farm {
  fields: Field[];
  fieldCount: number;
  totalActiveArea: number;
}
