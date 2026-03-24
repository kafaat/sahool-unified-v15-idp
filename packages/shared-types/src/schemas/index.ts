/**
 * SAHOOL Zod Validation Schemas
 * مخططات التحقق باستخدام Zod
 *
 * Runtime validation schemas for core API contracts.
 * These schemas mirror the TypeScript interfaces defined in the
 * sibling modules (auth.ts, field.ts, contracts/api-responses.ts)
 * and provide runtime validation via Zod.
 *
 * IMPORTANT: `zod` is NOT yet installed in this package.
 * Before using these schemas, add zod as a dependency:
 *
 *   npm install zod          # in packages/shared-types
 *   # or add to package.json: "dependencies": { "zod": "^3.23.0" }
 *
 * @module @sahool/shared-types/schemas
 * @version 16.0.0
 */

import { z } from 'zod';

// ═══════════════════════════════════════════════════════════════════════════
// Auth / User Schemas - مخططات المصادقة والمستخدمين
// ═══════════════════════════════════════════════════════════════════════════

/**
 * User roles available in the platform.
 * Aligned with UserRole in auth.ts
 */
export const UserRoleSchema = z.enum([
  'admin',
  'super_admin',
  'manager',
  'operator',
  'expert',
  'farmer',
  'agronomist',
  'researcher',
  'field_officer',
  'viewer',
]);

/**
 * Login request payload.
 * Validates email format and minimum password length.
 */
export const LoginRequestSchema = z.object({
  email: z.string().email('Invalid email address | بريد إلكتروني غير صالح'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters | يجب أن تكون كلمة المرور 8 أحرف على الأقل'),
});

/**
 * Login response payload.
 * Aligned with LoginResponse in auth.ts and contracts/api-responses.ts
 */
export const LoginResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string().optional(),
  token_type: z.string().default('Bearer'),
  expires_in: z.number().positive().optional(),
  user: z.lazy(() => UserSchema),
  requires_2fa: z.boolean().optional(),
});

/**
 * User entity schema.
 * Aligned with User interface in auth.ts
 */
export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1).max(100),
  name_ar: z.string().optional(),
  role: z.string(),
  /** @deprecated Use tenantId instead */
  tenant_id: z.string().uuid().optional(),
  tenantId: z.string().uuid().optional(),
  permissions: z.array(z.string()).optional(),
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

/**
 * JWT payload schema.
 * Aligned with JWTPayload in auth.ts
 */
export const JWTPayloadSchema = z.object({
  sub: z.string(),
  id: z.string().optional(),
  email: z.string().email().optional(),
  role: z.string().optional(),
  tenantId: z.string().uuid().optional(),
  /** @deprecated Use tenantId instead */
  tenant_id: z.string().uuid().optional(),
  permissions: z.array(z.string()).optional(),
  iat: z.number().optional(),
  exp: z.number().optional(),
});

/**
 * Permission schema.
 * Aligned with Permission in auth.ts
 */
export const PermissionSchema = z.object({
  id: z.string(),
  name: z.string(),
  resource: z.string(),
  action: z.string(),
  scope: z.enum(['own', 'tenant', 'global']).optional(),
});

// ═══════════════════════════════════════════════════════════════════════════
// Geographic Schemas - المخططات الجغرافية
// ═══════════════════════════════════════════════════════════════════════════

/**
 * A single coordinate pair: [longitude, latitude].
 * Aligned with GeoJSON spec and field.ts GeoJSONPoint coordinates.
 */
export const CoordinateSchema = z.tuple([z.number(), z.number()]);

/**
 * GeoJSON Point geometry.
 * Aligned with GeoJSONPoint in field.ts
 */
export const GeoPointSchema = z.object({
  type: z.literal('Point'),
  coordinates: CoordinateSchema,
});

/**
 * GeoJSON Polygon geometry.
 * Aligned with GeoJSONPolygon in field.ts
 */
export const GeoPolygonSchema = z.object({
  type: z.literal('Polygon'),
  coordinates: z.array(z.array(CoordinateSchema)),
});

/**
 * GeoJSON MultiPolygon geometry.
 * Aligned with GeoJSONMultiPolygon in field.ts
 */
export const GeoMultiPolygonSchema = z.object({
  type: z.literal('MultiPolygon'),
  coordinates: z.array(z.array(z.array(CoordinateSchema))),
});

