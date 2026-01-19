/**
 * {{name}} - SAHOOL Platform Service
 *
 * Auto-generated Express/Node.js service with:
 * - Health/readiness endpoints
 * - Prometheus metrics
 * - Audit logging middleware
 * - Structured logging
 */

import express, { Request, Response, NextFunction } from "express";
import client from "prom-client";

// ─────────────────────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────────────────────

const app = express();
const port = Number(process.env.PORT || "{{port}}");
const service = process.env.SERVICE_NAME || "{{name}}";
const serviceLayer = process.env.SERVICE_LAYER || "{{layer}}";
const serviceVersion = process.env.SERVICE_VERSION || "1.0.0";

// Audit configuration
const auditEnabled = process.env.AUDIT_ENABLED !== "false";
const auditExcludePaths = (
  process.env.AUDIT_EXCLUDE_PATHS || "/healthz,/readyz,/metrics"
).split(",");

// ─────────────────────────────────────────────────────────────────────────────
// Prometheus Metrics
// ─────────────────────────────────────────────────────────────────────────────

const register = new client.Registry();
client.collectDefaultMetrics({ register });

const httpReqs = new client.Counter({
  name: "http_requests_total",
  help: "Total HTTP requests",
  labelNames: ["service", "path", "method", "status"] as const,
});
register.registerMetric(httpReqs);

const httpLatency = new client.Histogram({
  name: "http_request_duration_seconds",
  help: "Request latency in seconds",
  labelNames: ["service", "path", "method"] as const,
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
});
register.registerMetric(httpLatency);

// ─────────────────────────────────────────────────────────────────────────────
// Audit Middleware
// ─────────────────────────────────────────────────────────────────────────────

interface AuditContext {
  service: string;
  method: string;
  path: string;
  query?: string;
  ipAddress: string;
  userAgent?: string;
  correlationId?: string;
  userId?: string;
}

/**
 * Extract client IP address, handling proxy headers
 */
function getClientIp(req: Request): string {
  const forwarded = req.headers["x-forwarded-for"];
  if (forwarded) {
    const first = Array.isArray(forwarded) ? forwarded[0] : forwarded.split(",")[0];
    return first.trim();
  }
  return req.socket.remoteAddress || "unknown";
}

/**
 * Extract user ID from JWT token (for logging only)
 */
function extractUserId(req: Request): string | undefined {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith("Bearer ")) {
    return undefined;
  }

  try {
    const token = authHeader.slice(7);
    const payloadB64 = token.split(".")[1];
    const payload = JSON.parse(Buffer.from(payloadB64, "base64url").toString());
    return payload.sub;
  } catch {
    return undefined;
  }
}

/**
 * Structured logging function
 */
function log(level: "info" | "warn" | "error", message: string, data?: Record<string, unknown>): void {
  const logEntry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    service,
    ...data,
  };
  console[level](JSON.stringify(logEntry));
}

/**
 * Audit logging middleware
 */
function auditMiddleware(req: Request, res: Response, next: NextFunction): void {
  // Skip excluded paths
  if (auditExcludePaths.includes(req.path)) {
    return next();
  }

  const startTime = Date.now();

  // Build audit context
  const auditContext: AuditContext = {
    service,
    method: req.method,
    path: req.path,
    query: Object.keys(req.query).length > 0 ? JSON.stringify(req.query) : undefined,
    ipAddress: getClientIp(req),
    userAgent: req.headers["user-agent"],
    correlationId: req.headers["x-correlation-id"] as string | undefined,
    userId: extractUserId(req),
  };

  // Log on response finish
  res.on("finish", () => {
    const durationMs = Date.now() - startTime;

    // Log audit event
    if (auditEnabled) {
      log("info", "audit.request", {
        ...auditContext,
        statusCode: res.statusCode,
        durationMs,
      });
    }

    // Update metrics
    httpReqs.inc({
      service,
      path: req.path,
      method: req.method,
      status: res.statusCode.toString(),
    });
    httpLatency.observe(
      { service, path: req.path, method: req.method },
      durationMs / 1000
    );
  });

  next();
}

// ─────────────────────────────────────────────────────────────────────────────
// Middleware Setup
// ─────────────────────────────────────────────────────────────────────────────

app.use(express.json());
app.use(auditMiddleware);

// ─────────────────────────────────────────────────────────────────────────────
// Health & Metrics Endpoints
// ─────────────────────────────────────────────────────────────────────────────

app.get("/healthz", (_req, res) =>
  res.json({
    status: "ok",
    service,
    version: serviceVersion,
  })
);

app.get("/readyz", (_req, res) =>
  res.json({
    status: "ready",
    service,
    checks: {
      database: true, // TODO: Implement actual check
      nats: true, // TODO: Implement actual check
    },
  })
);

app.get("/metrics", async (_req, res) => {
  res.set("Content-Type", register.contentType);
  res.end(await register.metrics());
});

// ─────────────────────────────────────────────────────────────────────────────
// API Routes
// ─────────────────────────────────────────────────────────────────────────────

app.get("/", (_req, res) => {
  res.json({
    service,
    layer: serviceLayer,
    version: serviceVersion,
  });
});

// TODO: Add your API routes here
// Example:
// app.get("/api/v1/resource", (req, res) => {
//   res.json({ data: "..." });
// });

// ─────────────────────────────────────────────────────────────────────────────
// Server Startup
// ─────────────────────────────────────────────────────────────────────────────

app.listen(port, "0.0.0.0", () => {
  log("info", "service.startup", {
    port,
    layer: serviceLayer,
    version: serviceVersion,
  });
});
