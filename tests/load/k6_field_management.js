/**
 * SAHOOL Platform - Field Management Service Load Test
 * اختبار الحمل لخدمة إدارة الحقول
 *
 * Service: field-management-service (port 3000)
 * Purpose: Load test field CRUD operations, the highest-traffic service in the platform
 *
 * Run with:
 *   k6 run tests/load/k6_field_management.js
 *   k6 run --env BASE_URL=http://field-service:3000 tests/load/k6_field_management.js
 *
 * Environment variables:
 *   - BASE_URL: Field management service URL (default: http://localhost:3000)
 *   - AUTH_TOKEN: JWT token for authenticated requests
 *   - TENANT_ID: Tenant ID for multi-tenant testing (default: tenant_loadtest)
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// =============================================================================
// Configuration
// =============================================================================

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';
const TENANT_ID = __ENV.TENANT_ID || 'tenant_loadtest';

// =============================================================================
// Custom Metrics
// =============================================================================

// Latency trends
const healthLatency = new Trend('field_health_latency', true);
const listFieldsLatency = new Trend('field_list_latency', true);
const getFieldLatency = new Trend('field_get_latency', true);
const createFieldLatency = new Trend('field_create_latency', true);
const updateFieldLatency = new Trend('field_update_latency', true);
const deleteFieldLatency = new Trend('field_delete_latency', true);
const fieldSearchLatency = new Trend('field_search_latency', true);

// Success rates
const readSuccessRate = new Rate('field_read_success');
const writeSuccessRate = new Rate('field_write_success');
const healthSuccessRate = new Rate('field_health_success');

// Counters
const totalReads = new Counter('field_total_reads');
const totalWrites = new Counter('field_total_writes');
const failedOperations = new Counter('field_failed_operations');
const rateLimitHits = new Counter('field_rate_limit_hits');

// =============================================================================
// Test Options
// =============================================================================

export const options = {
  stages: [
    { duration: '1m', target: 20 },    // Ramp up to 20 VUs
    { duration: '2m', target: 100 },   // Ramp up to 100 VUs
    { duration: '3m', target: 200 },   // Ramp up to 200 VUs
    { duration: '3m', target: 200 },   // Hold at 200 VUs
    { duration: '1m', target: 50 },    // Ramp down to 50 VUs
    { duration: '1m', target: 0 },     // Ramp down to 0
  ],
  thresholds: {
    // Health endpoint thresholds
    field_health_latency: ['p(95)<200', 'p(99)<500'],
    field_health_success: ['rate>0.99'],

    // Read endpoint thresholds
    field_list_latency: ['p(95)<500', 'p(99)<1000'],
    field_get_latency: ['p(95)<500', 'p(99)<1000'],
    field_search_latency: ['p(95)<500', 'p(99)<1000'],

    // Write endpoint thresholds
    field_create_latency: ['p(95)<1000', 'p(99)<2000'],
    field_update_latency: ['p(95)<1000', 'p(99)<2000'],
    field_delete_latency: ['p(95)<1000', 'p(99)<2000'],

    // Overall success rates
    field_read_success: ['rate>0.98'],
    field_write_success: ['rate>0.95'],

    // General HTTP thresholds
    http_req_failed: ['rate<0.03'],
    checks: ['rate>0.95'],
  },
  tags: {
    test_type: 'load',
    service: 'field-management-service',
    environment: __ENV.ENVIRONMENT || 'local',
  },
};

// =============================================================================
// Helper Functions
// =============================================================================

function getHeaders() {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Tenant-ID': TENANT_ID,
  };
  if (AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  return headers;
}

function randomElement(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function randomFloat(min, max) {
  return parseFloat((Math.random() * (max - min) + min).toFixed(4));
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomString(length) {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Generate a realistic GeoJSON polygon for field boundary.
 */
function generateFieldPolygon(centerLat, centerLon) {
  const radius = randomFloat(0.002, 0.01); // ~0.2-1.0 km
  const points = randomInt(4, 8);
  const coordinates = [];

  for (let i = 0; i < points; i++) {
    const angle = (2 * Math.PI * i) / points;
    const r = radius * (0.8 + Math.random() * 0.4);
    coordinates.push([
      centerLon + r * Math.cos(angle),
      centerLat + r * Math.sin(angle),
    ]);
  }
  coordinates.push(coordinates[0]); // Close polygon

  return {
    type: 'Polygon',
    coordinates: [coordinates],
  };
}

