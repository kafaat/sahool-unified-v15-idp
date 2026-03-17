/**
 * Next.js Instrumentation File
 * ملف أدوات القياس لـ Next.js
 *
 * Required by @sentry/nextjs v9+ for proper server and edge initialization.
 * Replaces the old sentry.server.config.ts and sentry.edge.config.ts pattern.
 *
 * @see https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation
 */

/** True when the error is a missing-module resolution failure. */
function isModuleNotFound(err: unknown): boolean {
  return (
    err instanceof Error &&
    "code" in err &&
    (err as NodeJS.ErrnoException).code === "MODULE_NOT_FOUND"
  );
}

export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    try {
      const Sentry = await import("@sentry/nextjs");

      const SENTRY_DSN =
        process.env.SENTRY_DSN || process.env.NEXT_PUBLIC_SENTRY_DSN;

      if (SENTRY_DSN && SENTRY_DSN.length > 0) {
        Sentry.init({
          dsn: SENTRY_DSN,
          environment: process.env.NODE_ENV,
          release: process.env.NEXT_PUBLIC_APP_VERSION || "1.0.0",
          tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,
          debug: false,

          integrations: [Sentry.httpIntegration()],

          beforeSend(event) {
            if (event.request?.headers) {
              const headers = event.request.headers as Record<string, string>;
              delete headers["cookie"];
              delete headers["authorization"];
              delete headers["x-csrf-token"];
              delete headers["x-api-key"];
            }

            if (event.request?.query_string) {
              const params = new URLSearchParams(event.request.query_string);
              params.delete("token");
              params.delete("access_token");
              params.delete("refresh_token");
              event.request.query_string = params.toString();
            }

            return event;
          },
        });
      }
    } catch (err: unknown) {
      if (!isModuleNotFound(err)) {
        console.warn("[sentry:nodejs] init failed:", err);
      }
    }
  }

  if (process.env.NEXT_RUNTIME === "edge") {
    try {
      const Sentry = await import("@sentry/nextjs");

      const SENTRY_DSN =
        process.env.SENTRY_DSN || process.env.NEXT_PUBLIC_SENTRY_DSN;

      if (SENTRY_DSN && SENTRY_DSN.length > 0) {
        Sentry.init({
          dsn: SENTRY_DSN,
          environment: process.env.NODE_ENV,
          release: process.env.NEXT_PUBLIC_APP_VERSION || "1.0.0",
          tracesSampleRate: process.env.NODE_ENV === "production" ? 0.05 : 0.5,
          debug: false,

          beforeSend(event) {
            if (event.request?.headers) {
              const headers = event.request.headers as Record<string, string>;
              delete headers["cookie"];
              delete headers["authorization"];
              delete headers["x-csrf-token"];
            }

            return event;
          },
        });
      }
    } catch (err: unknown) {
      if (!isModuleNotFound(err)) {
        console.warn("[sentry:edge] init failed:", err);
      }
    }
  }
}

/**
 * Capture errors from nested React Server Components.
 * Required by @sentry/nextjs v9+ for proper error reporting.
 *
 * @see https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/#errors-from-nested-react-server-components
 */
export async function onRequestError(
  ...args: unknown[]
): Promise<void> {
  try {
    const Sentry = await import("@sentry/nextjs");
    if (typeof Sentry.captureRequestError === "function") {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      await (Sentry.captureRequestError as (...a: any[]) => any)(...args);
    }
  } catch (err: unknown) {
    if (!isModuleNotFound(err)) {
      console.warn("[sentry] captureRequestError failed:", err);
    }
  }
}
