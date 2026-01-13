/**
 * SAHOOL Content Security Policy Configuration
 * إعدادات سياسة أمان المحتوى
 *
 * Implements strict CSP headers to prevent XSS and other injection attacks
 * تنفيذ CSP صارمة لمنع هجمات XSS والحقن الأخرى
 */

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface CSPDirectives {
  "default-src"?: string[];
  "script-src"?: string[];
  "style-src"?: string[];
  "img-src"?: string[];
  "font-src"?: string[];
  "connect-src"?: string[];
  "media-src"?: string[];
  "object-src"?: string[];
  "frame-src"?: string[];
  "worker-src"?: string[];
  "child-src"?: string[];
  "frame-ancestors"?: string[];
  "form-action"?: string[];
  "base-uri"?: string[];
  "manifest-src"?: string[];
  "upgrade-insecure-requests"?: boolean;
  "block-all-mixed-content"?: boolean;
  "report-uri"?: string[];
  "report-to"?: string;
}

export interface CSPConfig {
  directives: CSPDirectives;
  reportOnly?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Nonce Generation
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Generate cryptographically secure nonce
 * إنشاء nonce آمن من الناحية التشفيرية
 *
 * Uses Web Crypto API which is compatible with Edge Runtime
 */
export function generateNonce(): string {
  // Use Web Crypto API for Edge Runtime compatibility
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);

  // Convert to base64
  const base64 = btoa(String.fromCharCode(...array));
  return base64;
}

// ═══════════════════════════════════════════════════════════════════════════
// Environment Detection
// ═══════════════════════════════════════════════════════════════════════════

const isDevelopment = process.env.NODE_ENV === "development";
const isProduction = process.env.NODE_ENV === "production";

// ═══════════════════════════════════════════════════════════════════════════
// Development Port Configuration
// ═══════════════════════════════════════════════════════════════════════════

const DEV_API_PORT = process.env.DEV_API_PORT || "8000";
const DEV_WS_PORT = process.env.DEV_WS_PORT || "8081";
const DEV_WEB_PORT = process.env.DEV_WEB_PORT || "3000";
const DEV_ADMIN_PORT = process.env.DEV_ADMIN_PORT || "3001";

// ═══════════════════════════════════════════════════════════════════════════
// CSP Directives Configuration
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get CSP directives based on environment
 * الحصول على توجيهات CSP بناءً على البيئة
 */
export function getCSPDirectives(nonce?: string): CSPDirectives {
  const directives: CSPDirectives = {
    "default-src": ["'self'"],

    // Script sources - Use nonce in production, allow unsafe-eval only in dev
    "script-src": [
      "'self'",
      ...(nonce ? [`'nonce-${nonce}'`] : []),
      // Next.js requires 'unsafe-eval' for hot reloading in development
      ...(isDevelopment ? ["'unsafe-eval'"] : []),
      // Strict dynamic for better security with nonces
      ...(nonce && isProduction ? ["'strict-dynamic'"] : []),
    ],

    // Style sources - Use nonce in production
    "style-src": [
      "'self'",
      ...(nonce ? [`'nonce-${nonce}'`] : []),
      // Google Fonts
      "https://fonts.googleapis.com",
      // Allow inline styles only in development
      ...(isDevelopment ? ["'unsafe-inline'"] : []),
    ],

    // Image sources
    "img-src": [
      "'self'",
      "data:",
      "blob:",
      "https:",
      // OpenStreetMap tiles
      "https://tile.openstreetmap.org",
      "https://*.tile.openstreetmap.org",
      // Sentinel Hub satellite imagery
      "https://sentinel-hub.com",
      "https://*.sentinel-hub.com",
      // SAHOOL CDN
      "https://*.sahool.ye",
    ],

    // Font sources
    "font-src": [
      "'self'",
      "data:",
      // Google Fonts
      "https://fonts.gstatic.com",
    ],

    // Connect sources (API, WebSocket, etc.)
    "connect-src": [
      "'self'",
      // Backend API - require environment variable or use localhost in dev only
      ...(process.env.NEXT_PUBLIC_API_URL
        ? [process.env.NEXT_PUBLIC_API_URL]
        : isDevelopment
          ? [`http://localhost:${DEV_API_PORT}`]
          : []),
      // Development-only localhost connections with specific ports
      ...(isDevelopment
        ? [
            // WebSocket for hot module replacement and real-time features
            `ws://localhost:${DEV_WS_PORT}`,
            // API backend
            `http://localhost:${DEV_API_PORT}`,
            // Next.js dev server
            `http://localhost:${DEV_WEB_PORT}`,
            // Admin dev server
            `http://localhost:${DEV_ADMIN_PORT}`,
          ]
        : []),
      // External services
      "https://tile.openstreetmap.org",
      "https://*.tile.openstreetmap.org",
      "https://sentinel-hub.com",
      "https://*.sentinel-hub.com",
      "https://*.sahool.ye",
    ],

    // Media sources
    "media-src": ["'self'", "https://*.sahool.ye"],

    // Object sources - Block all
    "object-src": ["'none'"],

    // Frame sources
    "frame-src": ["'none'"],

    // Worker sources (for service workers, web workers)
    "worker-src": ["'self'", "blob:"],

    // Child sources
    "child-src": ["'self'", "blob:"],

    // Frame ancestors - Prevent clickjacking
    "frame-ancestors": ["'none'"],

    // Form action - Only allow same origin
    "form-action": ["'self'"],

    // Base URI - Restrict base tag
    "base-uri": ["'self'"],

    // Manifest source
    "manifest-src": ["'self'"],

    // Upgrade insecure requests in production
    "upgrade-insecure-requests": isProduction,

    // Block mixed content in production
    "block-all-mixed-content": isProduction,

    // CSP reporting endpoint
    "report-uri": ["/api/csp-report"],
  };

  return directives;
}

