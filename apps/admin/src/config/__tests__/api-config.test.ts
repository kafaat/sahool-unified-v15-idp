/**
 * API Configuration Tests
 * اختبارات إعدادات API
 *
 * Tests config/api.ts exports and URL generation
 */

import { describe, it, expect } from 'vitest';
import {
  API_BASE_URL,
  API_URL,
  IS_TEST,
  SERVICE_PORTS,
  getServiceUrl,
  SERVICE_URLS,
  API_PATHS,
  API_ENDPOINTS,
  API_URLS,
  TIMEOUT_TIERS,
  API_CONFIG,
} from '@/config/api';

describe('Environment Configuration', () => {
  it('IS_TEST is true in test environment', () => {
    expect(IS_TEST).toBe(true);
  });

  it('API_BASE_URL has a value', () => {
    expect(API_BASE_URL).toBeDefined();
    expect(typeof API_BASE_URL).toBe('string');
  });

  it('API_URL is alias for API_BASE_URL', () => {
    expect(API_URL).toBe(API_BASE_URL);
  });
});

describe('SERVICE_PORTS', () => {
  it('has all core service ports', () => {
    expect(SERVICE_PORTS.auth).toBeDefined();
    expect(SERVICE_PORTS.fieldManagement).toBeDefined();
    expect(SERVICE_PORTS.weather).toBeDefined();
    expect(SERVICE_PORTS.irrigation).toBeDefined();
    expect(SERVICE_PORTS.notifications).toBeDefined();
    expect(SERVICE_PORTS.task).toBeDefined();
    expect(SERVICE_PORTS.equipment).toBeDefined();
  });

  it('ports are valid numbers', () => {
    Object.entries(SERVICE_PORTS).forEach(([_key, port]) => {
      expect(typeof port).toBe('number');
      expect(port).toBeGreaterThan(0);
      expect(port).toBeLessThan(65536);
    });
  });

  it('has vision and terrain ports', () => {
    expect(SERVICE_PORTS.yoloVision).toBeDefined();
    expect(SERVICE_PORTS.terrainCore).toBeDefined();
    expect(SERVICE_PORTS.hydrology).toBeDefined();
    expect(SERVICE_PORTS.edgeOrchestrator).toBeDefined();
  });
});

describe('getServiceUrl', () => {
  it('generates URLs with port in development', () => {
    const url = getServiceUrl(3000);
    expect(url).toContain('3000');
    expect(url).toMatch(/^https?:\/\//);
  });
});

describe('SERVICE_URLS', () => {
  it('has URLs for all services', () => {
    expect(SERVICE_URLS.auth).toBeDefined();
    expect(SERVICE_URLS.fieldManagement).toBeDefined();
    expect(SERVICE_URLS.weather).toBeDefined();
    expect(SERVICE_URLS.satellite).toBeDefined();
  });

  it('URLs are strings with protocol', () => {
    Object.values(SERVICE_URLS).forEach((url) => {
      expect(typeof url).toBe('string');
      expect(url).toMatch(/^https?:\/\//);
    });
  });
});

describe('API_PATHS', () => {
  it('has auth paths', () => {
    expect(API_PATHS.auth.login).toBeDefined();
    expect(API_PATHS.auth.logout).toBeDefined();
    expect(API_PATHS.auth.refresh).toBeDefined();
    expect(API_PATHS.auth.me).toBeDefined();
  });

  it('has field paths with ID builder', () => {
    expect(API_PATHS.fields.list).toBeDefined();
    expect(typeof API_PATHS.fields.byId).toBe('function');
    expect(API_PATHS.fields.byId('test-id')).toContain('test-id');
  });

  it('has health paths', () => {
    expect(API_PATHS.health.live).toBeDefined();
    expect(API_PATHS.health.ready).toBeDefined();
  });

  it('has weather paths', () => {
    expect(API_PATHS.weather.current).toBeDefined();
    expect(API_PATHS.weather.forecast).toBeDefined();
  });

  it('has sensor paths with farm ID builder', () => {
    expect(typeof API_PATHS.sensors.readings).toBe('function');
  });

  it('has copilot paths', () => {
    expect(API_PATHS.copilot.chat).toBeDefined();
    expect(API_PATHS.copilot.tools).toBeDefined();
  });

  it('API_ENDPOINTS is alias for API_PATHS', () => {
    expect(API_ENDPOINTS).toBe(API_PATHS);
  });
});

describe('API_URLS', () => {
  it('has complete auth URLs', () => {
    expect(API_URLS.auth.login).toContain('login');
    expect(API_URLS.auth.logout).toContain('logout');
    expect(API_URLS.auth.refresh).toContain('refresh');
    expect(API_URLS.auth.me).toContain('me');
  });

  it('has field management URLs', () => {
    expect(API_URLS.fields.list).toBeDefined();
    expect(typeof API_URLS.fields.byId).toBe('function');
  });

  it('has weather URLs', () => {
    expect(API_URLS.weatherEndpoints.current).toBeDefined();
    expect(API_URLS.weatherEndpoints.forecast).toBeDefined();
  });

  it('has satellite URLs with field ID builders', () => {
    expect(typeof API_URLS.satelliteEndpoints.timeseries).toBe('function');
    const url = API_URLS.satelliteEndpoints.timeseries('field-1');
    expect(url).toContain('field-1');
  });
});

describe('TIMEOUT_TIERS', () => {
  it('has all required tiers', () => {
    expect(TIMEOUT_TIERS.default).toBeDefined();
    expect(TIMEOUT_TIERS.upload).toBeDefined();
    expect(TIMEOUT_TIERS.analysis).toBeDefined();
    expect(TIMEOUT_TIERS.report).toBeDefined();
    expect(TIMEOUT_TIERS.healthCheck).toBeDefined();
  });

  it('tiers are in increasing order', () => {
    expect(TIMEOUT_TIERS.healthCheck).toBeLessThanOrEqual(TIMEOUT_TIERS.default);
    expect(TIMEOUT_TIERS.default).toBeLessThanOrEqual(TIMEOUT_TIERS.upload);
    expect(TIMEOUT_TIERS.upload).toBeLessThanOrEqual(TIMEOUT_TIERS.analysis);
  });
});

describe('API_CONFIG', () => {
  it('has timeout configuration', () => {
    expect(API_CONFIG.timeout).toBeDefined();
    expect(typeof API_CONFIG.timeout).toBe('number');
  });
});
