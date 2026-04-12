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

### ✅ Implemented (this scaffold)
| Endpoint | Description |
|---|---|
| `POST /partner/v1/oauth/token` | `authorization_code` + `refresh_token` grants with rotation + reuse detection |
| `GET /.well-known/openid-configuration` | OIDC discovery |
| `GET /.well-known/jwks.json` | Public key set (RSA, RS256) |
| `GET /healthz` `/readyz` `/health` | K8s probes + DB ping |

### ⏳ Planned (next branch: `claude/wave1-partner-auth-consent-screen`)
| Endpoint | Returns 501 until live |
|---|---|
| `GET /partner/v1/oauth/authorize` | Interactive consent screen (HTML) |
| `POST /partner/v1/oauth/revoke` | RFC 7009 token revocation |
| `POST /partner/v1/oauth/introspect` | RFC 7662 token introspection |
| `GET /partner/v1/oauth/userinfo` | OIDC UserInfo |
| Admin API | Partner app registration (CRUD `oauth_clients`) |

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
