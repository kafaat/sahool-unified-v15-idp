/**
 * SAHOOL Platform - Terrain Core Service Load Test
 * اختبار الحمل لخدمة التضاريس الأساسية
 *
 * Service: terrain-core-service (port 8185)
 * Purpose: Load test terrain analysis endpoints for DEM processing, slope, and aspect analysis
 *
 * Run with:
 *   k6 run tests/load/k6_terrain_service.js
 *   k6 run --env BASE_URL=http://terrain-service:8185 tests/load/k6_terrain_service.js
 *
 * Environment variables:
 *   - BASE_URL: Terrain service URL (default: http://localhost:8185)
 *   - AUTH_TOKEN: JWT token for authenticated requests
 *   - TENANT_ID: Tenant ID for multi-tenant testing (default: tenant_loadtest)
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// =============================================================================
// Configuration
// =============================================================================

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8185';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';
const TENANT_ID = __ENV.TENANT_ID || 'tenant_loadtest';

// =============================================================================
// Custom Metrics
// =============================================================================

// Latency trends
const healthLatency = new Trend('terrain_health_latency', true);
const demProcessingLatency = new Trend('terrain_dem_processing_latency', true);
const slopeAnalysisLatency = new Trend('terrain_slope_analysis_latency', true);
const aspectAnalysisLatency = new Trend('terrain_aspect_analysis_latency', true);
const elevationQueryLatency = new Trend('terrain_elevation_query_latency', true);

// Success rates
const analysisSuccessRate = new Rate('terrain_analysis_success');
const healthSuccessRate = new Rate('terrain_health_success');

// Counters
const totalAnalyses = new Counter('terrain_total_analyses');
const failedAnalyses = new Counter('terrain_failed_analyses');
const rateLimitHits = new Counter('terrain_rate_limit_hits');

// =============================================================================
// Test Options
// =============================================================================

export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 VUs
    { duration: '2m', target: 30 },   // Ramp up to 30 VUs
    { duration: '3m', target: 50 },   // Ramp up to 50 VUs
    { duration: '3m', target: 50 },   // Hold at 50 VUs
    { duration: '1m', target: 20 },   // Ramp down to 20 VUs
    { duration: '1m', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    // Health endpoint thresholds
    terrain_health_latency: ['p(95)<200', 'p(99)<500'],
    terrain_health_success: ['rate>0.99'],

    // Analysis endpoint thresholds
    terrain_dem_processing_latency: ['p(95)<3000', 'p(99)<5000'],
    terrain_slope_analysis_latency: ['p(95)<3000', 'p(99)<5000'],
    terrain_aspect_analysis_latency: ['p(95)<3000', 'p(99)<5000'],
    terrain_elevation_query_latency: ['p(95)<1000', 'p(99)<2000'],

    // Overall success rate
    terrain_analysis_success: ['rate>0.95'],

    // General HTTP thresholds
    http_req_failed: ['rate<0.05'],
    checks: ['rate>0.95'],
  },
  tags: {
    test_type: 'load',
    service: 'terrain-core-service',
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

// Cryptographically secure random number in [0, 1)
function secureRandom() {
  const array = new Uint32Array(1);
  crypto.getRandomValues(array);
  return array[0] * Math.pow(2, -32);
}

function randomElement(array) {
  return array[Math.floor(secureRandom() * array.length)];
}

function randomFloat(min, max) {
  return parseFloat((secureRandom() * (max - min) + min).toFixed(4));
}

function randomInt(min, max) {
  return Math.floor(secureRandom() * (max - min + 1)) + min;
}

/**
 * Generate a random GeoJSON polygon within Yemen's geographic bounds.
 * Used to simulate field boundary submissions for terrain analysis.
 */
