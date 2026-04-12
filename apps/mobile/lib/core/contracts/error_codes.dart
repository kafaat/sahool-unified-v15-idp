/// SAHOOL Unified Error Codes (auto-generated)
/// DO NOT EDIT - Generated from packages/shared-types/src/contracts/error-codes.ts
/// Run: npx tsx scripts/sync-contracts-to-dart.ts
///
/// Contract version: 4.12.0
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
  static const String cropSeasonNotFound = 'F1101';
  static const String cropSeasonAlreadyEnded = 'F1102';
  static const String cropSeasonAnotherCurrentExists = 'F1103';
  static const String cropSeasonInvalidDateRange = 'F1104';
  static const String fieldOperationNotFound = 'F1201';
  static const String fieldOperationInvalidType = 'F1202';
  static const String fieldOperationInvalidDate = 'F1203';
  static const String fieldOperationDurationInvalid = 'F1204';
  static const String fieldOperationLockedByErp = 'F1205';
  static const String fieldOperationNotApproved = 'F1206';
  static const String fieldOperationRejected = 'F1207';
  static const String fieldOperationAlreadyPosted = 'F1208';
  static const String erpAdapterNotConfigured = 'F1301';
  static const String erpPostingFailed = 'F1302';
  static const String erpWebhookUnavailable = 'F1303';
  static const String erpSignatureInvalid = 'F1304';
  static const String idempotencyKeyConflict = 'F1401';
  static const String idempotencyKeyExpired = 'F1402';
  static const String subZoneNotFound = 'F1501';
  static const String subZoneInvalidPolygon = 'F1502';
  static const String subZoneOutsideField = 'F1503';
  static const String subZoneAreaTooSmall = 'F1504';
  static const String subZoneSelfIntersection = 'F1505';
  static const String reportNotFound = 'F1601';
  static const String reportNotReady = 'F1602';
  static const String reportRenderFailed = 'F1603';
  static const String reportContentUnavailable = 'F1604';
  static const String reportExpired = 'F1605';
  static const String carbonComputationFailed = 'F1701';
  static const String carbonNoComputableInputs = 'F1702';
  static const String carbonInvalidFactor = 'F1703';
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
  static const String advisoryComprehensiveDegraded = 'A1009';
  static const String advisoryComprehensiveAllSourcesDown = 'A1010';
  static const String advisoryComprehensiveTimeout = 'A1011';
  static const String loanFieldNotFound = 'L1001';
  static const String loanCropNotVerified = 'L1002';
  static const String loanAreaMismatch = 'L1003';
  static const String loanRiskTooHigh = 'L1004';
  static const String loanNdviDataUnavailable = 'L1005';
  static const String loanRequestedAmountExceedsSafe = 'L1006';
  static const String weatherGraphRenderFailed = 'W1009';
  static const String weatherGraphNotFound = 'W1010';
  static const String weatherGraphInvalidSignature = 'W1011';
  static const String weatherGraphExpired = 'W1012';
  static const String weatherGraphNoHistory = 'W1013';
  static const String traceabilityChainTampered = 'T1001';
  static const String traceabilityAnchorPersistFailed = 'T1002';
  static const String traceabilitySubscriberUnavailable = 'T1003';
  static const String geofenceNoFieldMapping = 'G1001';
  static const String geofenceEquipmentTenantMismatch = 'G1002';
  static const String geofenceAutodraftRetry = 'G1003';
  static const String geofenceAlertNotActionable = 'G1004';
  static const String reportStorageUploadFailed = 'R1001';
  static const String reportStorageCredentialsMissing = 'R1002';
  static const String reportStorageSigningFailed = 'R1003';
  static const String unknown = 'UNKNOWN';

  // Vision Service (E-codes)
  static const String visionInvalidFormat = 'E1001';
  static const String visionFileTooLarge = 'E1002';
  static const String visionInvalidDimensions = 'E1003';
  static const String visionInvalidConfidence = 'E1004';
  static const String visionUnsupportedType = 'E1005';
  static const String visionInvalidModelVariant = 'E1006';
  static const String visionEmptyImage = 'E1007';
  static const String visionMissingRequiredField = 'E1008';
  static const String visionCorruptFile = 'E1009';
  static const String visionInvalidBoundingBox = 'E1010';
  static const String visionModelNotFound = 'E2001';
  static const String visionModelLoadFailed = 'E2002';
  static const String visionInferenceFailed = 'E2003';
  static const String visionModelIncompatible = 'E2004';
  static const String visionModelVersionNotFound = 'E2005';
  static const String visionWarmupFailed = 'E2006';
  static const String visionTensorrtError = 'E2007';
  static const String visionImageDecode = 'E3001';
  static const String visionPreprocessingFailed = 'E3002';
  static const String visionPostprocessingFailed = 'E3003';
  static const String visionBatchFailed = 'E3004';
  static const String visionBatchProcessingFailed = 'E3005';
  static const String visionGpuOom = 'E4001';
  static const String visionCpuOom = 'E4002';
  static const String visionDiskSpaceLow = 'E4003';
  static const String visionMaxConcurrent = 'E4004';
  static const String visionDbError = 'E5001';
  static const String visionCacheError = 'E5002';
  static const String visionNatsError = 'E5003';
  static const String visionRateExceeded = 'E6001';
  static const String visionQuotaExceeded = 'E6002';
  static const String visionInferenceTimeout = 'E7001';
  static const String visionRequestTimeout = 'E7002';
  static const String visionAuthInvalidToken = 'E8001';
  static const String visionAuthTokenExpired = 'E8002';
  static const String visionPermissionDenied = 'E8003';
  static const String erosionEngineUnavailable = 'ER1001';
  static const String erosionInvalidSoilTexture = 'ER1002';
  static const String erosionTenantMismatch = 'ER1003';
  static const String erosionComputeFailed = 'ER1004';
  static const String erosionWindEngineUnavailable = 'ER1005';
  static const String erosionWindComputeFailed = 'ER1006';
  static const String erosionCombinedComputeFailed = 'ER1007';
  static const String erosionYemenUnknownRegion = 'ER1008';
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
  'F1101': ErrorMessage(
    code: 'F1101',
    httpStatus: 404,
    en: 'Crop season not found',
    ar: 'الموسم المحصولي غير موجود',
    retryable: false,
  ),
  'F1102': ErrorMessage(
    code: 'F1102',
    httpStatus: 400,
    en: 'Crop season is already ended',
    ar: 'الموسم المحصولي منتهٍ بالفعل',
    retryable: false,
  ),
  'F1103': ErrorMessage(
    code: 'F1103',
    httpStatus: 400,
    en: 'Another current season exists for this field - end it first',
    ar: 'يوجد موسم حالي آخر لهذا الحقل — يجب إنهاؤه أولاً',
    retryable: false,
  ),
  'F1104': ErrorMessage(
    code: 'F1104',
    httpStatus: 400,
    en: 'Invalid date range - harvest date must be after sowing date',
    ar: 'نطاق التواريخ غير صالح — تاريخ الحصاد يجب أن يكون بعد تاريخ البذار',
    retryable: false,
  ),
  'F1201': ErrorMessage(
    code: 'F1201',
    httpStatus: 404,
    en: 'Field operation not found',
    ar: 'عملية الحقل غير موجودة',
    retryable: false,
  ),
  'F1202': ErrorMessage(
    code: 'F1202',
    httpStatus: 400,
    en: 'Invalid field operation type',
    ar: 'نوع العملية غير صالح',
    retryable: false,
  ),
  'F1203': ErrorMessage(
    code: 'F1203',
    httpStatus: 400,
    en: 'Invalid operation date',
    ar: 'تاريخ العملية غير صالح',
    retryable: false,
  ),
  'F1204': ErrorMessage(
    code: 'F1204',
    httpStatus: 400,
    en: 'Invalid duration - must be a non-negative number of hours',
    ar: 'مدة العملية غير صالحة — يجب أن تكون عدداً غير سالب من الساعات',
    retryable: false,
  ),
  'F1205': ErrorMessage(
    code: 'F1205',
    httpStatus: 400,
    en: 'Operation is locked because it was posted to ERP - reverse the posting first',
    ar: 'العملية مقفلة لأنها مرحلة إلى نظام المحاسبة — يجب إلغاء الترحيل أولاً',
    retryable: false,
  ),
  'F1206': ErrorMessage(
    code: 'F1206',
    httpStatus: 400,
    en: 'Only approved operations can be posted to ERP',
    ar: 'لا يمكن ترحيل عملية غير معتمدة إلى نظام المحاسبة',
    retryable: false,
  ),
  'F1207': ErrorMessage(
    code: 'F1207',
    httpStatus: 400,
    en: 'Operation has been rejected and cannot be approved',
    ar: 'العملية مرفوضة ولا يمكن اعتمادها',
    retryable: false,
  ),
  'F1208': ErrorMessage(
    code: 'F1208',
    httpStatus: 409,
    en: 'Operation has already been posted to ERP',
    ar: 'تم ترحيل العملية مسبقاً إلى نظام المحاسبة',
    retryable: false,
  ),
  'F1301': ErrorMessage(
    code: 'F1301',
    httpStatus: 400,
    en: 'No ERP adapter is configured',
    ar: 'لا يوجد موفر ERP مفعّل حالياً',
    retryable: false,
  ),
  'F1302': ErrorMessage(
    code: 'F1302',
    httpStatus: 502,
    en: 'ERP posting failed - will be retried by the background worker',
    ar: 'فشل ترحيل العملية إلى ERP - ستتم إعادة المحاولة تلقائياً',
    retryable: true,
  ),
  'F1303': ErrorMessage(
    code: 'F1303',
    httpStatus: 502,
    en: 'External ERP webhook is unavailable',
    ar: 'نقطة الاتصال بنظام المحاسبة الخارجي غير متاحة',
    retryable: true,
  ),
  'F1304': ErrorMessage(
    code: 'F1304',
    httpStatus: 401,
    en: 'ERP webhook signature is invalid',
    ar: 'توقيع webhook غير صالح',
    retryable: false,
  ),
  'F1401': ErrorMessage(
    code: 'F1401',
    httpStatus: 409,
    en: 'Idempotency-Key conflict: same key used with a different body',
    ar: 'تعارض في مفتاح Idempotency — نفس المفتاح مع جسم مختلف',
    retryable: false,
  ),
  'F1402': ErrorMessage(
    code: 'F1402',
    httpStatus: 410,
    en: 'Idempotency-Key has expired',
    ar: 'انتهت صلاحية مفتاح Idempotency',
    retryable: false,
  ),
  'F1501': ErrorMessage(
    code: 'F1501',
    httpStatus: 404,
    en: 'Sub-zone not found',
    ar: 'المنطقة الفرعية غير موجودة',
    retryable: false,
  ),
  'F1502': ErrorMessage(
    code: 'F1502',
    httpStatus: 400,
    en: 'Sub-zone polygon geometry is invalid',
    ar: 'هندسة المنطقة الفرعية غير صالحة',
    retryable: false,
  ),
  'F1503': ErrorMessage(
    code: 'F1503',
    httpStatus: 400,
    en: 'Sub-zone boundary must lie inside the parent field',
    ar: 'يجب أن تكون حدود المنطقة الفرعية داخل حدود الحقل',
    retryable: false,
  ),
  'F1504': ErrorMessage(
    code: 'F1504',
    httpStatus: 400,
    en: 'Sub-zone area is smaller than the minimum allowed (1 m²)',
    ar: 'مساحة المنطقة الفرعية أصغر من الحد المسموح',
    retryable: false,
  ),
  'F1505': ErrorMessage(
    code: 'F1505',
    httpStatus: 400,
    en: 'Sub-zone polygon has self-intersection',
    ar: 'المنطقة الفرعية تحتوي على تقاطع ذاتي',
    retryable: false,
  ),
  'F1601': ErrorMessage(
    code: 'F1601',
    httpStatus: 404,
    en: 'Report not found',
    ar: 'التقرير غير موجود',
    retryable: false,
  ),
  'F1602': ErrorMessage(
    code: 'F1602',
    httpStatus: 400,
    en: 'Report is not ready yet — poll until status=ready',
    ar: 'التقرير غير جاهز بعد — انتظر حتى تصبح الحالة جاهز',
    retryable: true,
  ),
  'F1603': ErrorMessage(
    code: 'F1603',
    httpStatus: 500,
    en: 'Report rendering failed',
    ar: 'فشل توليد التقرير',
    retryable: true,
  ),
  'F1604': ErrorMessage(
    code: 'F1604',
    httpStatus: 404,
    en: 'Report content not available',
    ar: 'محتوى التقرير غير متوفر',
    retryable: false,
  ),
  'F1605': ErrorMessage(
    code: 'F1605',
    httpStatus: 410,
    en: 'Report URL has expired — regenerate',
    ar: 'انتهت صلاحية رابط التقرير — يرجى إعادة التوليد',
    retryable: false,
  ),
  'F1701': ErrorMessage(
    code: 'F1701',
    httpStatus: 500,
    en: 'Carbon computation failed',
    ar: 'فشل حساب البصمة الكربونية',
    retryable: true,
  ),
  'F1702': ErrorMessage(
    code: 'F1702',
    httpStatus: 400,
    en: 'Operation has no inputs suitable for carbon computation',
    ar: 'لا توجد مدخلات كافية لحساب البصمة الكربونية للعملية',
    retryable: false,
  ),
  'F1703': ErrorMessage(
    code: 'F1703',
    httpStatus: 500,
    en: 'Invalid emission factor configuration',
    ar: 'تهيئة معامل الانبعاث غير صالحة',
    retryable: false,
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
  'E1001': ErrorMessage(
    code: 'E1001',
    httpStatus: 400,
    en: 'Invalid image format. Supported: JPEG, PNG, WebP, BMP, TIFF',
    ar: 'تنسيق الصورة غير صالح. المدعوم: JPEG، PNG، WebP، BMP، TIFF',
    retryable: false,
  ),
  'E1002': ErrorMessage(
    code: 'E1002',
    httpStatus: 400,
    en: 'Image file too large. Maximum size: 50MB',
    ar: 'حجم ملف الصورة كبير جداً. الحد الأقصى: 50 ميجابايت',
    retryable: false,
  ),
  'E1004': ErrorMessage(
    code: 'E1004',
    httpStatus: 400,
    en: 'Confidence threshold must be between 0 and 1',
    ar: 'عتبة الثقة يجب أن تكون بين 0 و1',
    retryable: false,
  ),
  'E1006': ErrorMessage(
    code: 'E1006',
    httpStatus: 400,
    en: 'Invalid model variant. Valid options: n, s, m, l, x',
    ar: 'نوع النموذج غير صالح. الخيارات الصالحة: n، s، m، l، x',
    retryable: false,
  ),
  'E1008': ErrorMessage(
    code: 'E1008',
    httpStatus: 400,
    en: 'A required field is missing in the vision request',
    ar: 'حقل مطلوب مفقود في طلب الرؤية',
    retryable: false,
  ),
  'E1010': ErrorMessage(
    code: 'E1010',
    httpStatus: 400,
    en: 'Invalid bounding box coordinates',
    ar: 'إحداثيات المربع المحيط غير صالحة',
    retryable: false,
  ),
  'E2001': ErrorMessage(
    code: 'E2001',
    httpStatus: 503,
    en: 'Vision model not found or not loaded',
    ar: 'نموذج الرؤية غير موجود أو غير محمل',
    retryable: false,
  ),
  'E2002': ErrorMessage(
    code: 'E2002',
    httpStatus: 503,
    en: 'Failed to load vision model',
    ar: 'فشل تحميل نموذج الرؤية',
    retryable: true,
  ),
  'E2003': ErrorMessage(
    code: 'E2003',
    httpStatus: 503,
    en: 'Vision inference failed - please try again',
    ar: 'فشل استدلال الرؤية - يرجى المحاولة مرة أخرى',
    retryable: true,
  ),
  'E2005': ErrorMessage(
    code: 'E2005',
    httpStatus: 503,
    en: 'Vision model version not found',
    ar: 'إصدار نموذج الرؤية غير موجود',
    retryable: false,
  ),
  'E2007': ErrorMessage(
    code: 'E2007',
    httpStatus: 503,
    en: 'TensorRT optimization error in vision service',
    ar: 'خطأ في تحسين TensorRT في خدمة الرؤية',
    retryable: true,
  ),
  'E3001': ErrorMessage(
    code: 'E3001',
    httpStatus: 400,
    en: 'Failed to decode image. The image may be corrupted.',
    ar: 'فشل فك ترميز الصورة. قد تكون الصورة تالفة.',
    retryable: false,
  ),
  'E3002': ErrorMessage(
    code: 'E3002',
    httpStatus: 400,
    en: 'Image preprocessing failed',
    ar: 'فشلت المعالجة المسبقة للصورة',
    retryable: false,
  ),
  'E3003': ErrorMessage(
    code: 'E3003',
    httpStatus: 500,
    en: 'Result postprocessing failed - please try again',
    ar: 'فشلت معالجة النتائج اللاحقة - يرجى المحاولة مرة أخرى',
    retryable: true,
  ),
  'E3005': ErrorMessage(
    code: 'E3005',
    httpStatus: 400,
    en: 'Batch image processing failed',
    ar: 'فشلت معالجة دفعة الصور',
    retryable: true,
  ),
  'E4001': ErrorMessage(
    code: 'E4001',
    httpStatus: 503,
    en: 'GPU out of memory. Try a smaller image or retry later.',
    ar: 'نفدت ذاكرة وحدة معالجة الرسومات. جرب صورة أصغر أو أعد المحاولة لاحقاً.',
    retryable: true,
  ),
  'E4002': ErrorMessage(
    code: 'E4002',
    httpStatus: 503,
    en: 'System out of memory. Please retry later.',
    ar: 'نفدت ذاكرة النظام. يرجى المحاولة لاحقاً.',
    retryable: true,
  ),
  'E4003': ErrorMessage(
    code: 'E4003',
    httpStatus: 503,
    en: 'Low disk space - vision service temporarily unavailable',
    ar: 'مساحة القرص منخفضة - خدمة الرؤية غير متاحة مؤقتاً',
    retryable: true,
  ),
  'E4004': ErrorMessage(
    code: 'E4004',
    httpStatus: 503,
    en: 'Maximum concurrent requests exceeded. Please retry later.',
    ar: 'تم تجاوز الحد الأقصى للطلبات المتزامنة. يرجى المحاولة لاحقاً.',
    retryable: true,
  ),
  'E5001': ErrorMessage(
    code: 'E5001',
    httpStatus: 502,
    en: 'Vision service database error',
    ar: 'خطأ في قاعدة بيانات خدمة الرؤية',
    retryable: true,
  ),
  'E5002': ErrorMessage(
    code: 'E5002',
    httpStatus: 502,
    en: 'Vision service cache error',
    ar: 'خطأ في ذاكرة التخزين المؤقت لخدمة الرؤية',
    retryable: true,
  ),
  'E5003': ErrorMessage(
    code: 'E5003',
    httpStatus: 502,
    en: 'Vision service message queue error',
    ar: 'خطأ في قائمة رسائل خدمة الرؤية',
    retryable: true,
  ),
  'E6001': ErrorMessage(
    code: 'E6001',
    httpStatus: 429,
    en: 'Vision API rate limit exceeded. Please wait before retrying.',
    ar: 'تم تجاوز حد معدل واجهة برمجة الرؤية. يرجى الانتظار قبل إعادة المحاولة.',
    retryable: true,
  ),
  'E6002': ErrorMessage(
    code: 'E6002',
    httpStatus: 429,
    en: 'Vision API quota exceeded for this billing period',
    ar: 'تم تجاوز حصة واجهة برمجة الرؤية لفترة الفوترة هذه',
    retryable: false,
  ),
  'E7001': ErrorMessage(
    code: 'E7001',
    httpStatus: 504,
    en: 'Vision inference timed out. Please try again.',
    ar: 'انتهت مهلة استدلال الرؤية. يرجى المحاولة مرة أخرى.',
    retryable: true,
  ),
  'E7002': ErrorMessage(
    code: 'E7002',
    httpStatus: 504,
    en: 'Vision request timed out',
    ar: 'انتهت مهلة طلب الرؤية',
    retryable: true,
  ),
  'E8001': ErrorMessage(
    code: 'E8001',
    httpStatus: 401,
    en: 'Invalid authentication token for vision service',
    ar: 'رمز مصادقة غير صالح لخدمة الرؤية',
    retryable: false,
  ),
  'E8002': ErrorMessage(
    code: 'E8002',
    httpStatus: 401,
    en: 'Authentication token has expired. Please login again.',
    ar: 'انتهت صلاحية رمز المصادقة. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  ),
  'E8003': ErrorMessage(
    code: 'E8003',
    httpStatus: 401,
    en: 'Permission denied for this vision operation',
    ar: 'تم رفض الإذن لهذه العملية في خدمة الرؤية',
    retryable: false,
  ),
  'A1009': ErrorMessage(
    code: 'A1009',
    httpStatus: 200,
    en: 'Some advisory sources returned degraded results',
    ar: 'بعض مصادر الاستشارة أعادت نتائج ناقصة',
    retryable: true,
  ),
  'A1010': ErrorMessage(
    code: 'A1010',
    httpStatus: 503,
    en: 'All advisory downstream services are unavailable',
    ar: 'جميع خدمات الاستشارة التابعة غير متاحة',
    retryable: true,
  ),
  'A1011': ErrorMessage(
    code: 'A1011',
    httpStatus: 504,
    en: 'Comprehensive advisory orchestration timed out',
    ar: 'انتهت مهلة تنسيق الاستشارة الشاملة',
    retryable: true,
  ),
  'L1001': ErrorMessage(
    code: 'L1001',
    httpStatus: 404,
    en: 'Field not found for loan verification',
    ar: 'لم يُعثر على الحقل للتحقق من القرض',
    retryable: false,
  ),
  'L1002': ErrorMessage(
    code: 'L1002',
    httpStatus: 200,
    en: 'Crop could not be verified via satellite NDVI',
    ar: 'لا يمكن التحقق من المحصول عبر مؤشر NDVI الفضائي',
    retryable: false,
  ),
  'L1003': ErrorMessage(
    code: 'L1003',
    httpStatus: 200,
    en: 'Declared area does not match GIS-measured area',
    ar: 'المساحة المُعلنة لا تطابق المساحة المقاسة بنظم المعلومات الجغرافية',
    retryable: false,
  ),
  'L1004': ErrorMessage(
    code: 'L1004',
    httpStatus: 200,
    en: 'Field risk profile exceeds safe loan threshold',
    ar: 'مستوى مخاطر الحقل يتجاوز الحد الآمن للإقراض',
    retryable: false,
  ),
  'L1005': ErrorMessage(
    code: 'L1005',
    httpStatus: 503,
    en: 'NDVI history unavailable for loan verification',
    ar: 'بيانات NDVI غير متاحة للتحقق من القرض',
    retryable: true,
  ),
  'L1006': ErrorMessage(
    code: 'L1006',
    httpStatus: 200,
    en: 'Requested loan amount exceeds the recommended safe limit',
    ar: 'مبلغ القرض المطلوب يتجاوز الحد الآمن الموصى به',
    retryable: false,
  ),
  'W1009': ErrorMessage(
    code: 'W1009',
    httpStatus: 500,
    en: 'Failed to render weather graph SVG',
    ar: 'فشل في توليد الرسم البياني للطقس',
    retryable: true,
  ),
  'W1010': ErrorMessage(
    code: 'W1010',
    httpStatus: 404,
    en: 'Weather graph not found',
    ar: 'لم يُعثر على الرسم البياني للطقس',
    retryable: false,
  ),
  'W1011': ErrorMessage(
    code: 'W1011',
    httpStatus: 403,
    en: 'Invalid weather graph signature',
    ar: 'توقيع الرسم البياني للطقس غير صالح',
    retryable: false,
  ),
  'W1012': ErrorMessage(
    code: 'W1012',
    httpStatus: 410,
    en: 'Weather graph has expired',
    ar: 'انتهت صلاحية الرسم البياني للطقس',
    retryable: true,
  ),
  'W1013': ErrorMessage(
    code: 'W1013',
    httpStatus: 200,
    en: 'No historical weather data for the requested range',
    ar: 'لا توجد بيانات طقس تاريخية للفترة المطلوبة',
    retryable: false,
  ),
  'T1001': ErrorMessage(
    code: 'T1001',
    httpStatus: 409,
    en: 'Traceability chain integrity check failed',
    ar: 'فشل التحقق من سلامة سلسلة التتبع',
    retryable: false,
  ),
  'T1002': ErrorMessage(
    code: 'T1002',
    httpStatus: 500,
    en: 'Failed to persist traceability anchor',
    ar: 'فشل حفظ مرساة التتبع',
    retryable: true,
  ),
  'T1003': ErrorMessage(
    code: 'T1003',
    httpStatus: 503,
    en: 'Traceability anchoring subscriber is not running',
    ar: 'مشترك تتبع المراسي غير مُفعَّل',
    retryable: true,
  ),
  'G1001': ErrorMessage(
    code: 'G1001',
    httpStatus: 200,
    en: 'Geofence has no field mapping; auto-draft skipped',
    ar: 'السياج الجغرافي لا يرتبط بحقل؛ تم تخطي المسودة التلقائية',
    retryable: false,
  ),
  'G1002': ErrorMessage(
    code: 'G1002',
    httpStatus: 404,
    en: 'Equipment not found for this tenant',
    ar: 'المعدة غير موجودة لهذا المستأجر',
    retryable: false,
  ),
  'G1003': ErrorMessage(
    code: 'G1003',
    httpStatus: 202,
    en: 'Auto-draft queued for retry',
    ar: 'تمت جدولة المسودة التلقائية لإعادة المحاولة',
    retryable: true,
  ),
  'G1004': ErrorMessage(
    code: 'G1004',
    httpStatus: 200,
    en: 'Geofence alert type is not actionable',
    ar: 'نوع تنبيه السياج الجغرافي غير قابل للتنفيذ',
    retryable: false,
  ),
  'R1001': ErrorMessage(
    code: 'R1001',
    httpStatus: 500,
    en: 'Failed to upload report to object storage',
    ar: 'فشل في رفع التقرير إلى التخزين',
    retryable: true,
  ),
  'R1002': ErrorMessage(
    code: 'R1002',
    httpStatus: 500,
    en: 'Object storage credentials are not configured',
    ar: 'بيانات اعتماد التخزين غير مُهيَّأة',
    retryable: false,
  ),
  'R1003': ErrorMessage(
    code: 'R1003',
    httpStatus: 500,
    en: 'Failed to sign object storage URL',
    ar: 'فشل في توقيع عنوان التخزين',
    retryable: true,
  ),
  'ER1001': ErrorMessage(
    code: 'ER1001',
    httpStatus: 503,
    en: 'Soil erosion (RUSLE) engine is not available',
    ar: 'محرك تقييم تعرية التربة (RUSLE) غير متاح',
    retryable: true,
  ),
  'ER1002': ErrorMessage(
    code: 'ER1002',
    httpStatus: 400,
    en: 'Unknown soil texture class',
    ar: 'نوع تربة غير معروف',
    retryable: false,
  ),
  'ER1003': ErrorMessage(
    code: 'ER1003',
    httpStatus: 403,
    en: 'Tenant identifier does not match the authenticated caller',
    ar: 'معرّف المستأجر لا يتطابق مع المتصل الموثّق',
    retryable: false,
  ),
  'ER1004': ErrorMessage(
    code: 'ER1004',
    httpStatus: 500,
    en: 'RUSLE soil loss computation failed',
    ar: 'فشل حساب فقد التربة RUSLE',
    retryable: true,
  ),
  'ER1005': ErrorMessage(
    code: 'ER1005',
    httpStatus: 503,
    en: 'Wind erosion (RWEQ) engine is not available',
    ar: 'محرك تقييم التعرية الريحية (RWEQ) غير متاح',
    retryable: true,
  ),
  'ER1006': ErrorMessage(
    code: 'ER1006',
    httpStatus: 500,
    en: 'RWEQ wind erosion computation failed',
    ar: 'فشل حساب التعرية الريحية RWEQ',
    retryable: true,
  ),
  'ER1007': ErrorMessage(
    code: 'ER1007',
    httpStatus: 500,
    en: 'Combined water + wind erosion computation failed',
    ar: 'فشل حساب التعرية المشتركة (المائية + الريحية)',
    retryable: true,
  ),
  'ER1008': ErrorMessage(
    code: 'ER1008',
    httpStatus: 400,
    en: 'Unknown Yemen region preset (expected: tihama, eastern_plateau, hadhramaut, southern_coast, highlands)',
    ar: 'منطقة يمنية غير معروفة (المتوقع: تهامة، الهضبة الشرقية، حضرموت، الساحل الجنوبي، المرتفعات)',
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
