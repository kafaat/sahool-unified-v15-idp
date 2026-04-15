# Partner Auth Service — خادم مصادقة الشركاء

OAuth 2.0 + OpenID Connect authorization server for SAHOOL partner
integrations. **FieldView-compatible**: partners already integrated with
Climate FieldView can port with minimal changes (identical token response
shape, OIDC `id_token`, 4 h access-token TTL, 30 d refresh token with
1 h rotation window, `X-Api-Key` / `X-Sahool-Partner-Key` metering
header separate from OAuth).

- **Port**: `3030` (`SERVICE_PORTS.PARTNER_AUTH`)
- **Framework**: NestJS 10 + Prisma 5 + `jose` (RFC 7515/7517) + `bcryptjs`
- **DB**: PostgreSQL 16 + PgBouncer (transaction mode)
- **Contracts**: `@sahool/shared-types/contracts` → `PARTNER_OAUTH_ENDPOINTS`, `PARTNER_OAUTH_SCOPES`, `PARTNER_HEADERS`, `PARTNER_LIMITS`
- **Kong route**: `/partner/v1/*` and `/.well-known/*` → `partner-auth-service:3030`

## Status — ما يعمل / ما هو مُخطَّط

### ✅ Implemented
| Endpoint | Description | Since |
|---|---|---|
| `POST /partner/v1/oauth/token` | `authorization_code` + `refresh_token` grants with rotation + reuse detection | v1 |
| `GET /partner/v1/oauth/authorize` | Interactive consent screen (bilingual AR/EN, RTL-aware, CSRF-protected) | v2 |
| `POST /partner/v1/oauth/authorize` | Processes consent decision → 302 back to client | v2 |
| `POST /partner/v1/oauth/revoke` | RFC 7009 token revocation (silent on unknown tokens) | v2 |
| `POST /partner/v1/oauth/introspect` | RFC 7662 token introspection (`{active: false}` leak-proof) | v2 |
| `GET /partner/v1/oauth/userinfo` | OIDC UserInfo (Bearer-authenticated) | v2 |
| `GET /.well-known/openid-configuration` | OIDC discovery | v1 |
| `GET /.well-known/jwks.json` | Public key set (RSA, RS256) | v1 |
| `GET /healthz` `/readyz` `/health` | K8s probes + DB ping | v1 |

### ✅ Admin API (v3 — `claude/wave1-partner-auth-admin-api`)
| Endpoint | Description |
|---|---|
| `POST   /api/v1/admin/partner-auth/clients` | Register partner app — returns `client_secret` + `partnerApiKey` ONCE |
| `GET    /api/v1/admin/partner-auth/clients` | Paginated list (filter by `status=`, `name=`) |
| `GET    /api/v1/admin/partner-auth/clients/{id}` | Retrieve public metadata (never exposes hashes) |
| `PATCH  /api/v1/admin/partner-auth/clients/{id}` | Update name, redirect URIs, scopes, rate tier |
| `POST   /api/v1/admin/partner-auth/clients/{id}/rotate-secret` | New plaintext secret (one-time return) |
| `POST   /api/v1/admin/partner-auth/clients/{id}/rotate-api-key` | New plaintext X-Sahool-Partner-Key |
| `POST   /api/v1/admin/partner-auth/clients/{id}/suspend` | Block all flows (reversible) |
| `POST   /api/v1/admin/partner-auth/clients/{id}/unsuspend` | Reactivate a suspended client |
| `DELETE /api/v1/admin/partner-auth/clients/{id}` | Permanent revoke + cascade-revoke all tokens |
| `GET    /api/v1/admin/partner-auth/consents` | List/filter consent grants |
| `DELETE /api/v1/admin/partner-auth/consents/{grantId}` | Revoke a user's consent (GDPR Art. 17) |
| `GET    /api/v1/admin/partner-auth/tokens/access` | List active access tokens |
| `GET    /api/v1/admin/partner-auth/tokens/refresh` | List refresh tokens + rotation chains |
| `POST   /api/v1/admin/partner-auth/tokens/revoke-all/client/{id}` | Breach response — bulk revoke |
| `POST   /api/v1/admin/partner-auth/tokens/revoke-all/user/{id}` | User-wide forget-me across partners |
| `GET    /api/v1/admin/partner-auth/signing-keys` | List RSA signing keys (active + retired) |
| `POST   /api/v1/admin/partner-auth/signing-keys/rotate` | Hot-rotate the JWS signing key |
| `DELETE /api/v1/admin/partner-auth/signing-keys/{kid}` | Delete a fully-expired retired key |

All admin endpoints require `Authorization: Bearer <jwt>` with `role=ADMIN`
(or `roles` array containing `"ADMIN"`). Verified by `AdminGuard` against
`SAHOOL_SESSION_SECRET` (HS256, shared with user-service).

### ✅ Kong gateway wiring (v4 — `claude/wave1-partner-auth-kong-wiring`)

All 4 service blocks live in `infrastructure/gateway/kong/active/kong.yml`:

