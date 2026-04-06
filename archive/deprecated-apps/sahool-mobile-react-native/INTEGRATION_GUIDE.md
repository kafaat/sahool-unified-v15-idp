# SAHOOL Sync Manager - Integration Guide

# دليل دمج مدير المزامنة - تطبيق ساهول

## 📋 Overview - نظرة عامة

This guide explains how to integrate the TypeScript/React Native Sync Manager into your application, whether you're starting fresh or migrating from the existing Flutter implementation.

يشرح هذا الدليل كيفية دمج مدير المزامنة TypeScript/React Native في تطبيقك، سواء كنت تبدأ من الصفر أو تنتقل من تطبيق Flutter الحالي.

## 🔄 Migration from Flutter - الانتقال من Flutter

### Current Flutter Implementation

The SAHOOL mobile app currently has Flutter-based sync functionality:

- `/apps/mobile/lib/core/offline/offline_sync_engine.dart`
- `/apps/mobile/lib/core/offline/sync_conflict_resolver.dart`
- `/apps/mobile/lib/core/sync/queue_manager.dart`

### Migration Strategy

#### Option 1: Complete Migration to React Native

If you're planning to migrate the entire app to React Native:

1. **Phase 1**: Set up React Native project structure
2. **Phase 2**: Implement core services (auth, storage, network)
3. **Phase 3**: Integrate the Sync Manager
4. **Phase 4**: Migrate UI components
5. **Phase 5**: Testing and deployment

#### Option 2: Keep Flutter, Use Concepts

If staying with Flutter, use this TypeScript implementation as a reference:

1. **Adapt patterns**: Apply the same architectural patterns to Dart
2. **Enhance existing**: Improve current Flutter sync with new strategies
3. **Add features**: Implement missing features like custom resolvers

## 🚀 Fresh Integration - دمج جديد

### Step 1: Install Dependencies

```bash
cd apps/mobile/sahool-mobile

# Install required packages
npm install @react-native-async-storage/async-storage
npm install @react-native-community/netinfo

# Install TypeScript dependencies
npm install --save-dev typescript @types/react @types/react-native
```

### Step 2: Initialize Sync Manager in App

Create `src/App.tsx`:

```typescript
import React, { useEffect } from 'react';
import { SafeAreaView, StatusBar } from 'react-native';
import SyncManager from './services/syncManager';
import { ConflictResolutionStrategy } from './models/syncTypes';

const App = () => {
  useEffect(() => {
    // Initialize sync manager on app start
    const syncManager = SyncManager.getInstance({
      autoSync: true,
      syncInterval: 5 * 60 * 1000, // 5 minutes
      maxRetries: 3,
      conflictResolution: ConflictResolutionStrategy.LAST_WRITE_WINS,
      syncOnlyOnWifi: false,
      throttleOnSlowConnection: true,
    });

    console.log('✅ Sync Manager initialized');

    // Cleanup on unmount
    return () => {
      syncManager.shutdown();
    };
  }, []);

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <StatusBar barStyle="dark-content" />
      {/* Your app components */}
    </SafeAreaView>
  );
};

export default App;
```

### Step 3: Create API Client Integration

Create `src/services/apiClient.ts`:

```typescript
import SyncManager from "./syncManager";
import {
  SyncOperationType,
  SyncDataType,
  SyncPriority,
} from "../models/syncTypes";

class APIClient {
  private syncManager: SyncManager;
  private baseURL: string;
  private authToken: string | null = null;

  constructor() {
    this.syncManager = SyncManager.getInstance();
    this.baseURL = process.env.API_BASE_URL || "https://api.sahool.com";
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  // Field Observations API
  async createFieldObservation(observation: any) {
    return await this.syncManager.queueOperation(
      SyncOperationType.CREATE,
      SyncDataType.FIELD_OBSERVATION,
      observation,
      {
        priority: SyncPriority.HIGH,
        endpoint: "/api/v1/field-observations",
        metadata: {
          timestamp: new Date().toISOString(),
        },
      },
    );
  }

  async updateFieldObservation(id: string, data: any, previousData?: any) {
    return await this.syncManager.queueOperation(
      SyncOperationType.UPDATE,
      SyncDataType.FIELD_OBSERVATION,
      data,
      {
        entityId: id,
        previousData,
        priority: SyncPriority.NORMAL,
        endpoint: `/api/v1/field-observations/${id}`,
      },
    );
  }

  // Sensor Readings API
  async createSensorReading(reading: any) {
    return await this.syncManager.queueOperation(
      SyncOperationType.CREATE,
      SyncDataType.SENSOR_READING,
      reading,
      {
        priority: SyncPriority.NORMAL,
        endpoint: "/api/v1/sensor-readings",
      },
    );
  }

  // Task Completions API
  async completeTask(taskId: string, completion: any) {
    return await this.syncManager.queueOperation(
      SyncOperationType.CREATE,
      SyncDataType.TASK_COMPLETION,
      { ...completion, taskId },
      {
        priority: SyncPriority.HIGH,
        endpoint: `/api/v1/tasks/${taskId}/complete`,
      },
    );
  }

  // Image Uploads API
  async uploadImage(imageData: any) {
    return await this.syncManager.queueOperation(
      SyncOperationType.UPLOAD,
      SyncDataType.IMAGE_UPLOAD,
      imageData,
      {
        priority: SyncPriority.LOW,
        endpoint: "/api/v1/images",
      },
    );
  }
}

export default new APIClient();
```

