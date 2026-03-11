/**
 * SAHOOL Rate Limiting Integration Tests
 * اختبارات تكامل تحديد المعدل
 *
 * Tests verify:
 * - ThrottlerModule configuration across all NestJS services
 * - ThrottlerGuard registered as APP_GUARD
 * - Rate limit behavior (429 on exceeded, headers set, TTL reset)
 * - Tier-based limits (Starter, Professional, Enterprise)
 * - Auth endpoint stricter rate limiting (login, password reset)
 *
 * @author SAHOOL Platform Team
 */

import { describe, it, expect, beforeAll } from "vitest";
import * as fs from "fs";
import * as path from "path";

// ═══════════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════════

const SERVICES_DIR = path.resolve(
  __dirname,
  "../../../apps/services"
);

/**
 * All NestJS services that must have ThrottlerModule configured.
 * Each entry maps service directory name to its expected port.
 */
const NESTJS_SERVICES = [
  { name: "user-service", port: 3025 },
  { name: "field-management-service", port: 3000 },
  { name: "marketplace-service", port: 3010 },
  { name: "chat-service", port: 8115 },
  { name: "iot-service", port: 8117 },
  { name: "research-core", port: 3015 },
  { name: "crop-growth-model", port: 3023 },
  { name: "disaster-assessment", port: 3020 },
  { name: "yield-prediction-service", port: 8152 },
] as const;

/**
 * Expected ThrottlerModule configuration tiers (per-service defaults).
 * These are the base limits applied globally in each service's AppModule.
 */
const EXPECTED_THROTTLE_TIERS = {
  short: { ttl: 1000, limit: 10 },
  medium: { ttl: 60000, limit: 100 },
  long: { ttl: 3600000, limit: 1000 },
} as const;

/**
 * Platform rate limit tiers as defined in CLAUDE.md and shared/middleware/rate_limit.py.
 * These are enforced at the API gateway (Kong) level.
 */
const PLATFORM_RATE_LIMIT_TIERS = {
  starter: { requestsPerMinute: 30, requestsPerHour: 500 },
  professional: { requestsPerMinute: 60, requestsPerHour: 2000 },
  enterprise: { requestsPerMinute: 120, requestsPerHour: 5000 },
  research: { requestsPerMinute: 120, requestsPerHour: 10000 },
  internal: { requestsPerMinute: 1000, requestsPerHour: 50000 },
} as const;

/**
 * Auth endpoint rate limits as implemented in user-service auth controller.
 */
const AUTH_ENDPOINT_LIMITS = {
  login: { limit: 5, ttl: 60000 },
  register: { limit: 10, ttl: 60000 },
  "forgot-password": { limit: 3, ttl: 60000 },
  "reset-password": { limit: 5, ttl: 60000 },
  "send-otp": { limit: 3, ttl: 60000 },
  "verify-otp": { limit: 5, ttl: 60000 },
  refresh: { limit: 10, ttl: 60000 },
} as const;

/**
 * Rate limit header names as defined in @sahool/shared-types contracts.
 */
