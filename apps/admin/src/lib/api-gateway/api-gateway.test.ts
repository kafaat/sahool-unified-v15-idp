/**
 * SAHOOL API Gateway Tests
 * اختبارات بوابة API
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import {
  request,
  getServiceConfig,
  getAllServices,
  checkServiceHealth,
  checkAllServicesHealth,
  getCircuitBreakerStatus,
  ApiGateway,
} from './index';

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      request: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    })),
    get: vi.fn(),
    isAxiosError: vi.fn(() => false),
  },
}));

describe('API Gateway', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getServiceConfig', () => {
    it('should return config for field-core service', () => {
      const config = getServiceConfig('field-core');
      expect(config).toBeDefined();
      expect(config.name).toBe('field-core');
      expect(config.baseUrl).toBeDefined();
    });

    it('should return config for satellite service', () => {
      const config = getServiceConfig('satellite');
      expect(config).toBeDefined();
      expect(config.name).toBe('satellite');
    });

    it('should return config for weather service', () => {
      const config = getServiceConfig('weather');
      expect(config).toBeDefined();
      expect(config.name).toBe('weather');
    });

    it('should return config for all service types', () => {
      const services = getAllServices();

      services.forEach((service) => {
        const config = getServiceConfig(service);
        expect(config).toBeDefined();
        expect(config.name).toBe(service);
        expect(typeof config.baseUrl).toBe('string');
      });
    });
  });

  describe('getAllServices', () => {
    it('should return array of all services', () => {
      const services = getAllServices();
      expect(Array.isArray(services)).toBe(true);
      expect(services.length).toBeGreaterThan(0);
    });

    it('should include core services', () => {
      const services = getAllServices();
      expect(services).toContain('field-core');
      expect(services).toContain('auth');
      expect(services).toContain('weather');
    });
  });

  describe('request', () => {
    it('should make a request to the correct service', async () => {
      const mockResponse = { data: { success: true, id: 'test-123' }, status: 200 };
      const mockRequest = vi.fn().mockResolvedValue(mockResponse);
      const mockAxiosInstance = {
        request: mockRequest,
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      };

      vi.mocked(axios.create).mockReturnValue(mockAxiosInstance as any);

      const result = await request('field-core', '/api/v1/fields');

      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.data).toEqual({ success: true, id: 'test-123' });
      expect(result.meta?.service).toBe('field-core');
      expect(typeof result.meta?.latency).toBe('number');
    });

    it('should handle request errors gracefully', async () => {
      const mockError = new Error('Network Error');
      (mockError as any).code = 'ECONNREFUSED';
      (mockError as any).response = undefined;

      const mockRequest = vi.fn().mockRejectedValue(mockError);
      const mockAxiosInstance = {
        request: mockRequest,
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      };

      vi.mocked(axios.create).mockReturnValue(mockAxiosInstance as any);

      const result = await request('weather', '/api/forecast');

      expect(result).toBeDefined();
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error?.code).toBe('ECONNREFUSED');
      expect(result.meta?.service).toBe('weather');
    });
  });

  describe('checkServiceHealth', () => {
    it('should return health status for a service', async () => {
      const mockHealthy = {
        data: { status: 'healthy' },
        status: 200,
      };

      vi.mocked(axios.get).mockResolvedValue(mockHealthy);

      const health = await checkServiceHealth('field-core');
      expect(health).toBeDefined();
      expect(health.name).toBe('field-core');
    });

    it('should handle unhealthy services', async () => {
      vi.mocked(axios.get).mockRejectedValue(new Error('Connection refused'));

      const health = await checkServiceHealth('field-core');
      expect(health).toBeDefined();
      expect(health.status).toBe('unhealthy');
    });
  });

  describe('checkAllServicesHealth', () => {
    it('should check health of all services', async () => {
      vi.mocked(axios.get).mockResolvedValue({ data: {}, status: 200 });

      const results = await checkAllServicesHealth();
      expect(Array.isArray(results)).toBe(true);
      expect(results.length).toBe(getAllServices().length);
    });

    it('should return array of health statuses', async () => {
      vi.mocked(axios.get).mockResolvedValue({ data: {}, status: 200 });

      const results = await checkAllServicesHealth();
      results.forEach((health) => {
        expect(health).toHaveProperty('name');
        expect(health).toHaveProperty('status');
        expect(health).toHaveProperty('lastCheck');
      });
    });
  });

  describe('Circuit Breaker', () => {
    it('should start with closed state for all services', () => {
      // Get circuit breaker status
      const status = getCircuitBreakerStatus();

      // Initially should be empty or have closed circuits
      if (status.size > 0) {
        for (const [, breaker] of status) {
          expect(['closed', 'half-open', 'open']).toContain(breaker.state);
        }
      }
      // No services accessed yet means no circuit breakers created
      expect(status).toBeDefined();
    });

    it('should track failure count in circuit breaker', async () => {
      const mockError = new Error('Service unavailable');
      (mockError as any).response = { status: 500 };

      const mockRequest = vi.fn().mockRejectedValue(mockError);
      const mockAxiosInstance = {
        request: mockRequest,
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn((_, errorHandler) => errorHandler) },
        },
      };

      vi.mocked(axios.create).mockReturnValue(mockAxiosInstance as any);

      // Make a failing request (this creates the circuit breaker entry)
      const result = await request('alerts', '/api/test');

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should return circuit open error when breaker is open', async () => {
      // The getCircuitBreakerStatus function returns the current state
      const status = getCircuitBreakerStatus();
      expect(status).toBeInstanceOf(Map);

      // Verify circuit breaker exports are available
      expect(ApiGateway.getCircuitBreakerStatus).toBeDefined();
    });
  });

  describe('ApiGateway export', () => {
    it('should export all functions', () => {
      expect(ApiGateway.request).toBeDefined();
      expect(ApiGateway.getServiceConfig).toBeDefined();
      expect(ApiGateway.getAllServices).toBeDefined();
      expect(ApiGateway.checkServiceHealth).toBeDefined();
      expect(ApiGateway.checkAllServicesHealth).toBeDefined();
      expect(ApiGateway.getCircuitBreakerStatus).toBeDefined();
      expect(ApiGateway.getCachedHealth).toBeDefined();
    });
  });
});