### Step 4: Create Custom Hooks for React

Create `src/hooks/useSync.ts`:

```typescript
import { useState, useEffect } from "react";
import SyncManager from "../services/syncManager";
import {
  SyncStatusInfo,
  SyncEventType,
  SyncStatistics,
} from "../models/syncTypes";

export const useSyncStatus = () => {
  const [status, setStatus] = useState<SyncStatusInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const syncManager = SyncManager.getInstance();

    const updateStatus = async () => {
      try {
        const newStatus = await syncManager.getSyncStatus();
        setStatus(newStatus);
      } finally {
        setLoading(false);
      }
    };

    // Initial load
    updateStatus();

    // Listen for changes
    const onSyncCompleted = () => updateStatus();
    const onNetworkChange = () => updateStatus();

    syncManager.addEventListener(SyncEventType.SYNC_COMPLETED, onSyncCompleted);
    syncManager.addEventListener(
      SyncEventType.NETWORK_STATUS_CHANGED,
      onNetworkChange,
    );

    // Update every 10 seconds
    const interval = setInterval(updateStatus, 10000);

    return () => {
      clearInterval(interval);
      syncManager.removeEventListener(
        SyncEventType.SYNC_COMPLETED,
        onSyncCompleted,
      );
      syncManager.removeEventListener(
        SyncEventType.NETWORK_STATUS_CHANGED,
        onNetworkChange,
      );
    };
  }, []);

  return { status, loading };
};

export const useSyncStatistics = () => {
  const [stats, setStats] = useState<SyncStatistics | null>(null);

  useEffect(() => {
    const syncManager = SyncManager.getInstance();

    const updateStats = () => {
      const newStats = syncManager.getStatistics();
      setStats(newStats);
    };

    // Initial load
    updateStats();

    // Listen for sync completion
    syncManager.addEventListener(SyncEventType.SYNC_COMPLETED, updateStats);

    return () => {
      syncManager.removeEventListener(
        SyncEventType.SYNC_COMPLETED,
        updateStats,
      );
    };
  }, []);

  return stats;
};

export const useForceSync = () => {
  const [syncing, setSyncing] = useState(false);

  const forceSync = async () => {
    setSyncing(true);
    try {
      const syncManager = SyncManager.getInstance();
      await syncManager.forceSync();
    } finally {
      setSyncing(false);
    }
  };

  return { forceSync, syncing };
};
```

### Step 5: Create UI Components

Create `src/components/SyncStatusBar.tsx`:

```typescript
import React from 'react';
import { View, Text, ActivityIndicator, TouchableOpacity, StyleSheet } from 'react-native';
import { useSyncStatus, useForceSync } from '../hooks/useSync';

const SyncStatusBar = () => {
  const { status, loading } = useSyncStatus();
  const { forceSync, syncing } = useForceSync();

  if (loading || !status) {
    return null;
  }

  const getStatusColor = () => {
    if (!status.isOnline) return '#FF6B6B';
    if (status.isSyncing) return '#4ECDC4';
    if (status.failedCount > 0) return '#FFA500';
    if (status.conflictCount > 0) return '#FFD93D';
    return '#6BCF7F';
  };

  const getStatusText = () => {
    if (!status.isOnline) return 'غير متصل';
    if (status.isSyncing) return 'جاري المزامنة...';
    if (status.pendingCount > 0) return `معلق: ${status.pendingCount}`;
    return 'متزامن';
  };

  return (
    <View style={[styles.container, { backgroundColor: getStatusColor() }]}>
      <View style={styles.content}>
        {status.isSyncing && <ActivityIndicator size="small" color="#FFF" />}

        <Text style={styles.statusText}>{getStatusText()}</Text>

        {status.pendingCount > 0 && !status.isSyncing && (
          <TouchableOpacity
            onPress={forceSync}
            disabled={syncing}
            style={styles.syncButton}
          >
            <Text style={styles.syncButtonText}>
              {syncing ? 'جاري...' : 'مزامنة الآن'}
            </Text>
          </TouchableOpacity>
        )}
      </View>

      {status.failedCount > 0 && (
        <Text style={styles.errorText}>فشل: {status.failedCount}</Text>
      )}

      {status.conflictCount > 0 && (
        <Text style={styles.warningText}>تعارضات: {status.conflictCount}</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 12,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statusText: {
    color: '#FFF',
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
  },
  syncButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  syncButtonText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: '600',
  },
  errorText: {
    color: '#FFF',
    fontSize: 12,
    marginTop: 4,
  },
  warningText: {
    color: '#FFF',
    fontSize: 12,
    marginTop: 4,
  },
});

export default SyncStatusBar;
```

## 🔧 Advanced Integration - دمج متقدم

