/**
 * Sentry Configuration for Frontend
 * إعدادات Sentry للواجهة الأمامية
 */

import * as Sentry from '@sentry/nextjs';

export interface SentryConfig {
  dsn: string;
  environment: string;
  release?: string;
  tracesSampleRate?: number;
  replaysSessionSampleRate?: number;
  replaysOnErrorSampleRate?: number;
}

/**
 * Initialize Sentry for error tracking
 * تهيئة Sentry لتتبع الأخطاء
 */
export function initSentry(config: SentryConfig): void {
  const {
    dsn,
    environment,
    release,
    tracesSampleRate = 0.1,
    replaysSessionSampleRate = 0.1,
    replaysOnErrorSampleRate = 1.0,
  } = config;

  if (!dsn) {
    console.warn('Sentry DSN not provided - error tracking disabled');
    return;
  }

  Sentry.init({
    dsn,
    environment,
    release,

    // Performance Monitoring
    tracesSampleRate,

    // Session Replay
    replaysSessionSampleRate,
    replaysOnErrorSampleRate,

    // Integrations
    integrations: [
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],

    // Filter out non-critical errors
    beforeSend(event: Sentry.ErrorEvent, hint: Sentry.EventHint) {
      const error = hint.originalException as Error;

      // Ignore network errors that are often user-side
      if (error?.message?.includes('Network Error')) {
        return null;
      }

      // Ignore aborted requests
      if (error?.name === 'AbortError') {
        return null;
      }

      return event;
    },

    // Don't send PII
    beforeBreadcrumb(breadcrumb: Sentry.Breadcrumb): Sentry.Breadcrumb | null {
      // Remove sensitive data from breadcrumbs
      if (breadcrumb.category === 'xhr' || breadcrumb.category === 'fetch') {
        if (breadcrumb.data?.url?.includes('password')) {
          return null;
        }
      }
      return breadcrumb;
    },
  });
}

/**
 * Set user context for Sentry
 * تعيين سياق المستخدم لـ Sentry
 */
export function setUserContext(user: {
  id: string;
  email?: string;
  tenantId?: string;
  roles?: string[];
}): void {
  Sentry.setUser({
    id: user.id,
    email: user.email,
    // Custom context
    tenant_id: user.tenantId,
    roles: user.roles?.join(','),
  });
}

/**
 * Clear user context on logout
 * مسح سياق المستخدم عند تسجيل الخروج
 */
export function clearUserContext(): void {
  Sentry.setUser(null);
}

/**
 * Set additional context
 * تعيين سياق إضافي
 */
export function setContext(name: string, context: Record<string, unknown>): void {
  Sentry.setContext(name, context);
}

/**
 * Add breadcrumb for debugging
 * إضافة breadcrumb للتصحيح
 */
export function addBreadcrumb(
  message: string,
  category: string,
  level: Sentry.SeverityLevel = 'info',
  data?: Record<string, unknown>
): void {
  Sentry.addBreadcrumb({
    message,
    category,
    level,
    data,
    timestamp: Date.now() / 1000,
  });
}

/**
 * Capture exception with additional context
 * التقاط استثناء مع سياق إضافي
 */
export function captureException(
  error: Error,
  context?: {
    tags?: Record<string, string>;
    extra?: Record<string, unknown>;
    level?: Sentry.SeverityLevel;
  }
): string {
  return Sentry.captureException(error, {
    tags: context?.tags,
    extra: context?.extra,
    level: context?.level,
  });
}

/**
 * Capture message
 * التقاط رسالة
 */
export function captureMessage(
  message: string,
  level: Sentry.SeverityLevel = 'info',
  context?: Record<string, unknown>
): string {
  return Sentry.captureMessage(message, {
    level,
    extra: context,
  });
}

/**
 * Start performance transaction
 * بدء معاملة الأداء
 */
export function startTransaction(
  name: string,
  op: string
): Sentry.Span | undefined {
  return Sentry.startInactiveSpan({
    name,
    op,
  });
}

/**
 * Create child span
 * إنشاء span فرعي
 */
export function startSpan<T>(
  options: { name: string; op: string },
  callback: (span: Sentry.Span | undefined) => T
): T {
  return Sentry.startSpan(options, callback);
}

export { Sentry };