/**
 * Field geometry: either a Polygon or MultiPolygon.
 * Aligned with FieldGeometry in field.ts
 */
export const FieldGeometrySchema = z.discriminatedUnion('type', [
  GeoPolygonSchema,
  GeoMultiPolygonSchema,
]);

// ═══════════════════════════════════════════════════════════════════════════
// Field Schemas - مخططات الحقول
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Field status enum.
 * Aligned with FieldStatus in field.ts
 */
export const FieldStatusSchema = z.enum(['active', 'fallow', 'preparing', 'harvested', 'inactive']);

/**
 * Soil type classification.
 * Aligned with SoilType in field.ts
 */
export const SoilTypeSchema = z.enum([
  'clay',
  'sandy',
  'loamy',
  'silty',
  'peaty',
  'chalky',
  'mixed',
]);

/**
 * Irrigation type.
 * Aligned with IrrigationType in field.ts
 */
export const IrrigationTypeSchema = z.enum([
  'drip',
  'sprinkler',
  'flood',
  'pivot',
  'furrow',
  'rainfed',
  'subsurface',
]);

/**
 * Soil analysis data.
 * Aligned with SoilAnalysis in field.ts
 */
export const SoilAnalysisSchema = z.object({
  ph: z.number().min(0).max(14),
  organicMatter: z.number().nonnegative(),
  nitrogen: z.number().nonnegative(),
  phosphorus: z.number().nonnegative(),
  potassium: z.number().nonnegative(),
  calcium: z.number().nonnegative().optional(),
  magnesium: z.number().nonnegative().optional(),
  sulfur: z.number().nonnegative().optional(),
  electricalConductivity: z.number().nonnegative().optional(),
  cec: z.number().nonnegative().optional(),
  texture: z
    .object({
      sand: z.number().min(0).max(100),
      silt: z.number().min(0).max(100),
      clay: z.number().min(0).max(100),
    })
    .optional(),
  sampleDate: z.string(),
  labName: z.string().optional(),
});

/**
 * Field entity schema.
 * Aligned with Field interface in field.ts.
 * Source of truth: field-management-service Prisma schema.
 */
export const FieldSchema = z.object({
  id: z.string().uuid(),
  version: z.number().int().nonnegative(),
  farmId: z.string().uuid().optional(),
  name: z.string().min(1).max(100),
  nameAr: z.string().optional(),
  tenantId: z.string().uuid(),
  cropType: z.string().optional(),
  ownerId: z.string().uuid().optional(),
  status: FieldStatusSchema,
  areaHectares: z.number().positive().optional(),
  geometry: FieldGeometrySchema.optional(),
  centroid: GeoPointSchema.optional(),
  boundingBox: z
    .object({
      minLon: z.number(),
      minLat: z.number(),
      maxLon: z.number(),
      maxLat: z.number(),
    })
    .optional(),

  // Health & Analysis
  healthScore: z.number().min(0).max(1).optional(),
  ndviValue: z.number().min(-1).max(1).optional(),

  // Terrain
  elevation: z.number().optional(),
  slope: z.number().optional(),
  aspect: z.number().optional(),

  // Agricultural Info
  soilType: SoilTypeSchema.optional(),
  irrigationType: IrrigationTypeSchema.optional(),
  lastSoilAnalysis: SoilAnalysisSchema.optional(),
  currentCropId: z.string().uuid().optional(),
  plantingDate: z.string().optional(),
  expectedHarvestDate: z.string().optional(),
  tags: z.array(z.string()).optional(),

  // Sync Metadata
  isDeleted: z.boolean().optional(),
  serverUpdatedAt: z.string().datetime().optional(),
  etag: z.string().optional(),

  // Timestamps
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  metadata: z.record(z.string(), z.unknown()).optional(),
});

/**
 * Field creation payload.
 * Aligned with CreateFieldPayload in field.ts
 */
export const CreateFieldPayloadSchema = z.object({
  farmId: z.string().uuid(),
  name: z.string().min(1).max(100),
  nameAr: z.string().optional(),
  geometry: FieldGeometrySchema,
  areaHectares: z.number().positive().optional(),
  soilType: SoilTypeSchema.optional(),
  irrigationType: IrrigationTypeSchema.optional(),
  tags: z.array(z.string()).optional(),
});

/**
 * Field update payload.
 * Aligned with UpdateFieldPayload in field.ts
 */
