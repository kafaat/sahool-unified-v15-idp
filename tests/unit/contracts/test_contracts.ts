/**
 * SAHOOL Unified API Contracts - Unit Tests
 * اختبارات وحدة العقود الموحدة
 *
 * Validates contract integrity, consistency, and correctness.
 * Run: npx tsx tests/unit/contracts/test_contracts.ts
 *
 * @version 16.0.0
 */

import {
  CONTRACT_VERSION,
  SERVICE_PORTS,
  SERVICE_PORT_ALIASES,
  SERVICE_REGISTRY,
  ERROR_CODES,
  ERROR_MESSAGES,
  getErrorMessage,
  getLocalizedError,
  httpStatusToErrorCode,
  isRetryable,
  AUTH_ENDPOINTS,
  FIELD_ENDPOINTS,
  WEATHER_ENDPOINTS,
  CROP_HEALTH_ENDPOINTS,
  IRRIGATION_ENDPOINTS,
  TASK_ENDPOINTS,
  EQUIPMENT_ENDPOINTS,
  NOTIFICATION_ENDPOINTS,
  IOT_ENDPOINTS,
  BILLING_ENDPOINTS,
  AUDIT_ENDPOINTS,
  HEALTH_ENDPOINTS,
  VISION_ENDPOINTS,
  TERRAIN_ENDPOINTS,
  ADVISORY_ENDPOINTS,
  INDICATOR_ENDPOINTS,
  CHAT_ENDPOINTS,
  YIELD_ENDPOINTS,
  SOIL_ENDPOINTS,
  DRONE_ENDPOINTS,
  INVENTORY_ENDPOINTS,
  TRACEABILITY_ENDPOINTS,
  PUBLIC_ENDPOINTS,
  buildUrl,
  API_PREFIX,
} from "../../../packages/shared-types/src/contracts/index";

// ─────────────────────────────────────────────────────────────────────────────
// Test Utilities
// ─────────────────────────────────────────────────────────────────────────────

let passed = 0;
let failed = 0;

function assert(condition: boolean, message: string): void {
  if (condition) {
    passed++;
  } else {
    failed++;
    console.error(`  ❌ FAIL: ${message}`);
  }
}

function section(name: string): void {
  console.log(`\n── ${name} ──`);
}

// ─────────────────────────────────────────────────────────────────────────────
// 1. CONTRACT_VERSION
// ─────────────────────────────────────────────────────────────────────────────
section("CONTRACT_VERSION");

assert(typeof CONTRACT_VERSION === "string", "CONTRACT_VERSION should be a string");
assert(/^\d+\.\d+\.\d+$/.test(CONTRACT_VERSION), `CONTRACT_VERSION should be semver: ${CONTRACT_VERSION}`);
console.log(`  Contract version: ${CONTRACT_VERSION}`);

// ─────────────────────────────────────────────────────────────────────────────
// 2. SERVICE_PORTS - Uniqueness & Range
// ─────────────────────────────────────────────────────────────────────────────
section("SERVICE_PORTS - Uniqueness & Range");

const allPorts = Object.entries(SERVICE_PORTS);

// Infrastructure ports (gateways, proxies) may share ports with services they front
// Deprecated ports are aliases that intentionally share a port with their replacement
const INFRA_PORTS = ["KONG_GATEWAY", "KONG_ADMIN"];
const DEPRECATED_PORTS = ["WECHAT"];
const EXCLUDED_PORTS = [...INFRA_PORTS, ...DEPRECATED_PORTS];
const servicePorts = allPorts.filter(([name]) => !EXCLUDED_PORTS.includes(name));
const servicePortValues = servicePorts.map(([, v]) => v);
const uniqueServicePorts = new Set(servicePortValues);

assert(allPorts.length > 50, `Should have 50+ ports, got ${allPorts.length}`);
assert(
  uniqueServicePorts.size === servicePortValues.length,
  `All service ports should be unique (excluding infra). Found ${servicePortValues.length - uniqueServicePorts.size} duplicates`,
);

// Detect duplicate ports (informational for infra ports)
const portMap = new Map<number, string[]>();
for (const [name, port] of allPorts) {
  if (!portMap.has(port)) portMap.set(port, []);
  portMap.get(port)!.push(name);
}
for (const [port, names] of portMap) {
  if (names.length > 1) {
    const isInfraOverlap = names.some((n) => INFRA_PORTS.includes(n));
    if (isInfraOverlap) {
      console.log(`  ℹ️  Port ${port} shared (infra overlap): ${names.join(", ")}`);
    } else {
      console.error(`  ⚠️  Port ${port} used by: ${names.join(", ")}`);
    }
  }
}

