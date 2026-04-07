/**
 * SAHOOL Logging Utility
 * أداة تسجيل سجلات النظام
 *
 * Provides environment-aware logging that:
 * - Only logs in development mode by default
 * - Provides critical logging for production errors
 * - Integrates with error tracking service (when configured)
 */

const isDev = process.env.NODE_ENV === 'development';

// Sentry DSN check - only load Sentry when properly configured
const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;
const isSentryEnabled = Boolean(SENTRY_DSN && SENTRY_DSN.length > 0);

/** Minimal Sentry interface for the methods we actually use */
interface SentryLike {
  captureException(error: unknown, hint?: { extra?: Record<string, unknown> }): string;
  captureMessage(
    message: string,
    captureContext?: { level?: string; extra?: Record<string, unknown> }
  ): string;
}

// Lazy-loaded Sentry module to avoid OpenTelemetry issues when not configured
let SentryModule: SentryLike | null = null;

async function getSentry(): Promise<SentryLike | null> {
  if (!isSentryEnabled) return null;
  if (SentryModule) return SentryModule;

  try {
    const mod = await import('@sentry/nextjs');
    // Validate the module actually exposes the methods we need.
    // When @sentry/nextjs is aliased to `false` (webpack) the import
    // resolves to an empty module instead of throwing.
    if (
      typeof (mod as Record<string, unknown>).captureException === 'function' &&
      typeof (mod as Record<string, unknown>).captureMessage === 'function'
    ) {
      SentryModule = mod as SentryLike;
      return SentryModule;
    }
    if (isDev) {
      console.warn(
        '[Logger] @sentry/nextjs loaded but missing expected methods, continuing without error tracking'
      );
    }
    return null;
  } catch (error) {
    // Sentry import failed - continue without it
    if (isDev) {
      console.warn('[Logger] Sentry import failed, continuing without error tracking:', error);
    }
    return null;
  }
}

export const logger = {
  /**
   * Log general information (development only)
   * تسجيل معلومات عامة (بيئة التطوير فقط)
   */
  log: (...args: unknown[]) => {
    if (isDev) {
      console.log(...args);
    }
  },

  /**
   * Log errors (all environments)
   * تسجيل الأخطاء (جميع البيئات)
   *
   * In production, errors are logged as structured JSON to avoid exposing
   * sensitive details while still capturing actionable information.
   */
  error: (...args: unknown[]) => {
    if (isDev) {
      console.error(...args);
    } else {
      // In production, log structured JSON to avoid exposing sensitive details
      console.error(
        JSON.stringify({
          level: 'error',
          service: 'sahool-web',
          timestamp: new Date().toISOString(),
          message: args[0] instanceof Error ? args[0].message : String(args[0]),
        })
      );
    }
  },

  /**
   * Log warnings (development only)
   * تسجيل التحذيرات (بيئة التطوير فقط)
   */
  warn: (...args: unknown[]) => {
    if (isDev) {
      console.warn(...args);
    }
  },

  /**
   * Log debug information (development only)
   * تسجيل معلومات التصحيح (بيئة التطوير فقط)
   */
  debug: (...args: unknown[]) => {
    if (isDev) {
      console.debug(...args);
    }
  },

  /**
   * Log informational messages (development only)
   * تسجيل رسائل إعلامية (بيئة التطوير فقط)
   */
  info: (...args: unknown[]) => {
    if (isDev) {
      console.info(...args);
    }
  },

  /**
   * Create a console group (development only)
   * إنشاء مجموعة في وحدة التحكم (بيئة التطوير فقط)
   */
  group: (...args: unknown[]) => {
    if (isDev) {
      console.group(...args);
    }
  },

  /**
   * End a console group (development only)
   * إنهاء مجموعة في وحدة التحكم (بيئة التطوير فقط)
   */
  groupEnd: () => {
    if (isDev) {
      console.groupEnd();
    }
  },

  /**
   * Critical errors that should always be logged
   * الأخطاء الحرجة التي يجب تسجيلها دائمًا
   *
   * These are logged in both development and production,
   * and should be sent to an error tracking service (when configured).
   */
  critical: (...args: unknown[]) => {
    // Always log critical errors
    console.error(...args);

    // Send to error tracking service in production (if Sentry is configured)
    if (!isDev && isSentryEnabled) {
      const firstArg = args[0];
      const extraData = args.slice(1);

      // Use async Sentry loading to avoid blocking and OpenTelemetry issues
      getSentry()
        .then((Sentry) => {
          if (!Sentry) return;

          if (firstArg instanceof Error) {
            // Handle Error objects
            Sentry.captureException(firstArg, {
              extra: extraData.length > 0 ? { context: extraData } : undefined,
            });
          } else if (typeof firstArg === 'string') {
            // Handle string messages
            Sentry.captureMessage(firstArg, {
              level: 'error',
              extra: extraData.length > 0 ? { context: extraData } : undefined,
            });
          } else {
            // Handle other types (objects, etc.)
            Sentry.captureMessage('Critical error occurred', {
              level: 'error',
              extra: { context: args },
            });
          }
        })
        .catch(() => {
          // Silently fail if Sentry cannot be loaded
        });
    }
  },

  /**
   * Production-safe error logging
   * تسجيل الأخطاء الآمن للإنتاج
   *
   * Logs errors to console in development,
   * sends structured logs in production
   */
  production: (...args: unknown[]) => {
    if (isDev) {
      console.log(...args);
    } else {
      // In production, send to logging service
      // This prevents exposing sensitive information in console
      console.error(
        JSON.stringify({
          level: 'error',
          service: 'sahool-web',
          timestamp: new Date().toISOString(),
          message: args,
        })
      );
    }
  },
};

export default logger;
