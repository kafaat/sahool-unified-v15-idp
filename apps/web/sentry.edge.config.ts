/**
 * Sentry Edge Configuration
 * تكوين Sentry لـ Edge Runtime
 *
 * This file configures the initialization of Sentry for edge features (Middleware, Edge Route handlers).
 * The config you add here will be used whenever middleware handles a request.
 */

import * as Sentry from '@sentry/nextjs';

const SENTRY_DSN = process.env.SENTRY_DSN || process.env.NEXT_PUBLIC_SENTRY_DSN;

Sentry.init({
  dsn: SENTRY_DSN,

  // Environment
  environment: process.env.NODE_ENV,

  // App identification
  release: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',

  // Lower sample rate for edge to reduce overhead
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.05 : 0.5,

  // Debug mode
  debug: false,

  // Filter sensitive data
  beforeSend(event) {
    // Remove sensitive headers
    if (event.request?.headers) {
      const headers = event.request.headers as Record<string, string>;
      delete headers['cookie'];
      delete headers['authorization'];
      delete headers['x-csrf-token'];
    }

    return event;
  },
});

// Export utility for edge error capture
export function captureEdgeException(
  error: Error,
  context?: Record<string, unknown>
) {
  Sentry.withScope((scope) => {
    if (context) {
      scope.setExtras(context);
    }
    scope.setTag('app', 'sahool-web');
    scope.setTag('runtime', 'edge');
    Sentry.captureException(error);
  });
}
