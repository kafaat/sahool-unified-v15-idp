# Merge Report: Auth Service Enterprise Upgrade
Date: 2025-12-13

Upgraded component:
- platform-core/auth-service (Node/Express)

Key improvements applied:
- Tenants table + UUID tenant_id FK
- Unique email per tenant (tenant_id,email)
- Composite indexes for multi-tenant performance
- Soft-delete fields
- Added tables: roles, permissions, user_roles, role_permissions, auth_sessions, api_keys, password_history, user_oauth_providers, auth_audit_logs
- Tenant header enforcement: X-Tenant-Id

Files touched:
- platform-core/auth-service/src/index.ts
- platform-core/auth-service/package.json
- platform-core/auth-service/k8s/*
- platform-core/auth-service/AUTH_ENTERPRISE_NOTES.md
