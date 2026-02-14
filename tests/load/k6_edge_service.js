/**
 * SAHOOL Platform - Edge Orchestrator Service Load Test
 * اختبار الحمل لخدمة تنسيق الحافة
 *
 * Service: edge-orchestrator-service (port 8180)
 * Purpose: Load test edge device management, model deployment, and data sync endpoints
 *
 * Run with:
 *   k6 run tests/load/k6_edge_service.js
 *   k6 run --env BASE_URL=http://edge-service:8180 tests/load/k6_edge_service.js
 *
 * Environment variables:
 *   - BASE_URL: Edge orchestrator service URL (default: http://localhost:8180)
 *   - AUTH_TOKEN: JWT token for authenticated requests
 *   - TENANT_ID: Tenant ID for multi-tenant testing (default: tenant_loadtest)
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// =============================================================================
// Configuration
// =============================================================================

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8180';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';
const TENANT_ID = __ENV.TENANT_ID || 'tenant_loadtest';

// =============================================================================
// Custom Metrics
// =============================================================================

// Latency trends
const healthLatency = new Trend('edge_health_latency', true);
const devicesListLatency = new Trend('edge_devices_list_latency', true);
const deviceRegistrationLatency = new Trend('edge_device_registration_latency', true);
const modelDeployLatency = new Trend('edge_model_deploy_latency', true);
const dataSyncLatency = new Trend('edge_data_sync_latency', true);
const deviceStatusLatency = new Trend('edge_device_status_latency', true);

// Success rates
const operationSuccessRate = new Rate('edge_operation_success');
const healthSuccessRate = new Rate('edge_health_success');

// Counters
const totalOperations = new Counter('edge_total_operations');
const failedOperations = new Counter('edge_failed_operations');
const rateLimitHits = new Counter('edge_rate_limit_hits');
const deployments = new Counter('edge_deployments_initiated');
const syncsInitiated = new Counter('edge_syncs_initiated');

// =============================================================================
// Test Options
// =============================================================================

export const options = {
  stages: [
    { duration: '1m', target: 5 },    // Ramp up to 5 VUs
    { duration: '2m', target: 20 },   // Ramp up to 20 VUs
    { duration: '3m', target: 40 },   // Ramp up to 40 VUs
    { duration: '3m', target: 40 },   // Hold at 40 VUs
    { duration: '1m', target: 10 },   // Ramp down to 10 VUs
    { duration: '1m', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    // Health endpoint thresholds
    edge_health_latency: ['p(95)<200', 'p(99)<500'],
    edge_health_success: ['rate>0.99'],

    // Operation endpoint thresholds
    edge_devices_list_latency: ['p(95)<2000', 'p(99)<3000'],
    edge_device_registration_latency: ['p(95)<2000', 'p(99)<3000'],
    edge_model_deploy_latency: ['p(95)<2000', 'p(99)<4000'],
    edge_data_sync_latency: ['p(95)<2000', 'p(99)<4000'],
    edge_device_status_latency: ['p(95)<1000', 'p(99)<2000'],

    // Overall success rate
    edge_operation_success: ['rate>0.95'],

    // General HTTP thresholds
    http_req_failed: ['rate<0.05'],
    checks: ['rate>0.95'],
  },
  tags: {
    test_type: 'load',
    service: 'edge-orchestrator-service',
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
  return parseFloat((Math.random() * (max - min) + min).toFixed(2));
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

function generateDeviceId() {
  return `jetson-orin-${randomString(8)}`;
}

function generateMacAddress() {
  const hex = '0123456789abcdef';
  let mac = '';
  for (let i = 0; i < 6; i++) {
    if (i > 0) mac += ':';
    mac += hex.charAt(randomInt(0, 15)) + hex.charAt(randomInt(0, 15));
  }
  return mac;
}

// =============================================================================
// Test Data
// =============================================================================

const DEVICE_TYPES = ['jetson_orin_nano', 'jetson_orin_nx', 'jetson_agx_orin', 'raspberry_pi_4', 'coral_dev_board'];
const DEVICE_STATUSES = ['online', 'offline', 'maintenance', 'provisioning'];
const MODEL_NAMES = ['yolo26-pest-nano', 'yolo26-disease-small', 'yolo26-weed-nano', 'crop-counter-lite', 'ripeness-classifier'];
const MODEL_VERSIONS = ['1.0.0', '1.1.0', '1.2.0', '2.0.0'];
const SYNC_TYPES = ['full', 'incremental', 'delta', 'metadata_only'];
const FIRMWARE_VERSIONS = ['5.1.1', '5.1.2', '5.2.0', '6.0.0-rc1'];

const YEMEN_LOCATIONS = [
  { name: 'Sanaa',    lat: 15.3694, lon: 44.1910 },
  { name: 'Aden',     lat: 12.7855, lon: 45.0187 },
  { name: 'Taiz',     lat: 13.5795, lon: 44.0202 },
  { name: 'Ibb',      lat: 13.9667, lon: 44.1667 },
];

// =============================================================================
// Setup
// =============================================================================

export function setup() {
  console.log('='.repeat(70));
  console.log('SAHOOL - Edge Orchestrator Service Load Test');
  console.log('اختبار الحمل لخدمة تنسيق الحافة');
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
  // Group 2: Device Registration and Listing
  // -------------------------------------------------------------------------
  group('Device Management', function () {
    // List devices
    const listResp = http.get(
      `${BASE_URL}/api/v1/edge/devices?tenant_id=${TENANT_ID}&limit=20`,
      { headers, timeout: '15s' }
    );

    devicesListLatency.add(listResp.timings.duration);
    totalOperations.add(1);

    const listOk = check(listResp, {
      'devices list responds': (r) => r.status === 200 || r.status === 404,
      'devices list not server error': (r) => r.status < 500,
    });

    if (listOk) {
      operationSuccessRate.add(1);
    } else {
      operationSuccessRate.add(0);
      failedOperations.add(1);
    }

    if (listResp.status === 429) {
      rateLimitHits.add(1);
    }

    sleep(0.5);

    // Register a new device (30% of iterations)
    if (Math.random() < 0.3) {
      const location = randomElement(YEMEN_LOCATIONS);
      const devicePayload = JSON.stringify({
        device_id: generateDeviceId(),
        tenant_id: TENANT_ID,
        device_type: randomElement(DEVICE_TYPES),
        name: `Edge Device ${randomString(4)}`,
        mac_address: generateMacAddress(),
        firmware_version: randomElement(FIRMWARE_VERSIONS),
        location: {
          latitude: location.lat + randomFloat(-0.05, 0.05),
          longitude: location.lon + randomFloat(-0.05, 0.05),
          name: location.name,
        },
        capabilities: {
          gpu: randomElement([true, false]),
          camera: true,
          sensors: randomElement([['temperature', 'humidity'], ['temperature', 'humidity', 'soil_moisture']]),
          storage_gb: randomElement([32, 64, 128, 256]),
          ram_gb: randomElement([4, 8, 16, 32]),
        },
        metadata: {
          test: true,
          loadtest_id: `loadtest_${Date.now()}`,
        },
      });

      const regResp = http.post(`${BASE_URL}/api/v1/edge/devices`, devicePayload, {
        headers,
        timeout: '15s',
      });

      deviceRegistrationLatency.add(regResp.timings.duration);
      totalOperations.add(1);

      const regOk = check(regResp, {
        'device registration responds': (r) => r.status === 201 || r.status === 200 || r.status === 400 || r.status === 409 || r.status === 422,
        'device registration not server error': (r) => r.status < 500,
      });

      if (regOk) {
        operationSuccessRate.add(1);
      } else {
        operationSuccessRate.add(0);
        failedOperations.add(1);
      }

      sleep(0.5);
    }

    // Get specific device status (40% of iterations)
    if (Math.random() < 0.4) {
      const deviceId = generateDeviceId();
      const statusResp = http.get(
        `${BASE_URL}/api/v1/edge/devices/${deviceId}`,
        { headers, timeout: '10s' }
      );

      deviceStatusLatency.add(statusResp.timings.duration);
      totalOperations.add(1);

      check(statusResp, {
        'device status responds': (r) => r.status === 200 || r.status === 404,
        'device status not server error': (r) => r.status < 500,
      });

      operationSuccessRate.add(statusResp.status < 500 ? 1 : 0);

      sleep(0.3);
    }

    sleep(0.5);
  });

  // -------------------------------------------------------------------------
  // Group 3: Model Deployment
  // -------------------------------------------------------------------------
  group('Model Deployment', function () {
    const deviceId = generateDeviceId();
    const modelName = randomElement(MODEL_NAMES);
    const modelVersion = randomElement(MODEL_VERSIONS);

    const deployPayload = JSON.stringify({
      device_id: deviceId,
      tenant_id: TENANT_ID,
      model_name: modelName,
      model_version: modelVersion,
      priority: randomElement(['low', 'normal', 'high']),
      deployment_config: {
        batch_size: randomElement([1, 2, 4]),
        precision: randomElement(['fp32', 'fp16', 'int8']),
        max_concurrent: randomElement([1, 2, 4]),
        enable_tensorrt: randomElement([true, false]),
      },
      rollback_on_failure: true,
      metadata: {
        test: true,
        initiated_by: 'k6_load_test',
      },
    });

    const deployResp = http.post(`${BASE_URL}/api/v1/edge/deploy`, deployPayload, {
      headers,
      timeout: '20s',
    });

    modelDeployLatency.add(deployResp.timings.duration);
    totalOperations.add(1);
    deployments.add(1);

    const deployOk = check(deployResp, {
      'model deploy responds': (r) => r.status === 200 || r.status === 202 || r.status === 400 || r.status === 404 || r.status === 422,
      'model deploy not server error': (r) => r.status < 500,
      'model deploy within timeout': (r) => r.timings.duration < 5000,
    });

    if (deployOk) {
      operationSuccessRate.add(1);
    } else {
      operationSuccessRate.add(0);
      failedOperations.add(1);
    }

    if (deployResp.status === 429) {
      rateLimitHits.add(1);
    }

    if (deployResp.status === 200 || deployResp.status === 202) {
      check(deployResp, {
        'deploy response has deployment_id': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.deployment_id !== undefined || body.id !== undefined || body.status !== undefined;
          } catch {
            return false;
          }
        },
      });
    }

    sleep(randomFloat(0.5, 1.5));
  });

  // -------------------------------------------------------------------------
  // Group 4: Data Synchronization
  // -------------------------------------------------------------------------
  group('Data Synchronization', function () {
    const deviceId = generateDeviceId();
    const syncType = randomElement(SYNC_TYPES);

    const syncPayload = JSON.stringify({
      device_id: deviceId,
      tenant_id: TENANT_ID,
      sync_type: syncType,
      direction: randomElement(['upload', 'download', 'bidirectional']),
      data_types: randomElement([
        ['detections', 'telemetry'],
        ['detections', 'telemetry', 'images'],
        ['models', 'config'],
        ['telemetry'],
      ]),
      since: new Date(Date.now() - randomInt(3600, 86400) * 1000).toISOString(),
      max_records: randomElement([100, 500, 1000, 5000]),
      compression: randomElement([true, false]),
      metadata: {
        test: true,
        network_type: randomElement(['wifi', '4g', '3g', 'satellite']),
        bandwidth_kbps: randomInt(100, 10000),
      },
    });

    const syncResp = http.post(`${BASE_URL}/api/v1/edge/sync`, syncPayload, {
      headers,
      timeout: '20s',
    });

    dataSyncLatency.add(syncResp.timings.duration);
    totalOperations.add(1);
    syncsInitiated.add(1);

    const syncOk = check(syncResp, {
      'data sync responds': (r) => r.status === 200 || r.status === 202 || r.status === 400 || r.status === 404 || r.status === 422,
      'data sync not server error': (r) => r.status < 500,
      'data sync within timeout': (r) => r.timings.duration < 5000,
    });

    if (syncOk) {
      operationSuccessRate.add(1);
    } else {
      operationSuccessRate.add(0);
      failedOperations.add(1);
    }

    if (syncResp.status === 429) {
      rateLimitHits.add(1);
    }

    if (syncResp.status === 200 || syncResp.status === 202) {
      check(syncResp, {
        'sync response has status': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.sync_id !== undefined || body.status !== undefined;
          } catch {
            return false;
          }
        },
      });
    }

    sleep(randomFloat(0.5, 1.5));
  });

  // -------------------------------------------------------------------------
  // Group 5: Heartbeat Simulation (15% of iterations)
  // -------------------------------------------------------------------------
  if (Math.random() < 0.15) {
    group('Device Heartbeat', function () {
      // Simulate multiple devices sending heartbeats
      const deviceCount = randomInt(2, 5);

      for (let i = 0; i < deviceCount; i++) {
        const deviceId = generateDeviceId();
        const heartbeatPayload = JSON.stringify({
          device_id: deviceId,
          tenant_id: TENANT_ID,
          timestamp: new Date().toISOString(),
          status: randomElement(DEVICE_STATUSES),
          metrics: {
            cpu_usage: randomFloat(10, 95),
            memory_usage: randomFloat(20, 90),
            gpu_usage: randomFloat(0, 100),
            temperature_celsius: randomFloat(35, 80),
            disk_usage: randomFloat(10, 85),
            uptime_hours: randomFloat(1, 720),
          },
          active_models: randomElement([
            ['yolo26-pest-nano'],
            ['yolo26-pest-nano', 'yolo26-disease-small'],
            [],
          ]),
        });

        const heartbeatResp = http.post(
          `${BASE_URL}/api/v1/edge/devices/${deviceId}/heartbeat`,
          heartbeatPayload,
          { headers, timeout: '10s' }
        );

        totalOperations.add(1);

        check(heartbeatResp, {
          'heartbeat responds': (r) => r.status < 500,
        });

        operationSuccessRate.add(heartbeatResp.status < 500 ? 1 : 0);

        sleep(0.2);
      }
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
  console.log('Edge Orchestrator Service Load Test Complete');
  console.log('اختبار الحمل لخدمة تنسيق الحافة مكتمل');
  console.log(`Duration: ${durationSec} seconds`);
  console.log('='.repeat(70));
}

// =============================================================================
// Handle Summary - JSON Output
// =============================================================================

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    test_type: 'edge_service_load_test',
    service: 'edge-orchestrator-service',
    base_url: BASE_URL,
    health: {
      latency_p95: (data.metrics.edge_health_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.edge_health_success?.values?.rate || 0) * 100).toFixed(2) + '%',
    },
    operations: {
      devices_list_p95: (data.metrics.edge_devices_list_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      device_registration_p95: (data.metrics.edge_device_registration_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      model_deploy_p95: (data.metrics.edge_model_deploy_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      data_sync_p95: (data.metrics.edge_data_sync_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      device_status_p95: (data.metrics.edge_device_status_latency?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
      success_rate: ((data.metrics.edge_operation_success?.values?.rate || 0) * 100).toFixed(2) + '%',
      total: data.metrics.edge_total_operations?.values?.count || 0,
      failed: data.metrics.edge_failed_operations?.values?.count || 0,
    },
    deployments: {
      initiated: data.metrics.edge_deployments_initiated?.values?.count || 0,
    },
    syncs: {
      initiated: data.metrics.edge_syncs_initiated?.values?.count || 0,
    },
    rate_limits: {
      hits: data.metrics.edge_rate_limit_hits?.values?.count || 0,
    },
    http: {
      requests: data.metrics.http_reqs?.values?.count || 0,
      failed_rate: ((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2) + '%',
      duration_p95: (data.metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(2) + 'ms',
    },
  };

  const textSummary = `
${'='.repeat(70)}
           Edge Orchestrator Service Load Test Results
           نتائج اختبار الحمل لخدمة تنسيق الحافة
${'='.repeat(70)}

HEALTH CHECKS:
${'─'.repeat(70)}
  Latency (p95):             ${summary.health.latency_p95}
  Success Rate:              ${summary.health.success_rate}

EDGE OPERATIONS PERFORMANCE:
${'─'.repeat(70)}
  Device List (p95):         ${summary.operations.devices_list_p95}
  Device Registration (p95): ${summary.operations.device_registration_p95}
  Model Deploy (p95):        ${summary.operations.model_deploy_p95}
  Data Sync (p95):           ${summary.operations.data_sync_p95}
  Device Status (p95):       ${summary.operations.device_status_p95}
  Success Rate:              ${summary.operations.success_rate}
  Total Operations:          ${summary.operations.total}
  Failed Operations:         ${summary.operations.failed}

ACTIVITY:
${'─'.repeat(70)}
  Deployments Initiated:     ${summary.deployments.initiated}
  Syncs Initiated:           ${summary.syncs.initiated}
  Rate Limit Hits:           ${summary.rate_limits.hits}

HTTP OVERVIEW:
${'─'.repeat(70)}
  Total Requests:            ${summary.http.requests}
  Failed Rate:               ${summary.http.failed_rate}
  Duration (p95):            ${summary.http.duration_p95}

${'='.repeat(70)}
`;

  return {
    stdout: textSummary,
    './results/k6_edge_service_results.json': JSON.stringify(summary, null, 2),
  };
}