| Kong service block | Purpose | Rate limit |
|---|---|---|
| `partner-auth-oauth-public` | `/partner/v1/oauth/{token,authorize,revoke,introspect,userinfo}` | 30–120 req/min per IP (tighter on `/token`) |
| `partner-auth-wellknown` | `/.well-known/openid-configuration`, `/.well-known/jwks.json` | `proxy-cache` (1h + 15m respectively) |
| `partner-auth-admin` | `/api/v1/admin/partner-auth/*` (defense-in-depth `jwt` plugin) | 100 req/min, 2000 req/hour |
| `partner-auth-health` | `/healthz`, `/readyz`, `/health` (no auth, no rate limit) | — |

Validation: [`tests/integration/gateway/test_partner_auth_kong_routes.py`](../../tests/integration/gateway/test_partner_auth_kong_routes.py) checks the kong.yml structure stays in sync with the contract constants.

### ⏳ Planned (remaining branches)
| Feature | Branch |
|---|---|
| Admin web UI for partner registration | `claude/wave1-partner-portal-ui` |
| Custom Kong plugin for `X-Sahool-Partner-Key` → rate-tier lookup | `claude/wave1-partner-auth-kong-plugin` |
| Live user-service fetch in `/userinfo` (currently minimal claims) | `claude/wave1-partner-auth-userinfo-fresh` |
| Private-key at-rest encryption via Vault KEK | `claude/wave1-partner-auth-signing-key-kms` |

## Seeding local dev data

```bash
# From repo root, after DATABASE_URL is set and migrations applied
cd apps/services/partner-auth-service
npm run prisma:migrate    # creates tables
npm run prisma:seed       # creates RSA key + 2 dev partners
```

The seed prints `client_secret` + `partnerApiKey` to STDOUT **exactly once**.
Capture into your local `.env` — they cannot be retrieved later.

Sample output:
```
🌱 partner-auth-service seed starting…
  ✅ Signing key created: kid=Xk3m…
  ✅ Client created: sahool-sandbox-cli
  ✅ Client created: sahool-dev-portal

📋 Seed summary:
  • sahool-sandbox-cli
      client_secret:       sah_cs_<40-char-nanoid>
      X-Sahool-Partner-Key: sahk_<32-char-nanoid>
  • sahool-dev-portal
      client_secret:       sah_cs_<…>
      X-Sahool-Partner-Key: sahk_<…>

⚠️  Secrets are plaintext and shown ONCE only.
```

## /authorize consent flow

```
Partner opens:  https://api.sahool.com/partner/v1/oauth/authorize
                 ?response_type=code
                 &client_id=partner-leaf
                 &redirect_uri=https://leaf.example.com/cb
                 &scope=openid+fields:read+operations:harvest:read
                 &state=<csrf>  &nonce=<rp>
                 &code_challenge=<pkce>  &code_challenge_method=S256

  ┌─────────────────────────────────────────────────────────┐
  │ partner-auth-service /authorize (GET)                    │
  │   1. SahoolSessionGuard — check sahool_session cookie/hdr│
  │      ↳ if missing → 302 to SAHOOL login with return_to   │
  │   2. AuthorizeService.validateRequest                    │
  │      ↳ client exists + active + not revoked              │
  │      ↳ redirect_uri matches one of client.redirectUris   │
  │      ↳ response_type = "code"                            │
  │      ↳ requested scopes ⊆ client.allowedScopes           │
  │      ↳ PKCE method ∈ {S256, plain}                       │
  │   3. Check ConsentGrant memory                           │
  │      ↳ if prior grant covers requested scopes AND        │
  │        prompt != "consent" → SKIP screen, go to step 5   │
  │   4. Render bilingual consent HTML (scopes + Allow/Deny) │
  │   5. On Allow → mint AuthCode, upsert ConsentGrant,      │
  │        302 to redirect_uri?code=…&state=…                │
  │   5'. On Deny → 302 to redirect_uri?error=access_denied  │
  └─────────────────────────────────────────────────────────┘
```

### Consent-screen security

- Inline CSS only, no external resources, no JS required
- `frame-ancestors 'none'` + `X-Frame-Options: DENY` — clickjacking defense
- **CSRF** protected via stateless HMAC token tied to user id + issuance
  time; 15-minute TTL; constant-time signature compare
- Scope labels derived from a server-side lookup table (bilingual) — no
  client-side translation that could drift
- `noindex,nofollow` meta — consent URL must not be indexed

### Session integration

The `SahoolSessionGuard` accepts either:
- `X-Sahool-Session` header (JWT signed by user-service, HS256)
- `sahool_session` cookie with the same JWT

Required JWT claims: `sub` (user id), `tid` (tenant id). Optional:
`email`, `name`, `name_ar`, `locale`.

When missing/invalid, the guard sets `req.loginRedirect` to
`$SAHOOL_LOGIN_URL?return_to=<current_url>` and the controller 302s there.

## Authentication model

