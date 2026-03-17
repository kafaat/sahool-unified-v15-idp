/**
 * Empty shim for @sentry/nextjs when the package is not installed.
 *
 * Webpack's `resolve.alias: { "@sentry/nextjs": false }` creates a module
 * reference with no factory function, which causes "Cannot read properties
 * of undefined (reading 'call')" at runtime.  Pointing the alias at this
 * file instead gives webpack a real module to bundle.
 */
export {};