### Background Sync Setup

For iOS, add to `ios/YourApp/Info.plist`:

```xml
<key>UIBackgroundModes</key>
<array>
  <string>fetch</string>
  <string>processing</string>
</array>
```

For Android, add to `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### Conflict Resolution UI

Create a component to handle manual conflict resolution:

```typescript
import React from 'react';
import { View, Text, Button } from 'react-native';
import SyncManager from '../services/syncManager';

const ConflictResolver = ({ operationId, conflictData }) => {
  const handleResolve = async (useLocal: boolean) => {
    const syncManager = SyncManager.getInstance();

    // Get operation
    const operation = await syncManager.getOperation(operationId);

    if (!operation || !operation.conflictData) return;

    // Resolve with user choice
    const resolved = useLocal
      ? operation.conflictData.localVersion
      : operation.conflictData.serverVersion;

    // Update operation with resolved data
    operation.data = resolved;
    operation.conflictData.resolvedData = resolved;
    operation.conflictData.resolvedAt = new Date();
    operation.conflictData.resolvedBy = 'USER';

    // Retry sync
    await syncManager.forceSync();
  };

  return (
    <View>
      <Text>تم اكتشاف تعارض</Text>
      <Text>الحقول المتعارضة: {conflictData.conflictingFields.join(', ')}</Text>

      <Button title="استخدام النسخة المحلية" onPress={() => handleResolve(true)} />
      <Button title="استخدام نسخة الخادم" onPress={() => handleResolve(false)} />
    </View>
  );
};

export default ConflictResolver;
```

## 📊 Monitoring & Analytics

### Setup Analytics Integration

```typescript
import SyncManager from "./services/syncManager";
import { SyncEventType } from "./models/syncTypes";
import Analytics from "./services/analytics"; // Your analytics service

const setupSyncAnalytics = () => {
  const syncManager = SyncManager.getInstance();

  // Track sync events
  syncManager.addEventListener(SyncEventType.SYNC_COMPLETED, (event) => {
    Analytics.track("Sync Completed", {
      successCount: event.data.successCount,
      failedCount: event.data.failedCount,
      duration: event.data.duration,
    });
  });

  syncManager.addEventListener(SyncEventType.SYNC_FAILED, (event) => {
    Analytics.track("Sync Failed", {
      error: event.data.message,
    });
  });

  syncManager.addEventListener(SyncEventType.CONFLICT_DETECTED, (event) => {
    Analytics.track("Conflict Detected", {
      operationId: event.operationId,
    });
  });
};

export default setupSyncAnalytics;
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test syncManager.test.ts
```

### Integration Testing

```typescript
import SyncManager from "./services/syncManager";
import apiClient from "./services/apiClient";

describe("E2E Sync Flow", () => {
  it("should sync field observation from creation to server", async () => {
    // Create observation
    const observationId = await apiClient.createFieldObservation({
      fieldId: "field-123",
      notes: "Test observation",
    });

    // Wait for sync
    const syncManager = SyncManager.getInstance();
    await syncManager.forceSync();

    // Verify synced
    const status = await syncManager.getSyncStatus();
    expect(status.pendingCount).toBe(0);
  });
});
```

## 🔐 Security Considerations

### Encrypt Sensitive Data

```typescript
import * as Crypto from "expo-crypto";

const encryptData = async (data: any) => {
  const jsonString = JSON.stringify(data);
  const encrypted = await Crypto.digestStringAsync(
    Crypto.CryptoDigestAlgorithm.SHA256,
    jsonString,
  );
  return encrypted;
};

// Use when queuing sensitive operations
await syncManager.queueOperation(
  SyncOperationType.CREATE,
  SyncDataType.FIELD_OBSERVATION,
  await encryptData(sensitiveData),
);
```

## 📱 Platform-Specific Considerations

### iOS

- Enable background fetch capability
- Handle app state changes
- Respect low power mode

### Android

- Use WorkManager for background sync
- Handle doze mode
- Respect battery optimization settings

## 🚀 Performance Optimization

### 1. Batch Operations

```typescript
// Instead of multiple individual operations
const observations = [...]; // Array of observations

for (const obs of observations) {
  await syncManager.queueOperation(
    SyncOperationType.CREATE,
    SyncDataType.FIELD_OBSERVATION,
    obs
  );
}
```

### 2. Prioritize Critical Data

```typescript
await syncManager.queueOperation(
  SyncOperationType.CREATE,
  SyncDataType.TASK_COMPLETION,
  data,
  { priority: SyncPriority.CRITICAL }, // Will sync first
);
```

### 3. Monitor Queue Size

```typescript
const status = await syncManager.getSyncStatus();

if (status.pendingCount > 100) {
  // Alert user or increase sync frequency
  syncManager.startAutoSync(); // With shorter interval
}
```

## 📞 Support

For issues or questions:

- Check the [SYNC_MANAGER_README.md](./SYNC_MANAGER_README.md)
- Review examples in [syncManager.example.ts](./src/services/syncManager.example.ts)
- Contact the development team

---

**Last Updated:** 2026-01-02
**Version:** 1.0.0
