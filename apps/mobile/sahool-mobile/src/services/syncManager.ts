/**
 * SAHOOL Mobile - Offline Sync Manager
 * مدير المزامنة بدون اتصال
 *
 * Comprehensive offline-first sync manager for SAHOOL mobile application
 * Features:
 * - Priority-based queue management
 * - Automatic conflict resolution with multiple strategies
 * - Network-aware synchronization
 * - Queue persistence and recovery
 * - Retry logic with exponential backoff
 * - Real-time sync status updates
 */

import AsyncStorage from "@react-native-async-storage/async-storage";
import NetInfo, { NetInfoState } from "@react-native-community/netinfo";
import {
  SyncOperation,
  SyncOperationType,
  SyncPriority,
  SyncOperationStatus,
  SyncDataType,
  ConflictResolutionStrategy,
  ConflictData,
  SyncStatus,
  SyncStatusInfo,
  SyncResult,
  BatchSyncResult,
  SyncConfig,
  NetworkStatus,
  SyncStatistics,
  SyncEventType,
  SyncEvent,
  SyncEventListener,
  ISyncStorage,
  CustomConflictResolver,
} from "../models/syncTypes";

// ═══════════════════════════════════════════════════════════════════════════
// الثوابت - Constants
// ═══════════════════════════════════════════════════════════════════════════

const STORAGE_KEYS = {
  QUEUE: "@sahool_sync_queue",
  LAST_SYNC: "@sahool_last_sync",
  STATISTICS: "@sahool_sync_stats",
  CONFIG: "@sahool_sync_config",
};

const DEFAULT_CONFIG: SyncConfig = {
  autoSync: true,
  syncInterval: 5 * 60 * 1000, // 5 دقائق
  maxRetries: 5,
  retryDelayBase: 1000,
  retryDelayMax: 30000,
  batchSize: 10,
  maxQueueSize: 1000,
  conflictResolution: ConflictResolutionStrategy.LAST_WRITE_WINS,
  syncOnlyOnWifi: false,
  throttleOnSlowConnection: true,
  persistQueue: true,
  enableCompression: false,
  maxUploadSize: 10 * 1024 * 1024, // 10 MB
  timeoutMs: 30000,
};

// ═══════════════════════════════════════════════════════════════════════════
// مدير المزامنة - Sync Manager Class
// ═══════════════════════════════════════════════════════════════════════════

export class SyncManager {
  private static instance: SyncManager | null = null;

  // إعدادات المزامنة - Sync configuration
  private config: SyncConfig;

  // قائمة انتظار العمليات - Operations queue
  private queue: SyncOperation[] = [];

  // حالة المزامنة - Sync state
  private currentStatus: SyncStatus = SyncStatus.IDLE;
  private isSyncing: boolean = false;
  private isPaused: boolean = false;

  // حالة الشبكة - Network state
  private networkStatus: NetworkStatus = NetworkStatus.OFFLINE;
  private isOnline: boolean = false;

  // مؤقت المزامنة - Sync timer
  private syncTimer: NodeJS.Timeout | null = null;

  // الإحصائيات - Statistics
  private statistics: SyncStatistics = this.initializeStatistics();

  // المستمعون للأحداث - Event listeners
  private eventListeners: Map<SyncEventType, Set<SyncEventListener>> =
    new Map();

  // حالي المزامنة - Custom resolvers
  private customResolvers: Map<SyncDataType, CustomConflictResolver> =
    new Map();

  // التخزين - Storage
  private storage: ISyncStorage;

  // ═══════════════════════════════════════════════════════════════════════════
  // البناء والتهيئة - Constructor & Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  private constructor(config?: Partial<SyncConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.storage = new AsyncStorageAdapter();
    this.initializeNetworkListener();
    this.loadPersistedData();

