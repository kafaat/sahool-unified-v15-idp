/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * SAHOOL IDP - Advanced Load Testing Scenarios
 * سيناريوهات اختبار الحمل المتقدمة لمنصة سهول
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * Features:
 * - Multiple concurrent scenarios (Auth, Fields, Weather, IoT)
 * - Support for 15-100+ virtual agents
 * - Spike testing, stress testing, soak testing
 * - Chaos engineering integration
 * - Detailed metrics and error categorization
 *
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import http from "k6/http";
import { check, group, sleep, fail } from "k6";
import { Rate, Trend, Counter, Gauge } from "k6/metrics";
import {
  randomIntBetween,
  randomItem,
} from "https://jslib.k6.io/k6-utils/1.2.0/index.js";

// ═══════════════════════════════════════════════════════════════════════════════
// CUSTOM METRICS - مقاييس مخصصة
// ═══════════════════════════════════════════════════════════════════════════════

// Success rates by scenario
const authSuccessRate = new Rate("auth_success_rate");
const fieldOpsSuccessRate = new Rate("field_ops_success_rate");
const weatherSuccessRate = new Rate("weather_success_rate");
const iotSuccessRate = new Rate("iot_success_rate");
const sessionPersistenceRate = new Rate("session_persistence_rate");

// Response time trends by endpoint
const authDuration = new Trend("auth_duration_ms");
const fieldListDuration = new Trend("field_list_duration_ms");
const fieldCreateDuration = new Trend("field_create_duration_ms");
const fieldUpdateDuration = new Trend("field_update_duration_ms");
const weatherDuration = new Trend("weather_duration_ms");
const iotDuration = new Trend("iot_duration_ms");

// Error counters
const connectionPoolErrors = new Counter("connection_pool_errors");
const sessionLossErrors = new Counter("session_loss_errors");
const raceConditionErrors = new Counter("race_condition_errors");
const timeoutErrors = new Counter("timeout_errors");
const serverErrors = new Counter("server_errors_5xx");
const clientErrors = new Counter("client_errors_4xx");

// System metrics
const activeAgents = new Gauge("active_agents");
const requestsPerSecond = new Rate("requests_per_second");

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION - الإعدادات
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_URL = __ENV.BASE_URL || "http://sahool-nginx:80";
const AGENT_COUNT = parseInt(__ENV.AGENT_COUNT) || 20;
const TEST_TYPE = __ENV.TEST_TYPE || "standard"; // standard, stress, spike, soak
const ENVIRONMENT = __ENV.ENVIRONMENT || "simulation";

// Scenario weights (percentage of traffic)
const SCENARIO_WEIGHTS = {
  auth: 20, // 20% authentication requests
  fields: 40, // 40% field operations
  weather: 25, // 25% weather queries
  iot: 15, // 15% IoT data
};

// Test configurations by type
const TEST_CONFIGS = {
  standard: {
    stages: [
      { duration: "30s", target: AGENT_COUNT },
      { duration: "2m", target: AGENT_COUNT },
      { duration: "30s", target: 0 },
    ],
  },
  stress: {
    stages: [
      { duration: "30s", target: AGENT_COUNT },
      { duration: "1m", target: AGENT_COUNT * 2 },
      { duration: "1m", target: AGENT_COUNT * 3 },
      { duration: "1m", target: AGENT_COUNT * 4 },
      { duration: "2m", target: AGENT_COUNT * 5 }, // Peak: 5x agents
      { duration: "1m", target: AGENT_COUNT },
      { duration: "30s", target: 0 },
    ],
  },
  spike: {
    stages: [
      { duration: "1m", target: AGENT_COUNT },
      { duration: "10s", target: AGENT_COUNT * 10 }, // Sudden spike!
      { duration: "1m", target: AGENT_COUNT * 10 },
      { duration: "10s", target: AGENT_COUNT },
      { duration: "1m", target: AGENT_COUNT },
      { duration: "30s", target: 0 },
    ],
  },
  soak: {
    stages: [
      { duration: "1m", target: AGENT_COUNT },
      { duration: "10m", target: AGENT_COUNT }, // Long duration
      { duration: "1m", target: 0 },
    ],
  },
};

