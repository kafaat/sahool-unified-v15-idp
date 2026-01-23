/**
 * SAHOOL Event Schemas - Zod Validation
 * مخططات أحداث سهول - التحقق من صحة البيانات
 *
 * Comprehensive Zod schemas for runtime validation of event payloads.
 * Ensures type safety and data integrity across services.
 *
 * @packageDocumentation
 */

import { z } from "zod";

// ============================================================================
// Common Schemas - المخططات المشتركة
// ============================================================================

/**
 * UUID schema with validation
 * مخطط UUID مع التحقق
 */
export const UUIDSchema = z.string().uuid();

/**
 * ISO date string schema
 * مخطط تاريخ ISO
 */
export const ISODateSchema = z.string().datetime().or(z.date());

/**
 * GeoJSON Polygon schema for field boundaries
 * مخطط مضلع GeoJSON لحدود الحقول
 */
export const GeoJSONPolygonSchema = z.object({
  type: z.literal("Polygon"),
  coordinates: z.array(z.array(z.tuple([z.number(), z.number()]))),
});

/**
 * Event metadata schema
 * مخطط البيانات الوصفية للحدث
 */
export const EventMetadataSchema = z.object({
  correlationId: z.string().optional(),
  causationId: z.string().optional(),
  userId: z.string().optional(),
  traceId: z.string().optional(),
  spanId: z.string().optional(),
  source: z.string().optional(),
});

export type EventMetadata = z.infer<typeof EventMetadataSchema>;

/**
 * Base event schema - all events extend this
 * مخطط الحدث الأساسي
 */
export const BaseEventSchema = z.object({
  eventId: z.string().uuid(),
  eventType: z.string(),
  timestamp: ISODateSchema,
  version: z.string().default("1.0"),
  metadata: EventMetadataSchema.optional(),
});

export type BaseEvent = z.infer<typeof BaseEventSchema>;

// ============================================================================
// Common Field Types - أنواع الحقول المشتركة
// ============================================================================

/** Severity levels | مستويات الخطورة */
export const SeveritySchema = z.enum(["low", "medium", "high", "critical"]);
export type Severity = z.infer<typeof SeveritySchema>;

/** Priority levels | مستويات الأولوية */
export const PrioritySchema = z.enum(["low", "medium", "high", "urgent"]);
export type Priority = z.infer<typeof PrioritySchema>;

/** Notification channels | قنوات الإشعارات */
export const NotificationChannelSchema = z.enum(["email", "sms", "push", "in_app", "whatsapp"]);
export type NotificationChannel = z.infer<typeof NotificationChannelSchema>;

/** Currency codes | رموز العملات */
export const CurrencySchema = z.enum(["SAR", "YER", "USD", "EUR", "AED"]);
export type Currency = z.infer<typeof CurrencySchema>;

// ============================================================================
// Field Event Schemas - مخططات أحداث الحقول
// ============================================================================

/**
 * Field created event payload
 * حمولة حدث إنشاء الحقل
 */
export const FieldCreatedPayloadSchema = z.object({
  fieldId: UUIDSchema,
  farmId: UUIDSchema,
  tenantId: UUIDSchema,
  userId: UUIDSchema.optional(),
  name: z.string().min(1).max(120),
  nameAr: z.string().max(120).optional(),
  area: z.number().positive(),
  areaUnit: z.enum(["hectares", "acres", "square_meters"]).default("hectares"),
  location: GeoJSONPolygonSchema,
  geometryWkt: z.string().min(10).optional(),
  cropType: z.string().optional(),
  soilType: z.string().optional(),
  irrigationType: z.string().optional(),
  createdAt: ISODateSchema.optional(),
});

export type FieldCreatedPayload = z.infer<typeof FieldCreatedPayloadSchema>;

/**
 * Field updated event payload
 * حمولة حدث تحديث الحقل
 */
export const FieldUpdatedPayloadSchema = z.object({
  fieldId: UUIDSchema,
  tenantId: UUIDSchema.optional(),
  userId: UUIDSchema.optional(),
  changes: z.object({
    name: z.string().min(1).max(120).optional(),
    nameAr: z.string().max(120).optional(),
    area: z.number().positive().optional(),
    location: GeoJSONPolygonSchema.optional(),
    cropType: z.string().optional(),
    soilType: z.string().optional(),
    irrigationType: z.string().optional(),
    ndviValue: z.number().min(-1).max(1).optional(),
  }),
  updatedAt: ISODateSchema.optional(),
});

export type FieldUpdatedPayload = z.infer<typeof FieldUpdatedPayloadSchema>;

/**
 * Field deleted event payload
 * حمولة حدث حذف الحقل
 */
