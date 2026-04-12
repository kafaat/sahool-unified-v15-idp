# SAHOOL Services — OpenAPI Coverage Catalog

> Last synced: 2026-04-12 · Branch: `claude/wave1-openapi-specs` · CONTRACT_VERSION `4.12.0`

## Summary

| Metric | Count |
|---|---|
| Total services | 48 |
| ✅ Fully specified | 2 |
| ⏳ In progress | 0 |
| ❌ Planned | 46 |
| **Coverage** | **4.2%** |

## Legend

- ✅ — Full OpenAPI 3.1 spec, Spectral passing, examples present
- ⏳ — Partial spec OR spec exists but fails Spectral
- ❌ — Planned, not started

---

## Services catalog

### 🏛️ Core Services (8)

| Service | Port | Lang | Spec | Coverage | Priority | Notes |
|---|---|---|---|---|---|---|
| partner-auth-service | 3030 | NestJS | ✅ [partner-auth.openapi.yaml](services/partner-auth.openapi.yaml) | 100% | — | OAuth 2.0 / OIDC v4.12.0 |
| user-service | 3025 | NestJS | ✅ [user-service.openapi.yaml](services/user-service.openapi.yaml) | 100% | — | JWT HS256 + 2FA + 17 endpoints |
| field-management-service | 3000 | NestJS | ❌ | 0% | Tier 1 | Planned — `claude/wave1-field-mgmt-openapi` |
| marketplace-service | 3010 | NestJS | ❌ | 0% | Tier 2 | Agricultural marketplace |
| research-core | 3015 | NestJS | ❌ | 0% | Tier 3 | Research trials |
| disaster-assessment | 3020 | NestJS | ❌ | 0% | Tier 3 | Disaster risk assessment |
| billing-core | 8089 | Python | ❌ | 0% | Tier 2 | Billing & invoicing |
| notification-service | 8110 | Python | ❌ | 0% | Tier 2 | Push notifications |

### 🧠 Intelligence Layer (17)

| Service | Port | Lang | Spec | Coverage | Priority | Notes |
|---|---|---|---|---|---|---|
| vegetation-analysis-service | 8090 | Python | ❌ | 0% | Tier 1 | NDVI — highest partner interest |
| indicators-service | 8091 | Python | ❌ | 0% | Tier 3 | Field indicators computation |
| weather-service | 8092 | Python | ❌ | 0% | Tier 1 | Weather data |
| advisory-service | 8093 | Python | ❌ | 0% | Tier 1 | Advisory & recommendations |
| irrigation-smart | 8094 | Python | ❌ | 0% | Tier 1 | Smart irrigation |
| crop-intelligence-service | 8095 | Python | ❌ | 0% | Tier 1 | Crop health AI |
| ndvi-processor | 8118 | Python | ❌ | 0% | Tier 3 | Deprecating → vegetation-analysis-service |
| virtual-sensors | 8119 | Python | ❌ | 0% | Tier 3 | Virtual sensor computation |
| field-intelligence | 8120 | Python | ❌ | 0% | Tier 3 | Field analytics |
| skills-service | 8121 | Python | ❌ | 0% | Tier 3 | Farmer skills assessment |
| soil-analysis-service | 8134 | Python | ❌ | 0% | Tier 1 | Soil analysis |
| pest-detection-service | 8125 | Python | ❌ | 0% | Tier 3 | Pest detection AI |
| digital-twin-engine | 8253 | Python | ❌ | 0% | Tier 3 | Digital twin simulation |
| lai-estimation | 3022 | Node.js | ❌ | 0% | Tier 3 | Leaf Area Index |
| yield-prediction-service | 8152 | Node.js | ❌ | 0% | Tier 3 | Yield prediction ML (NestJS) |
| yield-prediction-legacy | 3021 | Node.js | ❌ | 0% | Tier 3 | Legacy, sunset planned |
| crop-growth-model | 3023 | Node.js | ❌ | 0% | Tier 3 | Crop growth simulation |

### 🎯 Decision & Advisory (1)

| Service | Port | Lang | Spec | Coverage | Priority | Notes |
|---|---|---|---|---|---|---|
| agro-rules | 8151 | Python | ❌ | 0% | Tier 3 | Agronomic rules engine |

### 💼 Business Operations (7)

| Service | Port | Lang | Spec | Coverage | Priority | Notes |
|---|---|---|---|---|---|---|
| task-service | 8103 | Python | ❌ | 0% | Tier 2 | Task management |
| equipment-service | 8101 | Python | ❌ | 0% | Tier 2 | Equipment tracking |
| alert-service | 8113 | Python | ❌ | 0% | Tier 2 | Alert management |
| audit-service | 8114 | Python | ❌ | 0% | Tier 3 | Audit logging |
| provider-config | 8104 | Python | ❌ | 0% | Tier 3 | Provider configuration |
| inventory-service | 8116 | Python | ❌ | 0% | Tier 3 | Inventory management |
| chat-service | 8115 | Node.js | ❌ | 0% | Tier 2 | Real-time messaging |