/**
 * Build CSP header string from directives
 * إنشاء سلسلة header CSP من التوجيهات
 */
export function buildCSPHeader(directives: CSPDirectives): string {
  const policies: string[] = [];

  for (const [key, value] of Object.entries(directives)) {
    // Handle boolean directives
    if (typeof value === "boolean") {
      if (value) {
        policies.push(key);
      }
      continue;
    }

    // Handle array directives
    if (Array.isArray(value) && value.length > 0) {
      policies.push(`${key} ${value.join(" ")}`);
    }

    // Handle string directives
    if (typeof value === "string") {
      policies.push(`${key} ${value}`);
    }
  }

  return policies.join("; ");
}

/**
 * Get complete CSP configuration for the current environment
 * الحصول على تكوين CSP الكامل للبيئة الحالية
 */
export function getCSPConfig(nonce?: string): CSPConfig {
  return {
    directives: getCSPDirectives(nonce),
    // Use report-only mode in development for testing
    reportOnly: isDevelopment && process.env.CSP_REPORT_ONLY === "true",
  };
}

/**
 * Get CSP header value
 * الحصول على قيمة header CSP
 */
export function getCSPHeader(nonce?: string): string {
  const config = getCSPConfig(nonce);
  return buildCSPHeader(config.directives);
}

/**
 * Get CSP header name based on mode
 * الحصول على اسم header CSP بناءً على الوضع
 */
export function getCSPHeaderName(reportOnly = false): string {
  return reportOnly
    ? "Content-Security-Policy-Report-Only"
    : "Content-Security-Policy";
}

// ═══════════════════════════════════════════════════════════════════════════
// CSP Violation Reporting Configuration
// ═══════════════════════════════════════════════════════════════════════════

export interface CSPViolationReport {
  "document-uri": string;
  "violated-directive": string;
  "effective-directive": string;
  "original-policy": string;
  "blocked-uri": string;
  "status-code": number;
  "source-file"?: string;
  "line-number"?: number;
  "column-number"?: number;
}

export interface CSPReportBody {
  "csp-report": CSPViolationReport;
}

/**
 * Validate CSP violation report
 * التحقق من صحة تقرير انتهاك CSP
 */
export function isValidCSPReport(body: unknown): body is CSPReportBody {
  if (typeof body !== "object" || body === null) return false;

  const report = body as Record<string, unknown>;

  if (!("csp-report" in report)) return false;

  const cspReport = report["csp-report"];
  if (typeof cspReport !== "object" || cspReport === null) return false;

  const violation = cspReport as Record<string, unknown>;

  // Required fields
  return (
    typeof violation["document-uri"] === "string" &&
    typeof violation["violated-directive"] === "string" &&
    typeof violation["blocked-uri"] === "string"
  );
}

/**
 * Sanitize CSP report for logging
 * تنظيف تقرير CSP للتسجيل
 */
export function sanitizeCSPReport(
  report: CSPViolationReport,
): Record<string, unknown> {
  return {
    timestamp: new Date().toISOString(),
    documentUri: report["document-uri"],
    violatedDirective: report["violated-directive"],
    effectiveDirective: report["effective-directive"],
    blockedUri: report["blocked-uri"],
    statusCode: report["status-code"],
    sourceFile: report["source-file"],
    lineNumber: report["line-number"],
    columnNumber: report["column-number"],
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Export
// ═══════════════════════════════════════════════════════════════════════════

export const CSP = {
  generateNonce,
  getDirectives: getCSPDirectives,
  buildHeader: buildCSPHeader,
  getConfig: getCSPConfig,
  getHeader: getCSPHeader,
  getHeaderName: getCSPHeaderName,
  isValidReport: isValidCSPReport,
  sanitizeReport: sanitizeCSPReport,
};

export default CSP;
