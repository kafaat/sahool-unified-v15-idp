# SAHOOL Shared Domain

> Cross-cutting authentication and multi-tenancy domain models

## Modules

| Module     | Description                     |
| ---------- | ------------------------------- |
| `auth/`    | Password hashing, JWT utilities |
| `users/`   | User models and service         |
| `tenancy/` | Multi-tenant support            |

## Usage

```python
from shared.domain.auth import hash_password, verify_password
from shared.domain.users import UserService
from shared.domain.tenancy import TenantContext
```

## Security Note

This module handles sensitive authentication logic.
Always use secure password hashing (bcrypt/argon2).

## Consumers

All services that require authentication:

- `kernel/services/field_ops/`
- `kernel-services-v15.3/marketplace-service/`
- `kernel-services-v15.3/research-core/`