function generateFieldBoundary() {
  // Yemen approximate bounds: lat 12.5-16.5, lon 42.5-53.0
  const centerLat = randomFloat(13.0, 16.0);
  const centerLon = randomFloat(43.0, 48.0);
  const radius = randomFloat(0.005, 0.02); // ~0.5-2km

  const points = randomInt(4, 8);
  const coordinates = [];
  for (let i = 0; i < points; i++) {
    const angle = (2 * Math.PI * i) / points;
    const r = radius * (0.8 + secureRandom() * 0.4);
    coordinates.push([
      centerLon + r * Math.cos(angle),
      centerLat + r * Math.sin(angle),
    ]);
  }
  // Close the polygon
  coordinates.push(coordinates[0]);

  return {
    type: 'Polygon',
    coordinates: [coordinates],
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
];

const RESOLUTIONS = [10, 30, 90]; // meters per pixel (Sentinel-2, SRTM 1-arc, SRTM 3-arc)
const OUTPUT_FORMATS = ['geotiff', 'json', 'png'];

// =============================================================================
// Setup
// =============================================================================

export function setup() {
  console.log('='.repeat(70));
  console.log('SAHOOL - Terrain Core Service Load Test');
  console.log('اختبار الحمل لخدمة التضاريس الأساسية');
  console.log('='.repeat(70));
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Auth Token: ${AUTH_TOKEN ? 'Provided' : 'Not provided'}`);
  console.log(`Tenant ID: ${TENANT_ID}`);
  console.log('='.repeat(70));

  // Verify service is reachable
  const healthResp = http.get(`${BASE_URL}/healthz`);
  if (healthResp.status !== 200) {
    console.warn(`WARNING: Health check returned status ${healthResp.status}`);
  } else {
    console.log('Service health check passed.');
  }

  return { startTime: Date.now() };
}

// =============================================================================
// Test Scenarios
// =============================================================================

export default function () {
  const headers = getHeaders();

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

    const readyResp = http.get(`${BASE_URL}/readyz`, { headers });
    healthLatency.add(readyResp.timings.duration);

    check(readyResp, {
      'readyz returns 200': (r) => r.status === 200,
    });

    sleep(0.3);
  });

  // -------------------------------------------------------------------------
  // Group 2: DEM Processing
  // -------------------------------------------------------------------------
  group('DEM Processing', function () {
    const boundary = generateFieldBoundary();
    const resolution = randomElement(RESOLUTIONS);

    const payload = JSON.stringify({
      field_id: `field_${randomInt(1000, 9999)}`,
      tenant_id: TENANT_ID,
      geometry: boundary,
      resolution: resolution,
      source: randomElement(['srtm', 'aster', 'copernicus']),
      output_format: randomElement(OUTPUT_FORMATS),
      include_statistics: true,
    });

    const resp = http.post(`${BASE_URL}/api/v1/terrain/dem`, payload, {
      headers,
      timeout: '30s',
    });

    demProcessingLatency.add(resp.timings.duration);
    totalAnalyses.add(1);

    const success = check(resp, {
      'DEM processing responds': (r) => r.status === 200 || r.status === 202 || r.status === 400 || r.status === 422,
      'DEM processing not server error': (r) => r.status < 500,
      'DEM processing within timeout': (r) => r.timings.duration < 8000,
    });

    if (success) {
      analysisSuccessRate.add(1);
    } else {
      analysisSuccessRate.add(0);
      failedAnalyses.add(1);
    }

    if (resp.status === 429) {
      rateLimitHits.add(1);
    }

    if (resp.status === 200) {
      check(resp, {
        'DEM response has elevation data': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.elevation !== undefined || body.statistics !== undefined || body.data !== undefined;
          } catch {
            return false;
          }
        },
      });
    }

    sleep(randomFloat(0.5, 1.5));
  });

  // -------------------------------------------------------------------------
  // Group 3: Slope Analysis
  // -------------------------------------------------------------------------
  group('Slope Analysis', function () {
    const boundary = generateFieldBoundary();

    const payload = JSON.stringify({
      field_id: `field_${randomInt(1000, 9999)}`,
      tenant_id: TENANT_ID,
      geometry: boundary,
      resolution: randomElement(RESOLUTIONS),
      units: randomElement(['degrees', 'percent']),
      classification: randomElement(['flat', 'gentle', 'moderate', 'steep', 'auto']),
      output_format: randomElement(OUTPUT_FORMATS),
    });

    const resp = http.post(`${BASE_URL}/api/v1/terrain/slope`, payload, {
      headers,
      timeout: '30s',
    });

    slopeAnalysisLatency.add(resp.timings.duration);
    totalAnalyses.add(1);

    const success = check(resp, {
      'slope analysis responds': (r) => r.status === 200 || r.status === 202 || r.status === 400 || r.status === 422,
      'slope analysis not server error': (r) => r.status < 500,
      'slope analysis within timeout': (r) => r.timings.duration < 8000,
    });

    if (success) {
      analysisSuccessRate.add(1);
    } else {
      analysisSuccessRate.add(0);
      failedAnalyses.add(1);
    }

    if (resp.status === 429) {
      rateLimitHits.add(1);
    }

    if (resp.status === 200) {
      check(resp, {
        'slope response has analysis data': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.slope !== undefined || body.statistics !== undefined || body.data !== undefined;
          } catch {
            return false;
          }
        },
      });
    }

    sleep(randomFloat(0.5, 1.5));
  });

  // -------------------------------------------------------------------------
  // Group 4: Aspect Analysis
  // -------------------------------------------------------------------------
  group('Aspect Analysis', function () {
    const boundary = generateFieldBoundary();

    const payload = JSON.stringify({
      field_id: `field_${randomInt(1000, 9999)}`,
      tenant_id: TENANT_ID,
      geometry: boundary,
      resolution: randomElement(RESOLUTIONS),
      classification: true,
      output_format: randomElement(OUTPUT_FORMATS),
    });

    const resp = http.post(`${BASE_URL}/api/v1/terrain/aspect`, payload, {
      headers,
      timeout: '30s',
    });

    aspectAnalysisLatency.add(resp.timings.duration);
    totalAnalyses.add(1);

    const success = check(resp, {
      'aspect analysis responds': (r) => r.status === 200 || r.status === 202 || r.status === 400 || r.status === 422,
      'aspect analysis not server error': (r) => r.status < 500,
      'aspect analysis within timeout': (r) => r.timings.duration < 8000,
    });

    if (success) {
      analysisSuccessRate.add(1);
    } else {
      analysisSuccessRate.add(0);
      failedAnalyses.add(1);
    }

    if (resp.status === 429) {
      rateLimitHits.add(1);
    }

    if (resp.status === 200) {
      check(resp, {
        'aspect response has direction data': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.aspect !== undefined || body.statistics !== undefined || body.data !== undefined;
          } catch {
            return false;
          }
        },
      });
    }

    sleep(randomFloat(0.5, 1.5));
  });

  // -------------------------------------------------------------------------
  // Group 5: Elevation Point Queries (20% of iterations)
  // -------------------------------------------------------------------------
  if (secureRandom() < 0.2) {
    group('Elevation Point Query', function () {
      const location = randomElement(YEMEN_LOCATIONS);
      const lat = location.lat + randomFloat(-0.05, 0.05);
      const lon = location.lon + randomFloat(-0.05, 0.05);

      const resp = http.get(
        `${BASE_URL}/api/v1/terrain/dem?lat=${lat}&lon=${lon}`,
        { headers, timeout: '10s' }
      );

      elevationQueryLatency.add(resp.timings.duration);
      totalAnalyses.add(1);

      const success = check(resp, {
        'elevation query responds': (r) => r.status === 200 || r.status === 400 || r.status === 404,
        'elevation query not server error': (r) => r.status < 500,
      });

      if (success) {
        analysisSuccessRate.add(1);
      } else {
        analysisSuccessRate.add(0);
        failedAnalyses.add(1);
      }

      sleep(0.5);
    });
  }

  // -------------------------------------------------------------------------
  // Group 6: Combined Terrain Profile (10% of iterations)
  // -------------------------------------------------------------------------
  if (secureRandom() < 0.1) {
    group('Combined Terrain Profile', function () {
      const boundary = generateFieldBoundary();
      const fieldId = `field_${randomInt(1000, 9999)}`;

      // Request DEM, slope, and aspect in sequence for the same field
      const demPayload = JSON.stringify({
        field_id: fieldId,
        tenant_id: TENANT_ID,
        geometry: boundary,
        resolution: 30,
        output_format: 'json',
        include_statistics: true,
      });

      const demResp = http.post(`${BASE_URL}/api/v1/terrain/dem`, demPayload, {
        headers,
        timeout: '30s',
      });
      demProcessingLatency.add(demResp.timings.duration);

      check(demResp, {
        'combined DEM responds': (r) => r.status < 500,
      });

      sleep(0.3);

      const slopePayload = JSON.stringify({
        field_id: fieldId,
        tenant_id: TENANT_ID,
        geometry: boundary,
        resolution: 30,
        units: 'degrees',
        output_format: 'json',
      });

      const slopeResp = http.post(`${BASE_URL}/api/v1/terrain/slope`, slopePayload, {
        headers,
        timeout: '30s',
      });
      slopeAnalysisLatency.add(slopeResp.timings.duration);

      check(slopeResp, {
        'combined slope responds': (r) => r.status < 500,
      });

      sleep(0.3);

      const aspectPayload = JSON.stringify({
        field_id: fieldId,
        tenant_id: TENANT_ID,
        geometry: boundary,
        resolution: 30,
        output_format: 'json',
      });

      const aspectResp = http.post(`${BASE_URL}/api/v1/terrain/aspect`, aspectPayload, {
        headers,
        timeout: '30s',
      });
      aspectAnalysisLatency.add(aspectResp.timings.duration);

      check(aspectResp, {
        'combined aspect responds': (r) => r.status < 500,
      });

      totalAnalyses.add(3);
      sleep(1.0);
    });
  }

  // Random sleep between iterations
  sleep(randomFloat(1.0, 2.5));
}

// =============================================================================
// Teardown
// =============================================================================

export function teardown(data) {
  const durationSec = ((Date.now() - data.startTime) / 1000).toFixed(2);
  console.log('='.repeat(70));
  console.log('Terrain Core Service Load Test Complete');
  console.log('اختبار الحمل لخدمة التضاريس مكتمل');
  console.log(`Duration: ${durationSec} seconds`);
  console.log('='.repeat(70));
}

// =============================================================================
// Handle Summary - JSON Output
// =============================================================================

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    test_type: 'terrain_service_load_test',
    service: 'terrain-core-service',
    base_url: BASE_URL,
    health: {
      latency_p95: (data.metrics.terrain_health_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.terrain_health_success?.values?.rate || 0) * 100).toFixed(2) + '%',
    },
    analysis: {
      dem_latency_p95: (data.metrics.terrain_dem_processing_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      slope_latency_p95: (data.metrics.terrain_slope_analysis_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      aspect_latency_p95: (data.metrics.terrain_aspect_analysis_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      elevation_latency_p95: (data.metrics.terrain_elevation_query_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.terrain_analysis_success?.values?.rate || 0) * 100).toFixed(2) + '%',
      total: data.metrics.terrain_total_analyses?.values?.count || 0,
      failed: data.metrics.terrain_failed_analyses?.values?.count || 0,
    },
    rate_limits: {
      hits: data.metrics.terrain_rate_limit_hits?.values?.count || 0,
    },
    http: {
      requests: data.metrics.http_reqs?.values?.count || 0,
      failed_rate: ((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2) + '%',
      duration_p95: (data.metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
    },
  };

  const textSummary = `
${'='.repeat(70)}
           Terrain Core Service Load Test Results
           نتائج اختبار الحمل لخدمة التضاريس
${'='.repeat(70)}

HEALTH CHECKS:
${'─'.repeat(70)}
  Latency (p95):         ${summary.health.latency_p95}
  Success Rate:          ${summary.health.success_rate}

TERRAIN ANALYSIS PERFORMANCE:
${'─'.repeat(70)}
  DEM Processing (p95):  ${summary.analysis.dem_latency_p95}
  Slope Analysis (p95):  ${summary.analysis.slope_latency_p95}
  Aspect Analysis (p95): ${summary.analysis.aspect_latency_p95}
  Elevation Query (p95): ${summary.analysis.elevation_latency_p95}
  Success Rate:          ${summary.analysis.success_rate}
  Total Analyses:        ${summary.analysis.total}
  Failed Analyses:       ${summary.analysis.failed}

RATE LIMITING:
${'─'.repeat(70)}
  Rate Limit Hits:       ${summary.rate_limits.hits}

HTTP OVERVIEW:
${'─'.repeat(70)}
  Total Requests:        ${summary.http.requests}
  Failed Rate:           ${summary.http.failed_rate}
  Duration (p95):        ${summary.http.duration_p95}

${'='.repeat(70)}
`;

  return {
    stdout: textSummary,
    './results/k6_terrain_service_results.json': JSON.stringify(summary, null, 2),
  };
}
