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
  SERVICE_HEALTH_ENDPOINTS,
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
const INFRA_PORTS = ["KONG_GATEWAY", "KONG_ADMIN"];
const servicePorts = allPorts.filter(([name]) => !INFRA_PORTS.includes(name));
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

// ─────────────────────────────────────────────────────────────────────────────
// Tests: Contract drift fixes (v2.3.0)
// ─────────────────────────────────────────────────────────────────────────────

console.log("\n▶ Contract drift fixes (v2.3.0)");

// FIELD_ENDPOINTS.BOUNDARY* must no longer use deprecated /field-core/ prefix
assert(
  !FIELD_ENDPOINTS.BOUNDARY.includes("/field-core/"),
  "FIELD_ENDPOINTS.BOUNDARY should not contain deprecated /field-core/ prefix",
);
assert(
  FIELD_ENDPOINTS.BOUNDARY === `${API_PREFIX}/fields/{fieldId}/boundary`,
  "FIELD_ENDPOINTS.BOUNDARY should use /api/v1/fields/{fieldId}/boundary",
);
assert(
  !FIELD_ENDPOINTS.BOUNDARY_HISTORY.includes("/field-core/"),
  "FIELD_ENDPOINTS.BOUNDARY_HISTORY should not contain /field-core/",
);
assert(
  !FIELD_ENDPOINTS.BOUNDARY_ROLLBACK.includes("/field-core/"),
  "FIELD_ENDPOINTS.BOUNDARY_ROLLBACK should not contain /field-core/",
);

// CHAT_ENDPOINTS field-* must no longer use deprecated /field-chat/ prefix
assert(
  !CHAT_ENDPOINTS.FIELD_MESSAGES.includes("/field-chat/"),
  "CHAT_ENDPOINTS.FIELD_MESSAGES should not contain deprecated /field-chat/",
);
assert(
  CHAT_ENDPOINTS.FIELD_MESSAGES === `${API_PREFIX}/chat/fields/{fieldId}/messages`,
  "CHAT_ENDPOINTS.FIELD_MESSAGES should use /api/v1/chat/fields/{fieldId}/messages",
);
assert(
  !CHAT_ENDPOINTS.FIELD_PARTICIPANTS.includes("/field-chat/"),
  "CHAT_ENDPOINTS.FIELD_PARTICIPANTS should not contain /field-chat/",
);

// ADVISORY_ENDPOINTS must have new canonical entries + deprecated aliases
const advisoryAny = ADVISORY_ENDPOINTS as Record<string, string>;
assert(
  advisoryAny.ADVICE === `${API_PREFIX}/advisory/advice`,
  "ADVISORY_ENDPOINTS.ADVICE should be /api/v1/advisory/advice",
);
assert(
  advisoryAny.DISEASE === `${API_PREFIX}/advisory/disease`,
  "ADVISORY_ENDPOINTS.DISEASE should be /api/v1/advisory/disease",
);
assert(
  advisoryAny.NUTRIENTS === `${API_PREFIX}/advisory/nutrients`,
  "ADVISORY_ENDPOINTS.NUTRIENTS should be /api/v1/advisory/nutrients",
);
assert(
  advisoryAny.AGRO_ADVICE !== undefined,
  "ADVISORY_ENDPOINTS.AGRO_ADVICE (deprecated alias) should still exist for back-compat",
);

// WEATHER_ENDPOINTS Kong-routed variants - real external URLs
const weatherAny = WEATHER_ENDPOINTS as Record<string, string>;
assert(
  weatherAny.KONG_CURRENT === `${API_PREFIX}/weather/weather/current`,
  "WEATHER_ENDPOINTS.KONG_CURRENT should reflect actual Kong-routed URL",
);
assert(
  weatherAny.KONG_FORECAST === `${API_PREFIX}/weather/weather/forecast`,
  "WEATHER_ENDPOINTS.KONG_FORECAST should reflect actual Kong-routed URL",
);
assert(
  weatherAny.KONG_AGRICULTURAL_REPORT ===
    `${API_PREFIX}/weather/weather/agricultural-report`,
  "WEATHER_ENDPOINTS.KONG_AGRICULTURAL_REPORT should reflect actual Kong-routed URL",
);
assert(
  weatherAny.KONG_CURRENT_BY_LOCATION === `${API_PREFIX}/weather/v1/current/{locationId}`,
  "WEATHER_ENDPOINTS.KONG_CURRENT_BY_LOCATION should be /api/v1/weather/v1/current/{locationId}",
);

// ─────────────────────────────────────────────────────────────────────────────
// Tests: SERVICE_HEALTH_ENDPOINTS
// ─────────────────────────────────────────────────────────────────────────────

console.log("\n▶ SERVICE_HEALTH_ENDPOINTS");

assert(
  typeof SERVICE_HEALTH_ENDPOINTS === "object" && SERVICE_HEALTH_ENDPOINTS !== null,
  "SERVICE_HEALTH_ENDPOINTS should be exported as an object",
);

const healthEntries = Object.entries(SERVICE_HEALTH_ENDPOINTS as Record<string, string>);
assert(
  healthEntries.length >= 15,
  `SERVICE_HEALTH_ENDPOINTS should expose at least 15 services, got ${healthEntries.length}`,
);

for (const [key, path] of healthEntries) {
  assert(
    typeof path === "string" && path.startsWith(`${API_PREFIX}/`),
    `SERVICE_HEALTH_ENDPOINTS.${key} should start with ${API_PREFIX}/`,
  );
  assert(
    path.endsWith("/healthz"),
    `SERVICE_HEALTH_ENDPOINTS.${key} should end with /healthz, got ${path}`,
  );
  assert(
    !path.includes("{"),
    `SERVICE_HEALTH_ENDPOINTS.${key} must not contain path parameters`,
  );
}

// Common services must be present
const requiredHealth = [
  "FIELD_MANAGEMENT",
  "WEATHER",
  "IRRIGATION",
  "ADVISORY",
  "TASKS",
  "NOTIFICATIONS",
  "ALERTS",
];
for (const key of requiredHealth) {
  assert(
    key in (SERVICE_HEALTH_ENDPOINTS as Record<string, string>),
    `SERVICE_HEALTH_ENDPOINTS.${key} is required for the Service Health Dashboard`,
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Tests: CONTRACT_VERSION cadence
// ─────────────────────────────────────────────────────────────────────────────

console.log("\n▶ CONTRACT_VERSION cadence");
assert(
  /^2\.(?:[3-9]|[1-9]\d+)\.\d+$/.test(CONTRACT_VERSION) ||
    /^[3-9]\.\d+\.\d+$/.test(CONTRACT_VERSION),
  `CONTRACT_VERSION must be bumped to >= 2.3.0 after drift fixes, got ${CONTRACT_VERSION}`,
);

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
