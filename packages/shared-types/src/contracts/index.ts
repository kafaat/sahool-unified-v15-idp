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
// 4.20.0 — extend SATELLITE_MONITOR_ENDPOINTS with six endpoints that
//          were previously hardcoded in satellite-monitor/api.ts:
//          * FIELD_PEST_PREDICTIONS   (/satellite-monitor/fields/{fieldId}/pest-predictions)
//          * FIELD_IRRIGATION_SCHEDULE(/satellite-monitor/fields/{fieldId}/irrigation-schedule)
//          * FIELD_YIELD_PREDICTION   (/satellite-monitor/fields/{fieldId}/yield-prediction)
//          * FIELD_HISTORICAL         (/satellite-monitor/fields/{fieldId}/historical)
//          * FIELD_SOIL_MOISTURE_SAR  (/satellite-monitor/fields/{fieldId}/soil-moisture-sar)
//          * FIELD_DOWNLOAD           (/satellite-monitor/fields/{fieldId}/download)
//          Purely additive.
// 4.21.0 — Phase 3: Unified Cross-Platform Data Contract
//          * Fix PHENOLOGY endpoint path: /satellite/phenology/ → /satellite/v1/phenology/
//            (was returning 404 because Kong strips /api/v1/satellite but backend
//             registers routes under /v1/phenology/{field_id} — the /v1/ prefix must
//             appear after the Kong strip-prefix)
//          * Add IndexMapResponse, CalendarDateEntry, IndexCalendarResponse,
//            IndexTileType, IndexDataSource to api-responses.ts — canonical DTOs
//            consumed identically by Web (useIndexMap) and Mobile (indexMapProvider).
//            Purely additive; no existing exports removed.
// 4.22.0 — Contract audit and gap-fill (purely additive):
//          * SERVICE_PORTS: add AGRO_RULES (8151), DEMO_DATA (8261),
//            CODE_REVIEW_AGENT (8145) — all referenced in endpoints /
//            health checks but were missing from the ports map.
//          * SERVICE_REGISTRY: add agro-rules, carbon-service,
//            partner-auth-service, demo-data, code-review-agent entries.
//          * SERVICE_PORT_ALIASES: add agroRules, partnerAuth,
//            carbonService, codeReviewAgent, demoData.
//          * SERVICE_HEALTH_ENDPOINTS: add VISION, TERRAIN, AUDIT, CARBON,
//            COPILOT, SOIL, DRONE, EDGE, HYDROLOGY, LEVELING (were missing
//            despite all having live kongRoutes in the registry).
//          * CRM_ENDPOINTS (new): FARMERS, FARMER_CREATE/GET/UPDATE/DELETE,
//            INTERACTIONS, SEGMENTS, NOTES, ANALYTICS — crm-service had a
//            registered port + Kong route but no typed endpoint group.
//          * ERROR_MESSAGES: add 7 missing Vision error entries:
//            E1003 VISION_INVALID_DIMENSIONS,
//            E1005 VISION_UNSUPPORTED_TYPE,
//            E1007 VISION_EMPTY_IMAGE,
//            E1009 VISION_CORRUPT_FILE,
//            E2004 VISION_MODEL_INCOMPATIBLE,
//            E2006 VISION_WARMUP_FAILED,
//            E3004 VISION_BATCH_FAILED.
// 4.23.0 — Direct code audit — real gaps fixed:
//          * SERVICE_PORTS: add SKILL_ROUTER (8205) — skill-router-service
//            exists at apps/services/skill-router-service/app/config.py but
//            was entirely absent from the contract.
//          * SERVICE_PORTS: add TEST_HARNESS_SIDECAR (8299) — test-only
//            sidecar (refuses production start) at
//            apps/services/test-harness-sidecar/src/config.py.
//          * ServiceInfo interface: make kongRoute optional; add 'worker'
//            to the type union — agro-rules is a pure NATS consumer worker
//            with no HTTP interface and should NOT have a kongRoute.
//          * SERVICE_REGISTRY['agro-rules']: remove incorrect kongRoute,
//            change type 'python' → 'worker' (actual code: worker.py + NATS).
//          * SERVICE_REGISTRY: add 'skill-router-service' entry.
//          * SERVICE_PORT_ALIASES: add skillRouter, testHarnessSidecar.
//          * CRM_ENDPOINTS: complete rewrite — previous version used wrong
//            /crm prefix (service registers routes at /api/v1/farmers,
//            /api/v1/deals, etc. — confirmed from crm-service/src/main.py).
//            Added missing: DEAL_CREATE, DEALS, DEAL_STAGE_UPDATE,
//            DEALS_PIPELINE, QUERY. Removed non-existent: FARMER_DELETE
//            (no DELETE handler), INTERACTION_GET (no GET-by-ID handler),
//            SEGMENTS, NOTES, ANALYTICS (all were incorrectly defined —
//            no matching handlers exist in crm-service/src/main.py).
//          * SKILL_ROUTER_ENDPOINTS (new): ROUTE, SKILLS — matches the
//            actual router in skill-router-service/app/router.py.
//          * SERVICE_HEALTH_ENDPOINTS: add SKILL_ROUTER, CRM.
export const CONTRACT_VERSION = "4.23.0" as const;

export * from './service-ports';
export * from './error-codes';
export * from './api-endpoints';
export * from './api-responses';
