/// SAHOOL Unified Error Codes (auto-generated)
/// DO NOT EDIT - Generated from packages/shared-types/src/contracts/error-codes.ts
/// Run: npx tsx scripts/sync-contracts-to-dart.ts
///
/// Contract version: 3.0.0
library;

/// Unified error codes used across all SAHOOL clients and services.
abstract final class ErrorCodes {
  static const String networkError = 'NETWORK_ERROR';
  static const String timeout = 'TIMEOUT';
  static const String circuitOpen = 'CIRCUIT_OPEN';
  static const String invalidResponse = 'INVALID_RESPONSE';
  static const String unauthorized = 'UNAUTHORIZED';
  static const String tokenExpired = 'TOKEN_EXPIRED';
  static const String tokenInvalid = 'TOKEN_INVALID';
  static const String sessionExpired = 'SESSION_EXPIRED';
  static const String forbidden = 'FORBIDDEN';
  static const String insufficientPermissions = 'INSUFFICIENT_PERMISSIONS';
  static const String badRequest = 'BAD_REQUEST';
  static const String validationError = 'VALIDATION_ERROR';
  static const String notFound = 'NOT_FOUND';
  static const String conflict = 'CONFLICT';
  static const String rateLimited = 'RATE_LIMITED';
  static const String serverError = 'SERVER_ERROR';
  static const String badGateway = 'BAD_GATEWAY';
  static const String serviceUnavailable = 'SERVICE_UNAVAILABLE';
  static const String gatewayTimeout = 'GATEWAY_TIMEOUT';
  static const String offline = 'OFFLINE';
  static const String syncFailed = 'SYNC_FAILED';
  static const String syncConflict = 'SYNC_CONFLICT';
  static const String certificateError = 'CERTIFICATE_ERROR';
  static const String weatherLocationNotFound = 'W1001';
  static const String weatherDataUnavailable = 'W1002';
  static const String weatherProviderError = 'W1003';
  static const String weatherApiKeyInvalid = 'W1004';
  static const String weatherForecastRangeInvalid = 'W1005';
  static const String weatherCoordinateInvalid = 'W1006';
  static const String weatherCacheError = 'W1007';
  static const String weatherRateLimited = 'W1008';
  static const String marketplaceProductNotFound = 'M1001';
  static const String marketplaceInsufficientStock = 'M1002';
  static const String marketplaceOrderNotFound = 'M1003';
  static const String marketplaceWalletNotFound = 'M1004';
  static const String marketplaceInsufficientBalance = 'M1005';
  static const String marketplaceInvalidTransaction = 'M1006';
  static const String marketplaceEscrowNotFound = 'M1007';
  static const String marketplaceLoanNotFound = 'M1008';
  static const String marketplaceDuplicateTransaction = 'M1009';
  static const String marketplacePinRequired = 'M1010';
  static const String marketplaceCreditScoreError = 'M1011';
  static const String marketplaceRateLimited = 'M1012';
  static const String fieldNotFound = 'F1001';
  static const String fieldBoundaryInvalid = 'F1002';
  static const String fieldAreaTooLarge = 'F1003';
  static const String fieldCoordinateInvalid = 'F1004';
  static const String fieldDuplicateName = 'F1005';
  static const String fieldTenantMismatch = 'F1006';
  static const String fieldCropNotSupported = 'F1007';
  static const String fieldSyncConflict = 'F1008';
  static const String fieldGeojsonInvalid = 'F1009';
  static const String fieldPostgisError = 'F1010';
  static const String irrigationFieldNotFound = 'I1001';
  static const String irrigationScheduleNotFound = 'I1002';
  static const String irrigationInvalidWaterVolume = 'I1003';
  static const String irrigationSensorDataInvalid = 'I1004';
  static const String irrigationCalculationError = 'I1005';
  static const String irrigationMethodNotSupported = 'I1006';
  static const String irrigationCropNotFound = 'I1007';
  static const String irrigationEfficiencyOutOfRange = 'I1008';
  static const String notificationNotFound = 'N1001';
  static const String notificationDeliveryFailed = 'N1002';
  static const String notificationDeviceNotRegistered = 'N1003';
  static const String notificationInvalidChannel = 'N1004';
  static const String notificationTemplateNotFound = 'N1005';
  static const String notificationRateLimited = 'N1006';
  static const String notificationPreferencesNotFound = 'N1007';
  static const String notificationBroadcastFailed = 'N1008';
  static const String advisoryNotFound = 'A1001';
  static const String advisoryCropNotSupported = 'A1002';
  static const String advisorySoilDataMissing = 'A1003';
  static const String advisoryRecommendationFailed = 'A1004';
  static const String advisoryFertilizerCalcError = 'A1005';
  static const String advisoryKnowledgeBaseError = 'A1006';
  static const String advisoryWeatherDataUnavailable = 'A1007';
  static const String advisoryRateLimited = 'A1008';
  static const String userNotFound = 'U1001';
  static const String userEmailExists = 'U1002';
  static const String userPhoneExists = 'U1003';
  static const String userInvalidCredentials = 'U1004';
  static const String userAccountLocked = 'U1005';
  static const String userOtpExpired = 'U1006';
  static const String userOtpInvalid = 'U1007';
  static const String userTokenExpired = 'U1008';
  static const String user2faRequired = 'U1009';
  static const String userPasswordTooWeak = 'U1010';
  static const String billingSubscriptionNotFound = 'B1001';
  static const String billingPlanNotFound = 'B1002';
  static const String billingPaymentFailed = 'B1003';
  static const String billingInvoiceNotFound = 'B1004';
  static const String billingQuotaExceeded = 'B1005';
  static const String billingInvalidPlanChange = 'B1006';
  static const String sensorCalculationError = 'S1001';
  static const String sensorInvalidInput = 'S1002';
  static const String sensorCalibrationFailed = 'S1003';
  static const String sensorDataOutOfRange = 'S1004';
  static const String vegetationFieldNotFound = 'V1001';
  static const String vegetationNdviDataUnavailable = 'V1002';
  static const String vegetationSatelliteError = 'V1003';
  static const String vegetationCloudCoverHigh = 'V1004';
  static const String vegetationInvalidDateRange = 'V1005';
  static const String vegetationAnomalyDetectionFailed = 'V1006';
  static const String vegetationIndicatorNotFound = 'V1007';
  static const String vegetationIndicatorValueInvalid = 'V1008';
  static const String unknown = 'UNKNOWN';