export const FieldDeletedPayloadSchema = z.object({
  fieldId: UUIDSchema,
  farmId: UUIDSchema.optional(),
  tenantId: UUIDSchema.optional(),
  userId: UUIDSchema.optional(),
  deletedAt: ISODateSchema,
  reason: z.string().optional(),
});

export type FieldDeletedPayload = z.infer<typeof FieldDeletedPayloadSchema>;

// ============================================================================
// Farm Event Schemas - مخططات أحداث المزارع
// ============================================================================

/**
 * Farm created event payload
 * حمولة حدث إنشاء المزرعة
 */
export const FarmCreatedPayloadSchema = z.object({
  farmId: UUIDSchema,
  tenantId: UUIDSchema,
  ownerId: UUIDSchema.optional(),
  name: z.string().min(1).max(120),
  nameAr: z.string().max(120).optional(),
  locationLat: z.number().min(-90).max(90),
  locationLon: z.number().min(-180).max(180),
  totalAreaHectares: z.number().positive().optional(),
  createdAt: ISODateSchema.optional(),
});

export type FarmCreatedPayload = z.infer<typeof FarmCreatedPayloadSchema>;

// ============================================================================
// Weather Event Schemas - مخططات أحداث الطقس
// ============================================================================

/** Weather alert types | أنواع تنبيهات الطقس */
export const WeatherAlertTypeSchema = z.enum([
  "frost",
  "heatwave",
  "storm",
  "heavy_rain",
  "drought",
  "wind",
]);
export type WeatherAlertType = z.infer<typeof WeatherAlertTypeSchema>;

/**
 * Weather forecast event payload
 * حمولة حدث توقعات الطقس
 */
export const WeatherForecastPayloadSchema = z.object({
  fieldId: UUIDSchema.optional(),
  tenantId: UUIDSchema.optional(),
  locationLat: z.number().min(-90).max(90),
  locationLon: z.number().min(-180).max(180),
  forecastDate: ISODateSchema,
  temperature: z.number().optional(),
  temperatureMin: z.number().optional(),
  temperatureMax: z.number().optional(),
  humidity: z.number().min(0).max(100).optional(),
  windSpeed: z.number().min(0).optional(),
  windDirection: z.number().min(0).max(360).optional(),
  precipitation: z.number().min(0).optional(),
  conditions: z.string().optional(),
  conditionsAr: z.string().optional(),
  provider: z.string().optional(),
});

export type WeatherForecastPayload = z.infer<typeof WeatherForecastPayloadSchema>;

/**
 * Weather alert event payload
 * حمولة حدث تنبيه الطقس
 */
export const WeatherAlertPayloadSchema = z.object({
  alertId: UUIDSchema,
  tenantId: UUIDSchema,
  fieldIds: z.array(UUIDSchema).default([]),
  alertType: WeatherAlertTypeSchema,
  severity: SeveritySchema,
  title: z.string(),
  titleAr: z.string().optional(),
  message: z.string(),
  messageAr: z.string().optional(),
  startTime: ISODateSchema,
  endTime: ISODateSchema.optional(),
  affectedAreaRadiusKm: z.number().min(0).optional(),
});

export type WeatherAlertPayload = z.infer<typeof WeatherAlertPayloadSchema>;

// ============================================================================
// Satellite Event Schemas - مخططات أحداث الأقمار الصناعية
// ============================================================================

/** Satellite anomaly types | أنواع شذوذات الأقمار الصناعية */
export const SatelliteAnomalyTypeSchema = z.enum([
  "ndvi_drop",
  "vegetation_loss",
  "water_stress",
  "disease_pattern",
  "growth_delay",
]);
export type SatelliteAnomalyType = z.infer<typeof SatelliteAnomalyTypeSchema>;

/**
 * Satellite data ready event payload
 * حمولة حدث جاهزية بيانات الأقمار الصناعية
 */
export const SatelliteDataReadyPayloadSchema = z.object({
  fieldId: UUIDSchema,
  tenantId: UUIDSchema,
  satelliteSource: z.string(),
  captureDate: ISODateSchema,
  processingDate: ISODateSchema.optional(),
  cloudCoverage: z.number().min(0).max(100).optional(),
  ndviMean: z.number().min(-1).max(1).optional(),
  ndviMin: z.number().min(-1).max(1).optional(),
  ndviMax: z.number().min(-1).max(1).optional(),
  eviMean: z.number().optional(),
  ndwiMean: z.number().min(-1).max(1).optional(),
  imageUrl: z.string().url().optional(),
  thumbnailUrl: z.string().url().optional(),
  dataUrl: z.string().url().optional(),
  resolutionMeters: z.number().min(0).optional(),
  bands: z.array(z.string()).default([]),
});

