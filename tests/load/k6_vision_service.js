/**
 * SAHOOL Platform - YOLO26 Vision Service Load Test
 * اختبار الحمل لخدمة الرؤية الحاسوبية YOLO26
 *
 * Service: yolo26-vision-service (port 8150)
 * Purpose: Load test computer vision endpoints for pest, disease, and weed detection
 *
 * Run with:
 *   k6 run tests/load/k6_vision_service.js
 *   k6 run --env BASE_URL=http://vision-service:8150 tests/load/k6_vision_service.js
 *
 * Environment variables:
 *   - BASE_URL: Vision service URL (default: http://localhost:8150)
 *   - AUTH_TOKEN: JWT token for authenticated requests
 *   - TENANT_ID: Tenant ID for multi-tenant testing (default: tenant_loadtest)
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// =============================================================================
// Configuration
// =============================================================================

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8150';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';
const TENANT_ID = __ENV.TENANT_ID || 'tenant_loadtest';

// =============================================================================
// Custom Metrics
// =============================================================================

// Latency trends
const healthLatency = new Trend('vision_health_latency', true);
const pestDetectionLatency = new Trend('vision_pest_detection_latency', true);
const diseaseDetectionLatency = new Trend('vision_disease_detection_latency', true);
const weedDetectionLatency = new Trend('vision_weed_detection_latency', true);
const batchDetectionLatency = new Trend('vision_batch_detection_latency', true);
const modelInfoLatency = new Trend('vision_model_info_latency', true);

// Success rates
const detectionSuccessRate = new Rate('vision_detection_success');
const healthSuccessRate = new Rate('vision_health_success');

// Counters
const totalDetections = new Counter('vision_total_detections');
const failedDetections = new Counter('vision_failed_detections');
const rateLimitHits = new Counter('vision_rate_limit_hits');

// =============================================================================
// Test Options
// =============================================================================

export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 VUs
    { duration: '2m', target: 50 },   // Ramp up to 50 VUs
    { duration: '3m', target: 100 },  // Ramp up to 100 VUs
    { duration: '3m', target: 100 },  // Hold at 100 VUs
    { duration: '1m', target: 50 },   // Ramp down to 50 VUs
    { duration: '1m', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    // Health endpoint thresholds
    vision_health_latency: ['p(95)<200'],
    vision_health_success: ['rate>0.99'],

    // Detection endpoint thresholds
    vision_pest_detection_latency: ['p(95)<5000', 'p(99)<8000'],
    vision_disease_detection_latency: ['p(95)<5000', 'p(99)<8000'],
    vision_weed_detection_latency: ['p(95)<5000', 'p(99)<8000'],

    // Batch detection thresholds (more lenient)
    vision_batch_detection_latency: ['p(95)<10000'],

    // Overall success rate
    vision_detection_success: ['rate>0.95'],

    // General HTTP thresholds
    http_req_failed: ['rate<0.05'],
    checks: ['rate>0.95'],
  },
  tags: {
    test_type: 'load',
    service: 'yolo26-vision-service',
    environment: __ENV.ENVIRONMENT || 'local',
  },
};

// =============================================================================
// Helper Functions
// =============================================================================

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
    'X-Tenant-ID': TENANT_ID,
  };
  if (AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  return headers;
}

function getMultipartHeaders() {
  const headers = {
    'X-Tenant-ID': TENANT_ID,
  };
  if (AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  return headers;
}

/**
 * Generate a minimal synthetic test image as binary data.
 * Creates a small valid JPEG-like payload for upload testing.
 */
function generateTestImagePayload() {
  // Create a minimal binary payload that simulates an image file.
  // In a real scenario, use open() to load actual test images from disk.
  const size = Math.floor(secureRandom() * 50000) + 10000; // 10-60KB
  const data = new ArrayBuffer(size);
  const view = new Uint8Array(data);
  // JPEG magic bytes
  view[0] = 0xFF;
  view[1] = 0xD8;
  view[2] = 0xFF;
  view[3] = 0xE0;
  // Fill with random-ish data
  for (let i = 4; i < size - 2; i++) {
    view[i] = (i * 37 + 13) % 256;
  }
  // JPEG end marker
  view[size - 2] = 0xFF;
  view[size - 1] = 0xD9;
  return data;
}

function randomElement(array) {
  return array[Math.floor(secureRandom() * array.length)];
}

function randomFloat(min, max) {
  return parseFloat((secureRandom() * (max - min) + min).toFixed(2));
}

// =============================================================================
// Test Data
// =============================================================================

const CONFIDENCE_THRESHOLDS = [0.2, 0.25, 0.3, 0.4, 0.5];
const IMAGE_SIZES = [320, 416, 512, 640, 832];
const MODEL_VARIANTS = ['n', 's', 'm', 'l', 'x'];

// =============================================================================
// Setup
// =============================================================================

