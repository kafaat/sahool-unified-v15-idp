/**
 * SAHOOL Unified API Response Shapes
 * أشكال استجابات الـ API الموحدة
 *
 * Single source of truth for API response/request types.
 * Used by: Web, Admin, Mobile, api-client, backend services.
 *
 * @module @sahool/shared-types/contracts
 * @version 16.0.0
 */

// ---------------------------------------------------------------------------
// Core Response Wrapper - غلاف الاستجابة الأساسي
// ---------------------------------------------------------------------------

/** Standard API success/error response used by ALL services */
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  errorAr?: string;
  errorCode?: string;
  requestId?: string;
  message?: string;
  pagination?: PaginationMeta;
}

export interface PaginationMeta {
  total: number;
  page: number;
  limit: number;
  totalPages?: number;
  hasMore?: boolean;
  offset?: number;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: PaginationMeta;
}

// ---------------------------------------------------------------------------
// Common Enums - التعدادات المشتركة
// ---------------------------------------------------------------------------

export type Locale = 'ar' | 'en';
export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type Priority = 'urgent' | 'high' | 'medium' | 'low';
export type TrendDirection = 'up' | 'down' | 'stable';
export type HealthStatus = 'healthy' | 'moderate' | 'stressed' | 'critical';

export type FieldStatus = 'active' | 'inactive' | 'fallow' | 'preparing' | 'harvested' | 'deleted';
export type TaskStatus = 'open' | 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type AlertSeverity = 'info' | 'warning' | 'critical' | 'emergency';
export type AlertStatus = 'active' | 'unread' | 'read' | 'acknowledged' | 'resolved' | 'dismissed';
export type DeviceStatus = 'online' | 'offline' | 'warning' | 'error' | 'maintenance';
export type EquipmentStatus = 'available' | 'in_use' | 'maintenance' | 'broken' | 'retired';
export type SubscriptionPlan = 'free' | 'basic' | 'starter' | 'professional' | 'enterprise';
export type SyncStatus =
  | 'idle'
  | 'syncing'
  | 'conflict'
  | 'error'
  | 'pending'
  | 'synced'
  | 'failed';

// ---------------------------------------------------------------------------
// GeoJSON Types - أنواع الجغرافيا
// ---------------------------------------------------------------------------

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface GeoPoint {
  type: 'Point';
  coordinates: [number, number]; // [lng, lat]
}

export interface GeoPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface GeoMultiPolygon {
  type: 'MultiPolygon';
  coordinates: number[][][][];
}

// ---------------------------------------------------------------------------
// Auth Request / Response Shapes - أشكال طلبات واستجابات المصادقة
// ---------------------------------------------------------------------------

/**
 * OTP delivery channel — must match user-service SendOtpDto.
 * Backend: `apps/services/user-service/src/auth/auth.service.ts` SendOtpDto
 */
export const OTP_CHANNEL = {
  SMS: 'sms',
  WHATSAPP: 'whatsapp',
  TELEGRAM: 'telegram',
  EMAIL: 'email',
} as const;
export type OtpChannel = (typeof OTP_CHANNEL)[keyof typeof OTP_CHANNEL];

/**
 * OTP purpose — must match user-service SendOtpDto / VerifyOtpDto.
 * `login` was added 2026-04 to enable passwordless OTP login.
 */
export const OTP_PURPOSE = {
  PASSWORD_RESET: 'password_reset',
  VERIFY_PHONE: 'verify_phone',
  LOGIN: 'login',
} as const;
export type OtpPurpose = (typeof OTP_PURPOSE)[keyof typeof OTP_PURPOSE];

/**
 * send-otp request body — canonical shape accepted by backend user-service
 * at POST /api/v1/auth/send-otp. Proxy routes (web/admin) MUST forward
 * exactly these field names.
 */
export interface SendOtpRequest {
  identifier: string;
  channel: OtpChannel;
  purpose: OtpPurpose;
  language?: Locale;
  tenantId?: string;
}

export interface SendOtpResponse {
  success: boolean;
  message?: string;
  expiresIn?: number;
}

/**
 * verify-otp request body — canonical shape. Backend DTO uses `otpCode`
 * (NOT `otp`). Historical bug: web proxy accepted `otp` and forwarded it
 * unchanged, making verify-otp silently fail.
 */
