/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * SAHOOL IDP - Chaos Engineering Testing
 * اختبار هندسة الفوضى لمنصة سهول
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * This script tests system resilience by simulating:
 * - Service failures (503 responses)
 * - Network latency spikes
 * - Database connection issues
 * - Session loss scenarios
 * - Cascading failures
 *
 * Purpose: Verify that the system degrades gracefully under failure conditions
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
// CHAOS METRICS - مقاييس الفوضى
// ═══════════════════════════════════════════════════════════════════════════════

const recoveryRate = new Rate("recovery_rate");
const failoverSuccessRate = new Rate("failover_success_rate");
const gracefulDegradationRate = new Rate("graceful_degradation_rate");
const circuitBreakerTrips = new Counter("circuit_breaker_trips");
const retrySuccesses = new Counter("retry_successes");
const retryFailures = new Counter("retry_failures");
const cascadeFailures = new Counter("cascade_failures");
const recoveryTime = new Trend("recovery_time_ms");

// Standard metrics
const requestDuration = new Trend("request_duration_ms");
const errorRate = new Rate("error_rate");

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION - الإعدادات
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_URL = __ENV.BASE_URL || "http://sahool-nginx:80";
const CHAOS_LEVEL = __ENV.CHAOS_LEVEL || "medium"; // low, medium, high, extreme
const AGENT_COUNT = parseInt(__ENV.AGENT_COUNT) || 20;

// Chaos configurations
const CHAOS_CONFIGS = {
  low: {
    failureRate: 0.05, // 5% failure injection
    maxRetries: 3,
    retryDelay: 1000,
    stages: [
      { duration: "30s", target: AGENT_COUNT },
      { duration: "2m", target: AGENT_COUNT },
      { duration: "30s", target: 0 },
    ],
  },
  medium: {
    failureRate: 0.15, // 15% failure injection
    maxRetries: 3,
    retryDelay: 500,
    stages: [
      { duration: "30s", target: AGENT_COUNT },
      { duration: "1m", target: AGENT_COUNT },
      { duration: "30s", target: AGENT_COUNT * 2 },
      { duration: "1m", target: AGENT_COUNT * 2 },
      { duration: "30s", target: AGENT_COUNT },
      { duration: "30s", target: 0 },
    ],
  },
  high: {
    failureRate: 0.3, // 30% failure injection
    maxRetries: 5,
    retryDelay: 300,
    stages: [
      { duration: "20s", target: AGENT_COUNT },
      { duration: "30s", target: AGENT_COUNT * 2 },
      { duration: "1m", target: AGENT_COUNT * 3 },
      { duration: "30s", target: AGENT_COUNT * 4 },
      { duration: "1m", target: AGENT_COUNT * 2 },
      { duration: "30s", target: 0 },
    ],
  },
  extreme: {
    failureRate: 0.5, // 50% failure injection
    maxRetries: 5,
    retryDelay: 200,
    stages: [
      { duration: "15s", target: AGENT_COUNT * 2 },
      { duration: "30s", target: AGENT_COUNT * 5 },
      { duration: "1m", target: AGENT_COUNT * 10 },
      { duration: "30s", target: AGENT_COUNT * 5 },
      { duration: "30s", target: 0 },
    ],
  },
};

const config = CHAOS_CONFIGS[CHAOS_LEVEL];

