/**
 * SAHOOL Platform - Agricultural Workflows Load Test
 * اختبار الأداء والحمل - سير العمل الزراعي
 *
 * Purpose  : Validate performance of the end-to-end agricultural advisory
 *            and field management workflows under realistic concurrent load.
 * Duration : ~12 minutes total
 * Peak VUs : 80 concurrent virtual users
 *
 * Scenarios covered
 * -----------------
 * S1: Complete Advisory Workflow   (field → weather → NDVI → advisory)
 * S2: Smart Irrigation Workflow    (sensor → weather → calculate → schedule)
 * S3: Pest Detection Workflow      (image → detect → alert → advisory)
 * S4: Harvest & Market Workflow    (harvest → quality → traceability → market)
 * S5: Auth & Tenant Onboarding     (register → verify → create field)
 *
 * SLOs (Service Level Objectives)
 * --------------------------------
 * - p95 response time < 500 ms
 * - p99 response time < 1500 ms
 * - Error rate < 2%
 * - Advisory endpoint p95 < 800 ms
 * - Vision detection p95 < 2000 ms  (GPU inference)
 *
 * Run
 * ---
 *   k6 run tests/load/scenarios/agricultural_workflows.js
 *   k6 run --env BASE_URL=http://gateway:8000 tests/load/scenarios/agricultural_workflows.js
 *
 * Environment Variables
 * ---------------------
 *   BASE_URL         – API gateway base URL (default: http://localhost:8000)
 *   FIELD_URL        – Field service direct URL (default: http://localhost:3000)
 *   ADVISORY_URL     – Advisory service URL    (default: http://localhost:8093)
 *   WEATHER_URL      – Weather service URL     (default: http://localhost:8092)
 *   IRRIGATION_URL   – Irrigation service URL  (default: http://localhost:8094)
 *   VISION_URL       – Vision service URL      (default: http://localhost:8150)
 *   TRACEABILITY_URL – Traceability service URL (default: http://localhost:8123)
 *   AUTH_TOKEN       – Bearer JWT token (optional, uses fallback mock if absent)
 *   TENANT_ID        – Tenant ID for the test run
 *
 * Author: SAHOOL Platform Team
 */

import http from "k6/http";
import { check, group, sleep, fail } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

// =============================================================================
// Service URLs
// =============================================================================

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const FIELD_URL = __ENV.FIELD_URL || "http://localhost:3000";
const ADVISORY_URL = __ENV.ADVISORY_URL || "http://localhost:8093";
const WEATHER_URL = __ENV.WEATHER_URL || "http://localhost:8092";
const IRRIGATION_URL = __ENV.IRRIGATION_URL || "http://localhost:8094";
const VISION_URL = __ENV.VISION_URL || "http://localhost:8150";
const VEGETATION_URL = __ENV.VEGETATION_URL || "http://localhost:8090";
const TRACEABILITY_URL = __ENV.TRACEABILITY_URL || "http://localhost:8123";
const AUTH_TOKEN = __ENV.AUTH_TOKEN || "load-test-bearer-token";
const TENANT_ID = __ENV.TENANT_ID || "tenant_loadtest_workflows";

// =============================================================================
// Custom Metrics
// =============================================================================

const advisoryWorkflowDuration = new Trend("advisory_workflow_duration", true);
const irrigationWorkflowDuration = new Trend("irrigation_workflow_duration", true);
const visionWorkflowDuration = new Trend("vision_workflow_duration", true);
const harvestWorkflowDuration = new Trend("harvest_workflow_duration", true);

const workflowSuccessRate = new Rate("workflow_success_rate");
const advisorySuccessRate = new Rate("advisory_success_rate");
const irrigationSuccessRate = new Rate("irrigation_success_rate");
const visionSuccessRate = new Rate("vision_success_rate");

const fieldCreations = new Counter("field_creations_total");
const advisoryRequests = new Counter("advisory_requests_total");
const irrigationCalculations = new Counter("irrigation_calculations_total");
const alertsGenerated = new Counter("alerts_generated_total");

// =============================================================================
// Test Options & Thresholds
// =============================================================================

