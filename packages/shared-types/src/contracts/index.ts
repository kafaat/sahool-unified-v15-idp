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
// 4.16.0 — expand web feature surface so the remaining 9 feature-API files
//          can stop hardcoding `/api/v1/…`:
//          * SEED_ENDPOINTS: RECOMMENDATIONS
//          * IRRIGATION_ENDPOINTS: EFFICIENCY_REPORT, IRRIGATION_EXECUTED,
//            CALCULATE_WITH_ACTION, PIVOT_SPEED
//          * ADVISORY_ENDPOINTS: SPRAY_WINDOWS
//          * EPIDEMIC_ENDPOINTS (new): LIST, GET, REPORT
//          * LEVELING_ENDPOINTS (new): ANALYZE, PLAN, COST, EQUIPMENT,
//            SIMULATE (field-scoped leveling-optimizer-service surface)
//          * PRECISION_ENDPOINTS (new): VRA, GDD, FERTILIZER_CALCULATE
//          * SATELLITE_MONITOR_ENDPOINTS (new): FIELDS, FIELD_GET, STATS,
//            ALERTS (dashboard aggregator, distinct from SATELLITE_ENDPOINTS)
//          Purely additive.
// 4.17.0 — expand mobile feature surface for remaining repos:
//          * GDD_ENDPOINTS (new): ACCUMULATION, RECORDS, CALCULATE,
//            CURRENT_STAGE, STAGES, CROPS, CROP_REQUIREMENTS, FORECAST,
//            SETTINGS, COMPARE, TREND
//          * GAMIFICATION_ENDPOINTS (new): PROFILE, LEADERBOARD
//          * LAB_ENDPOINTS (new): SAMPLES, SAMPLE_BY_BARCODE
//          * PAYMENT_ENDPOINTS (new): Tharwatt wallet integration
//            (DEPOSIT/WITHDRAW/TRANSFER/TOPUP/STATUS/TRANSACTIONS/
//            BALANCE/VALIDATE_PHONE/OPERATORS/CANCEL). Distinct from
//            BILLING_ENDPOINTS which covers Stripe + platform wallet.
//          Purely additive.
// 4.18.0 — close governance gaps from the unified-API audit:
//          * SERVICE_HEALTH_ENDPOINTS (new): per-service Kong-routed
//            /healthz paths, used by web Service Health Dashboard.
//          * HYDROLOGY_ENDPOINTS (new): drainage, watershed, flow,
//            stream-network, rainfall-runoff, infiltration. TERRAIN_ENDPOINTS
//            HYDROLOGY_* entries marked @deprecated (aliased).
//          * VEGETATION_ENDPOINTS (new): NDVI, EVI, SAVI, NDWI, LAI,
//            chlorophyll, timeseries, stress-map. Split out from
//            SATELLITE_ENDPOINTS for dedicated vegetation-analysis-service.
//          * DRONE_ENDPOINTS expanded 4 → 17 (flight lifecycle, telemetry,
//            VRA application, device registration).
//          * SOIL_ENDPOINTS expanded with per-field moisture/salinity/pH
//            /nutrients paths and analysis interpretation.
//          * WIP_SERVICES marker introduced for task/vision/drone services
//            (consumed by scripts/endpoint-reality-check.ts).
//          * COMMUNITY_CHAT, NDVI_PROCESSOR, YIELD_PREDICTION_LEGACY ports
//            tagged @deprecated with explicit removal version (v3.0.0 →
//            re-baselined to v5.0.0 to honour main's 4.x cadence).
//          Purely additive.
// 4.19.0 - AUDIT_ENDPOINTS extended with three endpoints audit-service
//          has been serving since the audit-service consolidation PR
//          but had no typed representation:
//          * RESOURCE_TRAIL (/audit/resources/{resourceType}/{resourceId}/trail)
//            — reverse-chronological trail with skip+limit-only
//            pagination. NOT used by the admin Field Audit History
//            panel because it can't honour the page's category /
//            user / date-range filters; that panel hits LOGS with
//            `resource_type` + `resource_id` pinned in the query
//            string instead. Exported for future callers that
//            genuinely want the unfiltered trail.
//          * USER_TRAIL     (/audit/users/{userId}/trail)
//            — same skip+limit-only constraint, user-scoped.
//          * CHAIN_VALIDATE (/audit/chain/validate)
//          Purely additive; no existing exports removed.
// 4.20.0 - SATELLITE_ENDPOINTS extended with two endpoints that back the
//          map-visualization upgrade (Phase 1 + 2):
//          * INDEX_MAP  (/satellite/v1/indices/{fieldId}/{indexName}/map)
//            — raster-tile metadata per index so the MapLibre layer can
//            render any of NDVI / NDRE / NDWI / EVI / SAVI / LAI, not
//            just hard-coded NDVI. Returns `{rasterUrl, bounds,
//            colorScale, label, unit, dataSource}`.
//          * INDEX_PIXEL (/satellite/v1/indices/{fieldId}/pixel)
//            — all 44 computed indices at a given lat/lon, powering the
//            EOSDA/OneSoil-style click-to-inspect popup.
//          Purely additive; no existing exports removed.
// 4.21.0 - SATELLITE_ENDPOINTS extended with three multi-date endpoints
//          (Phase 3) that close the "no N-date comparison" gap vs
//          EOSDA / OneSoil:
//          * INDEX_COMPOSITE (/satellite/v1/indices/{fieldId}/{indexName}/composite)
//            — N-day median/mean composite with p25/p75 envelopes.
//          * INDEX_FILMSTRIP (/satellite/v1/indices/{fieldId}/{indexName}/filmstrip)
//            — thumbnail carousel metadata (date + rasterUrl + value +
//            status), cadence-controlled + capped at ~20 frames.
//          * INDEX_MULTI_COMPARE (/satellite/v1/indices/{fieldId}/{indexName}/multi-date-compare)
//            — compare the same index across up to 12 dates, with
//            `delta_from_previous` computed server-side.
//          Purely additive; no existing exports removed. The legacy
//          `/v1/ndvi-timeseries/compare` stays in place for backwards
//          compatibility but new callers should use INDEX_MULTI_COMPARE.
export const CONTRACT_VERSION = "4.21.0" as const;

export * from './service-ports';
export * from './error-codes';
export * from './api-endpoints';
export * from './api-responses';