export interface VerifyOtpRequest {
  identifier: string;
  otpCode: string;
  purpose: OtpPurpose;
  tenantId?: string;
}

export interface VerifyOtpResponse {
  success: boolean;
  message?: string;
  /** Present only when purpose = 'password_reset' */
  resetToken?: string;
  /** Present only when purpose = 'verify_phone' */
  verified?: boolean;
  /** Present only when purpose = 'login' — login tokens are issued */
  access_token?: string;
  refresh_token?: string;
  expires_in?: number;
  token_type?: string;
  user?: UserProfile;
}

/** POST /api/v1/auth/login request body */
export interface LoginRequest {
  email?: string;
  phone?: string;
  password: string;
  totp_code?: string;
  tenantId?: string;
}

/** POST /api/v1/auth/register request body */
export interface RegisterRequest {
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
  name?: string;
  phone?: string;
  tenantId?: string;
}

/** POST /api/v1/auth/logout request body */
export interface LogoutRequest {
  refresh_token?: string;
  session_id?: string;
  revoke_all_sessions?: boolean;
}

/** POST /api/v1/auth/refresh request body */
export interface RefreshTokenRequest {
  refresh_token: string;
}

// ---------------------------------------------------------------------------
// Auth Response Shapes - أشكال استجابات المصادقة
// ---------------------------------------------------------------------------

export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
  expires_in?: number;
  user: UserProfile;
  requires_2fa?: boolean;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  nameAr?: string;
  role: string;
  tenantId?: string;
  /** @deprecated Use `tenantId` instead */
  tenant_id?: string;
  permissions?: string[];
  phone?: string;
  language?: Locale;
  avatar?: string;
  createdAt?: string;
  updatedAt?: string;
}

// ---------------------------------------------------------------------------
// Field Response Shapes - أشكال استجابات الحقول
// ---------------------------------------------------------------------------

export interface FieldResponse {
  id: string;
  name: string;
  nameAr?: string;
  tenantId?: string;
  farmId: string;
  ownerId?: string;
  crop?: string;
  cropAr?: string;
  cropType?: string;
  description?: string;
  descriptionAr?: string;
  status: FieldStatus;
  /** @deprecated Use `boundary` instead. Duplicate of boundary geometry kept for backwards compatibility. Removal: v5.0.0 */
  polygon?: GeoPolygon;
  boundary?: GeoPolygon;
  /** @deprecated Use `boundary` instead. Duplicate of boundary geometry kept for backwards compatibility. Removal: v5.0.0 */
  geometry?: GeoPolygon;
  /** @since 4.10.0 — Immutable boundary id; fetch geometry via `/partner/v1/boundaries/{id}` */
  boundaryId?: string;
  centroid?: GeoPoint;
  area: number;
  areaHectares?: number;
  irrigationType?: string;
  soilType?: string;
  plantingDate?: string;
  expectedHarvest?: string;
  ndviValue?: number;
  ndviCurrent?: number;
  healthScore?: number;
  metadata?: Record<string, unknown>;
  version?: number;
  createdAt?: string;
  updatedAt?: string;
}

// ---------------------------------------------------------------------------
// Weather Response Shapes - أشكال استجابات الطقس
// ---------------------------------------------------------------------------

export interface WeatherCurrentResponse {
  location: Coordinates & { name?: string };
  current: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    windDirection?: number;
    pressure?: number;
    cloudCover?: number;
    uvIndex?: number;
    description: string;
    descriptionAr?: string;
    icon?: string;
  };
  timestamp: string;
}

export interface WeatherForecastResponse {
  location: Coordinates;
  daily: DailyForecast[];
  hourly?: HourlyForecast[];
}

export interface DailyForecast {
  date: string;
  tempMax: number;
  tempMin: number;
  humidity: number;
  precipitation: number;
  precipitationProbability?: number;
  windSpeed: number;
  description: string;
  descriptionAr?: string;
  icon?: string;
}

export interface HourlyForecast {
  time: string;
  temperature: number;
  humidity: number;
  precipitation: number;
  windSpeed: number;
  icon?: string;
}

export interface WeatherAlertResponse {
  id?: string;
  type: string;
  severity: Severity;
  title: string;
  titleAr?: string;
  message: string;
  messageAr?: string;
  affectedAreas?: string[];
  startTime?: string;
  endTime?: string;
  isActive?: boolean;
  timestamp?: string;
}

