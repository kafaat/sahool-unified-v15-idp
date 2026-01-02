/**
 * SAHOOL Mobile - Offline Sync Types
 * أنواع بيانات المزامنة بدون اتصال
 *
 * Defines all TypeScript types and interfaces for the offline sync system
 */

// ═══════════════════════════════════════════════════════════════════════════
// عمليات المزامنة - Sync Operations
// ═══════════════════════════════════════════════════════════════════════════

/**
 * نوع عملية المزامنة
 * Type of sync operation to perform
 */
export enum SyncOperationType {
  CREATE = 'CREATE',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
  UPLOAD = 'UPLOAD',
}

/**
 * أولوية العملية
 * Priority level for sync operations
 */
export enum SyncPriority {
  CRITICAL = 0,  // حرج - عمليات الحذف والتحديثات الهامة
  HIGH = 1,      // عالية - إكمال المهام
  NORMAL = 2,    // عادية - ملاحظات الحقول
  LOW = 3,       // منخفضة - رفع الصور والبيانات الإضافية
}

/**
 * حالة عملية المزامنة
 * Status of a sync operation
 */
export enum SyncOperationStatus {
  PENDING = 'PENDING',       // في الانتظار
  PROCESSING = 'PROCESSING', // قيد المعالجة
  COMPLETED = 'COMPLETED',   // مكتمل
  FAILED = 'FAILED',        // فشل
  CONFLICT = 'CONFLICT',    // تعارض
  RETRYING = 'RETRYING',    // إعادة المحاولة
}

// ═══════════════════════════════════════════════════════════════════════════
// أنواع البيانات المزامنة - Data Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * نوع البيانات المراد مزامنتها
 * Type of data being synced
 */
export enum SyncDataType {
  FIELD_OBSERVATION = 'FIELD_OBSERVATION',  // ملاحظات الحقول
  SENSOR_READING = 'SENSOR_READING',        // قراءات المستشعرات
  TASK_COMPLETION = 'TASK_COMPLETION',      // إكمال المهام
  IMAGE_UPLOAD = 'IMAGE_UPLOAD',            // رفع الصور
  FIELD_UPDATE = 'FIELD_UPDATE',            // تحديث بيانات الحقل
  FARM_UPDATE = 'FARM_UPDATE',              // تحديث بيانات المزرعة
  IRRIGATION_LOG = 'IRRIGATION_LOG',        // سجل الري
  PEST_REPORT = 'PEST_REPORT',              // تقرير الآفات
}

// ═══════════════════════════════════════════════════════════════════════════
// عملية المزامنة - Sync Operation
// ═══════════════════════════════════════════════════════════════════════════

/**
 * عملية مزامنة واحدة في قائمة الانتظار
 * Single sync operation in the queue
 */
export interface SyncOperation {
  id: string;                           // معرف فريد للعملية
  type: SyncOperationType;              // نوع العملية
  dataType: SyncDataType;               // نوع البيانات
  priority: SyncPriority;               // الأولوية
  status: SyncOperationStatus;          // الحالة
  data: Record<string, any>;            // البيانات المراد مزامنتها
  previousData?: Record<string, any>;   // البيانات السابقة (للكشف عن التعارضات)
  entityId?: string;                    // معرف الكيان (للتحديث/الحذف)
  endpoint: string;                     // نقطة النهاية API
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'; // طريقة HTTP
  headers?: Record<string, string>;     // رؤوس إضافية
  createdAt: Date;                      // تاريخ الإنشاء
  updatedAt: Date;                      // تاريخ آخر تحديث
  scheduledAt?: Date;                   // موعد التنفيذ المجدول
  attemptCount: number;                 // عدد المحاولات
  maxAttempts: number;                  // الحد الأقصى للمحاولات
  lastError?: string;                   // آخر خطأ
  conflictData?: ConflictData;          // بيانات التعارض
  metadata?: Record<string, any>;       // بيانات إضافية
}

// ═══════════════════════════════════════════════════════════════════════════
// استراتيجيات حل التعارض - Conflict Resolution
// ═══════════════════════════════════════════════════════════════════════════