export const options = {
  scenarios: {
    advisory_workflow: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "2m", target: 20 }, // Warm-up
        { duration: "4m", target: 40 }, // Ramp to target
        { duration: "3m", target: 40 }, // Steady state
        { duration: "2m", target: 20 }, // Scale down
        { duration: "1m", target: 0 }, //  Cool-down
      ],
      gracefulRampDown: "30s",
      exec: "advisoryWorkflow",
    },
    irrigation_workflow: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "2m", target: 15 },
        { duration: "4m", target: 30 },
        { duration: "3m", target: 30 },
        { duration: "2m", target: 0 },
      ],
      gracefulRampDown: "30s",
      exec: "irrigationWorkflow",
    },
    pest_detection_workflow: {
      executor: "constant-vus",
      vus: 5, // Vision is GPU-intensive — keep VUs low
      duration: "8m",
      exec: "pestDetectionWorkflow",
    },
    harvest_market_workflow: {
      executor: "per-vu-iterations",
      vus: 10,
      iterations: 20,
      maxDuration: "5m",
      exec: "harvestMarketWorkflow",
    },
  },

  thresholds: {
    // Global SLOs
    http_req_duration: ["p(95)<500", "p(99)<1500", "avg<300"],
    http_req_failed: ["rate<0.02"], // < 2% error rate

    // Per-workflow SLOs
    advisory_workflow_duration: ["p(95)<800"],
    irrigation_workflow_duration: ["p(95)<600"],
    vision_workflow_duration: ["p(95)<2000"],
    harvest_workflow_duration: ["p(95)<400"],

    // Success rates
    workflow_success_rate: ["rate>0.97"],
    advisory_success_rate: ["rate>0.95"],
    irrigation_success_rate: ["rate>0.97"],
    vision_success_rate: ["rate>0.90"], // Vision can be slower / unavailable in CI
  },

  tags: {
    test_type: "agricultural_workflows_load",
    environment: __ENV.ENVIRONMENT || "local",
    platform: "sahool",
  },
};

// =============================================================================
// Helpers
// =============================================================================

// Cryptographically secure random in [0, 1)
function secureRandom() {
  const arr = new Uint32Array(1);
  crypto.getRandomValues(arr);
  return arr[0] * Math.pow(2, -32);
}