  // Vision Service (E-codes)
  static const String visionInvalidFormat = 'E1001';
  static const String visionFileTooLarge = 'E1002';
  static const String visionInvalidDimensions = 'E1003';
  static const String visionUnsupportedType = 'E1004';
  static const String visionEmptyImage = 'E1005';
  static const String visionCorruptFile = 'E1006';
  static const String visionModelNotFound = 'E2001';
  static const String visionModelLoadFailed = 'E2002';
  static const String visionInferenceFailed = 'E2003';
  static const String visionModelIncompatible = 'E2004';
  static const String visionWarmupFailed = 'E2005';
  static const String visionImageDecode = 'E3001';
  static const String visionBatchFailed = 'E3003';
  static const String visionGpuOom = 'E4001';
  static const String visionMaxConcurrent = 'E4004';
  static const String visionDbError = 'E5001';
  static const String visionCacheError = 'E5002';
  static const String visionRateExceeded = 'E6001';
  static const String visionQuotaExceeded = 'E6002';
  static const String visionInferenceTimeout = 'E7001';
  static const String visionRequestTimeout = 'E7002';
}

/// Bilingual error message.
class ErrorMessage {
  final String code;
  final int httpStatus;
  final String en;
  final String ar;
  final bool retryable;

  const ErrorMessage({
    required this.code,
    required this.httpStatus,
    required this.en,
    required this.ar,
    required this.retryable,
  });
}

