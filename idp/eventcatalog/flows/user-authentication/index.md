---
id: user-authentication
name: User Authentication
version: 1.0.0
summary: A farmer logs in via the mobile app, receives a JWT, and gains authenticated access to platform services.
steps:
  - id: sahool.auth.login_requested
    title: Login Requested
    service: mobile-app
  - id: sahool.auth.token_issued
    title: JWT Issued
    service: user-service
  - id: sahool.auth.access_granted
    title: Access Granted
    service: kong-gateway
---

The mobile app sends credentials to Kong, which routes the request to the user-service. The user-service validates credentials against PostgreSQL, retrieves signing keys from Vault, and issues a JWT with tenant claims. Kong validates subsequent requests using the JWT and forwards authenticated traffic to backend services.

```mermaid
sequenceDiagram
    participant MA as Mobile App
    participant K as Kong Gateway
    participant US as user-service
    participant PG as PostgreSQL
    participant V as HashiCorp Vault

    MA->>K: POST /api/v1/auth/login (credentials)
    K->>US: forward login request
    US->>PG: validate credentials
    PG-->>US: user record + tenant_id
    US->>V: fetch JWT signing key
    V-->>US: signing key
    US->>US: issue JWT (sub, tid, roles)
    US-->>K: 200 OK + JWT
    K-->>MA: JWT access token + refresh token
    Note over MA,K: Subsequent requests
    MA->>K: GET /api/v1/fields (Authorization: Bearer JWT)
    K->>K: validate JWT signature & claims
    K->>US: forward authenticated request
```