// All ports in valid range
for (const [name, port] of allPorts) {
  assert(port >= 1024 && port <= 65535, `${name} port ${port} should be in 1024-65535`);
}

// Key ports sanity check
assert(SERVICE_PORTS.FIELD_MANAGEMENT === 3000, "FIELD_MANAGEMENT should be 3000");
assert(SERVICE_PORTS.USER_SERVICE === 3025, "USER_SERVICE should be 3025");
assert(SERVICE_PORTS.WEATHER === 8092, "WEATHER should be 8092");
assert(SERVICE_PORTS.ADVISORY === 8093, "ADVISORY should be 8093");
assert(SERVICE_PORTS.NOTIFICATIONS === 8110, "NOTIFICATIONS should be 8110");

console.log(`  ✓ ${allPorts.length} ports validated, all unique`);

// ─────────────────────────────────────────────────────────────────────────────
// 3. SERVICE_PORT_ALIASES - Backward Compatibility
// ─────────────────────────────────────────────────────────────────────────────
section("SERVICE_PORT_ALIASES");

const aliases = Object.entries(SERVICE_PORT_ALIASES);
assert(aliases.length > 10, `Should have aliases, got ${aliases.length}`);

// Every alias value must exist in SERVICE_PORTS
for (const [alias, port] of aliases) {
  assert(
    servicePortValues.includes(port) || Object.values(SERVICE_PORTS).includes(port),
    `Alias '${alias}' points to port ${port} which is not in SERVICE_PORTS`,
  );
}

// Key aliases
assert(SERVICE_PORT_ALIASES.auth === SERVICE_PORTS.USER_SERVICE, "auth alias should point to USER_SERVICE");
assert(SERVICE_PORT_ALIASES.fieldCore === SERVICE_PORTS.FIELD_MANAGEMENT, "fieldCore alias should point to FIELD_MANAGEMENT");
assert(SERVICE_PORT_ALIASES.satellite === SERVICE_PORTS.VEGETATION_ANALYSIS, "satellite alias should point to VEGETATION_ANALYSIS");

console.log(`  ✓ ${aliases.length} aliases validated`);

// ─────────────────────────────────────────────────────────────────────────────
// 4. ERROR_CODES & ERROR_MESSAGES
// ─────────────────────────────────────────────────────────────────────────────
section("ERROR_CODES & ERROR_MESSAGES");

const errorCodeEntries = Object.entries(ERROR_CODES);
assert(errorCodeEntries.length > 20, `Should have 20+ error codes, got ${errorCodeEntries.length}`);

// Every ERROR_CODE should have a corresponding ERROR_MESSAGE
for (const [name, code] of errorCodeEntries) {
  // Skip vision-specific codes that use numeric E-codes
  if (code.startsWith("E")) continue;

  const msg = ERROR_MESSAGES[code];
  assert(msg !== undefined, `ERROR_CODE ${name} (${code}) missing from ERROR_MESSAGES`);

  if (msg) {
    assert(typeof msg.en === "string" && msg.en.length > 0, `${code}: English message should not be empty`);
    assert(typeof msg.ar === "string" && msg.ar.length > 0, `${code}: Arabic message should not be empty`);
    assert(typeof msg.httpStatus === "number", `${code}: httpStatus should be a number`);
    assert(typeof msg.retryable === "boolean", `${code}: retryable should be a boolean`);
  }
}

// Helper functions
const unauthorizedMsg = getErrorMessage("UNAUTHORIZED");
assert(unauthorizedMsg.httpStatus === 401, "UNAUTHORIZED httpStatus should be 401");
assert(unauthorizedMsg.en.length > 0, "UNAUTHORIZED should have English message");
assert(unauthorizedMsg.ar.length > 0, "UNAUTHORIZED should have Arabic message");

const localizedEn = getLocalizedError("FORBIDDEN", "en");
const localizedAr = getLocalizedError("FORBIDDEN", "ar");
assert(localizedEn.length > 0, "getLocalizedError should return English");
assert(localizedAr.length > 0, "getLocalizedError should return Arabic");
assert(localizedEn !== localizedAr, "English and Arabic messages should differ");

