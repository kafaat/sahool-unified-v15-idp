/**
 * Next.js Instrumentation File
 * ملف أدوات القياس لـ Next.js
 *
 * Required by @sentry/nextjs v9+ for proper server and edge initialization.
 * Replaces the old sentry.server.config.ts and sentry.edge.config.ts pattern.
 *
 * @see https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation
 */

/**
 * True only when @sentry/nextjs itself is the missing module.
 * Transitive dependency failures (e.g. a Sentry sub-package missing) are
 * NOT swallowed — they are logged so monitoring doesn't silently disappear.
 * This mirrors the stricter check used in next.config.js.
 */
function isSentryMissing(err: unknown): boolean {
  if (!(err instanceof Error) || !("code" in err)) return false;
  const code = (err as NodeJS.ErrnoException).code;
  return (
    (code === "MODULE_NOT_FOUND" || code === "ERR_MODULE_NOT_FOUND") &&
    /['"]@sentry\/nextjs['"]/.test(err.message)
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
      if (!isSentryMissing(err)) {
        console.warn("[sentry] init failed:", err);
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
      if (!isSentryMissing(err)) {
        console.warn("[sentry] init failed:", err);
      }
    }
  }
}

/**
 * Capture errors from nested React Server Components.
 * Required by @sentry/nextjs v9+ for proper error reporting.
 *
 * Uses a dynamic wrapper because @sentry/nextjs is an optional dependency.
 * A static re-export would fail the build/runtime if the package is absent.
 *
 * @see https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/#errors-from-nested-react-server-components
 */
export async function onRequestError(
  ...args: unknown[]
): Promise<void> {
  try {
    const Sentry = await import("@sentry/nextjs");
    if (typeof Sentry.captureRequestError === "function") {
      await (Sentry.captureRequestError as (...a: any[]) => any)(...args);
    }
  } catch (err: unknown) {
    if (!isSentryMissing(err)) {
      console.warn("[sentry] captureRequestError failed:", err);
    }
  }
}
