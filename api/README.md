# SAHOOL API Specifications

**CONTRACT_VERSION**: `4.12.0`
**Branch**: `claude/wave1-openapi-specs` (Wave 1 — #5)
**Last updated**: 2026-04-12

---

## Overview | نظرة عامة

**English** — This directory is the canonical home for every OpenAPI specification the SAHOOL platform ships. It contains the unified gateway-level contract (`gateway-openapi.yaml`, fronted by Kong) and a per-service subdirectory where each microservice publishes its own OpenAPI 3.1 document. The specs here are the **single source of truth** for HTTP surfaces: partners, SDK generators, mobile clients, AI agents, and internal services all resolve endpoint shapes, request/response schemas, auth scopes, and error codes from these files — not from hand-written client code.

Everything here is tightly coupled to `packages/shared-types/src/contracts/` (TypeScript). The TS contracts define ports, error codes, endpoint paths, and response envelopes; the OpenAPI files import them conceptually (same names, same shapes) so that a breaking change flagged by `api-contracts-guard.yml` will also surface here. When adding a new endpoint, always bump the relevant TS contract first, then mirror the change into the service's OpenAPI spec, then regenerate SDKs.

**العربية** — هذا الدليل هو المرجع الرسمي الوحيد لكل مواصفات OpenAPI في منصة SAHOOL. يحتوي على عقد البوابة الموحد (`gateway-openapi.yaml`) ومجلد فرعي لكل خدمة ميكروية تنشر فيه مواصفاتها الخاصة بصيغة OpenAPI 3.1. تعتبر هذه الملفات **مصدر الحقيقة الوحيد** لكل واجهات HTTP: الشركاء، مولدات SDK، تطبيقات الجوال، وكلاء الذكاء الاصطناعي، والخدمات الداخلية — جميعها تستند إلى هذه الملفات.

كل ما هنا مرتبط ارتباطًا وثيقًا بـ `packages/shared-types/src/contracts/`. عند إضافة نقطة نهاية جديدة، يجب أولًا تحديث عقود TypeScript، ثم عكس التغيير في مواصفات OpenAPI للخدمة، ثم إعادة توليد SDK.

---

## Directory layout

```
api/
├── gateway-openapi.yaml            # Unified gateway spec (Kong-level, 550 lines)
├── services/                       # Per-service specs (48 services target)
│   ├── partner-auth.openapi.yaml   # OAuth 2.0 / OIDC (v4.12.0) — ✅ shipped
│   └── ... (more as they ship)
├── README.md                       # this file — entry point
├── SERVICES.md                     # catalog of all services + spec status
└── .spectral.yaml                  # OpenAPI linting rules (Spectral)
```

- **`gateway-openapi.yaml`** — aggregated, Kong-facing view of the public surface. Useful for partners who only talk to `api.sahool.app` and don't care about internal service boundaries.
- **`services/*.openapi.yaml`** — one file per service, matching the service's package name (e.g. `partner-auth-service` → `partner-auth.openapi.yaml`). These are the authoritative per-service specs and drive SDK generation.
- **`.spectral.yaml`** — shared linting rules (naming, security requirements, response envelope). Enforced in CI via `.github/workflows/openapi-validation.yml`.
- **`SERVICES.md`** — living catalog tracking coverage across all 48 services.

---

## Quick start for partners

All examples below assume:

- Gateway host: `https://api.sahool.app`
- Partner client credentials: `PARTNER_CLIENT_ID`, `PARTNER_CLIENT_SECRET`
- Redirect URI: `https://partner.example.com/callback`

### 1. Authorization Code → Token exchange

```bash
# Step 1: Redirect the farmer to the authorization endpoint
#   https://api.sahool.app/oauth/authorize?
#     response_type=code
#     &client_id=$PARTNER_CLIENT_ID
#     &redirect_uri=https%3A%2F%2Fpartner.example.com%2Fcallback
#     &scope=fields:read+advisory:read+offline_access
#     &state=xyz123
#     &code_challenge=$PKCE_CHALLENGE
#     &code_challenge_method=S256

# Step 2: Exchange the authorization code for tokens
curl -X POST https://api.sahool.app/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "$PARTNER_CLIENT_ID:$PARTNER_CLIENT_SECRET" \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE_FROM_CALLBACK" \
  -d "redirect_uri=https://partner.example.com/callback" \
  -d "code_verifier=$PKCE_VERIFIER"

# Response:
# {
#   "access_token":  "eyJhbGciOiJSUzI1NiIs...",
#   "token_type":    "Bearer",
#   "expires_in":    3600,
#   "refresh_token": "rt_7f3c...",
#   "id_token":      "eyJhbGc...",
#   "scope":         "fields:read advisory:read offline_access"
# }
```

### 2. Calling a protected endpoint

```bash
# Fetch the farmer's fields (through field-management-service, via gateway)
curl -X GET "https://api.sahool.app/api/v1/fields" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/json" \
  -H "Accept-Language: ar-SA,en;q=0.8" \
  -H "X-Request-Id: $(uuidgen)"
```

The gateway validates the JWT signature, checks the required scope
(`fields:read`), extracts `tid` (tenant id), and proxies to the
downstream service with a propagated `X-Tenant-Id` header.

### 3. Refresh token rotation

```bash
curl -X POST https://api.sahool.app/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "$PARTNER_CLIENT_ID:$PARTNER_CLIENT_SECRET" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=$REFRESH_TOKEN"
```

> ⚠️ Refresh tokens are **single-use**. The old token is revoked
> immediately and a new one is issued. Store the new `refresh_token`
> from the response or your next refresh will fail.

### 4. Token revocation (logout)

```bash
curl -X POST https://api.sahool.app/oauth/revoke \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "$PARTNER_CLIENT_ID:$PARTNER_CLIENT_SECRET" \
  -d "token=$ACCESS_TOKEN_OR_REFRESH_TOKEN" \
  -d "token_type_hint=access_token"
```

### 5. Discovery & JWKS

```bash
# OIDC discovery document
curl https://api.sahool.app/.well-known/openid-configuration

# JWKS — rotate your cached keys hourly
curl https://api.sahool.app/.well-known/jwks.json
```

---

## SDK generation

Use `openapi-generator-cli` v7+. Install once:

```bash
npm install -g @openapitools/openapi-generator-cli
```

### TypeScript / Axios

```bash
npx @openapitools/openapi-generator-cli generate \
  -i api/services/partner-auth.openapi.yaml \
  -g typescript-axios \
  -o sdks/typescript/partner-auth \
  --additional-properties=supportsES6=true,withInterfaces=true,useSingleRequestParameter=true
```

Output: `sdks/typescript/partner-auth/`
Post-install:

```bash
cd sdks/typescript/partner-auth && npm install && npm run build
```

Usage:

```ts
import { Configuration, OAuthApi } from "@sahool/sdk-partner-auth";

const api = new OAuthApi(new Configuration({
  basePath: "https://api.sahool.app",
  accessToken: async () => currentToken(),
}));

const { data } = await api.tokenPost({ grantType: "refresh_token", refreshToken });
```

### Python (httpx)

```bash
npx @openapitools/openapi-generator-cli generate \
  -i api/services/partner-auth.openapi.yaml \
  -g python \
  -o sdks/python/partner-auth \
  --additional-properties=packageName=sahool_partner_auth,library=asyncio,generateSourceCodeOnly=false
```

Output: `sdks/python/partner-auth/`
Post-install:

```bash
cd sdks/python/partner-auth && pip install -e .
```

### Dart / Dio (mobile)

```bash
npx @openapitools/openapi-generator-cli generate \
  -i api/services/partner-auth.openapi.yaml \
  -g dart-dio \
  -o sdks/dart/partner_auth \
  --additional-properties=pubName=sahool_partner_auth,pubVersion=4.12.0,nullSafe=true
```

Output: `sdks/dart/partner_auth/`
Post-install:

```bash
cd sdks/dart/partner_auth && dart pub get && dart run build_runner build
```

The Dart SDK integrates with `apps/mobile/lib/core/contracts/` (generated from TS contracts via `npx tsx scripts/sync-contracts-to-dart.ts`).

### Go

```bash
npx @openapitools/openapi-generator-cli generate \
  -i api/services/partner-auth.openapi.yaml \
  -g go \
  -o sdks/go/partner-auth \
  --additional-properties=packageName=partnerauth,packageVersion=4.12.0,generateInterfaces=true
```

Output: `sdks/go/partner-auth/`
Post-install:

```bash
cd sdks/go/partner-auth && go mod tidy
```

### Java

```bash
npx @openapitools/openapi-generator-cli generate \
  -i api/services/partner-auth.openapi.yaml \
  -g java \
  -o sdks/java/partner-auth \
  --additional-properties=library=okhttp-gson,java8=true,dateLibrary=java8,groupId=app.sahool,artifactId=partner-auth-sdk,artifactVersion=4.12.0
```

Output: `sdks/java/partner-auth/`
Post-install:

```bash
cd sdks/java/partner-auth && mvn install
```

### C# / .NET

```bash
npx @openapitools/openapi-generator-cli generate \
  -i api/services/partner-auth.openapi.yaml \
  -g csharp-netcore \
  -o sdks/csharp/partner-auth \
  --additional-properties=packageName=Sahool.PartnerAuth,packageVersion=4.12.0,targetFramework=net8.0,netCoreProjectFile=true
```

Output: `sdks/csharp/partner-auth/`
Post-install:

```bash
cd sdks/csharp/partner-auth/src/Sahool.PartnerAuth && dotnet build
```

### Auth setup (all languages)

Generated SDKs expose an `accessToken` or `Configuration.AccessToken` field. Supply it **dynamically** (as a callback / provider) so refreshed tokens propagate without restarting the client:

- TS/JS: `new Configuration({ accessToken: async () => store.getToken() })`
- Python: `Configuration(access_token=lambda: get_token())`
- Dart: `OpenAPI.dio.options.headers["Authorization"] = "Bearer $token"`
- Go: pass `context.WithValue(ctx, sw.ContextAccessToken, token)`
- Java: `defaultClient.setBearerToken(token)`
- C#: `Configuration.Default.AccessToken = token;`

---

## Linting & validation

### Spectral (rule-based OpenAPI linting)

```bash
npx @stoplight/spectral-cli lint api/services/partner-auth.openapi.yaml
npx @stoplight/spectral-cli lint "api/services/*.openapi.yaml"
```

Rules live in `api/.spectral.yaml`. They enforce:

- `operationId` must be camelCase and unique
- Every operation must declare at least one `4xx` response
- All responses must use the unified envelope (`ApiResponse`, `ErrorResponse`)
- Security requirements must reference a declared scheme
- Tags must match the service domain (e.g. `auth`, `oauth`, `admin`)

### Redocly (bundling + validation + doc preview)

```bash
# Validate (stricter than Spectral on $ref resolution)
npx @redocly/cli lint api/services/partner-auth.openapi.yaml

# Bundle all $refs into a single file (useful for publishing)
npx @redocly/cli bundle api/services/partner-auth.openapi.yaml -o dist/partner-auth.bundled.yaml

# Preview as HTML docs in the browser (http://localhost:8080)
npx @redocly/cli preview-docs api/services/partner-auth.openapi.yaml

# Build static HTML bundle
npx @redocly/cli build-docs api/services/partner-auth.openapi.yaml \
  -o dist/partner-auth.html
```

### Quick sanity check before commit

```bash
# from repo root
for f in api/services/*.openapi.yaml api/gateway-openapi.yaml; do
  echo "→ $f"
  npx @stoplight/spectral-cli lint "$f" && \
  npx @redocly/cli lint "$f" || exit 1
done
```

---

## CI validation

Every PR that touches `api/**` is validated by
`.github/workflows/openapi-validation.yml` (shipped by a parallel
Wave 1 branch). It runs, in order:

1. **Spectral** on every `*.openapi.yaml`
2. **Redocly lint** on every `*.openapi.yaml`
3. **Breaking-change diff** (`@redocly/cli diff`) vs. `main`
4. **Contract consistency** — cross-checks that every `operationId` referenced in `packages/shared-types/src/contracts/api-endpoints.ts` has a matching operation in the OpenAPI file
5. **SDK generation smoke test** — generates a TypeScript SDK and compiles it

A failed check blocks merge. For emergency fixes, waivers require two CODEOWNERS approvals on the `api/` path.

---

## Contribution guide

When adding (or amending) a service's OpenAPI spec:

1. **Read the service first.** Study its controllers:
   - NestJS: `apps/services/<name>/src/**/*.controller.ts`
   - FastAPI: `apps/services/<name>/src/api/v1/*.py`
2. **Reference TS contracts.** Any path, port, error code, or response envelope must already exist in:
   - `packages/shared-types/src/contracts/service-ports.ts` (ports)
   - `packages/shared-types/src/contracts/api-endpoints.ts` (paths)
   - `packages/shared-types/src/contracts/error-codes.ts` (error codes, bilingual)
   - `packages/shared-types/src/contracts/api-responses.ts` (envelope shapes)
   If it does not exist there, stop and add it to the TS contracts first.
3. **Name the file** `<service-short-name>.openapi.yaml`. Drop the `-service` suffix (e.g. `partner-auth-service` → `partner-auth.openapi.yaml`).
4. **Use `info.version`** that matches `CONTRACT_VERSION` at the time of writing. Bump on every new spec change:
   - **Patch** — internal doc tweaks, example fixes
   - **Minor** — new additive endpoint, optional field
   - **Major** — removed endpoint, required field change, auth change
5. **Reuse components.** Refer to the shared `components` library (coming in Wave 2) via `$ref`; do not duplicate error schemas.
6. **Bilingual errors.** Every `4xx`/`5xx` example must include `message` (English) and `message_ar` (Arabic).
7. **Security.** Declare the auth scheme per-operation. Default is `bearerAuth` (JWT from Kong). Mark public endpoints with `security: []`.
8. **Health endpoints.** Always include `/healthz` and `/readyz` with `security: []` and operation tag `health`.
9. **Add an entry to [`SERVICES.md`](SERVICES.md).** Move the service row from `❌` → `⏳` (in-progress) → `✅` (published).
10. **Bump `CONTRACT_VERSION`** in `packages/shared-types/src/contracts/index.ts` if new endpoints or fields were introduced.
11. **Run locally:**
    ```bash
    npx @stoplight/spectral-cli lint api/services/<name>.openapi.yaml
    npx @redocly/cli lint api/services/<name>.openapi.yaml
    ```
12. **Open a PR** with the `api-change` label. CI will validate; CODEOWNERS for `api/` will review.

### Required sections in every service spec

```yaml
openapi: 3.1.0
info:
  title: <Service Name>
  version: 4.12.0
  description: <one-paragraph EN + AR>
  contact:
    name: SAHOOL Platform Team
    email: platform@sahool.app
  license:
    name: Proprietary (KAFAAT)
servers:
  - url: https://api.sahool.app
    description: Production (via Kong)
  - url: https://staging-api.sahool.app
    description: Staging
  - url: http://localhost:{port}
    description: Local dev
    variables:
      port:
        default: "3030"
security:
  - bearerAuth: []
tags: [...]
paths: {...}
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas: {...}
  responses:
    ErrorResponse: { $ref: "../shared/errors.yaml#/ErrorResponse" }
```

---

## References

| Resource | URL |
|---|---|
| **OpenAPI 3.1 spec** | <https://spec.openapis.org/oas/v3.1.0> |
| **AsyncAPI** (future: NATS event specs) | <https://www.asyncapi.com/docs/reference/specification/latest> |
| **JSON Schema** | <https://json-schema.org/specification.html> |
| **Stoplight Spectral** | <https://meta.stoplight.io/docs/spectral> |
| **Redocly CLI** | <https://redocly.com/docs/cli/> |
| **OpenAPI Generator** | <https://openapi-generator.tech/docs/generators/> |
| **OAuth 2.0 RFC 6749** | <https://datatracker.ietf.org/doc/html/rfc6749> |
| **OIDC Core** | <https://openid.net/specs/openid-connect-core-1_0.html> |
| **PKCE RFC 7636** | <https://datatracker.ietf.org/doc/html/rfc7636> |
| **RFC 8594 Sunset Header** | <https://datatracker.ietf.org/doc/html/rfc8594> |
| **SAHOOL API Gateway docs** | [`docs/API_GATEWAY.md`](../docs/API_GATEWAY.md) |
| **SAHOOL TS contracts** | [`packages/shared-types/src/contracts/`](../packages/shared-types/src/contracts/) |
| **SAHOOL service registry** | [`governance/services.yaml`](../governance/services.yaml) |

---

_Maintained by the SAHOOL Platform Team · Proprietary (KAFAAT) · Questions: `#platform-api` on Slack_