export type SatelliteDataReadyPayload = z.infer<typeof SatelliteDataReadyPayloadSchema>;

/**
 * Satellite anomaly event payload
 * حمولة حدث شذوذ الأقمار الصناعية
 */
export const SatelliteAnomalyPayloadSchema = z.object({
  anomalyId: UUIDSchema,
  fieldId: UUIDSchema,
  tenantId: UUIDSchema,
  anomalyType: SatelliteAnomalyTypeSchema,
  severity: SeveritySchema,
  confidenceScore: z.number().min(0).max(1),
  affectedAreaHectares: z.number().min(0).optional(),
  affectedAreaPercentage: z.number().min(0).max(100).optional(),
  detectionDate: ISODateSchema.optional(),
  currentValue: z.number().optional(),
  baselineValue: z.number().optional(),
  deviation: z.number().optional(),
  centroidLat: z.number().min(-90).max(90).optional(),
  centroidLon: z.number().min(-180).max(180).optional(),
  geometryWkt: z.string().optional(),
  recommendedAction: z.string().optional(),
  recommendedActionAr: z.string().optional(),
});

export type SatelliteAnomalyPayload = z.infer<typeof SatelliteAnomalyPayloadSchema>;

// ============================================================================
// Health Event Schemas - مخططات أحداث الصحة
// ============================================================================

/** Stress types | أنواع الإجهاد */
export const StressTypeSchema = z.enum([
  "water",
  "nutrient",
  "heat",
  "cold",
  "salinity",
  "compaction",
]);
export type StressType = z.infer<typeof StressTypeSchema>;

/**
 * Disease detected event payload
 * حمولة حدث اكتشاف المرض
 */
export const DiseaseDetectedPayloadSchema = z.object({
  detectionId: UUIDSchema,
  fieldId: UUIDSchema,
  tenantId: UUIDSchema,
  cropType: z.string().optional(),
  diseaseName: z.string(),
  diseaseNameAr: z.string().optional(),
  diseaseCategory: z.enum(["fungal", "bacterial", "viral", "pest"]).optional(),
  confidenceScore: z.number().min(0).max(1),
  severity: SeveritySchema,
  detectionMethod: z.enum(["ai", "manual", "sensor"]).optional(),
  affectedAreaHectares: z.number().min(0).optional(),
  symptomsObserved: z.array(z.string()).default([]),
  imageUrls: z.array(z.string().url()).default([]),
  treatmentRecommendation: z.string().optional(),
  treatmentRecommendationAr: z.string().optional(),
  urgencyLevel: z.string().optional(),
  estimatedYieldImpact: z.number().min(0).max(100).optional(),
});

export type DiseaseDetectedPayload = z.infer<typeof DiseaseDetectedPayloadSchema>;

/**
 * Crop stress event payload
 * حمولة حدث إجهاد المحصول
 */
export const CropStressPayloadSchema = z.object({
  stressId: UUIDSchema,
  fieldId: UUIDSchema,
  tenantId: UUIDSchema,
  stressType: StressTypeSchema,
  severity: SeveritySchema,
  confidenceScore: z.number().min(0).max(1),
  ndviValue: z.number().min(-1).max(1).optional(),
  ndwiValue: z.number().min(-1).max(1).optional(),
  temperatureValue: z.number().optional(),
  soilMoistureValue: z.number().min(0).max(100).optional(),
  affectedAreaHectares: z.number().min(0).optional(),
  detectionDate: ISODateSchema.optional(),
  actionRequired: z.string().optional(),
  actionRequiredAr: z.string().optional(),
  timeSensitivity: z.enum(["immediate", "soon", "monitor"]).optional(),
});

export type CropStressPayload = z.infer<typeof CropStressPayloadSchema>;

// ============================================================================
// Inventory Event Schemas - مخططات أحداث المخزون
// ============================================================================

/** Movement types | أنواع الحركة */
export const MovementTypeSchema = z.enum(["in", "out", "transfer", "adjustment"]);
export type MovementType = z.infer<typeof MovementTypeSchema>;

/**
 * Low stock event payload
 * حمولة حدث انخفاض المخزون
 */
export const LowStockPayloadSchema = z.object({
  alertId: UUIDSchema.optional(),
  tenantId: UUIDSchema,
  warehouseId: UUIDSchema.optional(),
  productId: UUIDSchema,
  productName: z.string(),
  productNameAr: z.string().optional(),
  productCategory: z.string().optional(),
  sku: z.string().optional(),
  currentQuantity: z.number().min(0),
  unitOfMeasure: z.string(),
  thresholdQuantity: z.number().min(0),
  reorderQuantity: z.number().min(0).optional(),
  severity: SeveritySchema,
  preferredSupplierId: UUIDSchema.optional(),
  estimatedRestockDays: z.number().int().min(0).optional(),
  estimatedCost: z.number().min(0).optional(),
  currency: CurrencySchema.default("SAR"),
});