/**
 * استراتيجية حل التعارض
 * Strategy for resolving sync conflicts
 */
export enum ConflictResolutionStrategy {
  LAST_WRITE_WINS = 'LAST_WRITE_WINS',   // آخر كتابة تفوز (بناءً على الطابع الزمني)
  SERVER_WINS = 'SERVER_WINS',           // الخادم يفوز دائماً
  CLIENT_WINS = 'CLIENT_WINS',           // العميل يفوز دائماً
  MANUAL_MERGE = 'MANUAL_MERGE',         // دمج يدوي (يتطلب تدخل المستخدم)
  FIELD_LEVEL_MERGE = 'FIELD_LEVEL_MERGE', // دمج على مستوى الحقول
  CUSTOM = 'CUSTOM',                     // استراتيجية مخصصة
}

/**
 * بيانات التعارض
 * Data about a sync conflict
 */
export interface ConflictData {
  detectedAt: Date;                     // وقت اكتشاف التعارض
  localVersion: Record<string, any>;    // الإصدار المحلي
  serverVersion: Record<string, any>;   // إصدار الخادم
  baseVersion?: Record<string, any>;    // الإصدار الأساسي (قبل التغييرات)
  conflictingFields: string[];          // الحقول المتعارضة
  resolutionStrategy?: ConflictResolutionStrategy; // الاستراتيجية المطبقة
  resolvedData?: Record<string, any>;   // البيانات بعد الحل
  resolvedAt?: Date;                    // وقت الحل
  resolvedBy?: 'AUTO' | 'USER';        // من حل التعارض
}

// ═══════════════════════════════════════════════════════════════════════════
// حالة المزامنة - Sync Status
// ═══════════════════════════════════════════════════════════════════════════

/**
 * حالة المزامنة العامة
 * Overall sync status
 */
export enum SyncStatus {
  IDLE = 'IDLE',                 // خامل - لا توجد عمليات جارية
  SYNCING = 'SYNCING',          // جاري المزامنة
  SUCCESS = 'SUCCESS',          // نجحت المزامنة
  PARTIAL_SUCCESS = 'PARTIAL_SUCCESS', // نجحت جزئياً
  ERROR = 'ERROR',              // خطأ في المزامنة
  OFFLINE = 'OFFLINE',          // غير متصل
  PAUSED = 'PAUSED',            // متوقف مؤقتاً
  CONFLICT_PENDING = 'CONFLICT_PENDING', // في انتظار حل التعارضات
}

/**
 * معلومات حالة المزامنة
 * Detailed sync status information
 */
export interface SyncStatusInfo {
  status: SyncStatus;                   // الحالة الحالية
  isOnline: boolean;                    // حالة الاتصال
  isSyncing: boolean;                   // جاري المزامنة؟
  lastSyncTime?: Date;                  // آخر وقت مزامنة
  nextSyncTime?: Date;                  // الوقت المجدول للمزامنة القادمة
  pendingCount: number;                 // عدد العمليات المعلقة
  failedCount: number;                  // عدد العمليات الفاشلة
  conflictCount: number;                // عدد التعارضات
  completedCount: number;               // عدد العمليات المكتملة
  totalDataSize: number;                // حجم البيانات بالبايت
  lastError?: string;                   // آخر خطأ
  syncProgress?: number;                // نسبة التقدم (0-100)
}

// ═══════════════════════════════════════════════════════════════════════════
// نتيجة المزامنة - Sync Result
// ═══════════════════════════════════════════════════════════════════════════

/**
 * نتيجة عملية المزامنة
 * Result of a sync operation
 */
export interface SyncResult {
  success: boolean;                     // نجحت العملية؟
  operationId: string;                  // معرف العملية
  timestamp: Date;                      // وقت التنفيذ
  duration: number;                     // مدة التنفيذ بالميلي ثانية
  error?: Error;                        // الخطأ إن وجد
  conflictDetected?: boolean;           // تم اكتشاف تعارض؟
  serverResponse?: any;                 // استجابة الخادم
  retryScheduled?: boolean;             // تم جدولة إعادة محاولة؟
  nextRetryAt?: Date;                   // موعد إعادة المحاولة القادمة
}

