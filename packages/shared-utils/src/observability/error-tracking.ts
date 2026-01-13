/**
 * Sentry Error Tracking Integration
 * تكامل Sentry لتتبع الأخطاء
 */

// Check if we're in browser environment
const isBrowser = typeof window !== "undefined";

interface ErrorContext {
  componentStack?: string;
  tags?: Record<string, string>;
  extra?: Record<string, unknown>;
  user?: {
    id?: string;
    email?: string;
    name?: string;
  };
}

interface BreadcrumbData {
  category: string;
  message: string;
  level?: "debug" | "info" | "warning" | "error";
  data?: Record<string, unknown>;
}

/**
 * Initialize Sentry (call this in your app entry point)
 * Note: In production, use @sentry/nextjs package
 */
export function initSentry(dsn?: string): void {
  if (!isBrowser) return;

  const sentryDsn = dsn || process.env.NEXT_PUBLIC_SENTRY_DSN;

  if (!sentryDsn) {
    console.warn("[Sentry] No DSN provided, error tracking disabled");
    return;
  }

  // In production, replace this with actual Sentry initialization:
  // import * as Sentry from '@sentry/nextjs';
  // Sentry.init({ dsn: sentryDsn, ... });

  console.info("[Sentry] Error tracking initialized");

  // Set up global error handlers
  window.onerror = (message, source, lineno, colno, error) => {
    captureException(error || new Error(String(message)), {
      extra: { source, lineno, colno },
    });
  };

  window.onunhandledrejection = (event) => {
    captureException(event.reason, {
      tags: { type: "unhandledrejection" },
    });
  };
}

/**
 * Capture an exception and send to Sentry
 */
export function captureException(
  error: Error | unknown,
  context?: ErrorContext,
): void {
  const errorObj = error instanceof Error ? error : new Error(String(error));

  // In development, log to console
  if (process.env.NODE_ENV === "development") {
    console.error("[Sentry] Captured Exception:", errorObj);
    if (context) {
      console.error("[Sentry] Context:", context);
    }
    return;
  }

  // In production, send to error logging endpoint
  logErrorToServer({
    type: "exception",
    message: errorObj.message,
    stack: errorObj.stack,
    context,
    timestamp: new Date().toISOString(),
    url: isBrowser ? window.location.href : undefined,
    userAgent: isBrowser ? navigator.userAgent : undefined,
  });
}

/**
 * Capture a message (for non-error events)
 */
export function captureMessage(
  message: string,
  level: "debug" | "info" | "warning" | "error" = "info",
  context?: ErrorContext,
): void {
  if (process.env.NODE_ENV === "development") {
    console.log(`[Sentry] ${level.toUpperCase()}: ${message}`);
    return;
  }

  logErrorToServer({
    type: "message",
    message,
    level,
    context,
    timestamp: new Date().toISOString(),
    url: isBrowser ? window.location.href : undefined,
  });
}

/**
 * Add breadcrumb for debugging
 */
export function addBreadcrumb(data: BreadcrumbData): void {
  if (process.env.NODE_ENV === "development") {
    console.log(`[Sentry Breadcrumb] ${data.category}: ${data.message}`);
  }

  // Store breadcrumbs in memory for error context
  breadcrumbs.push({
    ...data,
    timestamp: new Date().toISOString(),
  });

  // Keep only last 50 breadcrumbs
  if (breadcrumbs.length > 50) {
    breadcrumbs.shift();
  }
}

/**
 * Set user context
 */
export function setUser(user: ErrorContext["user"] | null): void {
  currentUser = user;
}

/**
 * Set extra context
 */
export function setContext(
  name: string,
  context: Record<string, unknown>,
): void {
  extraContext[name] = context;
}

// Internal state
const breadcrumbs: Array<BreadcrumbData & { timestamp: string }> = [];
let currentUser: ErrorContext["user"] | null = null;
const extraContext: Record<string, Record<string, unknown>> = {};

/**
 * Send error to server logging endpoint
 */
async function logErrorToServer(data: Record<string, unknown>): Promise<void> {
  try {
    const payload = {
      ...data,
      breadcrumbs: breadcrumbs.slice(-20),
      user: currentUser,
      context: extraContext,
      environment: process.env.NODE_ENV,
      release: process.env.NEXT_PUBLIC_APP_VERSION,
    };

    // Send to logging endpoint
    await fetch("/api/log-error", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).catch(() => {
      // Silently fail if logging endpoint is unavailable
    });
  } catch {
    // Don't throw errors from error logging
  }
}

/**
 * React Error Boundary integration helper
 */
export function captureReactError(
  error: Error,
  errorInfo: { componentStack?: string },
): void {
  captureException(error, {
    componentStack: errorInfo.componentStack,
    tags: { framework: "react" },
  });
}