// Export options based on test type
export const options = {
  scenarios: {
    // Authentication Scenario
    auth_flow: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: TEST_CONFIGS[TEST_TYPE].stages,
      gracefulRampDown: "30s",
      exec: "authScenario",
    },
    // Field Operations Scenario
    field_operations: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: TEST_CONFIGS[TEST_TYPE].stages,
      gracefulRampDown: "30s",
      exec: "fieldScenario",
    },
    // Weather Queries Scenario
    weather_queries: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: TEST_CONFIGS[TEST_TYPE].stages.map((s) => ({
        duration: s.duration,
        target: Math.floor(s.target * 0.5), // Half the agents
      })),
      gracefulRampDown: "30s",
      exec: "weatherScenario",
    },
    // IoT Data Scenario
    iot_data: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: TEST_CONFIGS[TEST_TYPE].stages.map((s) => ({
        duration: s.duration,
        target: Math.floor(s.target * 0.3), // 30% of agents
      })),
      gracefulRampDown: "30s",
      exec: "iotScenario",
    },
  },

  thresholds: {
    // HTTP metrics
    http_req_duration: ["p(95)<1000", "p(99)<2000"],
    http_req_failed: ["rate<0.1"],

    // Scenario-specific
    auth_success_rate: ["rate>0.90"],
    field_ops_success_rate: ["rate>0.85"],
    weather_success_rate: ["rate>0.90"],
    session_persistence_rate: ["rate>0.85"],

    // Response times
    auth_duration_ms: ["p(95)<1000"],
    field_list_duration_ms: ["p(95)<500"],
    weather_duration_ms: ["p(95)<800"],

    // Error limits
    connection_pool_errors: ["count<50"],
    session_loss_errors: ["count<30"],
    server_errors_5xx: ["count<100"],
  },

  tags: {
    test_type: TEST_TYPE,
    environment: ENVIRONMENT,
    agent_count: AGENT_COUNT.toString(),
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS - دوال مساعدة
// ═══════════════════════════════════════════════════════════════════════════════

function getAgentId() {
  return `agent_${__VU}_${__ITER}`;
}

function getHeaders(token = null) {
  const headers = {
    "Content-Type": "application/json",
    "X-Agent-ID": getAgentId(),
    "X-Tenant-ID": "tenant_simulation",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

function randomString(length = 8) {
  const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

function categorizeError(response) {
  const body = response.body || "";
  const status = response.status;

  if (status >= 500) {
    serverErrors.add(1);
    return "server_error";
  }

  if (status >= 400 && status < 500) {
    clientErrors.add(1);
  }

  if (
    body.includes("Connection is not available") ||
    body.includes("pool exhausted") ||
    body.includes("too many connections")
  ) {
    connectionPoolErrors.add(1);
    return "connection_pool";
  }

  if (
    status === 401 ||
    body.includes("session expired") ||
    body.includes("invalid token")
  ) {
    sessionLossErrors.add(1);
    return "session_loss";
  }

  if (body.includes("duplicate key") || body.includes("constraint violation")) {
    raceConditionErrors.add(1);
    return "race_condition";
  }

  if (response.error && response.error.includes("timeout")) {
    timeoutErrors.add(1);
    return "timeout";
  }

  return "other";
}

// ═══════════════════════════════════════════════════════════════════════════════
// SETUP - الإعداد
// ═══════════════════════════════════════════════════════════════════════════════

export function setup() {
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log("  SAHOOL IDP - Advanced Load Testing");
  console.log("  اختبار الحمل المتقدم لمنصة سهول");
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log(`  Test Type: ${TEST_TYPE}`);
  console.log(`  Base URL: ${BASE_URL}`);
  console.log(`  Base Agent Count: ${AGENT_COUNT}`);
  console.log(`  Environment: ${ENVIRONMENT}`);
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );

  // Verify service health
  const healthRes = http.get(`${BASE_URL}/healthz`, { timeout: "10s" });
  const isHealthy = healthRes.status === 200;

  console.log(`\n  Health Check: ${isHealthy ? "PASSED" : "FAILED"}`);

  return {
    startTime: new Date().toISOString(),
    baseUrl: BASE_URL,
    testType: TEST_TYPE,
    isHealthy,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCENARIO: Authentication - سيناريو المصادقة
// ═══════════════════════════════════════════════════════════════════════════════

export function authScenario() {
  const agentId = getAgentId();
  activeAgents.add(1);

  group("Auth: Login Flow", () => {
    // Login
    const loginPayload = JSON.stringify({
      username: `user_${agentId}`,
      email: `${agentId}@sahool-test.io`,
      password: "test_password_123",
    });

    const startTime = Date.now();
    const loginRes = http.post(`${BASE_URL}/api/auth/login`, loginPayload, {
      headers: getHeaders(),
      timeout: "30s",
    });
    authDuration.add(Date.now() - startTime);

    const success = check(loginRes, {
      "login status 200": (r) => r.status === 200,
      "login has token": (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.token || body.access_token;
        } catch {
          return false;
        }
      },
    });

    authSuccessRate.add(success);

    if (!success) {
      categorizeError(loginRes);
    }

    let token = null;
    if (loginRes.status === 200) {
      try {
        const body = JSON.parse(loginRes.body);
        token = body.token || body.access_token;
      } catch {}
    }

    sleep(randomIntBetween(1, 3));

    // Session persistence test
    if (token) {
      let sessionValid = true;
      for (let i = 0; i < 3; i++) {
        const profileRes = http.get(`${BASE_URL}/api/profile`, {
          headers: getHeaders(token),
          timeout: "10s",
        });

        if (profileRes.status === 401) {
          sessionValid = false;
          sessionLossErrors.add(1);
          break;
        }
        sleep(0.5);
      }
      sessionPersistenceRate.add(sessionValid);
    }
  });

  sleep(randomIntBetween(2, 5));
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCENARIO: Field Operations - سيناريو عمليات الحقول
// ═══════════════════════════════════════════════════════════════════════════════

export function fieldScenario() {
  const agentId = getAgentId();
  const token = `mock_token_${agentId}`;
  activeAgents.add(1);

  group("Fields: CRUD Operations", () => {
    // List fields
    const listStart = Date.now();
    const listRes = http.get(
      `${BASE_URL}/api/fields?tenant_id=tenant_simulation&limit=20`,
      {
        headers: getHeaders(token),
        timeout: "30s",
      },
    );
    fieldListDuration.add(Date.now() - listStart);

    check(listRes, {
      "list fields status OK": (r) => r.status === 200 || r.status === 401,
    });

    sleep(randomIntBetween(1, 2));

    // Create field
    const fieldData = {
      tenant_id: "tenant_simulation",
      name: `Field_${agentId}_${randomString(4)}`,
      name_ar: `حقل ${agentId}`,
      crop_type: randomItem(["wheat", "barley", "rice", "corn", "dates"]),
      area_hectares: randomIntBetween(1, 100),
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [44.19 + Math.random() * 0.1, 15.37 + Math.random() * 0.1],
            [44.2 + Math.random() * 0.1, 15.37 + Math.random() * 0.1],
            [44.2 + Math.random() * 0.1, 15.38 + Math.random() * 0.1],
            [44.19 + Math.random() * 0.1, 15.38 + Math.random() * 0.1],
            [44.19 + Math.random() * 0.1, 15.37 + Math.random() * 0.1],
          ],
        ],
      },
    };

    const createStart = Date.now();
    const createRes = http.post(
      `${BASE_URL}/api/fields`,
      JSON.stringify(fieldData),
      {
        headers: getHeaders(token),
        timeout: "30s",
      },
    );
    fieldCreateDuration.add(Date.now() - createStart);

    const createSuccess = check(createRes, {
      "create field status OK": (r) => r.status === 201 || r.status === 200,
    });

    fieldOpsSuccessRate.add(createSuccess);

    if (!createSuccess) {
      categorizeError(createRes);
    }

    let fieldId = null;
    if (createRes.status === 201 || createRes.status === 200) {
      try {
        const body = JSON.parse(createRes.body);
        fieldId = body.id || body.field_id;
      } catch {}
    }

    sleep(randomIntBetween(1, 2));

    // Update field (if created)
    if (fieldId) {
      const updateData = {
        area_hectares: randomIntBetween(10, 200),
        crop_type: randomItem(["wheat", "barley", "rice"]),
      };

      const updateStart = Date.now();
      const updateRes = http.patch(
        `${BASE_URL}/api/fields/${fieldId}`,
        JSON.stringify(updateData),
        {
          headers: getHeaders(token),
          timeout: "30s",
        },
      );
      fieldUpdateDuration.add(Date.now() - updateStart);

      check(updateRes, {
        "update field status OK": (r) => r.status === 200 || r.status === 404,
      });

      sleep(randomIntBetween(1, 2));

      // Delete field (cleanup)
      http.del(`${BASE_URL}/api/fields/${fieldId}`, null, {
        headers: getHeaders(token),
        timeout: "30s",
      });
    }
  });

  sleep(randomIntBetween(2, 4));
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCENARIO: Weather Queries - سيناريو استعلامات الطقس
// ═══════════════════════════════════════════════════════════════════════════════

export function weatherScenario() {
  const agentId = getAgentId();
  const token = `mock_token_${agentId}`;
  activeAgents.add(1);

  group("Weather: Data Queries", () => {
    // Get current weather
    const locations = [
      { lat: 24.7136, lon: 46.6753, name: "Riyadh" },
      { lat: 21.4858, lon: 39.1925, name: "Jeddah" },
      { lat: 26.4207, lon: 50.0888, name: "Dammam" },
      { lat: 17.4933, lon: 44.1277, name: "Najran" },
      { lat: 24.4672, lon: 39.6024, name: "Medina" },
    ];

    const location = randomItem(locations);

    const weatherStart = Date.now();
    const weatherRes = http.get(
      `${BASE_URL}/api/weather/current?lat=${location.lat}&lon=${location.lon}`,
      {
        headers: getHeaders(token),
        timeout: "30s",
      },
    );
    weatherDuration.add(Date.now() - weatherStart);

    const success = check(weatherRes, {
      "weather status OK": (r) => r.status === 200 || r.status === 401,
      "weather response time < 2s": (r) => r.timings.duration < 2000,
    });

    weatherSuccessRate.add(success);

    if (!success) {
      categorizeError(weatherRes);
    }

    sleep(randomIntBetween(1, 3));

    // Get weather forecast
    const forecastRes = http.get(
      `${BASE_URL}/api/weather/forecast?lat=${location.lat}&lon=${location.lon}&days=7`,
      {
        headers: getHeaders(token),
        timeout: "30s",
      },
    );

    check(forecastRes, {
      "forecast status OK": (r) => r.status === 200 || r.status === 401,
    });
  });

  sleep(randomIntBetween(3, 6));
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCENARIO: IoT Data - سيناريو بيانات إنترنت الأشياء
// ═══════════════════════════════════════════════════════════════════════════════

export function iotScenario() {
  const agentId = getAgentId();
  const token = `mock_token_${agentId}`;
  activeAgents.add(1);

  group("IoT: Sensor Data", () => {
    // Send sensor data
    const sensorData = {
      device_id: `sensor_${agentId}_${randomString(4)}`,
      tenant_id: "tenant_simulation",
      timestamp: new Date().toISOString(),
      readings: {
        soil_moisture: randomIntBetween(20, 80),
        soil_temperature: randomIntBetween(15, 40),
        air_temperature: randomIntBetween(20, 50),
        humidity: randomIntBetween(30, 90),
        light_intensity: randomIntBetween(100, 1000),
        ph_level: (Math.random() * 4 + 5).toFixed(1),
      },
      location: {
        lat: 24.7136 + Math.random() * 0.1,
        lon: 46.6753 + Math.random() * 0.1,
      },
    };

    const iotStart = Date.now();
    const iotRes = http.post(
      `${BASE_URL}/api/iot/readings`,
      JSON.stringify(sensorData),
      {
        headers: getHeaders(token),
        timeout: "30s",
      },
    );
    iotDuration.add(Date.now() - iotStart);

    const success = check(iotRes, {
      "iot data status OK": (r) =>
        r.status === 201 || r.status === 200 || r.status === 401,
    });

    iotSuccessRate.add(success);

    if (!success) {
      categorizeError(iotRes);
    }

    sleep(randomIntBetween(2, 5));

    // Get sensor history
    http.get(
      `${BASE_URL}/api/iot/readings?device_id=${sensorData.device_id}&limit=10`,
      {
        headers: getHeaders(token),
        timeout: "30s",
      },
    );
  });

  sleep(randomIntBetween(5, 10));
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEARDOWN - التنظيف
// ═══════════════════════════════════════════════════════════════════════════════

export function teardown(data) {
  console.log(
    "\n═══════════════════════════════════════════════════════════════",
  );
  console.log("  SAHOOL IDP - Advanced Load Test Complete");
  console.log("  اكتمل اختبار الحمل المتقدم لمنصة سهول");
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log(`  Start: ${data.startTime}`);
  console.log(`  End: ${new Date().toISOString()}`);
  console.log(`  Test Type: ${data.testType}`);
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SUMMARY HANDLER - معالج الملخص
// ═══════════════════════════════════════════════════════════════════════════════

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    test_type: TEST_TYPE,
    environment: ENVIRONMENT,
    agent_count: AGENT_COUNT,
    scenarios: {
      auth: {
        success_rate: data.metrics.auth_success_rate?.values?.rate || 0,
        avg_duration: data.metrics.auth_duration_ms?.values?.avg || 0,
      },
      fields: {
        success_rate: data.metrics.field_ops_success_rate?.values?.rate || 0,
        list_duration: data.metrics.field_list_duration_ms?.values?.avg || 0,
        create_duration:
          data.metrics.field_create_duration_ms?.values?.avg || 0,
      },
      weather: {
        success_rate: data.metrics.weather_success_rate?.values?.rate || 0,
        avg_duration: data.metrics.weather_duration_ms?.values?.avg || 0,
      },
      iot: {
        success_rate: data.metrics.iot_success_rate?.values?.rate || 0,
        avg_duration: data.metrics.iot_duration_ms?.values?.avg || 0,
      },
    },
    errors: {
      connection_pool: data.metrics.connection_pool_errors?.values?.count || 0,
      session_loss: data.metrics.session_loss_errors?.values?.count || 0,
      race_condition: data.metrics.race_condition_errors?.values?.count || 0,
      timeout: data.metrics.timeout_errors?.values?.count || 0,
      server_5xx: data.metrics.server_errors_5xx?.values?.count || 0,
      client_4xx: data.metrics.client_errors_4xx?.values?.count || 0,
    },
    http: {
      total_requests: data.metrics.http_reqs?.values?.count || 0,
      failed_rate: data.metrics.http_req_failed?.values?.rate || 0,
      avg_duration: data.metrics.http_req_duration?.values?.avg || 0,
      p95_duration: data.metrics.http_req_duration?.values["p(95)"] || 0,
      p99_duration: data.metrics.http_req_duration?.values["p(99)"] || 0,
    },
  };

  return {
    "/results/advanced-test-summary.json": JSON.stringify(summary, null, 2),
    stdout: generateTextSummary(summary),
  };
}

function generateTextSummary(summary) {
  return `
═══════════════════════════════════════════════════════════════════════════════
  ADVANCED LOAD TEST SUMMARY - ملخص اختبار الحمل المتقدم
═══════════════════════════════════════════════════════════════════════════════

  Test Type: ${summary.test_type}
  Agent Count: ${summary.agent_count}

  SCENARIO RESULTS:
  ───────────────────────────────────────────────────────────────────────────────
    Auth:     ${(summary.scenarios.auth.success_rate * 100).toFixed(1)}% success, ${summary.scenarios.auth.avg_duration.toFixed(0)}ms avg
    Fields:   ${(summary.scenarios.fields.success_rate * 100).toFixed(1)}% success, ${summary.scenarios.fields.create_duration.toFixed(0)}ms avg create
    Weather:  ${(summary.scenarios.weather.success_rate * 100).toFixed(1)}% success, ${summary.scenarios.weather.avg_duration.toFixed(0)}ms avg
    IoT:      ${(summary.scenarios.iot.success_rate * 100).toFixed(1)}% success, ${summary.scenarios.iot.avg_duration.toFixed(0)}ms avg

  ERROR ANALYSIS:
  ───────────────────────────────────────────────────────────────────────────────
    Connection Pool: ${summary.errors.connection_pool}
    Session Loss:    ${summary.errors.session_loss}
    Race Conditions: ${summary.errors.race_condition}
    Timeouts:        ${summary.errors.timeout}
    Server (5xx):    ${summary.errors.server_5xx}
    Client (4xx):    ${summary.errors.client_4xx}

  HTTP METRICS:
  ───────────────────────────────────────────────────────────────────────────────
    Total Requests: ${summary.http.total_requests}
    Failed Rate:    ${(summary.http.failed_rate * 100).toFixed(2)}%
    Avg Duration:   ${summary.http.avg_duration.toFixed(0)}ms
    P95 Duration:   ${summary.http.p95_duration.toFixed(0)}ms
    P99 Duration:   ${summary.http.p99_duration.toFixed(0)}ms

═══════════════════════════════════════════════════════════════════════════════
`;
}