export type LowStockPayload = z.infer<typeof LowStockPayloadSchema>;

/**
 * Inventory movement event payload
 * حمولة حدث حركة المخزون
 */
export const InventoryMovementPayloadSchema = z.object({
  movementId: UUIDSchema,
  tenantId: UUIDSchema.optional(),
  productId: UUIDSchema,
  quantity: z.number(),
  movementType: MovementTypeSchema,
  fromWarehouseId: UUIDSchema.optional(),
  toWarehouseId: UUIDSchema.optional(),
  reason: z.string().optional(),
  movedAt: ISODateSchema,
  movedBy: UUIDSchema.optional(),
});

export type InventoryMovementPayload = z.infer<typeof InventoryMovementPayloadSchema>;

/**
 * Batch expired event payload
 * حمولة حدث انتهاء صلاحية الدفعة
 */
export const BatchExpiredPayloadSchema = z.object({
  alertId: UUIDSchema.optional(),
  tenantId: UUIDSchema,
  warehouseId: UUIDSchema.optional(),
  batchId: UUIDSchema,
  batchNumber: z.string(),
  productId: UUIDSchema,
  productName: z.string(),
  productNameAr: z.string().optional(),
  expiryDate: ISODateSchema,
  quantity: z.number().min(0),
  unitOfMeasure: z.string(),
  status: z.enum(["expiring_soon", "expired", "critical"]),
  daysUntilExpiry: z.number().int(),
  valueAtRisk: z.number().min(0).optional(),
  currency: CurrencySchema.default("SAR"),
  recommendedAction: z.string().optional(),
  recommendedActionAr: z.string().optional(),
});

export type BatchExpiredPayload = z.infer<typeof BatchExpiredPayloadSchema>;

// ============================================================================
// Billing Event Schemas - مخططات أحداث الفوترة
// ============================================================================

/** Plan tiers | مستويات الخطط */
export const PlanTierSchema = z.enum(["free", "basic", "professional", "enterprise"]);
export type PlanTier = z.infer<typeof PlanTierSchema>;

/** Billing cycles | دورات الفوترة */
export const BillingCycleSchema = z.enum(["monthly", "quarterly", "annual"]);
export type BillingCycle = z.infer<typeof BillingCycleSchema>;

/** Payment methods | طرق الدفع */
export const PaymentMethodSchema = z.enum([
  "credit_card",
  "debit_card",
  "bank_transfer",
  "wallet",
  "apple_pay",
  "stc_pay",
  "mada",
]);
export type PaymentMethod = z.infer<typeof PaymentMethodSchema>;

/**
 * Subscription created event payload
 * حمولة حدث إنشاء الاشتراك
 */
export const SubscriptionCreatedPayloadSchema = z.object({
  subscriptionId: UUIDSchema,
  tenantId: UUIDSchema,
  userId: UUIDSchema,
  planId: z.string(),
  planName: z.string(),
  planTier: PlanTierSchema,
  billingCycle: BillingCycleSchema,
  startDate: ISODateSchema,
  endDate: ISODateSchema.optional(),
  trialEndDate: ISODateSchema.optional(),
  priceAmount: z.number().min(0),
  currency: CurrencySchema.default("SAR"),
  maxFields: z.number().int().min(0).optional(),
  maxAreaHectares: z.number().min(0).optional(),
  featuresEnabled: z.array(z.string()).default([]),
  autoRenew: z.boolean().default(true),
  paymentMethodId: z.string().optional(),
});

export type SubscriptionCreatedPayload = z.infer<typeof SubscriptionCreatedPayloadSchema>;

/**
 * Payment completed event payload
 * حمولة حدث اكتمال الدفع
 */
export const PaymentCompletedPayloadSchema = z.object({
  paymentId: UUIDSchema,
  subscriptionId: UUIDSchema.optional(),
  invoiceId: UUIDSchema.optional(),
  tenantId: UUIDSchema,
  amount: z.number().min(0),
  currency: CurrencySchema.default("SAR"),
  paymentMethod: PaymentMethodSchema,
  paymentProvider: z.string().optional(),
  transactionId: z.string(),
  paymentDate: ISODateSchema.optional(),
  description: z.string().optional(),
  descriptionAr: z.string().optional(),
  subtotal: z.number().min(0).optional(),
  taxAmount: z.number().min(0).optional(),
  taxPercentage: z.number().min(0).max(100).optional(),
  receiptUrl: z.string().url().optional(),
  invoiceUrl: z.string().url().optional(),
});