export const UpdateFieldPayloadSchema = CreateFieldPayloadSchema.partial().extend({
  status: FieldStatusSchema.optional(),
  currentCropId: z.string().uuid().optional(),
  plantingDate: z.string().optional(),
  expectedHarvestDate: z.string().optional(),
});

/**
 * Field filters for list queries.
 * Aligned with FieldFilters in field.ts
 */
export const FieldFiltersSchema = z.object({
  farmId: z.string().uuid().optional(),
  status: z.union([FieldStatusSchema, z.array(FieldStatusSchema)]).optional(),
  soilType: z.union([SoilTypeSchema, z.array(SoilTypeSchema)]).optional(),
  irrigationType: z.union([IrrigationTypeSchema, z.array(IrrigationTypeSchema)]).optional(),
  cropId: z.string().optional(),
  tags: z.array(z.string()).optional(),
  minArea: z.number().nonnegative().optional(),
  maxArea: z.number().positive().optional(),
  search: z.string().optional(),
  page: z.number().int().positive().optional(),
  limit: z.number().int().positive().optional(),
  sortBy: z.enum(['name', 'areaHectares', 'createdAt', 'updatedAt']).optional(),
  sortOrder: z.enum(['asc', 'desc']).optional(),
});

// ═══════════════════════════════════════════════════════════════════════════
// API Response Wrapper Schemas - مخططات أغلفة استجابات الـ API
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Pagination metadata.
 * Aligned with PaginationMeta in contracts/api-responses.ts
 */
export const PaginationMetaSchema = z.object({
  total: z.number().int().nonnegative(),
  page: z.number().int().positive(),
  limit: z.number().int().positive(),
  totalPages: z.number().int().nonnegative().optional(),
  hasMore: z.boolean().optional(),
  offset: z.number().int().nonnegative().optional(),
});

/**
 * Generic API response wrapper factory.
 * Aligned with ApiResponse<T> in contracts/api-responses.ts
 *
 * @example
 * const UserResponseSchema = ApiResponseSchema(UserSchema);
 * const parsed = UserResponseSchema.parse(apiResponse);
 */
export const ApiResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    error: z.string().optional(),
    errorAr: z.string().optional(),
    errorCode: z.string().optional(),
    requestId: z.string().optional(),
    message: z.string().optional(),
    pagination: PaginationMetaSchema.optional(),
  });

/**
 * Generic paginated response wrapper factory.
 * Aligned with PaginatedResponse<T> in contracts/api-responses.ts
 *
 * @example
 * const FieldListResponseSchema = PaginatedResponseSchema(FieldSchema);
 * const parsed = FieldListResponseSchema.parse(apiResponse);
 */
export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    success: z.boolean(),
    data: z.array(itemSchema).optional(),
    error: z.string().optional(),
    errorAr: z.string().optional(),
    errorCode: z.string().optional(),
    requestId: z.string().optional(),
    message: z.string().optional(),
    pagination: PaginationMetaSchema,
  });

// ═══════════════════════════════════════════════════════════════════════════
// Advisory Schemas - مخططات الاستشارات
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Advisory type enum.
 */
export const AdvisoryTypeSchema = z.enum([
  'irrigation',
  'fertilizer',
  'pest',
  'disease',
  'general',
]);

/**
 * Advisory priority enum.
 * Maps to the alert priority encoding in the platform:
 *   critical  -> [!!!] immediate action (<6h)
 *   warning   -> [!!]  action within 24-48h
 *   advisory  -> [!]   action within 1 week
 *   informational -> [.]  for awareness
 */
export const AdvisoryPrioritySchema = z.enum(['critical', 'warning', 'advisory', 'informational']);

/**
 * Advisory entity schema.
 * Bilingual (Arabic/English) advisory content.
 */
export const AdvisorySchema = z.object({
  id: z.string().uuid(),
  type: AdvisoryTypeSchema,
  title: z.string().min(1),
  title_ar: z.string().optional(),
  description: z.string().min(1),
  description_ar: z.string().optional(),
  priority: AdvisoryPrioritySchema,
  field_id: z.string().uuid().optional(),
  crop_type: z.string().optional(),
  recommendations: z.array(z.string()).optional(),
  recommendations_ar: z.array(z.string()).optional(),
  created_at: z.string().datetime().optional(),
  expires_at: z.string().datetime().optional(),
});

