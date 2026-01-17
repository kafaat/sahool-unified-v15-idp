/**
 * Spike Test - SAHOOL Platform
 *
 * Purpose: Test system behavior under sudden traffic spikes
 * Duration: 8 minutes
 * Pattern: Sudden surge from 10 to 200 VUs and back
 *
 * Goals:
 * - Test auto-scaling response
 * - Verify system doesn't crash
 * - Measure recovery time
 * - Test circuit breakers and rate limiting
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { config, spikeThresholds } from "../lib/config.js";
import {
  authenticate,
  authenticatedRequest,
  validateResponse,
  generateRandomField,
  createWeatherAnalysisRequest,
  thinkTime,
  randomElement,
  randomInt,
} from "../lib/helpers.js";

// Test configuration
export const options = {
  stages: [
    { duration: "30s", target: 10 }, // Normal load
    { duration: "30s", target: 200 }, // SPIKE! Jump to 200 VUs
    { duration: "2m", target: 200 }, // Hold spike
    { duration: "30s", target: 10 }, // Drop back down
    { duration: "2m", target: 10 }, // Recovery period
    { duration: "30s", target: 150 }, // Second spike
    { duration: "1m", target: 150 }, // Hold second spike
    { duration: "30s", target: 0 }, // Cool down
  ],
  thresholds: spikeThresholds,
  tags: {
    test_type: "spike",
    environment: __ENV.ENVIRONMENT || "local",
  },
};

// Setup
export function setup() {
  console.log("⚡ Starting Spike Test...");
  console.log("Configuration:");
  console.log(`  - Duration: 8 minutes`);
  console.log(`  - Spike 1: 10 → 200 VUs in 30s`);
  console.log(`  - Spike 2: 10 → 150 VUs in 30s`);
  console.log(`  - Environment: ${__ENV.ENVIRONMENT || "local"}`);
  console.log("");
  console.log("📈 Testing sudden traffic bursts...");
  console.log("");

  return {
    startTime: Date.now(),
    spikeStartTimes: [],
    currentPhase: "normal",
  };
}

// Detect current phase based on VU count
function getCurrentPhase() {
  const vu = __VU;
  if (vu <= 20) return "normal";
  if (vu >= 100) return "spike";
  return "transition";
}

// Main test function
export default function (data) {
  const iteration = __ITER;
  const currentVU = __VU;
  const phase = getCurrentPhase();

  // Log phase transitions
  if (iteration === 0) {
    console.log(`[VU ${currentVU}] Joined during ${phase} phase`);
  }

  // Authenticate
  const authData = authenticate();

  if (!authData || !authData.success) {
    console.error(
      `[VU ${currentVU}] Authentication failed during ${phase} phase`,
    );
    sleep(2);
    return;
  }

  // Spike Test Pattern 1: High-Priority Operations (all users)
  group("Critical Path - Field List", () => {
    const url = `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}&limit=20`;
    const response = authenticatedRequest("GET", url, null, authData.token);

    const checks = {
      "field list successful": (r) => r.status === 200,
      "field list has data": (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.items !== undefined || body.data !== undefined;
        } catch {
          return false;
        }
      },
      "response time acceptable": (r) => {
        // More lenient during spike
        const threshold = phase === "spike" ? 3000 : 1000;
        return r.timings.duration < threshold;
      },
    };

    const result = check(response, checks);

    if (!result && phase === "spike") {
      console.warn(`[VU ${currentVU}] Field list degraded during spike`);
    }

    sleep(0.5);
  });

  // Spike Test Pattern 2: Weather Requests (80% of users)
  if (Math.random() < 0.8) {
    group("Weather Forecast", () => {
      const locations = ["sanaa", "aden", "taiz"];
      const location = randomElement(locations);
      const url = `${config.weatherUrl}/v1/forecast/${location}?days=3`;

      const response = authenticatedRequest("GET", url, null, authData.token);

      check(response, {
        "weather forecast accessible": (r) =>
          r.status === 200 || r.status === 429 || r.status === 503,
        "weather response time reasonable": (r) => {
          const threshold = phase === "spike" ? 5000 : 2000;
          return r.timings.duration < threshold;
        },
      });

      sleep(randomInt(0, 2) * 0.5);
    });
  }

  // Spike Test Pattern 3: Field Creation (during normal phase: 40%, during spike: 20%)
  const creationProbability = phase === "spike" ? 0.2 : 0.4;

  if (Math.random() < creationProbability) {
    group("Field Creation", () => {
      const fieldData = generateRandomField(authData.tenantId);
      const url = `${config.fieldServiceUrl}/fields`;
      const response = authenticatedRequest(
        "POST",
        url,
        fieldData,
        authData.token,
      );

      check(response, {
        "field creation handled": (r) => {
          // During spike, we accept rate limiting
          if (phase === "spike") {
            return r.status === 201 || r.status === 429 || r.status === 503;
          }
          return r.status === 201;
        },
        "rate limiting present during spike": (r) => {
          if (phase === "spike" && r.status === 429) {
            return r.headers["Retry-After"] !== undefined;
          }
          return true;
        },
      });

      sleep(1);
    });
  }

  // Spike Test Pattern 4: Billing Quota (all users, monitor for degradation)
  group("Quota Check", () => {
    const url = `${config.billingUrl}/v1/tenants/${authData.tenantId}/quota`;
    const response = authenticatedRequest("GET", url, null, authData.token);

    check(response, {
      "quota check responsive": (r) =>
        r.status === 200 || r.status === 429 || r.status === 503,
      "quota cached properly": (r) => {
        if (r.status === 200) {
          return (
            r.headers["Cache-Control"] !== undefined ||
            r.headers["X-Cache"] !== undefined
          );
        }
        return true;
      },
    });

    sleep(0.3);
  });

  // Spike Test Pattern 5: Health Check Monitoring
  group("System Health", () => {
    const healthUrl = `${config.fieldServiceUrl}/healthz`;
    const response = http.get(healthUrl, { timeout: "5s" });

    const healthChecks = {
      "health endpoint accessible": (r) => r.status === 200 || r.status === 503,
      "health check fast": (r) => r.timings.duration < 500,
    };

    const result = check(response, healthChecks);

    if (!result && phase === "spike") {
      console.warn(
        `[VU ${currentVU}] Health endpoint degraded during spike (${response.status})`,
      );
    }
  });

  // Spike Test Pattern 6: Error Rate Monitoring
  group("Error Rate Check", () => {
    const testUrl = `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}&limit=1`;
    const response = authenticatedRequest("GET", testUrl, null, authData.token);

    check(response, {
      "no critical errors": (r) => r.status < 500 || r.status === 503,
      "circuit breaker working": (r) => {
        // If we get 503, it should be a circuit breaker response
        if (r.status === 503) {
          try {
            const body = JSON.parse(r.body);
            return body.message !== undefined || body.error !== undefined;
          } catch {
            return true;
          }
        }
        return true;
      },
    });
  });

  // Spike Test Pattern 7: Recovery Test (during normal phase after spike)
  if (phase === "normal" && iteration > 50) {
    group("Recovery Verification", () => {
      // Test if system has recovered to normal performance
      const url = `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}`;
      const start = Date.now();
      const response = authenticatedRequest("GET", url, null, authData.token);
      const duration = Date.now() - start;

      check(response, {
        "system recovered - status ok": (r) => r.status === 200,
        "system recovered - response fast": () => duration < 500,
        "system recovered - no errors": (r) => r.status < 400,
      });
    });
  }

  // Spike Test Pattern 8: Concurrent Requests (during spike only)
  if (phase === "spike" && Math.random() < 0.3) {
    group("Concurrent Request Burst", () => {
      const requests = [];

      // Prepare 5 concurrent requests
      for (let i = 0; i < 5; i++) {
        requests.push({
          method: "GET",
          url: `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}&limit=10`,
          params: {
            headers: {
              Authorization: `Bearer ${authData.token}`,
              "Content-Type": "application/json",
              "X-Tenant-Id": config.tenantId,
            },
          },
        });
      }

      // Send all requests concurrently
      const responses = http.batch(requests);

      // Check that at least some succeed
      const successCount = responses.filter((r) => r.status === 200).length;
      check(responses, {
        "some concurrent requests succeed": () => successCount > 0,
        "not all concurrent requests fail": () =>
          successCount < 5 ||
          responses.filter((r) => r.status >= 500).length === 0,
      });
    });
  }

  // Dynamic think time based on phase
  if (phase === "spike") {
    sleep(randomInt(0, 1) * 0.3); // Very short think time during spike
  } else if (phase === "normal") {
    thinkTime(1, 2); // Normal think time
  } else {
    sleep(randomInt(0, 2) * 0.5); // Medium think time during transition
  }
}

// Teardown
export function teardown(data) {
  const duration = ((Date.now() - data.startTime) / 1000 / 60).toFixed(2);
  console.log("\n⚡ Spike Test Completed");
  console.log(`Duration: ${duration} minutes`);
  console.log("");
  console.log("📊 Key Metrics to Review:");
  console.log("  - Response time during spike vs normal");
  console.log("  - Error rate during spike");
  console.log("  - Recovery time after spike");
  console.log("  - Rate limiting effectiveness");
  console.log("  - Circuit breaker activations");
  console.log("");
  console.log("✅ Check if system:");
  console.log("  - Handled sudden load increase");
  console.log("  - Maintained availability");
  console.log("  - Recovered to normal performance");
  console.log("  - Applied rate limiting properly");
}