export type PaymentCompletedPayload = z.infer<typeof PaymentCompletedPayloadSchema>;

/**
 * Payment failed event payload
 * حمولة حدث فشل الدفع
 */
export const PaymentFailedPayloadSchema = z.object({
  paymentId: UUIDSchema,
  subscriptionId: UUIDSchema.optional(),
  tenantId: UUIDSchema,
  amount: z.number().min(0),
  currency: CurrencySchema.default("SAR"),
  failureReason: z.string(),
  failureMessage: z.string().optional(),
  failureMessageAr: z.string().optional(),
  paymentMethod: PaymentMethodSchema.optional(),
  retryCount: z.number().int().min(0).default(0),
  nextRetryDate: ISODateSchema.optional(),
});

export type PaymentFailedPayload = z.infer<typeof PaymentFailedPayloadSchema>;

// ============================================================================
// Task Event Schemas - مخططات أحداث المهام
// ============================================================================

/**
 * Task created event payload
 * حمولة حدث إنشاء المهمة
 */
export const TaskCreatedPayloadSchema = z.object({
  taskId: UUIDSchema,
  fieldId: UUIDSchema.optional(),
  tenantId: UUIDSchema,
  title: z.string().min(1).max(200),
  titleAr: z.string().max(200).optional(),
  description: z.string().optional(),
  descriptionAr: z.string().optional(),
  priority: PrioritySchema,
  dueDate: ISODateSchema.optional(),
  assignedTo: UUIDSchema.optional(),
  createdBy: UUIDSchema.optional(),
  createdAt: ISODateSchema.optional(),
});

export type TaskCreatedPayload = z.infer<typeof TaskCreatedPayloadSchema>;

/**
 * Task completed event payload
 * حمولة حدث اكتمال المهمة
 */
export const TaskCompletedPayloadSchema = z.object({
  taskId: UUIDSchema,
  tenantId: UUIDSchema.optional(),
  completedBy: UUIDSchema,
  completedAt: ISODateSchema,
  evidenceNotes: z.string().optional(),
  evidenceNotesAr: z.string().optional(),
});

export type TaskCompletedPayload = z.infer<typeof TaskCompletedPayloadSchema>;

// ============================================================================
// Alert Event Schemas - مخططات أحداث التنبيهات
// ============================================================================

/** Alert types | أنواع التنبيهات */
export const AlertTypeSchema = z.enum([
  "weather",
  "pest",
  "disease",
  "irrigation",
  "system",
  "inventory",
]);
export type AlertType = z.infer<typeof AlertTypeSchema>;

/**
 * Alert created event payload
 * حمولة حدث إنشاء التنبيه
 */
export const AlertCreatedPayloadSchema = z.object({
  alertId: UUIDSchema,
  tenantId: UUIDSchema,
  fieldId: UUIDSchema.optional(),
  alertType: AlertTypeSchema,
  severity: SeveritySchema,
  title: z.string(),
  titleAr: z.string().optional(),
  message: z.string(),
  messageAr: z.string().optional(),
  createdAt: ISODateSchema.optional(),
  expiresAt: ISODateSchema.optional(),
  actionUrl: z.string().url().optional(),
});

export type AlertCreatedPayload = z.infer<typeof AlertCreatedPayloadSchema>;

// ============================================================================
// IoT Event Schemas - مخططات أحداث إنترنت الأشياء
// ============================================================================

/** Sensor types | أنواع المستشعرات */
export const SensorTypeSchema = z.enum([
  "temperature",
  "humidity",
  "soil_moisture",
  "ph",
  "light",
  "ec",
  "nitrogen",
  "phosphorus",
  "potassium",
  "wind_speed",
  "rainfall",
  "other",
]);
export type SensorType = z.infer<typeof SensorTypeSchema>;

/** Disconnect reasons | أسباب الانقطاع */
export const DisconnectReasonSchema = z.enum([
  "timeout",
  "user_action",
  "error",
  "maintenance",
  "other",
]);
export type DisconnectReason = z.infer<typeof DisconnectReasonSchema>;

/**
 * Sensor reading event payload
 * حمولة حدث قراءة المستشعر
 */
export const SensorReadingPayloadSchema = z.object({
  deviceId: z.string(),
  fieldId: UUIDSchema.optional(),
  tenantId: UUIDSchema.optional(),
  sensorType: SensorTypeSchema,
  value: z.number(),
  unit: z.string(),
  latitude: z.number().min(-90).max(90).optional(),
  longitude: z.number().min(-180).max(180).optional(),
  readingTime: ISODateSchema,
  quality: z.number().min(0).max(100).optional(),
  batteryLevel: z.number().min(0).max(100).optional(),
});

