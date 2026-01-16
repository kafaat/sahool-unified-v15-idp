/**
 * Stress Test - SAHOOL Platform
 *
 * Purpose: Find the breaking point of the system
 * Duration: 15 minutes
 * VUs: Ramp up to 200
 *
 * Goals:
 * - Identify system limits
 * - Test graceful degradation
 * - Verify error handling under extreme load
 * - Test recovery after stress
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { config, stressThresholds } from "../lib/config.js";
import {
  authenticate,
  authenticatedRequest,
  validateResponse,
  generateRandomField,
  generateRandomOperation,
  createWeatherAnalysisRequest,
  thinkTime,
  randomElement,
  randomInt,
  logIteration,
} from "../lib/helpers.js";

// Test configuration
export const options = {
  stages: [
    { duration: "2m", target: 20 }, // Warm up
    { duration: "3m", target: 100 }, // Ramp up to 100 VUs
    { duration: "3m", target: 150 }, // Ramp up to 150 VUs
    { duration: "2m", target: 200 }, // Push to 200 VUs
    { duration: "2m", target: 200 }, // Hold at 200 VUs
    { duration: "2m", target: 50 }, // Recovery - scale down to 50
    { duration: "1m", target: 0 }, // Cool down
  ],
  thresholds: stressThresholds,
  tags: {
    test_type: "stress",
    environment: __ENV.ENVIRONMENT || "local",
  },
};

// Setup
export function setup() {
  console.log("💥 Starting Stress Test...");
  console.log("Configuration:");
  console.log(`  - Duration: 15 minutes`);
  console.log(`  - Peak VUs: 200`);
  console.log(`  - Goal: Find breaking point`);
  console.log(`  - Environment: ${__ENV.ENVIRONMENT || "local"}`);
  console.log("");
  console.log("⚠️  This test will push the system to its limits!");
  console.log("");

  return {
    startTime: Date.now(),
    errors: [],
  };
}

// Main test function
export default function (data) {
  const iteration = __ITER;
  const currentVU = __VU;

  // Reduced think time for stress
  const stressThinkTime = () => sleep(randomInt(0, 1));

  // Authenticate with retries
  let authData;
  let retries = 3;
  while (retries > 0 && !authData) {
    authData = authenticate();
    if (!authData || !authData.success) {
      retries--;
      sleep(1);
    } else {
      break;
    }
  }

  if (!authData || !authData.success) {
    console.error(`[VU ${currentVU}] Auth failed after retries, aborting`);
    sleep(5);
    return;
  }

  logIteration(iteration, `VU ${currentVU} - Stress iteration`);

  // Stress Pattern 1: Aggressive Field Operations (70% of VUs)
  if (Math.random() < 0.7) {
    group("Aggressive Field Operations", () => {
      // Rapid field creation
      for (let i = 0; i < randomInt(1, 3); i++) {
        const fieldData = generateRandomField(authData.tenantId);
        const createUrl = `${config.fieldServiceUrl}/fields`;
        const response = authenticatedRequest(
          "POST",
          createUrl,
          fieldData,
          authData.token,
        );

        check(response, {
          "field creation handled": (r) =>
            r.status === 201 || r.status === 429 || r.status === 503,
        });

        stressThinkTime();
      }

      // Rapid listing
      for (let i = 0; i < randomInt(3, 6); i++) {
        const listUrl = `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}&limit=50`;
        const response = authenticatedRequest(
          "GET",
          listUrl,
          null,
          authData.token,
        );

        check(response, {
          "list request handled": (r) =>
            r.status === 200 || r.status === 429 || r.status === 503,
        });

        stressThinkTime();
      }
    });
  }

  // Stress Pattern 2: Heavy Weather Requests (50% of VUs)
  if (Math.random() < 0.5) {
    group("Heavy Weather Requests", () => {
      const locations = ["sanaa", "aden", "taiz", "hodeidah", "ibb", "dhamar"];

      // Request multiple locations rapidly
      for (let i = 0; i < randomInt(2, 5); i++) {
        const location = randomElement(locations);
        const url = `${config.weatherUrl}/v1/forecast/${location}?days=7`;
        const response = authenticatedRequest("GET", url, null, authData.token);

        check(response, {
          "weather request handled": (r) =>
            r.status === 200 || r.status === 429 || r.status === 503,
          "response time acceptable under stress": (r) =>
            r.timings.duration < 5000,
        });

        stressThinkTime();
      }

      // Current weather for all locations
      locations.forEach((location) => {
        const url = `${config.weatherUrl}/v1/current/${location}`;
        authenticatedRequest("GET", url, null, authData.token);
      });
    });
  }

  // Stress Pattern 3: Concurrent Operations (40% of VUs)
  if (Math.random() < 0.4) {
    group("Concurrent Operations", () => {
      // Create field first
      const fieldData = generateRandomField(authData.tenantId);
      const fieldUrl = `${config.fieldServiceUrl}/fields`;
      const fieldResponse = authenticatedRequest(
        "POST",
        fieldUrl,
        fieldData,
        authData.token,
      );

      const fieldResult = validateResponse(
        fieldResponse,
        201,
        "field creation",
      );
      const fieldId = fieldResult.data?.id || fieldResult.data?.field_id;

      if (fieldId) {
        // Rapid operation creation
        for (let i = 0; i < randomInt(2, 5); i++) {
          const operationData = generateRandomOperation(
            fieldId,
            authData.tenantId,
          );
          const opUrl = `${config.fieldServiceUrl}/operations`;
          const opResponse = authenticatedRequest(
            "POST",
            opUrl,
            operationData,
            authData.token,
          );

          check(opResponse, {
            "operation creation handled": (r) =>
              r.status === 201 || r.status === 429 || r.status === 503,
          });

          stressThinkTime();
        }

        // List operations repeatedly
        for (let i = 0; i < randomInt(3, 6); i++) {
          const listUrl = `${config.fieldServiceUrl}/operations?field_id=${fieldId}`;
          authenticatedRequest("GET", listUrl, null, authData.token);
          stressThinkTime();
        }
      }
    });
  }

  // Stress Pattern 4: Billing Quota Checks (30% of VUs)
  if (Math.random() < 0.3) {
    group("Quota Check Storm", () => {
      // Rapid quota checks
      for (let i = 0; i < randomInt(5, 10); i++) {
        const quotaUrl = `${config.billingUrl}/v1/tenants/${authData.tenantId}/quota`;
        const response = authenticatedRequest(
          "GET",
          quotaUrl,
          null,
          authData.token,
        );

        check(response, {
          "quota check handled": (r) =>
            r.status === 200 || r.status === 429 || r.status === 503,
        });

        stressThinkTime();
      }
    });
  }

  // Stress Pattern 5: Mixed Read/Write (60% of VUs)
  if (Math.random() < 0.6) {
    group("Mixed Operations", () => {
      const operations = [
        // Read operations
        () =>
          authenticatedRequest(
            "GET",
            `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}`,
            null,
            authData.token,
          ),
        () =>
          authenticatedRequest(
            "GET",
            `${config.weatherUrl}/v1/forecast/sanaa`,
            null,
            authData.token,
          ),
        () =>
          authenticatedRequest(
            "GET",
            `${config.billingUrl}/v1/plans`,
            null,
            authData.token,
          ),
        // Write operations
        () => {
          const field = generateRandomField(authData.tenantId);
          return authenticatedRequest(
            "POST",
            `${config.fieldServiceUrl}/fields`,
            field,
            authData.token,
          );
        },
      ];

      // Execute random operations
      for (let i = 0; i < randomInt(5, 10); i++) {
        const operation = randomElement(operations);
        const response = operation();

        check(response, {
          "mixed operation handled": (r) => r.status < 500 || r.status === 503,
        });

        stressThinkTime();
      }
    });
  }

  // Stress Pattern 6: Health Check Spam (10% of VUs)
  if (Math.random() < 0.1) {
    group("Health Check Storm", () => {
      const healthEndpoints = [
        `${config.fieldServiceUrl}/healthz`,
        `${config.weatherUrl}/healthz`,
        `${config.billingUrl}/healthz`,
      ];

      // Rapid health checks
      for (let i = 0; i < randomInt(10, 20); i++) {
        const endpoint = randomElement(healthEndpoints);
        const response = http.get(endpoint, { timeout: "5s" });

        check(response, {
          "health endpoint responsive": (r) =>
            r.status === 200 || r.status === 503,
          "health check fast": (r) => r.timings.duration < 1000,
        });
      }
    });
  }

  // Track errors
  group("Error Monitoring", () => {
    // Check if we're getting rate limited
    const testUrl = `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}&limit=1`;
    const response = authenticatedRequest("GET", testUrl, null, authData.token);

    const errorChecks = {
      "no server errors (5xx)": (r) => r.status < 500 || r.status === 503,
      "rate limiting working": (r) =>
        r.status !== 429 || r.headers["Retry-After"] !== undefined,
      "response within timeout": (r) => r.timings.duration < 10000,
    };

    const result = check(response, errorChecks);

    if (!result) {
      console.warn(
        `[VU ${currentVU}] Error detected: Status ${response.status}, Duration ${response.timings.duration}ms`,
      );
    }
  });

  // Minimal think time under stress
  sleep(randomInt(0, 2) * 0.1);
}

// Teardown
export function teardown(data) {
  const duration = ((Date.now() - data.startTime) / 1000 / 60).toFixed(2);
  console.log("\n💥 Stress Test Completed");
  console.log(`Duration: ${duration} minutes`);
  console.log("");
  console.log("📊 Check metrics for:");
  console.log("  - Maximum sustainable load");
  console.log("  - Error rates under stress");
  console.log("  - Recovery time");
  console.log("  - Resource exhaustion points");
  console.log("");
  console.log("⚠️  Review logs for any critical failures");
}
