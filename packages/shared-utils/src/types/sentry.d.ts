/**
 * Sentry Type Declarations
 * Type declarations for @sentry/nextjs when not installed
 * This allows the package to compile without @sentry/nextjs as a hard dependency
 */

declare module '@sentry/nextjs' {
  export interface SentryUser {
    id?: string;
    email?: string;
    [key: string]: unknown;
  }

  export interface ErrorEvent {
    [key: string]: unknown;
  }

  export interface EventHint {
    originalException?: unknown;
  }

  export interface Breadcrumb {
    message?: string;
    category?: string;
    level?: SeverityLevel;
    data?: {
      url?: string;
      [key: string]: unknown;
    };
    timestamp?: number;
  }

  export interface Span {
    finish(): void;
    setStatus(status: string): void;
  }

  export type SeverityLevel = 'fatal' | 'error' | 'warning' | 'log' | 'info' | 'debug';

  export interface InitOptions {
    dsn?: string;
    environment?: string;
    release?: string;
    tracesSampleRate?: number;
    replaysSessionSampleRate?: number;
    replaysOnErrorSampleRate?: number;
    integrations?: unknown[];
    beforeSend?(event: ErrorEvent, hint: EventHint): ErrorEvent | null;
    beforeBreadcrumb?(breadcrumb: Breadcrumb): Breadcrumb | null;
  }

  export function init(options: InitOptions): void;
  export function setUser(user: SentryUser | null): void;
  export function setContext(name: string, context: Record<string, unknown>): void;
  export function addBreadcrumb(breadcrumb: Breadcrumb): void;
  export function captureException(error: Error, options?: { tags?: Record<string, string>; extra?: Record<string, unknown>; level?: SeverityLevel }): string;
  export function captureMessage(message: string, options?: { level?: SeverityLevel; extra?: Record<string, unknown> }): string;
  export function startInactiveSpan(options: { name: string; op: string }): Span | undefined;
  export function startSpan<T>(options: { name: string; op: string }, callback: (span: Span | undefined) => T): T;
  export function replayIntegration(options?: { maskAllText?: boolean; blockAllMedia?: boolean }): unknown;
}