### 📡 IoT & Integration (8)

| Service | Port | Lang | Spec | Coverage | Priority | Notes |
|---|---|---|---|---|---|---|
| iot-service | 8117 | Node.js | ❌ | 0% | Tier 2 | IoT device management |
| iot-gateway | 8106 | Python | ❌ | 0% | Tier 2 | IoT protocol gateway |
| iot-sensor-hub | 8251 | Python | ❌ | 0% | Tier 3 | IoT sensor hub |
| ws-gateway | 8081 | Python | ❌ | 0% | Tier 2 | WebSocket gateway |
| astronomical-calendar | 8111 | Python | ❌ | 0% | Tier 3 | Islamic calendar & timings |
| drone-service | 8126 | Python | ❌ | 0% | Tier 2 | Drone fleet & VRA |
| ussd-gateway | 8183 | Python | ❌ | 0% | Tier 3 | USSD gateway |
| whatsapp-bot-service | 8240 | Python | ❌ | 0% | Tier 3 | WhatsApp bot integration |

### 🤝 Community & Social (7)

| Service | Port | Lang | Spec | Coverage | Priority | Notes |
|---|---|---|---|---|---|---|
| cooperative-service | 8127 | Python | ❌ | 0% | Tier 2 | Cooperative management |
| globalgap-compliance | 8128 | Python | ❌ | 0% | Tier 2 | GlobalGAP IFA v6 compliance |
| traceability-service | 8123 | Python | ❌ | 0% | Tier 2 | Product traceability |
| crm-service | 8131 | Python | ❌ | 0% | Tier 2 | Farmer CRM |
| logistics-service | 8167 | Python | ❌ | 0% | Tier 3 | Logistics management |
| supply-chain-service | 8230 | Python | ❌ | 0% | Tier 3 | Supply chain management |
| wechat-service | 8133 | Python | ❌ | 0% | Tier 3 | WeChat integration |

### 🤖 AI & Agents (11)

| Service | Port | Lang | Spec | Coverage | Priority | Notes |
|---|---|---|---|---|---|---|
| agent-registry | 8160 | Python | ❌ | 0% | Tier 3 | Agent registry |
| code-fix-agent | 8162 | Python | ❌ | 0% | Tier 3 | Code fix AI agent |
| code-review-service | 8102 | Python | ❌ | 0% | Tier 3 | Code review service |
| ai-advisor | 8112 | Python | ❌ | 0% | Tier 3 | AI advisory service |
| ai-agents-core | 8161 | Python | ❌ | 0% | Tier 3 | AI agents core module |
| ai-agents-service | 8130 | Python | ❌ | 0% | Tier 3 | AI agents service |
| ai-chat-assistant | 8260 | Python | ❌ | 0% | Tier 3 | AI chat assistant |
| llm-orchestrator-service | 8164 | Python | ❌ | 0% | Tier 3 | LLM orchestration |
| copilot-api | 8088 | Python | ❌ | 0% | Tier 3 | AI copilot (multi-LLM, RAG) |
| knowledge-graph | 8140 | Python | ❌ | 0% | Tier 3 | Knowledge graph |
| mcp-server | 8201 | Python | ❌ | 0% | Tier 3 | Model Context Protocol |

### 👁️ Vision, Terrain & Edge (7)

| Service | Port | Lang | Spec | Coverage | Priority | Notes |
|---|---|---|---|---|---|---|
| yolo26-vision-service | 8150 | Python | ❌ | 0% | Tier 1 | Pest/disease/weed detection (CUDA) |
| ground-vision-service | 8182 | Python | ❌ | 0% | Tier 3 | Ground-level vision analysis |
| terrain-core-service | 8185 | Python | ❌ | 0% | Tier 3 | DEM processing |
| hydrology-service | 8165 | Python | ❌ | 0% | Tier 3 | Hydrology & drainage |
| leveling-optimizer-service | 8170 | Python | ❌ | 0% | Tier 3 | Field leveling optimization |
| edge-orchestrator-service | 8180 | Python | ❌ | 0% | Tier 3 | Jetson Orin edge management |
| vllm-deepseek | 8270 | Python | ❌ | 0% | Tier 3 | vLLM inference server |

### 🔧 Specialized (5)

| Service | Port | Lang | Spec | Coverage | Priority | Notes |
|---|---|---|---|---|---|---|
| fertigation-engine | 8252 | Python | ❌ | 0% | Tier 3 | Fertigation management |
| irrigation-cycle-engine | 8250 | Python | ❌ | 0% | Tier 3 | Irrigation cycle optimization |
| lowcode-engine | 8132 | Python | ❌ | 0% | Tier 3 | Low-code workflow automation |
| demo-data | 8261 | Python | ❌ | 0% | Tier 3 | Demo data generator |
| code-review-agent | 8145 | Node.js | ❌ | 0% | Tier 3 | Code review agent (NestJS) |