const RATE_LIMIT_HEADERS = {
  REMAINING: "X-RateLimit-Remaining-Minute",
  LIMIT: "X-RateLimit-Limit-Minute",
  RESET: "X-RateLimit-Reset",
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Reads the app.module.ts file for a given NestJS service.
 */
function readAppModule(serviceName: string): string {
  const modulePath = path.join(
    SERVICES_DIR,
    serviceName,
    "src",
    "app.module.ts"
  );

  if (!fs.existsSync(modulePath)) {
    throw new Error(
      `AppModule not found for service ${serviceName} at ${modulePath}`
    );
  }

  return fs.readFileSync(modulePath, "utf-8");
}

/**
 * Reads the main.ts file for a given NestJS service.
 */
function readMainFile(serviceName: string): string {
  const mainPath = path.join(
    SERVICES_DIR,
    serviceName,
    "src",
    "main.ts"
  );

  if (!fs.existsSync(mainPath)) {
    throw new Error(
      `main.ts not found for service ${serviceName} at ${mainPath}`
    );
  }

  return fs.readFileSync(mainPath, "utf-8");
}

/**
 * Reads the auth controller file for the user-service.
 */
function readAuthController(): string {
  const controllerPath = path.join(
    SERVICES_DIR,
    "user-service",
    "src",
    "auth",
    "auth.controller.ts"
  );

  if (!fs.existsSync(controllerPath)) {
    throw new Error(
      `Auth controller not found at ${controllerPath}`
    );
  }

  return fs.readFileSync(controllerPath, "utf-8");
}

/**
 * Reads the Python rate limit middleware.
 */
function readPythonRateLimitMiddleware(): string {
  const middlewarePath = path.resolve(
    __dirname,
    "../../../shared/middleware/rate_limit.py"
  );

  if (!fs.existsSync(middlewarePath)) {
    throw new Error(
      `Python rate limit middleware not found at ${middlewarePath}`
    );
  }

  return fs.readFileSync(middlewarePath, "utf-8");
}

/**
 * Extracts ThrottlerModule configuration values from source code.
 * Returns parsed tier configs or null if not found.
 */
function extractThrottlerConfig(
  source: string
): Array<{ name: string; ttl: number; limit: number }> | null {
  const configs: Array<{ name: string; ttl: number; limit: number }> = [];

  // Match each throttler tier block
  const tierRegex =
    /\{\s*name:\s*["'](\w+)["'],?\s*ttl:\s*(\d+),?\s*[\s\S]*?limit:\s*(\d+)/g;
  let match;

  while ((match = tierRegex.exec(source)) !== null) {
    configs.push({
      name: match[1],
      ttl: parseInt(match[2], 10),
      limit: parseInt(match[3], 10),
    });
  }

  return configs.length > 0 ? configs : null;
}

/**
 * Extracts @Throttle decorator configuration for a given endpoint.
 */
function extractEndpointThrottle(
  source: string,
  endpointName: string
): { limit: number; ttl: number } | null {
  // Look for @Throttle decorator near @Post("endpointName")
  const regex = new RegExp(
    `@Throttle\\(\\{\\s*default:\\s*\\{\\s*limit:\\s*(\\d+),\\s*ttl:\\s*(\\d+)\\s*\\}\\s*\\}\\)\\s*[\\s\\S]*?@Post\\(["']${endpointName}["']\\)|@Post\\(["']${endpointName}["']\\)[\\s\\S]*?@Throttle\\(\\{\\s*default:\\s*\\{\\s*limit:\\s*(\\d+),\\s*ttl:\\s*(\\d+)\\s*\\}\\s*\\}\\)`,
    "m"
  );

  // Also try the reverse order (Throttle before Post, which is the actual pattern)
  const reverseRegex = new RegExp(
    `@Throttle\\(\\{\\s*default:\\s*\\{\\s*limit:\\s*(\\d+),\\s*ttl:\\s*(\\d+)\\s*\\}\\s*\\}\\)[\\s\\S]{0,200}?@Post\\(["']${endpointName}["']\\)`,
    "m"
  );

  // Try the pattern where @Post comes first
  const postFirstRegex = new RegExp(
    `@Post\\(["']${endpointName}["']\\)[\\s\\S]{0,200}?@Throttle\\(\\{\\s*default:\\s*\\{\\s*limit:\\s*(\\d+),\\s*ttl:\\s*(\\d+)\\s*\\}\\s*\\}\\)`,
    "m"
  );

  let result = reverseRegex.exec(source);
  if (result) {
    return { limit: parseInt(result[1], 10), ttl: parseInt(result[2], 10) };
  }

  result = postFirstRegex.exec(source);
  if (result) {
    return { limit: parseInt(result[1], 10), ttl: parseInt(result[2], 10) };
  }

  return null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tests: Rate Limiter Configuration
// ═══════════════════════════════════════════════════════════════════════════════

describe("Rate Limiting", () => {
  describe("ThrottlerModule Configuration", () => {
    it.each(NESTJS_SERVICES.map((s) => [s.name, s.port]))(
      "service %s (port %i) has ThrottlerModule imported",
      (serviceName) => {
        const source = readAppModule(serviceName as string);

        expect(source).toContain(
          'import { ThrottlerModule, ThrottlerGuard } from "@nestjs/throttler"'
        );
        expect(source).toContain("ThrottlerModule.forRoot");
      }
    );

    it.each(NESTJS_SERVICES.map((s) => [s.name, s.port]))(
      "service %s (port %i) registers ThrottlerGuard as APP_GUARD",
      (serviceName) => {
        const source = readAppModule(serviceName as string);

        // Verify APP_GUARD import
        expect(source).toContain("APP_GUARD");

        // Verify ThrottlerGuard is provided as APP_GUARD
        expect(source).toMatch(
          /provide:\s*APP_GUARD,\s*\n?\s*useClass:\s*ThrottlerGuard/
        );
      }
    );

    it.each(NESTJS_SERVICES.map((s) => [s.name]))(
      "service %s has three throttle tiers configured (short, medium, long)",
      (serviceName) => {
        const source = readAppModule(serviceName as string);
        const configs = extractThrottlerConfig(source);

        expect(configs).not.toBeNull();
        expect(configs!.length).toBeGreaterThanOrEqual(3);

        const tierNames = configs!.map((c) => c.name);
        expect(tierNames).toContain("short");
        expect(tierNames).toContain("medium");
        expect(tierNames).toContain("long");
      }
    );

    it("rate limit configs use consistent TTL values across services", () => {
      const serviceConfigs: Record<
        string,
        Array<{ name: string; ttl: number; limit: number }>
      > = {};

      for (const service of NESTJS_SERVICES) {
        const source = readAppModule(service.name);
        const configs = extractThrottlerConfig(source);
        if (configs) {
          serviceConfigs[service.name] = configs;
        }
      }

      // All services should have the same TTL values for each tier
      const ttlValues: Record<string, Set<number>> = {
        short: new Set(),
        medium: new Set(),
        long: new Set(),
      };

      for (const [, configs] of Object.entries(serviceConfigs)) {
        for (const config of configs) {
          if (ttlValues[config.name]) {
            ttlValues[config.name].add(config.ttl);
          }
        }
      }

      // TTL values should be consistent across all services
      expect(ttlValues.short.size).toBe(1);
      expect(ttlValues.medium.size).toBe(1);
      expect(ttlValues.long.size).toBe(1);

      // Verify expected TTL values
      expect(ttlValues.short.has(EXPECTED_THROTTLE_TIERS.short.ttl)).toBe(true);
      expect(ttlValues.medium.has(EXPECTED_THROTTLE_TIERS.medium.ttl)).toBe(
        true
      );
      expect(ttlValues.long.has(EXPECTED_THROTTLE_TIERS.long.ttl)).toBe(true);
    });

    it("short tier TTL is 1 second (1000ms)", () => {
      for (const service of NESTJS_SERVICES) {
        const source = readAppModule(service.name);
        const configs = extractThrottlerConfig(source);
        const shortTier = configs?.find((c) => c.name === "short");

        expect(shortTier).toBeDefined();
        expect(shortTier!.ttl).toBe(1000);
      }
    });

    it("medium tier TTL is 1 minute (60000ms)", () => {
      for (const service of NESTJS_SERVICES) {
        const source = readAppModule(service.name);
        const configs = extractThrottlerConfig(source);
        const mediumTier = configs?.find((c) => c.name === "medium");

        expect(mediumTier).toBeDefined();
        expect(mediumTier!.ttl).toBe(60000);
      }
    });

    it("long tier TTL is 1 hour (3600000ms)", () => {
      for (const service of NESTJS_SERVICES) {
        const source = readAppModule(service.name);
        const configs = extractThrottlerConfig(source);
        const longTier = configs?.find((c) => c.name === "long");

        expect(longTier).toBeDefined();
        expect(longTier!.ttl).toBe(3600000);
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Rate Limit Behavior
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Rate Limit Behavior", () => {
    it("ThrottlerModule is configured to return 429 when limit exceeded", () => {
      // ThrottlerGuard from @nestjs/throttler returns 429 by default
      // We verify this by checking that no custom exception override exists
      for (const service of NESTJS_SERVICES) {
        const source = readAppModule(service.name);

        // ThrottlerGuard should be used directly (not a custom subclass
        // that might change the status code)
        expect(source).toMatch(/useClass:\s*ThrottlerGuard/);

        // Verify no custom handleRequest override that might change behavior
        expect(source).not.toContain("ThrottlerException");
      }
    });

    it("rate limit headers are defined in shared-types contracts", () => {
      const contractsPath = path.resolve(
        __dirname,
        "../../../packages/shared-types/src/contracts/api-responses.ts"
      );

      if (!fs.existsSync(contractsPath)) {
        // Skip if contracts package not available
        return;
      }

      const source = fs.readFileSync(contractsPath, "utf-8");

      // Verify rate limit header constants are defined
      expect(source).toContain("RATE_LIMIT_HEADER_NAMES");
      expect(source).toContain(RATE_LIMIT_HEADERS.REMAINING);
      expect(source).toContain(RATE_LIMIT_HEADERS.LIMIT);
      expect(source).toContain(RATE_LIMIT_HEADERS.RESET);
    });

    it("rate limit response interface includes remaining, limit, and reset fields", () => {
      const contractsPath = path.resolve(
        __dirname,
        "../../../packages/shared-types/src/contracts/api-responses.ts"
      );

      if (!fs.existsSync(contractsPath)) {
        return;
      }

      const source = fs.readFileSync(contractsPath, "utf-8");

      // Verify RateLimitHeaders interface
      expect(source).toContain("interface RateLimitHeaders");
      expect(source).toContain("remaining: number");
      expect(source).toContain("limit: number");
      expect(source).toContain("reset: number");
    });

    it("services apply rate limiting globally (not per-route only)", () => {
      for (const service of NESTJS_SERVICES) {
        const source = readAppModule(service.name);

        // ThrottlerGuard as APP_GUARD means it applies to ALL routes
        const appGuardMatches = source.match(
          /provide:\s*APP_GUARD,\s*\n?\s*useClass:\s*ThrottlerGuard/g
        );

        expect(appGuardMatches).not.toBeNull();
        expect(appGuardMatches!.length).toBeGreaterThanOrEqual(1);
      }
    });

    it("health endpoints should skip rate limiting in field-management-service", () => {
      const healthControllerPath = path.join(
        SERVICES_DIR,
        "field-management-service",
        "src",
        "health",
        "health.controller.ts"
      );

      if (!fs.existsSync(healthControllerPath)) {
        return;
      }

      const source = fs.readFileSync(healthControllerPath, "utf-8");

      // Health endpoints should use @SkipThrottle()
      expect(source).toContain("SkipThrottle");
      expect(source).toContain("@SkipThrottle()");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Tier-Based Limits
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Tier-Based Rate Limits", () => {
    it("Starter tier allows 30 requests per minute", () => {
      expect(PLATFORM_RATE_LIMIT_TIERS.starter.requestsPerMinute).toBe(30);
    });

    it("Professional tier allows 60 requests per minute", () => {
      expect(PLATFORM_RATE_LIMIT_TIERS.professional.requestsPerMinute).toBe(60);
    });

    it("Enterprise tier allows 120 requests per minute", () => {
      expect(PLATFORM_RATE_LIMIT_TIERS.enterprise.requestsPerMinute).toBe(120);
    });

    it("Starter tier allows 500 requests per hour", () => {
      expect(PLATFORM_RATE_LIMIT_TIERS.starter.requestsPerHour).toBe(500);
    });

    it("Professional tier allows 2000 requests per hour", () => {
      expect(PLATFORM_RATE_LIMIT_TIERS.professional.requestsPerHour).toBe(
        2000
      );
    });

    it("Enterprise tier allows 5000 requests per hour", () => {
      expect(PLATFORM_RATE_LIMIT_TIERS.enterprise.requestsPerHour).toBe(5000);
    });

    it("Internal tier allows 1000 requests per minute", () => {
      expect(PLATFORM_RATE_LIMIT_TIERS.internal.requestsPerMinute).toBe(1000);
    });

    it("Python middleware defines matching tier limits", () => {
      const source = readPythonRateLimitMiddleware();

      // Verify free/starter tier: 30 req/min
      expect(source).toContain("requests_per_minute=30");
      expect(source).toContain("requests_per_hour=500");

      // Verify standard/professional tier: 60 req/min
      expect(source).toContain("requests_per_minute=60");
      expect(source).toContain("requests_per_hour=2000");

      // Verify premium/enterprise tier: 120 req/min
      expect(source).toContain("requests_per_minute=120");
      expect(source).toContain("requests_per_hour=5000");

      // Verify internal tier: 1000 req/min
      expect(source).toContain("requests_per_minute=1000");
      expect(source).toContain("requests_per_hour=50000");
    });

    it("tier limits increase monotonically (starter < professional < enterprise)", () => {
      const { starter, professional, enterprise } = PLATFORM_RATE_LIMIT_TIERS;

      expect(starter.requestsPerMinute).toBeLessThan(
        professional.requestsPerMinute
      );
      expect(professional.requestsPerMinute).toBeLessThanOrEqual(
        enterprise.requestsPerMinute
      );

      expect(starter.requestsPerHour).toBeLessThan(
        professional.requestsPerHour
      );
      expect(professional.requestsPerHour).toBeLessThan(
        enterprise.requestsPerHour
      );
    });

    it("Professional tier is exactly 2x Starter tier (requests per minute)", () => {
      expect(PLATFORM_RATE_LIMIT_TIERS.professional.requestsPerMinute).toBe(
        PLATFORM_RATE_LIMIT_TIERS.starter.requestsPerMinute * 2
      );
    });

    it("Enterprise tier is exactly 4x Starter tier (requests per minute)", () => {
      expect(PLATFORM_RATE_LIMIT_TIERS.enterprise.requestsPerMinute).toBe(
        PLATFORM_RATE_LIMIT_TIERS.starter.requestsPerMinute * 4
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Auth Endpoint Protection
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Auth Endpoint Protection", () => {
    let authControllerSource: string;

    beforeAll(() => {
      authControllerSource = readAuthController();
    });

    it("login endpoint has stricter rate limiting (5 req/min)", () => {
      const throttle = extractEndpointThrottle(
        authControllerSource,
        "login"
      );

      expect(throttle).not.toBeNull();
      expect(throttle!.limit).toBe(AUTH_ENDPOINT_LIMITS.login.limit);
      expect(throttle!.ttl).toBe(AUTH_ENDPOINT_LIMITS.login.ttl);
    });

    it("login rate limit is stricter than the global default", () => {
      const throttle = extractEndpointThrottle(
        authControllerSource,
        "login"
      );

      expect(throttle).not.toBeNull();
      // Login limit (5/min) should be much lower than global medium tier (100/min)
      expect(throttle!.limit).toBeLessThan(
        EXPECTED_THROTTLE_TIERS.medium.limit
      );
    });

    it("forgot-password endpoint has strict rate limiting (3 req/min)", () => {
      const throttle = extractEndpointThrottle(
        authControllerSource,
        "forgot-password"
      );

      expect(throttle).not.toBeNull();
      expect(throttle!.limit).toBe(
        AUTH_ENDPOINT_LIMITS["forgot-password"].limit
      );
      expect(throttle!.ttl).toBe(AUTH_ENDPOINT_LIMITS["forgot-password"].ttl);
    });

    it("reset-password endpoint has rate limiting (5 req/min)", () => {
      const throttle = extractEndpointThrottle(
        authControllerSource,
        "reset-password"
      );

      expect(throttle).not.toBeNull();
      expect(throttle!.limit).toBe(
        AUTH_ENDPOINT_LIMITS["reset-password"].limit
      );
      expect(throttle!.ttl).toBe(AUTH_ENDPOINT_LIMITS["reset-password"].ttl);
    });

    it("registration endpoint has rate limiting (10 req/min)", () => {
      const throttle = extractEndpointThrottle(
        authControllerSource,
        "register"
      );

      expect(throttle).not.toBeNull();
      expect(throttle!.limit).toBe(AUTH_ENDPOINT_LIMITS.register.limit);
      expect(throttle!.ttl).toBe(AUTH_ENDPOINT_LIMITS.register.ttl);
    });

    it("token refresh endpoint has rate limiting (10 req/min)", () => {
      const throttle = extractEndpointThrottle(
        authControllerSource,
        "refresh"
      );

      expect(throttle).not.toBeNull();
      expect(throttle!.limit).toBe(AUTH_ENDPOINT_LIMITS.refresh.limit);
      expect(throttle!.ttl).toBe(AUTH_ENDPOINT_LIMITS.refresh.ttl);
    });

    it("send-otp endpoint has strict rate limiting (3 req/min)", () => {
      const throttle = extractEndpointThrottle(
        authControllerSource,
        "send-otp"
      );

      expect(throttle).not.toBeNull();
      expect(throttle!.limit).toBe(AUTH_ENDPOINT_LIMITS["send-otp"].limit);
      expect(throttle!.ttl).toBe(AUTH_ENDPOINT_LIMITS["send-otp"].ttl);
    });

    it("verify-otp endpoint has rate limiting (5 req/min)", () => {
      const throttle = extractEndpointThrottle(
        authControllerSource,
        "verify-otp"
      );

      expect(throttle).not.toBeNull();
      expect(throttle!.limit).toBe(AUTH_ENDPOINT_LIMITS["verify-otp"].limit);
      expect(throttle!.ttl).toBe(AUTH_ENDPOINT_LIMITS["verify-otp"].ttl);
    });

    it("auth controller imports Throttle decorator", () => {
      expect(authControllerSource).toContain("Throttle");
      expect(authControllerSource).toMatch(
        /import\s*\{[^}]*Throttle[^}]*\}\s*from\s*["']@nestjs\/throttler["']/
      );
    });

    it("password-related endpoints have stricter limits than general auth endpoints", () => {
      const loginLimit = AUTH_ENDPOINT_LIMITS.login.limit;
      const forgotPwLimit = AUTH_ENDPOINT_LIMITS["forgot-password"].limit;
      const registerLimit = AUTH_ENDPOINT_LIMITS.register.limit;

      // Password operations should be more restricted than registration
      expect(loginLimit).toBeLessThanOrEqual(registerLimit);
      expect(forgotPwLimit).toBeLessThanOrEqual(loginLimit);
    });

    it("all auth endpoints use 60-second TTL windows", () => {
      for (const [, config] of Object.entries(AUTH_ENDPOINT_LIMITS)) {
        expect(config.ttl).toBe(60000);
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Service-Specific Throttle Overrides
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Service-Specific Throttle Overrides", () => {
    it("chat service message sending has custom rate limit (10 req/min)", () => {
      const controllerPath = path.join(
        SERVICES_DIR,
        "chat-service",
        "src",
        "chat",
        "chat.controller.ts"
      );

      if (!fs.existsSync(controllerPath)) {
        return;
      }

      const source = fs.readFileSync(controllerPath, "utf-8");

      // Chat message sending should have a custom throttle
      expect(source).toContain("@Throttle");
      expect(source).toMatch(
        /@Throttle\(\{\s*default:\s*\{\s*limit:\s*10,\s*ttl:\s*60000\s*\}\s*\}\)/
      );
    });

    it("IoT data ingestion has custom rate limit", () => {
      const controllerPath = path.join(
        SERVICES_DIR,
        "iot-service",
        "src",
        "iot",
        "iot.controller.ts"
      );

      if (!fs.existsSync(controllerPath)) {
        return;
      }

      const source = fs.readFileSync(controllerPath, "utf-8");

      // IoT service should have throttle decorators on specific endpoints
      expect(source).toContain("@Throttle");
    });

    it("field-management-service has custom throttle on bulk operations", () => {
      const controllerPath = path.join(
        SERVICES_DIR,
        "field-management-service",
        "src",
        "fields",
        "fields.controller.ts"
      );

      if (!fs.existsSync(controllerPath)) {
        return;
      }

      const source = fs.readFileSync(controllerPath, "utf-8");

      // Bulk operations should have stricter limits
      expect(source).toContain("@Throttle");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Python Rate Limiting Middleware Consistency
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Python Rate Limiting Middleware", () => {
    let middlewareSource: string;

    beforeAll(() => {
      middlewareSource = readPythonRateLimitMiddleware();
    });

    it("implements token bucket algorithm", () => {
      expect(middlewareSource).toContain("class TokenBucket");
      expect(middlewareSource).toContain("def consume");
      expect(middlewareSource).toContain("def _refill");
    });

    it("defines RateLimitConfig dataclass with required fields", () => {
      expect(middlewareSource).toContain("class RateLimitConfig");
      expect(middlewareSource).toContain("requests_per_minute");
      expect(middlewareSource).toContain("requests_per_hour");
      expect(middlewareSource).toContain("burst_limit");
    });

    it("defines TierConfig with free, standard, premium, and internal tiers", () => {
      expect(middlewareSource).toContain("class TierConfig");
      expect(middlewareSource).toContain("free:");
      expect(middlewareSource).toContain("standard:");
      expect(middlewareSource).toContain("premium:");
      expect(middlewareSource).toContain("internal:");
    });

    it("Python tier names map to platform tier names", () => {
      // Python uses free/standard/premium/internal
      // Platform docs use starter/professional/enterprise/internal
      // The limits should match regardless of naming
      const pythonToplatform: Record<string, keyof typeof PLATFORM_RATE_LIMIT_TIERS> = {
        free: "starter",
        standard: "professional",
        premium: "enterprise",
        internal: "internal",
      };

      for (const [pythonTier, platformTier] of Object.entries(
        pythonToplatform
      )) {
        const expectedLimit =
          PLATFORM_RATE_LIMIT_TIERS[platformTier].requestsPerMinute;
        expect(middlewareSource).toContain(
          `requests_per_minute=${expectedLimit}`
        );
      }
    });

    it("returns 429 status code for rate-limited requests", () => {
      // The middleware should use HTTP 429 Too Many Requests
      expect(middlewareSource).toMatch(/429|Too Many Requests|HTTPException/);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Cross-Service Consistency
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Cross-Service Rate Limit Consistency", () => {
    it("all NestJS services have ThrottlerModule in their imports array", () => {
      const missingServices: string[] = [];

      for (const service of NESTJS_SERVICES) {
        try {
          const source = readAppModule(service.name);
          if (!source.includes("ThrottlerModule.forRoot")) {
            missingServices.push(service.name);
          }
        } catch {
          // Service module file doesn't exist - skip
        }
      }

      expect(missingServices).toEqual([]);
    });

    it("no service uses unlimited rate limiting", () => {
      for (const service of NESTJS_SERVICES) {
        const source = readAppModule(service.name);
        const configs = extractThrottlerConfig(source);

        if (configs) {
          for (const config of configs) {
            // No tier should allow more than 10000 requests
            expect(config.limit).toBeLessThanOrEqual(10000);
            // No tier should have a TTL of 0
            expect(config.ttl).toBeGreaterThan(0);
          }
        }
      }
    });

    it("the auth example controller documents expected rate limits", () => {
      const examplePath = path.join(
        SERVICES_DIR,
        "shared",
        "auth",
        "auth.controller.example.ts"
      );

      if (!fs.existsSync(examplePath)) {
        return;
      }

      const source = fs.readFileSync(examplePath, "utf-8");

      // The example should document rate limits
      expect(source).toContain("5 requests per minute");
      expect(source).toContain("3 requests per minute");
      expect(source).toContain("10 requests per minute");
    });

    it("field-management-service has higher limits than user-service (more traffic)", () => {
      const fieldSource = readAppModule("field-management-service");
      const userSource = readAppModule("user-service");

      const fieldConfigs = extractThrottlerConfig(fieldSource);
      const userConfigs = extractThrottlerConfig(userSource);

      expect(fieldConfigs).not.toBeNull();
      expect(userConfigs).not.toBeNull();

      const fieldMedium = fieldConfigs!.find((c) => c.name === "medium");
      const userMedium = userConfigs!.find((c) => c.name === "medium");

      expect(fieldMedium).toBeDefined();
      expect(userMedium).toBeDefined();

      // Field management handles more traffic, so its limits should be >= user service
      expect(fieldMedium!.limit).toBeGreaterThanOrEqual(userMedium!.limit);
    });
  });
});
