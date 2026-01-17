/**
 * Load Test - SAHOOL Platform
 *
 * Purpose: Test system under expected production load
 * Duration: 10 minutes
 * VUs: 50 concurrent users
 *
 * Scenarios:
 * - User authentication
 * - Field management (CRUD)
 * - Weather data retrieval
 * - Satellite imagery analysis
 * - Equipment management
 * - Task creation and updates
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { config, loadThresholds } from "../lib/config.js";
import {
  authenticate,
  authenticatedRequest,
  validateResponse,
  generateRandomField,
  generateRandomOperation,
  generateRandomTask,
  generateRandomEquipment,
  createWeatherAnalysisRequest,
  createSatelliteAnalysisRequest,
  createIrrigationRequest,
  thinkTime,
  randomElement,
  randomInt,
  logIteration,
} from "../lib/helpers.js";

// Test configuration
export const options = {
  stages: [
    { duration: "2m", target: 10 }, // Ramp up to 10 users
    { duration: "3m", target: 50 }, // Ramp up to 50 users
    { duration: "3m", target: 50 }, // Stay at 50 users
    { duration: "2m", target: 0 }, // Ramp down to 0
  ],
  thresholds: loadThresholds,
  tags: {
    test_type: "load",
    environment: __ENV.ENVIRONMENT || "local",
  },
};

// Setup
export function setup() {
  console.log("⚡ Starting Load Test...");
  console.log("Configuration:");
  console.log(`  - Duration: 10 minutes`);
  console.log(`  - Peak VUs: 50`);
  console.log(`  - Target RPS: 50+`);
  console.log(`  - Environment: ${__ENV.ENVIRONMENT || "local"}`);
  console.log("");

  return { startTime: Date.now() };
}

// Main test function
export default function () {
  const iteration = __ITER;
  let authData;
  let fieldId;

  // Authenticate (70% of users)
  if (Math.random() < 0.7) {
    authData = authenticate();

    if (!authData || !authData.success) {
      console.error(`[VU ${__VU}] Authentication failed`);
      sleep(5);
      return;
    }
  } else {
    // Simulate unauthenticated/cached session
    authData = {
      success: true,
      token: "cached_token",
      userId: `user_${randomInt(1, 100)}`,
      tenantId: config.tenantId,
    };
  }

  logIteration(iteration, `VU ${__VU} starting iteration`);

  // Scenario 1: Field Management (60% of users)
  if (Math.random() < 0.6) {
    group("Field Management", () => {
      // List fields
      const listUrl = `${config.fieldServiceUrl}/fields?tenant_id=${authData.tenantId}&limit=20`;
      const listResponse = authenticatedRequest(
        "GET",
        listUrl,
        null,
        authData.token,
      );

      validateResponse(listResponse, 200, "list fields");
      sleep(randomInt(1, 2));

      // Create field (30% of field management users)
      if (Math.random() < 0.3) {
        const fieldData = generateRandomField(authData.tenantId);
        const createUrl = `${config.fieldServiceUrl}/fields`;
        const createResponse = authenticatedRequest(
          "POST",
          createUrl,
          fieldData,
          authData.token,
        );

        const result = validateResponse(createResponse, 201, "create field");

        if (result.success && result.data) {
          fieldId = result.data.id || result.data.field_id;
          sleep(1);

          // Update field (50% of created fields)
          if (Math.random() < 0.5 && fieldId) {
            const updateData = {
              name: `Updated ${fieldData.name}`,
              crop_type: randomElement(["wheat", "tomato", "corn"]),
            };
            const updateUrl = `${config.fieldServiceUrl}/fields/${fieldId}`;
            authenticatedRequest("PUT", updateUrl, updateData, authData.token);
            sleep(1);
          }
        }
      }

      thinkTime(0.5, 1.5);
    });
  }

  // Scenario 2: Weather Information (40% of users)
  if (Math.random() < 0.4) {
    group("Weather Forecast", () => {
      const locations = ["sanaa", "aden", "taiz", "hodeidah"];
      const location = randomElement(locations);
      const days = randomInt(3, 7);

      const url = `${config.weatherUrl}/v1/forecast/${location}?days=${days}`;
      const response = authenticatedRequest("GET", url, null, authData.token);

      const result = validateResponse(response, 200, "weather forecast");

      if (result.success && result.data) {
        check(result.data, {
          "has daily forecast": (d) => d.daily_forecast !== undefined,
          "forecast has correct days": (d) =>
            d.daily_forecast && d.daily_forecast.length <= days,
        });
      }

      thinkTime(1, 2);
    });
  }

  // Scenario 3: Satellite Imagery (20% of users)
  if (Math.random() < 0.2) {
    group("Satellite Analysis", () => {
      // Use existing field or create temporary one
      if (!fieldId) {
        const fieldData = generateRandomField(authData.tenantId);
        const createUrl = `${config.fieldServiceUrl}/fields`;
        const createResponse = authenticatedRequest(
          "POST",
          createUrl,
          fieldData,
          authData.token,
        );
        const result = validateResponse(
          createResponse,
          201,
          "create field for satellite",
        );

        if (result.success && result.data) {
          fieldId = result.data.id || result.data.field_id;
        }
      }

      if (fieldId) {
        const analysisRequest = createSatelliteAnalysisRequest(fieldId);
        const url = `${config.satelliteUrl}/v1/analyze`;
        const response = authenticatedRequest(
          "POST",
          url,
          analysisRequest,
          authData.token,
        );

        validateResponse(response, 200, "satellite analysis");
        sleep(2); // Satellite analysis takes longer
      }

      thinkTime(1, 3);
    });
  }

  // Scenario 4: Operations Management (35% of users)
  if (Math.random() < 0.35 && fieldId) {
    group("Field Operations", () => {
      // List operations
      const listUrl = `${config.fieldServiceUrl}/operations?field_id=${fieldId}&limit=10`;
      const listResponse = authenticatedRequest(
        "GET",
        listUrl,
        null,
        authData.token,
      );

      validateResponse(listResponse, 200, "list operations");
      sleep(1);

      // Create operation (50% of operation users)
      if (Math.random() < 0.5) {
        const operationData = generateRandomOperation(
          fieldId,
          authData.tenantId,
        );
        const createUrl = `${config.fieldServiceUrl}/operations`;
        const createResponse = authenticatedRequest(
          "POST",
          createUrl,
          operationData,
          authData.token,
        );

        const result = validateResponse(
          createResponse,
          201,
          "create operation",
        );

        if (result.success && result.data) {
          const operationId = result.data.id || result.data.operation_id;

          // Complete operation (30% of created operations)
          if (Math.random() < 0.3 && operationId) {
            const completeUrl = `${config.fieldServiceUrl}/operations/${operationId}/complete`;
            authenticatedRequest(
              "POST",
              completeUrl,
              { notes: "Load test completion" },
              authData.token,
            );
            sleep(0.5);
          }
        }
      }

      thinkTime(0.5, 1.5);
    });
  }

  // Scenario 5: Task Management (30% of users)
  if (Math.random() < 0.3) {
    group("Task Management", () => {
      // List tasks
      const listUrl = `${config.taskUrl}/api/v1/tasks?limit=20`;
      const listResponse = authenticatedRequest(
        "GET",
        listUrl,
        null,
        authData.token,
      );

      validateResponse(listResponse, 200, "list tasks");
      sleep(1);

      // Create task (40% of task users)
      if (Math.random() < 0.4 && fieldId) {
        const taskData = generateRandomTask(fieldId, authData.tenantId);
        const createUrl = `${config.taskUrl}/api/v1/tasks`;
        const createResponse = authenticatedRequest(
          "POST",
          createUrl,
          taskData,
          authData.token,
        );

        const result = validateResponse(createResponse, 201, "create task");

        if (result.success && result.data) {
          const taskId = result.data.task_id || result.data.id;

          // Start task (50% of created tasks)
          if (Math.random() < 0.5 && taskId) {
            const startUrl = `${config.taskUrl}/api/v1/tasks/${taskId}/start`;
            authenticatedRequest("POST", startUrl, {}, authData.token);
            sleep(0.5);
          }
        }
      }

      thinkTime(0.5, 1.5);
    });
  }

  // Scenario 6: Equipment Management (15% of users)
  if (Math.random() < 0.15) {
    group("Equipment Management", () => {
      // List equipment
      const listUrl = `${config.equipmentUrl}/api/v1/equipment?limit=20`;
      const listResponse = authenticatedRequest(
        "GET",
        listUrl,
        null,
        authData.token,
      );

      validateResponse(listResponse, 200, "list equipment");
      sleep(1);

      // Create equipment (30% of equipment users)
      if (Math.random() < 0.3) {
        const equipmentData = generateRandomEquipment(
          fieldId,
          authData.tenantId,
        );
        const createUrl = `${config.equipmentUrl}/api/v1/equipment`;
        const createResponse = authenticatedRequest(
          "POST",
          createUrl,
          equipmentData,
          authData.token,
        );

        const result = validateResponse(
          createResponse,
          201,
          "create equipment",
        );

        if (result.success && result.data) {
          const equipmentId = result.data.equipment_id || result.data.id;

          // Update telemetry (60% of created equipment)
          if (Math.random() < 0.6 && equipmentId) {
            const telemetryUrl = `${config.equipmentUrl}/api/v1/equipment/${equipmentId}/telemetry`;
            const telemetryData = {
              fuel_percent: randomInt(30, 100),
              hours: randomInt(100, 5000) + Math.random(),
              lat: 15.3694 + (Math.random() - 0.5) * 0.1,
              lon: 44.191 + (Math.random() - 0.5) * 0.1,
            };
            authenticatedRequest(
              "POST",
              telemetryUrl,
              telemetryData,
              authData.token,
            );
            sleep(0.5);
          }
        }
      }

      thinkTime(0.5, 1.5);
    });
  }

  // Scenario 7: Irrigation Smart Service (25% of users)
  if (Math.random() < 0.25 && fieldId) {
    group("Irrigation Calculation", () => {
      const irrigationRequest = createIrrigationRequest(fieldId);
      const url = `${config.fieldServiceUrl}/v1/calculate`;
      const response = authenticatedRequest(
        "POST",
        url,
        irrigationRequest,
        authData.token,
      );

      validateResponse(response, 200, "irrigation calculation");

      thinkTime(1, 2);
    });
  }

  // Scenario 8: Billing & Quota Check (10% of users)
  if (Math.random() < 0.1) {
    group("Billing Operations", () => {
      // Get quota
      const quotaUrl = `${config.billingUrl}/v1/tenants/${authData.tenantId}/quota`;
      const quotaResponse = authenticatedRequest(
        "GET",
        quotaUrl,
        null,
        authData.token,
      );

      const result = validateResponse(quotaResponse, 200, "get quota");

      if (result.success && result.data) {
        check(result.data, {
          "quota has usage data": (d) => d.usage !== undefined,
          "quota has plan info": (d) => d.plan !== undefined,
        });
      }

      sleep(1);

      // Get plans (20% of billing users)
      if (Math.random() < 0.2) {
        const plansUrl = `${config.billingUrl}/v1/plans`;
        authenticatedRequest("GET", plansUrl, null, authData.token);
        sleep(0.5);
      }

      thinkTime(0.5, 1);
    });
  }

  // Random think time between user actions
  thinkTime(1, 3);
}

// Teardown
export function teardown(data) {
  const duration = ((Date.now() - data.startTime) / 1000).toFixed(2);
  console.log("\n✅ Load Test Completed");
  console.log(`Duration: ${duration} seconds`);
  console.log("Check the summary for detailed metrics.");
}
