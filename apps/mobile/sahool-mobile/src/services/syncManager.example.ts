/**
 * SAHOOL Mobile - Sync Manager Usage Examples
 * أمثلة استخدام مدير المزامنة
 *
 * This file demonstrates how to use the SyncManager in your application
 */

import SyncManager from "./syncManager";
import {
  SyncDataType,
  SyncOperationType,
  SyncPriority,
  ConflictResolutionStrategy,
  SyncEventType,
  FieldObservation,
  SensorReading,
  TaskCompletion,
  ImageUpload,
} from "../models/syncTypes";

// ═══════════════════════════════════════════════════════════════════════════
// التهيئة - Initialization
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال 1: تهيئة مدير المزامنة
 * Example 1: Initialize sync manager
 */
export function initializeSyncManager() {
  const syncManager = SyncManager.getInstance({
    autoSync: true,
    syncInterval: 5 * 60 * 1000, // كل 5 دقائق - Every 5 minutes
    maxRetries: 3,
    conflictResolution: ConflictResolutionStrategy.LAST_WRITE_WINS,
    syncOnlyOnWifi: false,
    throttleOnSlowConnection: true,
  });

  console.log("✅ تم تهيئة مدير المزامنة");
  return syncManager;
}

// ═══════════════════════════════════════════════════════════════════════════
// ملاحظات الحقول - Field Observations
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال 2: إضافة ملاحظة حقل جديدة
 * Example 2: Queue a new field observation
 */
export async function createFieldObservation() {
  const syncManager = SyncManager.getInstance();

  const observation: FieldObservation = {
    fieldId: "field-123",
    observedAt: new Date(),
    observationType: "PEST_DETECTION",
    notes: "لوحظ وجود آفات على النباتات في القطاع الشمالي",
    images: ["local://image1.jpg", "local://image2.jpg"],
    location: {
      latitude: 24.7136,
      longitude: 46.6753,
    },
    userId: "user-456",
  };

  try {
    const operationId = await syncManager.queueOperation(
      SyncOperationType.CREATE,
      SyncDataType.FIELD_OBSERVATION,
      observation,
      {
        priority: SyncPriority.HIGH,
      },
    );

    console.log(`✅ تمت إضافة ملاحظة الحقل للمزامنة: ${operationId}`);
    return operationId;
  } catch (error) {
    console.error("❌ خطأ في إضافة ملاحظة الحقل:", error);
    throw error;
  }
}

/**
 * مثال 3: تحديث ملاحظة حقل موجودة
 * Example 3: Update existing field observation
 */