export function setup() {
  console.log('='.repeat(70));
  console.log('SAHOOL - YOLO26 Vision Service Load Test');
  console.log('اختبار الحمل لخدمة الرؤية الحاسوبية');
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
  // Group 2: Pest Detection
  // -------------------------------------------------------------------------
  group('Pest Detection', function () {
    const imageData = generateTestImagePayload();
    const confidence = randomElement(CONFIDENCE_THRESHOLDS);
    const imgSize = randomElement(IMAGE_SIZES);

    const formData = {
      file: http.file(imageData, 'test_crop.jpg', 'image/jpeg'),
      confidence_threshold: String(confidence),
      image_size: String(imgSize),
    };

    const resp = http.post(`${BASE_URL}/api/v1/detect/pest`, formData, {
      headers: getMultipartHeaders(),
      timeout: '30s',
    });

    pestDetectionLatency.add(resp.timings.duration);
    totalDetections.add(1);

    const success = check(resp, {
      'pest detection responds': (r) => r.status === 200 || r.status === 400 || r.status === 422,
      'pest detection not server error': (r) => r.status < 500,
      'pest detection within timeout': (r) => r.timings.duration < 10000,
    });

    if (success) {
      detectionSuccessRate.add(1);
    } else {
      detectionSuccessRate.add(0);
      failedDetections.add(1);
    }

    if (resp.status === 429) {
      rateLimitHits.add(1);
    }

    if (resp.status === 200) {
      check(resp, {
        'pest response has detections': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.detections !== undefined || body.results !== undefined;
          } catch {
            return false;
          }
        },
      });
    }

    sleep(randomFloat(0.5, 1.5));
  });

  // -------------------------------------------------------------------------
  // Group 3: Disease Detection
  // -------------------------------------------------------------------------
  group('Disease Detection', function () {
    const imageData = generateTestImagePayload();
    const confidence = randomElement(CONFIDENCE_THRESHOLDS);
    const imgSize = randomElement(IMAGE_SIZES);

    const formData = {
      file: http.file(imageData, 'test_leaf.jpg', 'image/jpeg'),
      confidence_threshold: String(confidence),
      image_size: String(imgSize),
    };

    const resp = http.post(`${BASE_URL}/api/v1/detect/disease`, formData, {
      headers: getMultipartHeaders(),
      timeout: '30s',
    });

    diseaseDetectionLatency.add(resp.timings.duration);
    totalDetections.add(1);

    const success = check(resp, {
      'disease detection responds': (r) => r.status === 200 || r.status === 400 || r.status === 422,
      'disease detection not server error': (r) => r.status < 500,
      'disease detection within timeout': (r) => r.timings.duration < 10000,
    });

    if (success) {
      detectionSuccessRate.add(1);
    } else {
      detectionSuccessRate.add(0);
      failedDetections.add(1);
    }

    if (resp.status === 429) {
      rateLimitHits.add(1);
    }

    if (resp.status === 200) {
      check(resp, {
        'disease response has detections': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.detections !== undefined || body.results !== undefined;
          } catch {
            return false;
          }
        },
      });
    }

    sleep(randomFloat(0.5, 1.5));
  });

  // -------------------------------------------------------------------------
  // Group 4: Weed Detection
  // -------------------------------------------------------------------------
  group('Weed Detection', function () {
    const imageData = generateTestImagePayload();
    const confidence = randomElement(CONFIDENCE_THRESHOLDS);

    const formData = {
      file: http.file(imageData, 'test_field.jpg', 'image/jpeg'),
      confidence_threshold: String(confidence),
    };

    const resp = http.post(`${BASE_URL}/api/v1/detect/weed`, formData, {
      headers: getMultipartHeaders(),
      timeout: '30s',
    });

    weedDetectionLatency.add(resp.timings.duration);
    totalDetections.add(1);

    const success = check(resp, {
      'weed detection responds': (r) => r.status === 200 || r.status === 400 || r.status === 422,
      'weed detection not server error': (r) => r.status < 500,
      'weed detection within timeout': (r) => r.timings.duration < 10000,
    });

    if (success) {
      detectionSuccessRate.add(1);
    } else {
      detectionSuccessRate.add(0);
      failedDetections.add(1);
    }

    if (resp.status === 429) {
      rateLimitHits.add(1);
    }

    sleep(randomFloat(0.5, 1.5));
  });

  // -------------------------------------------------------------------------
  // Group 5: Model Management (10% of iterations)
  // -------------------------------------------------------------------------
  if (secureRandom() < 0.1) {
    group('Model Management', function () {
      // List model versions
      const versionsResp = http.get(`${BASE_URL}/api/v1/models/versions`, { headers });
      modelInfoLatency.add(versionsResp.timings.duration);

      check(versionsResp, {
        'model versions responds': (r) => r.status === 200 || r.status === 404,
      });

      sleep(0.3);

      // Get specific model info
      const variant = randomElement(MODEL_VARIANTS);
      const infoResp = http.get(`${BASE_URL}/api/v1/models/${variant}/info`, { headers });
      modelInfoLatency.add(infoResp.timings.duration);

      check(infoResp, {
        'model info responds': (r) => r.status === 200 || r.status === 404,
      });

      sleep(0.3);

      // Check loaded models
      const loadedResp = http.get(`${BASE_URL}/api/v1/models/loaded`, { headers });
      modelInfoLatency.add(loadedResp.timings.duration);

      check(loadedResp, {
        'loaded models responds': (r) => r.status === 200,
      });

      sleep(0.3);
    });
  }

  // -------------------------------------------------------------------------
  // Group 6: Batch Detection (5% of iterations)
  // -------------------------------------------------------------------------
  if (secureRandom() < 0.05) {
    group('Batch Detection', function () {
      // Submit a small batch of images for pest detection
      const images = [];
      for (let i = 0; i < 3; i++) {
        images.push(http.file(generateTestImagePayload(), `batch_${i}.jpg`, 'image/jpeg'));
      }

      const formData = {
        'files': images,
        confidence_threshold: '0.3',
      };

      const batchResp = http.post(`${BASE_URL}/api/v1/batch/detect/pest`, formData, {
        headers: getMultipartHeaders(),
        timeout: '60s',
      });

      batchDetectionLatency.add(batchResp.timings.duration);

      check(batchResp, {
        'batch detection responds': (r) => r.status === 200 || r.status === 202 || r.status === 400 || r.status === 422,
        'batch detection not server error': (r) => r.status < 500,
      });

      // Check batch status
      const statusResp = http.get(`${BASE_URL}/api/v1/batch/status`, { headers });
      check(statusResp, {
        'batch status responds': (r) => r.status === 200 || r.status === 404,
      });

      sleep(1.0);
    });
  }

  // Random sleep between iterations to simulate realistic user behavior
  sleep(randomFloat(1.0, 3.0));
}