/**
 * Generate a random field creation payload.
 */
function generateFieldPayload() {
  const location = randomElement(YEMEN_LOCATIONS);
  const crop = randomElement(CROP_TYPES);

  return {
    tenant_id: TENANT_ID,
    name: `Test Field ${randomString(6)}`,
    name_ar: `حقل اختبار ${randomString(6)}`,
    crop_type: crop,
    area_hectares: randomFloat(0.5, 25.0),
    geometry: generateFieldPolygon(location.lat, location.lon),
    soil_type: randomElement(SOIL_TYPES),
    irrigation_type: randomElement(IRRIGATION_TYPES),
    planting_date: new Date(Date.now() - randomInt(1, 90) * 86400000).toISOString().split('T')[0],
    status: randomElement(['active', 'planned', 'fallow']),
    metadata: {
      test: true,
      loadtest_id: `loadtest_${Date.now()}`,
    },
  };
}

// =============================================================================
// Test Data
// =============================================================================

const YEMEN_LOCATIONS = [
  { name: 'Sanaa',    lat: 15.3694, lon: 44.1910 },
  { name: 'Aden',     lat: 12.7855, lon: 45.0187 },
  { name: 'Taiz',     lat: 13.5795, lon: 44.0202 },
  { name: 'Hodeidah', lat: 14.7979, lon: 42.9545 },
  { name: 'Ibb',      lat: 13.9667, lon: 44.1667 },
  { name: 'Dhamar',   lat: 14.5428, lon: 44.4051 },
  { name: 'Marib',    lat: 15.4622, lon: 45.3265 },
  { name: 'Hajjah',   lat: 15.6949, lon: 43.6050 },
];

const CROP_TYPES = ['wheat', 'tomato', 'coffee', 'qat', 'banana', 'cucumber', 'pepper', 'potato', 'corn', 'grapes', 'date_palm', 'mango', 'barley'];
const SOIL_TYPES = ['loamy', 'sandy', 'clay', 'silty', 'chalky', 'peaty'];
const IRRIGATION_TYPES = ['drip', 'sprinkler', 'flood', 'furrow', 'center_pivot', 'rainfed'];
const PAGE_SIZES = [10, 20, 50];
const SORT_FIELDS = ['name', 'created_at', 'area_hectares', 'crop_type'];
const SORT_ORDERS = ['asc', 'desc'];

// =============================================================================
// Setup
// =============================================================================