export type SensorReadingPayload = z.infer<typeof SensorReadingPayloadSchema>;

/**
 * Device connected event payload
 * حمولة حدث اتصال الجهاز
 */
export const DeviceConnectedPayloadSchema = z.object({
  deviceId: z.string(),
  deviceType: z.string(),
  fieldId: UUIDSchema.optional(),
  tenantId: UUIDSchema.optional(),
  connectedAt: ISODateSchema,
  ipAddress: z.string().ip().optional(),
  firmwareVersion: z.string().optional(),
});

export type DeviceConnectedPayload = z.infer<typeof DeviceConnectedPayloadSchema>;

/**
 * Device disconnected event payload
 * حمولة حدث انقطاع الجهاز
 */
export const DeviceDisconnectedPayloadSchema = z.object({
  deviceId: z.string(),
  deviceType: z.string(),
  fieldId: UUIDSchema.optional(),
  tenantId: UUIDSchema.optional(),
  disconnectedAt: ISODateSchema,
  reason: DisconnectReasonSchema.optional(),
  lastKnownStatus: z.string().optional(),
});

export type DeviceDisconnectedPayload = z.infer<typeof DeviceDisconnectedPayloadSchema>;

// ============================================================================
// Notification Event Schemas - مخططات أحداث الإشعارات
// ============================================================================

/** Recipient types | أنواع المستلمين */
export const RecipientTypeSchema = z.enum(["user", "group", "all"]);
export type RecipientType = z.infer<typeof RecipientTypeSchema>;

/**
 * Notification send event payload
 * حمولة حدث إرسال الإشعار
 */
export const NotificationSendPayloadSchema = z.object({
  notificationId: UUIDSchema,
  tenantId: UUIDSchema.optional(),
  recipientId: z.string(),
  recipientType: RecipientTypeSchema,
  channel: NotificationChannelSchema,
  priority: PrioritySchema,
  subject: z.string(),
  subjectAr: z.string().optional(),
  message: z.string(),
  messageAr: z.string().optional(),
  data: z.record(z.unknown()).optional(),
  actionUrl: z.string().url().optional(),
  scheduledFor: ISODateSchema.optional(),
});

export type NotificationSendPayload = z.infer<typeof NotificationSendPayloadSchema>;

// ============================================================================
// User Event Schemas - مخططات أحداث المستخدمين
// ============================================================================

/**
 * User created event payload
 * حمولة حدث إنشاء المستخدم
 */
export const UserCreatedPayloadSchema = z.object({
  userId: UUIDSchema,
  tenantId: UUIDSchema.optional(),
  email: z.string().email(),
  username: z.string().optional(),
  firstName: z.string().optional(),
  firstNameAr: z.string().optional(),
  lastName: z.string().optional(),
  lastNameAr: z.string().optional(),
  role: z.string(),
  phone: z.string().optional(),
  createdAt: ISODateSchema.optional(),
});

export type UserCreatedPayload = z.infer<typeof UserCreatedPayloadSchema>;

/**
 * User updated event payload
 * حمولة حدث تحديث المستخدم
 */
export const UserUpdatedPayloadSchema = z.object({
  userId: UUIDSchema,
  tenantId: UUIDSchema.optional(),
  changes: z.object({
    email: z.string().email().optional(),
    username: z.string().optional(),
    firstName: z.string().optional(),
    lastName: z.string().optional(),
    role: z.string().optional(),
    phone: z.string().optional(),
  }),
  updatedAt: ISODateSchema.optional(),
});

export type UserUpdatedPayload = z.infer<typeof UserUpdatedPayloadSchema>;

// ============================================================================
// Order Event Schemas - مخططات أحداث الطلبات
// ============================================================================

/** Order item schema | مخطط عنصر الطلب */
export const OrderItemSchema = z.object({
  productId: UUIDSchema,
  quantity: z.number().int().positive(),
  price: z.number().min(0),
  productName: z.string().optional(),
});

/** Shipping address schema | مخطط عنوان الشحن */
export const ShippingAddressSchema = z.object({
  street: z.string(),
  city: z.string(),
  country: z.string(),
  postalCode: z.string(),
  region: z.string().optional(),
});

/**
 * Order placed event payload
 * حمولة حدث تقديم الطلب
 */
export const OrderPlacedPayloadSchema = z.object({
  orderId: UUIDSchema,
  tenantId: UUIDSchema.optional(),
  userId: UUIDSchema,
  items: z.array(OrderItemSchema).min(1),
  totalAmount: z.number().min(0),
  currency: CurrencySchema.default("SAR"),
  shippingAddress: ShippingAddressSchema.optional(),
  notes: z.string().optional(),
  placedAt: ISODateSchema.optional(),
});

