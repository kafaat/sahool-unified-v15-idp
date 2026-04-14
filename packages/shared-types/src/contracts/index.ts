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
// 4.13.0 — add canonical auth request shapes (SendOtpRequest, VerifyOtpRequest,
//          LoginRequest, RegisterRequest, LogoutRequest, RefreshTokenRequest)
//          + OTP_PURPOSE/OTP_CHANNEL const enums. Fixes `otp` vs `otpCode`
//          and `reset` vs `password_reset` drift between web proxy routes
//          and user-service DTOs. Adds `login` as a valid OTP purpose for
//          passwordless OTP login on mobile + web.
// 4.14.0 — expand endpoint coverage so the web proxy routes under
//          apps/web/src/app/api/ can stop hardcoding `/api/v1/…` strings:
//          * ADVISORY_ENDPOINTS: field-scoped recommendations/disease-assess
//            /fertilizer-plan/crop-advice
//          * PEST_ENDPOINTS: new group for pest-detection-service
//            (LIST, BY_CROP, IDENTIFY, TREATMENT_RECOMMEND)
//          * SOIL_ENDPOINTS: TESTS_BY_FIELD, PRODUCTS, CROP_REQUIREMENTS,
//            INTERPRET, AMENDMENT_PLAN, PH_STATUS, EC_STATUS
//          * TASK_ENDPOINTS: ASSIGN
//          * TERRAIN_ENDPOINTS: DEM_FIELD, SLOPE_FIELD, TWI, CONTOURS, ANALYZE
//          * EQUIPMENT_ENDPOINTS: MAINTENANCE_SCHEDULE(_BY_ID), ISSUES
//          Purely additive; no renames, no removals.
// 4.15.0 — expand mobile surface so feature repositories stop hardcoding:
//          * BILLING_ENDPOINTS: DEPOSIT/WITHDRAW/TRANSFER (flat variants),
//            PAYMENTS, INVOICE_PAYMENT_INTENT, STRIPE_*, PAYMENT_METHOD*
//          * CHAT_ENDPOINTS: MUTE, REPORT, CLEAR_MESSAGES
//          * USER_ENDPOINTS: BLOCK
//          * EQUIPMENT_ENDPOINTS: ALERTS, LOCATION, TELEMETRY, FUEL,
//            FUEL_SUMMARY, USAGE, USAGE_START, USAGE_END, USAGE_SUMMARY
//          Purely additive.
export const CONTRACT_VERSION = "4.15.0" as const;

export * from './service-ports';
export * from './error-codes';
export * from './api-endpoints';
export * from './api-responses';
