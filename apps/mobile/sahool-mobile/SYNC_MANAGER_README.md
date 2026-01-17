# SAHOOL Mobile - Offline Sync Manager

# مدير المزامنة بدون اتصال - تطبيق ساهول المحمول

## 📋 نظرة عامة - Overview

A comprehensive offline-first synchronization manager for the SAHOOL mobile application. This system provides robust data synchronization capabilities with intelligent conflict resolution, priority-based queuing, and network-aware operations.

نظام شامل للمزامنة بدون اتصال لتطبيق ساهول المحمول. يوفر هذا النظام قدرات مزامنة بيانات قوية مع حل ذكي للتعارضات، قائمة انتظار تعتمد على الأولوية، وعمليات واعية بحالة الشبكة.

## 🎯 الميزات الرئيسية - Key Features

### 1. إدارة قائمة الانتظار - Queue Management

- ✅ Priority-based operation queuing (Critical, High, Normal, Low)
- ✅ Persistent queue storage with automatic recovery
- ✅ Automatic queue cleanup of completed operations
- ✅ Maximum queue size protection

### 2. حل التعارضات - Conflict Resolution

- ✅ Multiple resolution strategies:
  - **LAST_WRITE_WINS**: آخر كتابة تفوز (بناءً على الطابع الزمني)
  - **SERVER_WINS**: الخادم يفوز دائماً
  - **CLIENT_WINS**: العميل يفوز دائماً
  - **FIELD_LEVEL_MERGE**: دمج على مستوى الحقول
  - **MANUAL_MERGE**: دمج يدوي (يتطلب تدخل المستخدم)
  - **CUSTOM**: استراتيجية مخصصة
- ✅ Custom conflict resolvers per data type
- ✅ Automatic conflict detection with field-level comparison

### 3. إدارة الشبكة - Network Management

- ✅ Automatic network status detection (Online, Offline, Slow, Metered)
- ✅ WiFi-only sync option
- ✅ Connection throttling on slow/metered connections
- ✅ Automatic sync when network becomes available

### 4. إعادة المحاولة - Retry Logic

- ✅ Exponential backoff with jitter
- ✅ Configurable max retries
- ✅ Scheduled retry timing
- ✅ Automatic cleanup of failed operations after max retries

### 5. أنواع البيانات - Data Types Support

- ✅ Field observations (ملاحظات الحقول)
- ✅ Sensor readings (قراءات المستشعرات)
- ✅ Task completions (إكمال المهام)
- ✅ Image uploads (رفع الصور)
- ✅ Field updates (تحديثات الحقول)
- ✅ Farm updates (تحديثات المزارع)
- ✅ Irrigation logs (سجلات الري)
- ✅ Pest reports (تقارير الآفات)

### 6. الأحداث - Event System

- ✅ Real-time event notifications
- ✅ Event types: SYNC_STARTED, SYNC_COMPLETED, SYNC_FAILED, CONFLICT_DETECTED, etc.
- ✅ Custom event listeners
- ✅ React component integration support

### 7. الإحصائيات - Statistics & Monitoring

- ✅ Comprehensive sync statistics
- ✅ Real-time sync status
- ✅ Performance metrics
- ✅ Data usage tracking

## 📦 التثبيت - Installation

### المتطلبات - Dependencies

```bash
npm install @react-native-async-storage/async-storage
npm install @react-native-community/netinfo
```

أو باستخدام yarn:

```bash
yarn add @react-native-async-storage/async-storage
yarn add @react-native-community/netinfo
```

### الملفات المطلوبة - Required Files

```
src/
├── models/
│   └── syncTypes.ts          # جميع تعريفات الأنواع
└── services/
    ├── syncManager.ts        # المدير الرئيسي
    └── syncManager.example.ts # أمثلة الاستخدام
```

## 🚀 الاستخدام السريع - Quick Start

### 1. التهيئة - Initialization

```typescript
import SyncManager from "./services/syncManager";
import { ConflictResolutionStrategy } from "./models/syncTypes";

// تهيئة مدير المزامنة
const syncManager = SyncManager.getInstance({
  autoSync: true,
  syncInterval: 5 * 60 * 1000, // كل 5 دقائق
  maxRetries: 3,
  conflictResolution: ConflictResolutionStrategy.LAST_WRITE_WINS,
  syncOnlyOnWifi: false,
  throttleOnSlowConnection: true,
});
```

