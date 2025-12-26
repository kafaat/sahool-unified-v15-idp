/**
 * k6 Load Testing Configuration
 * SAHOOL Platform - Unified Agricultural Platform
 *
 * Environment Variables:
 * - BASE_URL: Base URL for API (default: http://localhost:8000)
 * - AUTH_URL: Authentication service URL (default: http://localhost:8080)
 * - FIELD_SERVICE_URL: Field service URL (default: http://localhost:8080)
 * - SATELLITE_URL: Satellite service URL (default: http://localhost:8090)
 * - WEATHER_URL: Weather service URL (default: http://localhost:8092)
 * - BILLING_URL: Billing service URL (default: http://localhost:8089)
 * - TEST_USER_EMAIL: Test user email (default: loadtest@sahool.io)
 * - TEST_USER_PASSWORD: Test user password (default: LoadTest123!)
 * - TENANT_ID: Tenant ID for testing (default: tenant_loadtest)
 */

import { group } from 'k6';

// Base configuration
export const config = {
  // Service URLs
  baseUrl: __ENV.BASE_URL || 'http://localhost:8000',
  authUrl: __ENV.AUTH_URL || 'http://localhost:8080',
  fieldServiceUrl: __ENV.FIELD_SERVICE_URL || 'http://localhost:8080',
  satelliteUrl: __ENV.SATELLITE_URL || 'http://localhost:8090',
  weatherUrl: __ENV.WEATHER_URL || 'http://localhost:8092',
  billingUrl: __ENV.BILLING_URL || 'http://localhost:8089',
  equipmentUrl: __ENV.EQUIPMENT_URL || 'http://localhost:8101',
  taskUrl: __ENV.TASK_URL || 'http://localhost:8103',
  cropHealthUrl: __ENV.CROP_HEALTH_URL || 'http://localhost:8095',

  // Test user credentials
  testUser: {
    email: __ENV.TEST_USER_EMAIL || 'loadtest@sahool.io',
    password: __ENV.TEST_USER_PASSWORD || 'LoadTest123!',
  },

  // Tenant configuration
  tenantId: __ENV.TENANT_ID || 'tenant_loadtest',

  // API timeouts
  timeout: '30s',

  // Rate limits
  rateLimit: {
    rpm: 1000, // requests per minute
  },
};

// Performance thresholds
export const thresholds = {
  // HTTP request duration thresholds
  'http_req_duration': [
    'p(95)<500',   // 95% of requests should be below 500ms
    'p(99)<1000',  // 99% of requests should be below 1s
    'avg<300',     // average should be below 300ms
  ],

  // HTTP request failed rate
  'http_req_failed': [
    'rate<0.01',   // error rate should be less than 1%
  ],

  // HTTP request rate
  'http_reqs': [
    'rate>10',     // should handle at least 10 requests per second
  ],

  // Custom checks
  'checks': [
    'rate>0.99',   // 99% of checks should pass
  ],

  // Group-specific thresholds
  'group_duration{group:::Authentication}': ['p(95)<1000'],
  'group_duration{group:::Field Operations}': ['p(95)<800'],
  'group_duration{group:::Weather Forecast}': ['p(95)<1500'],
  'group_duration{group:::Satellite Imagery}': ['p(95)<2000'],
  'group_duration{group:::Billing Operations}': ['p(95)<600'],
};

// Smoke test thresholds (stricter)
export const smokeThresholds = {
  'http_req_duration': ['p(95)<800', 'p(99)<1500'],
  'http_req_failed': ['rate<0.01'],
  'checks': ['rate>0.99'],
};

// Load test thresholds (production-like)
export const loadThresholds = {
  'http_req_duration': ['p(95)<500', 'p(99)<1000', 'avg<300'],
  'http_req_failed': ['rate<0.01'],
  'http_reqs': ['rate>50'], // 50 RPS minimum
  'checks': ['rate>0.99'],
};

// Stress test thresholds (degraded performance acceptable)
export const stressThresholds = {
  'http_req_duration': ['p(95)<2000', 'p(99)<5000'],
  'http_req_failed': ['rate<0.05'], // 5% error rate acceptable under stress
  'checks': ['rate>0.95'],
};

// Spike test thresholds
export const spikeThresholds = {
  'http_req_duration': ['p(95)<1500', 'p(99)<3000'],
  'http_req_failed': ['rate<0.05'],
  'checks': ['rate>0.95'],
};

// Soak test thresholds (long-running stability)
export const soakThresholds = {
  'http_req_duration': ['p(95)<600', 'p(99)<1200', 'avg<350'],
  'http_req_failed': ['rate<0.01'],
  'checks': ['rate>0.99'],
};

// Package tier limits (for quota testing)
export const packageTiers = {
  free: {
    name: 'Free',
    limits: {
      fields: 3,
      satellite_analyses_per_month: 10,
      storage_gb: 1,
    },
  },
  starter: {
    name: 'Starter',
    limits: {
      fields: 10,
      satellite_analyses_per_month: 50,
      ai_diagnoses_per_month: 20,
      storage_gb: 5,
    },
  },
  professional: {
    name: 'Professional',
    limits: {
      fields: 50,
      satellite_analyses_per_month: 200,
      ai_diagnoses_per_month: 100,
      storage_gb: 20,
    },
  },
  enterprise: {
    name: 'Enterprise',
    limits: {
      fields: -1, // unlimited
      satellite_analyses_per_month: -1,
      ai_diagnoses_per_month: -1,
      storage_gb: 100,
    },
  },
};

// Yemen locations for testing
export const yemenLocations = [
  { id: 'sanaa', name: 'Sana\'a', name_ar: 'صنعاء', lat: 15.3694, lon: 44.1910 },
  { id: 'aden', name: 'Aden', name_ar: 'عدن', lat: 12.7855, lon: 45.0187 },
  { id: 'taiz', name: 'Taiz', name_ar: 'تعز', lat: 13.5795, lon: 44.0202 },
  { id: 'hodeidah', name: 'Hodeidah', name_ar: 'الحديدة', lat: 14.7979, lon: 42.9545 },
  { id: 'ibb', name: 'Ibb', name_ar: 'إب', lat: 13.9667, lon: 44.1667 },
  { id: 'dhamar', name: 'Dhamar', name_ar: 'ذمار', lat: 14.5428, lon: 44.4051 },
  { id: 'marib', name: 'Marib', name_ar: 'مأرب', lat: 15.4622, lon: 45.3265 },
  { id: 'hajjah', name: 'Hajjah', name_ar: 'حجة', lat: 15.6949, lon: 43.6050 },
];

// Crop types for testing
export const cropTypes = [
  'wheat', 'tomato', 'coffee', 'qat', 'banana', 'cucumber',
  'pepper', 'potato', 'corn', 'grapes', 'date_palm', 'mango'
];

// Operation types
export const operationTypes = [
  'planting', 'irrigation', 'fertilization', 'spraying',
  'scouting', 'maintenance', 'sampling', 'harvest'
];

// Equipment types
export const equipmentTypes = [
  'tractor', 'pump', 'drone', 'harvester', 'sprayer',
  'pivot', 'sensor', 'vehicle'
];

export default config;
