# SAHOOL Low-Code Builder Production Sprint Plan

This plan moves the current SAHOOL Low-Code PoC toward a production internal builder while preserving the original constraints: design tokens only, approved OpenAPI operations only, Tenant Context, RBAC, unified response handling, and no automatic Flutter package additions.

## Week 1: Widget Tests and PoC Hardening

| Day | Deliverable |
| --- | --- |
| 1 | Generate widget tests for the existing `analyzeSatelliteGeometry` form. |
| 2 | Add guardrail tests for missing Tenant Context and missing RBAC permission. |
| 3 | Add validation and successful-submit payload tests. |
| 4 | Add SAHOOL linter checks that generated tests exist. |
| 5 | Run targeted Flutter tests where the Flutter SDK is available and document gaps. |

## Week 2: Schema Registry Adapter

| Day | Deliverable |
| --- | --- |
| 1 | Add `schema-registry/registry.json` as the central spec index. |
| 2 | Add approved operation whitelist files. |
| 3 | Add template mappings for forms, card lists, and table views. |
| 4 | Add registry validation script. |
| 5 | Wire registry validation into `npm run lint:sahool`. |

## Weeks 3-4: GET View Generation

| Day | Deliverable |
| --- | --- |
| 1 | Add OpenAPI GET view generator skeleton. |
| 2 | Generate Card list for approved list operations with pagination and filters. |
| 3 | Add DataTable mode guarded by pagination, filtering, and sorting requirements. |
| 4 | Add generated view smoke checks to SAHOOL linter. |
| 5 | Add view docs and sample usage. |
| 6-10 | Expand approved GET operations incrementally after spec readiness review. |

## Week 5: Tenant Context Verification

| Day | Deliverable |
| --- | --- |
| 1 | Define Tenant Context adapter interface for generated widgets. |
| 2 | Connect adapter to tenant-service contract. |
| 3 | Add tenant language, timezone, and unit settings to generated widget inputs. |
| 4 | Add active-plan checks without hardcoding tenant plans in generated code. |
| 5 | Add tests for inactive tenant and unsupported plan handling. |

## Week 6: RBAC Service Integration

| Day | Deliverable |
| --- | --- |
| 1 | Define Permission Service adapter interface for generated widgets. |
| 2 | Map OpenAPI operation IDs to resource/action pairs. |
| 3 | Replace caller-provided permission sets with async permission checks. |
| 4 | Add tests for deny, allow, and service error paths. |
| 5 | Document approved RBAC mapping rules. |

## Week 7: Unified Response Handling

| Day | Deliverable |
| --- | --- |
| 1 | Add generated client adapter constrained to unified response schema. |
| 2 | Add field error mapping for form widgets. |
| 3 | Add global error handling for `UnifiedApiException` only. |
| 4 | Add tests for field errors, global errors, and success payloads. |
| 5 | Add linter check rejecting generic `catch` in generated code. |

## Week 8: Production Readiness Gate

| Day | Deliverable |
| --- | --- |
| 1 | Add registry review checklist for approving new operations. |
| 2 | Add generated-code diff review guide. |
| 3 | Run security and linter gates on all generated assets. |
| 4 | Produce coverage report for generated widget tests. |
| 5 | Publish production rollout notes for the first 10 approved endpoints. |

## Persistent Constraints

- No UI generation without Tenant Context.
- No API call generation without unified response schema handling.
- No automatic Flutter package additions.
- No colors or typography outside SAHOOL tokens.
- No generated screen bypassing RBAC.
- No NDVI or skill output treated as diagnostic truth without confidence and freshness.