### 2. إضافة عمليات للمزامنة - Queue Operations

```typescript
import {
  SyncOperationType,
  SyncDataType,
  SyncPriority,
} from "./models/syncTypes";

// إضافة ملاحظة حقل جديدة
const operationId = await syncManager.queueOperation(
  SyncOperationType.CREATE,
  SyncDataType.FIELD_OBSERVATION,
  {
    fieldId: "field-123",
    observedAt: new Date(),
    observationType: "PEST_DETECTION",
    notes: "لوحظ وجود آفات على النباتات",
    userId: "user-456",
  },
  {
    priority: SyncPriority.HIGH,
  },
);
```

### 3. الاستماع للأحداث - Listen to Events

```typescript
import { SyncEventType } from "./models/syncTypes";

// الاستماع لإكمال المزامنة
syncManager.addEventListener(SyncEventType.SYNC_COMPLETED, (event) => {
  console.log("✅ اكتملت المزامنة:", event.data);
});

// الاستماع للتعارضات
syncManager.addEventListener(SyncEventType.CONFLICT_DETECTED, (event) => {
  console.warn("⚠️ تعارض:", event.operationId);
});
```

### 4. الحصول على الحالة - Get Status

```typescript
// الحصول على حالة المزامنة الحالية
const status = await syncManager.getSyncStatus();

console.log(`معلق: ${status.pendingCount}`);
console.log(`فاشل: ${status.failedCount}`);
console.log(`تعارضات: ${status.conflictCount}`);
```

## 📖 الأمثلة التفصيلية - Detailed Examples

### مثال 1: إضافة قراءة مستشعر

Example 1: Add Sensor Reading

```typescript
const reading = {
  sensorId: "sensor-789",
  fieldId: "field-123",
  readingType: "SOIL_MOISTURE",
  value: 45.5,
  unit: "%",
  timestamp: new Date(),
  quality: "GOOD",
};

await syncManager.queueOperation(
  SyncOperationType.CREATE,
  SyncDataType.SENSOR_READING,
  reading,
);
```

### مثال 2: إكمال مهمة

Example 2: Complete Task

```typescript
const completion = {
  taskId: "task-456",
  completedAt: new Date(),
  completedBy: "user-123",
  status: "COMPLETED",
  notes: "تم إكمال المهمة بنجاح",
  location: {
    latitude: 24.7136,
    longitude: 46.6753,
  },
};

await syncManager.queueOperation(
  SyncOperationType.CREATE,
  SyncDataType.TASK_COMPLETION,
  completion,
  {
    priority: SyncPriority.HIGH,
  },
);
```

### مثال 3: رفع صورة

Example 3: Upload Image

```typescript
const imageUpload = {
  localUri: "file:///path/to/image.jpg",
  entityType: SyncDataType.FIELD_OBSERVATION,
  entityId: "observation-123",
  size: 1024 * 500, // 500 KB
  mimeType: "image/jpeg",
};

await syncManager.queueOperation(
  SyncOperationType.UPLOAD,
  SyncDataType.IMAGE_UPLOAD,
  imageUpload,
  {
    priority: SyncPriority.LOW, // أولوية منخفضة للصور
  },
);
```

### مثال 4: محلل تعارض مخصص

Example 4: Custom Conflict Resolver

```typescript
syncManager.registerCustomResolver(
  SyncDataType.FIELD_OBSERVATION,
  async (local, server, base) => {
    // دمج ذكي - Smart merge
    return {
      ...server,
      notes: local.notes, // الملاحظات المحلية لها الأولوية
      images: [...new Set([...server.images, ...local.images])], // دمج الصور
      updatedAt: new Date(),
    };
  },
);
```

## 🎨 الاستخدام في React Components

### مثال: مكون حالة المزامنة

Example: Sync Status Component

