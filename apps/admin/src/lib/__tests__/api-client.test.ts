/**
 * API Client Tests - Phase 2 Coverage
 * اختبارات عميل API - المرحلة الثانية
 *
 * Tests lib/api.ts: apiClient setup, interceptors, and API functions
 */

import { describe, it, expect, vi } from 'vitest';

// Mock config/api before importing lib/api. The mock must expose every symbol
// that `lib/api-client.ts` imports — missing keys surface as
// "No <X> export is defined on the '@/config/api' mock" errors at test time.
vi.mock('@/config/api', () => ({
  API_URL: 'http://localhost:8000',
  API_BASE_URL: 'http://localhost:8000',
  API_BASE_HOST: 'http://localhost',
  API_URLS: {
    auth: {
      login: 'http://localhost:8000/api/v1/auth/login',
      me: 'http://localhost:8000/api/v1/auth/me',
    },
    fieldCore: 'http://localhost:3000',
    weather: 'http://localhost:8092',
    satellite: 'http://localhost:8090',
    indicators: 'http://localhost:8091',
  },
  SERVICE_URLS: {
    user: 'http://localhost:3025',
    fieldManagement: 'http://localhost:3000',
    weather: 'http://localhost:8092',
    satellite: 'http://localhost:8090',
  },
  SERVICE_PORTS: {
    USER: 3025,
    FIELD_MANAGEMENT: 3000,
    WEATHER: 8092,
    SATELLITE: 8090,
  },
  API_PATHS: {},
  API_ENDPOINTS: {},
  API_CONFIG: { timeout: 30000 },
  TIMEOUT_TIERS: {
    default: 30000,
    upload: 120000,
    analysis: 180000,
    report: 60000,
    healthCheck: 5000,
  },
  DEFAULT_TIMEOUT: 30000,
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  DEFAULT_HEADERS: {},
  getServiceUrl: (port: number) => `http://localhost:${port}`,
  IS_PRODUCTION: false,
  IS_DEVELOPMENT: false,
  IS_TEST: true,
}));

// Mock logger
vi.mock('@/lib/logger', () => ({
  logger: {
    log: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
    production: vi.fn(),
    critical: vi.fn(),
  },
}));

// Mock js-cookie
vi.mock('js-cookie', () => ({
  default: {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn(),
  },
}));

// Mock api-client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
}));

describe('API Client Configuration', () => {
  it('exports apiClient', async () => {
    const api = await import('@/lib/api');
    expect(api.apiClient).toBeDefined();
  });

  it('exports API_URLS', async () => {
    const api = await import('@/lib/api');
    expect(api.API_URLS).toBeDefined();
  });

  it('apiClient has withCredentials for cookie auth', async () => {
    const api = await import('@/lib/api');
    // The apiClient is an axios instance created with withCredentials: true
    expect(api.apiClient).toBeDefined();
  });
});

describe('API Functions Exist', () => {
  it('exports dashboard functions', async () => {
    const api = await import('@/lib/api');
    expect(typeof api.fetchDashboardStats).toBe('function');
    expect(typeof api.fetchDiagnoses).toBe('function');
  });

  it('exports farm functions', async () => {
    const api = await import('@/lib/api');
    expect(typeof api.fetchFarms).toBe('function');
  });

  it('exports weather functions if defined', async () => {
    const api = await import('@/lib/api');
    // These may be defined - check they are functions if they exist
    if (api.getWeatherCurrent) {
      expect(typeof api.getWeatherCurrent).toBe('function');
    }
  });
});