// ═══════════════════════════════════════════════════════════════════════════
// Common Enum Schemas - مخططات التعدادات المشتركة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Locale enum. Aligned with Locale in contracts/api-responses.ts
 */
export const LocaleSchema = z.enum(['ar', 'en']);

/**
 * Severity enum. Aligned with Severity in contracts/api-responses.ts
 */
export const SeveritySchema = z.enum(['low', 'medium', 'high', 'critical']);

/**
 * Priority enum. Aligned with Priority in contracts/api-responses.ts
 */
export const PrioritySchema = z.enum(['urgent', 'high', 'medium', 'low']);

/**
 * Health status enum. Aligned with HealthStatus in contracts/api-responses.ts
 */
export const HealthStatusSchema = z.enum(['healthy', 'moderate', 'stressed', 'critical']);

/**
 * Trend direction enum. Aligned with TrendDirection in contracts/api-responses.ts
 */
export const TrendDirectionSchema = z.enum(['up', 'down', 'stable']);

// ═══════════════════════════════════════════════════════════════════════════
// Crop Schemas - مخططات المحاصيل
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Crop growth stage enum.
 * Aligned with CropStage in field.ts
 */
export const CropStageSchema = z.enum([
  'germination',
  'seedling',
  'vegetative',
  'tillering',
  'stem_elongation',
  'booting',
  'heading',
  'flowering',
  'pollination',
  'grain_fill',
  'ripening',
  'maturity',
  'harvest',
]);

/**
 * Crop category enum.
 * Aligned with CropCategory in field.ts
 */
export const CropCategorySchema = z.enum([
  'cereals',
  'legumes',
  'vegetables',
  'fruits',
  'oilseeds',
  'fiber',
  'fodder',
  'cash_crops',
  'spices',
]);

// ═══════════════════════════════════════════════════════════════════════════
// Operation Schemas - مخططات العمليات
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Operation type enum.
 * Aligned with OperationType in field.ts
 */
export const OperationTypeSchema = z.enum([
  'irrigation',
  'fertilization',
  'spraying',
  'tillage',
  'planting',
  'harvesting',
  'scouting',
  'pruning',
  'weeding',
  'mulching',
  'soil_sampling',
  'other',
]);

/**
 * Operation status enum.
 * Aligned with OperationStatus in field.ts
 */
export const OperationStatusSchema = z.enum([
  'planned',
  'in_progress',
  'completed',
  'cancelled',
  'failed',
]);

// ═══════════════════════════════════════════════════════════════════════════
// Inferred Types - الأنواع المستنتجة
// ═══════════════════════════════════════════════════════════════════════════

/** Inferred type from LoginRequestSchema */
export type LoginRequest = z.infer<typeof LoginRequestSchema>;

/** Inferred type from LoginResponseSchema */
export type LoginResponse = z.infer<typeof LoginResponseSchema>;

/** Inferred type from UserSchema */
export type UserValidated = z.infer<typeof UserSchema>;

/** Inferred type from JWTPayloadSchema */
export type JWTPayloadValidated = z.infer<typeof JWTPayloadSchema>;

/** Inferred type from PermissionSchema */
export type PermissionValidated = z.infer<typeof PermissionSchema>;

/** Inferred type from FieldSchema */
export type FieldValidated = z.infer<typeof FieldSchema>;

/** Inferred type from CreateFieldPayloadSchema */
export type CreateFieldPayload = z.infer<typeof CreateFieldPayloadSchema>;

/** Inferred type from UpdateFieldPayloadSchema */
export type UpdateFieldPayload = z.infer<typeof UpdateFieldPayloadSchema>;

/** Inferred type from FieldFiltersSchema */
export type FieldFiltersValidated = z.infer<typeof FieldFiltersSchema>;

/** Inferred type from AdvisorySchema */
export type AdvisoryValidated = z.infer<typeof AdvisorySchema>;

/** Inferred type from PaginationMetaSchema */
export type PaginationMetaValidated = z.infer<typeof PaginationMetaSchema>;

/** Inferred type from SoilAnalysisSchema */
export type SoilAnalysisValidated = z.infer<typeof SoilAnalysisSchema>;

/** Inferred type from CoordinateSchema */
export type Coordinate = z.infer<typeof CoordinateSchema>;

/** Inferred type from UserRoleSchema */
export type UserRole = z.infer<typeof UserRoleSchema>;