```typescript
import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import SyncManager from './services/syncManager';
import { SyncEventType, SyncStatusInfo } from './models/syncTypes';

const SyncStatusBar = () => {
  const [status, setStatus] = useState<SyncStatusInfo | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    const syncManager = SyncManager.getInstance();

    // تحديث الحالة
    const updateStatus = async () => {
      const newStatus = await syncManager.getSyncStatus();
      setStatus(newStatus);
    };

    // الاستماع للأحداث
    syncManager.addEventListener(SyncEventType.SYNC_STARTED, () => {
      setIsSyncing(true);
    });

    syncManager.addEventListener(SyncEventType.SYNC_COMPLETED, () => {
      setIsSyncing(false);
      updateStatus();
    });

    syncManager.addEventListener(SyncEventType.NETWORK_STATUS_CHANGED, () => {
      updateStatus();
    });

    updateStatus();

    // تحديث دوري
    const interval = setInterval(updateStatus, 10000); // كل 10 ثواني

    return () => {
      clearInterval(interval);
      // إزالة المستمعين هنا
    };
  }, []);

  if (!status) return null;

  return (
    <View style={{ padding: 10, backgroundColor: '#f0f0f0' }}>
      <View style={{ flexDirection: 'row', alignItems: 'center' }}>
        {isSyncing && <ActivityIndicator size="small" />}
        <Text style={{ marginLeft: 10 }}>
          {status.isOnline ? '🌐 متصل' : '📴 غير متصل'}
        </Text>
      </View>

      {status.pendingCount > 0 && (
        <Text>معلق: {status.pendingCount} عملية</Text>
      )}

      {status.failedCount > 0 && (
        <Text style={{ color: 'red' }}>فاشل: {status.failedCount}</Text>
      )}

      {status.conflictCount > 0 && (
        <Text style={{ color: 'orange' }}>
          تعارضات: {status.conflictCount}
        </Text>
      )}

      {status.lastSyncTime && (
        <Text style={{ fontSize: 12, color: '#666' }}>
          آخر مزامنة: {status.lastSyncTime.toLocaleString('ar-SA')}
        </Text>
      )}
    </View>
  );
};

export default SyncStatusBar;
```

### مثال: نموذج إضافة ملاحظة

Example: Field Observation Form

```typescript
import React, { useState } from 'react';
import { View, TextInput, Button, Alert } from 'react-native';
import SyncManager from './services/syncManager';
import { SyncOperationType, SyncDataType } from './models/syncTypes';

const FieldObservationForm = ({ fieldId, userId }) => {
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!notes.trim()) {
      Alert.alert('خطأ', 'الرجاء إدخال الملاحظات');
      return;
    }

    setLoading(true);

    try {
      const syncManager = SyncManager.getInstance();

      await syncManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.FIELD_OBSERVATION,
        {
          fieldId,
          observedAt: new Date(),
          observationType: 'GENERAL',
          notes,
          userId,
        }
      );

      Alert.alert('نجاح', 'تم حفظ الملاحظة وستتم مزامنتها تلقائياً');
      setNotes('');
    } catch (error) {
      Alert.alert('خطأ', 'فشل حفظ الملاحظة');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <TextInput
        value={notes}
        onChangeText={setNotes}
        placeholder="أدخل ملاحظاتك هنا..."
        multiline
        numberOfLines={4}
        style={{
          borderWidth: 1,
          borderColor: '#ccc',
          padding: 10,
          marginBottom: 10,
        }}
      />

      <Button
        title={loading ? 'جاري الحفظ...' : 'حفظ'}
        onPress={handleSubmit}
        disabled={loading}
      />
    </View>
  );
};

export default FieldObservationForm;
```

## ⚙️ الإعدادات - Configuration

### جميع خيارات الإعدادات

All Configuration Options