/// Unified error messages (en + ar).
const Map<String, ErrorMessage> errorMessages = {
  'NETWORK_ERROR': ErrorMessage(
    code: 'NETWORK_ERROR',
    httpStatus: 0,
    en: 'Network error - please check your connection',
    ar: 'خطأ في الشبكة - يرجى التحقق من اتصالك',
    retryable: true,
  ),
  'TIMEOUT': ErrorMessage(
    code: 'TIMEOUT',
    httpStatus: 504,
    en: 'Request timed out - please try again',
    ar: 'انتهت مهلة الطلب - يرجى المحاولة مرة أخرى',
    retryable: true,
  ),
  'CIRCUIT_OPEN': ErrorMessage(
    code: 'CIRCUIT_OPEN',
    httpStatus: 503,
    en: 'Service temporarily unavailable',
    ar: 'الخدمة غير متاحة مؤقتاً',
    retryable: true,
  ),
  'INVALID_RESPONSE': ErrorMessage(
    code: 'INVALID_RESPONSE',
    httpStatus: 502,
    en: 'Invalid response from server',
    ar: 'استجابة غير صالحة من الخادم',
    retryable: false,
  ),
  'UNAUTHORIZED': ErrorMessage(
    code: 'UNAUTHORIZED',
    httpStatus: 401,
    en: 'Authentication required',
    ar: 'المصادقة مطلوبة',
    retryable: false,
  ),
  'TOKEN_EXPIRED': ErrorMessage(
    code: 'TOKEN_EXPIRED',
    httpStatus: 401,
    en: 'Session expired. Please login again.',
    ar: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  ),
  'TOKEN_INVALID': ErrorMessage(
    code: 'TOKEN_INVALID',
    httpStatus: 401,
    en: 'Invalid authentication token',
    ar: 'رمز مصادقة غير صالح',
    retryable: false,
  ),
  'SESSION_EXPIRED': ErrorMessage(
    code: 'SESSION_EXPIRED',
    httpStatus: 401,
    en: 'Session expired. Please login again.',
    ar: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  ),
  'FORBIDDEN': ErrorMessage(
    code: 'FORBIDDEN',
    httpStatus: 403,
    en: 'Access denied - insufficient permissions',
    ar: 'الوصول مرفوض - صلاحيات غير كافية',
    retryable: false,
  ),
  'INSUFFICIENT_PERMISSIONS': ErrorMessage(
    code: 'INSUFFICIENT_PERMISSIONS',
    httpStatus: 403,
    en: 'You do not have permission to perform this action',
    ar: 'ليس لديك صلاحية لتنفيذ هذا الإجراء',
    retryable: false,
  ),
  'BAD_REQUEST': ErrorMessage(
    code: 'BAD_REQUEST',
    httpStatus: 400,
    en: 'Invalid request',
    ar: 'طلب غير صالح',
    retryable: false,
  ),
  'VALIDATION_ERROR': ErrorMessage(
    code: 'VALIDATION_ERROR',
    httpStatus: 400,
    en: 'Validation error - please check your input',
    ar: 'خطأ في التحقق - يرجى مراجعة المدخلات',
    retryable: false,
  ),
  'NOT_FOUND': ErrorMessage(
    code: 'NOT_FOUND',
    httpStatus: 404,
    en: 'Resource not found',
    ar: 'المورد غير موجود',
    retryable: false,
  ),
  'CONFLICT': ErrorMessage(
    code: 'CONFLICT',
    httpStatus: 409,
    en: 'Conflict - resource was modified by another request',
    ar: 'تعارض - تم تعديل المورد بواسطة طلب آخر',
    retryable: false,
  ),
  'RATE_LIMITED': ErrorMessage(
    code: 'RATE_LIMITED',
    httpStatus: 429,
    en: 'Too many requests. Please wait.',
    ar: 'طلبات كثيرة جداً. يرجى الانتظار.',
    retryable: true,
  ),
  'SERVER_ERROR': ErrorMessage(
    code: 'SERVER_ERROR',
    httpStatus: 500,
    en: 'Server error - please try again later',
    ar: 'خطأ في الخادم - يرجى المحاولة لاحقاً',
    retryable: true,
  ),
  'BAD_GATEWAY': ErrorMessage(
    code: 'BAD_GATEWAY',
    httpStatus: 502,
    en: 'Bad gateway - upstream service error',
    ar: 'خطأ في البوابة - خطأ في الخدمة الأصلية',
    retryable: true,
  ),
  'SERVICE_UNAVAILABLE': ErrorMessage(
    code: 'SERVICE_UNAVAILABLE',
    httpStatus: 503,
    en: 'Service temporarily unavailable',
    ar: 'الخدمة غير متاحة مؤقتاً',
    retryable: true,
  ),
  'GATEWAY_TIMEOUT': ErrorMessage(
    code: 'GATEWAY_TIMEOUT',
    httpStatus: 504,
    en: 'Gateway timeout - please try again',
    ar: 'انتهت مهلة البوابة - يرجى المحاولة مرة أخرى',
    retryable: true,
  ),
  'OFFLINE': ErrorMessage(
    code: 'OFFLINE',
    httpStatus: 0,
    en: 'You are offline. Changes will sync when connected.',
    ar: 'أنت غير متصل. سيتم مزامنة التغييرات عند الاتصال.',
    retryable: true,
  ),
  'SYNC_FAILED': ErrorMessage(
    code: 'SYNC_FAILED',
    httpStatus: 0,
    en: 'Sync failed. Please try again.',
    ar: 'فشلت المزامنة. يرجى المحاولة مرة أخرى.',
    retryable: true,
  ),
  'SYNC_CONFLICT': ErrorMessage(
    code: 'SYNC_CONFLICT',
    httpStatus: 409,
    en: 'Sync conflict detected. Please resolve manually.',
    ar: 'تم اكتشاف تعارض في المزامنة. يرجى الحل يدوياً.',
    retryable: false,
  ),
  'CERTIFICATE_ERROR': ErrorMessage(
    code: 'CERTIFICATE_ERROR',
    httpStatus: 0,
    en: 'Security certificate error',
    ar: 'خطأ في شهادة الأمان',
    retryable: false,
  ),
  'W1001': ErrorMessage(
    code: 'W1001',
    httpStatus: 404,
    en: 'Weather location not found',
    ar: 'موقع الطقس غير موجود',
    retryable: false,
  ),
  'W1002': ErrorMessage(
    code: 'W1002',
    httpStatus: 503,
    en: 'Weather data is currently unavailable',
    ar: 'بيانات الطقس غير متاحة حالياً',
    retryable: true,
  ),
  'W1003': ErrorMessage(
    code: 'W1003',
    httpStatus: 502,
    en: 'Weather provider returned an error',
    ar: 'أرجع مزود الطقس خطأ',
    retryable: true,
  ),
  'W1004': ErrorMessage(
    code: 'W1004',
    httpStatus: 401,
    en: 'Invalid weather API key',
    ar: 'مفتاح واجهة برمجة الطقس غير صالح',
    retryable: false,
  ),
  'W1005': ErrorMessage(
    code: 'W1005',
    httpStatus: 400,
    en: 'Invalid forecast date range',
    ar: 'نطاق تاريخ التنبؤ غير صالح',
    retryable: false,
  ),
  'W1006': ErrorMessage(
    code: 'W1006',
    httpStatus: 400,
    en: 'Invalid geographic coordinates',
    ar: 'إحداثيات جغرافية غير صالحة',
    retryable: false,
  ),
  'W1007': ErrorMessage(
    code: 'W1007',
    httpStatus: 503,
    en: 'Weather cache error',
    ar: 'خطأ في ذاكرة التخزين المؤقت للطقس',
    retryable: true,
  ),
  'W1008': ErrorMessage(
    code: 'W1008',
    httpStatus: 429,
    en: 'Weather API rate limit exceeded. Please wait.',
    ar: 'تم تجاوز حد معدل واجهة برمجة الطقس. يرجى الانتظار.',
    retryable: true,
  ),
  'M1001': ErrorMessage(
    code: 'M1001',
    httpStatus: 404,
    en: 'Product not found in marketplace',
    ar: 'المنتج غير موجود في السوق',
    retryable: false,
  ),
  'M1002': ErrorMessage(
    code: 'M1002',
    httpStatus: 409,
    en: 'Insufficient stock for the requested quantity',
    ar: 'المخزون غير كافٍ للكمية المطلوبة',
    retryable: false,
  ),
  'M1003': ErrorMessage(
    code: 'M1003',
    httpStatus: 404,
    en: 'Order not found',
    ar: 'الطلب غير موجود',
    retryable: false,
  ),
  'M1004': ErrorMessage(
    code: 'M1004',
    httpStatus: 404,
    en: 'Wallet not found for the specified user',
    ar: 'المحفظة غير موجودة للمستخدم المحدد',
    retryable: false,
  ),
  'M1005': ErrorMessage(
    code: 'M1005',
    httpStatus: 402,
    en: 'Insufficient wallet balance for this transaction',
    ar: 'رصيد المحفظة غير كافٍ لهذه المعاملة',
    retryable: false,
  ),
  'M1006': ErrorMessage(
    code: 'M1006',
    httpStatus: 400,
    en: 'Invalid transaction details',
    ar: 'تفاصيل المعاملة غير صالحة',
    retryable: false,
  ),
  'M1007': ErrorMessage(
    code: 'M1007',
    httpStatus: 404,
    en: 'Escrow record not found',
    ar: 'سجل الضمان غير موجود',
    retryable: false,
  ),
  'M1008': ErrorMessage(
    code: 'M1008',
    httpStatus: 404,
    en: 'Loan record not found',
    ar: 'سجل القرض غير موجود',
    retryable: false,
  ),
  'M1009': ErrorMessage(
    code: 'M1009',
    httpStatus: 409,
    en: 'Duplicate transaction detected',
    ar: 'تم اكتشاف معاملة مكررة',
    retryable: false,
  ),
  'M1010': ErrorMessage(
    code: 'M1010',
    httpStatus: 403,
    en: 'PIN verification required to complete this transaction',
    ar: 'يلزم التحقق من الرقم السري لإتمام هذه المعاملة',
    retryable: false,
  ),
  'M1011': ErrorMessage(
    code: 'M1011',
    httpStatus: 503,
    en: 'Credit score service is currently unavailable',
    ar: 'خدمة التصنيف الائتماني غير متاحة حالياً',
    retryable: true,
  ),
  'M1012': ErrorMessage(
    code: 'M1012',
    httpStatus: 429,
    en: 'Marketplace API rate limit exceeded. Please wait.',
    ar: 'تم تجاوز حد معدل واجهة برمجة السوق. يرجى الانتظار.',
    retryable: true,
  ),
  'F1001': ErrorMessage(
    code: 'F1001',
    httpStatus: 404,
    en: 'Field not found',
    ar: 'الحقل غير موجود',
    retryable: false,
  ),
  'F1002': ErrorMessage(
    code: 'F1002',
    httpStatus: 400,
    en: 'Field boundary geometry is invalid',
    ar: 'هندسة حدود الحقل غير صالحة',
    retryable: false,
  ),
  'F1003': ErrorMessage(
    code: 'F1003',
    httpStatus: 400,
    en: 'Field area exceeds maximum allowed size',
    ar: 'مساحة الحقل تتجاوز الحد الأقصى المسموح به',
    retryable: false,
  ),
  'F1004': ErrorMessage(
    code: 'F1004',
    httpStatus: 400,
    en: 'Invalid field coordinates',
    ar: 'إحداثيات الحقل غير صالحة',
    retryable: false,
  ),
  'F1005': ErrorMessage(
    code: 'F1005',
    httpStatus: 409,
    en: 'A field with this name already exists',
    ar: 'يوجد حقل بهذا الاسم بالفعل',
    retryable: false,
  ),
  'F1006': ErrorMessage(
    code: 'F1006',
    httpStatus: 403,
    en: 'Field does not belong to the current tenant',
    ar: 'الحقل لا ينتمي إلى المستأجر الحالي',
    retryable: false,
  ),
  'F1007': ErrorMessage(
    code: 'F1007',
    httpStatus: 400,
    en: 'Crop type is not supported for this field region',
    ar: 'نوع المحصول غير مدعوم لمنطقة هذا الحقل',
    retryable: false,
  ),
  'F1008': ErrorMessage(
    code: 'F1008',
    httpStatus: 409,
    en: 'Field data sync conflict detected. Please resolve manually.',
    ar: 'تم اكتشاف تعارض في مزامنة بيانات الحقل. يرجى الحل يدوياً.',
    retryable: false,
  ),
  'F1009': ErrorMessage(
    code: 'F1009',
    httpStatus: 400,
    en: 'Invalid GeoJSON format for field boundary',
    ar: 'تنسيق GeoJSON غير صالح لحدود الحقل',
    retryable: false,
  ),
  'F1010': ErrorMessage(
    code: 'F1010',
    httpStatus: 500,
    en: 'PostGIS spatial operation failed',
    ar: 'فشلت العملية المكانية في PostGIS',
    retryable: true,
  ),
  'I1001': ErrorMessage(
    code: 'I1001',
    httpStatus: 404,
    en: 'Field not found for irrigation scheduling',
    ar: 'الحقل غير موجود لجدولة الري',
    retryable: false,
  ),
  'I1002': ErrorMessage(
    code: 'I1002',
    httpStatus: 404,
    en: 'Irrigation schedule not found',
    ar: 'جدول الري غير موجود',
    retryable: false,
  ),
  'I1003': ErrorMessage(
    code: 'I1003',
    httpStatus: 400,
    en: 'Invalid water volume - must be a positive value',
    ar: 'حجم المياه غير صالح - يجب أن يكون قيمة موجبة',
    retryable: false,
  ),
  'I1004': ErrorMessage(
    code: 'I1004',
    httpStatus: 400,
    en: 'Soil moisture sensor data is invalid or out of range',
    ar: 'بيانات مستشعر رطوبة التربة غير صالحة أو خارج النطاق',
    retryable: false,
  ),
  'I1005': ErrorMessage(
    code: 'I1005',
    httpStatus: 500,
    en: 'Irrigation calculation failed - please try again',
    ar: 'فشل حساب الري - يرجى المحاولة مرة أخرى',
    retryable: true,
  ),
  'I1006': ErrorMessage(
    code: 'I1006',
    httpStatus: 400,
    en: 'Irrigation method is not supported for this field configuration',
    ar: 'طريقة الري غير مدعومة لتكوين هذا الحقل',
    retryable: false,
  ),
  'I1007': ErrorMessage(
    code: 'I1007',
    httpStatus: 404,
    en: 'Crop not found for irrigation water requirement calculation',
    ar: 'المحصول غير موجود لحساب الاحتياج المائي للري',
    retryable: false,
  ),
  'I1008': ErrorMessage(
    code: 'I1008',
    httpStatus: 400,
    en: 'Irrigation efficiency must be between 0 and 100 percent',
    ar: 'كفاءة الري يجب أن تكون بين 0 و100 بالمائة',
    retryable: false,
  ),
  'N1001': ErrorMessage(
    code: 'N1001',
    httpStatus: 404,
    en: 'Notification not found',
    ar: 'الإشعار غير موجود',
    retryable: false,
  ),
  'N1002': ErrorMessage(
    code: 'N1002',
    httpStatus: 502,
    en: 'Notification delivery failed',
    ar: 'فشل تسليم الإشعار',
    retryable: true,
  ),
  'N1003': ErrorMessage(
    code: 'N1003',
    httpStatus: 404,
    en: 'Device is not registered for push notifications',
    ar: 'الجهاز غير مسجل لتلقي الإشعارات الفورية',
    retryable: false,
  ),
  'N1004': ErrorMessage(
    code: 'N1004',
    httpStatus: 400,
    en: 'Invalid notification channel specified',
    ar: 'قناة الإشعار المحددة غير صالحة',
    retryable: false,
  ),
  'N1005': ErrorMessage(
    code: 'N1005',
    httpStatus: 404,
    en: 'Notification template not found',
    ar: 'قالب الإشعار غير موجود',
    retryable: false,
  ),
  'N1006': ErrorMessage(
    code: 'N1006',
    httpStatus: 429,
    en: 'Notification rate limit exceeded. Please wait.',
    ar: 'تم تجاوز حد معدل الإشعارات. يرجى الانتظار.',
    retryable: true,
  ),
  'N1007': ErrorMessage(
    code: 'N1007',
    httpStatus: 404,
    en: 'Notification preferences not found for this user',
    ar: 'تفضيلات الإشعارات غير موجودة لهذا المستخدم',
    retryable: false,
  ),
  'N1008': ErrorMessage(
    code: 'N1008',
    httpStatus: 500,
    en: 'Broadcast notification failed to send',
    ar: 'فشل إرسال الإشعار الجماعي',
    retryable: true,
  ),
  'A1001': ErrorMessage(
    code: 'A1001',
    httpStatus: 404,
    en: 'Advisory recommendation not found',
    ar: 'التوصية الاستشارية غير موجودة',
    retryable: false,
  ),
  'A1002': ErrorMessage(
    code: 'A1002',
    httpStatus: 400,
    en: 'Crop type is not supported by the advisory engine',
    ar: 'نوع المحصول غير مدعوم من محرك الاستشارات',
    retryable: false,
  ),
  'A1003': ErrorMessage(
    code: 'A1003',
    httpStatus: 422,
    en: 'Soil data is missing or incomplete for advisory generation',
    ar: 'بيانات التربة مفقودة أو غير مكتملة لإنشاء الاستشارة',
    retryable: false,
  ),
  'A1004': ErrorMessage(
    code: 'A1004',
    httpStatus: 500,
    en: 'Failed to generate advisory recommendation',
    ar: 'فشل إنشاء التوصية الاستشارية',
    retryable: true,
  ),
  'A1005': ErrorMessage(
    code: 'A1005',
    httpStatus: 500,
    en: 'Fertilizer calculation error - please verify soil test data',
    ar: 'خطأ في حساب الأسمدة - يرجى التحقق من بيانات فحص التربة',
    retryable: true,
  ),
  'A1006': ErrorMessage(
    code: 'A1006',
    httpStatus: 503,
    en: 'Agricultural knowledge base is currently unavailable',
    ar: 'قاعدة المعرفة الزراعية غير متاحة حالياً',
    retryable: true,
  ),
  'A1007': ErrorMessage(
    code: 'A1007',
    httpStatus: 503,
    en: 'Weather data required for advisory is unavailable',
    ar: 'بيانات الطقس المطلوبة للاستشارة غير متاحة',
    retryable: true,
  ),
  'A1008': ErrorMessage(
    code: 'A1008',
    httpStatus: 429,
    en: 'Advisory service rate limit exceeded. Please wait.',
    ar: 'تم تجاوز حد معدل خدمة الاستشارات. يرجى الانتظار.',
    retryable: true,
  ),
  'U1001': ErrorMessage(
    code: 'U1001',
    httpStatus: 404,
    en: 'User not found',
    ar: 'المستخدم غير موجود',
    retryable: false,
  ),
  'U1002': ErrorMessage(
    code: 'U1002',
    httpStatus: 409,
    en: 'A user with this email already exists',
    ar: 'يوجد مستخدم بهذا البريد الإلكتروني بالفعل',
    retryable: false,
  ),
  'U1003': ErrorMessage(
    code: 'U1003',
    httpStatus: 409,
    en: 'A user with this phone number already exists',
    ar: 'يوجد مستخدم برقم الهاتف هذا بالفعل',
    retryable: false,
  ),
  'U1004': ErrorMessage(
    code: 'U1004',
    httpStatus: 401,
    en: 'Invalid email or password',
    ar: 'البريد الإلكتروني أو كلمة المرور غير صحيحة',
    retryable: false,
  ),
  'U1005': ErrorMessage(
    code: 'U1005',
    httpStatus: 403,
    en: 'Account is locked due to too many failed login attempts',
    ar: 'تم قفل الحساب بسبب محاولات تسجيل دخول فاشلة كثيرة',
    retryable: false,
  ),
  'U1006': ErrorMessage(
    code: 'U1006',
    httpStatus: 401,
    en: 'OTP has expired. Please request a new one.',
    ar: 'انتهت صلاحية رمز التحقق. يرجى طلب رمز جديد.',
    retryable: false,
  ),
  'U1007': ErrorMessage(
    code: 'U1007',
    httpStatus: 401,
    en: 'Invalid OTP code',
    ar: 'رمز التحقق غير صالح',
    retryable: false,
  ),
  'U1008': ErrorMessage(
    code: 'U1008',
    httpStatus: 401,
    en: 'User token has expired. Please login again.',
    ar: 'انتهت صلاحية رمز المستخدم. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  ),
  'U1009': ErrorMessage(
    code: 'U1009',
    httpStatus: 403,
    en: 'Two-factor authentication is required',
    ar: 'المصادقة الثنائية مطلوبة',
    retryable: false,
  ),
  'U1010': ErrorMessage(
    code: 'U1010',
    httpStatus: 400,
    en: 'Password does not meet security requirements',
    ar: 'كلمة المرور لا تستوفي متطلبات الأمان',
    retryable: false,
  ),
  'B1001': ErrorMessage(
    code: 'B1001',
    httpStatus: 404,
    en: 'Subscription not found',
    ar: 'الاشتراك غير موجود',
    retryable: false,
  ),
  'B1002': ErrorMessage(
    code: 'B1002',
    httpStatus: 404,
    en: 'Billing plan not found',
    ar: 'خطة الفوترة غير موجودة',
    retryable: false,
  ),
  'B1003': ErrorMessage(
    code: 'B1003',
    httpStatus: 402,
    en: 'Payment processing failed',
    ar: 'فشلت معالجة الدفع',
    retryable: true,
  ),
  'B1004': ErrorMessage(
    code: 'B1004',
    httpStatus: 404,
    en: 'Invoice not found',
    ar: 'الفاتورة غير موجودة',
    retryable: false,
  ),
  'B1005': ErrorMessage(
    code: 'B1005',
    httpStatus: 429,
    en: 'Billing quota exceeded. Please upgrade your plan.',
    ar: 'تم تجاوز حصة الفوترة. يرجى ترقية خطتك.',
    retryable: false,
  ),
  'B1006': ErrorMessage(
    code: 'B1006',
    httpStatus: 400,
    en: 'Invalid plan change - cannot downgrade with active features',
    ar: 'تغيير الخطة غير صالح - لا يمكن التخفيض مع وجود ميزات نشطة',
    retryable: false,
  ),
  'S1001': ErrorMessage(
    code: 'S1001',
    httpStatus: 500,
    en: 'Virtual sensor calculation failed',
    ar: 'فشل حساب المستشعر الافتراضي',
    retryable: true,
  ),
  'S1002': ErrorMessage(
    code: 'S1002',
    httpStatus: 400,
    en: 'Invalid input data for virtual sensor',
    ar: 'بيانات إدخال غير صالحة للمستشعر الافتراضي',
    retryable: false,
  ),
  'S1003': ErrorMessage(
    code: 'S1003',
    httpStatus: 500,
    en: 'Sensor calibration failed',
    ar: 'فشلت معايرة المستشعر',
    retryable: true,
  ),
  'S1004': ErrorMessage(
    code: 'S1004',
    httpStatus: 400,
    en: 'Sensor data is outside the acceptable range',
    ar: 'بيانات المستشعر خارج النطاق المقبول',
    retryable: false,
  ),
  'V1001': ErrorMessage(
    code: 'V1001',
    httpStatus: 404,
    en: 'Field not found for vegetation analysis',
    ar: 'الحقل غير موجود لتحليل الغطاء النباتي',
    retryable: false,
  ),
  'V1002': ErrorMessage(
    code: 'V1002',
    httpStatus: 503,
    en: 'NDVI data is currently unavailable for this field',
    ar: 'بيانات مؤشر الغطاء النباتي غير متاحة حالياً لهذا الحقل',
    retryable: true,
  ),
  'V1003': ErrorMessage(
    code: 'V1003',
    httpStatus: 502,
    en: 'Satellite imagery provider returned an error',
    ar: 'أرجع مزود صور الأقمار الصناعية خطأ',
    retryable: true,
  ),
  'V1004': ErrorMessage(
    code: 'V1004',
    httpStatus: 422,
    en: 'Cloud cover is too high for reliable NDVI analysis',
    ar: 'الغطاء السحابي مرتفع جداً لتحليل موثوق لمؤشر الغطاء النباتي',
    retryable: true,
  ),
  'V1005': ErrorMessage(
    code: 'V1005',
    httpStatus: 400,
    en: 'Invalid date range for vegetation analysis',
    ar: 'نطاق التاريخ غير صالح لتحليل الغطاء النباتي',
    retryable: false,
  ),
  'V1006': ErrorMessage(
    code: 'V1006',
    httpStatus: 500,
    en: 'Vegetation anomaly detection failed',
    ar: 'فشل اكتشاف شذوذ الغطاء النباتي',
    retryable: true,
  ),
  'V1007': ErrorMessage(
    code: 'V1007',
    httpStatus: 404,
    en: 'Vegetation indicator not found',
    ar: 'مؤشر الغطاء النباتي غير موجود',
    retryable: false,
  ),
  'V1008': ErrorMessage(
    code: 'V1008',
    httpStatus: 400,
    en: 'Vegetation indicator value is out of valid range',
    ar: 'قيمة مؤشر الغطاء النباتي خارج النطاق الصالح',
    retryable: false,
  ),
  'UNKNOWN': ErrorMessage(
    code: 'UNKNOWN',
    httpStatus: 0,
    en: 'An unexpected error occurred',
    ar: 'حدث خطأ غير متوقع',
    retryable: false,
  ),
};

/// Get error message by code, with fallback to UNKNOWN.
ErrorMessage getErrorMessage(String code) =>
    errorMessages[code] ?? errorMessages[ErrorCodes.unknown]!;

/// Get localized error string.
String getLocalizedError(String code, {String locale = 'ar'}) {
  final msg = getErrorMessage(code);
  return locale == 'ar' ? msg.ar : msg.en;
}

/// Map HTTP status to error code.
String httpStatusToErrorCode(int status) => switch (status) {
      401 => ErrorCodes.unauthorized,
      403 => ErrorCodes.forbidden,
      404 => ErrorCodes.notFound,
      409 => ErrorCodes.conflict,
      429 => ErrorCodes.rateLimited,
      400 => ErrorCodes.badRequest,
      502 => ErrorCodes.invalidResponse,
      503 => ErrorCodes.serviceUnavailable,
      504 => ErrorCodes.gatewayTimeout,
      >= 500 => ErrorCodes.serverError,
      _ => ErrorCodes.unknown,
    };

/// Check if an error code is retryable.
bool isRetryable(String code) => getErrorMessage(code).retryable;
