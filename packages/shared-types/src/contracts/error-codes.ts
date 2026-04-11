/**
 * SAHOOL Unified Error Codes
 * أكواد الأخطاء الموحدة
 *
 * Single source of truth for all API error codes.
 * Used by: Web, Admin, Mobile, api-client, backend services.
 *
 * @module @sahool/shared-types/contracts
 * @version 16.0.0
 */

// ---------------------------------------------------------------------------
// Error Codes - أكواد الأخطاء
// ---------------------------------------------------------------------------

/**
 * Unified error codes used across all SAHOOL clients and services.
 * Each code maps to an HTTP status, English message, and Arabic message.
 */
export const ERROR_CODES = {
  // ── Network & Transport ──────────────────────────────────────────────
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  CIRCUIT_OPEN: 'CIRCUIT_OPEN',
  INVALID_RESPONSE: 'INVALID_RESPONSE',

  // ── Authentication (401) ─────────────────────────────────────────────
  UNAUTHORIZED: 'UNAUTHORIZED',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  TOKEN_INVALID: 'TOKEN_INVALID',
  SESSION_EXPIRED: 'SESSION_EXPIRED',

  // ── Authorization (403) ──────────────────────────────────────────────
  FORBIDDEN: 'FORBIDDEN',
  INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',

  // ── Client Errors (4xx) ──────────────────────────────────────────────
  BAD_REQUEST: 'BAD_REQUEST',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  CONFLICT: 'CONFLICT',
  RATE_LIMITED: 'RATE_LIMITED',

  // ── Server Errors (5xx) ──────────────────────────────────────────────
  SERVER_ERROR: 'SERVER_ERROR',
  BAD_GATEWAY: 'BAD_GATEWAY',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  GATEWAY_TIMEOUT: 'GATEWAY_TIMEOUT',

  // ── Mobile-Specific ──────────────────────────────────────────────────
  OFFLINE: 'OFFLINE',
  SYNC_FAILED: 'SYNC_FAILED',
  SYNC_CONFLICT: 'SYNC_CONFLICT',
  CERTIFICATE_ERROR: 'CERTIFICATE_ERROR',

  // ── Vision Service (E1xxx-E8xxx) ─────────────────────────────────────
  // Validation errors (E1xxx)
  VISION_INVALID_FORMAT: 'E1001',
  VISION_FILE_TOO_LARGE: 'E1002',
  VISION_INVALID_DIMENSIONS: 'E1003',
  VISION_INVALID_CONFIDENCE: 'E1004',
  VISION_UNSUPPORTED_TYPE: 'E1005',
  VISION_INVALID_MODEL_VARIANT: 'E1006',
  VISION_EMPTY_IMAGE: 'E1007',
  VISION_MISSING_REQUIRED_FIELD: 'E1008',
  VISION_CORRUPT_FILE: 'E1009',
  VISION_INVALID_BOUNDING_BOX: 'E1010',
  // Model errors (E2xxx)
  VISION_MODEL_NOT_FOUND: 'E2001',
  VISION_MODEL_LOAD_FAILED: 'E2002',
  VISION_INFERENCE_FAILED: 'E2003',
  VISION_MODEL_INCOMPATIBLE: 'E2004',
  VISION_MODEL_VERSION_NOT_FOUND: 'E2005',
  VISION_WARMUP_FAILED: 'E2006',
  VISION_TENSORRT_ERROR: 'E2007',
  // Processing errors (E3xxx)
  VISION_IMAGE_DECODE: 'E3001',
  VISION_PREPROCESSING_FAILED: 'E3002',
  VISION_POSTPROCESSING_FAILED: 'E3003',
  VISION_BATCH_FAILED: 'E3004',
  VISION_BATCH_PROCESSING_FAILED: 'E3005',
  // Resource errors (E4xxx)
  VISION_GPU_OOM: 'E4001',
  VISION_CPU_OOM: 'E4002',
  VISION_DISK_SPACE_LOW: 'E4003',
  VISION_MAX_CONCURRENT: 'E4004',
  // External errors (E5xxx)
  VISION_DB_ERROR: 'E5001',
  VISION_CACHE_ERROR: 'E5002',
  VISION_NATS_ERROR: 'E5003',
  // Rate limit errors (E6xxx)
  VISION_RATE_EXCEEDED: 'E6001',
  VISION_QUOTA_EXCEEDED: 'E6002',
  // Timeout errors (E7xxx)
  VISION_INFERENCE_TIMEOUT: 'E7001',
  VISION_REQUEST_TIMEOUT: 'E7002',
  // Auth errors (E8xxx)
  VISION_AUTH_INVALID_TOKEN: 'E8001',
  VISION_AUTH_TOKEN_EXPIRED: 'E8002',
  VISION_PERMISSION_DENIED: 'E8003',

  // ── Weather Service (W1xxx) ───────────────────────────────────────────
  WEATHER_LOCATION_NOT_FOUND: 'W1001',
  WEATHER_DATA_UNAVAILABLE: 'W1002',
  WEATHER_PROVIDER_ERROR: 'W1003',
  WEATHER_API_KEY_INVALID: 'W1004',
  WEATHER_FORECAST_RANGE_INVALID: 'W1005',
  WEATHER_COORDINATE_INVALID: 'W1006',
  WEATHER_CACHE_ERROR: 'W1007',
  WEATHER_RATE_LIMITED: 'W1008',

  // ── Marketplace Service (M1xxx) ────────────────────────────────────
  MARKETPLACE_PRODUCT_NOT_FOUND: 'M1001',
  MARKETPLACE_INSUFFICIENT_STOCK: 'M1002',
  MARKETPLACE_ORDER_NOT_FOUND: 'M1003',
  MARKETPLACE_WALLET_NOT_FOUND: 'M1004',
  MARKETPLACE_INSUFFICIENT_BALANCE: 'M1005',
  MARKETPLACE_INVALID_TRANSACTION: 'M1006',
  MARKETPLACE_ESCROW_NOT_FOUND: 'M1007',
  MARKETPLACE_LOAN_NOT_FOUND: 'M1008',
  MARKETPLACE_DUPLICATE_TRANSACTION: 'M1009',
  MARKETPLACE_PIN_REQUIRED: 'M1010',
  MARKETPLACE_CREDIT_SCORE_ERROR: 'M1011',
  MARKETPLACE_RATE_LIMITED: 'M1012',

  // ── Field Management Service (F1xxx) ───────────────────────────────
  FIELD_NOT_FOUND: 'F1001',
  FIELD_BOUNDARY_INVALID: 'F1002',
  FIELD_AREA_TOO_LARGE: 'F1003',
  FIELD_COORDINATE_INVALID: 'F1004',
  FIELD_DUPLICATE_NAME: 'F1005',
  FIELD_TENANT_MISMATCH: 'F1006',
  FIELD_CROP_NOT_SUPPORTED: 'F1007',
  FIELD_SYNC_CONFLICT: 'F1008',
  FIELD_GEOJSON_INVALID: 'F1009',
  FIELD_POSTGIS_ERROR: 'F1010',
  // Crop Season (F11xx)
  CROP_SEASON_NOT_FOUND: 'F1101',
  CROP_SEASON_ALREADY_ENDED: 'F1102',
  CROP_SEASON_ANOTHER_CURRENT_EXISTS: 'F1103',
  CROP_SEASON_INVALID_DATE_RANGE: 'F1104',
  // Field Operation (F12xx)
  FIELD_OPERATION_NOT_FOUND: 'F1201',
  FIELD_OPERATION_INVALID_TYPE: 'F1202',
  FIELD_OPERATION_INVALID_DATE: 'F1203',
  FIELD_OPERATION_DURATION_INVALID: 'F1204',
  FIELD_OPERATION_LOCKED_BY_ERP: 'F1205',
  FIELD_OPERATION_NOT_APPROVED: 'F1206',
  FIELD_OPERATION_REJECTED: 'F1207',
  FIELD_OPERATION_ALREADY_POSTED: 'F1208',
  // ERP Sync (F13xx)
  ERP_ADAPTER_NOT_CONFIGURED: 'F1301',
  ERP_POSTING_FAILED: 'F1302',
  ERP_WEBHOOK_UNAVAILABLE: 'F1303',
  ERP_SIGNATURE_INVALID: 'F1304',
  // Idempotency (F14xx)
  IDEMPOTENCY_KEY_CONFLICT: 'F1401',
  IDEMPOTENCY_KEY_EXPIRED: 'F1402',
  // Field Sub-Zone (F15xx)
  SUB_ZONE_NOT_FOUND: 'F1501',
  SUB_ZONE_INVALID_POLYGON: 'F1502',
  SUB_ZONE_OUTSIDE_FIELD: 'F1503',
  SUB_ZONE_AREA_TOO_SMALL: 'F1504',
  SUB_ZONE_SELF_INTERSECTION: 'F1505',
  // Field Report (F16xx)
  REPORT_NOT_FOUND: 'F1601',
  REPORT_NOT_READY: 'F1602',
  REPORT_RENDER_FAILED: 'F1603',
  REPORT_CONTENT_UNAVAILABLE: 'F1604',
  REPORT_EXPIRED: 'F1605',
  // Carbon (F17xx)
  CARBON_COMPUTATION_FAILED: 'F1701',
  CARBON_NO_COMPUTABLE_INPUTS: 'F1702',
  CARBON_INVALID_FACTOR: 'F1703',

  // ── Irrigation Service (I1xxx) ─────────────────────────────────────
  IRRIGATION_FIELD_NOT_FOUND: 'I1001',
  IRRIGATION_SCHEDULE_NOT_FOUND: 'I1002',
  IRRIGATION_INVALID_WATER_VOLUME: 'I1003',
  IRRIGATION_SENSOR_DATA_INVALID: 'I1004',
  IRRIGATION_CALCULATION_ERROR: 'I1005',
  IRRIGATION_METHOD_NOT_SUPPORTED: 'I1006',
  IRRIGATION_CROP_NOT_FOUND: 'I1007',
  IRRIGATION_EFFICIENCY_OUT_OF_RANGE: 'I1008',

  // ── Notification Service (N1xxx) ───────────────────────────────────
  NOTIFICATION_NOT_FOUND: 'N1001',
  NOTIFICATION_DELIVERY_FAILED: 'N1002',
  NOTIFICATION_DEVICE_NOT_REGISTERED: 'N1003',
  NOTIFICATION_INVALID_CHANNEL: 'N1004',
  NOTIFICATION_TEMPLATE_NOT_FOUND: 'N1005',
  NOTIFICATION_RATE_LIMITED: 'N1006',
  NOTIFICATION_PREFERENCES_NOT_FOUND: 'N1007',
  NOTIFICATION_BROADCAST_FAILED: 'N1008',

  // ── Advisory Service (A1xxx) ───────────────────────────────────────
  ADVISORY_NOT_FOUND: 'A1001',
  ADVISORY_CROP_NOT_SUPPORTED: 'A1002',
  ADVISORY_SOIL_DATA_MISSING: 'A1003',
  ADVISORY_RECOMMENDATION_FAILED: 'A1004',
  ADVISORY_FERTILIZER_CALC_ERROR: 'A1005',
  ADVISORY_KNOWLEDGE_BASE_ERROR: 'A1006',
  ADVISORY_WEATHER_DATA_UNAVAILABLE: 'A1007',
  ADVISORY_RATE_LIMITED: 'A1008',

  // ── User Service (U1xxx) ────────────────────────────────────────────
  USER_NOT_FOUND: 'U1001',
  USER_EMAIL_EXISTS: 'U1002',
  USER_PHONE_EXISTS: 'U1003',
  USER_INVALID_CREDENTIALS: 'U1004',
  USER_ACCOUNT_LOCKED: 'U1005',
  USER_OTP_EXPIRED: 'U1006',
  USER_OTP_INVALID: 'U1007',
  USER_TOKEN_EXPIRED: 'U1008',
  USER_2FA_REQUIRED: 'U1009',
  USER_PASSWORD_TOO_WEAK: 'U1010',

  // ── Billing Service (B1xxx) ────────────────────────────────────────
  BILLING_SUBSCRIPTION_NOT_FOUND: 'B1001',
  BILLING_PLAN_NOT_FOUND: 'B1002',
  BILLING_PAYMENT_FAILED: 'B1003',
  BILLING_INVOICE_NOT_FOUND: 'B1004',
  BILLING_QUOTA_EXCEEDED: 'B1005',
  BILLING_INVALID_PLAN_CHANGE: 'B1006',

  // ── Virtual Sensors Service (S1xxx) ────────────────────────────────
  SENSOR_CALCULATION_ERROR: 'S1001',
  SENSOR_INVALID_INPUT: 'S1002',
  SENSOR_CALIBRATION_FAILED: 'S1003',
  SENSOR_DATA_OUT_OF_RANGE: 'S1004',

  // ── Vegetation & NDVI Service (V1xxx) ──────────────────────────────
  VEGETATION_FIELD_NOT_FOUND: 'V1001',
  VEGETATION_NDVI_DATA_UNAVAILABLE: 'V1002',
  VEGETATION_SATELLITE_ERROR: 'V1003',
  VEGETATION_CLOUD_COVER_HIGH: 'V1004',
  VEGETATION_INVALID_DATE_RANGE: 'V1005',
  VEGETATION_ANOMALY_DETECTION_FAILED: 'V1006',
  VEGETATION_INDICATOR_NOT_FOUND: 'V1007',
  VEGETATION_INDICATOR_VALUE_INVALID: 'V1008',

  // ── Generic ──────────────────────────────────────────────────────────
  UNKNOWN: 'UNKNOWN',
} as const;