    if (this.config.autoSync) {
      this.startAutoSync();
    }
  }

  /**
   * الحصول على مثيل واحد من مدير المزامنة
   * Get singleton instance of SyncManager
   */
  public static getInstance(config?: Partial<SyncConfig>): SyncManager {
    if (!SyncManager.instance) {
      SyncManager.instance = new SyncManager(config);
    }
    return SyncManager.instance;
  }

  /**
   * تهيئة الإحصائيات
   * Initialize statistics object
   */
  private initializeStatistics(): SyncStatistics {
    return {
      totalOperations: 0,
      successfulOperations: 0,
      failedOperations: 0,
      conflictOperations: 0,
      averageSyncTime: 0,
      totalDataSynced: 0,
      lastSyncDuration: 0,
      syncsByDataType: {} as Record<SyncDataType, number>,
      peakQueueSize: 0,
    };
  }

  /**
   * تحميل البيانات المحفوظة
   * Load persisted data from storage
   */
  private async loadPersistedData(): Promise<void> {
    try {
      // تحميل قائمة الانتظار - Load queue
      if (this.config.persistQueue) {
        const queue = await this.storage.loadQueue();
        this.queue = queue.filter(
          (op) => op.status !== SyncOperationStatus.COMPLETED,
        );
        console.log(`📦 تم تحميل ${this.queue.length} عملية من التخزين المحلي`);
      }

      // تحميل الإحصائيات - Load statistics
      const stats = await this.storage.getStatistics();
      if (stats) {
        this.statistics = stats;
      }

      console.log("✅ تم تحميل بيانات المزامنة المحفوظة");
    } catch (error) {
      console.error("❌ خطأ في تحميل البيانات المحفوظة:", error);
    }
  }

  /**
   * تهيئة مستمع الشبكة
   * Initialize network status listener
   */
  private initializeNetworkListener(): void {
    NetInfo.addEventListener((state: NetInfoState) => {
      this.handleNetworkChange(state);
    });
  }

  /**
   * معالجة تغيير حالة الشبكة
   * Handle network status change
   */
  private handleNetworkChange(state: NetInfoState): void {
    const wasOnline = this.isOnline;
    this.isOnline = state.isConnected ?? false;

    // تحديد حالة الشبكة - Determine network status
    if (!this.isOnline) {
      this.networkStatus = NetworkStatus.OFFLINE;
      this.currentStatus = SyncStatus.OFFLINE;
    } else if (state.details && "cellularGeneration" in state.details) {
      // اتصال محمول - Mobile connection
      this.networkStatus = NetworkStatus.METERED;
    } else if (state.type === "wifi") {
      this.networkStatus = NetworkStatus.ONLINE;
    } else {
      this.networkStatus = NetworkStatus.ONLINE;
    }

    // إطلاق حدث تغيير الشبكة - Emit network change event
    this.emitEvent({
      type: SyncEventType.NETWORK_STATUS_CHANGED,
      timestamp: new Date(),
      data: { status: this.networkStatus, isOnline: this.isOnline },
    });

    // بدء المزامنة إذا أصبحنا متصلين - Start sync if we're now online
    if (!wasOnline && this.isOnline && this.queue.length > 0) {
      console.log("🌐 الاتصال متاح، بدء المزامنة التلقائية");
      this.syncWhenOnline();
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // إدارة قائمة الانتظار - Queue Management
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * إضافة عملية إلى قائمة الانتظار
   * Queue an operation for syncing
   */
  public async queueOperation(
    type: SyncOperationType,
    dataType: SyncDataType,
    data: Record<string, any>,
    options?: {
      priority?: SyncPriority;
      entityId?: string;
      endpoint?: string;
      previousData?: Record<string, any>;
      metadata?: Record<string, any>;
    },
  ): Promise<string> {
    // التحقق من حجم قائمة الانتظار - Check queue size
    if (this.queue.length >= this.config.maxQueueSize) {
      throw new Error(
        `تجاوز الحد الأقصى لحجم قائمة الانتظار (${this.config.maxQueueSize})`,
      );
    }

    // إنشاء العملية - Create operation
    const operation: SyncOperation = {
      id: this.generateOperationId(),
      type,
      dataType,
      priority: options?.priority ?? this.determinePriority(type, dataType),
      status: SyncOperationStatus.PENDING,
      data,
      previousData: options?.previousData,
      entityId: options?.entityId,
      endpoint: options?.endpoint ?? this.getEndpointForDataType(dataType),
      method: this.getMethodForOperationType(type),
      createdAt: new Date(),
      updatedAt: new Date(),
      attemptCount: 0,
      maxAttempts: this.config.maxRetries,
      metadata: options?.metadata,
    };

    // إضافة إلى قائمة الانتظار - Add to queue
    this.queue.push(operation);

    // تحديث الإحصائيات - Update statistics
    this.statistics.totalOperations++;
    this.statistics.peakQueueSize = Math.max(
      this.statistics.peakQueueSize,
      this.queue.length,
    );

    // حفظ قائمة الانتظار - Save queue
    if (this.config.persistQueue) {
      await this.saveQueueToStorage();
    }

    // إطلاق حدث - Emit event
    this.emitEvent({
      type: SyncEventType.OPERATION_QUEUED,
      timestamp: new Date(),
      operationId: operation.id,
      data: { operation },
    });

    console.log(
      `➕ تمت إضافة عملية ${operation.id} إلى قائمة الانتظار (${this.queue.length} عملية)`,
    );

    // بدء المزامنة إذا كنا متصلين - Start sync if online
    if (this.isOnline && !this.isSyncing && !this.isPaused) {
      this.processQueue();
    }

    return operation.id;
  }

  /**
   * معالجة قائمة الانتظار
   * Process the sync queue
   */
  public async processQueue(): Promise<BatchSyncResult> {
    // التحقق من الحالة - Check preconditions
    if (this.isSyncing) {
      console.log("⏳ المزامنة قيد التنفيذ بالفعل");
      return this.createEmptyBatchResult();
    }

    if (this.isPaused) {
      console.log("⏸️ المزامنة متوقفة مؤقتاً");
      return this.createEmptyBatchResult();
    }

    if (!this.isOnline) {
      console.log("📴 لا يوجد اتصال بالإنترنت");
      this.currentStatus = SyncStatus.OFFLINE;
      return this.createEmptyBatchResult();
    }

    if (this.queue.length === 0) {
      console.log("✅ قائمة الانتظار فارغة");
      this.currentStatus = SyncStatus.IDLE;
      return this.createEmptyBatchResult();
    }

    // التحقق من نوع الاتصال - Check connection type
    if (
      this.config.syncOnlyOnWifi &&
      this.networkStatus === NetworkStatus.METERED
    ) {
      console.log("📱 تم تعطيل المزامنة على البيانات الخلوية");
      return this.createEmptyBatchResult();
    }

    // بدء المزامنة - Start syncing
    this.isSyncing = true;
    this.currentStatus = SyncStatus.SYNCING;
    const startTime = Date.now();

    this.emitEvent({
      type: SyncEventType.SYNC_STARTED,
      timestamp: new Date(),
    });

    console.log(`🔄 بدء معالجة قائمة الانتظار (${this.queue.length} عملية)`);

    // معالجة العمليات حسب الأولوية - Process operations by priority
    const sortedQueue = this.sortQueueByPriority();
    const batchSize = this.getBatchSize();
    const batch = sortedQueue.slice(0, batchSize);

    const results: SyncResult[] = [];
    const errors: Array<{ operationId: string; error: Error }> = [];

    for (const operation of batch) {
      try {
        const result = await this.processOperation(operation);
        results.push(result);

        if (result.success) {
          this.statistics.successfulOperations++;
          this.removeOperationFromQueue(operation.id);
        } else if (result.conflictDetected) {
          this.statistics.conflictOperations++;
        } else {
          this.statistics.failedOperations++;
          if (operation.attemptCount >= operation.maxAttempts) {
            this.removeOperationFromQueue(operation.id);
          }
        }
      } catch (error) {
        console.error(`❌ خطأ في معالجة العملية ${operation.id}:`, error);
        errors.push({ operationId: operation.id, error: error as Error });
        this.statistics.failedOperations++;
      }
    }

    // حساب النتائج - Calculate results
    const duration = Date.now() - startTime;
    const successCount = results.filter((r) => r.success).length;
    const failedCount = results.filter(
      (r) => !r.success && !r.conflictDetected,
    ).length;
    const conflictCount = results.filter((r) => r.conflictDetected).length;

    const batchResult: BatchSyncResult = {
      success: failedCount === 0 && conflictCount === 0,
      totalOperations: batch.length,
      successCount,
      failedCount,
      conflictCount,
      skippedCount: 0,
      results,
      duration,
      errors,
    };

    // تحديث الحالة - Update status
    this.isSyncing = false;
    if (batchResult.success) {
      this.currentStatus = SyncStatus.SUCCESS;
    } else if (successCount > 0) {
      this.currentStatus = SyncStatus.PARTIAL_SUCCESS;
    } else if (conflictCount > 0) {
      this.currentStatus = SyncStatus.CONFLICT_PENDING;
    } else {
      this.currentStatus = SyncStatus.ERROR;
    }

    // تحديث الإحصائيات - Update statistics
    this.statistics.lastSyncDuration = duration;
    this.statistics.averageSyncTime =
      (this.statistics.averageSyncTime *
        (this.statistics.totalOperations - batch.length) +
        duration) /
      this.statistics.totalOperations;

    // حفظ التغييرات - Save changes
    if (this.config.persistQueue) {
      await this.saveQueueToStorage();
    }
    await this.storage.saveStatistics(this.statistics);
    await this.storage.saveLastSyncTime(new Date());

    // إطلاق حدث - Emit event
    const eventType = batchResult.success
      ? SyncEventType.SYNC_COMPLETED
      : SyncEventType.SYNC_FAILED;

    this.emitEvent({
      type: eventType,
      timestamp: new Date(),
      data: batchResult,
    });

    console.log(
      `✅ اكتملت المزامنة: ${successCount} ناجحة، ${failedCount} فاشلة، ${conflictCount} تعارض`,
    );

    return batchResult;
  }

  /**
   * معالجة عملية واحدة
   * Process a single operation
   */
  private async processOperation(
    operation: SyncOperation,
  ): Promise<SyncResult> {
    const startTime = Date.now();
    operation.status = SyncOperationStatus.PROCESSING;
    operation.attemptCount++;
    operation.updatedAt = new Date();

    console.log(
      `⚙️ معالجة العملية ${operation.id} (محاولة ${operation.attemptCount}/${operation.maxAttempts})`,
    );

    try {
      // تنفيذ الطلب - Execute request
      const response = await this.executeRequest(operation);

      // التحقق من التعارضات - Check for conflicts
      if (response.status === 409 || response.status === 412) {
        console.log(`⚠️ تم اكتشاف تعارض للعملية ${operation.id}`);

        const conflictData = await this.detectConflict(
          operation,
          response.data,
        );
        operation.conflictData = conflictData;
        operation.status = SyncOperationStatus.CONFLICT;

        // محاولة حل التعارض تلقائياً - Try to resolve automatically
        const resolved = await this.handleConflict(operation);
        if (resolved) {
          operation.status = SyncOperationStatus.COMPLETED;
          return this.createSyncResult(operation, startTime, true, false);
        }

        this.emitEvent({
          type: SyncEventType.CONFLICT_DETECTED,
          timestamp: new Date(),
          operationId: operation.id,
          data: { conflictData },
        });

        return this.createSyncResult(operation, startTime, false, true);
      }

      // نجحت العملية - Operation succeeded
      if (response.status >= 200 && response.status < 300) {
        operation.status = SyncOperationStatus.COMPLETED;

        // تحديث الإحصائيات - Update statistics
        const dataSize = JSON.stringify(operation.data).length;
        this.statistics.totalDataSynced += dataSize;
        this.statistics.syncsByDataType[operation.dataType] =
          (this.statistics.syncsByDataType[operation.dataType] || 0) + 1;

        this.emitEvent({
          type: SyncEventType.OPERATION_COMPLETED,
          timestamp: new Date(),
          operationId: operation.id,
        });

        console.log(`✅ نجحت العملية ${operation.id}`);
        return this.createSyncResult(
          operation,
          startTime,
          true,
          false,
          response,
        );
      }

      // فشلت العملية - Operation failed
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    } catch (error) {
      console.error(`❌ فشلت العملية ${operation.id}:`, error);

      operation.status = SyncOperationStatus.FAILED;
      operation.lastError = (error as Error).message;

      // جدولة إعادة المحاولة - Schedule retry
      if (operation.attemptCount < operation.maxAttempts) {
        const retryDelay = this.calculateRetryDelay(operation.attemptCount);
        operation.scheduledAt = new Date(Date.now() + retryDelay);
        operation.status = SyncOperationStatus.RETRYING;

        console.log(`🔄 سيتم إعادة المحاولة بعد ${retryDelay}ms`);
      }

      this.emitEvent({
        type: SyncEventType.OPERATION_FAILED,
        timestamp: new Date(),
        operationId: operation.id,
        data: { error: (error as Error).message },
      });

      return this.createSyncResult(
        operation,
        startTime,
        false,
        false,
        undefined,
        error as Error,
        operation.attemptCount < operation.maxAttempts,
        operation.scheduledAt,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // حل التعارضات - Conflict Resolution
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * اكتشاف التعارض
   * Detect conflict between local and server data
   */
  private async detectConflict(
    operation: SyncOperation,
    serverData: any,
  ): Promise<ConflictData> {
    const conflictingFields: string[] = [];

    if (operation.previousData) {
      // مقارنة على مستوى الحقول - Field-level comparison
      for (const key in operation.data) {
        if (
          operation.previousData[key] !== undefined &&
          operation.data[key] !== operation.previousData[key] &&
          serverData[key] !== operation.previousData[key] &&
          operation.data[key] !== serverData[key]
        ) {
          conflictingFields.push(key);
        }
      }
    }

    return {
      detectedAt: new Date(),
      localVersion: operation.data,
      serverVersion: serverData,
      baseVersion: operation.previousData,
      conflictingFields,
    };
  }

  /**
   * معالجة التعارض
   * Handle conflict resolution
   */
  public async handleConflict(operation: SyncOperation): Promise<boolean> {
    if (!operation.conflictData) {
      return false;
    }

    const { localVersion, serverVersion, baseVersion } = operation.conflictData;

    console.log(`🔧 محاولة حل التعارض للعملية ${operation.id}`);

    // استخدام محلل مخصص إذا كان متاحاً - Use custom resolver if available
    const customResolver = this.customResolvers.get(operation.dataType);
    if (customResolver) {
      try {
        const resolved = await customResolver(
          localVersion,
          serverVersion,
          baseVersion,
        );
        operation.data = resolved;
        operation.conflictData.resolvedData = resolved;
        operation.conflictData.resolvedAt = new Date();
        operation.conflictData.resolvedBy = "AUTO";
        operation.conflictData.resolutionStrategy =
          ConflictResolutionStrategy.CUSTOM;

        this.emitEvent({
          type: SyncEventType.CONFLICT_RESOLVED,
          timestamp: new Date(),
          operationId: operation.id,
          data: { strategy: "CUSTOM", resolved },
        });

        console.log(`✅ تم حل التعارض باستخدام محلل مخصص`);
        return true;
      } catch (error) {
        console.error("❌ فشل المحلل المخصص:", error);
      }
    }

    // استخدام استراتيجية الحل الافتراضية - Use default resolution strategy
    const strategy = this.config.conflictResolution;
    let resolved: Record<string, any> | null = null;

    switch (strategy) {
      case ConflictResolutionStrategy.SERVER_WINS:
        resolved = serverVersion;
        break;

      case ConflictResolutionStrategy.CLIENT_WINS:
        resolved = localVersion;
        break;

      case ConflictResolutionStrategy.LAST_WRITE_WINS:
        resolved = this.resolveLastWriteWins(localVersion, serverVersion);
        break;

      case ConflictResolutionStrategy.FIELD_LEVEL_MERGE:
        resolved = this.resolveFieldLevelMerge(
          localVersion,
          serverVersion,
          baseVersion,
          operation.conflictData.conflictingFields,
        );
        break;

      case ConflictResolutionStrategy.MANUAL_MERGE:
        // يتطلب تدخل المستخدم - Requires user intervention
        console.log("👤 يتطلب حل يدوي من المستخدم");
        return false;

      default:
        resolved = serverVersion;
    }

    if (resolved) {
      operation.data = resolved;
      operation.conflictData.resolvedData = resolved;
      operation.conflictData.resolvedAt = new Date();
      operation.conflictData.resolvedBy = "AUTO";
      operation.conflictData.resolutionStrategy = strategy;

      this.emitEvent({
        type: SyncEventType.CONFLICT_RESOLVED,
        timestamp: new Date(),
        operationId: operation.id,
        data: { strategy, resolved },
      });

      console.log(`✅ تم حل التعارض باستخدام استراتيجية ${strategy}`);
      return true;
    }

    return false;
  }

  /**
   * حل بآخر كتابة تفوز
   * Resolve using last write wins strategy
   */
  private resolveLastWriteWins(
    local: Record<string, any>,
    server: Record<string, any>,
  ): Record<string, any> {
    const localTime = new Date(
      local.updatedAt || local.updated_at || 0,
    ).getTime();
    const serverTime = new Date(
      server.updatedAt || server.updated_at || 0,
    ).getTime();

    return localTime > serverTime ? local : server;
  }

  /**
   * حل بالدمج على مستوى الحقول
   * Resolve using field-level merge
   */
  private resolveFieldLevelMerge(
    local: Record<string, any>,
    server: Record<string, any>,
    base: Record<string, any> | undefined,
    conflictingFields: string[],
  ): Record<string, any> {
    const merged = { ...server };

    // دمج التغييرات المحلية غير المتعارضة - Merge non-conflicting local changes
    for (const key in local) {
      if (!conflictingFields.includes(key)) {
        if (!base || local[key] !== base[key]) {
          merged[key] = local[key];
        }
      }
    }

    return merged;
  }

  /**
   * تسجيل محلل تعارض مخصص
   * Register a custom conflict resolver for a data type
   */
  public registerCustomResolver(
    dataType: SyncDataType,
    resolver: CustomConflictResolver,
  ): void {
    this.customResolvers.set(dataType, resolver);
    console.log(`✅ تم تسجيل محلل مخصص لـ ${dataType}`);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الشبكة والاتصال - Network & Connectivity
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * اكتشاف حالة الشبكة
   * Detect current network status
   */
  public async detectNetworkStatus(): Promise<NetworkStatus> {
    try {
      const state = await NetInfo.fetch();

      if (!state.isConnected) {
        return NetworkStatus.OFFLINE;
      }

      if (state.details && "cellularGeneration" in state.details) {
        return NetworkStatus.METERED;
      }

      // يمكن إضافة فحص السرعة هنا - Can add speed test here
      // if (await this.isSlowConnection()) {
      //   return NetworkStatus.SLOW;
      // }

      return NetworkStatus.ONLINE;
    } catch (error) {
      console.error("خطأ في اكتشاف حالة الشبكة:", error);
      return NetworkStatus.OFFLINE;
    }
  }

  /**
   * المزامنة عند الاتصال
   * Sync when network becomes available
   */
  public async syncWhenOnline(): Promise<void> {
    if (this.isOnline && this.queue.length > 0) {
      console.log("🌐 بدء المزامنة التلقائية");
      await this.processQueue();
    }
  }

  /**
   * تقليل السرعة على الاتصال البطيء
   * Throttle operations on slow connection
   */
  private getBatchSize(): number {
    if (!this.config.throttleOnSlowConnection) {
      return this.config.batchSize;
    }

    switch (this.networkStatus) {
      case NetworkStatus.SLOW:
        return Math.ceil(this.config.batchSize / 2);
      case NetworkStatus.METERED:
        return Math.ceil(this.config.batchSize / 3);
      default:
        return this.config.batchSize;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // استمرارية البيانات - Data Persistence
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * حفظ قائمة الانتظار إلى التخزين المحلي
   * Save queue to local storage
   */
  public async saveQueueToStorage(): Promise<void> {
    try {
      await this.storage.saveQueue(this.queue);
      console.log(`💾 تم حفظ ${this.queue.length} عملية إلى التخزين المحلي`);
    } catch (error) {
      console.error("❌ خطأ في حفظ قائمة الانتظار:", error);
      throw error;
    }
  }

  /**
   * تحميل قائمة الانتظار من التخزين المحلي
   * Load queue from local storage
   */
  public async loadQueueFromStorage(): Promise<void> {
    try {
      const queue = await this.storage.loadQueue();
      this.queue = queue.filter(
        (op) => op.status !== SyncOperationStatus.COMPLETED,
      );
      console.log(`📦 تم تحميل ${this.queue.length} عملية من التخزين المحلي`);
    } catch (error) {
      console.error("❌ خطأ في تحميل قائمة الانتظار:", error);
      throw error;
    }
  }

  /**
   * حذف العمليات المكتملة
   * Clear completed operations
   */
  public async clearCompletedOperations(): Promise<number> {
    const beforeCount = this.queue.length;
    this.queue = this.queue.filter(
      (op) => op.status !== SyncOperationStatus.COMPLETED,
    );
    const clearedCount = beforeCount - this.queue.length;

    if (this.config.persistQueue && clearedCount > 0) {
      await this.saveQueueToStorage();
    }

    this.emitEvent({
      type: SyncEventType.QUEUE_CLEARED,
      timestamp: new Date(),
      data: { clearedCount },
    });

    console.log(`🗑️ تم حذف ${clearedCount} عملية مكتملة`);
    return clearedCount;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الحالة والإحصائيات - Status & Statistics
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * الحصول على وقت آخر مزامنة
   * Get last sync time
   */
  public async getLastSyncTime(): Promise<Date | null> {
    return await this.storage.getLastSyncTime();
  }

  /**
   * الحصول على حالة المزامنة
   * Get current sync status
   */
  public async getSyncStatus(): Promise<SyncStatusInfo> {
    const lastSyncTime = await this.getLastSyncTime();
    const pendingOps = this.queue.filter(
      (op) => op.status === SyncOperationStatus.PENDING,
    );
    const failedOps = this.queue.filter(
      (op) => op.status === SyncOperationStatus.FAILED,
    );
    const conflictOps = this.queue.filter(
      (op) => op.status === SyncOperationStatus.CONFLICT,
    );
    const completedOps = this.queue.filter(
      (op) => op.status === SyncOperationStatus.COMPLETED,
    );

    const totalDataSize = this.queue.reduce((sum, op) => {
      return sum + JSON.stringify(op.data).length;
    }, 0);

    const syncProgress =
      this.isSyncing && this.queue.length > 0
        ? Math.round((completedOps.length / this.queue.length) * 100)
        : 0;

    return {
      status: this.currentStatus,
      isOnline: this.isOnline,
      isSyncing: this.isSyncing,
      lastSyncTime,
      nextSyncTime: this.syncTimer
        ? new Date(Date.now() + this.config.syncInterval)
        : undefined,
      pendingCount: pendingOps.length,
      failedCount: failedOps.length,
      conflictCount: conflictOps.length,
      completedCount: completedOps.length,
      totalDataSize,
      syncProgress: this.isSyncing ? syncProgress : undefined,
    };
  }

  /**
   * الحصول على الإحصائيات
   * Get sync statistics
   */
  public getStatistics(): SyncStatistics {
    return { ...this.statistics };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // التحكم في المزامنة - Sync Control
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * بدء المزامنة التلقائية
   * Start automatic sync
   */
  public startAutoSync(): void {
    if (this.syncTimer) {
      return; // Already running
    }

    this.syncTimer = setInterval(() => {
      if (!this.isPaused && this.isOnline) {
        this.processQueue();
      }
    }, this.config.syncInterval);

    console.log(
      `⏰ تم بدء المزامنة التلقائية كل ${this.config.syncInterval / 1000}s`,
    );
  }

  /**
   * إيقاف المزامنة التلقائية
   * Stop automatic sync
   */
  public stopAutoSync(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
      this.syncTimer = null;
      console.log("⏹️ تم إيقاف المزامنة التلقائية");
    }
  }

  /**
   * إيقاف المزامنة مؤقتاً
   * Pause sync operations
   */
  public pause(): void {
    this.isPaused = true;
    this.currentStatus = SyncStatus.PAUSED;
    console.log("⏸️ تم إيقاف المزامنة مؤقتاً");
  }

  /**
   * استئناف المزامنة
   * Resume sync operations
   */
  public resume(): void {
    this.isPaused = false;
    console.log("▶️ تم استئناف المزامنة");

    if (this.isOnline && this.queue.length > 0) {
      this.processQueue();
    }
  }

  /**
   * مزامنة فورية
   * Force immediate sync
   */
  public async forceSync(): Promise<BatchSyncResult> {
    console.log("🔄 بدء المزامنة الفورية");
    return await this.processQueue();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الأحداث - Events
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * الاستماع لحدث معين
   * Listen to a specific event
   */
  public addEventListener(
    type: SyncEventType,
    listener: SyncEventListener,
  ): void {
    if (!this.eventListeners.has(type)) {
      this.eventListeners.set(type, new Set());
    }
    this.eventListeners.get(type)!.add(listener);
  }

  /**
   * إزالة مستمع حدث
   * Remove event listener
   */
  public removeEventListener(
    type: SyncEventType,
    listener: SyncEventListener,
  ): void {
    const listeners = this.eventListeners.get(type);
    if (listeners) {
      listeners.delete(listener);
    }
  }

  /**
   * إطلاق حدث
   * Emit an event
   */
  private emitEvent(event: SyncEvent): void {
    const listeners = this.eventListeners.get(event.type);
    if (listeners) {
      listeners.forEach((listener) => {
        try {
          listener(event);
        } catch (error) {
          console.error("خطأ في معالج الحدث:", error);
        }
      });
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // دوال مساعدة - Helper Functions
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * توليد معرف فريد للعملية
   * Generate unique operation ID
   */
  private generateOperationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * تحديد الأولوية بناءً على النوع
   * Determine priority based on operation and data type
   */
  private determinePriority(
    type: SyncOperationType,
    dataType: SyncDataType,
  ): SyncPriority {
    if (type === SyncOperationType.DELETE) {
      return SyncPriority.CRITICAL;
    }

    switch (dataType) {
      case SyncDataType.TASK_COMPLETION:
        return SyncPriority.HIGH;
      case SyncDataType.FIELD_OBSERVATION:
      case SyncDataType.SENSOR_READING:
        return SyncPriority.NORMAL;
      case SyncDataType.IMAGE_UPLOAD:
        return SyncPriority.LOW;
      default:
        return SyncPriority.NORMAL;
    }
  }

  /**
   * الحصول على نقطة النهاية بناءً على نوع البيانات
   * Get API endpoint for data type
   */
  private getEndpointForDataType(dataType: SyncDataType): string {
    const endpoints: Record<SyncDataType, string> = {
      [SyncDataType.FIELD_OBSERVATION]: "/api/field-observations",
      [SyncDataType.SENSOR_READING]: "/api/sensor-readings",
      [SyncDataType.TASK_COMPLETION]: "/api/task-completions",
      [SyncDataType.IMAGE_UPLOAD]: "/api/images",
      [SyncDataType.FIELD_UPDATE]: "/api/fields",
      [SyncDataType.FARM_UPDATE]: "/api/farms",
      [SyncDataType.IRRIGATION_LOG]: "/api/irrigation-logs",
      [SyncDataType.PEST_REPORT]: "/api/pest-reports",
    };

    return endpoints[dataType] || "/api/sync";
  }

  /**
   * الحصول على طريقة HTTP بناءً على نوع العملية
   * Get HTTP method for operation type
   */
  private getMethodForOperationType(
    type: SyncOperationType,
  ): "GET" | "POST" | "PUT" | "DELETE" | "PATCH" {
    switch (type) {
      case SyncOperationType.CREATE:
        return "POST";
      case SyncOperationType.UPDATE:
        return "PUT";
      case SyncOperationType.DELETE:
        return "DELETE";
      case SyncOperationType.UPLOAD:
        return "POST";
      default:
        return "POST";
    }
  }

  /**
   * ترتيب قائمة الانتظار حسب الأولوية
   * Sort queue by priority
   */
  private sortQueueByPriority(): SyncOperation[] {
    return [...this.queue]
      .filter(
        (op) =>
          op.status === SyncOperationStatus.PENDING ||
          op.status === SyncOperationStatus.RETRYING,
      )
      .filter((op) => !op.scheduledAt || op.scheduledAt <= new Date())
      .sort((a, b) => {
        // الأولوية أولاً - Priority first
        if (a.priority !== b.priority) {
          return a.priority - b.priority;
        }
        // ثم وقت الإنشاء - Then creation time
        return a.createdAt.getTime() - b.createdAt.getTime();
      });
  }

  /**
   * حساب تأخير إعادة المحاولة مع Exponential Backoff
   * Calculate retry delay with exponential backoff
   */
  private calculateRetryDelay(attemptCount: number): number {
    const delay = Math.min(
      this.config.retryDelayBase * Math.pow(2, attemptCount - 1),
      this.config.retryDelayMax,
    );

    // إضافة عشوائية لتجنب تزامن إعادة المحاولات - Add jitter
    return delay + Math.random() * 1000;
  }

  /**
   * إزالة عملية من قائمة الانتظار
   * Remove operation from queue
   */
  private removeOperationFromQueue(operationId: string): void {
    const index = this.queue.findIndex((op) => op.id === operationId);
    if (index !== -1) {
      this.queue.splice(index, 1);
    }
  }

  /**
   * تنفيذ طلب HTTP
   * Execute HTTP request
   */
  private async executeRequest(operation: SyncOperation): Promise<any> {
    // هنا يتم تنفيذ الطلب الفعلي باستخدام fetch أو axios
    // This is where you'd implement the actual HTTP request using fetch or axios

    const url = `${this.getBaseUrl()}${operation.endpoint}${operation.entityId ? `/${operation.entityId}` : ""}`;

    // Use AbortController for broader compatibility (AbortSignal.timeout
    // is not available on older React Native / Hermes versions).
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeoutMs);

    let response: Response;
    try {
      response = await fetch(url, {
        method: operation.method,
        headers: {
          "Content-Type": "application/json",
          ...operation.headers,
        },
        body:
          operation.method !== "GET" && operation.method !== "DELETE"
            ? JSON.stringify(operation.data)
            : undefined,
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeoutId);
    }

    if (!response.ok) {
      // Try to parse error body, fall back to status text
      let errorBody: unknown;
      try { errorBody = await response.json(); } catch { errorBody = null; }
      return {
        status: response.status,
        statusText: response.statusText,
        data: errorBody,
      };
    }

    const data = await response.json();

    return {
      status: response.status,
      statusText: response.statusText,
      data,
    };
  }

  /**
   * الحصول على عنوان URL الأساسي
   * Get base API URL
   */
  private getBaseUrl(): string {
    // يجب تعيين هذا من الإعدادات - This should be set from config
    return process.env.API_BASE_URL || "https://api.sahool.app";
  }

  /**
   * إنشاء نتيجة مزامنة
   * Create sync result object
   */
  private createSyncResult(
    operation: SyncOperation,
    startTime: number,
    success: boolean,
    conflictDetected: boolean,
    serverResponse?: any,
    error?: Error,
    retryScheduled?: boolean,
    nextRetryAt?: Date,
  ): SyncResult {
    return {
      success,
      operationId: operation.id,
      timestamp: new Date(),
      duration: Date.now() - startTime,
      error,
      conflictDetected,
      serverResponse,
      retryScheduled,
      nextRetryAt,
    };
  }

  /**
   * إنشاء نتيجة دفعة فارغة
   * Create empty batch result
   */
  private createEmptyBatchResult(): BatchSyncResult {
    return {
      success: true,
      totalOperations: 0,
      successCount: 0,
      failedCount: 0,
      conflictCount: 0,
      skippedCount: 0,
      results: [],
      duration: 0,
      errors: [],
    };
  }

  /**
   * تنظيف وإيقاف المدير
   * Cleanup and shutdown
   */
  public async shutdown(): Promise<void> {
    console.log("🛑 إيقاف مدير المزامنة...");

    this.stopAutoSync();

    if (this.config.persistQueue) {
      await this.saveQueueToStorage();
    }

    await this.storage.saveStatistics(this.statistics);

    this.eventListeners.clear();
    this.customResolvers.clear();

    console.log("✅ تم إيقاف مدير المزامنة بنجاح");
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// محول التخزين - Storage Adapter
// ═══════════════════════════════════════════════════════════════════════════

/**
 * محول AsyncStorage
 * AsyncStorage implementation of ISyncStorage
 */
class AsyncStorageAdapter implements ISyncStorage {
  async saveQueue(operations: SyncOperation[]): Promise<void> {
    await AsyncStorage.setItem(STORAGE_KEYS.QUEUE, JSON.stringify(operations));
  }

  async loadQueue(): Promise<SyncOperation[]> {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.QUEUE);
    if (!data) return [];

    let operations: any[];
    try {
      operations = JSON.parse(data);
    } catch {
      // Corrupted queue data - reset to empty
      await AsyncStorage.removeItem(STORAGE_KEYS.QUEUE);
      return [];
    }
    if (!Array.isArray(operations)) return [];
    // تحويل التواريخ - Convert dates
    return operations.map((op: any) => ({
      ...op,
      createdAt: new Date(op.createdAt),
      updatedAt: new Date(op.updatedAt),
      scheduledAt: op.scheduledAt ? new Date(op.scheduledAt) : undefined,
      conflictData: op.conflictData
        ? {
            ...op.conflictData,
            detectedAt: new Date(op.conflictData.detectedAt),
            resolvedAt: op.conflictData.resolvedAt
              ? new Date(op.conflictData.resolvedAt)
              : undefined,
          }
        : undefined,
    }));
  }

  async clearQueue(): Promise<void> {
    await AsyncStorage.removeItem(STORAGE_KEYS.QUEUE);
  }

  async saveOperation(operation: SyncOperation): Promise<void> {
    const queue = await this.loadQueue();
    const index = queue.findIndex((op) => op.id === operation.id);

    if (index !== -1) {
      queue[index] = operation;
    } else {
      queue.push(operation);
    }

    await this.saveQueue(queue);
  }

  async removeOperation(operationId: string): Promise<void> {
    const queue = await this.loadQueue();
    const filtered = queue.filter((op) => op.id !== operationId);
    await this.saveQueue(filtered);
  }

  async updateOperation(
    operationId: string,
    updates: Partial<SyncOperation>,
  ): Promise<void> {
    const queue = await this.loadQueue();
    const index = queue.findIndex((op) => op.id === operationId);

    if (index !== -1) {
      queue[index] = { ...queue[index], ...updates };
      await this.saveQueue(queue);
    }
  }

  async getOperation(operationId: string): Promise<SyncOperation | null> {
    const queue = await this.loadQueue();
    return queue.find((op) => op.id === operationId) || null;
  }

  async saveLastSyncTime(time: Date): Promise<void> {
    await AsyncStorage.setItem(STORAGE_KEYS.LAST_SYNC, time.toISOString());
  }

  async getLastSyncTime(): Promise<Date | null> {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.LAST_SYNC);
    return data ? new Date(data) : null;
  }

  async saveStatistics(stats: SyncStatistics): Promise<void> {
    await AsyncStorage.setItem(STORAGE_KEYS.STATISTICS, JSON.stringify(stats));
  }

  async getStatistics(): Promise<SyncStatistics | null> {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.STATISTICS);
    if (!data) return null;

    let stats: any;
    try {
      stats = JSON.parse(data);
    } catch {
      // Corrupted statistics data - reset
      await AsyncStorage.removeItem(STORAGE_KEYS.STATISTICS);
      return null;
    }
    return {
      ...stats,
      firstSyncTime: stats.firstSyncTime
        ? new Date(stats.firstSyncTime)
        : undefined,
      lastSuccessfulSync: stats.lastSuccessfulSync
        ? new Date(stats.lastSuccessfulSync)
        : undefined,
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// التصدير - Exports
// ═══════════════════════════════════════════════════════════════════════════

export default SyncManager;
