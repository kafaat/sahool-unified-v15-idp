/**
 * API Services Tests
 * اختبارات خدمات API
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  userService,
  iotService,
  irrigationService,
  alertService,
  equipmentService,
} from '../services';

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
  buildUrl: (template: string, params: Record<string, string>) => {
    let url = template;
    for (const [key, value] of Object.entries(params)) {
      url = url.replace(`:${key}`, value);
    }
    return url;
  },
}));

// Ensure global.fetch is always a vi.fn() mock before each test
beforeEach(() => {
  global.fetch = vi.fn() as typeof fetch;
});

function mockFetch(data: unknown, ok = true, status = 200) {
  (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
    ok,
    status,
    json: () => Promise.resolve(data),
  });
}

describe('User Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as ReturnType<typeof vi.fn>).mockReset();
  });

  describe('getAll', () => {
    it('fetches users with pagination', async () => {
      const mockData = {
        data: [{ id: '1', name: 'User 1' }],
        meta: { total: 1, page: 1, limit: 10, totalPages: 1 },
      };
      mockFetch(mockData);

      const result = await userService.getAll({ page: 1, limit: 10 });
      expect(result).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalled();
    });

    it('includes search and filter params', async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });

      await userService.getAll({ search: 'admin', role: 'admin', status: 'active' });

      const calledUrl = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(calledUrl).toContain('search=admin');
      expect(calledUrl).toContain('role=admin');
      expect(calledUrl).toContain('status=active');
    });

    it('throws on HTTP error', async () => {
      mockFetch({}, false, 500);
      await expect(userService.getAll()).rejects.toThrow('HTTP 500');
    });
  });

  describe('getById', () => {
    it('fetches user by ID', async () => {
      const mockUser = { id: 'user-1', name: 'Admin' };
      mockFetch(mockUser);

      const result = await userService.getById('user-1');
      expect(result).toEqual(mockUser);
    });

    it('throws on 404', async () => {
      mockFetch({}, false, 404);
      await expect(userService.getById('nonexistent')).rejects.toThrow();
    });
  });

  describe('create', () => {
    it('creates user with POST', async () => {
      const newUser = { email: 'new@sahool.io', password: 'pass', name: 'New' };
      mockFetch({ id: 'new-1', ...newUser });

      const result = await userService.create(newUser);
      expect(result.id).toBe('new-1');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({ method: 'POST' })
      );
    });
  });

  describe('update', () => {
    it('updates user with PUT', async () => {
      mockFetch({ id: '1', name: 'Updated' });

      const result = await userService.update('1', { name: 'Updated' });
      expect(result.name).toBe('Updated');
    });
  });

  describe('delete', () => {
    it('deletes user with DELETE', async () => {
      mockFetch({ success: true });

      const result = await userService.delete('1');
      expect(result.success).toBe(true);
    });
  });
});

describe('IoT Service', () => {
  beforeEach(() => {
    (global.fetch as ReturnType<typeof vi.fn>).mockReset();
  });

  describe('getAll', () => {
    it('fetches devices', async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      const result = await iotService.getAll();
      expect(result.data).toEqual([]);
    });

    it('filters by fieldId and type', async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      await iotService.getAll({ fieldId: 'f1', type: 'soil_moisture' });

      const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(url).toContain('field_id=f1');
      expect(url).toContain('type=soil_moisture');
    });
  });

  describe('getReadings', () => {
    it('fetches device readings with date range', async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      await iotService.getReadings('device-1', { from: '2025-01-01', to: '2025-01-31' });

      const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(url).toContain('from=2025-01-01');
    });
  });

  describe('create', () => {
    it('registers new device', async () => {
      mockFetch({ id: 'd-1' });
      const result = await iotService.create({
        name: 'Sensor',
        type: 'soil_moisture',
        fieldId: 'f1',
        serialNumber: 'SN-001',
      });
      expect(result.id).toBe('d-1');
    });
  });

  describe('update', () => {
    it('updates device', async () => {
      mockFetch({ id: 'd-1', status: 'offline' });
      const result = await iotService.update('d-1', { status: 'offline' });
      expect(result.status).toBe('offline');
    });
  });

  describe('delete', () => {
    it('deletes device', async () => {
      mockFetch({ success: true });
      const result = await iotService.delete('d-1');
      expect(result.success).toBe(true);
    });
  });
});

describe('Irrigation Service', () => {
  beforeEach(() => {
    (global.fetch as ReturnType<typeof vi.fn>).mockReset();
  });

  it('fetches all schedules', async () => {
    mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
    const result = await irrigationService.getAll();
    expect(result.data).toEqual([]);
  });

  it('fetches schedule by ID', async () => {
    mockFetch({ id: 'irr-1' });
    const result = await irrigationService.getById('irr-1');
    expect(result.id).toBe('irr-1');
  });

  it('creates schedule', async () => {
    mockFetch({ id: 'irr-new' });
    const result = await irrigationService.create({
      fieldId: 'f1',
      name: 'Morning',
      type: 'scheduled',
      startDate: '2025-01-01',
      frequency: 'daily',
      duration: 60,
      waterAmount: 500,
    });
    expect(result.id).toBe('irr-new');
  });

  it('updates schedule', async () => {
    mockFetch({ id: 'irr-1', status: 'paused' });
    const result = await irrigationService.update('irr-1', { status: 'paused' });
    expect(result.status).toBe('paused');
  });

  it('deletes schedule', async () => {
    mockFetch({ success: true });
    const result = await irrigationService.delete('irr-1');
    expect(result.success).toBe(true);
  });
});

describe('Alert Service', () => {
  beforeEach(() => {
    (global.fetch as ReturnType<typeof vi.fn>).mockReset();
  });

  it('fetches all alerts', async () => {
    mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
    const result = await alertService.getAll();
    expect(result.data).toEqual([]);
  });

  it('filters alerts by type and severity', async () => {
    mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
    await alertService.getAll({ type: 'pest', severity: 'critical' });

    const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
    expect(url).toContain('type=pest');
    expect(url).toContain('severity=critical');
  });

  it('acknowledges alert', async () => {
    mockFetch({ id: 'a-1', status: 'acknowledged' });
    const result = await alertService.acknowledge('a-1');
    expect(result.status).toBe('acknowledged');
  });

  it('resolves alert', async () => {
    mockFetch({ id: 'a-1', status: 'resolved' });
    const result = await alertService.resolve('a-1', 'Fixed the issue');
    expect(result.status).toBe('resolved');
  });

  it('creates alert', async () => {
    mockFetch({ id: 'a-new' });
    const result = await alertService.create({
      type: 'pest',
      severity: 'critical',
      title: 'RPW Detected',
      titleAr: 'كشف سوسة النخيل',
      message: 'Red Palm Weevil detected',
      messageAr: 'تم الكشف عن سوسة النخيل الحمراء',
      source: 'vision-service',
    });
    expect(result.id).toBe('a-new');
  });

  it('deletes alert', async () => {
    mockFetch({ success: true });
    const result = await alertService.delete('a-1');
    expect(result.success).toBe(true);
  });
});

describe('Equipment Service', () => {
  beforeEach(() => {
    (global.fetch as ReturnType<typeof vi.fn>).mockReset();
  });

  it('fetches all equipment', async () => {
    mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
    const result = await equipmentService.getAll();
    expect(result.data).toEqual([]);
  });

  it('creates equipment', async () => {
    mockFetch({ id: 'e-1' });
    const result = await equipmentService.create({
      name: 'Tractor A',
      nameAr: 'جرار أ',
      type: 'tractor',
    });
    expect(result.id).toBe('e-1');
  });

  it('updates equipment', async () => {
    mockFetch({ id: 'e-1', status: 'maintenance' });
    const result = await equipmentService.update('e-1', { status: 'maintenance' });
    expect(result.status).toBe('maintenance');
  });

  it('deletes equipment', async () => {
    mockFetch({ success: true });
    const result = await equipmentService.delete('e-1');
    expect(result.success).toBe(true);
  });
});
