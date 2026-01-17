/**
 * Smoke Test - SAHOOL Platform
 *
 * Purpose: Verify basic functionality with minimal load
 * Duration: 1 minute
 * VUs: 1
 *
 * Tests:
 * - Health checks
 * - Authentication flow
 * - Basic CRUD operations
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { config, smokeThresholds } from "../lib/config.js";
import {
  authenticate,
  authenticatedRequest,
  validateResponse,
  generateRandomField,
  thinkTime,
} from "../lib/helpers.js";

// Test configuration
export const options = {
  vus: 1,
  duration: "1m",
  thresholds: smokeThresholds,
  tags: {
    test_type: "smoke",
    environment: __ENV.ENVIRONMENT || "local",
  },
};

// Setup: runs once
export function setup() {
  console.log("🔥 Starting Smoke Test...");
  console.log(`Environment: ${__ENV.ENVIRONMENT || "local"}`);
  console.log(`Base URL: ${config.baseUrl}`);

  // Verify services are reachable
  const healthChecks = [
    { name: "Field Service", url: `${config.fieldServiceUrl}/healthz` },
    { name: "Weather Service", url: `${config.weatherUrl}/healthz` },
    { name: "Satellite Service", url: `${config.satelliteUrl}/healthz` },
  ];

  console.log("\n📋 Pre-flight health checks:");
  healthChecks.forEach((service) => {
    try {
      const res = http.get(service.url, { timeout: "5s" });
      const status = res.status === 200 ? "✅" : "❌";
      console.log(`${status} ${service.name}: ${res.status}`);
    } catch (e) {
      console.log(`❌ ${service.name}: unreachable`);
    }
  });

  console.log("\n🚀 Starting test execution...\n");
  return { timestamp: new Date().toISOString() };
}

// Main test function
export default function () {
  let authData;
  let fieldId;
  let operationId;

  // Group 1: Authentication
  group("Authentication", () => {
    authData = authenticate();

    check(authData, {
      "authentication successful": (data) => data.success === true,
      "token is present": (data) =>
        data.token !== null && data.token !== undefined,
      "userId is present": (data) => data.userId !== null,
      "tenantId is present": (data) => data.tenantId !== null,
    });

    sleep(0.5);
  });

  if (!authData || !authData.success) {
    console.error("❌ Authentication failed, aborting test");
    return;
  }

  // Group 2: Health Check
  group("Health Check", () => {
    const healthUrl = `${config.fieldServiceUrl}/healthz`;
    const response = http.get(healthUrl);

    check(response, {
      "health check status is 200": (r) => r.status === 200,
      "health check response time < 200ms": (r) => r.timings.duration < 200,
    });

    sleep(0.3);
  });

  // Group 3: Field List
  group("List Fields", () => {
    const url = `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}&limit=10`;
    const response = authenticatedRequest("GET", url, null, authData.token);

    const result = validateResponse(response, 200, "list fields");

    if (result.success && result.data) {
      check(result.data, {
        "fields list has items array": (data) =>
          Array.isArray(data.items) || Array.isArray(data.data),
      });
    }

    sleep(0.5);
  });

  // Group 4: Create Field
  group("Create Field", () => {
    const fieldData = generateRandomField(authData.tenantId);
    const url = `${config.fieldServiceUrl}/fields`;
    const response = authenticatedRequest(
      "POST",
      url,
      fieldData,
      authData.token,
    );

    const result = validateResponse(response, 201, "create field");

    if (result.success && result.data) {
      fieldId = result.data.id || result.data.field_id;

      check(result.data, {
        "created field has id": (data) =>
          data.id !== undefined || data.field_id !== undefined,
        "created field has name": (data) => data.name !== undefined,
        "created field has tenant_id": (data) => data.tenant_id !== undefined,
      });
    }

    sleep(1);
  });

  // Group 5: Get Field by ID
  if (fieldId) {
    group("Get Field by ID", () => {
      const url = `${config.fieldServiceUrl}/fields/${fieldId}`;
      const response = authenticatedRequest("GET", url, null, authData.token);

      const result = validateResponse(response, 200, "get field");

      if (result.success && result.data) {
        check(result.data, {
          "field id matches": (data) => (data.id || data.field_id) === fieldId,
          "field has geometry": (data) =>
            data.geometry !== undefined || data.boundary !== undefined,
        });
      }

      sleep(0.5);
    });
  }

  // Group 6: Create Operation
  if (fieldId) {
    group("Create Operation", () => {
      const operationData = {
        tenant_id: authData.tenantId,
        field_id: fieldId,
        operation_type: "irrigation",
        scheduled_date: new Date(Date.now() + 86400000).toISOString(), // tomorrow
        notes: "Smoke test operation",
      };

      const url = `${config.fieldServiceUrl}/operations`;
      const response = authenticatedRequest(
        "POST",
        url,
        operationData,
        authData.token,
      );

      const result = validateResponse(response, 201, "create operation");

      if (result.success && result.data) {
        operationId = result.data.id || result.data.operation_id;

        check(result.data, {
          "operation has id": (data) =>
            data.id !== undefined || data.operation_id !== undefined,
          "operation type matches": (data) =>
            data.operation_type === "irrigation",
        });
      }

      sleep(0.5);
    });
  }

  // Group 7: Weather Forecast
  group("Weather Forecast", () => {
    const url = `${config.weatherUrl}/v1/forecast/sanaa?days=3`;
    const response = authenticatedRequest("GET", url, null, authData.token);

    const result = validateResponse(response, 200, "weather forecast");

    if (result.success && result.data) {
      check(result.data, {
        "forecast has location_id": (data) => data.location_id !== undefined,
        "forecast has daily data": (data) =>
          data.daily_forecast !== undefined &&
          Array.isArray(data.daily_forecast),
      });
    }

    sleep(0.5);
  });

  // Group 8: Billing - Get Plans
  group("Billing Plans", () => {
    const url = `${config.billingUrl}/v1/plans?active_only=true`;
    const response = authenticatedRequest("GET", url, null, authData.token);

    const result = validateResponse(response, 200, "get plans");

    if (result.success && result.data) {
      check(result.data, {
        "plans list exists": (data) =>
          data.plans !== undefined && Array.isArray(data.plans),
        "plans list not empty": (data) => data.plans && data.plans.length > 0,
      });
    }

    sleep(0.5);
  });

  // Group 9: Cleanup - Delete Operation
  if (operationId) {
    group("Delete Operation", () => {
      const url = `${config.fieldServiceUrl}/operations/${operationId}`;
      const response = authenticatedRequest(
        "DELETE",
        url,
        null,
        authData.token,
      );

      check(response, {
        "operation deleted": (r) => r.status === 204 || r.status === 200,
      });

      sleep(0.3);
    });
  }

  // Group 10: Cleanup - Delete Field
  if (fieldId) {
    group("Delete Field", () => {
      const url = `${config.fieldServiceUrl}/fields/${fieldId}`;
      const response = authenticatedRequest(
        "DELETE",
        url,
        null,
        authData.token,
      );

      check(response, {
        "field deleted": (r) => r.status === 204 || r.status === 200,
      });

      sleep(0.3);
    });
  }

  // Think time between iterations
  thinkTime(1, 2);
}

// Teardown: runs once
export function teardown(data) {
  console.log("\n✅ Smoke Test Completed");
  console.log(`Started at: ${data.timestamp}`);
  console.log(`Ended at: ${new Date().toISOString()}`);
}