export type ErrorCode = (typeof ERROR_CODES)[keyof typeof ERROR_CODES];

// ---------------------------------------------------------------------------
// Error Messages - رسائل الأخطاء (ثنائية اللغة)
// ---------------------------------------------------------------------------

export interface ErrorMessage {
  /** Error code */
  code: ErrorCode;
  /** Default HTTP status (0 = no HTTP mapping) */
  httpStatus: number;
  /** English message */
  en: string;
  /** Arabic message */
  ar: string;
  /** Whether client should retry */
  retryable: boolean;
}

export const ERROR_MESSAGES: Record<string, ErrorMessage> = {
  // ── Network & Transport ──────────────────────────────────────────────
  [ERROR_CODES.NETWORK_ERROR]: {
    code: ERROR_CODES.NETWORK_ERROR,
    httpStatus: 0,
    en: 'Network error - please check your connection',
    ar: 'خطأ في الشبكة - يرجى التحقق من اتصالك',
    retryable: true,
  },
  [ERROR_CODES.TIMEOUT]: {
    code: ERROR_CODES.TIMEOUT,
    httpStatus: 504,
    en: 'Request timed out - please try again',
    ar: 'انتهت مهلة الطلب - يرجى المحاولة مرة أخرى',
    retryable: true,
  },
  [ERROR_CODES.CIRCUIT_OPEN]: {
    code: ERROR_CODES.CIRCUIT_OPEN,
    httpStatus: 503,
    en: 'Service temporarily unavailable',
    ar: 'الخدمة غير متاحة مؤقتاً',
    retryable: true,
  },
  [ERROR_CODES.INVALID_RESPONSE]: {
    code: ERROR_CODES.INVALID_RESPONSE,
    httpStatus: 502,
    en: 'Invalid response from server',
    ar: 'استجابة غير صالحة من الخادم',
    retryable: false,
  },

  // ── Authentication (401) ─────────────────────────────────────────────
  [ERROR_CODES.UNAUTHORIZED]: {
    code: ERROR_CODES.UNAUTHORIZED,
    httpStatus: 401,
    en: 'Authentication required',
    ar: 'المصادقة مطلوبة',
    retryable: false,
  },
  [ERROR_CODES.TOKEN_EXPIRED]: {
    code: ERROR_CODES.TOKEN_EXPIRED,
    httpStatus: 401,
    en: 'Session expired. Please login again.',
    ar: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  },
  [ERROR_CODES.TOKEN_INVALID]: {
    code: ERROR_CODES.TOKEN_INVALID,
    httpStatus: 401,
    en: 'Invalid authentication token',
    ar: 'رمز مصادقة غير صالح',
    retryable: false,
  },
  [ERROR_CODES.SESSION_EXPIRED]: {
    code: ERROR_CODES.SESSION_EXPIRED,
    httpStatus: 401,
    en: 'Session expired. Please login again.',
    ar: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  },

  // ── Authorization (403) ──────────────────────────────────────────────
  [ERROR_CODES.FORBIDDEN]: {
    code: ERROR_CODES.FORBIDDEN,
    httpStatus: 403,
    en: 'Access denied - insufficient permissions',
    ar: 'الوصول مرفوض - صلاحيات غير كافية',
    retryable: false,
  },
  [ERROR_CODES.INSUFFICIENT_PERMISSIONS]: {
    code: ERROR_CODES.INSUFFICIENT_PERMISSIONS,
    httpStatus: 403,
    en: 'You do not have permission to perform this action',
    ar: 'ليس لديك صلاحية لتنفيذ هذا الإجراء',
    retryable: false,
  },

  // ── Client Errors (4xx) ──────────────────────────────────────────────
  [ERROR_CODES.BAD_REQUEST]: {
    code: ERROR_CODES.BAD_REQUEST,
    httpStatus: 400,
    en: 'Invalid request',
    ar: 'طلب غير صالح',
    retryable: false,
  },
  [ERROR_CODES.VALIDATION_ERROR]: {
    code: ERROR_CODES.VALIDATION_ERROR,
    httpStatus: 400,
    en: 'Validation error - please check your input',
    ar: 'خطأ في التحقق - يرجى مراجعة المدخلات',
    retryable: false,
  },
  [ERROR_CODES.NOT_FOUND]: {
    code: ERROR_CODES.NOT_FOUND,
    httpStatus: 404,
    en: 'Resource not found',
    ar: 'المورد غير موجود',
    retryable: false,
  },
  [ERROR_CODES.CONFLICT]: {
    code: ERROR_CODES.CONFLICT,
    httpStatus: 409,
    en: 'Conflict - resource was modified by another request',
    ar: 'تعارض - تم تعديل المورد بواسطة طلب آخر',
    retryable: false,
  },
  [ERROR_CODES.RATE_LIMITED]: {
    code: ERROR_CODES.RATE_LIMITED,
    httpStatus: 429,
    en: 'Too many requests. Please wait.',
    ar: 'طلبات كثيرة جداً. يرجى الانتظار.',
    retryable: true,
  },

  // ── Server Errors (5xx) ──────────────────────────────────────────────
  [ERROR_CODES.SERVER_ERROR]: {
    code: ERROR_CODES.SERVER_ERROR,
    httpStatus: 500,
    en: 'Server error - please try again later',
    ar: 'خطأ في الخادم - يرجى المحاولة لاحقاً',
    retryable: true,
  },
  [ERROR_CODES.BAD_GATEWAY]: {
    code: ERROR_CODES.BAD_GATEWAY,
    httpStatus: 502,
    en: 'Bad gateway - upstream service error',
    ar: 'خطأ في البوابة - خطأ في الخدمة الأصلية',
    retryable: true,
  },
  [ERROR_CODES.SERVICE_UNAVAILABLE]: {
    code: ERROR_CODES.SERVICE_UNAVAILABLE,
    httpStatus: 503,
    en: 'Service temporarily unavailable',
    ar: 'الخدمة غير متاحة مؤقتاً',
    retryable: true,
  },
  [ERROR_CODES.GATEWAY_TIMEOUT]: {
    code: ERROR_CODES.GATEWAY_TIMEOUT,
    httpStatus: 504,
    en: 'Gateway timeout - please try again',
    ar: 'انتهت مهلة البوابة - يرجى المحاولة مرة أخرى',
    retryable: true,
  },

  // ── Mobile-Specific ──────────────────────────────────────────────────
  [ERROR_CODES.OFFLINE]: {
    code: ERROR_CODES.OFFLINE,
    httpStatus: 0,
    en: 'You are offline. Changes will sync when connected.',
    ar: 'أنت غير متصل. سيتم مزامنة التغييرات عند الاتصال.',
    retryable: true,
  },
  [ERROR_CODES.SYNC_FAILED]: {
    code: ERROR_CODES.SYNC_FAILED,
    httpStatus: 0,
    en: 'Sync failed. Please try again.',
    ar: 'فشلت المزامنة. يرجى المحاولة مرة أخرى.',
    retryable: true,
  },
  [ERROR_CODES.SYNC_CONFLICT]: {
    code: ERROR_CODES.SYNC_CONFLICT,
    httpStatus: 409,
    en: 'Sync conflict detected. Please resolve manually.',
    ar: 'تم اكتشاف تعارض في المزامنة. يرجى الحل يدوياً.',
    retryable: false,
  },
  [ERROR_CODES.CERTIFICATE_ERROR]: {
    code: ERROR_CODES.CERTIFICATE_ERROR,
    httpStatus: 0,
    en: 'Security certificate error',
    ar: 'خطأ في شهادة الأمان',
    retryable: false,
  },

  // ── Weather Service (W1xxx) ───────────────────────────────────────────
  [ERROR_CODES.WEATHER_LOCATION_NOT_FOUND]: {
    code: ERROR_CODES.WEATHER_LOCATION_NOT_FOUND,
    httpStatus: 404,
    en: 'Weather location not found',
    ar: 'موقع الطقس غير موجود',
    retryable: false,
  },
  [ERROR_CODES.WEATHER_DATA_UNAVAILABLE]: {
    code: ERROR_CODES.WEATHER_DATA_UNAVAILABLE,
    httpStatus: 503,
    en: 'Weather data is currently unavailable',
    ar: 'بيانات الطقس غير متاحة حالياً',
    retryable: true,
  },
  [ERROR_CODES.WEATHER_PROVIDER_ERROR]: {
    code: ERROR_CODES.WEATHER_PROVIDER_ERROR,
    httpStatus: 502,
    en: 'Weather provider returned an error',
    ar: 'أرجع مزود الطقس خطأ',
    retryable: true,
  },
  [ERROR_CODES.WEATHER_API_KEY_INVALID]: {
    code: ERROR_CODES.WEATHER_API_KEY_INVALID,
    httpStatus: 401,
    en: 'Invalid weather API key',
    ar: 'مفتاح واجهة برمجة الطقس غير صالح',
    retryable: false,
  },
  [ERROR_CODES.WEATHER_FORECAST_RANGE_INVALID]: {
    code: ERROR_CODES.WEATHER_FORECAST_RANGE_INVALID,
    httpStatus: 400,
    en: 'Invalid forecast date range',
    ar: 'نطاق تاريخ التنبؤ غير صالح',
    retryable: false,
  },
  [ERROR_CODES.WEATHER_COORDINATE_INVALID]: {
    code: ERROR_CODES.WEATHER_COORDINATE_INVALID,
    httpStatus: 400,
    en: 'Invalid geographic coordinates',
    ar: 'إحداثيات جغرافية غير صالحة',
    retryable: false,
  },
  [ERROR_CODES.WEATHER_CACHE_ERROR]: {
    code: ERROR_CODES.WEATHER_CACHE_ERROR,
    httpStatus: 503,
    en: 'Weather cache error',
    ar: 'خطأ في ذاكرة التخزين المؤقت للطقس',
    retryable: true,
  },
  [ERROR_CODES.WEATHER_RATE_LIMITED]: {
    code: ERROR_CODES.WEATHER_RATE_LIMITED,
    httpStatus: 429,
    en: 'Weather API rate limit exceeded. Please wait.',
    ar: 'تم تجاوز حد معدل واجهة برمجة الطقس. يرجى الانتظار.',
    retryable: true,
  },

  // ── Marketplace Service (M1xxx) ────────────────────────────────────
  [ERROR_CODES.MARKETPLACE_PRODUCT_NOT_FOUND]: {
    code: ERROR_CODES.MARKETPLACE_PRODUCT_NOT_FOUND,
    httpStatus: 404,
    en: 'Product not found in marketplace',
    ar: 'المنتج غير موجود في السوق',
    retryable: false,
  },
  [ERROR_CODES.MARKETPLACE_INSUFFICIENT_STOCK]: {
    code: ERROR_CODES.MARKETPLACE_INSUFFICIENT_STOCK,
    httpStatus: 409,
    en: 'Insufficient stock for the requested quantity',
    ar: 'المخزون غير كافٍ للكمية المطلوبة',
    retryable: false,
  },
  [ERROR_CODES.MARKETPLACE_ORDER_NOT_FOUND]: {
    code: ERROR_CODES.MARKETPLACE_ORDER_NOT_FOUND,
    httpStatus: 404,
    en: 'Order not found',
    ar: 'الطلب غير موجود',
    retryable: false,
  },
  [ERROR_CODES.MARKETPLACE_WALLET_NOT_FOUND]: {
    code: ERROR_CODES.MARKETPLACE_WALLET_NOT_FOUND,
    httpStatus: 404,
    en: 'Wallet not found for the specified user',
    ar: 'المحفظة غير موجودة للمستخدم المحدد',
    retryable: false,
  },
  [ERROR_CODES.MARKETPLACE_INSUFFICIENT_BALANCE]: {
    code: ERROR_CODES.MARKETPLACE_INSUFFICIENT_BALANCE,
    httpStatus: 402,
    en: 'Insufficient wallet balance for this transaction',
    ar: 'رصيد المحفظة غير كافٍ لهذه المعاملة',
    retryable: false,
  },
  [ERROR_CODES.MARKETPLACE_INVALID_TRANSACTION]: {
    code: ERROR_CODES.MARKETPLACE_INVALID_TRANSACTION,
    httpStatus: 400,
    en: 'Invalid transaction details',
    ar: 'تفاصيل المعاملة غير صالحة',
    retryable: false,
  },
  [ERROR_CODES.MARKETPLACE_ESCROW_NOT_FOUND]: {
    code: ERROR_CODES.MARKETPLACE_ESCROW_NOT_FOUND,
    httpStatus: 404,
    en: 'Escrow record not found',
    ar: 'سجل الضمان غير موجود',
    retryable: false,
  },
  [ERROR_CODES.MARKETPLACE_LOAN_NOT_FOUND]: {
    code: ERROR_CODES.MARKETPLACE_LOAN_NOT_FOUND,
    httpStatus: 404,
    en: 'Loan record not found',
    ar: 'سجل القرض غير موجود',
    retryable: false,
  },
  [ERROR_CODES.MARKETPLACE_DUPLICATE_TRANSACTION]: {
    code: ERROR_CODES.MARKETPLACE_DUPLICATE_TRANSACTION,
    httpStatus: 409,
    en: 'Duplicate transaction detected',
    ar: 'تم اكتشاف معاملة مكررة',
    retryable: false,
  },
  [ERROR_CODES.MARKETPLACE_PIN_REQUIRED]: {
    code: ERROR_CODES.MARKETPLACE_PIN_REQUIRED,
    httpStatus: 403,
    en: 'PIN verification required to complete this transaction',
    ar: 'يلزم التحقق من الرقم السري لإتمام هذه المعاملة',
    retryable: false,
  },
  [ERROR_CODES.MARKETPLACE_CREDIT_SCORE_ERROR]: {
    code: ERROR_CODES.MARKETPLACE_CREDIT_SCORE_ERROR,
    httpStatus: 503,
    en: 'Credit score service is currently unavailable',
    ar: 'خدمة التصنيف الائتماني غير متاحة حالياً',
    retryable: true,
  },
  [ERROR_CODES.MARKETPLACE_RATE_LIMITED]: {
    code: ERROR_CODES.MARKETPLACE_RATE_LIMITED,
    httpStatus: 429,
    en: 'Marketplace API rate limit exceeded. Please wait.',
    ar: 'تم تجاوز حد معدل واجهة برمجة السوق. يرجى الانتظار.',
    retryable: true,
  },

  // ── Field Management Service (F1xxx) ───────────────────────────────
  [ERROR_CODES.FIELD_NOT_FOUND]: {
    code: ERROR_CODES.FIELD_NOT_FOUND,
    httpStatus: 404,
    en: 'Field not found',
    ar: 'الحقل غير موجود',
    retryable: false,
  },
  [ERROR_CODES.FIELD_BOUNDARY_INVALID]: {
    code: ERROR_CODES.FIELD_BOUNDARY_INVALID,
    httpStatus: 400,
    en: 'Field boundary geometry is invalid',
    ar: 'هندسة حدود الحقل غير صالحة',
    retryable: false,
  },
  [ERROR_CODES.FIELD_AREA_TOO_LARGE]: {
    code: ERROR_CODES.FIELD_AREA_TOO_LARGE,
    httpStatus: 400,
    en: 'Field area exceeds maximum allowed size',
    ar: 'مساحة الحقل تتجاوز الحد الأقصى المسموح به',
    retryable: false,
  },
  [ERROR_CODES.FIELD_COORDINATE_INVALID]: {
    code: ERROR_CODES.FIELD_COORDINATE_INVALID,
    httpStatus: 400,
    en: 'Invalid field coordinates',
    ar: 'إحداثيات الحقل غير صالحة',
    retryable: false,
  },
  [ERROR_CODES.FIELD_DUPLICATE_NAME]: {
    code: ERROR_CODES.FIELD_DUPLICATE_NAME,
    httpStatus: 409,
    en: 'A field with this name already exists',
    ar: 'يوجد حقل بهذا الاسم بالفعل',
    retryable: false,
  },
  [ERROR_CODES.FIELD_TENANT_MISMATCH]: {
    code: ERROR_CODES.FIELD_TENANT_MISMATCH,
    httpStatus: 403,
    en: 'Field does not belong to the current tenant',
    ar: 'الحقل لا ينتمي إلى المستأجر الحالي',
    retryable: false,
  },
  [ERROR_CODES.FIELD_CROP_NOT_SUPPORTED]: {
    code: ERROR_CODES.FIELD_CROP_NOT_SUPPORTED,
    httpStatus: 400,
    en: 'Crop type is not supported for this field region',
    ar: 'نوع المحصول غير مدعوم لمنطقة هذا الحقل',
    retryable: false,
  },
  [ERROR_CODES.FIELD_SYNC_CONFLICT]: {
    code: ERROR_CODES.FIELD_SYNC_CONFLICT,
    httpStatus: 409,
    en: 'Field data sync conflict detected. Please resolve manually.',
    ar: 'تم اكتشاف تعارض في مزامنة بيانات الحقل. يرجى الحل يدوياً.',
    retryable: false,
  },
  [ERROR_CODES.FIELD_GEOJSON_INVALID]: {
    code: ERROR_CODES.FIELD_GEOJSON_INVALID,
    httpStatus: 400,
    en: 'Invalid GeoJSON format for field boundary',
    ar: 'تنسيق GeoJSON غير صالح لحدود الحقل',
    retryable: false,
  },
  [ERROR_CODES.FIELD_POSTGIS_ERROR]: {
    code: ERROR_CODES.FIELD_POSTGIS_ERROR,
    httpStatus: 500,
    en: 'PostGIS spatial operation failed',
    ar: 'فشلت العملية المكانية في PostGIS',
    retryable: true,
  },
  // Crop Season (F11xx)
  [ERROR_CODES.CROP_SEASON_NOT_FOUND]: {
    code: ERROR_CODES.CROP_SEASON_NOT_FOUND,
    httpStatus: 404,
    en: 'Crop season not found',
    ar: 'الموسم المحصولي غير موجود',
    retryable: false,
  },
  [ERROR_CODES.CROP_SEASON_ALREADY_ENDED]: {
    code: ERROR_CODES.CROP_SEASON_ALREADY_ENDED,
    httpStatus: 400,
    en: 'Crop season is already ended',
    ar: 'الموسم المحصولي منتهٍ بالفعل',
    retryable: false,
  },
  [ERROR_CODES.CROP_SEASON_ANOTHER_CURRENT_EXISTS]: {
    code: ERROR_CODES.CROP_SEASON_ANOTHER_CURRENT_EXISTS,
    httpStatus: 400,
    en: 'Another current season exists for this field - end it first',
    ar: 'يوجد موسم حالي آخر لهذا الحقل — يجب إنهاؤه أولاً',
    retryable: false,
  },
  [ERROR_CODES.CROP_SEASON_INVALID_DATE_RANGE]: {
    code: ERROR_CODES.CROP_SEASON_INVALID_DATE_RANGE,
    httpStatus: 400,
    en: 'Invalid date range - harvest date must be after sowing date',
    ar: 'نطاق التواريخ غير صالح — تاريخ الحصاد يجب أن يكون بعد تاريخ البذار',
    retryable: false,
  },
  // Field Operation (F12xx)
  [ERROR_CODES.FIELD_OPERATION_NOT_FOUND]: {
    code: ERROR_CODES.FIELD_OPERATION_NOT_FOUND,
    httpStatus: 404,
    en: 'Field operation not found',
    ar: 'عملية الحقل غير موجودة',
    retryable: false,
  },
  [ERROR_CODES.FIELD_OPERATION_INVALID_TYPE]: {
    code: ERROR_CODES.FIELD_OPERATION_INVALID_TYPE,
    httpStatus: 400,
    en: 'Invalid field operation type',
    ar: 'نوع العملية غير صالح',
    retryable: false,
  },
  [ERROR_CODES.FIELD_OPERATION_INVALID_DATE]: {
    code: ERROR_CODES.FIELD_OPERATION_INVALID_DATE,
    httpStatus: 400,
    en: 'Invalid operation date',
    ar: 'تاريخ العملية غير صالح',
    retryable: false,
  },
  [ERROR_CODES.FIELD_OPERATION_DURATION_INVALID]: {
    code: ERROR_CODES.FIELD_OPERATION_DURATION_INVALID,
    httpStatus: 400,
    en: 'Invalid duration - must be a non-negative number of hours',
    ar: 'مدة العملية غير صالحة — يجب أن تكون عدداً غير سالب من الساعات',
    retryable: false,
  },
  [ERROR_CODES.FIELD_OPERATION_LOCKED_BY_ERP]: {
    code: ERROR_CODES.FIELD_OPERATION_LOCKED_BY_ERP,
    httpStatus: 400,
    en: 'Operation is locked because it was posted to ERP - reverse the posting first',
    ar: 'العملية مقفلة لأنها مرحلة إلى نظام المحاسبة — يجب إلغاء الترحيل أولاً',
    retryable: false,
  },
  [ERROR_CODES.FIELD_OPERATION_NOT_APPROVED]: {
    code: ERROR_CODES.FIELD_OPERATION_NOT_APPROVED,
    httpStatus: 400,
    en: 'Only approved operations can be posted to ERP',
    ar: 'لا يمكن ترحيل عملية غير معتمدة إلى نظام المحاسبة',
    retryable: false,
  },
  [ERROR_CODES.FIELD_OPERATION_REJECTED]: {
    code: ERROR_CODES.FIELD_OPERATION_REJECTED,
    httpStatus: 400,
    en: 'Operation has been rejected and cannot be approved',
    ar: 'العملية مرفوضة ولا يمكن اعتمادها',
    retryable: false,
  },
  [ERROR_CODES.FIELD_OPERATION_ALREADY_POSTED]: {
    code: ERROR_CODES.FIELD_OPERATION_ALREADY_POSTED,
    httpStatus: 409,
    en: 'Operation has already been posted to ERP',
    ar: 'تم ترحيل العملية مسبقاً إلى نظام المحاسبة',
    retryable: false,
  },
  // ERP Sync
  [ERROR_CODES.ERP_ADAPTER_NOT_CONFIGURED]: {
    code: ERROR_CODES.ERP_ADAPTER_NOT_CONFIGURED,
    httpStatus: 400,
    en: 'No ERP adapter is configured',
    ar: 'لا يوجد موفر ERP مفعّل حالياً',
    retryable: false,
  },
  [ERROR_CODES.ERP_POSTING_FAILED]: {
    code: ERROR_CODES.ERP_POSTING_FAILED,
    httpStatus: 502,
    en: 'ERP posting failed - will be retried by the background worker',
    ar: 'فشل ترحيل العملية إلى ERP - ستتم إعادة المحاولة تلقائياً',
    retryable: true,
  },
  [ERROR_CODES.ERP_WEBHOOK_UNAVAILABLE]: {
    code: ERROR_CODES.ERP_WEBHOOK_UNAVAILABLE,
    httpStatus: 502,
    en: 'External ERP webhook is unavailable',
    ar: 'نقطة الاتصال بنظام المحاسبة الخارجي غير متاحة',
    retryable: true,
  },
  [ERROR_CODES.ERP_SIGNATURE_INVALID]: {
    code: ERROR_CODES.ERP_SIGNATURE_INVALID,
    httpStatus: 401,
    en: 'ERP webhook signature is invalid',
    ar: 'توقيع webhook غير صالح',
    retryable: false,
  },
  // Idempotency
  [ERROR_CODES.IDEMPOTENCY_KEY_CONFLICT]: {
    code: ERROR_CODES.IDEMPOTENCY_KEY_CONFLICT,
    httpStatus: 409,
    en: 'Idempotency-Key conflict: same key used with a different body',
    ar: 'تعارض في مفتاح Idempotency — نفس المفتاح مع جسم مختلف',
    retryable: false,
  },
  [ERROR_CODES.IDEMPOTENCY_KEY_EXPIRED]: {
    code: ERROR_CODES.IDEMPOTENCY_KEY_EXPIRED,
    httpStatus: 410,
    en: 'Idempotency-Key has expired',
    ar: 'انتهت صلاحية مفتاح Idempotency',
    retryable: false,
  },
  // Field Sub-Zone (F15xx)
  [ERROR_CODES.SUB_ZONE_NOT_FOUND]: {
    code: ERROR_CODES.SUB_ZONE_NOT_FOUND,
    httpStatus: 404,
    en: 'Sub-zone not found',
    ar: 'المنطقة الفرعية غير موجودة',
    retryable: false,
  },
  [ERROR_CODES.SUB_ZONE_INVALID_POLYGON]: {
    code: ERROR_CODES.SUB_ZONE_INVALID_POLYGON,
    httpStatus: 400,
    en: 'Sub-zone polygon geometry is invalid',
    ar: 'هندسة المنطقة الفرعية غير صالحة',
    retryable: false,
  },
  [ERROR_CODES.SUB_ZONE_OUTSIDE_FIELD]: {
    code: ERROR_CODES.SUB_ZONE_OUTSIDE_FIELD,
    httpStatus: 400,
    en: 'Sub-zone boundary must lie inside the parent field',
    ar: 'يجب أن تكون حدود المنطقة الفرعية داخل حدود الحقل',
    retryable: false,
  },
  [ERROR_CODES.SUB_ZONE_AREA_TOO_SMALL]: {
    code: ERROR_CODES.SUB_ZONE_AREA_TOO_SMALL,
    httpStatus: 400,
    en: 'Sub-zone area is smaller than the minimum allowed (1 m²)',
    ar: 'مساحة المنطقة الفرعية أصغر من الحد المسموح',
    retryable: false,
  },
  [ERROR_CODES.SUB_ZONE_SELF_INTERSECTION]: {
    code: ERROR_CODES.SUB_ZONE_SELF_INTERSECTION,
    httpStatus: 400,
    en: 'Sub-zone polygon has self-intersection',
    ar: 'المنطقة الفرعية تحتوي على تقاطع ذاتي',
    retryable: false,
  },
  // Field Report (F16xx)
  [ERROR_CODES.REPORT_NOT_FOUND]: {
    code: ERROR_CODES.REPORT_NOT_FOUND,
    httpStatus: 404,
    en: 'Report not found',
    ar: 'التقرير غير موجود',
    retryable: false,
  },
  [ERROR_CODES.REPORT_NOT_READY]: {
    code: ERROR_CODES.REPORT_NOT_READY,
    httpStatus: 400,
    en: 'Report is not ready yet — poll until status=ready',
    ar: 'التقرير غير جاهز بعد — انتظر حتى تصبح الحالة جاهز',
    retryable: true,
  },
  [ERROR_CODES.REPORT_RENDER_FAILED]: {
    code: ERROR_CODES.REPORT_RENDER_FAILED,
    httpStatus: 500,
    en: 'Report rendering failed',
    ar: 'فشل توليد التقرير',
    retryable: true,
  },
  [ERROR_CODES.REPORT_CONTENT_UNAVAILABLE]: {
    code: ERROR_CODES.REPORT_CONTENT_UNAVAILABLE,
    httpStatus: 404,
    en: 'Report content not available',
    ar: 'محتوى التقرير غير متوفر',
    retryable: false,
  },
  [ERROR_CODES.REPORT_EXPIRED]: {
    code: ERROR_CODES.REPORT_EXPIRED,
    httpStatus: 410,
    en: 'Report URL has expired — regenerate',
    ar: 'انتهت صلاحية رابط التقرير — يرجى إعادة التوليد',
    retryable: false,
  },
  // Carbon (F17xx)
  [ERROR_CODES.CARBON_COMPUTATION_FAILED]: {
    code: ERROR_CODES.CARBON_COMPUTATION_FAILED,
    httpStatus: 500,
    en: 'Carbon computation failed',
    ar: 'فشل حساب البصمة الكربونية',
    retryable: true,
  },
  [ERROR_CODES.CARBON_NO_COMPUTABLE_INPUTS]: {
    code: ERROR_CODES.CARBON_NO_COMPUTABLE_INPUTS,
    httpStatus: 400,
    en: 'Operation has no inputs suitable for carbon computation',
    ar: 'لا توجد مدخلات كافية لحساب البصمة الكربونية للعملية',
    retryable: false,
  },
  [ERROR_CODES.CARBON_INVALID_FACTOR]: {
    code: ERROR_CODES.CARBON_INVALID_FACTOR,
    httpStatus: 500,
    en: 'Invalid emission factor configuration',
    ar: 'تهيئة معامل الانبعاث غير صالحة',
    retryable: false,
  },

  // ── Irrigation Service (I1xxx) ─────────────────────────────────────
  [ERROR_CODES.IRRIGATION_FIELD_NOT_FOUND]: {
    code: ERROR_CODES.IRRIGATION_FIELD_NOT_FOUND,
    httpStatus: 404,
    en: 'Field not found for irrigation scheduling',
    ar: 'الحقل غير موجود لجدولة الري',
    retryable: false,
  },
  [ERROR_CODES.IRRIGATION_SCHEDULE_NOT_FOUND]: {
    code: ERROR_CODES.IRRIGATION_SCHEDULE_NOT_FOUND,
    httpStatus: 404,
    en: 'Irrigation schedule not found',
    ar: 'جدول الري غير موجود',
    retryable: false,
  },
  [ERROR_CODES.IRRIGATION_INVALID_WATER_VOLUME]: {
    code: ERROR_CODES.IRRIGATION_INVALID_WATER_VOLUME,
    httpStatus: 400,
    en: 'Invalid water volume - must be a positive value',
    ar: 'حجم المياه غير صالح - يجب أن يكون قيمة موجبة',
    retryable: false,
  },
  [ERROR_CODES.IRRIGATION_SENSOR_DATA_INVALID]: {
    code: ERROR_CODES.IRRIGATION_SENSOR_DATA_INVALID,
    httpStatus: 400,
    en: 'Soil moisture sensor data is invalid or out of range',
    ar: 'بيانات مستشعر رطوبة التربة غير صالحة أو خارج النطاق',
    retryable: false,
  },
  [ERROR_CODES.IRRIGATION_CALCULATION_ERROR]: {
    code: ERROR_CODES.IRRIGATION_CALCULATION_ERROR,
    httpStatus: 500,
    en: 'Irrigation calculation failed - please try again',
    ar: 'فشل حساب الري - يرجى المحاولة مرة أخرى',
    retryable: true,
  },
  [ERROR_CODES.IRRIGATION_METHOD_NOT_SUPPORTED]: {
    code: ERROR_CODES.IRRIGATION_METHOD_NOT_SUPPORTED,
    httpStatus: 400,
    en: 'Irrigation method is not supported for this field configuration',
    ar: 'طريقة الري غير مدعومة لتكوين هذا الحقل',
    retryable: false,
  },
  [ERROR_CODES.IRRIGATION_CROP_NOT_FOUND]: {
    code: ERROR_CODES.IRRIGATION_CROP_NOT_FOUND,
    httpStatus: 404,
    en: 'Crop not found for irrigation water requirement calculation',
    ar: 'المحصول غير موجود لحساب الاحتياج المائي للري',
    retryable: false,
  },
  [ERROR_CODES.IRRIGATION_EFFICIENCY_OUT_OF_RANGE]: {
    code: ERROR_CODES.IRRIGATION_EFFICIENCY_OUT_OF_RANGE,
    httpStatus: 400,
    en: 'Irrigation efficiency must be between 0 and 100 percent',
    ar: 'كفاءة الري يجب أن تكون بين 0 و100 بالمائة',
    retryable: false,
  },

  // ── Notification Service (N1xxx) ───────────────────────────────────
  [ERROR_CODES.NOTIFICATION_NOT_FOUND]: {
    code: ERROR_CODES.NOTIFICATION_NOT_FOUND,
    httpStatus: 404,
    en: 'Notification not found',
    ar: 'الإشعار غير موجود',
    retryable: false,
  },
  [ERROR_CODES.NOTIFICATION_DELIVERY_FAILED]: {
    code: ERROR_CODES.NOTIFICATION_DELIVERY_FAILED,
    httpStatus: 502,
    en: 'Notification delivery failed',
    ar: 'فشل تسليم الإشعار',
    retryable: true,
  },
  [ERROR_CODES.NOTIFICATION_DEVICE_NOT_REGISTERED]: {
    code: ERROR_CODES.NOTIFICATION_DEVICE_NOT_REGISTERED,
    httpStatus: 404,
    en: 'Device is not registered for push notifications',
    ar: 'الجهاز غير مسجل لتلقي الإشعارات الفورية',
    retryable: false,
  },
  [ERROR_CODES.NOTIFICATION_INVALID_CHANNEL]: {
    code: ERROR_CODES.NOTIFICATION_INVALID_CHANNEL,
    httpStatus: 400,
    en: 'Invalid notification channel specified',
    ar: 'قناة الإشعار المحددة غير صالحة',
    retryable: false,
  },
  [ERROR_CODES.NOTIFICATION_TEMPLATE_NOT_FOUND]: {
    code: ERROR_CODES.NOTIFICATION_TEMPLATE_NOT_FOUND,
    httpStatus: 404,
    en: 'Notification template not found',
    ar: 'قالب الإشعار غير موجود',
    retryable: false,
  },
  [ERROR_CODES.NOTIFICATION_RATE_LIMITED]: {
    code: ERROR_CODES.NOTIFICATION_RATE_LIMITED,
    httpStatus: 429,
    en: 'Notification rate limit exceeded. Please wait.',
    ar: 'تم تجاوز حد معدل الإشعارات. يرجى الانتظار.',
    retryable: true,
  },
  [ERROR_CODES.NOTIFICATION_PREFERENCES_NOT_FOUND]: {
    code: ERROR_CODES.NOTIFICATION_PREFERENCES_NOT_FOUND,
    httpStatus: 404,
    en: 'Notification preferences not found for this user',
    ar: 'تفضيلات الإشعارات غير موجودة لهذا المستخدم',
    retryable: false,
  },
  [ERROR_CODES.NOTIFICATION_BROADCAST_FAILED]: {
    code: ERROR_CODES.NOTIFICATION_BROADCAST_FAILED,
    httpStatus: 500,
    en: 'Broadcast notification failed to send',
    ar: 'فشل إرسال الإشعار الجماعي',
    retryable: true,
  },

  // ── Advisory Service (A1xxx) ───────────────────────────────────────
  [ERROR_CODES.ADVISORY_NOT_FOUND]: {
    code: ERROR_CODES.ADVISORY_NOT_FOUND,
    httpStatus: 404,
    en: 'Advisory recommendation not found',
    ar: 'التوصية الاستشارية غير موجودة',
    retryable: false,
  },
  [ERROR_CODES.ADVISORY_CROP_NOT_SUPPORTED]: {
    code: ERROR_CODES.ADVISORY_CROP_NOT_SUPPORTED,
    httpStatus: 400,
    en: 'Crop type is not supported by the advisory engine',
    ar: 'نوع المحصول غير مدعوم من محرك الاستشارات',
    retryable: false,
  },
  [ERROR_CODES.ADVISORY_SOIL_DATA_MISSING]: {
    code: ERROR_CODES.ADVISORY_SOIL_DATA_MISSING,
    httpStatus: 422,
    en: 'Soil data is missing or incomplete for advisory generation',
    ar: 'بيانات التربة مفقودة أو غير مكتملة لإنشاء الاستشارة',
    retryable: false,
  },
  [ERROR_CODES.ADVISORY_RECOMMENDATION_FAILED]: {
    code: ERROR_CODES.ADVISORY_RECOMMENDATION_FAILED,
    httpStatus: 500,
    en: 'Failed to generate advisory recommendation',
    ar: 'فشل إنشاء التوصية الاستشارية',
    retryable: true,
  },
  [ERROR_CODES.ADVISORY_FERTILIZER_CALC_ERROR]: {
    code: ERROR_CODES.ADVISORY_FERTILIZER_CALC_ERROR,
    httpStatus: 500,
    en: 'Fertilizer calculation error - please verify soil test data',
    ar: 'خطأ في حساب الأسمدة - يرجى التحقق من بيانات فحص التربة',
    retryable: true,
  },
  [ERROR_CODES.ADVISORY_KNOWLEDGE_BASE_ERROR]: {
    code: ERROR_CODES.ADVISORY_KNOWLEDGE_BASE_ERROR,
    httpStatus: 503,
    en: 'Agricultural knowledge base is currently unavailable',
    ar: 'قاعدة المعرفة الزراعية غير متاحة حالياً',
    retryable: true,
  },
  [ERROR_CODES.ADVISORY_WEATHER_DATA_UNAVAILABLE]: {
    code: ERROR_CODES.ADVISORY_WEATHER_DATA_UNAVAILABLE,
    httpStatus: 503,
    en: 'Weather data required for advisory is unavailable',
    ar: 'بيانات الطقس المطلوبة للاستشارة غير متاحة',
    retryable: true,
  },
  [ERROR_CODES.ADVISORY_RATE_LIMITED]: {
    code: ERROR_CODES.ADVISORY_RATE_LIMITED,
    httpStatus: 429,
    en: 'Advisory service rate limit exceeded. Please wait.',
    ar: 'تم تجاوز حد معدل خدمة الاستشارات. يرجى الانتظار.',
    retryable: true,
  },

  // ── User Service (U1xxx) ────────────────────────────────────────────
  [ERROR_CODES.USER_NOT_FOUND]: {
    code: ERROR_CODES.USER_NOT_FOUND,
    httpStatus: 404,
    en: 'User not found',
    ar: 'المستخدم غير موجود',
    retryable: false,
  },
  [ERROR_CODES.USER_EMAIL_EXISTS]: {
    code: ERROR_CODES.USER_EMAIL_EXISTS,
    httpStatus: 409,
    en: 'A user with this email already exists',
    ar: 'يوجد مستخدم بهذا البريد الإلكتروني بالفعل',
    retryable: false,
  },
  [ERROR_CODES.USER_PHONE_EXISTS]: {
    code: ERROR_CODES.USER_PHONE_EXISTS,
    httpStatus: 409,
    en: 'A user with this phone number already exists',
    ar: 'يوجد مستخدم برقم الهاتف هذا بالفعل',
    retryable: false,
  },
  [ERROR_CODES.USER_INVALID_CREDENTIALS]: {
    code: ERROR_CODES.USER_INVALID_CREDENTIALS,
    httpStatus: 401,
    en: 'Invalid email or password',
    ar: 'البريد الإلكتروني أو كلمة المرور غير صحيحة',
    retryable: false,
  },
  [ERROR_CODES.USER_ACCOUNT_LOCKED]: {
    code: ERROR_CODES.USER_ACCOUNT_LOCKED,
    httpStatus: 403,
    en: 'Account is locked due to too many failed login attempts',
    ar: 'تم قفل الحساب بسبب محاولات تسجيل دخول فاشلة كثيرة',
    retryable: false,
  },
  [ERROR_CODES.USER_OTP_EXPIRED]: {
    code: ERROR_CODES.USER_OTP_EXPIRED,
    httpStatus: 401,
    en: 'OTP has expired. Please request a new one.',
    ar: 'انتهت صلاحية رمز التحقق. يرجى طلب رمز جديد.',
    retryable: false,
  },
  [ERROR_CODES.USER_OTP_INVALID]: {
    code: ERROR_CODES.USER_OTP_INVALID,
    httpStatus: 401,
    en: 'Invalid OTP code',
    ar: 'رمز التحقق غير صالح',
    retryable: false,
  },
  [ERROR_CODES.USER_TOKEN_EXPIRED]: {
    code: ERROR_CODES.USER_TOKEN_EXPIRED,
    httpStatus: 401,
    en: 'User token has expired. Please login again.',
    ar: 'انتهت صلاحية رمز المستخدم. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  },
  [ERROR_CODES.USER_2FA_REQUIRED]: {
    code: ERROR_CODES.USER_2FA_REQUIRED,
    httpStatus: 403,
    en: 'Two-factor authentication is required',
    ar: 'المصادقة الثنائية مطلوبة',
    retryable: false,
  },
  [ERROR_CODES.USER_PASSWORD_TOO_WEAK]: {
    code: ERROR_CODES.USER_PASSWORD_TOO_WEAK,
    httpStatus: 400,
    en: 'Password does not meet security requirements',
    ar: 'كلمة المرور لا تستوفي متطلبات الأمان',
    retryable: false,
  },

  // ── Billing Service (B1xxx) ────────────────────────────────────────
  [ERROR_CODES.BILLING_SUBSCRIPTION_NOT_FOUND]: {
    code: ERROR_CODES.BILLING_SUBSCRIPTION_NOT_FOUND,
    httpStatus: 404,
    en: 'Subscription not found',
    ar: 'الاشتراك غير موجود',
    retryable: false,
  },
  [ERROR_CODES.BILLING_PLAN_NOT_FOUND]: {
    code: ERROR_CODES.BILLING_PLAN_NOT_FOUND,
    httpStatus: 404,
    en: 'Billing plan not found',
    ar: 'خطة الفوترة غير موجودة',
    retryable: false,
  },
  [ERROR_CODES.BILLING_PAYMENT_FAILED]: {
    code: ERROR_CODES.BILLING_PAYMENT_FAILED,
    httpStatus: 402,
    en: 'Payment processing failed',
    ar: 'فشلت معالجة الدفع',
    retryable: true,
  },
  [ERROR_CODES.BILLING_INVOICE_NOT_FOUND]: {
    code: ERROR_CODES.BILLING_INVOICE_NOT_FOUND,
    httpStatus: 404,
    en: 'Invoice not found',
    ar: 'الفاتورة غير موجودة',
    retryable: false,
  },
  [ERROR_CODES.BILLING_QUOTA_EXCEEDED]: {
    code: ERROR_CODES.BILLING_QUOTA_EXCEEDED,
    httpStatus: 429,
    en: 'Billing quota exceeded. Please upgrade your plan.',
    ar: 'تم تجاوز حصة الفوترة. يرجى ترقية خطتك.',
    retryable: false,
  },
  [ERROR_CODES.BILLING_INVALID_PLAN_CHANGE]: {
    code: ERROR_CODES.BILLING_INVALID_PLAN_CHANGE,
    httpStatus: 400,
    en: 'Invalid plan change - cannot downgrade with active features',
    ar: 'تغيير الخطة غير صالح - لا يمكن التخفيض مع وجود ميزات نشطة',
    retryable: false,
  },

  // ── Virtual Sensors Service (S1xxx) ────────────────────────────────
  [ERROR_CODES.SENSOR_CALCULATION_ERROR]: {
    code: ERROR_CODES.SENSOR_CALCULATION_ERROR,
    httpStatus: 500,
    en: 'Virtual sensor calculation failed',
    ar: 'فشل حساب المستشعر الافتراضي',
    retryable: true,
  },
  [ERROR_CODES.SENSOR_INVALID_INPUT]: {
    code: ERROR_CODES.SENSOR_INVALID_INPUT,
    httpStatus: 400,
    en: 'Invalid input data for virtual sensor',
    ar: 'بيانات إدخال غير صالحة للمستشعر الافتراضي',
    retryable: false,
  },
  [ERROR_CODES.SENSOR_CALIBRATION_FAILED]: {
    code: ERROR_CODES.SENSOR_CALIBRATION_FAILED,
    httpStatus: 500,
    en: 'Sensor calibration failed',
    ar: 'فشلت معايرة المستشعر',
    retryable: true,
  },
  [ERROR_CODES.SENSOR_DATA_OUT_OF_RANGE]: {
    code: ERROR_CODES.SENSOR_DATA_OUT_OF_RANGE,
    httpStatus: 400,
    en: 'Sensor data is outside the acceptable range',
    ar: 'بيانات المستشعر خارج النطاق المقبول',
    retryable: false,
  },

  // ── Vegetation & NDVI Service (V1xxx) ──────────────────────────────
  [ERROR_CODES.VEGETATION_FIELD_NOT_FOUND]: {
    code: ERROR_CODES.VEGETATION_FIELD_NOT_FOUND,
    httpStatus: 404,
    en: 'Field not found for vegetation analysis',
    ar: 'الحقل غير موجود لتحليل الغطاء النباتي',
    retryable: false,
  },
  [ERROR_CODES.VEGETATION_NDVI_DATA_UNAVAILABLE]: {
    code: ERROR_CODES.VEGETATION_NDVI_DATA_UNAVAILABLE,
    httpStatus: 503,
    en: 'NDVI data is currently unavailable for this field',
    ar: 'بيانات مؤشر الغطاء النباتي غير متاحة حالياً لهذا الحقل',
    retryable: true,
  },
  [ERROR_CODES.VEGETATION_SATELLITE_ERROR]: {
    code: ERROR_CODES.VEGETATION_SATELLITE_ERROR,
    httpStatus: 502,
    en: 'Satellite imagery provider returned an error',
    ar: 'أرجع مزود صور الأقمار الصناعية خطأ',
    retryable: true,
  },
  [ERROR_CODES.VEGETATION_CLOUD_COVER_HIGH]: {
    code: ERROR_CODES.VEGETATION_CLOUD_COVER_HIGH,
    httpStatus: 422,
    en: 'Cloud cover is too high for reliable NDVI analysis',
    ar: 'الغطاء السحابي مرتفع جداً لتحليل موثوق لمؤشر الغطاء النباتي',
    retryable: true,
  },
  [ERROR_CODES.VEGETATION_INVALID_DATE_RANGE]: {
    code: ERROR_CODES.VEGETATION_INVALID_DATE_RANGE,
    httpStatus: 400,
    en: 'Invalid date range for vegetation analysis',
    ar: 'نطاق التاريخ غير صالح لتحليل الغطاء النباتي',
    retryable: false,
  },
  [ERROR_CODES.VEGETATION_ANOMALY_DETECTION_FAILED]: {
    code: ERROR_CODES.VEGETATION_ANOMALY_DETECTION_FAILED,
    httpStatus: 500,
    en: 'Vegetation anomaly detection failed',
    ar: 'فشل اكتشاف شذوذ الغطاء النباتي',
    retryable: true,
  },
  [ERROR_CODES.VEGETATION_INDICATOR_NOT_FOUND]: {
    code: ERROR_CODES.VEGETATION_INDICATOR_NOT_FOUND,
    httpStatus: 404,
    en: 'Vegetation indicator not found',
    ar: 'مؤشر الغطاء النباتي غير موجود',
    retryable: false,
  },
  [ERROR_CODES.VEGETATION_INDICATOR_VALUE_INVALID]: {
    code: ERROR_CODES.VEGETATION_INDICATOR_VALUE_INVALID,
    httpStatus: 400,
    en: 'Vegetation indicator value is out of valid range',
    ar: 'قيمة مؤشر الغطاء النباتي خارج النطاق الصالح',
    retryable: false,
  },

  // ── Vision Service (E1xxx-E8xxx) ──────────────────────────────────────
  [ERROR_CODES.VISION_INVALID_FORMAT]: {
    code: ERROR_CODES.VISION_INVALID_FORMAT,
    httpStatus: 400,
    en: 'Invalid image format. Supported: JPEG, PNG, WebP, BMP, TIFF',
    ar: 'تنسيق الصورة غير صالح. المدعوم: JPEG، PNG، WebP، BMP، TIFF',
    retryable: false,
  },
  [ERROR_CODES.VISION_FILE_TOO_LARGE]: {
    code: ERROR_CODES.VISION_FILE_TOO_LARGE,
    httpStatus: 400,
    en: 'Image file too large. Maximum size: 50MB',
    ar: 'حجم ملف الصورة كبير جداً. الحد الأقصى: 50 ميجابايت',
    retryable: false,
  },
  [ERROR_CODES.VISION_INVALID_CONFIDENCE]: {
    code: ERROR_CODES.VISION_INVALID_CONFIDENCE,
    httpStatus: 400,
    en: 'Confidence threshold must be between 0 and 1',
    ar: 'عتبة الثقة يجب أن تكون بين 0 و1',
    retryable: false,
  },
  [ERROR_CODES.VISION_INVALID_MODEL_VARIANT]: {
    code: ERROR_CODES.VISION_INVALID_MODEL_VARIANT,
    httpStatus: 400,
    en: 'Invalid model variant. Valid options: n, s, m, l, x',
    ar: 'نوع النموذج غير صالح. الخيارات الصالحة: n، s، m، l، x',
    retryable: false,
  },
  [ERROR_CODES.VISION_MISSING_REQUIRED_FIELD]: {
    code: ERROR_CODES.VISION_MISSING_REQUIRED_FIELD,
    httpStatus: 400,
    en: 'A required field is missing in the vision request',
    ar: 'حقل مطلوب مفقود في طلب الرؤية',
    retryable: false,
  },
  [ERROR_CODES.VISION_INVALID_BOUNDING_BOX]: {
    code: ERROR_CODES.VISION_INVALID_BOUNDING_BOX,
    httpStatus: 400,
    en: 'Invalid bounding box coordinates',
    ar: 'إحداثيات المربع المحيط غير صالحة',
    retryable: false,
  },
  [ERROR_CODES.VISION_MODEL_NOT_FOUND]: {
    code: ERROR_CODES.VISION_MODEL_NOT_FOUND,
    httpStatus: 503,
    en: 'Vision model not found or not loaded',
    ar: 'نموذج الرؤية غير موجود أو غير محمل',
    retryable: false,
  },
  [ERROR_CODES.VISION_MODEL_LOAD_FAILED]: {
    code: ERROR_CODES.VISION_MODEL_LOAD_FAILED,
    httpStatus: 503,
    en: 'Failed to load vision model',
    ar: 'فشل تحميل نموذج الرؤية',
    retryable: true,
  },
  [ERROR_CODES.VISION_INFERENCE_FAILED]: {
    code: ERROR_CODES.VISION_INFERENCE_FAILED,
    httpStatus: 503,
    en: 'Vision inference failed - please try again',
    ar: 'فشل استدلال الرؤية - يرجى المحاولة مرة أخرى',
    retryable: true,
  },
  [ERROR_CODES.VISION_MODEL_VERSION_NOT_FOUND]: {
    code: ERROR_CODES.VISION_MODEL_VERSION_NOT_FOUND,
    httpStatus: 503,
    en: 'Vision model version not found',
    ar: 'إصدار نموذج الرؤية غير موجود',
    retryable: false,
  },
  [ERROR_CODES.VISION_TENSORRT_ERROR]: {
    code: ERROR_CODES.VISION_TENSORRT_ERROR,
    httpStatus: 503,
    en: 'TensorRT optimization error in vision service',
    ar: 'خطأ في تحسين TensorRT في خدمة الرؤية',
    retryable: true,
  },
  [ERROR_CODES.VISION_IMAGE_DECODE]: {
    code: ERROR_CODES.VISION_IMAGE_DECODE,
    httpStatus: 400,
    en: 'Failed to decode image. The image may be corrupted.',
    ar: 'فشل فك ترميز الصورة. قد تكون الصورة تالفة.',
    retryable: false,
  },
  [ERROR_CODES.VISION_PREPROCESSING_FAILED]: {
    code: ERROR_CODES.VISION_PREPROCESSING_FAILED,
    httpStatus: 400,
    en: 'Image preprocessing failed',
    ar: 'فشلت المعالجة المسبقة للصورة',
    retryable: false,
  },
  [ERROR_CODES.VISION_POSTPROCESSING_FAILED]: {
    code: ERROR_CODES.VISION_POSTPROCESSING_FAILED,
    httpStatus: 500,
    en: 'Result postprocessing failed - please try again',
    ar: 'فشلت معالجة النتائج اللاحقة - يرجى المحاولة مرة أخرى',
    retryable: true,
  },
  [ERROR_CODES.VISION_BATCH_PROCESSING_FAILED]: {
    code: ERROR_CODES.VISION_BATCH_PROCESSING_FAILED,
    httpStatus: 400,
    en: 'Batch image processing failed',
    ar: 'فشلت معالجة دفعة الصور',
    retryable: true,
  },
  [ERROR_CODES.VISION_GPU_OOM]: {
    code: ERROR_CODES.VISION_GPU_OOM,
    httpStatus: 503,
    en: 'GPU out of memory. Try a smaller image or retry later.',
    ar: 'نفدت ذاكرة وحدة معالجة الرسومات. جرب صورة أصغر أو أعد المحاولة لاحقاً.',
    retryable: true,
  },
  [ERROR_CODES.VISION_CPU_OOM]: {
    code: ERROR_CODES.VISION_CPU_OOM,
    httpStatus: 503,
    en: 'System out of memory. Please retry later.',
    ar: 'نفدت ذاكرة النظام. يرجى المحاولة لاحقاً.',
    retryable: true,
  },
  [ERROR_CODES.VISION_DISK_SPACE_LOW]: {
    code: ERROR_CODES.VISION_DISK_SPACE_LOW,
    httpStatus: 503,
    en: 'Low disk space - vision service temporarily unavailable',
    ar: 'مساحة القرص منخفضة - خدمة الرؤية غير متاحة مؤقتاً',
    retryable: true,
  },
  [ERROR_CODES.VISION_MAX_CONCURRENT]: {
    code: ERROR_CODES.VISION_MAX_CONCURRENT,
    httpStatus: 503,
    en: 'Maximum concurrent requests exceeded. Please retry later.',
    ar: 'تم تجاوز الحد الأقصى للطلبات المتزامنة. يرجى المحاولة لاحقاً.',
    retryable: true,
  },
  [ERROR_CODES.VISION_DB_ERROR]: {
    code: ERROR_CODES.VISION_DB_ERROR,
    httpStatus: 502,
    en: 'Vision service database error',
    ar: 'خطأ في قاعدة بيانات خدمة الرؤية',
    retryable: true,
  },
  [ERROR_CODES.VISION_CACHE_ERROR]: {
    code: ERROR_CODES.VISION_CACHE_ERROR,
    httpStatus: 502,
    en: 'Vision service cache error',
    ar: 'خطأ في ذاكرة التخزين المؤقت لخدمة الرؤية',
    retryable: true,
  },
  [ERROR_CODES.VISION_NATS_ERROR]: {
    code: ERROR_CODES.VISION_NATS_ERROR,
    httpStatus: 502,
    en: 'Vision service message queue error',
    ar: 'خطأ في قائمة رسائل خدمة الرؤية',
    retryable: true,
  },
  [ERROR_CODES.VISION_RATE_EXCEEDED]: {
    code: ERROR_CODES.VISION_RATE_EXCEEDED,
    httpStatus: 429,
    en: 'Vision API rate limit exceeded. Please wait before retrying.',
    ar: 'تم تجاوز حد معدل واجهة برمجة الرؤية. يرجى الانتظار قبل إعادة المحاولة.',
    retryable: true,
  },
  [ERROR_CODES.VISION_QUOTA_EXCEEDED]: {
    code: ERROR_CODES.VISION_QUOTA_EXCEEDED,
    httpStatus: 429,
    en: 'Vision API quota exceeded for this billing period',
    ar: 'تم تجاوز حصة واجهة برمجة الرؤية لفترة الفوترة هذه',
    retryable: false,
  },
  [ERROR_CODES.VISION_INFERENCE_TIMEOUT]: {
    code: ERROR_CODES.VISION_INFERENCE_TIMEOUT,
    httpStatus: 504,
    en: 'Vision inference timed out. Please try again.',
    ar: 'انتهت مهلة استدلال الرؤية. يرجى المحاولة مرة أخرى.',
    retryable: true,
  },
  [ERROR_CODES.VISION_REQUEST_TIMEOUT]: {
    code: ERROR_CODES.VISION_REQUEST_TIMEOUT,
    httpStatus: 504,
    en: 'Vision request timed out',
    ar: 'انتهت مهلة طلب الرؤية',
    retryable: true,
  },
  [ERROR_CODES.VISION_AUTH_INVALID_TOKEN]: {
    code: ERROR_CODES.VISION_AUTH_INVALID_TOKEN,
    httpStatus: 401,
    en: 'Invalid authentication token for vision service',
    ar: 'رمز مصادقة غير صالح لخدمة الرؤية',
    retryable: false,
  },
  [ERROR_CODES.VISION_AUTH_TOKEN_EXPIRED]: {
    code: ERROR_CODES.VISION_AUTH_TOKEN_EXPIRED,
    httpStatus: 401,
    en: 'Authentication token has expired. Please login again.',
    ar: 'انتهت صلاحية رمز المصادقة. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  },
  [ERROR_CODES.VISION_PERMISSION_DENIED]: {
    code: ERROR_CODES.VISION_PERMISSION_DENIED,
    httpStatus: 401,
    en: 'Permission denied for this vision operation',
    ar: 'تم رفض الإذن لهذه العملية في خدمة الرؤية',
    retryable: false,
  },

  // ── Generic ──────────────────────────────────────────────────────────
  [ERROR_CODES.UNKNOWN]: {
    code: ERROR_CODES.UNKNOWN,
    httpStatus: 0,
    en: 'An unexpected error occurred',
    ar: 'حدث خطأ غير متوقع',
    retryable: false,
  },
};

// ---------------------------------------------------------------------------
// Helper Functions - دوال مساعدة
// ---------------------------------------------------------------------------

/**
 * Get the ErrorMessage for a given code.
 */
export function getErrorMessage(code: string): ErrorMessage {
  return ERROR_MESSAGES[code] ?? ERROR_MESSAGES[ERROR_CODES.UNKNOWN]!;
}

/**
 * Get localized error text.
 */
export function getLocalizedError(code: string, locale: 'ar' | 'en' = 'ar'): string {
  const msg = getErrorMessage(code);
  return locale === 'ar' ? msg.ar : msg.en;
}

/**
 * Map an HTTP status code to the best matching error code.
 */
export function httpStatusToErrorCode(status: number): ErrorCode {
  if (status === 401) return ERROR_CODES.UNAUTHORIZED;
  if (status === 403) return ERROR_CODES.FORBIDDEN;
  if (status === 404) return ERROR_CODES.NOT_FOUND;
  if (status === 409) return ERROR_CODES.CONFLICT;
  if (status === 429) return ERROR_CODES.RATE_LIMITED;
  if (status === 400) return ERROR_CODES.BAD_REQUEST;
  if (status === 502) return ERROR_CODES.INVALID_RESPONSE;
  if (status === 503) return ERROR_CODES.SERVICE_UNAVAILABLE;
  if (status === 504) return ERROR_CODES.GATEWAY_TIMEOUT;
  if (status >= 500) return ERROR_CODES.SERVER_ERROR;
  return ERROR_CODES.UNKNOWN;
}

/**
 * Check if an error code is retryable.
 */
export function isRetryable(code: string): boolean {
  return getErrorMessage(code).retryable;
}