// ---------------------------------------------------------------------------
// NDVI / Satellite Response Shapes - أشكال استجابات NDVI
// ---------------------------------------------------------------------------

export interface NdviResponse {
  fieldId: string;
  fieldName?: string;
  current: {
    value: number;
    category: { name: string; nameAr: string; color: string };
    date: string;
  };
  statistics: {
    average: number;
    min: number;
    max: number;
    trend: number;
    trendDirection: TrendDirection;
  };
  history: Array<{ date: string; value: number; cloudCover?: number }>;
  lastUpdated: string;
}

export interface NdviSummaryResponse {
  tenantId: string;
  totalFields: number;
  averageNdvi: number;
  averageHealth: number;
  totalAreaHectares: number;
  distribution: {
    healthy: number;
    moderate: number;
    stressed: number;
    critical: number;
  };
  timestamp: string;
}

// ---------------------------------------------------------------------------
// Crop Health Response Shapes - أشكال استجابات صحة المحاصيل
// ---------------------------------------------------------------------------

export interface CropHealthAnalysisResponse {
  imageId: string;
  fieldId?: string;
  diagnosis: {
    condition: string;
    conditionAr: string;
    confidence: number;
    severity: Severity;
  };
  diseases?: DiseaseDetectionResponse[];
  recommendations: string[];
  recommendationsAr: string[];
  timestamp: string;
}

export interface DiseaseDetectionResponse {
  name: string;
  nameAr: string;
  confidence: number;
  affectedArea: number;
  treatment: string;
  treatmentAr: string;
}

// ---------------------------------------------------------------------------
// Task Response Shapes - أشكال استجابات المهام
// ---------------------------------------------------------------------------

export interface TaskResponse {
  id: string;
  title: string;
  titleAr?: string;
  description?: string;
  descriptionAr?: string;
  fieldId: string;
  fieldName?: string;
  assigneeId?: string;
  assigneeName?: string;
  status: TaskStatus;
  priority: Priority;
  taskType?: string;
  dueDate?: string;
  completedAt?: string;
  notes?: string;
  createdBy?: string;
  createdAt: string;
  updatedAt: string;
}

// ---------------------------------------------------------------------------
// Equipment Response Shapes - أشكال استجابات المعدات
// ---------------------------------------------------------------------------

export interface EquipmentResponse {
  id: string;
  name: string;
  nameAr?: string;
  type: string;
  tenantId?: string;
  status: EquipmentStatus;
  model?: string;
  serialNumber?: string;
  specifications?: Record<string, unknown>;
  lastMaintenanceDate?: string;
  nextMaintenanceDate?: string;
  hoursUsed?: number;
  location?: GeoPoint;
  createdAt: string;
  updatedAt?: string;
}

// ---------------------------------------------------------------------------
// Alert Response Shapes - أشكال استجابات التنبيهات
// ---------------------------------------------------------------------------

export interface AlertResponse {
  id: string;
  type: string;
  severity: AlertSeverity;
  title: string;
  titleAr?: string;
  message: string;
  messageAr?: string;
  source?: string;
  fieldId?: string;
  fieldName?: string;
  status: AlertStatus;
  acknowledgedBy?: string;
  acknowledgedAt?: string;
  resolvedBy?: string;
  resolvedAt?: string;
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt?: string;
}

// ---------------------------------------------------------------------------
// IoT / Sensor Response Shapes - أشكال استجابات إنترنت الأشياء
// ---------------------------------------------------------------------------

export interface SensorResponse {
  id: string;
  fieldId: string;
  name: string;
  type: string;
  status: DeviceStatus;
  batteryLevel?: number;
  lastReading?: SensorReadingResponse;
  location?: GeoPoint;
  createdAt: string;
}

export interface SensorReadingResponse {
  sensorId: string;
  value: number;
  unit: string;
  timestamp: string;
  quality?: 'good' | 'fair' | 'poor';
}

// ---------------------------------------------------------------------------
// Irrigation Response Shapes - أشكال استجابات الري
// ---------------------------------------------------------------------------

export interface IrrigationRecommendationResponse {
  fieldId: string;
  recommendedAmount: number;
  recommendedDuration: number;
  urgency: 'none' | 'low' | 'medium' | 'high';
  reasoning: string;
  reasoningAr?: string;
  et0: number;
  soilMoistureDeficit: number;
  nextIrrigationDate?: string;
}

