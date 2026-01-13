/**
 * SAHOOL Admin Logging Utility
 * أداة تسجيل سجلات لوحة الإدارة
 *
 * Provides environment-aware logging that:
 * - Only logs in development mode by default
 * - Provides critical logging for production errors
 * - Integrates with error tracking service
 */

const isDev = process.env.NODE_ENV === "development";

export const logger = {
  /**
   * Log general information (development only)
   * تسجيل معلومات عامة (بيئة التطوير فقط)
   */
  log: (...args: any[]) => {
    if (isDev) {
      console.log(...args);
    }
  },

  /**
   * Log errors (development only)
   * تسجيل الأخطاء (بيئة التطوير فقط)
   */
  error: (...args: any[]) => {
    if (isDev) {
      console.error(...args);
    }
  },

  /**
   * Log warnings (development only)
   * تسجيل التحذيرات (بيئة التطوير فقط)
   */
  warn: (...args: any[]) => {
    if (isDev) {
      console.warn(...args);
    }
  },

  /**
   * Log debug information (development only)
   * تسجيل معلومات التصحيح (بيئة التطوير فقط)
   */
  debug: (...args: any[]) => {
    if (isDev) {
      console.debug(...args);
    }
  },

  /**
   * Log informational messages (development only)
   * تسجيل رسائل إعلامية (بيئة التطوير فقط)
   */
  info: (...args: any[]) => {
    if (isDev) {
      console.info(...args);
    }
  },

  /**
   * Create a console group (development only)
   * إنشاء مجموعة في وحدة التحكم (بيئة التطوير فقط)
   */
  group: (...args: any[]) => {
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
   * and should be sent to an error tracking service.
   */
  critical: (...args: any[]) => {
    // Always log critical errors
    console.error(...args);

    // TODO: Send to error tracking service in production
    // Example: Sentry.captureException(args[0]);
    // Example: Send to custom error logging endpoint
  },

  /**
   * Production-safe error logging
   * تسجيل الأخطاء الآمن للإنتاج
   *
   * Logs errors to console in development,
   * sends structured logs in production
   */
  production: (...args: any[]) => {
    if (isDev) {
      console.log(...args);
    } else {
      // In production, send to logging service
      // This prevents exposing sensitive information in console
      console.error(
        JSON.stringify({
          level: "error",
          service: "sahool-admin",
          timestamp: new Date().toISOString(),
          message: args,
        }),
      );
    }
  },
};

export default logger;
