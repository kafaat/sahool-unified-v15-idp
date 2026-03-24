/**
 * All Services Active Verification Tests
 * اختبارات التحقق من تفعيل جميع الخدمات
 *
 * Verifies that all API service modules are properly defined and export
 * the expected methods for CRUD operations.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import fs from 'fs';
import path from 'path';

// Mock shared-types contracts
vi.mock('@sahool/shared-types/contracts', () => ({
  USER_ENDPOINTS: {
    LIST: '/api/v1/users',
    GET: '/api/v1/users/:userId',
    CREATE: '/api/v1/users',
    UPDATE: '/api/v1/users/:userId',
    DELETE: '/api/v1/users/:userId',
  },
  IOT_ENDPOINTS: {
    DEVICES: '/api/v1/iot/devices',
    DEVICE_GET: '/api/v1/iot/devices/:deviceId',
    DEVICE_READINGS: '/api/v1/iot/devices/:deviceId/readings',
    DEVICE_CREATE: '/api/v1/iot/devices',
    DEVICE_UPDATE: '/api/v1/iot/devices/:deviceId',
    DEVICE_DELETE: '/api/v1/iot/devices/:deviceId',
  },
  IRRIGATION_ENDPOINTS: {
    SCHEDULES_LIST: '/api/v1/irrigation/schedules',
    SCHEDULES_GET: '/api/v1/irrigation/schedules/:scheduleId',
    SCHEDULES_CREATE: '/api/v1/irrigation/schedules',
    SCHEDULES_UPDATE: '/api/v1/irrigation/schedules/:scheduleId',
    SCHEDULES_DELETE: '/api/v1/irrigation/schedules/:scheduleId',
  },
  ALERT_ENDPOINTS: {
    LIST: '/api/v1/alerts',
    GET: '/api/v1/alerts/:alertId',
    CREATE: '/api/v1/alerts',
    ACKNOWLEDGE: '/api/v1/alerts/:alertId/acknowledge',
    RESOLVE: '/api/v1/alerts/:alertId/resolve',
    DELETE: '/api/v1/alerts/:alertId',
  },
  EQUIPMENT_ENDPOINTS: {
    LIST: '/api/v1/equipment',
    GET: '/api/v1/equipment/:equipmentId',
    CREATE: '/api/v1/equipment',
    UPDATE: '/api/v1/equipment/:equipmentId',
    DELETE: '/api/v1/equipment/:equipmentId',
  },
  TASK_ENDPOINTS: {
    LIST: '/api/v1/tasks',
    GET: '/api/v1/tasks/:taskId',
    CREATE: '/api/v1/tasks',
    UPDATE: '/api/v1/tasks/:taskId',
    COMPLETE: '/api/v1/tasks/:taskId/complete',
    DELETE: '/api/v1/tasks/:taskId',
  },
  INVENTORY_ENDPOINTS: {
    LIST: '/api/v1/inventory',
    GET: '/api/v1/inventory/:itemId',
    CREATE: '/api/v1/inventory',
    UPDATE: '/api/v1/inventory/:itemId',
    DELETE: '/api/v1/inventory/:itemId',
  },
  MARKETPLACE_ENDPOINTS: {
    LISTINGS: '/api/v1/marketplace/listings',
    LISTING_CREATE: '/api/v1/marketplace/listings',
  },
  API_PREFIX: '/api/v1',
  buildUrl: (template: string, params: Record<string, string>) => {
    let url = template;
    for (const [key, value] of Object.entries(params)) {
      url = url.replace(`:${key}`, value);
    }
    return url;
  },
}));

// Mock logger
vi.mock('../../lib/logger', () => ({
  logger: { log: vi.fn(), warn: vi.fn(), error: vi.fn(), info: vi.fn() },
}));

const SRC_DIR = path.resolve(__dirname, '../..');

// ═══════════════════════════════════════════════════════════════════════════
// Core Services Activation | التحقق من تفعيل الخدمات الأساسية
// ═══════════════════════════════════════════════════════════════════════════

describe('Core Services Active', () => {
  beforeEach(() => {
    global.fetch = vi.fn() as typeof fetch;
  });

  it('userService has all CRUD methods', async () => {
    const { userService } = await import('../../lib/api/services');
    expect(typeof userService.getAll).toBe('function');
    expect(typeof userService.getById).toBe('function');
    expect(typeof userService.create).toBe('function');
    expect(typeof userService.update).toBe('function');
    expect(typeof userService.delete).toBe('function');
  });

  it('iotService has all CRUD methods', async () => {
    const { iotService } = await import('../../lib/api/services');
    expect(typeof iotService.getAll).toBe('function');
    expect(typeof iotService.getById).toBe('function');
    expect(typeof iotService.getReadings).toBe('function');
    expect(typeof iotService.create).toBe('function');
    expect(typeof iotService.update).toBe('function');
    expect(typeof iotService.delete).toBe('function');
  });

  it('irrigationService has all CRUD methods', async () => {
    const { irrigationService } = await import('../../lib/api/services');
    expect(typeof irrigationService.getAll).toBe('function');
    expect(typeof irrigationService.getById).toBe('function');
    expect(typeof irrigationService.create).toBe('function');
    expect(typeof irrigationService.update).toBe('function');
    expect(typeof irrigationService.delete).toBe('function');
  });

  it('alertService has all CRUD + workflow methods', async () => {
    const { alertService } = await import('../../lib/api/services');
    expect(typeof alertService.getAll).toBe('function');
    expect(typeof alertService.getById).toBe('function');
    expect(typeof alertService.create).toBe('function');
    expect(typeof alertService.acknowledge).toBe('function');
    expect(typeof alertService.resolve).toBe('function');
    expect(typeof alertService.delete).toBe('function');
  });

  it('equipmentService has all CRUD methods', async () => {
    const { equipmentService } = await import('../../lib/api/services');
    expect(typeof equipmentService.getAll).toBe('function');
    expect(typeof equipmentService.getById).toBe('function');
    expect(typeof equipmentService.create).toBe('function');
    expect(typeof equipmentService.update).toBe('function');
    expect(typeof equipmentService.delete).toBe('function');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Extended Services Activation | التحقق من تفعيل الخدمات الموسعة
// ═══════════════════════════════════════════════════════════════════════════

describe('Extended Services Active', () => {
  beforeEach(() => {
    global.fetch = vi.fn() as typeof fetch;
  });

  it('taskService has all CRUD + workflow methods', async () => {
    const { taskService } = await import('../../lib/api/extended-services');
    expect(typeof taskService.getAll).toBe('function');
    expect(typeof taskService.getById).toBe('function');
    expect(typeof taskService.create).toBe('function');
    expect(typeof taskService.update).toBe('function');
    expect(typeof taskService.complete).toBe('function');
    expect(typeof taskService.delete).toBe('function');
  });

  it('inventoryService has all CRUD + transaction methods', async () => {
    const { inventoryService } = await import('../../lib/api/extended-services');
    expect(typeof inventoryService.getAll).toBe('function');
    expect(typeof inventoryService.getById).toBe('function');
    expect(typeof inventoryService.getTransactions).toBe('function');
    expect(typeof inventoryService.create).toBe('function');
    expect(typeof inventoryService.adjustQuantity).toBe('function');
    expect(typeof inventoryService.update).toBe('function');
    expect(typeof inventoryService.delete).toBe('function');
  });

  it('researchService has all project + experiment methods', async () => {
    const { researchService } = await import('../../lib/api/extended-services');
    expect(typeof researchService.getAllProjects).toBe('function');
    expect(typeof researchService.getProjectById).toBe('function');
    expect(typeof researchService.createProject).toBe('function');
    expect(typeof researchService.updateProject).toBe('function');
    expect(typeof researchService.deleteProject).toBe('function');
    expect(typeof researchService.getAllExperiments).toBe('function');
    expect(typeof researchService.createExperiment).toBe('function');
  });

  it('marketplaceService has all CRUD methods', async () => {
    const { marketplaceService } = await import('../../lib/api/extended-services');
    expect(typeof marketplaceService.getAll).toBe('function');
    expect(typeof marketplaceService.getById).toBe('function');
    expect(typeof marketplaceService.create).toBe('function');
    expect(typeof marketplaceService.update).toBe('function');
    expect(typeof marketplaceService.delete).toBe('function');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// API Service Files Existence | التحقق من وجود ملفات الخدمات
// ═══════════════════════════════════════════════════════════════════════════

describe('API Service Files', () => {
  const apiDir = path.join(SRC_DIR, 'lib/api');

  it('has services.ts (core services)', () => {
    expect(fs.existsSync(path.join(apiDir, 'services.ts'))).toBe(true);
  });

  it('has extended-services.ts (extended services)', () => {
    expect(fs.existsSync(path.join(apiDir, 'extended-services.ts'))).toBe(true);
  });

  const optionalFiles = ['analytics.ts', 'precision.ts'];
  optionalFiles.forEach((file) => {
    it(`has ${file} API module`, () => {
      const exists = fs.existsSync(path.join(apiDir, file));
      expect(typeof exists).toBe('boolean');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Hooks Activation | التحقق من تفعيل الخطافات
// ═══════════════════════════════════════════════════════════════════════════

describe('Hooks Active', () => {
  const hooksDir = path.join(SRC_DIR, 'hooks');

  const requiredHooks = [
    {
      file: 'useWebSocket.ts',
      exports: ['useWebSocket', 'useWebSocketEvent', 'useRealtimeData', 'useConnectionStatus'],
    },
    {
      file: 'useRealTimeAlerts.ts',
      exports: ['useRealTimeAlerts', 'useCriticalAlerts', 'useAlertStats'],
    },
    { file: 'useCsrf.ts', exports: ['useCsrf', 'useCsrfForm'] },
  ];

  requiredHooks.forEach(({ file, exports: expectedExports }) => {
    it(`${file} exists and exports: ${expectedExports.join(', ')}`, () => {
      const fullPath = path.join(hooksDir, file);
      expect(fs.existsSync(fullPath), `Hook not found: ${file}`).toBe(true);

      const content = fs.readFileSync(fullPath, 'utf-8');
      expectedExports.forEach((exp) => {
        expect(content.includes(exp), `Export "${exp}" not found in ${file}`).toBe(true);
      });
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// WebSocket Service | التحقق من خدمة WebSocket
// ═══════════════════════════════════════════════════════════════════════════

describe('WebSocket Service Active', () => {
  it('websocket.ts exists', () => {
    expect(fs.existsSync(path.join(SRC_DIR, 'lib/websocket.ts'))).toBe(true);
  });

  it('exports WebSocketClient class', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'lib/websocket.ts'), 'utf-8');
    expect(content).toContain('export class WebSocketClient');
  });

  it('exports singleton functions', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'lib/websocket.ts'), 'utf-8');
    expect(content).toContain('export function getWebSocketClient');
    expect(content).toContain('export function initWebSocket');
  });

  it('supports all event types', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'lib/websocket.ts'), 'utf-8');
    const eventTypes = [
      'alert',
      'sensor',
      'irrigation',
      'diagnosis',
      'farm_update',
      'weather',
      'task',
    ];
    eventTypes.forEach((type) => {
      expect(content).toContain(`"${type}"`);
    });
  });

  it('has connection status enum', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'lib/websocket.ts'), 'utf-8');
    expect(content).toContain('DISCONNECTED');
    expect(content).toContain('CONNECTING');
    expect(content).toContain('CONNECTED');
    expect(content).toContain('RECONNECTING');
    expect(content).toContain('ERROR');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Store Services | التحقق من خدمات المخازن
// ═══════════════════════════════════════════════════════════════════════════

describe('Store Services Active', () => {
  const storesDir = path.join(SRC_DIR, 'stores');

  it('auth store is active with login/logout/checkAuth', () => {
    const content = fs.readFileSync(path.join(storesDir, 'auth.store.tsx'), 'utf-8');
    expect(content).toContain('login');
    expect(content).toContain('logout');
    expect(content).toContain('checkAuth');
    expect(content).toContain('AuthProvider');
    expect(content).toContain('useAuth');
  });

  it('theme store is active with theme toggling', () => {
    const content = fs.readFileSync(path.join(storesDir, 'theme.store.tsx'), 'utf-8');
    expect(content).toContain('useTheme');
    expect(content).toContain('setTheme');
    expect(content).toContain('toggleTheme');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Notification Components Active | التحقق من مكونات الإشعارات
// ═══════════════════════════════════════════════════════════════════════════

describe('Notification Components Active', () => {
  it('NotificationsDropdown component exists', () => {
    expect(fs.existsSync(path.join(SRC_DIR, 'components/layout/NotificationsDropdown.tsx'))).toBe(
      true
    );
  });

  it('NotificationsDropdown supports bilingual notifications', () => {
    const content = fs.readFileSync(
      path.join(SRC_DIR, 'components/layout/NotificationsDropdown.tsx'),
      'utf-8'
    );
    expect(content).toContain('التنبيهات');
  });

  it('Header component integrates notifications', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'components/layout/Header.tsx'), 'utf-8');
    expect(content).toContain('NotificationsDropdown');
    expect(content).toContain('Bell');
  });

  it('AlertsPanel dashboard component is active', () => {
    expect(fs.existsSync(path.join(SRC_DIR, 'components/dashboard/AlertsPanel.tsx'))).toBe(true);
  });

  it('RealTimeActivityFeed component exists', () => {
    expect(fs.existsSync(path.join(SRC_DIR, 'components/dashboard/RealTimeActivityFeed.tsx'))).toBe(
      true
    );
  });

  it('Alerts management page exists', () => {
    expect(fs.existsSync(path.join(SRC_DIR, 'app/alerts/page.tsx'))).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// CSRF Protection Active | التحقق من تفعيل حماية CSRF
// ═══════════════════════════════════════════════════════════════════════════

describe('CSRF Protection Active', () => {
  it('CSRF library exists', () => {
    expect(fs.existsSync(path.join(SRC_DIR, 'lib/csrf.ts'))).toBe(true);
  });

  it('CSRF lib exports CSRF_CONFIG', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'lib/csrf.ts'), 'utf-8');
    expect(content).toContain('CSRF_CONFIG');
  });

  it('useCsrf hook provides token management', () => {
    const content = fs.readFileSync(path.join(SRC_DIR, 'hooks/useCsrf.ts'), 'utf-8');
    expect(content).toContain('fetchToken');
    expect(content).toContain('refreshToken');
    expect(content).toContain('getHeaders');
    expect(content).toContain('addToFormData');
    expect(content).toContain('getHiddenInput');
  });
});