// ---------------------------------------------------------------------------
// Billing Response Shapes - أشكال استجابات الفوترة
// ---------------------------------------------------------------------------

export interface SubscriptionResponse {
  id: string;
  tenantId: string;
  plan: SubscriptionPlan;
  status: 'active' | 'cancelled' | 'expired' | 'past_due';
  currentPeriodStart: string;
  currentPeriodEnd: string;
  features: string[];
  limits: {
    fields: number;
    users: number;
    storage: number;
    apiCalls: number;
  };
}

export interface InvoiceResponse {
  id: string;
  tenantId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'overdue' | 'cancelled';
  dueDate: string;
  paidAt?: string;
  items: Array<{
    description: string;
    quantity: number;
    unitPrice: number;
    total: number;
  }>;
}

// ---------------------------------------------------------------------------
// Notification Response Shapes - أشكال استجابات الإشعارات
// ---------------------------------------------------------------------------

export interface NotificationResponse {
  id: string;
  type: string;
  title: string;
  titleAr?: string;
  message: string;
  messageAr?: string;
  priority: Priority;
  read: boolean;
  createdAt: string;
  data?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Dashboard & Indicators - لوحة المعلومات
// ---------------------------------------------------------------------------

export interface DashboardStatsResponse {
  totalFarms: number;
  activeFarms: number;
  totalArea: number;
  totalDiagnoses?: number;
  pendingReviews?: number;
  criticalAlerts: number;
  avgHealthScore: number;
  weeklyDiagnoses?: number;
  totalFields?: number;
  totalAreaHectares?: number;
  activeAlerts?: number;
}

export interface FieldIndicatorsResponse {
  fieldId: string;
  indicators: Array<{
    id: string;
    name: string;
    nameAr: string;
    value: number;
    unit?: string;
    status: string;
    trend?: TrendDirection;
  }>;
  overallScore: number;
}

// ---------------------------------------------------------------------------
// Sync Response Shapes (Mobile) - أشكال المزامنة
// ---------------------------------------------------------------------------

export interface SyncResultResponse {
  clientId: string;
  serverId?: string;
  status: 'created' | 'updated' | 'conflict' | 'error';
  serverVersion?: number;
  etag?: string;
  serverData?: unknown;
  error?: string;
}

// ---------------------------------------------------------------------------
// Service Health Response - حالة الخدمة
// ---------------------------------------------------------------------------

export interface ServiceHealthResponse {
  status: 'ok' | 'degraded' | 'error';
  service: string;
  version?: string;
  checks?: Record<string, boolean>;
  uptime?: number;
  timestamp?: string;
}

// ---------------------------------------------------------------------------
// Rate Limit Headers - رؤوس حد المعدل
// ---------------------------------------------------------------------------

export interface RateLimitHeaders {
  /** Remaining requests in current window */
  remaining: number;
  /** Total requests allowed per window */
  limit: number;
  /** Unix timestamp when window resets */
  reset: number;
}

export const RATE_LIMIT_HEADER_NAMES = {
  REMAINING: 'X-RateLimit-Remaining-Minute',
  LIMIT: 'X-RateLimit-Limit-Minute',
  RESET: 'X-RateLimit-Reset',
} as const;

// ---------------------------------------------------------------------------
// Request Headers - رؤوس الطلبات
// ---------------------------------------------------------------------------

export const DEFAULT_HEADERS = {
  CONTENT_TYPE: 'application/json',
  ACCEPT: 'application/json',
  ACCEPT_LANGUAGE: 'ar,en',
} as const;

export const CUSTOM_HEADERS = {
  REQUEST_ID: 'X-Request-Id',
  TENANT_ID: 'X-Tenant-Id',
  CLIENT_PLATFORM: 'X-Client-Platform',
  CLIENT_VERSION: 'X-Client-Version',
  IF_MATCH: 'If-Match',
} as const;

// ---------------------------------------------------------------------------
// Timeout Configuration - إعدادات المهلة
// ---------------------------------------------------------------------------

export const TIMEOUT_DEFAULTS = {
  /** Standard API timeout (ms) */
  DEFAULT: 30_000,
  /** Quick operations (ms) */
  QUICK: 5_000,
  /** Core services (ms) */
  CORE: 10_000,
  /** Weather services (ms) */
  WEATHER: 15_000,
  /** Analytics/terrain (ms) */
  ANALYTICS: 30_000,
  /** AI/LLM operations (ms) */
  AI: 60_000,
  /** File uploads (ms) */
  UPLOAD: 60_000,
} as const;

// ---------------------------------------------------------------------------
// Circuit Breaker Configuration - إعدادات قاطع الدائرة
// ---------------------------------------------------------------------------

export const CIRCUIT_BREAKER_DEFAULTS = {
  /** Number of failures before opening circuit */
  THRESHOLD: 5,
  /** Time to wait before half-open (ms) */
  RESET_TIMEOUT: 30_000,
} as const;

// ---------------------------------------------------------------------------
// Retry Configuration - إعدادات إعادة المحاولة
// ---------------------------------------------------------------------------

export const RETRY_DEFAULTS = {
  /** Maximum number of retries */
  MAX_ATTEMPTS: 3,
  /** Base delay between retries (ms) */
  BASE_DELAY: 1_000,
  /** Delay multiplier for exponential backoff */
  MULTIPLIER: 2,
} as const;

// ---------------------------------------------------------------------------
// Free Tier Limits - حدود الطبقة المجانية
// ---------------------------------------------------------------------------

/** Free tier limits for C-tier farmers (Phase 3 of Component Unification Plan) */
export interface FreeTierLimits {
  dailyQueries: number;
  imageDetection: number;
  weatherAlerts: boolean;
  marketPrices: boolean;
  fieldCount: number;
  advancedNdvi: boolean;
  aiAdvisorFull: boolean;
}

export const DEFAULT_FREE_TIER: FreeTierLimits = {
  dailyQueries: 20,
  imageDetection: 3,
  weatherAlerts: true,
  marketPrices: true,
  fieldCount: 1,
  advancedNdvi: false,
  aiAdvisorFull: false,
};

// ---------------------------------------------------------------------------
// Wave 0: Upload / Export / Partner Response Shapes (@since 4.10.0)
// أشكال الاستجابات للرفع والتصدير وواجهة الشركاء
// ---------------------------------------------------------------------------

/** @since 4.10.0 — Closed set of upload lifecycle states */
export type UploadState =
  | "UPLOADING"
  | "PENDING"
  | "INBOX"
  | "DECLINED"
  | "IMPORTING"
  | "SUCCESS"
  | "INVALID";

/** @since 4.10.0 — Closed set of export job lifecycle states */
export type ExportState =
  | "PROCESSING"
  | "COMPLETED"
  | "NO_DATA"
  | "INVALID"
  | "EXPIRED";

/** @since 4.10.0 — POST /uploads body (initiate chunked upload) */
export interface UploadInitRequest {
  /** Base64-encoded MD5 of the entire payload (validated on completion) */
  md5: string;
  /** Total byte length (max 500 MiB = 524_288_000) */
  length: number;
  /** Vendor MIME type from MEDIA_TYPES */
  contentType: string;
  /** Optional metadata forwarded to ingestion pipeline (e.g. `{fieldId, fileName, resourceOwner}`) */
  metadata?: Record<string, string>;
}

/** @since 4.10.0 — POST /uploads 201 response */
export interface UploadInitResponse {
  uploadId: string;
  expiresAt?: string;
}

/** @since 4.10.0 — GET /uploads/{id}/status response */
export interface UploadStatusResponse {
  id: string;
  status: UploadState;
  bytesReceived?: number;
  /** Error messages when status = INVALID or DECLINED */
  errors?: Array<{ code: string; message: string; path?: string }>;
  updatedAt?: string;
}

/** @since 4.10.0 — POST /exports body */
export interface ExportInitRequest {
  contentType: string;
  definition?: Record<string, unknown>;
}

/** @since 4.10.0 — GET /exports/{id}/status response */
export interface ExportStatusResponse {
  id: string;
  status: ExportState;
  /** Base64 MD5 of completed contents */
  checksum?: string;
  /** Content length in bytes (when COMPLETED) */
  size?: number;
  /** Reusable delta-export token — re-run the same export to fetch only newer data */
  xNextToken?: string;
  error?: string;
}

/** @since 4.10.0 — POST /partner/v1/oauth/token body (application/x-www-form-urlencoded) */
export interface PartnerTokenRequest {
  grant_type: "authorization_code" | "refresh_token" | "client_credentials";
  code?: string;
  redirect_uri?: string;
  refresh_token?: string;
  client_id?: string;
  client_secret?: string;
  scope?: string;
}

/** @since 4.10.0 — POST /partner/v1/oauth/token 200 response (OAuth 2.0 + OIDC) */
export interface PartnerTokenResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  refresh_token?: string;
  scope: string;
  /** OIDC id_token (JWT) — present when `openid` scope was requested */
  id_token?: string;
}