```typescript
const config = {
  // المزامنة التلقائية - Auto sync
  autoSync: true, // تفعيل المزامنة التلقائية
  syncInterval: 5 * 60 * 1000, // فترة المزامنة (5 دقائق)

  // إعادة المحاولة - Retry
  maxRetries: 5, // الحد الأقصى لإعادة المحاولات
  retryDelayBase: 1000, // التأخير الأساسي (1 ثانية)
  retryDelayMax: 30000, // الحد الأقصى للتأخير (30 ثانية)

  // قائمة الانتظار - Queue
  batchSize: 10, // حجم الدفعة
  maxQueueSize: 1000, // الحد الأقصى لحجم قائمة الانتظار

  // حل التعارضات - Conflict resolution
  conflictResolution: ConflictResolutionStrategy.LAST_WRITE_WINS,

  // الشبكة - Network
  syncOnlyOnWifi: false, // المزامنة فقط على WiFi
  throttleOnSlowConnection: true, // تقليل السرعة على الاتصال البطيء

  // التخزين - Storage
  persistQueue: true, // حفظ قائمة الانتظار

  // إعدادات إضافية - Additional settings
  enableCompression: false, // تفعيل الضغط
  maxUploadSize: 10 * 1024 * 1024, // الحد الأقصى لحجم الرفع (10 MB)
  timeoutMs: 30000, // مهلة الطلب (30 ثانية)
};

const syncManager = SyncManager.getInstance(config);
```

## 🔧 واجهة برمجة التطبيقات - API Reference

### SyncManager Methods

#### `queueOperation(type, dataType, data, options?)`

إضافة عملية إلى قائمة الانتظار - Queue an operation for syncing

**Parameters:**

- `type`: SyncOperationType - نوع العملية
- `dataType`: SyncDataType - نوع البيانات
- `data`: Record<string, any> - البيانات
- `options`: Object (optional)
  - `priority`: SyncPriority
  - `entityId`: string
  - `endpoint`: string
  - `previousData`: Record<string, any>
  - `metadata`: Record<string, any>

**Returns:** `Promise<string>` - معرف العملية

#### `processQueue()`

معالجة قائمة الانتظار - Process the sync queue

**Returns:** `Promise<BatchSyncResult>`

#### `getSyncStatus()`

الحصول على حالة المزامنة - Get current sync status

**Returns:** `Promise<SyncStatusInfo>`

#### `getStatistics()`

الحصول على الإحصائيات - Get sync statistics

**Returns:** `SyncStatistics`

#### `getLastSyncTime()`

الحصول على وقت آخر مزامنة - Get last sync time

**Returns:** `Promise<Date | null>`

#### `startAutoSync()`

بدء المزامنة التلقائية - Start automatic sync

#### `stopAutoSync()`

إيقاف المزامنة التلقائية - Stop automatic sync

#### `pause()`

إيقاف المزامنة مؤقتاً - Pause sync operations

#### `resume()`

استئناف المزامنة - Resume sync operations

#### `forceSync()`

مزامنة فورية - Force immediate sync

**Returns:** `Promise<BatchSyncResult>`

#### `clearCompletedOperations()`

حذف العمليات المكتملة - Clear completed operations

**Returns:** `Promise<number>` - عدد العمليات المحذوفة

#### `registerCustomResolver(dataType, resolver)`

تسجيل محلل تعارض مخصص - Register custom conflict resolver

**Parameters:**

- `dataType`: SyncDataType
- `resolver`: CustomConflictResolver

#### `addEventListener(type, listener)`

الاستماع لحدث معين - Listen to a specific event

**Parameters:**

- `type`: SyncEventType
- `listener`: SyncEventListener

#### `removeEventListener(type, listener)`

إزالة مستمع حدث - Remove event listener

**Parameters:**

- `type`: SyncEventType
- `listener`: SyncEventListener

## 📊 أنواع الأحداث - Event Types

```typescript
enum SyncEventType {
  SYNC_STARTED = "SYNC_STARTED",
  SYNC_COMPLETED = "SYNC_COMPLETED",
  SYNC_FAILED = "SYNC_FAILED",
  OPERATION_QUEUED = "OPERATION_QUEUED",
  OPERATION_COMPLETED = "OPERATION_COMPLETED",
  OPERATION_FAILED = "OPERATION_FAILED",
  CONFLICT_DETECTED = "CONFLICT_DETECTED",
  CONFLICT_RESOLVED = "CONFLICT_RESOLVED",
  NETWORK_STATUS_CHANGED = "NETWORK_STATUS_CHANGED",
  QUEUE_CLEARED = "QUEUE_CLEARED",
}
```

## 🎯 أفضل الممارسات - Best Practices

### 1. تحديد الأولوية بشكل صحيح

Set Priorities Correctly

