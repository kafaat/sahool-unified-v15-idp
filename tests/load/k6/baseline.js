/**
 * SAHOOL Platform - Performance Baseline Tests
 * اختبارات خط الأساس للأداء
 *
 * This script establishes performance baselines for critical API endpoints.
 * Run with: k6 run tests/load/k6/baseline.js
 *
 * Environment variables:
 *   - BASE_URL: API Gateway URL (default: http://localhost:8000)
 *   - AUTH_TOKEN: JWT token for authenticated requests
 *   - VUS: Number of virtual users (default: 10)
 *   - DURATION: Test duration (default: 30s)
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// ═══════════════════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';

// Custom metrics for SAHOOL-specific monitoring
const fieldOpsLatency = new Trend('field_ops_latency');
const weatherLatency = new Trend('weather_latency');
const ndviLatency = new Trend('ndvi_latency');
const advisoryLatency = new Trend('advisory_latency');
const authLatency = new Trend('auth_latency');
const errorRate = new Rate('errors');
const requestCount = new Counter('requests');

// ═══════════════════════════════════════════════════════════════════════════════
// Test Options - Performance Baselines
// ═══════════════════════════════════════════════════════════════════════════════

export const options = {
  // Scenarios for different load patterns
  scenarios: {
    // Baseline: Steady load
    baseline: {
      executor: 'constant-vus',
      vus: parseInt(__ENV.VUS) || 10,
      duration: __ENV.DURATION || '30s',
    },
    // Spike test: Sudden traffic increase
    spike_test: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '10s', target: 5 },
        { duration: '10s', target: 50 },  // Spike
        { duration: '10s', target: 5 },
        { duration: '10s', target: 0 },
      ],
      startTime: '31s',  // Start after baseline
    },
  },

  // Performance thresholds (SLOs)
  thresholds: {
    // Overall response time
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95th < 500ms, 99th < 1s

    // Error rate
    errors: ['rate<0.01'],  // Less than 1% errors

    // Service-specific thresholds
    field_ops_latency: ['p(95)<300'],    // Field operations < 300ms
    weather_latency: ['p(95)<200'],      // Weather queries < 200ms
    ndvi_latency: ['p(95)<500'],         // NDVI analysis < 500ms (compute-heavy)
    advisory_latency: ['p(95)<400'],     // AI advisory < 400ms
    auth_latency: ['p(95)<150'],         // Auth < 150ms
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════════

// Cryptographically secure random number in [0, 1)
function secureRandom() {
  const array = new Uint32Array(1);
  crypto.getRandomValues(array);
  return array[0] * Math.pow(2, -32);
}

function getHeaders() {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Tenant-ID': 'tenant_test_001',
  };

  if (AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }

  return headers;
}

function checkResponse(response, expectedStatus = 200) {
  const success = check(response, {
    'status is correct': (r) => r.status === expectedStatus,
    'response has body': (r) => r.body && r.body.length > 0,
    'response is JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch {
        return false;
      }
    },
  });

  if (!success) {
    errorRate.add(1);
  } else {
    errorRate.add(0);
  }

  requestCount.add(1);
  return success;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Test Scenarios
// ═══════════════════════════════════════════════════════════════════════════════

export default function () {
  const headers = getHeaders();

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check Endpoints (Baseline)
  // ─────────────────────────────────────────────────────────────────────────────

  group('Health Checks', function () {
    // Kong Gateway health
    const kongHealth = http.get(`${BASE_URL}/health`, { headers });
    checkResponse(kongHealth);

    // Field Management Service health
    const fieldHealth = http.get(`${BASE_URL}/api/v1/fields/healthz`, { headers });
    if (fieldHealth.status === 200) {
      fieldOpsLatency.add(fieldHealth.timings.duration);
    }
    checkResponse(fieldHealth);

    sleep(0.5);
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Authentication Endpoints
  // ─────────────────────────────────────────────────────────────────────────────

  group('Authentication', function () {
    // Token validation (if token provided)
    if (AUTH_TOKEN) {
      const tokenValidation = http.get(`${BASE_URL}/api/v1/auth/validate`, { headers });
      authLatency.add(tokenValidation.timings.duration);
      checkResponse(tokenValidation);
    }

    sleep(0.3);
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Field Operations (Core Business Logic)
  // ─────────────────────────────────────────────────────────────────────────────

  group('Field Operations', function () {
    // List fields
    const listFields = http.get(`${BASE_URL}/api/v1/fields`, { headers });
    fieldOpsLatency.add(listFields.timings.duration);
    checkResponse(listFields);

    // Get single field (if we have fields)
    if (listFields.status === 200) {
      try {
        const fields = JSON.parse(listFields.body);
        if (fields.data && fields.data.length > 0) {
          const fieldId = fields.data[0].id;
          const fieldDetail = http.get(`${BASE_URL}/api/v1/fields/${fieldId}`, { headers });
          fieldOpsLatency.add(fieldDetail.timings.duration);
          checkResponse(fieldDetail);
        }
      } catch (e) {
        // Parsing error, skip
      }
    }

    sleep(0.5);
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Weather Service
  // ─────────────────────────────────────────────────────────────────────────────

  group('Weather Service', function () {
    // Get current weather for Sana'a
    const weather = http.get(
      `${BASE_URL}/api/v1/weather/current?lat=15.3694&lon=44.1910`,
      { headers }
    );
    weatherLatency.add(weather.timings.duration);
    checkResponse(weather);

    // Get weather forecast
    const forecast = http.get(
      `${BASE_URL}/api/v1/weather/forecast?lat=15.3694&lon=44.1910&days=5`,
      { headers }
    );
    weatherLatency.add(forecast.timings.duration);
    checkResponse(forecast);

    sleep(0.3);
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // NDVI / Vegetation Analysis
  // ─────────────────────────────────────────────────────────────────────────────

  group('NDVI Analysis', function () {
    // Get latest NDVI for a field (mock field ID)
    const ndvi = http.get(
      `${BASE_URL}/api/v1/ndvi/latest?field_id=test_field_001`,
      { headers }
    );
    ndviLatency.add(ndvi.timings.duration);
    // Allow 404 if field doesn't exist
    checkResponse(ndvi, ndvi.status === 404 ? 404 : 200);

    sleep(0.5);
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // AI Advisory Service
  // ─────────────────────────────────────────────────────────────────────────────

  group('Advisory Service', function () {
    // Get recommendations for a field
    const advisory = http.get(
      `${BASE_URL}/api/v1/advisory/recommendations?field_id=test_field_001`,
      { headers }
    );
    advisoryLatency.add(advisory.timings.duration);
    // Allow 404 if field doesn't exist
    checkResponse(advisory, advisory.status === 404 ? 404 : 200);

    sleep(0.5);
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Task Management
  // ─────────────────────────────────────────────────────────────────────────────

  group('Task Management', function () {
    // List tasks
    const tasks = http.get(`${BASE_URL}/api/v1/tasks?status=pending&limit=10`, { headers });
    checkResponse(tasks);

    sleep(0.3);
  });

  // Random sleep between iterations (simulate real user behavior)
  sleep(secureRandom() * 2 + 1);  // 1-3 seconds
}

// ═══════════════════════════════════════════════════════════════════════════════
// Setup and Teardown
// ═══════════════════════════════════════════════════════════════════════════════

export function setup() {
  console.log('='.repeat(60));
  console.log('SAHOOL Performance Baseline Test');
  console.log('خط الأساس لاختبار الأداء');
  console.log('='.repeat(60));
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Auth Token: ${AUTH_TOKEN ? 'Provided' : 'Not provided'}`);
  console.log('='.repeat(60));

  // Verify services are available
  const healthCheck = http.get(`${BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    console.warn('Warning: Kong Gateway health check failed');
  }

  return {};
}

export function teardown(data) {
  console.log('='.repeat(60));
  console.log('Test Complete - خط الأساس للأداء مكتمل');
  console.log('='.repeat(60));
}

// ═══════════════════════════════════════════════════════════════════════════════
// Performance Baseline Thresholds (SLOs)
// ═══════════════════════════════════════════════════════════════════════════════
//
// These thresholds define acceptable performance for SAHOOL Platform:
//
// | Service              | P95 Latency | P99 Latency | Max Error Rate |
// |----------------------|-------------|-------------|----------------|
// | Overall              | 500ms       | 1000ms      | 1%             |
// | Field Operations     | 300ms       | 500ms       | 0.5%           |
// | Weather Service      | 200ms       | 400ms       | 1%             |
// | NDVI Analysis        | 500ms       | 1000ms      | 1%             |
// | AI Advisory          | 400ms       | 800ms       | 1%             |
// | Authentication       | 150ms       | 300ms       | 0.1%           |
//
// Note: These baselines are for development/staging. Production thresholds
// should be adjusted based on actual infrastructure capacity.
//
// ═══════════════════════════════════════════════════════════════════════════════