/**
 * نتيجة دفعة من عمليات المزامنة
 * Result of batch sync operations
 */
export interface BatchSyncResult {
  success: boolean;                     // نجحت الدفعة كاملة؟
  totalOperations: number;              // إجمالي العمليات
  successCount: number;                 // عدد الناجحة
  failedCount: number;                  // عدد الفاشلة
  conflictCount: number;                // عدد التعارضات
  skippedCount: number;                 // عدد المتخطاة
  results: SyncResult[];                // نتائج فردية
  duration: number;                     // المدة الإجمالية
  errors: Array<{operationId: string; error: Error}>; // الأخطاء
}

// ═══════════════════════════════════════════════════════════════════════════
// إعدادات المزامنة - Sync Configuration
// ═══════════════════════════════════════════════════════════════════════════

/**
 * حالة الشبكة
 * Network connection status
 */
export enum NetworkStatus {
  ONLINE = 'ONLINE',           // متصل
  OFFLINE = 'OFFLINE',         // غير متصل
  SLOW = 'SLOW',              // اتصال بطيء
  METERED = 'METERED',        // اتصال محدود (بيانات محمولة)
}

/**
 * إعدادات المزامنة
 * Configuration for sync manager
 */
export interface SyncConfig {
  autoSync: boolean;                    // مزامنة تلقائية؟
  syncInterval: number;                 // فترة المزامنة بالميلي ثانية
  maxRetries: number;                   // الحد الأقصى لإعادة المحاولات
  retryDelayBase: number;               // التأخير الأساسي لإعادة المحاولة (ميلي ثانية)
  retryDelayMax: number;                // الحد الأقصى للتأخير
  batchSize: number;                    // حجم الدفعة
  maxQueueSize: number;                 // الحد الأقصى لحجم قائمة الانتظار
  conflictResolution: ConflictResolutionStrategy; // استراتيجية حل التعارض الافتراضية
  syncOnlyOnWifi: boolean;             // المزامنة فقط على WiFi؟
  throttleOnSlowConnection: boolean;    // تقليل السرعة على الاتصال البطيء؟
  persistQueue: boolean;                // حفظ قائمة الانتظار؟
  enableCompression: boolean;           // تفعيل الضغط؟
  maxUploadSize: number;                // الحد الأقصى لحجم الرفع (بايت)
  timeoutMs: number;                    // مهلة الطلب (ميلي ثانية)
}

// ═══════════════════════════════════════════════════════════════════════════
// إحصائيات المزامنة - Sync Statistics
// ═══════════════════════════════════════════════════════════════════════════

/**
 * إحصائيات المزامنة
 * Statistics about sync operations
 */
export interface SyncStatistics {
  totalOperations: number;              // إجمالي العمليات
  successfulOperations: number;         // العمليات الناجحة
  failedOperations: number;             // العمليات الفاشلة
  conflictOperations: number;           // عمليات التعارض
  averageSyncTime: number;              // متوسط وقت المزامنة (ميلي ثانية)
  totalDataSynced: number;              // إجمالي البيانات المزامنة (بايت)
  lastSyncDuration: number;             // مدة آخر مزامنة
  syncsByDataType: Record<SyncDataType, number>; // المزامنات حسب نوع البيانات
  peakQueueSize: number;                // الحد الأقصى لحجم قائمة الانتظار
  firstSyncTime?: Date;                 // أول وقت مزامنة
  lastSuccessfulSync?: Date;            // آخر مزامنة ناجحة
}

// ═══════════════════════════════════════════════════════════════════════════
// أنواع البيانات المحددة - Specific Data Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * ملاحظة حقل
 * Field observation data
 */
export interface FieldObservation {
  id?: string;
  fieldId: string;
  observedAt: Date;
  observationType: string;
  notes: string;
  images?: string[];
  location?: {
    latitude: number;
    longitude: number;
  };
  userId: string;
  metadata?: Record<string, any>;
}

/**
 * قراءة مستشعر
 * Sensor reading data
 */