function randomUUID() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (secureRandom() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function randomChoice(arr) {
  return arr[Math.floor(secureRandom() * arr.length)];
}

function defaultHeaders(tenantId) {
  return {
    "Content-Type": "application/json",
    Accept: "application/json",
    Authorization: `Bearer ${AUTH_TOKEN}`,
    "X-Tenant-ID": tenantId || TENANT_ID,
    "X-User-ID": randomUUID(),
    "X-Request-ID": randomUUID(),
  };
}

const CROP_TYPES = ["wheat", "barley", "tomato", "cucumber", "date_palm", "corn"];
const CROP_STAGES = ["germination", "tillering", "heading", "grain_fill", "ripening"];
const LOCATIONS = ["riyadh", "jeddah", "dammam", "taif", "mecca", "medina"];

function makeFieldPolygon() {
  const baseLon = 46.6 + secureRandom() * 0.5;
  const baseLat = 24.5 + secureRandom() * 0.5;
  const d = 0.01; // ~1 km
  return {
    type: "Polygon",
    coordinates: [
      [
        [baseLon, baseLat],
        [baseLon + d, baseLat],
        [baseLon + d, baseLat + d],
        [baseLon, baseLat + d],
        [baseLon, baseLat],
      ],
    ],
  };
}

function checkAndRecord(response, expectedStatuses, metricRate, description) {
  const ok = expectedStatuses.includes(response.status);
  metricRate.add(ok ? 1 : 0);
  workflowSuccessRate.add(ok ? 1 : 0);
  check(response, {
    [`${description} - acceptable status`]: () => ok,
  });
  if (!ok) {
    console.warn(`[WARN] ${description} returned HTTP ${response.status}`);
  }
  return ok;
}

// =============================================================================
// S1: Complete Agricultural Advisory Workflow
// =============================================================================

export function advisoryWorkflow() {
  const tenantId = TENANT_ID;
  const fieldId = randomUUID();
  const hdrs = defaultHeaders(tenantId);
  const cropType = randomChoice(CROP_TYPES);
  const stage = randomChoice(CROP_STAGES);
  const startTime = Date.now();

  group("S1: Agricultural Advisory Workflow", () => {
    // ── Step 1: Create field ──────────────────────────────────────────────
    group("1. Create Field", () => {
      const payload = JSON.stringify({
        name: `Load-Test Field ${randomUUID().slice(0, 8)}`,
        name_ar: "حقل اختبار الحمل",
        tenant_id: tenantId,
        area_hectares: 5 + secureRandom() * 20,
        crop_type: cropType,
        geometry: makeFieldPolygon(),
      });

      const res = http.post(`${FIELD_URL}/api/v1/fields`, payload, { headers: hdrs });
      checkAndRecord(res, [200, 201, 400, 409, 422], advisorySuccessRate, "create-field");
      fieldCreations.add(1);
    });
    sleep(0.3);

    // ── Step 2: Fetch weather ─────────────────────────────────────────────
    group("2. Fetch Weather", () => {
      const location = randomChoice(LOCATIONS);
      const res = http.get(`${WEATHER_URL}/api/v1/current?location=${location}`, { headers: hdrs });
      checkAndRecord(res, [200, 404, 503], advisorySuccessRate, "fetch-weather");
    });
    sleep(0.2);

    // ── Step 3: Request NDVI ──────────────────────────────────────────────
    group("3. Request NDVI", () => {
      const today = new Date().toISOString().split("T")[0];
      const res = http.get(
        `${VEGETATION_URL}/api/v1/ndvi?field_id=${fieldId}&date=${today}`,
        { headers: hdrs },
      );
      checkAndRecord(res, [200, 202, 404, 503], advisorySuccessRate, "ndvi-analysis");
    });
    sleep(0.3);

    // ── Step 4: Get advisory recommendations ─────────────────────────────
    group("4. Get Advisory Recommendations", () => {
      const payload = JSON.stringify({
        field_id: fieldId,
        tenant_id: tenantId,
        crop_type: cropType,
        crop_stage: stage,
        ndvi_value: 0.4 + secureRandom() * 0.4,
        weather: {
          temperature: 20 + secureRandom() * 20,
          rain_probability: secureRandom() * 30,
        },
      });

      const res = http.post(`${ADVISORY_URL}/api/v1/recommendations`, payload, { headers: hdrs });
      checkAndRecord(res, [200, 201, 400, 422, 503], advisorySuccessRate, "advisory-recommendations");
      advisoryRequests.add(1);
    });
    sleep(0.5);
  });

  advisoryWorkflowDuration.add(Date.now() - startTime);
  sleep(1 + secureRandom() * 2); // Think time 1-3s
}

// =============================================================================
// S2: Smart Irrigation Workflow
// =============================================================================

export function irrigationWorkflow() {
  const tenantId = TENANT_ID;
  const fieldId = randomUUID();
  const hdrs = defaultHeaders(tenantId);
  const startTime = Date.now();

  group("S2: Smart Irrigation Workflow", () => {
    // ── Step 1: Submit sensor reading ─────────────────────────────────────
    group("1. Submit IoT Sensor Reading", () => {
      const payload = JSON.stringify({
        sensor_id: randomUUID(),
        field_id: fieldId,
        reading_type: "soil_moisture",
        value: 15 + secureRandom() * 40, // 15–55 %
        unit: "percent",
        timestamp: new Date().toISOString(),
      });
      const res = http.post("http://localhost:8117/api/v1/readings", payload, { headers: hdrs });
      checkAndRecord(res, [200, 201, 400, 422, 503], irrigationSuccessRate, "iot-sensor-reading");
    });
    sleep(0.2);

    // ── Step 2: Fetch weather context ─────────────────────────────────────
    group("2. Fetch Weather for Irrigation Context", () => {
      const res = http.get(
        `${WEATHER_URL}/api/v1/forecast?location=riyadh&days=3`,
        { headers: hdrs },
      );
      checkAndRecord(res, [200, 404, 503], irrigationSuccessRate, "weather-forecast-for-irrigation");
    });
    sleep(0.2);

    // ── Step 3: Calculate irrigation ─────────────────────────────────────
    group("3. Calculate Irrigation", () => {
      const payload = JSON.stringify({
        field_id: fieldId,
        crop_type: randomChoice(["wheat", "tomato", "barley"]),
        crop_stage: randomChoice(CROP_STAGES),
        soil_moisture_percent: 15 + secureRandom() * 25,
        weather_context: {
          temperature: 25 + secureRandom() * 15,
          humidity: 30 + secureRandom() * 30,
          rain_probability: secureRandom() * 20,
          evapotranspiration_mm_day: 6 + secureRandom() * 6,
        },
      });

      const res = http.post(`${IRRIGATION_URL}/api/v1/calculate`, payload, { headers: hdrs });
      checkAndRecord(res, [200, 201, 400, 422, 503], irrigationSuccessRate, "irrigation-calculate");
      irrigationCalculations.add(1);
    });
    sleep(0.3);

    // ── Step 4: Schedule task ─────────────────────────────────────────────
    group("4. Schedule Irrigation Task", () => {
      const payload = JSON.stringify({
        task_type: "irrigation",
        field_id: fieldId,
        tenant_id: tenantId,
        priority: "high",
        scheduled_at: new Date(Date.now() + 7200000).toISOString(), // +2h
        instructions_en: "Irrigate field with 25mm",
        instructions_ar: "ري الحقل بمقدار 25 مم",
      });

      const res = http.post("http://localhost:8103/api/v1/tasks", payload, { headers: hdrs });
      checkAndRecord(res, [200, 201, 400, 422, 503], irrigationSuccessRate, "create-irrigation-task");
    });
    sleep(0.5);
  });

  irrigationWorkflowDuration.add(Date.now() - startTime);
  sleep(1 + secureRandom() * 1.5);
}

// =============================================================================
// S3: Pest Detection Workflow
// =============================================================================

// Minimal 1×1 white JPEG (base64) for test images
const TINY_JPEG_B64 =
  "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U" +
  "HRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAARCAABAAEDASIA" +
  "AhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABgUE/8QAIRAAAQMFAAMBAAAAAAAAAAAAAQIE" +
  "BREhMVFBYf/EABQBAQAAAAAAAAAAAAAAAAAAAAD/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oA" +
  "DAMBAAIRAxEAPwCRQANxjXS5KiVN8VrTHe5GvRfKoAIB/9k=";

export function pestDetectionWorkflow() {
  const tenantId = TENANT_ID;
  const fieldId = randomUUID();
  const hdrs = defaultHeaders(tenantId);
  const startTime = Date.now();

  group("S3: Pest Detection Workflow", () => {
    // ── Step 1: Submit image for detection ───────────────────────────────
    group("1. Submit Image for Pest Detection", () => {
      const task = randomChoice(["pest", "disease", "weed"]);
      const payload = JSON.stringify({
        image_base64: TINY_JPEG_B64,
        field_id: fieldId,
        model_variant: "n", // nano — fastest for load tests
        confidence_threshold: 0.25,
      });

      const res = http.post(`${VISION_URL}/api/v1/detect/${task}`, payload, {
        headers: hdrs,
        timeout: "20s", // GPU inference can be slow
      });
      checkAndRecord(res, [200, 400, 422, 503], visionSuccessRate, `vision-detect-${task}`);
      visionSuccessRate.add(res.status === 200 ? 1 : 0);
    });
    sleep(0.5);

    // ── Step 2: Generate alert (simulated) ───────────────────────────────
    group("2. Generate Alert", () => {
      const payload = JSON.stringify({
        alert_type: "pest_detected",
        field_id: fieldId,
        tenant_id: tenantId,
        severity: randomChoice(["low", "medium", "high"]),
        message_ar: "تم اكتشاف آفة في الحقل",
        message_en: "Pest detected in the field",
        detected_at: new Date().toISOString(),
      });

      const res = http.post("http://localhost:8113/api/v1/alerts", payload, { headers: hdrs });
      checkAndRecord(res, [200, 201, 400, 422, 503], visionSuccessRate, "create-alert");
      alertsGenerated.add(1);
    });
    sleep(0.3);

    // ── Step 3: Fetch advisory for detected pest ──────────────────────────
    group("3. Fetch Advisory for Pest", () => {
      const issues = ["aphid", "red_palm_weevil", "powdery_mildew", "rust"];
      const pest = randomChoice(issues);
      const res = http.get(
        `${ADVISORY_URL}/api/v1/recommendations?issue=${pest}&crop_type=wheat`,
        { headers: hdrs },
      );
      checkAndRecord(res, [200, 404, 503], visionSuccessRate, "advisory-for-pest");
    });
    sleep(1.0); // Vision workflow has longer think time
  });

  visionWorkflowDuration.add(Date.now() - startTime);
  sleep(2 + secureRandom() * 3);
}

// =============================================================================
// S4: Harvest & Market Workflow
// =============================================================================

export function harvestMarketWorkflow() {
  const tenantId = TENANT_ID;
  const fieldId = randomUUID();
  const harvestId = randomUUID();
  const hdrs = defaultHeaders(tenantId);
  const startTime = Date.now();

  group("S4: Harvest & Market Workflow", () => {
    // ── Step 1: Record harvest ────────────────────────────────────────────
    group("1. Record Harvest", () => {
      const payload = JSON.stringify({
        field_id: fieldId,
        tenant_id: tenantId,
        crop_type: randomChoice(["wheat", "barley", "tomato"]),
        variety: "Sakha 95",
        quantity_kg: 5000 + secureRandom() * 15000,
        moisture_percent: 10 + secureRandom() * 8,
        harvested_at: new Date().toISOString(),
      });

      const res = http.post("http://localhost:3000/api/v1/harvests", payload, { headers: hdrs });
      checkAndRecord(res, [200, 201, 400, 404, 422, 503], advisorySuccessRate, "record-harvest");
    });
    sleep(0.2);

    // ── Step 2: Generate traceability QR ─────────────────────────────────
    group("2. Generate Traceability QR", () => {
      const payload = JSON.stringify({
        harvest_id: harvestId,
        field_id: fieldId,
        tenant_id: tenantId,
        crop_type: "wheat",
        quality_grade: randomChoice(["A", "B", "C"]),
        quantity_kg: 8000,
      });

      const res = http.post(`${TRACEABILITY_URL}/api/v1/trace`, payload, { headers: hdrs });
      checkAndRecord(res, [200, 201, 400, 422, 503], advisorySuccessRate, "traceability-qr");
    });
    sleep(0.2);

    // ── Step 3: Check market prices ───────────────────────────────────────
    group("3. Check Market Prices", () => {
      const crop = randomChoice(CROP_TYPES);
      const res = http.get(
        `http://localhost:3010/api/v1/prices?crop_type=${crop}`,
        { headers: hdrs },
      );
      checkAndRecord(res, [200, 404, 503], advisorySuccessRate, "market-prices");
    });
    sleep(0.3);
  });

  harvestWorkflowDuration.add(Date.now() - startTime);
  sleep(0.5 + secureRandom());
}

// =============================================================================
// Setup (runs once before all VUs start)
// =============================================================================

export function setup() {
  console.log("=".repeat(65));
  console.log("SAHOOL Agricultural Workflows Load Test");
  console.log("اختبار الأداء - سير العمل الزراعي");
  console.log("=".repeat(65));
  console.log(`Tenant    : ${TENANT_ID}`);
  console.log(`Field URL : ${FIELD_URL}`);
  console.log(`Advisory  : ${ADVISORY_URL}`);
  console.log(`Weather   : ${WEATHER_URL}`);
  console.log(`Vegetation: ${VEGETATION_URL}`);
  console.log(`Vision    : ${VISION_URL}`);
  console.log(`Irrigation: ${IRRIGATION_URL}`);
  console.log("=".repeat(65));
  console.log("");

  // Pre-flight health checks
  const services = [
    { name: "Field Management", url: `${FIELD_URL}/healthz` },
    { name: "Advisory", url: `${ADVISORY_URL}/healthz` },
    { name: "Weather", url: `${WEATHER_URL}/healthz` },
    { name: "Irrigation", url: `${IRRIGATION_URL}/healthz` },
  ];

  console.log("Pre-flight health checks:");
  services.forEach(({ name, url }) => {
    try {
      const res = http.get(url, { timeout: "5s" });
      console.log(`  ${res.status === 200 ? "✅" : "⚠️"} ${name}: HTTP ${res.status}`);
    } catch (e) {
      console.log(`  ⚠️  ${name}: unreachable (${e})`);
    }
  });
  console.log("");

  return { startTime: Date.now() };
}

// =============================================================================
// Teardown (runs once after all VUs finish)
// =============================================================================

export function teardown(data) {
  const durationSec = ((Date.now() - data.startTime) / 1000).toFixed(1);
  console.log("");
  console.log("=".repeat(65));
  console.log(`✅ Agricultural Workflows Load Test Completed`);
  console.log(`   Duration   : ${durationSec} seconds`);
  console.log(`   Test type  : agricultural_workflows_load`);
  console.log("=".repeat(65));
  console.log("Check the summary metrics for SLO compliance.");
}
