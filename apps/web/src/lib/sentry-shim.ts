/**
 * No-op shim for @sentry/nextjs when the package is not installed.
 *
 * Webpack's `resolve.alias` points "@sentry/nextjs" at this file so that
 * `import * as Sentry from "@sentry/nextjs"` resolves to real (inert) exports
 * instead of blowing up at runtime.
 *
 * Every function used across the codebase is stubbed here as a safe no-op.
 */


const noop = (..._args: unknown[]): undefined => undefined;
const noopIntegration = (..._args: unknown[]) => ({ name: 'noop' });

// Core lifecycle
export const init = noop;
export const close = noop;
export const flush = noop;

// Error & message capture
export const captureException = noop;
export const captureMessage = noop;
export const captureEvent = noop;
export const captureRequestError = noop;

// Scope helpers
export const setUser = noop;
export const setContext = noop;
export const setTag = noop;
export const setTags = noop;
export const setExtra = noop;
export const setExtras = noop;
export const withScope = (cb: (scope: unknown) => void) => cb({});
export const configureScope = noop;

// Integrations referenced in instrumentation files
export const browserTracingIntegration = noopIntegration;
export const httpIntegration = noopIntegration;

// Router transition hook (instrumentation-client.ts exports this directly)
export const captureRouterTransitionStart = noop;

// Next.js wrappers
export const withSentryConfig = <T>(config: T): T => config;
