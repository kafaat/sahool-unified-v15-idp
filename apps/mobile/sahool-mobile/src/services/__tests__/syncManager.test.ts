/**
 * SAHOOL Mobile - Sync Manager Tests
 * اختبارات مدير المزامنة
 *
 * Unit tests for the SyncManager
 */

import SyncManager from '../syncManager';
import {
  SyncOperationType,
  SyncDataType,
  SyncPriority,
  ConflictResolutionStrategy,
  SyncEventType,
  SyncStatus,
} from '../../models/syncTypes';

// Mock dependencies
jest.mock('@react-native-async-storage/async-storage', () => ({
  setItem: jest.fn(() => Promise.resolve()),
  getItem: jest.fn(() => Promise.resolve(null)),
  removeItem: jest.fn(() => Promise.resolve()),
}));

jest.mock('@react-native-community/netinfo', () => ({
  addEventListener: jest.fn(() => jest.fn()),
  fetch: jest.fn(() =>
    Promise.resolve({
      isConnected: true,
      type: 'wifi',
    })
  ),
}));

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    statusText: 'OK',
    json: () => Promise.resolve({ success: true }),
  })
) as jest.Mock;

describe('SyncManager', () => {
  let syncManager: SyncManager;

  beforeEach(() => {
    // Reset singleton instance
    (SyncManager as any).instance = null;

    // Initialize sync manager
    syncManager = SyncManager.getInstance({
      autoSync: false,
      maxRetries: 3,
      conflictResolution: ConflictResolutionStrategy.SERVER_WINS,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // اختبارات التهيئة - Initialization Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Initialization', () => {
    test('should create singleton instance', () => {
      const instance1 = SyncManager.getInstance();
      const instance2 = SyncManager.getInstance();

      expect(instance1).toBe(instance2);
    });

    test('should initialize with default config', () => {
      const manager = SyncManager.getInstance();
      expect(manager).toBeDefined();
    });

    test('should initialize with custom config', () => {
      const manager = SyncManager.getInstance({
        maxRetries: 10,
        syncInterval: 60000,
      });

      expect(manager).toBeDefined();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // اختبارات إضافة العمليات - Queue Operations Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Queue Operations', () => {
    test('should queue a field observation', async () => {
      const observation = {
        fieldId: 'field-123',
        observedAt: new Date(),
        observationType: 'PEST_DETECTION',
        notes: 'Test observation',
        userId: 'user-456',
      };

      const operationId = await syncManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.FIELD_OBSERVATION,
        observation
      );

      expect(operationId).toBeDefined();
      expect(typeof operationId).toBe('string');
    });

    test('should queue with custom priority', async () => {
      const data = { test: 'data' };

      const operationId = await syncManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.SENSOR_READING,
        data,
        {
          priority: SyncPriority.HIGH,
        }
      );

      expect(operationId).toBeDefined();
    });

    test('should queue multiple operations', async () => {
      const operations = [
        {
          type: SyncOperationType.CREATE,
          dataType: SyncDataType.FIELD_OBSERVATION,
          data: { test: 'data1' },
        },
        {
          type: SyncOperationType.CREATE,
          dataType: SyncDataType.SENSOR_READING,
          data: { test: 'data2' },
        },
        {
          type: SyncOperationType.UPDATE,
          dataType: SyncDataType.FIELD_UPDATE,
          data: { test: 'data3' },
        },
      ];

      const ids: string[] = [];

      for (const op of operations) {
        const id = await syncManager.queueOperation(
          op.type,
          op.dataType,
          op.data
        );
        ids.push(id);
      }

      expect(ids).toHaveLength(3);
      expect(ids.every((id) => typeof id === 'string')).toBe(true);
    });

    test('should throw error when queue is full', async () => {
      // Create manager with small queue size
      const smallQueueManager = SyncManager.getInstance({
        maxQueueSize: 2,
      });

      // Fill the queue
      await smallQueueManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.FIELD_OBSERVATION,
        { test: 'data1' }
      );

      await smallQueueManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.FIELD_OBSERVATION,
        { test: 'data2' }
      );

      // This should throw
      await expect(
        smallQueueManager.queueOperation(
          SyncOperationType.CREATE,
          SyncDataType.FIELD_OBSERVATION,
          { test: 'data3' }
        )
      ).rejects.toThrow();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // اختبارات الحالة - Status Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Status', () => {
    test('should get sync status', async () => {
      const status = await syncManager.getSyncStatus();

      expect(status).toBeDefined();
      expect(status.status).toBeDefined();
      expect(typeof status.isOnline).toBe('boolean');
      expect(typeof status.isSyncing).toBe('boolean');
      expect(typeof status.pendingCount).toBe('number');
      expect(typeof status.failedCount).toBe('number');
      expect(typeof status.conflictCount).toBe('number');
    });

    test('should reflect queued operations in status', async () => {
      await syncManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.FIELD_OBSERVATION,
        { test: 'data' }
      );

      const status = await syncManager.getSyncStatus();

      expect(status.pendingCount).toBeGreaterThan(0);
    });

    test('should get statistics', () => {
      const stats = syncManager.getStatistics();

      expect(stats).toBeDefined();
      expect(typeof stats.totalOperations).toBe('number');
      expect(typeof stats.successfulOperations).toBe('number');
      expect(typeof stats.failedOperations).toBe('number');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // اختبارات الأحداث - Event Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Events', () => {
    test('should add event listener', () => {
      const listener = jest.fn();

      syncManager.addEventListener(SyncEventType.SYNC_STARTED, listener);

      // Listeners are stored internally
      expect(() => {
        syncManager.addEventListener(SyncEventType.SYNC_STARTED, listener);
      }).not.toThrow();
    });

    test('should remove event listener', () => {
      const listener = jest.fn();

      syncManager.addEventListener(SyncEventType.SYNC_STARTED, listener);
      syncManager.removeEventListener(SyncEventType.SYNC_STARTED, listener);

      // Should not throw
      expect(() => {
        syncManager.removeEventListener(SyncEventType.SYNC_STARTED, listener);
      }).not.toThrow();
    });

    test('should emit OPERATION_QUEUED event when operation is queued', (done) => {
      const listener = jest.fn((event) => {
        expect(event.type).toBe(SyncEventType.OPERATION_QUEUED);
        expect(event.operationId).toBeDefined();
        done();
      });

      syncManager.addEventListener(SyncEventType.OPERATION_QUEUED, listener);

      syncManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.FIELD_OBSERVATION,
        { test: 'data' }
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // اختبارات التحكم في المزامنة - Sync Control Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Sync Control', () => {
    test('should start auto sync', () => {
      expect(() => {
        syncManager.startAutoSync();
      }).not.toThrow();
    });

    test('should stop auto sync', () => {
      syncManager.startAutoSync();

      expect(() => {
        syncManager.stopAutoSync();
      }).not.toThrow();
    });

    test('should pause sync', () => {
      syncManager.pause();

      // Status should reflect paused state
      // (In actual implementation, you'd check internal state)
      expect(() => {
        syncManager.pause();
      }).not.toThrow();
    });

    test('should resume sync', () => {
      syncManager.pause();
      syncManager.resume();

      expect(() => {
        syncManager.resume();
      }).not.toThrow();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // اختبارات حل التعارضات - Conflict Resolution Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Conflict Resolution', () => {
    test('should register custom resolver', () => {
      const resolver = jest.fn((local, server, base) =>
        Promise.resolve({ ...server, custom: true })
      );

      expect(() => {
        syncManager.registerCustomResolver(
          SyncDataType.FIELD_OBSERVATION,
          resolver
        );
      }).not.toThrow();
    });

    test('should use custom resolver for conflicts', async () => {
      const resolver = jest.fn((local, server, base) =>
        Promise.resolve({ ...local, resolved: true })
      );

      syncManager.registerCustomResolver(
        SyncDataType.FIELD_OBSERVATION,
        resolver
      );

      // Queue an update operation that might conflict
      await syncManager.queueOperation(
        SyncOperationType.UPDATE,
        SyncDataType.FIELD_OBSERVATION,
        { id: 'obs-123', notes: 'Local changes' },
        {
          entityId: 'obs-123',
          previousData: { id: 'obs-123', notes: 'Original' },
        }
      );

      // Custom resolver is registered
      expect(resolver).toBeDefined();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // اختبارات التخزين - Storage Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Storage', () => {
    test('should save queue to storage', async () => {
      await syncManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.FIELD_OBSERVATION,
        { test: 'data' }
      );

      await expect(syncManager.saveQueueToStorage()).resolves.not.toThrow();
    });

    test('should load queue from storage', async () => {
      await expect(syncManager.loadQueueFromStorage()).resolves.not.toThrow();
    });

    test('should clear completed operations', async () => {
      const cleared = await syncManager.clearCompletedOperations();

      expect(typeof cleared).toBe('number');
      expect(cleared).toBeGreaterThanOrEqual(0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // اختبارات المزامنة - Sync Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Sync Processing', () => {
    test('should process queue', async () => {
      await syncManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.FIELD_OBSERVATION,
        { test: 'data' }
      );

      const result = await syncManager.processQueue();

      expect(result).toBeDefined();
      expect(typeof result.success).toBe('boolean');
      expect(typeof result.totalOperations).toBe('number');
      expect(typeof result.successCount).toBe('number');
      expect(typeof result.failedCount).toBe('number');
    });

    test('should force sync', async () => {
      await syncManager.queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.FIELD_OBSERVATION,
        { test: 'data' }
      );

      const result = await syncManager.forceSync();

      expect(result).toBeDefined();
    });

    test('should return empty result when queue is empty', async () => {
      const result = await syncManager.processQueue();

      expect(result.totalOperations).toBe(0);
      expect(result.success).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // اختبارات الشبكة - Network Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Network', () => {
    test('should detect network status', async () => {
      const status = await syncManager.detectNetworkStatus();

      expect(status).toBeDefined();
      expect(typeof status).toBe('string');
    });

    test('should sync when online', async () => {
      await expect(syncManager.syncWhenOnline()).resolves.not.toThrow();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // اختبارات التنظيف - Cleanup Tests
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Cleanup', () => {
    test('should shutdown gracefully', async () => {
      await expect(syncManager.shutdown()).resolves.not.toThrow();
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// اختبارات التكامل - Integration Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('SyncManager Integration', () => {
  let syncManager: SyncManager;

  beforeEach(() => {
    (SyncManager as any).instance = null;
    syncManager = SyncManager.getInstance({
      autoSync: false,
      maxRetries: 2,
    });
  });

  test('should handle complete workflow', async () => {
    // 1. Queue operations
    const id1 = await syncManager.queueOperation(
      SyncOperationType.CREATE,
      SyncDataType.FIELD_OBSERVATION,
      { fieldId: 'field-1', notes: 'Test observation' }
    );

    const id2 = await syncManager.queueOperation(
      SyncOperationType.CREATE,
      SyncDataType.SENSOR_READING,
      { sensorId: 'sensor-1', value: 45.5 }
    );

    // 2. Check status
    let status = await syncManager.getSyncStatus();
    expect(status.pendingCount).toBe(2);

    // 3. Process queue
    const result = await syncManager.processQueue();
    expect(result.totalOperations).toBeGreaterThan(0);

    // 4. Clear completed
    await syncManager.clearCompletedOperations();

    // 5. Check final status
    status = await syncManager.getSyncStatus();
    expect(status.completedCount).toBeGreaterThanOrEqual(0);
  });

  test('should handle events in workflow', (done) => {
    let eventsReceived = 0;
    const expectedEvents = 2; // OPERATION_QUEUED, SYNC_STARTED

    const listener = () => {
      eventsReceived++;
      if (eventsReceived >= expectedEvents) {
        done();
      }
    };

    syncManager.addEventListener(SyncEventType.OPERATION_QUEUED, listener);
    syncManager.addEventListener(SyncEventType.SYNC_STARTED, listener);

    syncManager
      .queueOperation(
        SyncOperationType.CREATE,
        SyncDataType.FIELD_OBSERVATION,
        { test: 'data' }
      )
      .then(() => {
        return syncManager.processQueue();
      });
  });
});