/** @since 4.10.0 — Lightweight field summary for partner list endpoints (no inline geometry) */
export interface PartnerFieldSummary {
  id: string;
  name: string;
  boundaryId: string;
  cropType?: string;
}

/** @since 4.10.0 — Immutable boundary resource (fetched on demand via /boundaries/{id}) */
export interface PartnerBoundaryResponse {
  id: string;
  properties: {
    area: { q: number; u: "ha" | "ac" | "m2" };
    centroid: GeoPoint;
  };
  geometry: GeoPolygon | GeoMultiPolygon;
}

/** @since 4.10.0 — Activity layer summary (asPlanted / asHarvested / asApplied / scouting) */
export interface PartnerActivityLayerSummary {
  id: string;
  fieldIds: string[];
  startTime: string;
  endTime: string;
  createdAt: string;
  updatedAt: string;
  /** Bytes in the raw contents payload (ZIP / ISOXML / shapefile) */
  length?: number;
}

/** @since 4.10.0 — Error envelope (mirrors FieldView structure for partner familiarity) */
export interface PartnerErrorEnvelope {
  error: {
    code: string;
    id: string;
    message: string;
    path?: string;
  };
}

// ---------------------------------------------------------------------------
// Wave 1 #3: Partner Admin Response Shapes (@since 4.12.0)
// ---------------------------------------------------------------------------

