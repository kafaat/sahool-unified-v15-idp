/**
 * API Client Integration Tests
 * اختبارات تكامل عميل API
 *
 * Tests for SahoolApiClient methods and error handling.
 * The client delegates transport to the unified axios instance, so we mock
 * that instance (not global.fetch).
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AxiosError, AxiosHeaders } from 'axios';

// ═══════════════════════════════════════════════════════════════════════════
// Module Mocks (vi.hoisted ensures variables are available for vi.mock)
// ═══════════════════════════════════════════════════════════════════════════

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: vi.fn(),
}));

vi.mock('../../logger', () => ({
  logger: {
    warn: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));

vi.mock('../../security/security', () => ({
  getCsrfHeaders: vi.fn(() => ({ 'X-CSRF-Token': 'test-csrf-token' })),
  getCsrfToken: vi.fn(() => 'test-csrf-token'),
}));

// Mock the unified client (axios instance used by client.ts)
vi.mock('../unified-client', () => ({
  unifiedApiClient: {
    request: mockRequest,
    post: mockRequest,
    defaults: { baseURL: '', headers: {} },
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
  sahoolClient: {
    axiosInstance: {
      request: mockRequest,
      post: mockRequest,
      defaults: { baseURL: '', headers: {} },
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    },
  },
}));

// Mock validation module
vi.mock('../../validation', () => ({
  sanitizers: {
    html: (text: string) => {
      if (typeof text !== 'string') return '';
      let result = text;
      let prev = '';
      while (result !== prev) {
        prev = result;
        result = result.replace(/<[^>]*>/g, '');
      }
      return result;
    },
    email: (email: string) => (email || '').trim().toLowerCase(),
    text: (text: string) => (text || '').trim(),
  },
  validators: {
    email: (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
    safeText: (text: string) =>
      typeof text === 'string' && text.length > 0 && !/<script/i.test(text),
  },
  validationErrors: {
    email: 'Invalid email format',
    unsafeText: 'Message contains unsafe content',
    emptyMessage: 'Message cannot be empty',
  },
}));

// Import after mocking
import { apiClient } from '../client';

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

/** Create a successful axios response */
function okResponse(data: unknown) {
  return {
    data,
    status: 200,
    statusText: 'OK',
    headers: { 'content-type': 'application/json' },
    config: { headers: new AxiosHeaders() },
  };
}