```typescript
// عمليات حرجة - Critical operations
SyncPriority.CRITICAL; // حذف البيانات

// أولوية عالية - High priority
SyncPriority.HIGH; // إكمال المهام

// أولوية عادية - Normal priority
SyncPriority.NORMAL; // ملاحظات الحقول

// أولوية منخفضة - Low priority
SyncPriority.LOW; // رفع الصور
```

### 2. استخدام البيانات السابقة للكشف عن التعارضات

Use Previous Data for Conflict Detection

```typescript
await syncManager.queueOperation(
  SyncOperationType.UPDATE,
  SyncDataType.FIELD_OBSERVATION,
  updatedData,
  {
    entityId: "observation-123",
    previousData: originalData, // مهم للكشف عن التعارضات
  },
);
```

### 3. الاستماع للأحداث المهمة

Listen to Important Events

```typescript
// الاستماع لفشل المزامنة
syncManager.addEventListener(SyncEventType.SYNC_FAILED, (event) => {
  // إخطار المستخدم
  Alert.alert("خطأ في المزامنة", "الرجاء المحاولة لاحقاً");
});

// الاستماع للتعارضات
syncManager.addEventListener(SyncEventType.CONFLICT_DETECTED, (event) => {
  // طلب تدخل المستخدم
  showConflictResolutionDialog(event.operationId);
});
```

### 4. تنظيف العمليات المكتملة بشكل دوري

Regularly Clean Completed Operations

```typescript
// تنظيف يومي
setInterval(
  () => {
    syncManager.clearCompletedOperations();
  },
  24 * 60 * 60 * 1000,
); // كل 24 ساعة
```

### 5. إدارة المزامنة حسب نوع الاتصال

Manage Sync Based on Connection Type

```typescript
const syncManager = SyncManager.getInstance({
  syncOnlyOnWifi: true, // مناسب لرفع الصور الكبيرة
  throttleOnSlowConnection: true, // تقليل الحمل على الاتصال البطيء
});
```

## 🐛 استكشاف الأخطاء - Troubleshooting

### المشكلة: العمليات لا تتزامن

Problem: Operations not syncing

**الحل - Solution:**

```typescript
// 1. تحقق من حالة الشبكة
const status = await syncManager.getSyncStatus();
console.log("Online:", status.isOnline);

// 2. تحقق من حالة المزامنة
console.log("Status:", status.status);
console.log("Is Syncing:", status.isSyncing);

// 3. فرض المزامنة
await syncManager.forceSync();
```

### المشكلة: تعارضات متكررة

Problem: Frequent conflicts

**الحل - Solution:**

```typescript
// استخدم استراتيجية حل مناسبة
const syncManager = SyncManager.getInstance({
  conflictResolution: ConflictResolutionStrategy.SERVER_WINS,
  // أو سجل محلل مخصص
});

syncManager.registerCustomResolver(dataType, customResolver);
```

### المشكلة: قائمة الانتظار ممتلئة

Problem: Queue full

**الحل - Solution:**

```typescript
// 1. نظف العمليات المكتملة
await syncManager.clearCompletedOperations();

// 2. زد الحد الأقصى
const syncManager = SyncManager.getInstance({
  maxQueueSize: 2000, // زيادة الحد الأقصى
});
```

## 📝 الملاحظات - Notes

1. **الأداء - Performance**: النظام مُحسّن للتعامل مع آلاف العمليات
2. **الأمان - Security**: تأكد من تشفير البيانات الحساسة قبل التخزين
3. **الاختبار - Testing**: اختبر على شبكات بطيئة ومتقطعة
4. **المراقبة - Monitoring**: راقب الإحصائيات بشكل دوري

## 🔗 الملفات ذات الصلة - Related Files

- `src/models/syncTypes.ts` - جميع تعريفات الأنواع
- `src/services/syncManager.ts` - المدير الرئيسي
- `src/services/syncManager.example.ts` - أمثلة الاستخدام

## 📞 الدعم - Support

للمساعدة والدعم، يرجى مراجعة الوثائق أو الاتصال بفريق التطوير.

For help and support, please refer to the documentation or contact the development team.

---

**نسخة - Version:** 1.0.0
**آخر تحديث - Last Updated:** 2026-01-02
**المطور - Developer:** SAHOOL Development Team