// httpStatusToErrorCode
assert(httpStatusToErrorCode(401) === ERROR_CODES.UNAUTHORIZED, "401 → UNAUTHORIZED");
assert(httpStatusToErrorCode(403) === ERROR_CODES.FORBIDDEN, "403 → FORBIDDEN");
assert(httpStatusToErrorCode(404) === ERROR_CODES.NOT_FOUND, "404 → NOT_FOUND");
assert(httpStatusToErrorCode(429) === ERROR_CODES.RATE_LIMITED, "429 → RATE_LIMITED");
assert(httpStatusToErrorCode(500) === ERROR_CODES.SERVER_ERROR, "500 → SERVER_ERROR");
assert(httpStatusToErrorCode(503) === ERROR_CODES.SERVICE_UNAVAILABLE, "503 → SERVICE_UNAVAILABLE");

// Retryable
assert(isRetryable("NETWORK_ERROR") === true, "NETWORK_ERROR should be retryable");
assert(isRetryable("TIMEOUT") === true, "TIMEOUT should be retryable");
assert(isRetryable("UNAUTHORIZED") === false, "UNAUTHORIZED should NOT be retryable");
assert(isRetryable("FORBIDDEN") === false, "FORBIDDEN should NOT be retryable");

// Unknown code fallback
const unknownMsg = getErrorMessage("NONEXISTENT_CODE_123");
assert(unknownMsg.code === ERROR_CODES.UNKNOWN, "Unknown code should fallback to UNKNOWN");

console.log(`  ✓ ${errorCodeEntries.length} error codes validated`);

// ─────────────────────────────────────────────────────────────────────────────
// 5. API Endpoints - Format & Consistency
// ─────────────────────────────────────────────────────────────────────────────
section("API Endpoints - Format");

assert(API_PREFIX === "/api/v1", `API_PREFIX should be /api/v1, got ${API_PREFIX}`);

// Collect all endpoint groups
const endpointGroups: Record<string, Record<string, string>> = {
  AUTH: AUTH_ENDPOINTS,
  FIELD: FIELD_ENDPOINTS,
  WEATHER: WEATHER_ENDPOINTS,
  CROP_HEALTH: CROP_HEALTH_ENDPOINTS,
  IRRIGATION: IRRIGATION_ENDPOINTS,
  TASK: TASK_ENDPOINTS,
  EQUIPMENT: EQUIPMENT_ENDPOINTS,
  NOTIFICATION: NOTIFICATION_ENDPOINTS,
  IOT: IOT_ENDPOINTS,
  BILLING: BILLING_ENDPOINTS,
  AUDIT: AUDIT_ENDPOINTS,
  VISION: VISION_ENDPOINTS,
  TERRAIN: TERRAIN_ENDPOINTS,
  ADVISORY: ADVISORY_ENDPOINTS,
  INDICATOR: INDICATOR_ENDPOINTS,
  CHAT: CHAT_ENDPOINTS,
  YIELD: YIELD_ENDPOINTS,
  SOIL: SOIL_ENDPOINTS,
  DRONE: DRONE_ENDPOINTS,
  INVENTORY: INVENTORY_ENDPOINTS,
  TRACEABILITY: TRACEABILITY_ENDPOINTS,
};

let totalEndpoints = 0;
const allEndpointPaths: string[] = [];

for (const [groupName, endpoints] of Object.entries(endpointGroups)) {
  const entries = Object.entries(endpoints);
  totalEndpoints += entries.length;

  for (const [name, path] of entries) {
    // All paths should start with /api/v1/
    assert(
      path.startsWith("/api/v1/"),
      `${groupName}.${name}: path should start with /api/v1/, got: ${path}`,
    );

    // No double slashes
    assert(!path.includes("//"), `${groupName}.${name}: path should not have double slashes`);

    // No trailing slash
    assert(!path.endsWith("/"), `${groupName}.${name}: path should not have trailing slash`);

    allEndpointPaths.push(path);
  }
}

assert(totalEndpoints > 150, `Should have 150+ endpoints, got ${totalEndpoints}`);
console.log(`  ✓ ${totalEndpoints} endpoints validated across ${Object.keys(endpointGroups).length} groups`);

// ─────────────────────────────────────────────────────────────────────────────
// 6. HEALTH_ENDPOINTS
// ─────────────────────────────────────────────────────────────────────────────
section("HEALTH_ENDPOINTS");