export type OrderPlacedPayload = z.infer<typeof OrderPlacedPayloadSchema>;

/**
 * Order completed event payload
 * حمولة حدث اكتمال الطلب
 */
export const OrderCompletedPayloadSchema = z.object({
  orderId: UUIDSchema,
  tenantId: UUIDSchema.optional(),
  userId: UUIDSchema,
  completedAt: ISODateSchema,
  totalAmount: z.number().min(0),
  currency: CurrencySchema.default("SAR"),
});

export type OrderCompletedPayload = z.infer<typeof OrderCompletedPayloadSchema>;

/**
 * Order cancelled event payload
 * حمولة حدث إلغاء الطلب
 */
export const OrderCancelledPayloadSchema = z.object({
  orderId: UUIDSchema,
  tenantId: UUIDSchema.optional(),
  userId: UUIDSchema,
  cancelledAt: ISODateSchema,
  reason: z.string().optional(),
  refundAmount: z.number().min(0).optional(),
});

export type OrderCancelledPayload = z.infer<typeof OrderCancelledPayloadSchema>;

// ============================================================================
// Agent Event Schemas - مخططات أحداث الوكلاء
// ============================================================================

/** Agent types | أنواع الوكلاء */
export const AgentTypeSchema = z.enum([
  "farm_advisor",
  "research",
  "planner",
  "analyst",
  "assistant",
]);
export type AgentType = z.infer<typeof AgentTypeSchema>;

/** Execution modes | أوضاع التنفيذ */
export const ExecutionModeSchema = z.enum(["plan", "execute", "hybrid"]);
export type ExecutionMode = z.infer<typeof ExecutionModeSchema>;

/**
 * Agent execution started event payload
 * حمولة حدث بدء تنفيذ الوكيل
 */
export const AgentExecutionStartedPayloadSchema = z.object({
  executionId: z.string(),
  agentType: AgentTypeSchema,
  tenantId: z.string(),
  task: z.string(),
  taskAr: z.string().optional(),
  mode: ExecutionModeSchema.default("hybrid"),
  fieldId: UUIDSchema.optional(),
  farmId: UUIDSchema.optional(),
  startedAt: ISODateSchema.optional(),
});

export type AgentExecutionStartedPayload = z.infer<typeof AgentExecutionStartedPayloadSchema>;

/**
 * Agent execution completed event payload
 * حمولة حدث اكتمال تنفيذ الوكيل
 */
export const AgentExecutionCompletedPayloadSchema = z.object({
  executionId: z.string(),
  agentType: AgentTypeSchema,
  tenantId: z.string(),
  status: z.literal("completed").default("completed"),
  totalSteps: z.number().int().min(0).default(0),
  durationMs: z.number().int().min(0).default(0),
  resultSummary: z.string().optional(),
  resultSummaryAr: z.string().optional(),
  tokensUsed: z.number().int().min(0).optional(),
  completedAt: ISODateSchema.optional(),
});

export type AgentExecutionCompletedPayload = z.infer<typeof AgentExecutionCompletedPayloadSchema>;

/**
 * Agent execution failed event payload
 * حمولة حدث فشل تنفيذ الوكيل
 */
export const AgentExecutionFailedPayloadSchema = z.object({
  executionId: z.string(),
  agentType: AgentTypeSchema,
  tenantId: z.string(),
  errorType: z.string(),
  errorMessage: z.string(),
  errorMessageAr: z.string().optional(),
  failedAtStep: z.number().int().optional(),
  durationMs: z.number().int().min(0).default(0),
  failedAt: ISODateSchema.optional(),
});

export type AgentExecutionFailedPayload = z.infer<typeof AgentExecutionFailedPayloadSchema>;

// ============================================================================
// Recommendation Event Schemas - مخططات أحداث التوصيات
// ============================================================================

/** Recommendation types | أنواع التوصيات */
export const RecommendationTypeSchema = z.enum([
  "irrigation",
  "fertilizer",
  "pest_control",
  "harvest",
  "planting",
]);
export type RecommendationType = z.infer<typeof RecommendationTypeSchema>;

/**
 * Recommendation created event payload
 * حمولة حدث إنشاء التوصية
 */
