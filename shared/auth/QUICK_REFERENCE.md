# Password Hasher - Quick Reference

# مرجع سريع - معالج كلمات المرور

## Python API

### Import

```python
from shared.auth.password_hasher import hash_password, verify_password, needs_rehash
```

### Hash Password

```python
hashed = hash_password("MyPassword123!")
# Returns: "$argon2id$v=19$m=65536,t=2,p=4$..."
```

### Verify Password

```python
is_valid, needs_migration = verify_password("MyPassword123!", hashed)
# is_valid: True if password matches
# needs_migration: True if hash should be updated
```

### Check if Rehash Needed

```python
should_rehash = needs_rehash(hashed)
# Returns: True if password should be rehashed
```

### Full Login Example

```python
from shared.auth.password_migration_helper import PasswordMigrationHelper

helper = PasswordMigrationHelper(user_repository)
result = await helper.authenticate_and_migrate(email, password)

if result.success:
    if result.needs_password_update:
        # Update password in database
        user_repository.update_password_hash(
            result.user_id,
            result.new_password_hash
        )
    # Generate JWT and return
    return {"access_token": create_token(result.user_id)}
else:
    raise UnauthorizedException("Invalid credentials")
```

---

## TypeScript API

### Import

```typescript
import {
  hashPassword,
  verifyPassword,
  needsRehash,
} from "@/shared/auth/password-hasher";
```

### Hash Password

```typescript
const hashed = await hashPassword("MyPassword123!");
// Returns: "$argon2id$v=19$m=65536,t=2,p=4$..."
```

### Verify Password

```typescript
const result = await verifyPassword("MyPassword123!", hashed);
// result = { isValid: true, needsRehash: false }
```

### Check if Rehash Needed

```typescript
const shouldRehash = await needsRehash(hashed);
// Returns: true if password should be rehashed
```

### Full Login Example

```typescript
async function login(email: string, password: string) {
  const user = await getUserByEmail(email);
  if (!user) throw new UnauthorizedException();

  const result = await verifyPassword(password, user.passwordHash);
  if (!result.isValid) throw new UnauthorizedException();

  // Migrate if needed
  if (result.needsRehash) {
    const newHash = await hashPassword(password);
    await updateUserPassword(user.id, newHash);
  }

  return { accessToken: generateJWT(user.id) };
}
```

---

## SQL Queries

### Check Migration Progress

```sql
SELECT * FROM password_migration_stats;
```

### Get Users Needing Migration

```sql
SELECT id, email, password_algorithm
FROM users
WHERE password_needs_migration = TRUE
LIMIT 10;
```

### Count by Algorithm

```sql
SELECT
    password_algorithm,
    COUNT(*) as count
FROM users
WHERE password_hash IS NOT NULL
GROUP BY password_algorithm;
```

---

## Command Line

### Install Dependencies

```bash
# Python
pip install argon2-cffi bcrypt

# TypeScript
npm install argon2 bcrypt
```

### Run Migration

```bash
# SQL migration
psql -U postgres -d sahool -f database/migrations/011_migrate_passwords_to_argon2.sql

# Python script (dry run)
python database/migrations/011_migrate_passwords_to_argon2.py --dry-run

# Python script (actual)
python database/migrations/011_migrate_passwords_to_argon2.py
```

### Run Tests

```bash
# Python
pytest tests/test_password_hasher.py -v

# TypeScript
npm test tests/test_password_hasher.test.ts
```

---

## Hash Formats

| Algorithm | Example Format                       |
| --------- | ------------------------------------ |
| Argon2id  | `$argon2id$v=19$m=65536,t=2,p=4$...` |
| bcrypt    | `$2b$12$...`                         |
| PBKDF2    | `<64-char-salt>$<64-char-hash>`      |

---

## Configuration

### Default Parameters (OWASP 2024)

- **Time cost**: 2 iterations
- **Memory cost**: 64 MB (65536 KiB)
- **Parallelism**: 4 threads
- **Hash length**: 256 bits (32 bytes)
- **Salt length**: 128 bits (16 bytes)

### Custom Configuration

```python
from shared.auth.password_hasher import PasswordHasher

hasher = PasswordHasher(
    time_cost=3,        # More iterations = slower but more secure
    memory_cost=131072, # 128 MB
    parallelism=8,      # More threads
    hash_len=32,
    salt_len=16
)
```

```typescript
import { PasswordHasher } from "@/shared/auth/password-hasher";

const hasher = new PasswordHasher({
  timeCost: 3,
  memoryCost: 131072,
  parallelism: 8,
  hashLength: 32,
  saltLength: 16,
});
```

---

## Common Patterns

### Registration

```python
# Python
from shared.auth.password_hasher import hash_password

password_hash = hash_password(request.password)
user = User(email=request.email, password_hash=password_hash)
db.add(user)
db.commit()
```

```typescript
// TypeScript
import { hashPassword } from "@/shared/auth/password-hasher";

const passwordHash = await hashPassword(request.password);
const user = await createUser({
  email: request.email,
  passwordHash,
});
```

### Password Change

```python
# Python
from shared.auth.password_hasher import verify_password, hash_password

# Verify current password
is_valid, _ = verify_password(current_password, user.password_hash)
if not is_valid:
    raise ValueError("Invalid current password")

# Hash new password
new_hash = hash_password(new_password)
user.password_hash = new_hash
db.commit()
```

```typescript
// TypeScript
import { verifyPassword, hashPassword } from "@/shared/auth/password-hasher";

// Verify current password
const result = await verifyPassword(currentPassword, user.passwordHash);
if (!result.isValid) {
  throw new Error("Invalid current password");
}

// Hash new password
const newHash = await hashPassword(newPassword);
await updateUser(user.id, { passwordHash: newHash });
```

---

## Troubleshooting

### Error: "argon2-cffi not available"

```bash
pip install argon2-cffi
```

### Error: "Module not found: argon2"

```bash
npm install argon2
```

### Migration not working

1. Check SQL migration was applied: `SELECT * FROM password_migration_stats;`
2. Verify code is using new hasher
3. Check user is successfully authenticating

### Performance issues

Reduce Argon2 parameters:

```python
hasher = PasswordHasher(time_cost=1, memory_cost=32768, parallelism=2)
```

---

## Files Reference

| File                                                      | Purpose                   |
| --------------------------------------------------------- | ------------------------- |
| `shared/auth/password_hasher.py`                          | Python implementation     |
| `shared/auth/password-hasher.ts`                          | TypeScript implementation |
| `shared/auth/password_migration_helper.py`                | Integration helper        |
| `shared/auth/password_hasher_example.py`                  | Complete examples         |
| `shared/auth/PASSWORD_MIGRATION_README.md`                | Full documentation        |
| `database/migrations/011_migrate_passwords_to_argon2.sql` | SQL migration             |
| `database/migrations/011_migrate_passwords_to_argon2.py`  | Python migration          |
| `tests/test_password_hasher.py`                           | Python tests              |
| `tests/test_password_hasher.test.ts`                      | TypeScript tests          |

---

**Last Updated**: 2024-12-27