// =============================================================================
// Teardown
// =============================================================================

export function teardown(data) {
  const durationSec = ((Date.now() - data.startTime) / 1000).toFixed(2);
  console.log('='.repeat(70));
  console.log('YOLO26 Vision Service Load Test Complete');
  console.log('اختبار الحمل لخدمة الرؤية مكتمل');
  console.log(`Duration: ${durationSec} seconds`);
  console.log('='.repeat(70));
}

// =============================================================================
// Handle Summary - JSON Output
// =============================================================================

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    test_type: 'vision_service_load_test',
    service: 'yolo26-vision-service',
    base_url: BASE_URL,
    health: {
      latency_p95: (data.metrics.vision_health_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.vision_health_success?.values?.rate || 0) * 100).toFixed(2) + '%',
    },
    detection: {
      pest_latency_p95: (data.metrics.vision_pest_detection_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      disease_latency_p95: (data.metrics.vision_disease_detection_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      weed_latency_p95: (data.metrics.vision_weed_detection_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.vision_detection_success?.values?.rate || 0) * 100).toFixed(2) + '%',
      total: data.metrics.vision_total_detections?.values?.count || 0,
      failed: data.metrics.vision_failed_detections?.values?.count || 0,
    },
    batch: {
      latency_p95: (data.metrics.vision_batch_detection_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
    },
    rate_limits: {
      hits: data.metrics.vision_rate_limit_hits?.values?.count || 0,
    },
    http: {
      requests: data.metrics.http_reqs?.values?.count || 0,
      failed_rate: ((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2) + '%',
      duration_p95: (data.metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
    },
  };

  const textSummary = `
${'='.repeat(70)}
           YOLO26 Vision Service Load Test Results
           نتائج اختبار الحمل لخدمة الرؤية الحاسوبية
${'='.repeat(70)}

HEALTH CHECKS:
${'─'.repeat(70)}
  Latency (p95):      ${summary.health.latency_p95}
  Success Rate:       ${summary.health.success_rate}

DETECTION PERFORMANCE:
${'─'.repeat(70)}
  Pest (p95):         ${summary.detection.pest_latency_p95}
  Disease (p95):      ${summary.detection.disease_latency_p95}
  Weed (p95):         ${summary.detection.weed_latency_p95}
  Success Rate:       ${summary.detection.success_rate}
  Total Detections:   ${summary.detection.total}
  Failed Detections:  ${summary.detection.failed}

BATCH DETECTION:
${'─'.repeat(70)}
  Latency (p95):      ${summary.batch.latency_p95}

RATE LIMITING:
${'─'.repeat(70)}
  Rate Limit Hits:    ${summary.rate_limits.hits}

HTTP OVERVIEW:
${'─'.repeat(70)}
  Total Requests:     ${summary.http.requests}
  Failed Rate:        ${summary.http.failed_rate}
  Duration (p95):     ${summary.http.duration_p95}

${'='.repeat(70)}
`;

  return {
    stdout: textSummary,
    './results/k6_vision_service_results.json': JSON.stringify(summary, null, 2),
  };
}
