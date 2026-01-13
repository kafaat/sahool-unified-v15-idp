/**
 * Soak Test - SAHOOL Platform
 *
 * Purpose: Test system stability over extended period
 * Duration: 2 hours
 * VUs: 20 constant users
 *
 * Goals:
 * - Detect memory leaks
 * - Find performance degradation over time
 * - Verify database connection pool stability
 * - Test cache effectiveness
 * - Monitor resource usage trends
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Counter, Trend } from "k6/metrics";
import { config, soakThresholds } from "../lib/config.js";
import {
  authenticate,
  authenticatedRequest,
  validateResponse,
  generateRandomField,
  generateRandomOperation,
  generateRandomTask,
  createWeatherAnalysisRequest,
  createSatelliteAnalysisRequest,
  thinkTime,
  randomElement,
  randomInt,
  logIteration,
} from "../lib/helpers.js";

// Custom metrics for soak test
const memoryLeakIndicator = new Trend("memory_leak_indicator");
const performanceDegradation = new Trend("performance_degradation");
const longRunningOps = new Counter("long_running_operations");

// Test configuration
export const options = {
  stages: [
    { duration: "5m", target: 20 }, // Ramp up to 20 VUs
    { duration: "110m", target: 20 }, // Hold at 20 VUs for 110 minutes (1h 50m)
    { duration: "5m", target: 0 }, // Ramp down
  ],
  thresholds: soakThresholds,
  tags: {
    test_type: "soak",
    environment: __ENV.ENVIRONMENT || "local",
  },
};

// Setup
export function setup() {
  console.log("⏱️  Starting Soak Test (Endurance Test)...");
  console.log("Configuration:");
  console.log(`  - Duration: 2 hours`);
  console.log(`  - Constant VUs: 20`);
  console.log(`  - Goal: Detect memory leaks and degradation`);
  console.log(`  - Environment: ${__ENV.ENVIRONMENT || "local"}`);
  console.log("");
  console.log("📊 Monitoring:");
  console.log("  - Response time trends");
  console.log("  - Memory usage patterns");
  console.log("  - Error rate stability");
  console.log("  - Resource cleanup");
  console.log("");
  console.log("☕ This will take a while...");
  console.log("");

  return {
    startTime: Date.now(),
    baselineResponseTimes: {},
  };
}

// Track baseline response times in first 5 minutes
let isBaselinePeriod = true;
let baselineCompleted = false;
const baselineResponseTimes = {};

// Main test function
export default function (data) {
  const iteration = __ITER;
  const currentVU = __VU;
  const elapsedMinutes = (Date.now() - data.startTime) / 1000 / 60;

  // Mark baseline period complete after 5 minutes
  if (elapsedMinutes > 5 && isBaselinePeriod) {
    isBaselinePeriod = false;
    if (!baselineCompleted) {
      baselineCompleted = true;
      console.log(
        "✅ Baseline period completed. Starting long-term stability monitoring...",
      );
    }
  }

  logIteration(
    iteration,
    `VU ${currentVU} - Soak test minute ${elapsedMinutes.toFixed(1)}`,
  );

  // Authenticate
  const authData = authenticate();

  if (!authData || !authData.success) {
    console.error(
      `[VU ${currentVU}] Authentication failed at ${elapsedMinutes.toFixed(1)}m`,
    );
    sleep(5);
    return;
  }

  // Soak Pattern 1: Regular Field Operations (every iteration)
  group("Field Operations Cycle", () => {
    const startTime = Date.now();

    // List fields
    const listUrl = `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}&limit=20`;
    const listResponse = authenticatedRequest(
      "GET",
      listUrl,
      null,
      authData.token,
    );

    const listDuration = Date.now() - startTime;

    check(listResponse, {
      "field list successful": (r) => r.status === 200,
      "field list performance stable": () => {
        if (isBaselinePeriod) {
          if (!baselineResponseTimes.fieldList) {
            baselineResponseTimes.fieldList = listDuration;
          }
          return true;
        }
        // Alert if response time degrades by more than 50%
        const degradation =
          listDuration / (baselineResponseTimes.fieldList || listDuration);
        performanceDegradation.add(degradation);
        return degradation < 1.5;
      },
    });

    sleep(2);

    // Create field (every 3rd iteration to avoid quota issues)
    if (iteration % 3 === 0) {
      const fieldData = generateRandomField(authData.tenantId);
      const createUrl = `${config.fieldServiceUrl}/fields`;
      const createResponse = authenticatedRequest(
        "POST",
        createUrl,
        fieldData,
        authData.token,
      );

      const result = validateResponse(createResponse, 201, "create field");
      const fieldId = result.data?.id || result.data?.field_id;

      if (fieldId) {
        sleep(1);

        // Create operation for the field
        const operationData = generateRandomOperation(
          fieldId,
          authData.tenantId,
        );
        const opUrl = `${config.fieldServiceUrl}/operations`;
        authenticatedRequest("POST", opUrl, operationData, authData.token);

        sleep(1);

        // Clean up - delete field to prevent accumulation
        const deleteUrl = `${config.fieldServiceUrl}/fields/${fieldId}`;
        authenticatedRequest("DELETE", deleteUrl, null, authData.token);
      }
    }

    sleep(2);
  });

  // Soak Pattern 2: Weather Monitoring (every iteration)
  group("Weather Data Cycle", () => {
    const locations = ["sanaa", "aden", "taiz", "hodeidah"];
    const location = randomElement(locations);

    // Current weather
    const currentUrl = `${config.weatherUrl}/v1/current/${location}`;
    const currentResponse = authenticatedRequest(
      "GET",
      currentUrl,
      null,
      authData.token,
    );

    check(currentResponse, {
      "current weather available": (r) => r.status === 200,
      "current weather cached": (r) => {
        // Should be cached after first hour
        if (elapsedMinutes > 60) {
          return r.timings.duration < 200;
        }
        return true;
      },
    });

    sleep(2);

    // Forecast (every other iteration)
    if (iteration % 2 === 0) {
      const forecastUrl = `${config.weatherUrl}/v1/forecast/${location}?days=7`;
      const forecastResponse = authenticatedRequest(
        "GET",
        forecastUrl,
        null,
        authData.token,
      );

      validateResponse(forecastResponse, 200, "weather forecast");
    }

    sleep(2);
  });

  // Soak Pattern 3: Billing Quota Checks (every iteration)
  group("Billing Stability", () => {
    const quotaUrl = `${config.billingUrl}/v1/tenants/${authData.tenantId}/quota`;
    const startTime = Date.now();
    const response = authenticatedRequest(
      "GET",
      quotaUrl,
      null,
      authData.token,
    );
    const duration = Date.now() - startTime;

    check(response, {
      "quota check stable": (r) => r.status === 200,
      "quota query performance": () => {
        // Track if database queries slow down over time
        if (!isBaselinePeriod) {
          const baseline = baselineResponseTimes.quota || duration;
          const ratio = duration / baseline;
          memoryLeakIndicator.add(duration);
          return ratio < 2.0; // Alert if 2x slower
        }
        if (!baselineResponseTimes.quota) {
          baselineResponseTimes.quota = duration;
        }
        return true;
      },
    });

    sleep(2);
  });

  // Soak Pattern 4: Task Management (every 5 iterations)
  if (iteration % 5 === 0) {
    group("Task Lifecycle", () => {
      // List tasks
      const listUrl = `${config.taskUrl}/api/v1/tasks?limit=20`;
      const listResponse = authenticatedRequest(
        "GET",
        listUrl,
        null,
        authData.token,
      );

      validateResponse(listResponse, 200, "list tasks");
      sleep(2);

      // Get task stats
      const statsUrl = `${config.taskUrl}/api/v1/tasks/stats`;
      const statsResponse = authenticatedRequest(
        "GET",
        statsUrl,
        null,
        authData.token,
      );

      check(statsResponse, {
        "task stats available": (r) => r.status === 200,
      });

      sleep(2);
    });
  }

  // Soak Pattern 5: Health Monitoring (every 10 iterations)
  if (iteration % 10 === 0) {
    group("System Health Monitoring", () => {
      const services = [
        { name: "Field Service", url: `${config.fieldServiceUrl}/healthz` },
        { name: "Weather Service", url: `${config.weatherUrl}/healthz` },
        { name: "Billing Service", url: `${config.billingUrl}/healthz` },
      ];

      services.forEach((service) => {
        const response = http.get(service.url, { timeout: "5s" });

        check(response, {
          [`${service.name} healthy`]: (r) => r.status === 200,
          [`${service.name} responds quickly`]: (r) => r.timings.duration < 300,
        });
      });

      sleep(2);
    });
  }

  // Soak Pattern 6: Equipment Telemetry (every 8 iterations)
  if (iteration % 8 === 0) {
    group("Equipment Telemetry Cycle", () => {
      // List equipment
      const listUrl = `${config.equipmentUrl}/api/v1/equipment?limit=20`;
      const listResponse = authenticatedRequest(
        "GET",
        listUrl,
        null,
        authData.token,
      );

      validateResponse(listResponse, 200, "list equipment");
      sleep(2);

      // Get alerts
      const alertsUrl = `${config.equipmentUrl}/api/v1/equipment/alerts`;
      const alertsResponse = authenticatedRequest(
        "GET",
        alertsUrl,
        null,
        authData.token,
      );

      check(alertsResponse, {
        "equipment alerts available": (r) => r.status === 200,
      });

      sleep(2);
    });
  }

  // Soak Pattern 7: Memory Leak Detection (every 20 iterations)
  if (iteration % 20 === 0) {
    group("Memory Leak Detection", () => {
      console.log(
        `[VU ${currentVU}] Memory check at ${elapsedMinutes.toFixed(1)}m (iteration ${iteration})`,
      );

      // Create and delete multiple fields to test cleanup
      const createdFields = [];

      for (let i = 0; i < 5; i++) {
        const fieldData = generateRandomField(authData.tenantId);
        const createUrl = `${config.fieldServiceUrl}/fields`;
        const response = authenticatedRequest(
          "POST",
          createUrl,
          fieldData,
          authData.token,
        );

        const result = validateResponse(response, 201, `create field ${i}`);
        if (result.data?.id || result.data?.field_id) {
          createdFields.push(result.data.id || result.data.field_id);
        }
        sleep(0.5);
      }

      // Delete all created fields
      createdFields.forEach((fieldId, index) => {
        const deleteUrl = `${config.fieldServiceUrl}/fields/${fieldId}`;
        authenticatedRequest("DELETE", deleteUrl, null, authData.token);
        sleep(0.3);
      });

      // Verify cleanup
      const listUrl = `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}`;
      const listResponse = authenticatedRequest(
        "GET",
        listUrl,
        null,
        authData.token,
      );

      check(listResponse, {
        "cleanup successful": (r) => {
          if (r.status === 200) {
            try {
              const body = JSON.parse(r.body);
              const items = body.items || body.data || [];
              // Deleted fields should not appear
              return !items.some((item) =>
                createdFields.includes(item.id || item.field_id),
              );
            } catch {
              return false;
            }
          }
          return false;
        },
      });

      sleep(2);
    });
  }

  // Soak Pattern 8: Long-running Operation Test (every 30 iterations)
  if (iteration % 30 === 0) {
    group("Long-running Operation", () => {
      console.log(
        `[VU ${currentVU}] Long-running operation test at ${elapsedMinutes.toFixed(1)}m`,
      );

      // Create field
      const fieldData = generateRandomField(authData.tenantId);
      const createUrl = `${config.fieldServiceUrl}/fields`;
      const createResponse = authenticatedRequest(
        "POST",
        createUrl,
        fieldData,
        authData.token,
      );

      const result = validateResponse(createResponse, 201, "create field");
      const fieldId = result.data?.id || result.data?.field_id;

      if (fieldId) {
        sleep(2);

        // Satellite analysis (long-running)
        const analysisRequest = createSatelliteAnalysisRequest(fieldId);
        const analysisUrl = `${config.satelliteUrl}/v1/analyze`;
        const startTime = Date.now();
        const analysisResponse = authenticatedRequest(
          "POST",
          analysisUrl,
          analysisRequest,
          authData.token,
        );
        const analysisDuration = Date.now() - startTime;

        check(analysisResponse, {
          "satellite analysis completes": (r) =>
            r.status === 200 || r.status === 202,
          "satellite analysis time reasonable": () => analysisDuration < 30000, // 30 seconds
        });

        if (analysisDuration > 10000) {
          longRunningOps.add(1);
          console.log(
            `[VU ${currentVU}] Long operation detected: ${analysisDuration}ms`,
          );
        }

        sleep(3);

        // Cleanup
        const deleteUrl = `${config.fieldServiceUrl}/fields/${fieldId}`;
        authenticatedRequest("DELETE", deleteUrl, null, authData.token);
      }

      sleep(2);
    });
  }

  // Regular think time
  thinkTime(3, 5);

  // Periodic status update
  if (iteration % 50 === 0) {
    const progress = ((elapsedMinutes / 120) * 100).toFixed(1);
    console.log(
      `⏱️  Soak test progress: ${progress}% (${elapsedMinutes.toFixed(1)}/120 minutes)`,
    );
  }
}

// Teardown
export function teardown(data) {
  const duration = ((Date.now() - data.startTime) / 1000 / 60).toFixed(2);
  console.log("\n⏱️  Soak Test Completed");
  console.log(`Duration: ${duration} minutes`);
  console.log("");
  console.log("📊 Analyze results for:");
  console.log("  - Response time trends over 2 hours");
  console.log("  - Memory leak indicators");
  console.log("  - Performance degradation patterns");
  console.log("  - Resource cleanup effectiveness");
  console.log("  - Database connection stability");
  console.log("  - Cache efficiency over time");
  console.log("");
  console.log("⚠️  Key Questions:");
  console.log("  - Did response times increase over time?");
  console.log("  - Were there any memory leak indicators?");
  console.log("  - Did error rates remain stable?");
  console.log("  - Did the system maintain performance?");
}