export const RecommendationCreatedPayloadSchema = z.object({
  recommendationId: UUIDSchema,
  fieldId: UUIDSchema,
  tenantId: UUIDSchema,
  recommendationType: RecommendationTypeSchema,
  title: z.string(),
  titleAr: z.string().optional(),
  description: z.string(),
  descriptionAr: z.string().optional(),
  priority: PrioritySchema,
  confidenceScore: z.number().min(0).max(1),
  validFrom: ISODateSchema.optional(),
  validUntil: ISODateSchema.optional(),
  estimatedImpact: z.string().optional(),
  estimatedImpactAr: z.string().optional(),
  createdAt: ISODateSchema.optional(),
});

export type RecommendationCreatedPayload = z.infer<typeof RecommendationCreatedPayloadSchema>;

// ============================================================================
// Export All Schemas - تصدير جميع المخططات
// ============================================================================

export const EventSchemas = {
  // Common
  BaseEvent: BaseEventSchema,
  EventMetadata: EventMetadataSchema,

  // Field
  FieldCreated: FieldCreatedPayloadSchema,
  FieldUpdated: FieldUpdatedPayloadSchema,
  FieldDeleted: FieldDeletedPayloadSchema,

  // Farm
  FarmCreated: FarmCreatedPayloadSchema,

  // Weather
  WeatherForecast: WeatherForecastPayloadSchema,
  WeatherAlert: WeatherAlertPayloadSchema,

  // Satellite
  SatelliteDataReady: SatelliteDataReadyPayloadSchema,
  SatelliteAnomaly: SatelliteAnomalyPayloadSchema,

  // Health
  DiseaseDetected: DiseaseDetectedPayloadSchema,
  CropStress: CropStressPayloadSchema,

  // Inventory
  LowStock: LowStockPayloadSchema,
  InventoryMovement: InventoryMovementPayloadSchema,
  BatchExpired: BatchExpiredPayloadSchema,

  // Billing
  SubscriptionCreated: SubscriptionCreatedPayloadSchema,
  PaymentCompleted: PaymentCompletedPayloadSchema,
  PaymentFailed: PaymentFailedPayloadSchema,

  // Task
  TaskCreated: TaskCreatedPayloadSchema,
  TaskCompleted: TaskCompletedPayloadSchema,

  // Alert
  AlertCreated: AlertCreatedPayloadSchema,

  // IoT
  SensorReading: SensorReadingPayloadSchema,
  DeviceConnected: DeviceConnectedPayloadSchema,
  DeviceDisconnected: DeviceDisconnectedPayloadSchema,

  // Notification
  NotificationSend: NotificationSendPayloadSchema,

  // User
  UserCreated: UserCreatedPayloadSchema,
  UserUpdated: UserUpdatedPayloadSchema,

  // Order
  OrderPlaced: OrderPlacedPayloadSchema,
  OrderCompleted: OrderCompletedPayloadSchema,
  OrderCancelled: OrderCancelledPayloadSchema,

  // Agent
  AgentExecutionStarted: AgentExecutionStartedPayloadSchema,
  AgentExecutionCompleted: AgentExecutionCompletedPayloadSchema,
  AgentExecutionFailed: AgentExecutionFailedPayloadSchema,

  // Recommendation
  RecommendationCreated: RecommendationCreatedPayloadSchema,
} as const;

// ============================================================================
// Validation Utilities - أدوات التحقق
// ============================================================================

/**
 * Validate an event payload against its schema.
 * التحقق من صحة حمولة الحدث مقابل مخططها
 *
 * @param schemaName - Name of the schema to validate against
 * @param payload - Payload to validate
 * @returns Validated payload or throws ZodError
 */
export function validatePayload<T extends keyof typeof EventSchemas>(
  schemaName: T,
  payload: unknown
): z.infer<(typeof EventSchemas)[T]> {
  const schema = EventSchemas[schemaName];
  return schema.parse(payload);
}

/**
 * Safely validate an event payload (returns result object).
 * التحقق الآمن من حمولة الحدث
 *
 * @param schemaName - Name of the schema
 * @param payload - Payload to validate
 * @returns Success or error result
 */
export function safeValidatePayload<T extends keyof typeof EventSchemas>(
  schemaName: T,
  payload: unknown
): z.SafeParseReturnType<unknown, z.infer<(typeof EventSchemas)[T]>> {
  const schema = EventSchemas[schemaName];
  return schema.safeParse(payload);
}

/**
 * Create a validated payload with defaults.
 * إنشاء حمولة تم التحقق منها مع القيم الافتراضية
 *
 * @param schemaName - Name of the schema
 * @param payload - Partial payload
 * @returns Validated payload with defaults applied
 */
export function createPayload<T extends keyof typeof EventSchemas>(
  schemaName: T,
  payload: Partial<z.input<(typeof EventSchemas)[T]>>
): z.infer<(typeof EventSchemas)[T]> {
  const schema = EventSchemas[schemaName];
  return schema.parse(payload);
}