---

## Priority rubric

Three tiers drive authoring order. Every service lands in exactly one tier; move a service up only when partner demand or a regulatory deadline justifies it.

### Tier 1 — Ship first (highest partner value)

Authentication, core field entity, and the top analytical services partners evaluate during integration. These nine specs must ship before any Tier 2 spec is merged.

- `user-service` — auth identity, foundational for every other call
- `field-management-service` — the canonical field resource
- `vegetation-analysis-service` — NDVI, highest partner interest
- `weather-service` — referenced by nearly every agronomic workflow
- `advisory-service` — recommendation envelope shape sets the tone
- `crop-intelligence-service` — crop health AI surface
- `irrigation-smart` — irrigation scheduling contracts
- `soil-analysis-service` — soil test ingest & interpretation
- `yolo26-vision-service` — vision detection endpoints

### Tier 2 — Ship second (business-critical)

Services that unblock commerce, notifications, IoT onboarding, compliance, and operational tooling. Start once Tier 1 is green across Spectral + Redocly.

- `marketplace-service`, `billing-core`, `traceability-service`
- `chat-service`, `notification-service`, `cooperative-service`
- `iot-service`, `iot-gateway`, `drone-service`, `ws-gateway`
- `globalgap-compliance`, `crm-service`
- `task-service`, `equipment-service`, `alert-service`

> Note: `carbon-service` is listed as a Tier 2 candidate in the rubric but is not yet present in `service-ports.ts`; defer until the port is allocated.

### Tier 3 — Ship when needed

Everything else — AI agents, research, demo data, specialized engines, regional channels (USSD / WhatsApp / WeChat), logistics, supply-chain, legacy yield-prediction, and internal-only code-review surfaces. These specs ship opportunistically, driven by a concrete partner or internal consumer request.

---

## Authoring checklist

Every new `api/services/<service>.openapi.yaml` must satisfy this checklist before merge. CI (`openapi-validation.yml`) enforces steps 4, 7, 9, and 11.

1. **Exhaustive controller sweep** — read every controller, router, and handler in `apps/services/<service>/src/`. Capture each route, method, path param, query param, header, and body schema.
2. **Contract cross-reference** — every path, port, and error code must match `@sahool/shared-types/contracts` (`service-ports.ts`, `api-endpoints.ts`, `error-codes.ts`). Local constants are a merge blocker.
3. **Schema definitions** — every request and response body defined under `components/schemas`. No inline object schemas beyond trivial `{ ok: true }` acks.
4. **Security schemes** — import `BearerAuth`, `PartnerOAuth2`, and `TenantHeader` from `gateway-openapi.yaml` via `$ref`. Do not redefine.
5. **Operation tags** — use the SAHOOL tag catalog defined in `.spectral.yaml`. Unknown tags fail lint.
6. **Examples** — at least one 2xx response example per operation. Prefer realistic agricultural payloads (NDVI 0.62, Urea 46 kg/ha, etc.).
7. **Error envelope** — every 4xx and 5xx response references `PartnerErrorEnvelope` (partner-facing) or `ApiError` (internal). Include bilingual EN/AR messages.
8. **Catalog update** — add or update the row in this `SERVICES.md`. Bump `CONTRACT_VERSION` (patch for additive, minor for structural, major for breaking).
9. **Spectral lint** — `npx @stoplight/spectral-cli lint api/services/<service>.openapi.yaml` must exit 0 with zero errors and zero warnings.
10. **Redocly preview** — `npx @redocly/cli build-docs api/services/<service>.openapi.yaml` must render without broken refs. Eyeball the HTML.
11. **Info block extensions** — include `x-service-name`, `x-service-port`, and `x-contract-version` in `info`. The CI guard reads these to keep this catalog honest.

---

## Tracking & reporting

- **This file is the source of truth.** Update it in the same PR that adds or modifies `api/services/*.openapi.yaml`. No catalog update = no merge.
- **CI enforcement.** `openapi-validation.yml` runs Spectral on every PR that touches `api/**`. It also diffs `x-contract-version` against `packages/shared-types/src/contracts/index.ts` and fails on drift.
- **Monthly review.** On the first Monday of each month, open a GitHub issue titled `OpenAPI Coverage H1 2026 — <YYYY-MM>` that lists Tier 1 and Tier 2 progress, blocked services, and any newly discovered endpoints. Close the prior month's issue with a link forward.
- **Coverage metric.** Computed as `✅ / total`. `⏳` does not count toward coverage. When coverage crosses 25%, 50%, 75%, and 100%, post to `#sahool-api-partners` and tag the partner-auth working group.
- **Deprecation interlock.** When a service moves to the deprecated list in `CLAUDE.md`, mark its row here with a strikethrough and link the successor spec. Do not delete the row until sunset.

---

_Maintained by the API Platform team. Questions → `#sahool-api-platform`._
