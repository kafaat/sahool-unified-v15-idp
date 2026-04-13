/**
 * SAHOOL Unified API Contracts
 * العقود الموحدة لواجهة برمجة التطبيقات
 *
 * Barrel export for all contract modules.
 *
 * @module @sahool/shared-types/contracts
 * @version 16.0.0
 */

/**
 * Contract version - bump on every change.
 * MAJOR: breaking change (removed endpoint, changed port)
 * MINOR: addition (new endpoint, new error code)
 * PATCH: fix (typo in message, documentation)
 */
// 4.12.1 — fix FIELD_ENDPOINTS.BOUNDARY* (was hitting non-existent
//          `/api/v1/field-core/...` route — caught by the 2026-04-13
//          end-to-end vertical-slice review).
export const CONTRACT_VERSION = "4.12.1" as const;

export * from './service-ports';
export * from './error-codes';
export * from './api-endpoints';
export * from './api-responses';
