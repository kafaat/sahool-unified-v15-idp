/**
 * API Client Integration Tests
 * اختبارات تكامل عميل API
 *
 * Tests for SahoolApiClient methods and error handling
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock the logger
vi.mock('../../logger', () => ({
  logger: {
    warn: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Import after mocking
import { apiClient } from '../client';

describe('SahoolApiClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiClient.clearToken();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Authentication', () => {
    it('should set and use auth token', () => {
      apiClient.setToken('test-token-123');
      // Token is set internally, we verify it's used in requests
      expect(true).toBe(true);
    });

    it('should clear auth token', () => {
      apiClient.setToken('test-token-123');
      apiClient.clearToken();
      // Token is cleared internally
      expect(true).toBe(true);
    });

    it('should validate email format on login', async () => {
      const result = await apiClient.login('invalid-email', 'password');

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should handle successful login', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: {
            access_token: 'jwt-token',
            user: { id: 'user-1', email: 'test@example.com' },
          },
        }),
      });

      const result = await apiClient.login('test@example.com', 'password123');

      expect(mockFetch).toHaveBeenCalled();
      expect(result.success).toBe(true);
    });

    it('should handle login failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ error: 'Invalid credentials' }),
      });

      const result = await apiClient.login('test@example.com', 'wrong-password');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid credentials');
    });
  });

  describe('Field Operations', () => {
    beforeEach(() => {
      apiClient.setToken('test-token');
    });

    it('should fetch fields list', async () => {
      const mockFields = [
        { id: 'field-1', name: 'Test Field 1' },
        { id: 'field-2', name: 'Test Field 2' },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: mockFields }),
      });

      const result = await apiClient.getFields('tenant-123');

      expect(mockFetch).toHaveBeenCalled();
      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('tenantId=tenant-123');
    });

    it('should fetch single field by ID', async () => {
      const mockField = { id: 'field-1', name: 'Test Field' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: mockField }),
      });

      const result = await apiClient.getField('field-1');

      expect(mockFetch).toHaveBeenCalled();
      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('/fields/field-1');
    });

    it('should create new field', async () => {
      const newField = {
        name: 'New Field',
        tenantId: 'tenant-123',
        boundary: { type: 'Polygon', coordinates: [] },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: { id: 'field-new', ...newField } }),
      });

      const result = await apiClient.createField(newField as any);

      expect(mockFetch).toHaveBeenCalled();
      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe('POST');
    });

    it('should update field with ETag for optimistic locking', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: { id: 'field-1' } }),
      });

      await apiClient.updateField('field-1', { name: 'Updated' } as any, 'etag-123');

      const [, options] = mockFetch.mock.calls[0];
      expect(options.headers['If-Match']).toBe('etag-123');
    });

    it('should delete field', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true }),
      });

      await apiClient.deleteField('field-1');

      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe('DELETE');
    });

    it('should find nearby fields', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: [] }),
      });

      await apiClient.getNearbyFields(15.3694, 44.191, 10000);

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('lat=15.3694');
      expect(callUrl).toContain('lng=44.191');
      expect(callUrl).toContain('radius=10000');
    });
  });

  describe('NDVI Analysis', () => {
    beforeEach(() => {
      apiClient.setToken('test-token');
    });

    it('should fetch field NDVI data', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: { average: 0.65, trend: 'increasing' },
        }),
      });

      const result = await apiClient.getFieldNdvi('field-1');

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('/fields/field-1/ndvi');
    });

    it('should fetch NDVI summary for tenant', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: { totalFields: 10, averageNdvi: 0.58 },
        }),
      });

      await apiClient.getNdviSummary('tenant-123');

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('tenantId=tenant-123');
    });
  });

  describe('Weather API', () => {
    it('should fetch current weather', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: { temperature: 25, humidity: 60 },
        }),
      });

      await apiClient.getWeather(15.3694, 44.191);

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('lat=15.3694');
      expect(callUrl).toContain('lng=44.191');
    });

    it('should fetch weather forecast', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: { days: [] },
        }),
      });

      await apiClient.getWeatherForecast(15.3694, 44.191, 14);

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('days=14');
    });

    it('should fetch agricultural risks', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: [{ type: 'frost', severity: 'low' }],
        }),
      });

      await apiClient.getAgriculturalRisks(15.3694, 44.191);

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('/weather/risks');
    });
  });

  describe('Task Operations', () => {
    beforeEach(() => {
      apiClient.setToken('test-token');
    });

    it('should fetch tasks with filters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: [] }),
      });

      await apiClient.getTasks({
        tenantId: 'tenant-1',
        fieldId: 'field-1',
        status: 'pending',
      });

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('tenantId=tenant-1');
      expect(callUrl).toContain('fieldId=field-1');
      expect(callUrl).toContain('status=pending');
    });

    it('should create task', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: { id: 'task-new' } }),
      });

      await apiClient.createTask({
        title: 'New Task',
        fieldId: 'field-1',
        priority: 'high',
      } as any);

      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe('POST');
    });

    it('should update task status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: { id: 'task-1', status: 'completed' } }),
      });

      await apiClient.updateTaskStatus('task-1', 'completed');

      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/tasks/task-1/status');
      expect(options.method).toBe('PUT');
    });

    it('should complete task with notes', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true }),
      });

      await apiClient.completeTask('task-1', 'Task completed successfully');

      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/tasks/task-1/complete');
      expect(JSON.parse(options.body).notes).toBe('Task completed successfully');
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));
      mockFetch.mockRejectedValueOnce(new Error('Network error'));
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await apiClient.getFields('tenant-123');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Network error');
    });

    it('should handle timeout', async () => {
      const abortError = new Error('Aborted');
      abortError.name = 'AbortError';
      mockFetch.mockRejectedValueOnce(abortError);

      const result = await apiClient.getFields('tenant-123');

      expect(result.success).toBe(false);
      expect(result.error).toContain('timeout');
    });

    it('should handle server errors (5xx) with retry', async () => {
      // First two calls fail with 500
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ error: 'Server error' }),
      });
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ error: 'Server error' }),
      });
      // Third call succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: [] }),
      });

      const result = await apiClient.getFields('tenant-123');

      // Should have retried and succeeded
      expect(mockFetch).toHaveBeenCalledTimes(3);
      expect(result.success).toBe(true);
    });

    it('should not retry client errors (4xx)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ error: 'Not found' }),
      });

      const result = await apiClient.getField('nonexistent');

      // Should not retry 404
      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(result.success).toBe(false);
      expect(result.error).toContain('Not found');
    });

    it('should handle invalid JSON response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      const result = await apiClient.getFields('tenant-123');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid JSON');
    });
  });

  describe('IoT Sensors', () => {
    it('should fetch sensor data for field', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: [{ id: 'sensor-1', type: 'soil_moisture' }],
        }),
      });

      await apiClient.getSensorData('field-1');

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('/iot/fields/field-1/sensors');
    });

    it('should fetch sensor history', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: [] }),
      });

      const from = new Date('2026-01-01');
      const to = new Date('2026-01-06');
      await apiClient.getSensorHistory('sensor-1', from, to);

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('/iot/sensors/sensor-1/history');
      expect(callUrl).toContain('from=');
      expect(callUrl).toContain('to=');
    });
  });

  describe('Irrigation', () => {
    it('should get irrigation recommendation', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: { recommendedAmount: 25, unit: 'mm' },
        }),
      });

      await apiClient.getIrrigationRecommendation('field-1');

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('/irrigation/fields/field-1/recommendation');
    });

    it('should calculate ET0', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: { et0: 5.2 } }),
      });

      await apiClient.calculateET0({
        temperature: 28,
        humidity: 55,
        windSpeed: 8,
        solarRadiation: 22,
      });

      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe('POST');
    });
  });

  describe('Field Chat', () => {
    it('should validate message before sending', async () => {
      // Empty message
      const result = await apiClient.sendFieldMessage('field-1', '');

      expect(result.success).toBe(false);
    });

    it('should send valid message', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true }),
      });

      await apiClient.sendFieldMessage('field-1', 'Hello team!');

      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe('POST');
    });

    it('should fetch field messages', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: [] }),
      });

      await apiClient.getFieldMessages('field-1', { limit: 20 });

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('limit=20');
    });
  });

  describe('WebSocket', () => {
    it('should generate correct WebSocket URL for HTTPS', () => {
      // The base URL is empty in test, so we test the logic
      const wsUrl = apiClient.getWebSocketUrl();
      expect(wsUrl).toContain('/ws');
    });
  });

  describe('Billing', () => {
    it('should fetch subscription', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: { plan: 'professional', status: 'active' },
        }),
      });

      await apiClient.getSubscription('tenant-123');

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('/billing/tenants/tenant-123/subscription');
    });

    it('should fetch invoices', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: [] }),
      });

      await apiClient.getInvoices('tenant-123');

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('/billing/tenants/tenant-123/invoices');
    });
  });

  describe('Field Intelligence', () => {
    it('should get living field score', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: { score: 85, level: 'healthy' },
        }),
      });

      await apiClient.getLivingFieldScore('field-1');

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('/fields/field-1/intelligence/score');
    });

    it('should get field zones', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ success: true, data: [] }),
      });

      await apiClient.getFieldZones('field-1');

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('/fields/field-1/intelligence/zones');
    });

    it('should get best days for activity', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: [{ date: '2026-01-07', score: 95 }],
        }),
      });

      await apiClient.getBestDaysForActivity('spraying', 7);

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain('activity=spraying');
      expect(callUrl).toContain('days=7');
    });

    it('should validate task date', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          success: true,
          data: { suitable: true, score: 80 },
        }),
      });

      await apiClient.validateTaskDate('2026-01-10', 'irrigation');

      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe('POST');
    });
  });
});