export function setup() {
  console.log('='.repeat(70));
  console.log('SAHOOL - Field Management Service Load Test');
  console.log('اختبار الحمل لخدمة إدارة الحقول');
  console.log('='.repeat(70));
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Auth Token: ${AUTH_TOKEN ? 'Provided' : 'Not provided'}`);
  console.log(`Tenant ID: ${TENANT_ID}`);
  console.log('Peak VUs: 200');
  console.log('='.repeat(70));

  // Verify service is reachable
  const healthResp = http.get(`${BASE_URL}/healthz`);
  if (healthResp.status !== 200) {
    console.warn(`WARNING: Health check returned status ${healthResp.status}`);
  } else {
    console.log('Service health check passed.');
  }

  // Try to create a seed field to use for GET requests
  const headers = getHeaders();
  const seedField = generateFieldPayload();
  const createResp = http.post(
    `${BASE_URL}/api/v1/fields`,
    JSON.stringify(seedField),
    { headers, timeout: '10s' }
  );

  let seedFieldId = null;
  if (createResp.status === 201 || createResp.status === 200) {
    try {
      const body = JSON.parse(createResp.body);
      seedFieldId = body.id || body.field_id;
      console.log(`Seed field created: ${seedFieldId}`);
    } catch {
      // Ignore parse errors
    }
  }

  return {
    startTime: Date.now(),
    seedFieldId: seedFieldId,
  };
}

// =============================================================================
// Test Scenarios
// =============================================================================

export default function (data) {
  const headers = getHeaders();
  let createdFieldId = null;

  // -------------------------------------------------------------------------
  // Group 1: Health and Readiness Checks
  // -------------------------------------------------------------------------
  group('Health Checks', function () {
    const healthResp = http.get(`${BASE_URL}/healthz`, { headers });
    healthLatency.add(healthResp.timings.duration);

    const healthOk = check(healthResp, {
      'healthz returns 200': (r) => r.status === 200,
      'healthz has status field': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.status !== undefined;
        } catch {
          return false;
        }
      },
    });
    healthSuccessRate.add(healthOk ? 1 : 0);

    sleep(0.2);
  });

  // -------------------------------------------------------------------------
  // Group 2: List Fields (Read - most common operation)
  // -------------------------------------------------------------------------
  group('List Fields', function () {
    const pageSize = randomElement(PAGE_SIZES);
    const sortField = randomElement(SORT_FIELDS);
    const sortOrder = randomElement(SORT_ORDERS);
    const page = randomInt(1, 5);

    const url = `${BASE_URL}/api/v1/fields?tenant_id=${TENANT_ID}&limit=${pageSize}&page=${page}&sort=${sortField}&order=${sortOrder}`;
    const listResp = http.get(url, { headers, timeout: '10s' });

    listFieldsLatency.add(listResp.timings.duration);
    totalReads.add(1);

    const listOk = check(listResp, {
      'list fields returns 200': (r) => r.status === 200,
      'list fields not server error': (r) => r.status < 500,
      'list fields has response body': (r) => r.body && r.body.length > 0,
    });

    if (listOk) {
      readSuccessRate.add(1);
    } else {
      readSuccessRate.add(0);
      failedOperations.add(1);
    }

    if (listResp.status === 429) {
      rateLimitHits.add(1);
    }

    // Validate response structure
    if (listResp.status === 200) {
      check(listResp, {
        'list response is valid JSON': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.data !== undefined || Array.isArray(body);
          } catch {
            return false;
          }
        },
      });
    }

    sleep(0.3);
  });

  // -------------------------------------------------------------------------
  // Group 3: Filter and Search Fields (Read)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.4) {
    group('Search Fields', function () {
      // Filter by crop type
      const cropFilter = randomElement(CROP_TYPES);
      const searchUrl = `${BASE_URL}/api/v1/fields?tenant_id=${TENANT_ID}&crop_type=${cropFilter}&limit=20`;
      const searchResp = http.get(searchUrl, { headers, timeout: '10s' });

      fieldSearchLatency.add(searchResp.timings.duration);
      totalReads.add(1);

      const searchOk = check(searchResp, {
        'search fields responds': (r) => r.status === 200 || r.status === 404,
        'search fields not server error': (r) => r.status < 500,
      });

      if (searchOk) {
        readSuccessRate.add(1);
      } else {
        readSuccessRate.add(0);
        failedOperations.add(1);
      }

      sleep(0.3);

      // Filter by status
      const statusFilter = randomElement(['active', 'planned', 'fallow', 'harvested']);
      const statusUrl = `${BASE_URL}/api/v1/fields?tenant_id=${TENANT_ID}&status=${statusFilter}&limit=20`;
      const statusResp = http.get(statusUrl, { headers, timeout: '10s' });

      fieldSearchLatency.add(statusResp.timings.duration);
      totalReads.add(1);

      check(statusResp, {
        'status filter responds': (r) => r.status < 500,
      });

      readSuccessRate.add(statusResp.status < 500 ? 1 : 0);

      sleep(0.3);
    });
  }

  // -------------------------------------------------------------------------
  // Group 4: Get Single Field (Read)
  // -------------------------------------------------------------------------
  group('Get Single Field', function () {
    // Use seed field or generate an ID
    const fieldId = data.seedFieldId || `field_${randomInt(1000, 9999)}`;
    const getResp = http.get(
      `${BASE_URL}/api/v1/fields/${fieldId}`,
      { headers, timeout: '10s' }
    );

    getFieldLatency.add(getResp.timings.duration);
    totalReads.add(1);

    const getOk = check(getResp, {
      'get field responds': (r) => r.status === 200 || r.status === 404,
      'get field not server error': (r) => r.status < 500,
    });

    if (getOk) {
      readSuccessRate.add(1);
    } else {
      readSuccessRate.add(0);
      failedOperations.add(1);
    }

    // Validate response structure for successful requests
    if (getResp.status === 200) {
      check(getResp, {
        'field response has id': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.id !== undefined || body.field_id !== undefined;
          } catch {
            return false;
          }
        },
        'field response has name': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.name !== undefined;
          } catch {
            return false;
          }
        },
      });
    }

    sleep(0.3);
  });

  // -------------------------------------------------------------------------
  // Group 5: Create Field (Write - 20% of iterations)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.2) {
    group('Create Field', function () {
      const fieldPayload = generateFieldPayload();
      const createResp = http.post(
        `${BASE_URL}/api/v1/fields`,
        JSON.stringify(fieldPayload),
        { headers, timeout: '15s' }
      );

      createFieldLatency.add(createResp.timings.duration);
      totalWrites.add(1);

      const createOk = check(createResp, {
        'create field responds': (r) => r.status === 201 || r.status === 200 || r.status === 400 || r.status === 422,
        'create field not server error': (r) => r.status < 500,
        'create field within threshold': (r) => r.timings.duration < 3000,
      });

      if (createOk) {
        writeSuccessRate.add(1);
      } else {
        writeSuccessRate.add(0);
        failedOperations.add(1);
      }

      if (createResp.status === 429) {
        rateLimitHits.add(1);
      }

      // Extract created field ID for subsequent operations
      if (createResp.status === 201 || createResp.status === 200) {
        try {
          const body = JSON.parse(createResp.body);
          createdFieldId = body.id || body.field_id;
        } catch {
          // Ignore parse errors
        }

        check(createResp, {
          'created field has id': (r) => {
            try {
              const body = JSON.parse(r.body);
              return body.id !== undefined || body.field_id !== undefined;
            } catch {
              return false;
            }
          },
        });
      }

      sleep(0.5);
    });
  }

  // -------------------------------------------------------------------------
  // Group 6: Update Field (Write - 10% of iterations, requires created field)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.1 && createdFieldId) {
    group('Update Field', function () {
      const updatePayload = JSON.stringify({
        name: `Updated Field ${randomString(6)}`,
        name_ar: `حقل محدث ${randomString(6)}`,
        crop_type: randomElement(CROP_TYPES),
        status: randomElement(['active', 'planned', 'fallow']),
        soil_type: randomElement(SOIL_TYPES),
        irrigation_type: randomElement(IRRIGATION_TYPES),
      });

      const updateResp = http.put(
        `${BASE_URL}/api/v1/fields/${createdFieldId}`,
        updatePayload,
        { headers, timeout: '15s' }
      );

      updateFieldLatency.add(updateResp.timings.duration);
      totalWrites.add(1);

      const updateOk = check(updateResp, {
        'update field responds': (r) => r.status === 200 || r.status === 400 || r.status === 404 || r.status === 422,
        'update field not server error': (r) => r.status < 500,
      });

      if (updateOk) {
        writeSuccessRate.add(1);
      } else {
        writeSuccessRate.add(0);
        failedOperations.add(1);
      }

      sleep(0.5);
    });
  }

  // -------------------------------------------------------------------------
  // Group 7: Delete Field (Write - 5% of iterations, requires created field)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.05 && createdFieldId) {
    group('Delete Field', function () {
      const deleteResp = http.del(
        `${BASE_URL}/api/v1/fields/${createdFieldId}`,
        null,
        { headers, timeout: '15s' }
      );

      deleteFieldLatency.add(deleteResp.timings.duration);
      totalWrites.add(1);

      const deleteOk = check(deleteResp, {
        'delete field responds': (r) => r.status === 200 || r.status === 204 || r.status === 404,
        'delete field not server error': (r) => r.status < 500,
      });

      if (deleteOk) {
        writeSuccessRate.add(1);
      } else {
        writeSuccessRate.add(0);
        failedOperations.add(1);
      }

      // Clear the ID since the field is deleted
      createdFieldId = null;

      sleep(0.5);
    });
  }

  // -------------------------------------------------------------------------
  // Group 8: Rapid Read Burst (15% of iterations - simulates dashboard refresh)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.15) {
    group('Dashboard Refresh Burst', function () {
      // Simulate a user refreshing a dashboard - multiple reads in quick succession
      const requests = [
        `${BASE_URL}/api/v1/fields?tenant_id=${TENANT_ID}&limit=10&sort=created_at&order=desc`,
        `${BASE_URL}/api/v1/fields?tenant_id=${TENANT_ID}&status=active&limit=50`,
        `${BASE_URL}/api/v1/fields?tenant_id=${TENANT_ID}&crop_type=wheat&limit=20`,
      ];

      for (const url of requests) {
        const resp = http.get(url, { headers, timeout: '10s' });
        listFieldsLatency.add(resp.timings.duration);
        totalReads.add(1);

        check(resp, {
          'burst read responds': (r) => r.status < 500,
        });

        readSuccessRate.add(resp.status < 500 ? 1 : 0);
      }

      sleep(0.5);
    });
  }

  // Random sleep between iterations
  sleep(randomFloat(0.5, 2.0));
}

// =============================================================================
// Teardown
// =============================================================================

export function teardown(data) {
  const durationSec = ((Date.now() - data.startTime) / 1000).toFixed(2);
  console.log('='.repeat(70));
  console.log('Field Management Service Load Test Complete');
  console.log('اختبار الحمل لخدمة إدارة الحقول مكتمل');
  console.log(`Duration: ${durationSec} seconds`);
  console.log('='.repeat(70));
}

// =============================================================================
// Handle Summary - JSON Output
// =============================================================================

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    test_type: 'field_management_load_test',
    service: 'field-management-service',
    base_url: BASE_URL,
    health: {
      latency_p95: (data.metrics.field_health_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.field_health_success?.values?.rate || 0) * 100).toFixed(2) + '%',
    },
    reads: {
      list_latency_p95: (data.metrics.field_list_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      get_latency_p95: (data.metrics.field_get_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      search_latency_p95: (data.metrics.field_search_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.field_read_success?.values?.rate || 0) * 100).toFixed(2) + '%',
      total: data.metrics.field_total_reads?.values?.count || 0,
    },
    writes: {
      create_latency_p95: (data.metrics.field_create_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      update_latency_p95: (data.metrics.field_update_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      delete_latency_p95: (data.metrics.field_delete_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.field_write_success?.values?.rate || 0) * 100).toFixed(2) + '%',
      total: data.metrics.field_total_writes?.values?.count || 0,
    },
    errors: {
      failed: data.metrics.field_failed_operations?.values?.count || 0,
      rate_limit_hits: data.metrics.field_rate_limit_hits?.values?.count || 0,
    },
    http: {
      requests: data.metrics.http_reqs?.values?.count || 0,
      failed_rate: ((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2) + '%',
      duration_p95: (data.metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
    },
  };

  const textSummary = `
${'='.repeat(70)}
           Field Management Service Load Test Results
           نتائج اختبار الحمل لخدمة إدارة الحقول
${'='.repeat(70)}

HEALTH CHECKS:
${'─'.repeat(70)}
  Latency (p95):           ${summary.health.latency_p95}
  Success Rate:            ${summary.health.success_rate}

READ OPERATIONS:
${'─'.repeat(70)}
  List Fields (p95):       ${summary.reads.list_latency_p95}
  Get Field (p95):         ${summary.reads.get_latency_p95}
  Search Fields (p95):     ${summary.reads.search_latency_p95}
  Success Rate:            ${summary.reads.success_rate}
  Total Reads:             ${summary.reads.total}

WRITE OPERATIONS:
${'─'.repeat(70)}
  Create Field (p95):      ${summary.writes.create_latency_p95}
  Update Field (p95):      ${summary.writes.update_latency_p95}
  Delete Field (p95):      ${summary.writes.delete_latency_p95}
  Success Rate:            ${summary.writes.success_rate}
  Total Writes:            ${summary.writes.total}

ERRORS:
${'─'.repeat(70)}
  Failed Operations:       ${summary.errors.failed}
  Rate Limit Hits:         ${summary.errors.rate_limit_hits}

HTTP OVERVIEW:
${'─'.repeat(70)}
  Total Requests:          ${summary.http.requests}
  Failed Rate:             ${summary.http.failed_rate}
  Duration (p95):          ${summary.http.duration_p95}

${'='.repeat(70)}
`;

  return {
    stdout: textSummary,
    './results/k6_field_management_results.json': JSON.stringify(summary, null, 2),
  };
}