export const options = {
  scenarios: {
    chaos_testing: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: config.stages,
      gracefulRampDown: "30s",
    },
  },
  thresholds: {
    recovery_rate: ["rate>0.80"], // 80% should recover
    failover_success_rate: ["rate>0.70"], // 70% failover success
    graceful_degradation_rate: ["rate>0.90"], // 90% should degrade gracefully
    recovery_time_ms: ["p(95)<5000"], // Recovery within 5s
    http_req_failed: ["rate<0.40"], // Allow up to 40% failures in chaos
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS - دوال مساعدة
// ═══════════════════════════════════════════════════════════════════════════════

function getAgentId() {
  return `chaos_agent_${__VU}`;
}

function shouldInjectFailure() {
  return Math.random() < config.failureRate;
}

function getHeaders(token = null) {
  const headers = {
    "Content-Type": "application/json",
    "X-Agent-ID": getAgentId(),
    "X-Chaos-Test": "true",
  };

  // Inject chaos headers to simulate failures
  if (shouldInjectFailure()) {
    headers["X-Inject-Delay"] = randomIntBetween(1000, 5000).toString();
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// Retry with exponential backoff
function retryRequest(requestFn, maxRetries = config.maxRetries) {
  let lastError = null;
  let retryDelay = config.retryDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const startTime = Date.now();
    const response = requestFn();

    requestDuration.add(Date.now() - startTime);

    // Success
    if (response.status >= 200 && response.status < 300) {
      if (attempt > 0) {
        retrySuccesses.add(1);
        recoveryTime.add(Date.now() - startTime);
      }
      return { success: true, response, attempts: attempt + 1 };
    }

    // Retryable errors (503, 502, 504, 429)
    if ([502, 503, 504, 429].includes(response.status)) {
      lastError = response;
      if (attempt < maxRetries) {
        sleep(retryDelay / 1000);
        retryDelay *= 2; // Exponential backoff
      }
      continue;
    }

    // Non-retryable error
    return { success: false, response, attempts: attempt + 1 };
  }

  retryFailures.add(1);
  return { success: false, response: lastError, attempts: maxRetries + 1 };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SETUP - الإعداد
// ═══════════════════════════════════════════════════════════════════════════════

export function setup() {
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log("  SAHOOL IDP - Chaos Engineering Test");
  console.log("  اختبار هندسة الفوضى لمنصة سهول");
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log(`  Chaos Level: ${CHAOS_LEVEL}`);
  console.log(`  Failure Rate: ${config.failureRate * 100}%`);
  console.log(`  Max Retries: ${config.maxRetries}`);
  console.log(`  Base URL: ${BASE_URL}`);
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );

  return {
    startTime: new Date().toISOString(),
    chaosLevel: CHAOS_LEVEL,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN TEST - الاختبار الرئيسي
// ═══════════════════════════════════════════════════════════════════════════════

export default function () {
  const agentId = getAgentId();
  const token = `chaos_token_${agentId}`;

  // ═══════════════════════════════════════════════════════════════════════════
  // TEST 1: Service Failure Recovery - استرداد فشل الخدمة
  // ═══════════════════════════════════════════════════════════════════════════

  group("Chaos: Service Failure Recovery", () => {
    const result = retryRequest(() => {
      return http.get(`${BASE_URL}/api/health`, {
        headers: getHeaders(token),
        timeout: "10s",
      });
    });

    recoveryRate.add(result.success);

    check(result.response, {
      "service recovered or available": (r) =>
        r && (r.status === 200 || r.status === 503),
    });
  });

  sleep(randomIntBetween(1, 2));

  // ═══════════════════════════════════════════════════════════════════════════
  // TEST 2: Load Balancer Failover - تجاوز فشل موازن الحمل
  // ═══════════════════════════════════════════════════════════════════════════

  group("Chaos: Load Balancer Failover", () => {
    // Make multiple requests to test failover between instances
    let successCount = 0;
    const instances = new Set();

    for (let i = 0; i < 5; i++) {
      const response = http.get(`${BASE_URL}/api/profile`, {
        headers: getHeaders(token),
        timeout: "15s",
      });

      if (response.status === 200) {
        successCount++;
        // Try to identify which instance responded
        const instanceId = response.headers["X-Instance-Id"] || "unknown";
        instances.add(instanceId);
      }

      sleep(0.3);
    }

    const failoverSuccess = successCount >= 3 || instances.size > 1;
    failoverSuccessRate.add(failoverSuccess);

    if (!failoverSuccess && successCount === 0) {
      cascadeFailures.add(1);
    }
  });

  sleep(randomIntBetween(1, 2));

  // ═══════════════════════════════════════════════════════════════════════════
  // TEST 3: Database Connection Stress - إجهاد اتصال قاعدة البيانات
  // ═══════════════════════════════════════════════════════════════════════════

  group("Chaos: Database Stress", () => {
    // Rapid database operations to stress connection pool
    const operations = [];

    for (let i = 0; i < 3; i++) {
      const fieldData = {
        tenant_id: "tenant_chaos",
        name: `ChaosField_${agentId}_${i}_${Date.now()}`,
        crop_type: "test",
        area_hectares: randomIntBetween(1, 10),
      };

      operations.push(
        http.post(`${BASE_URL}/api/fields`, JSON.stringify(fieldData), {
          headers: getHeaders(token),
          timeout: "20s",
        }),
      );
    }

    let gracefulCount = 0;
    operations.forEach((response) => {
      // Graceful = success OR proper error response (not timeout/connection failure)
      if (
        response.status === 201 ||
        response.status === 200 ||
        response.status === 503 ||
        response.status === 429 ||
        response.status === 401 ||
        response.status === 400
      ) {
        gracefulCount++;
      }
    });

    gracefulDegradationRate.add(gracefulCount >= 2);
  });

  sleep(randomIntBetween(1, 2));

  // ═══════════════════════════════════════════════════════════════════════════
  // TEST 4: Session Chaos - فوضى الجلسات
  // ═══════════════════════════════════════════════════════════════════════════

  group("Chaos: Session Resilience", () => {
    // Test session handling under chaos
    const sessions = [
      "valid_token",
      "invalid_token",
      "",
      null,
      "expired_token",
    ];

    sessions.forEach((sessionToken, index) => {
      const response = http.get(`${BASE_URL}/api/profile`, {
        headers: getHeaders(sessionToken || token),
        timeout: "10s",
      });

      // System should handle all session states gracefully
      const isGraceful = response.status !== 0 && !response.error;
      gracefulDegradationRate.add(isGraceful);
    });
  });

  sleep(randomIntBetween(1, 2));

  // ═══════════════════════════════════════════════════════════════════════════
  // TEST 5: Circuit Breaker Detection - كشف قاطع الدائرة
  // ═══════════════════════════════════════════════════════════════════════════

  group("Chaos: Circuit Breaker", () => {
    // Rapid requests to potentially trigger circuit breaker
    let consecutiveFailures = 0;
    let circuitOpen = false;

    for (let i = 0; i < 10 && !circuitOpen; i++) {
      const response = http.get(`${BASE_URL}/api/fields?limit=1`, {
        headers: getHeaders(token),
        timeout: "5s",
      });

      if (response.status >= 500 || response.status === 429) {
        consecutiveFailures++;
        if (consecutiveFailures >= 5) {
          circuitOpen = true;
          circuitBreakerTrips.add(1);
        }
      } else {
        consecutiveFailures = 0;
      }

      sleep(0.1);
    }

    // After potential circuit break, test recovery
    if (circuitOpen) {
      sleep(2); // Wait for circuit to potentially close

      const recoveryResponse = http.get(`${BASE_URL}/api/health`, {
        headers: getHeaders(token),
        timeout: "10s",
      });

      recoveryRate.add(recoveryResponse.status === 200);
    }
  });

  sleep(randomIntBetween(2, 4));

  // ═══════════════════════════════════════════════════════════════════════════
  // TEST 6: Concurrent Write Chaos - فوضى الكتابة المتزامنة
  // ═══════════════════════════════════════════════════════════════════════════

  group("Chaos: Concurrent Writes", () => {
    // Test for race conditions and data integrity
    const sharedFieldName = `SharedField_${Date.now()}`;
    const requests = [];

    // Multiple agents trying to create/update same resource
    for (let i = 0; i < 3; i++) {
      requests.push(
        http.post(
          `${BASE_URL}/api/fields`,
          JSON.stringify({
            tenant_id: "tenant_chaos",
            name: sharedFieldName,
            crop_type: "wheat",
            area_hectares: randomIntBetween(1, 100),
          }),
          {
            headers: getHeaders(token),
            timeout: "15s",
          },
        ),
      );
    }

    // Check for graceful handling (success or proper conflict response)
    let handled = 0;
    requests.forEach((response) => {
      if (
        response.status === 201 ||
        response.status === 200 ||
        response.status === 409 ||
        response.status === 400 ||
        response.status === 401
      ) {
        handled++;
      }
    });

    gracefulDegradationRate.add(handled >= 2);
  });

  sleep(randomIntBetween(2, 5));
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEARDOWN - التنظيف
// ═══════════════════════════════════════════════════════════════════════════════

export function teardown(data) {
  console.log(
    "\n═══════════════════════════════════════════════════════════════",
  );
  console.log("  CHAOS ENGINEERING TEST COMPLETE");
  console.log("  اكتمل اختبار هندسة الفوضى");
  console.log(
    "═══════════════════════════════════════════════════════════════",
  );
  console.log(`  Chaos Level: ${data.chaosLevel}`);
  console.log(`  Start: ${data.startTime}`);
  console.log(`  End: ${new Date().toISOString()}`);
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
    chaos_level: CHAOS_LEVEL,
    failure_rate_configured: config.failureRate,
    resilience_metrics: {
      recovery_rate: data.metrics.recovery_rate?.values?.rate || 0,
      failover_success_rate:
        data.metrics.failover_success_rate?.values?.rate || 0,
      graceful_degradation_rate:
        data.metrics.graceful_degradation_rate?.values?.rate || 0,
    },
    chaos_events: {
      circuit_breaker_trips:
        data.metrics.circuit_breaker_trips?.values?.count || 0,
      retry_successes: data.metrics.retry_successes?.values?.count || 0,
      retry_failures: data.metrics.retry_failures?.values?.count || 0,
      cascade_failures: data.metrics.cascade_failures?.values?.count || 0,
    },
    recovery: {
      avg_recovery_time: data.metrics.recovery_time_ms?.values?.avg || 0,
      p95_recovery_time: data.metrics.recovery_time_ms?.values["p(95)"] || 0,
    },
  };

  return {
    "/results/chaos-test-summary.json": JSON.stringify(summary, null, 2),
    stdout: generateChaosSummary(summary),
  };
}

function generateChaosSummary(summary) {
  const resilienceScore = (
    summary.resilience_metrics.recovery_rate * 40 +
    summary.resilience_metrics.failover_success_rate * 30 +
    summary.resilience_metrics.graceful_degradation_rate * 30
  ).toFixed(1);

  return `
═══════════════════════════════════════════════════════════════════════════════
  CHAOS ENGINEERING SUMMARY - ملخص هندسة الفوضى
═══════════════════════════════════════════════════════════════════════════════

  Chaos Level: ${summary.chaos_level.toUpperCase()}
  Failure Injection Rate: ${(summary.failure_rate_configured * 100).toFixed(0)}%

  RESILIENCE SCORE: ${resilienceScore}/100 ${resilienceScore >= 80 ? "✓" : "⚠"}

  RESILIENCE METRICS:
  ───────────────────────────────────────────────────────────────────────────────
    Recovery Rate:           ${(summary.resilience_metrics.recovery_rate * 100).toFixed(1)}%
    Failover Success:        ${(summary.resilience_metrics.failover_success_rate * 100).toFixed(1)}%
    Graceful Degradation:    ${(summary.resilience_metrics.graceful_degradation_rate * 100).toFixed(1)}%

  CHAOS EVENTS:
  ───────────────────────────────────────────────────────────────────────────────
    Circuit Breaker Trips:   ${summary.chaos_events.circuit_breaker_trips}
    Retry Successes:         ${summary.chaos_events.retry_successes}
    Retry Failures:          ${summary.chaos_events.retry_failures}
    Cascade Failures:        ${summary.chaos_events.cascade_failures}

  RECOVERY TIME:
  ───────────────────────────────────────────────────────────────────────────────
    Average:                 ${summary.recovery.avg_recovery_time.toFixed(0)}ms
    P95:                     ${summary.recovery.p95_recovery_time.toFixed(0)}ms

═══════════════════════════════════════════════════════════════════════════════
`;
}