export type PartnerClientStatus = "active" | "suspended" | "revoked";
export type PartnerRateTier = "starter" | "pro" | "enterprise";

/** @since 4.12.0 — Partner client row as returned to admin UIs. Never includes
 *  the client_secret hash or the X-Sahool-Partner-Key hash. */
export interface PartnerClientResponse {
  id: string;
  clientId: string;
  name: string;
  nameAr?: string | null;
  description?: string | null;
  homepageUrl?: string | null;
  logoUrl?: string | null;
  redirectUris: string[];
  allowedScopes: string[];
  rateTier: PartnerRateTier;
  status: PartnerClientStatus;
  contactEmail?: string | null;
  createdAt: string;
  updatedAt: string;
  revokedAt?: string | null;
  /** Present on create/rotate responses ONLY — one-time plaintext */
  clientSecret?: string;
  /** Present on create/rotate-api-key responses ONLY — one-time plaintext */
  partnerApiKey?: string;
}

/** @since 4.12.0 — Paginated list of partner clients */
export interface PartnerClientListResponse {
  results: PartnerClientResponse[];
  total: number;
  limit: number;
  offset: number;
}

/** @since 4.12.0 — Consent grant row for admin inspection */
export interface ConsentGrantAdminResponse {
  id: string;
  clientId: string;
  clientName: string;
  userId: string;
  tenantId: string;
  scopes: string[];
  acceptedAt: string;
  revokedAt?: string | null;
  consentIp?: string | null;
}

/** @since 4.12.0 — Access token admin view (never includes the JWT itself) */
export interface AccessTokenAdminResponse {
  jti: string;
  clientId: string;
  clientName?: string;
  userId: string;
  tenantId: string;
  scopes: string[];
  expiresAt: string;
  revokedAt?: string | null;
  revokedReason?: string | null;
  createdAt: string;
}

/** @since 4.12.0 — Refresh token admin view (shows rotation chain) */
export interface RefreshTokenAdminResponse {
  id: string;
  clientId: string;
  clientName?: string;
  userId: string;
  tenantId: string;
  scopes: string[];
  familyId: string;
  rotatedToId?: string | null;
  expiresAt: string;
  revokedAt?: string | null;
  revokedReason?: string | null;
  createdAt: string;
}

/** @since 4.12.0 — Signing key metadata for admin (never exposes private PEM) */
export interface SigningKeyAdminResponse {
  kid: string;
  alg: string;
  activatedAt: string;
  retiredAt?: string | null;
  publicPem: string;
}