assert(HEALTH_ENDPOINTS.LIVENESS === "/healthz", "LIVENESS should be /healthz");
assert(HEALTH_ENDPOINTS.READINESS === "/readyz", "READINESS should be /readyz");
assert(HEALTH_ENDPOINTS.HEALTH === "/health", "HEALTH should be /health");
assert(HEALTH_ENDPOINTS.METRICS === "/metrics", "METRICS should be /metrics");

console.log(`  ✓ 4 health endpoints validated`);

// ─────────────────────────────────────────────────────────────────────────────
// 7. PUBLIC_ENDPOINTS
// ─────────────────────────────────────────────────────────────────────────────
section("PUBLIC_ENDPOINTS");

assert(Array.isArray(PUBLIC_ENDPOINTS), "PUBLIC_ENDPOINTS should be an array");
assert(PUBLIC_ENDPOINTS.length > 5, `Should have 5+ public endpoints, got ${PUBLIC_ENDPOINTS.length}`);
assert(PUBLIC_ENDPOINTS.includes(AUTH_ENDPOINTS.LOGIN), "LOGIN should be public");
assert(PUBLIC_ENDPOINTS.includes(AUTH_ENDPOINTS.REGISTER), "REGISTER should be public");
assert(PUBLIC_ENDPOINTS.includes(HEALTH_ENDPOINTS.LIVENESS), "LIVENESS should be public");

console.log(`  ✓ ${PUBLIC_ENDPOINTS.length} public endpoints validated`);

// ─────────────────────────────────────────────────────────────────────────────
// 8. buildUrl Helper
// ─────────────────────────────────────────────────────────────────────────────
section("buildUrl Helper");

assert(
  buildUrl("/api/v1/fields/{fieldId}", { fieldId: "abc-123" }) === "/api/v1/fields/abc-123",
  "buildUrl should replace single param",
);

assert(
  buildUrl("/api/v1/{domain}/{id}", { domain: "tasks", id: "t-1" }) === "/api/v1/tasks/t-1",
  "buildUrl should replace multiple params",
);

// URL encoding
assert(
  buildUrl("/api/v1/fields/{fieldId}", { fieldId: "a b" }) === "/api/v1/fields/a%20b",
  "buildUrl should URL-encode param values",
);

// FIELD_ENDPOINTS.GET integration
assert(
  buildUrl(FIELD_ENDPOINTS.GET, { fieldId: "f-001" }) === "/api/v1/fields/f-001",
  "buildUrl with FIELD_ENDPOINTS.GET",
);

// TASK_ENDPOINTS.GET integration
assert(
  buildUrl(TASK_ENDPOINTS.GET, { taskId: "task-xyz" }) === "/api/v1/tasks/task-xyz",
  "buildUrl with TASK_ENDPOINTS.GET",
);

console.log(`  ✓ buildUrl helper validated`);

// ─────────────────────────────────────────────────────────────────────────────
// 9. SERVICE_REGISTRY Metadata
// ─────────────────────────────────────────────────────────────────────────────
section("SERVICE_REGISTRY");

if (SERVICE_REGISTRY) {
  const registryEntries = Object.entries(SERVICE_REGISTRY);
  assert(registryEntries.length > 0, "SERVICE_REGISTRY should not be empty");

  for (const [serviceName, info] of registryEntries) {
    assert(typeof serviceName === "string" && serviceName.length > 0, `Registry key should be a non-empty string`);
    assert(typeof info.name === "string" && info.name.length > 0, `${serviceName}: name should not be empty`);
    assert(typeof info.nameAr === "string" && info.nameAr.length > 0, `${serviceName}: nameAr should not be empty`);
    assert(typeof info.type === "string", `${serviceName}: type should be a string`);
    assert(
      ["python", "nodejs", "node", "mixed"].includes(info.type),
      `${serviceName}: type should be python/nodejs/node/mixed, got: ${info.type}`,
    );
    assert(typeof info.port === "number" && info.port > 0, `${serviceName}: port should be a positive number`);
  }

  console.log(`  ✓ ${registryEntries.length} registry entries validated`);
} else {
  console.log(`  ⚠️  SERVICE_REGISTRY not found (optional)`);
}

// ─────────────────────────────────────────────────────────────────────────────
// Summary
// ─────────────────────────────────────────────────────────────────────────────
console.log("\n══════════════════════════════════════════════");
console.log(`  Total: ${passed + failed} assertions`);
console.log(`  ✅ Passed: ${passed}`);
if (failed > 0) {
  console.log(`  ❌ Failed: ${failed}`);
  process.exit(1);
} else {
  console.log("  🎉 All contract tests passed!");
}