export interface SensorReading {
  id?: string;
  sensorId: string;
  fieldId: string;
  readingType: string;
  value: number;
  unit: string;
  timestamp: Date;
  quality: 'GOOD' | 'FAIR' | 'POOR';
  metadata?: Record<string, any>;
}

/**
 * إكمال مهمة
 * Task completion data
 */
export interface TaskCompletion {
  id?: string;
  taskId: string;
  completedAt: Date;
  completedBy: string;
  status: 'COMPLETED' | 'FAILED' | 'PARTIAL';
  notes?: string;
  attachments?: string[];
  location?: {
    latitude: number;
    longitude: number;
  };
}

/**
 * رفع صورة
 * Image upload data
 */
export interface ImageUpload {
  id?: string;
  localUri: string;
  remoteUrl?: string;
  entityType: SyncDataType;
  entityId: string;
  size: number;
  mimeType: string;
  uploadedAt?: Date;
  thumbnailUri?: string;
  metadata?: Record<string, any>;
}

// ═══════════════════════════════════════════════════════════════════════════
// نوع مخصص لحل التعارض - Custom Conflict Resolver
// ═══════════════════════════════════════════════════════════════════════════

/**
 * دالة مخصصة لحل التعارض
 * Custom function to resolve conflicts
 */
export type CustomConflictResolver = (
  local: Record<string, any>,
  server: Record<string, any>,
  base?: Record<string, any>
) => Promise<Record<string, any>>;

// ═══════════════════════════════════════════════════════════════════════════
// الأحداث - Events
// ═══════════════════════════════════════════════════════════════════════════

/**
 * نوع حدث المزامنة
 * Sync event type
 */
export enum SyncEventType {
  SYNC_STARTED = 'SYNC_STARTED',
  SYNC_COMPLETED = 'SYNC_COMPLETED',
  SYNC_FAILED = 'SYNC_FAILED',
  OPERATION_QUEUED = 'OPERATION_QUEUED',
  OPERATION_COMPLETED = 'OPERATION_COMPLETED',
  OPERATION_FAILED = 'OPERATION_FAILED',
  CONFLICT_DETECTED = 'CONFLICT_DETECTED',
  CONFLICT_RESOLVED = 'CONFLICT_RESOLVED',
  NETWORK_STATUS_CHANGED = 'NETWORK_STATUS_CHANGED',
  QUEUE_CLEARED = 'QUEUE_CLEARED',
}

/**
 * حدث المزامنة
 * Sync event
 */
export interface SyncEvent {
  type: SyncEventType;
  timestamp: Date;
  data?: any;
  operationId?: string;
}

/**
 * مستمع لأحداث المزامنة
 * Listener for sync events
 */
export type SyncEventListener = (event: SyncEvent) => void;

// ═══════════════════════════════════════════════════════════════════════════
// واجهة مدير التخزين - Storage Interface
// ═══════════════════════════════════════════════════════════════════════════

/**
 * واجهة التخزين المحلي
 * Interface for local storage operations
 */
export interface ISyncStorage {
  saveQueue(operations: SyncOperation[]): Promise<void>;
  loadQueue(): Promise<SyncOperation[]>;
  clearQueue(): Promise<void>;
  saveOperation(operation: SyncOperation): Promise<void>;
  removeOperation(operationId: string): Promise<void>;
  updateOperation(operationId: string, updates: Partial<SyncOperation>): Promise<void>;
  getOperation(operationId: string): Promise<SyncOperation | null>;
  saveLastSyncTime(time: Date): Promise<void>;
  getLastSyncTime(): Promise<Date | null>;
  saveStatistics(stats: SyncStatistics): Promise<void>;
  getStatistics(): Promise<SyncStatistics | null>;
}

// ═══════════════════════════════════════════════════════════════════════════
// تصدير جميع الأنواع - Export All Types
// ═══════════════════════════════════════════════════════════════════════════

export default {
  SyncOperationType,
  SyncPriority,
  SyncOperationStatus,
  SyncDataType,
  ConflictResolutionStrategy,
  SyncStatus,
  NetworkStatus,
  SyncEventType,
};