export async function updateFieldObservation(observationId: string) {
  const syncManager = SyncManager.getInstance();

  const previousData = {
    notes: "ملاحظات قديمة",
    updatedAt: new Date("2024-01-01"),
  };

  const updatedData = {
    id: observationId,
    notes: "تم معالجة الآفات بنجاح",
    updatedAt: new Date(),
    status: "RESOLVED",
  };

  try {
    const operationId = await syncManager.queueOperation(
      SyncOperationType.UPDATE,
      SyncDataType.FIELD_OBSERVATION,
      updatedData,
      {
        entityId: observationId,
        previousData, // للكشف عن التعارضات - For conflict detection
        priority: SyncPriority.NORMAL,
      },
    );

    console.log(`✅ تم تحديث ملاحظة الحقل: ${operationId}`);
    return operationId;
  } catch (error) {
    console.error("❌ خطأ في تحديث ملاحظة الحقل:", error);
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// قراءات المستشعرات - Sensor Readings
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال 4: إضافة قراءة مستشعر
 * Example 4: Queue sensor reading
 */
export async function createSensorReading() {
  const syncManager = SyncManager.getInstance();

  const reading: SensorReading = {
    sensorId: "sensor-789",
    fieldId: "field-123",
    readingType: "SOIL_MOISTURE",
    value: 45.5,
    unit: "%",
    timestamp: new Date(),
    quality: "GOOD",
    metadata: {
      batteryLevel: 85,
      signalStrength: -65,
    },
  };

  try {
    const operationId = await syncManager.queueOperation(
      SyncOperationType.CREATE,
      SyncDataType.SENSOR_READING,
      reading,
      {
        priority: SyncPriority.NORMAL,
      },
    );

    console.log(`✅ تمت إضافة قراءة المستشعر للمزامنة: ${operationId}`);
    return operationId;
  } catch (error) {
    console.error("❌ خطأ في إضافة قراءة المستشعر:", error);
    throw error;
  }
}

/**
 * مثال 5: إضافة قراءات متعددة دفعة واحدة
 * Example 5: Queue multiple sensor readings at once
 */
export async function createMultipleSensorReadings(readings: SensorReading[]) {
  const syncManager = SyncManager.getInstance();
  const operationIds: string[] = [];

  for (const reading of readings) {
    try {
      const id = await syncManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.SENSOR_READING,
        reading,
      );
      operationIds.push(id);
    } catch (error) {
      console.error("❌ خطأ في إضافة قراءة:", error);
    }
  }

  console.log(`✅ تمت إضافة ${operationIds.length} قراءة للمزامنة`);
  return operationIds;
}

// ═══════════════════════════════════════════════════════════════════════════
// إكمال المهام - Task Completions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال 6: إكمال مهمة
 * Example 6: Complete a task
 */
export async function completeTask(taskId: string, userId: string) {
  const syncManager = SyncManager.getInstance();

  const completion: TaskCompletion = {
    taskId,
    completedAt: new Date(),
    completedBy: userId,
    status: "COMPLETED",
    notes: "تم إكمال المهمة بنجاح",
    attachments: ["local://photo1.jpg"],
    location: {
      latitude: 24.7136,
      longitude: 46.6753,
    },
  };

  try {
    const operationId = await syncManager.queueOperation(
      SyncOperationType.CREATE,
      SyncDataType.TASK_COMPLETION,
      completion,
      {
        priority: SyncPriority.HIGH, // أولوية عالية لإكمال المهام
      },
    );

    console.log(`✅ تم تسجيل إكمال المهمة: ${operationId}`);
    return operationId;
  } catch (error) {
    console.error("❌ خطأ في تسجيل إكمال المهمة:", error);
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// رفع الصور - Image Uploads
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال 7: رفع صورة
 * Example 7: Upload an image
 */
export async function uploadImage(
  localUri: string,
  entityType: SyncDataType,
  entityId: string,
) {
  const syncManager = SyncManager.getInstance();

  const imageUpload: ImageUpload = {
    localUri,
    entityType,
    entityId,
    size: 1024 * 500, // 500 KB
    mimeType: "image/jpeg",
    metadata: {
      capturedAt: new Date(),
      deviceModel: "iPhone 13",
    },
  };

  try {
    const operationId = await syncManager.queueOperation(
      SyncOperationType.UPLOAD,
      SyncDataType.IMAGE_UPLOAD,
      imageUpload,
      {
        priority: SyncPriority.LOW, // أولوية منخفضة للصور
      },
    );

    console.log(`✅ تمت إضافة الصورة للرفع: ${operationId}`);
    return operationId;
  } catch (error) {
    console.error("❌ خطأ في إضافة الصورة للرفع:", error);
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// حل التعارضات - Conflict Resolution
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال 8: تسجيل محلل تعارض مخصص
 * Example 8: Register custom conflict resolver
 */
export function registerCustomConflictResolver() {
  const syncManager = SyncManager.getInstance();

  // محلل مخصص لملاحظات الحقول - Custom resolver for field observations
  syncManager.registerCustomResolver(
    SyncDataType.FIELD_OBSERVATION,
    async (local, server, base) => {
      console.log("🔧 حل تعارض ملاحظة الحقل...");

      // دمج ذكي - Smart merge
      const merged = {
        ...server,
        notes: local.notes, // الملاحظات المحلية لها الأولوية
        images: [
          ...new Set([...(server.images || []), ...(local.images || [])]),
        ], // دمج الصور
        updatedAt: new Date(), // تحديث الوقت
      };

      console.log("✅ تم حل التعارض بنجاح");
      return merged;
    },
  );

  console.log("✅ تم تسجيل محلل التعارض المخصص");
}

// ═══════════════════════════════════════════════════════════════════════════
// الأحداث - Events
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال 9: الاستماع لأحداث المزامنة
 * Example 9: Listen to sync events
 */
export function setupSyncEventListeners() {
  const syncManager = SyncManager.getInstance();

  // الاستماع لبدء المزامنة - Listen for sync start
  syncManager.addEventListener(SyncEventType.SYNC_STARTED, (event) => {
    console.log("🔄 بدأت المزامنة في:", event.timestamp);
    // تحديث واجهة المستخدم - Update UI
  });

  // الاستماع لإكمال المزامنة - Listen for sync completion
  syncManager.addEventListener(SyncEventType.SYNC_COMPLETED, (event) => {
    console.log("✅ اكتملت المزامنة:", event.data);
    // إخطار المستخدم - Notify user
  });

  // الاستماع لفشل المزامنة - Listen for sync failure
  syncManager.addEventListener(SyncEventType.SYNC_FAILED, (event) => {
    console.error("❌ فشلت المزامنة:", event.data);
    // عرض رسالة خطأ - Show error message
  });

  // الاستماع لتعارضات - Listen for conflicts
  syncManager.addEventListener(SyncEventType.CONFLICT_DETECTED, (event) => {
    console.warn("⚠️ تم اكتشاف تعارض:", event.operationId);
    // طلب تدخل المستخدم - Request user intervention
  });

  // الاستماع لتغيير حالة الشبكة - Listen for network changes
  syncManager.addEventListener(
    SyncEventType.NETWORK_STATUS_CHANGED,
    (event) => {
      console.log("🌐 تغيرت حالة الشبكة:", event.data);
      // تحديث شريط الحالة - Update status bar
    },
  );

  console.log("✅ تم إعداد مستمعي الأحداث");
}

// ═══════════════════════════════════════════════════════════════════════════
// التحكم في المزامنة - Sync Control
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال 10: التحكم في المزامنة التلقائية
 * Example 10: Control automatic sync
 */
export function controlAutoSync() {
  const syncManager = SyncManager.getInstance();

  // إيقاف المزامنة التلقائية - Stop auto sync
  syncManager.stopAutoSync();
  console.log("⏹️ تم إيقاف المزامنة التلقائية");

  // بدء المزامنة التلقائية - Start auto sync
  syncManager.startAutoSync();
  console.log("▶️ تم بدء المزامنة التلقائية");

  // إيقاف مؤقت - Pause
  syncManager.pause();
  console.log("⏸️ تم إيقاف المزامنة مؤقتاً");

  // استئناف - Resume
  syncManager.resume();
  console.log("▶️ تم استئناف المزامنة");
}

/**
 * مثال 11: مزامنة فورية
 * Example 11: Force immediate sync
 */
export async function forceSyncNow() {
  const syncManager = SyncManager.getInstance();

  console.log("🔄 بدء المزامنة الفورية...");

  try {
    const result = await syncManager.forceSync();

    console.log(`✅ اكتملت المزامنة الفورية:`);
    console.log(`   - ناجحة: ${result.successCount}`);
    console.log(`   - فاشلة: ${result.failedCount}`);
    console.log(`   - تعارضات: ${result.conflictCount}`);
    console.log(`   - المدة: ${result.duration}ms`);

    return result;
  } catch (error) {
    console.error("❌ خطأ في المزامنة الفورية:", error);
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// الحالة والإحصائيات - Status & Statistics
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال 12: الحصول على حالة المزامنة
 * Example 12: Get sync status
 */
export async function getSyncStatus() {
  const syncManager = SyncManager.getInstance();

  const status = await syncManager.getSyncStatus();

  console.log("📊 حالة المزامنة:");
  console.log(`   - الحالة: ${status.status}`);
  console.log(`   - متصل: ${status.isOnline ? "نعم" : "لا"}`);
  console.log(`   - جاري المزامنة: ${status.isSyncing ? "نعم" : "لا"}`);
  console.log(`   - معلق: ${status.pendingCount}`);
  console.log(`   - فاشل: ${status.failedCount}`);
  console.log(`   - تعارضات: ${status.conflictCount}`);
  console.log(`   - آخر مزامنة: ${status.lastSyncTime}`);

  if (status.syncProgress !== undefined) {
    console.log(`   - التقدم: ${status.syncProgress}%`);
  }

  return status;
}

/**
 * مثال 13: الحصول على الإحصائيات
 * Example 13: Get statistics
 */
export function getStatistics() {
  const syncManager = SyncManager.getInstance();

  const stats = syncManager.getStatistics();

  console.log("📈 إحصائيات المزامنة:");
  console.log(`   - إجمالي العمليات: ${stats.totalOperations}`);
  console.log(`   - ناجحة: ${stats.successfulOperations}`);
  console.log(`   - فاشلة: ${stats.failedOperations}`);
  console.log(`   - تعارضات: ${stats.conflictOperations}`);
  console.log(`   - متوسط الوقت: ${stats.averageSyncTime}ms`);
  console.log(
    `   - إجمالي البيانات: ${(stats.totalDataSynced / 1024).toFixed(2)} KB`,
  );

  return stats;
}

/**
 * مثال 14: حذف العمليات المكتملة
 * Example 14: Clear completed operations
 */
export async function clearCompleted() {
  const syncManager = SyncManager.getInstance();

  const clearedCount = await syncManager.clearCompletedOperations();

  console.log(`🗑️ تم حذف ${clearedCount} عملية مكتملة`);

  return clearedCount;
}

// ═══════════════════════════════════════════════════════════════════════════
// استخدام في React Component
// React Component Usage
// ═══════════════════════════════════════════════════════════════════════════

/**
 * مثال 15: استخدام في مكون React
 * Example 15: Usage in a React component
 */
export const ExampleComponent = () => {
  /*
  import React, { useEffect, useState } from 'react';
  import SyncManager from './services/syncManager';
  import { SyncStatusInfo, SyncEventType } from './models/syncTypes';

  const FieldObservationForm = () => {
    const [syncStatus, setSyncStatus] = useState<SyncStatusInfo | null>(null);
    const [isSyncing, setIsSyncing] = useState(false);

    useEffect(() => {
      const syncManager = SyncManager.getInstance();

      // تحديث الحالة - Update status
      const updateStatus = async () => {
        const status = await syncManager.getSyncStatus();
        setSyncStatus(status);
      };

      // الاستماع للأحداث - Listen to events
      syncManager.addEventListener(SyncEventType.SYNC_STARTED, () => {
        setIsSyncing(true);
      });

      syncManager.addEventListener(SyncEventType.SYNC_COMPLETED, () => {
        setIsSyncing(false);
        updateStatus();
      });

      updateStatus();

      // التنظيف - Cleanup
      return () => {
        // إزالة المستمعين - Remove listeners
      };
    }, []);

    const handleSubmit = async (observation: FieldObservation) => {
      const syncManager = SyncManager.getInstance();

      try {
        await syncManager.queueOperation(
          SyncOperationType.CREATE,
          SyncDataType.FIELD_OBSERVATION,
          observation
        );

        // إظهار رسالة نجاح - Show success message
        alert('تم حفظ الملاحظة وستتم مزامنتها تلقائياً');
      } catch (error) {
        // إظهار رسالة خطأ - Show error message
        alert('خطأ في حفظ الملاحظة');
      }
    };

    return (
      <View>
        {isSyncing && <Text>جاري المزامنة...</Text>}
        {syncStatus && (
          <Text>
            معلق: {syncStatus.pendingCount} | فاشل: {syncStatus.failedCount}
          </Text>
        )}
      </View>
    );
  };
  */
};

// ═══════════════════════════════════════════════════════════════════════════
// تصدير الأمثلة
// Export Examples
// ═══════════════════════════════════════════════════════════════════════════

export default {
  initializeSyncManager,
  createFieldObservation,
  updateFieldObservation,
  createSensorReading,
  createMultipleSensorReadings,
  completeTask,
  uploadImage,
  registerCustomConflictResolver,
  setupSyncEventListeners,
  controlAutoSync,
  forceSyncNow,
  getSyncStatus,
  getStatistics,
  clearCompleted,
};
