/**
 * SAHOOL Admin API Base URL
 * Lightweight module exporting only the base URL constant.
 *
 * Auth pages (login, register, forgot-password, etc.) should import from
 * this file instead of `@/config/api` to avoid pulling the full service-port
 * and endpoint map (~800 lines, ~30 KB) into the auth bundle.
 *
 * @module config/api-base
 */

/**
 * Base URL for the API Gateway (Kong)
 * In production: Uses NEXT_PUBLIC_API_URL
 * In development: Falls back to localhost:8000 (Kong gateway port)
 */
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