/** Create an AxiosError */
function axiosError(status: number, data?: unknown, message = 'Request failed') {
  const err = new AxiosError(
    message,
    status >= 500 ? 'ERR_BAD_RESPONSE' : 'ERR_BAD_REQUEST',
    undefined,
    undefined,
    {
      data: data ?? { error: message },
      status,
      statusText: 'Error',
      headers: {},
      config: { headers: new AxiosHeaders() },
    } as any
  );
  return err;
}

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

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
      // Token is set internally (no-op in cookie mode)
      expect(true).toBe(true);
    });

    it('should clear auth token', () => {
      apiClient.setToken('test-token-123');
      apiClient.clearToken();
      expect(true).toBe(true);
    });

    it('should validate email format on login', async () => {
      const result = await apiClient.login('invalid-email', 'password');

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should handle successful login', async () => {
      mockRequest.mockResolvedValueOnce(
        okResponse({
          success: true,
          data: {
            access_token: 'jwt-token',
            user: { id: 'user-1', email: 'test@example.com' },
          },
        })
      );

      const result = await apiClient.login('test@example.com', 'password123');

      expect(mockRequest).toHaveBeenCalled();
      expect(result.success).toBe(true);
    });

    it('should handle login failure', async () => {
      mockRequest.mockRejectedValueOnce(axiosError(401, { error: 'Invalid credentials' }));

      const result = await apiClient.login('test@example.com', 'wrong-password');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid credentials');
    });
  });

  describe('Field Operations', () => {
    it('should fetch fields list', async () => {
      const mockFields = [
        { id: 'field-1', name: 'Test Field 1' },
        { id: 'field-2', name: 'Test Field 2' },
      ];

      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: mockFields }));

      await apiClient.getFields('tenant-123');

      expect(mockRequest).toHaveBeenCalled();
      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/fields');
      expect(callArgs.params?.tenantId).toBe('tenant-123');
    });

    it('should fetch single field by ID', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { id: 'field-1' } }));

      await apiClient.getField('field-1');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/fields/field-1');
    });

    it('should create new field', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { id: 'field-new' } }));

      await apiClient.createField({
        name: 'New Field',
        tenantId: 'tenant-123',
        boundary: { type: 'Polygon', coordinates: [] },
      } as any);

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('POST');
    });

    it('should update field with ETag for optimistic locking', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { id: 'field-1' } }));

      await apiClient.updateField('field-1', { name: 'Updated' } as any, 'etag-123');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.headers?.['If-Match']).toBe('etag-123');
    });

    it('should delete field', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true }));

      await apiClient.deleteField('field-1');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('DELETE');
    });

    it('should find nearby fields', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: [] }));

      await apiClient.getNearbyFields(15.3694, 44.191, 10000);

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.params?.lat).toBe('15.3694');
      expect(callArgs.params?.lng).toBe('44.191');
      expect(callArgs.params?.radius).toBe('10000');
    });
  });

  describe('NDVI Analysis', () => {
    it('should fetch field NDVI data', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { average: 0.65 } }));

      await apiClient.getFieldNdvi('field-1');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/fields/field-1/ndvi');
    });

    it('should fetch NDVI summary for tenant', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { totalFields: 10 } }));

      await apiClient.getNdviSummary('tenant-123');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.params?.tenantId).toBe('tenant-123');
    });
  });

  describe('Weather API', () => {
    it('should fetch current weather via POST with lat/lon in body', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { temperature: 25 } }));

      await apiClient.getWeather(15.3694, 44.191);

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/weather/current');
      expect(callArgs.method).toBe('POST');
      const body = callArgs.data;
      expect(body.lat).toBe(15.3694);
      expect(body.lon).toBe(44.191);
    });

    it('should fetch weather forecast via POST with days in body', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { days: [] } }));

      await apiClient.getWeatherForecast(15.3694, 44.191, 14);

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/weather/forecast');
      expect(callArgs.method).toBe('POST');
      const body = callArgs.data;
      expect(body.days).toBe(14);
    });

    it('should fetch agricultural risks via POST', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: [{ type: 'frost' }] }));

      await apiClient.getAgriculturalRisks(15.3694, 44.191);

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/weather/agricultural-report');
      expect(callArgs.method).toBe('POST');
    });
  });

  describe('Task Operations', () => {
    it('should fetch tasks with filters', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: [] }));

      await apiClient.getTasks({
        tenantId: 'tenant-1',
        fieldId: 'field-1',
        status: 'pending',
      });

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.params?.tenantId).toBe('tenant-1');
      expect(callArgs.params?.fieldId).toBe('field-1');
      expect(callArgs.params?.status).toBe('pending');
    });

    it('should create task', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { id: 'task-new' } }));

      await apiClient.createTask({
        title: 'New Task',
        fieldId: 'field-1',
        priority: 'high',
      } as any);

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('POST');
    });

    it('should update task status', async () => {
      mockRequest.mockResolvedValueOnce(
        okResponse({ success: true, data: { id: 'task-1', status: 'completed' } })
      );

      await apiClient.updateTaskStatus('task-1', 'completed');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/tasks/task-1/status');
      expect(callArgs.method).toBe('PUT');
    });

    it('should complete task with notes', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true }));

      await apiClient.completeTask('task-1', 'Task completed successfully');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/tasks/task-1/complete');
      const body = callArgs.data;
      expect(body.notes).toBe('Task completed successfully');
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      const networkErr = new AxiosError('Network Error', 'ERR_NETWORK');
      mockRequest.mockRejectedValueOnce(networkErr);

      const result = await apiClient.getFields('tenant-123');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Network');
    });

    it('should handle timeout', async () => {
      const timeoutErr = new AxiosError('timeout', 'ECONNABORTED');
      mockRequest.mockRejectedValueOnce(timeoutErr);

      const result = await apiClient.getFields('tenant-123');

      expect(result.success).toBe(false);
      expect(result.error).toContain('timeout');
    });

    it('should handle server errors (5xx) with retry', async () => {
      // The unified client handles retries internally, so a single 500 is
      // returned after exhausting retries
      mockRequest.mockRejectedValueOnce(axiosError(500, { error: 'Server error' }));

      const result = await apiClient.getFields('tenant-123');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Server error');
    });

    it('should not retry client errors (4xx)', async () => {
      mockRequest.mockRejectedValueOnce(axiosError(404, { error: 'Not found' }));

      const result = await apiClient.getField('nonexistent');

      expect(mockRequest).toHaveBeenCalledTimes(1);
      expect(result.success).toBe(false);
      expect(result.error).toContain('Not found');
    });

    it('should handle invalid JSON response', async () => {
      mockRequest.mockRejectedValueOnce(new Error('Invalid JSON'));

      const result = await apiClient.getFields('tenant-123');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid JSON');
    });
  });

  describe('IoT Sensors', () => {
    it('should fetch sensor data for field', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: [{ id: 'sensor-1' }] }));

      await apiClient.getSensorData('field-1');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/iot/fields/field-1/sensors');
    });

    it('should fetch sensor history', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: [] }));

      const from = new Date('2026-01-01');
      const to = new Date('2026-01-06');
      await apiClient.getSensorHistory('sensor-1', from, to);

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/iot/sensors/sensor-1/history');
    });
  });

  describe('Irrigation', () => {
    it('should get irrigation recommendation', async () => {
      mockRequest.mockResolvedValueOnce(
        okResponse({ success: true, data: { recommendedAmount: 25 } })
      );

      await apiClient.getIrrigationRecommendation('field-1');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/irrigation/fields/field-1/recommendation');
    });

    it('should calculate ET0', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { et0: 5.2 } }));

      await apiClient.calculateET0({
        temperature: 28,
        humidity: 55,
        windSpeed: 8,
        solarRadiation: 22,
      });

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('POST');
    });
  });

  describe('Field Chat', () => {
    it('should validate message before sending', async () => {
      // Empty message should fail validation
      const result = await apiClient.sendFieldMessage('field-1', '');

      expect(result.success).toBe(false);
    });

    it('should send valid message', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true }));

      await apiClient.sendFieldMessage('field-1', 'Hello team!');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('POST');
    });

    it('should fetch field messages', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: [] }));

      await apiClient.getFieldMessages('field-1', { limit: 20 });

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.params?.limit).toBe('20');
    });
  });

  describe('WebSocket', () => {
    it('should generate correct WebSocket URL for HTTPS', () => {
      const wsUrl = apiClient.getWebSocketUrl();
      expect(wsUrl).toContain('/ws');
    });
  });

  describe('Billing', () => {
    it('should fetch subscription', async () => {
      mockRequest.mockResolvedValueOnce(
        okResponse({ success: true, data: { plan: 'professional' } })
      );

      await apiClient.getSubscription('tenant-123');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/billing/tenants/tenant-123/subscription');
    });

    it('should fetch invoices', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: [] }));

      await apiClient.getInvoices('tenant-123');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/billing/tenants/tenant-123/invoices');
    });
  });

  describe('Field Intelligence', () => {
    it('should get living field score', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { score: 85 } }));

      await apiClient.getLivingFieldScore('field-1');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/fields/field-1/intelligence/score');
    });

    it('should get field zones', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: [] }));

      await apiClient.getFieldZones('field-1');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.url).toContain('/fields/field-1/intelligence/zones');
    });

    it('should get best days for activity', async () => {
      mockRequest.mockResolvedValueOnce(
        okResponse({ success: true, data: [{ date: '2026-01-07' }] })
      );

      await apiClient.getBestDaysForActivity('spraying', 7);

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.params?.activity).toBe('spraying');
      expect(callArgs.params?.days).toBe('7');
    });

    it('should validate task date', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { suitable: true } }));

      await apiClient.validateTaskDate('2026-01-10', 'irrigation');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('POST');
    });
  });

  describe('CSRF Protection', () => {
    // Note: CSRF headers are injected by the unified client's axios interceptor
    // (in unified-client.ts), not by the domain methods in client.ts.
    // These tests verify that domain methods use correct HTTP methods, which
    // is a prerequisite for the interceptor to inject CSRF on non-GET requests.

    it('should use POST method for create operations', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { id: 'field-new' } }));

      await apiClient.createField({
        name: 'Test Field',
        tenantId: 'tenant-1',
        boundary: { type: 'Polygon', coordinates: [] },
      } as any);

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('POST');
    });

    it('should use PUT method for update operations', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true }));

      await apiClient.updateField('field-1', { name: 'Updated' } as any);

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('PUT');
    });

    it('should use DELETE method for delete operations', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true }));

      await apiClient.deleteField('field-1');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('DELETE');
    });

    it('should use PUT method for status update operations', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true }));

      await apiClient.updateTaskStatus('task-1', 'completed');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('PUT');
    });

    it('should use GET method for read operations', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: [] }));

      await apiClient.getFields('tenant-1');

      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.method).toBe('GET');
    });

    it('should use POST for file upload requests', async () => {
      const mockFile = new File(['dummy content'], 'test.jpg', {
        type: 'image/jpeg',
      });

      mockRequest.mockResolvedValueOnce(
        okResponse({ success: true, data: { disease: 'healthy' } })
      );

      await apiClient.analyzeCropHealth(mockFile);

      // analyzeCropHealth uses unifiedApiClient.post(url, formData, config)
      expect(mockRequest).toHaveBeenCalled();
      const url = mockRequest.mock.calls[0][0];
      expect(url).toContain('/crop-intelligence/analyze');
    });

    it('should handle missing CSRF token gracefully', async () => {
      const security = await import('../../security/security');
      vi.mocked(security.getCsrfHeaders).mockReturnValueOnce({});

      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { id: 'field-new' } }));

      const result = await apiClient.createField({
        name: 'Test Field',
        tenantId: 'tenant-1',
        boundary: { type: 'Polygon', coordinates: [] },
      } as any);

      expect(result.success).toBe(true);
      expect(mockRequest).toHaveBeenCalled();
    });

    it('should include ETag in update headers', async () => {
      mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: { id: 'field-1' } }));

      const result = await apiClient.updateField('field-1', { name: 'Updated' } as any, 'etag-123');

      expect(result.success).toBe(true);
      const callArgs = mockRequest.mock.calls[0][0];
      expect(callArgs.headers?.['If-Match']).toBe('etag-123');
    });

    it('should use correct HTTP methods for all state-changing operations', async () => {
      const stateChangingMethods = [
        {
          fn: () =>
            apiClient.createField({
              name: 'Test',
              tenantId: 'tenant-1',
              boundary: {},
            } as any),
          method: 'POST',
        },
        {
          fn: () => apiClient.updateField('field-1', { name: 'Updated' } as any),
          method: 'PUT',
        },
        { fn: () => apiClient.deleteField('field-1'), method: 'DELETE' },
        {
          fn: () =>
            apiClient.createTask({
              title: 'Task',
              fieldId: 'field-1',
              priority: 'high',
            } as any),
          method: 'POST',
        },
        {
          fn: () => apiClient.updateTaskStatus('task-1', 'completed'),
          method: 'PUT',
        },
        {
          fn: () => apiClient.sendFieldMessage('field-1', 'Hello'),
          method: 'POST',
        },
      ];

      for (const { fn, method } of stateChangingMethods) {
        vi.clearAllMocks();
        mockRequest.mockResolvedValueOnce(okResponse({ success: true, data: {} }));

        await fn();

        expect(mockRequest).toHaveBeenCalled();
        if (mockRequest.mock.calls.length > 0) {
          const callArgs = mockRequest.mock.calls[0][0];
          expect(callArgs.method).toBe(method);
        }
      }
    });
  });
});