```
  ┌────────────────┐      Authorization: Bearer <at>      ┌──────────────────┐
  │ Partner client │  ──────────────────────────────────▶ │ SAHOOL partner   │
  │ (Leaf, SWAT,   │      X-Sahool-Partner-Key: <key>     │ microservices    │
  │  DroneDeploy,  │                                       │ (Kong-routed)    │
  │  ag retailers) │      X-Request-Id: <uuid>            │                  │
  └────────────────┘                                       └──────────────────┘
        │  ▲
        │  │ POST /partner/v1/oauth/token
        │  │ Authorization: Basic base64(client_id:client_secret)
        │  │ grant_type=authorization_code&code=…&redirect_uri=…
        ▼  │
  ┌──────────────────────┐
  │ partner-auth-service │  port 3030
  │ (this service)       │
  └──────────────────────┘
        │
        ▼
    PostgreSQL (oauth_clients, auth_codes, access_tokens,
                refresh_tokens, consent_grants, signing_keys)
```

- **Identity** lives in `Authorization: Bearer <access_token>` — OAuth 2.0 / OIDC.
- **Metering** lives in `X-Sahool-Partner-Key` — Stripe/Shopify-style.
- The two are **decoupled** so a partner can rotate their metering key without invalidating active OAuth sessions, and vice versa.

## Token lifetimes (FieldView parity)

| Token | TTL | Rotation |
|---|---|---|
| Access token (JWT) | 4 h | Re-issued each `/token` call |
| Refresh token | 30 d | On use → new one issued, old re-TTL'd to **1 h** |
| Authorization code | 10 min | Single-use; replay triggers cascade revoke |
| id_token | 4 h | Same key as access token |

## Refresh-token rotation & reuse detection (OAuth 2.1 § 6)

When a refresh token is exchanged:

1. Old refresh token's row is updated: `rotated_to_id = <new_id>`, `expires_at = now + 1h`.
2. New refresh token is issued, same `family_id` as old.
3. If the **old** token is submitted again (already rotated), the service **cascade-revokes the entire `family_id`** — all access tokens + all refresh tokens in the chain. Partner must re-authorize.

This mitigates refresh-token theft: an attacker's stolen token is detected the moment the legitimate partner refreshes.

## Security notes

- **Client secrets** are bcrypt-hashed at registration.
- **Authorization codes** and **refresh tokens** are stored as SHA-256 hashes, never plaintext.
- **PKCE** (RFC 7636, S256 + plain) is supported for public clients.
- **CSRF / state** is the partner's responsibility per OAuth 2.0 § 10.12.
- **helmet** sets `frame-ancestors 'none'` to prevent consent-screen clickjacking.
- **No tokens** are ever logged, even at DEBUG (see `RequestLoggingInterceptor.redact`).

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `3030` | HTTP listen port |
| `NODE_ENV` | `development` | Env selector; production disables Swagger, hardens headers |
| `DATABASE_URL` | — | `postgresql://user:pass@pgbouncer:6432/sahool?sslmode=require` |
| `PARTNER_AUTH_ISSUER` | `https://api.sahool.com` | `iss` claim + base for OIDC discovery URLs |
| `CORS_ALLOWED_ORIGINS` | (defaults) | Comma-separated list |
| `CSRF_SECRET` | dev placeholder | HMAC secret for consent-screen CSRF tokens (32+ chars in production) |
| `SAHOOL_SESSION_SECRET` | dev placeholder | HS256 secret shared with user-service for sahool_session JWT verification |
| `SAHOOL_LOGIN_URL` | `https://app.sahool.com/login` | Where `/authorize` redirects unauthenticated users |
| `SAHOOL_SIGNOUT_URL` | `https://app.sahool.com/logout` | "Not you? Sign out" link on consent screen |

## Local development

```bash
# From repo root
cd apps/services/partner-auth-service
npm install
npx prisma generate
npm run start:dev      # → http://localhost:3030
```

### Quick smoke

```bash
# OIDC discovery
curl http://localhost:3030/.well-known/openid-configuration | jq

# JWKS
curl http://localhost:3030/.well-known/jwks.json | jq

# Stub endpoints (should return 501 with helpful body)
curl -X POST http://localhost:3030/partner/v1/oauth/revoke | jq
```

## Tests

```bash
npm run test         # unit
npm run test:e2e     # integration (needs DATABASE_URL)
```

## References

- [RFC 6749 — OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)
- [RFC 7009 — Token Revocation](https://datatracker.ietf.org/doc/html/rfc7009)
- [RFC 7517 — JWK](https://datatracker.ietf.org/doc/html/rfc7517)
- [RFC 7636 — PKCE](https://datatracker.ietf.org/doc/html/rfc7636)
- [RFC 7662 — Token Introspection](https://datatracker.ietf.org/doc/html/rfc7662)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html)
- [OAuth 2.1 Security Best Current Practice](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [Climate FieldView OAuth docs](https://dev.fieldview.com/api-details/) — reference compatibility target

## Roadmap

See `docs/migrations/PARTNER_AUTH_ROADMAP.md` (to be authored in next branch). High-level:

- **Branch 2**: consent screen (`/authorize`), `/revoke`, `/introspect`, `/userinfo`
- **Branch 3**: Admin UI for partner registration + rate-tier assignment
- **Branch 4**: Kong route integration + `X-Sahool-Partner-Key` rate-limit plugin
- **Branch 5**: migration from per-tenant JWT to partner OAuth scopes in downstream services
