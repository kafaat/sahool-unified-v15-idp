/**
 * Next.js Client Instrumentation File
 * ملف أدوات القياس للعميل
 *
 * Required by @sentry/nextjs v9+ for proper client-side initialization.
 * Replaces the old sentry.client.config.ts pattern.
 *
 * Bundle Optimizations:
 * - Replay integration removed (saves ~60-70KB gzipped) - only loaded on-error
 * - BrowserTracing kept as it is essential for performance monitoring
 * - Debug logging disabled (tree-shaken by withSentryConfig disableLogger: true)
 * - DSN guard prevents initialization when no DSN is configured
 *
 * @see https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation-client
 */

import * as Sentry from "@sentry/nextjs";

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;

// Only initialize Sentry if DSN is properly configured
if (SENTRY_DSN && SENTRY_DSN.length > 0) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: process.env.NODE_ENV,
    release: process.env.NEXT_PUBLIC_APP_VERSION || "1.0.0",
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,

    // Session Replay - lazy-loaded only on error to reduce initial bundle
    replaysSessionSampleRate: 0,
    replaysOnErrorSampleRate:
      process.env.NODE_ENV === "production" ? 0.1 : 0,

    debug: false,

    // Only BrowserTracing is loaded eagerly
    integrations: [Sentry.browserTracingIntegration()],

    // Filter sensitive data before sending
    beforeSend(event) {
      if (event.request?.headers) {
        const headers = event.request.headers as Record<string, string>;
        delete headers["cookie"];
        delete headers["authorization"];
        delete headers["x-csrf-token"];
      }

      if (event.breadcrumbs) {
        event.breadcrumbs = event.breadcrumbs.filter((breadcrumb) => {
          if (
            process.env.NODE_ENV === "production" &&
            breadcrumb.category === "console"
          ) {
            return false;
          }
          return true;
        });
      }

      return event;
    },

    ignoreErrors: [
      /^chrome-extension:\/\//,
      /^moz-extension:\/\//,
      "Network request failed",
      "Failed to fetch",
      "Load failed",
      "ResizeObserver loop limit exceeded",
      "ResizeObserver loop completed with undelivered notifications",
    ],

    tracePropagationTargets: [
      "localhost",
      /^https:\/\/.*\.sahool\.(app|io|ye)/,
    ],
  });
}

// Navigation instrumentation hook required by @sentry/nextjs v9+
export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;

// Re-export utilities for user context (safe to call even when Sentry is not initialized)
export function setSentryUser(user: { id: string; email?: string }) {
  if (SENTRY_DSN && SENTRY_DSN.length > 0) {
    Sentry.setUser({ id: user.id });
  }
}

export function clearSentryUser() {
  if (SENTRY_DSN && SENTRY_DSN.length > 0) {
    Sentry.setUser(null);
  }
}

export function setSentryContext(
  name: string,
  context: Record<string, unknown>,
) {
  if (SENTRY_DSN && SENTRY_DSN.length > 0) {
    Sentry.setContext(name, context);
  }
}
