/**
 * Sentry Server Configuration
 * تكوين Sentry للخادم
 *
 * This file configures the initialization of Sentry on the server.
 * The config you add here will be used whenever the server handles a request.
 */

import * as Sentry from '@sentry/nextjs';

const SENTRY_DSN = process.env.SENTRY_DSN || process.env.NEXT_PUBLIC_SENTRY_DSN;

Sentry.init({
  dsn: SENTRY_DSN,

  // Environment
  environment: process.env.NODE_ENV,

  // App identification
  release: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',

  // Performance Monitoring
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,

  // Debug mode
  debug: false, // Don't spam server logs

  // Filter sensitive data
  beforeSend(event) {
    // Remove sensitive headers
    if (event.request?.headers) {
      const headers = event.request.headers as Record<string, string>;
      delete headers['cookie'];
      delete headers['authorization'];
      delete headers['x-csrf-token'];
      delete headers['x-api-key'];
    }

    // Remove query params that might contain tokens
    if (event.request?.query_string) {
      const params = new URLSearchParams(event.request.query_string);
      params.delete('token');
      params.delete('access_token');
      params.delete('refresh_token');
      event.request.query_string = params.toString();
    }

    return event;
  },

  // Server-specific integrations
  integrations: [
    Sentry.httpIntegration(),
  ],
});

// Export utilities for server-side error capture
export function captureServerException(
  error: Error,
  context?: Record<string, unknown>
) {
  Sentry.withScope((scope) => {
    if (context) {
      scope.setExtras(context);
    }
    scope.setTag('app', 'sahool-web');
    scope.setTag('runtime', 'server');
    Sentry.captureException(error);
  });
}

export function captureServerMessage(
  message: string,
  level: Sentry.SeverityLevel = 'info',
  context?: Record<string, unknown>
) {
  Sentry.withScope((scope) => {
    if (context) {
      scope.setExtras(context);
    }
    scope.setTag('app', 'sahool-web');
    scope.setTag('runtime', 'server');
    Sentry.captureMessage(message, level);
  });
}

export function addServerBreadcrumb(
  message: string,
  category: string,
  data?: Record<string, unknown>
) {
  Sentry.addBreadcrumb({
    message,
    category,
    level: 'info',
    data,
  });
}
