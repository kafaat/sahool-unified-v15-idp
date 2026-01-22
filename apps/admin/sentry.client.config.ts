/**
 * Sentry Client Configuration
 * تكوين Sentry للعميل
 *
 * This file configures the initialization of Sentry on the client.
 * The config you add here will be used whenever a page is visited.
 *
 * Note: Sentry is only initialized when NEXT_PUBLIC_SENTRY_DSN is set.
 * This prevents OpenTelemetry warnings in development environments.
 */

import * as Sentry from "@sentry/nextjs";

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;

// Only initialize Sentry if DSN is properly configured
if (SENTRY_DSN && SENTRY_DSN.length > 0) {
  Sentry.init({
    dsn: SENTRY_DSN,

    // Environment
    environment: process.env.NODE_ENV,

    // App identification
    release: process.env.NEXT_PUBLIC_APP_VERSION || "1.0.0",

    // Performance Monitoring
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,

    // Session Replay (disabled by default for privacy)
    replaysSessionSampleRate: 0,
    replaysOnErrorSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 0,

    // Debug mode
    debug: process.env.NODE_ENV === "development",

    // Integrations
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],

    // Filter sensitive data before sending
    beforeSend(event) {
      // Remove sensitive headers
      if (event.request?.headers) {
        const headers = event.request.headers as Record<string, string>;
        delete headers["cookie"];
        delete headers["authorization"];
        delete headers["x-csrf-token"];
      }

      // Remove sensitive data from breadcrumbs
      if (event.breadcrumbs) {
        event.breadcrumbs = event.breadcrumbs.filter((breadcrumb) => {
          // Filter console breadcrumbs in production
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

    // Ignore common errors
    ignoreErrors: [
      // Browser extensions
      /^chrome-extension:\/\//,
      /^moz-extension:\/\//,
      // Network errors
      "Network request failed",
      "Failed to fetch",
      "Load failed",
      // ResizeObserver
      "ResizeObserver loop limit exceeded",
      "ResizeObserver loop completed with undelivered notifications",
    ],

    // Trace propagation
    tracePropagationTargets: [
      "localhost",
      /^https:\/\/.*\.sahool\.(app|io|ye)/,
    ],
  });
}

// Export utilities for user context (safe to call even when Sentry is not initialized)
export function setSentryUser(user: { id: string; email?: string }) {
  if (SENTRY_DSN && SENTRY_DSN.length > 0) {
    Sentry.setUser({
      id: user.id,
      // Don't send email to Sentry for privacy
    });
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
