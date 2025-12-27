# Password Hashing Migration to Argon2id
# ترحيل تشفير كلمات المرور إلى Argon2id

## Overview / نظرة عامة

This document describes the migration from legacy password hashing algorithms (bcrypt, PBKDF2) to **Argon2id**, the current OWASP-recommended algorithm for password hashing.

يصف هذا المستند الترحيل من خوارزميات تشفير كلمات المرور القديمة (bcrypt, PBKDF2) إلى **Argon2id**، الخوارزمية الموصى بها حالياً من OWASP لتشفير كلمات المرور.

### Why Argon2id? / لماذا Argon2id؟

- **OWASP Recommended**: Current industry best practice
- **Memory-hard**: Resistant to GPU and ASIC attacks
- **Configurable**: Tunable cost parameters
- **Proven**: Winner of Password Hashing Competition (2015)

## Files Created / الملفات المُنشأة

### Python Implementation

1. **`shared/auth/password_hasher.py`**
   - Main password hasher with Argon2id support
   - Backward compatibility for bcrypt and PBKDF2
   - Automatic migration detection

2. **`shared/auth/password_migration_helper.py`**
   - Helper functions for integrating migration into auth flows
   - Example implementations for FastAPI and SQLAlchemy

3. **`database/migrations/011_migrate_passwords_to_argon2.py`**
   - Script to flag passwords for migration
   - Batch processing support
   - Dry-run mode

4. **`database/migrations/011_migrate_passwords_to_argon2.sql`**
   - SQL migration to add tracking columns
   - Triggers for automatic algorithm detection
   - Monitoring views

5. **`tests/test_password_hasher.py`**
   - Comprehensive test suite
   - Tests for all algorithms
   - Migration scenario tests

### TypeScript Implementation

1. **`shared/auth/password-hasher.ts`**
   - TypeScript password hasher
   - Same features as Python version
   - Full backward compatibility

2. **`tests/test_password_hasher.test.ts`**
   - Jest/Mocha compatible tests
   - Full coverage

3. **`shared/auth/password-hasher-dependencies.json`**
   - Required npm packages

## Installation / التثبيت

### Python

```bash
# Install required packages
pip install argon2-cffi bcrypt

# Or use requirements file
pip install -r apps/services/shared/auth/requirements.txt
```

### TypeScript/Node.js

```bash
# Install required packages
npm install argon2 bcrypt

# Or
yarn add argon2 bcrypt
```

## Migration Process / عملية الترحيل

### Step 1: Run SQL Migration

```bash
# Connect to your database
psql -U postgres -d sahool -f database/migrations/011_migrate_passwords_to_argon2.sql
```

This will:
- Add `password_needs_migration` column
- Add `password_algorithm` column
- Flag existing bcrypt/PBKDF2 passwords
- Create monitoring views

### Step 2: Update Your Code

#### Python (FastAPI Example)

```python
from fastapi import APIRouter, HTTPException
from shared.auth.password_migration_helper import PasswordMigrationHelper
from shared.auth.password_hasher import hash_password

router = APIRouter()

@router.post("/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    # Create migration helper
    helper = PasswordMigrationHelper(user_repository)

    # Authenticate and check for migration
    result = await helper.authenticate_and_migrate(email, password)

    if not result.success:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # If password needs migration, update it
    if result.needs_password_update and result.new_password_hash:
        await helper.complete_migration(
            result.user_id,
            result.new_password_hash
        )

    # Generate JWT and return
    token = create_access_token(result.user_id)
    return {"access_token": token}

@router.post("/register")
async def register(email: str, password: str, db: Session = Depends(get_db)):
    # New users always use Argon2id
    password_hash = hash_password(password)

    user = User(email=email, password_hash=password_hash)
    db.add(user)
    db.commit()

    return {"user_id": user.id}
```

#### TypeScript (NestJS/Express Example)

```typescript
import { hashPassword, verifyPassword } from '@/shared/auth/password-hasher';

// Login endpoint
async function login(email: string, password: string) {
  // Get user from database
  const user = await getUserByEmail(email);
  if (!user) {
    throw new UnauthorizedException('Invalid credentials');
  }

  // Verify password and check migration
  const result = await verifyPassword(password, user.passwordHash);

  if (!result.isValid) {
    throw new UnauthorizedException('Invalid credentials');
  }

  // If needs migration, rehash and update
  if (result.needsRehash) {
    const newHash = await hashPassword(password);
    await updateUserPassword(user.id, newHash);
  }

  // Generate JWT
  const token = generateJWT(user.id);
  return { accessToken: token };
}

// Registration endpoint
async function register(email: string, password: string) {
  // New users always use Argon2id
  const passwordHash = await hashPassword(password);

  const user = await createUser({
    email,
    passwordHash,
    passwordAlgorithm: 'argon2id',
  });

  return { userId: user.id };
}
```

### Step 3: Monitor Migration Progress

```sql
-- View migration statistics
SELECT * FROM password_migration_stats;

-- Example output:
-- password_algorithm | count | needs_migration | migration_percentage
-- argon2id          | 1500  | 0               | 0.00
-- bcrypt            | 500   | 500             | 100.00
-- pbkdf2_sha256     | 200   | 200             | 100.00
```

### Step 4 (Optional): Force Migration

If you want to migrate all passwords at once (requires user cooperation):

```bash
# Run Python migration script
python database/migrations/011_migrate_passwords_to_argon2.py --dry-run

# After reviewing, run actual migration
python database/migrations/011_migrate_passwords_to_argon2.py
```

**Note**: This only flags passwords for migration. Actual rehashing happens on next login.

## API Reference / مرجع API

### Python

#### `PasswordHasher` Class

```python
from shared.auth.password_hasher import PasswordHasher

hasher = PasswordHasher(
    time_cost=2,        # Argon2 time cost (iterations)
    memory_cost=65536,  # Memory usage in KiB (64 MB)
    parallelism=4,      # Number of threads
    hash_len=32,        # Hash length in bytes
    salt_len=16         # Salt length in bytes
)

# Hash a password
hashed = hasher.hash_password("MyPassword123!")

# Verify a password
is_valid, needs_rehash = hasher.verify_password("MyPassword123!", hashed)

# Check if rehashing is needed
needs_migration = hasher.needs_rehash(hashed)
```

#### Global Functions

```python
from shared.auth.password_hasher import (
    hash_password,
    verify_password,
    needs_rehash,
    generate_otp,
    generate_secure_token
)

# Hash password (uses default settings)
hashed = hash_password("MyPassword123!")

# Verify password
is_valid, needs_rehash = verify_password("MyPassword123!", hashed)

# Generate OTP
otp = generate_otp(6)  # 6-digit OTP

# Generate secure token
token = generate_secure_token(32)  # 32 bytes = 64 hex chars
```

### TypeScript

#### `PasswordHasher` Class

```typescript
import { PasswordHasher } from '@/shared/auth/password-hasher';

const hasher = new PasswordHasher({
  timeCost: 2,        // Argon2 time cost (iterations)
  memoryCost: 65536,  // Memory usage in KiB (64 MB)
  parallelism: 4,     // Number of threads
  hashLength: 32,     // Hash length in bytes
  saltLength: 16      // Salt length in bytes
});

// Hash a password
const hashed = await hasher.hashPassword('MyPassword123!');

// Verify a password
const result = await hasher.verifyPassword('MyPassword123!', hashed);
// result = { isValid: true, needsRehash: false }

// Check if rehashing is needed
const needsMigration = await hasher.needsRehash(hashed);
```

#### Global Functions

```typescript
import {
  hashPassword,
  verifyPassword,
  needsRehash,
  generateOTP,
  generateSecureToken
} from '@/shared/auth/password-hasher';

// Hash password
const hashed = await hashPassword('MyPassword123!');

// Verify password
const result = await verifyPassword('MyPassword123!', hashed);

// Generate OTP
const otp = generateOTP(6);  // 6-digit OTP

// Generate secure token
const token = generateSecureToken(32);  // 32 bytes = 64 hex chars
```

## Security Considerations / اعتبارات الأمان

### Argon2id Parameters

Current settings (OWASP recommended for 2024):
- **Time cost**: 2 iterations
- **Memory cost**: 64 MB
- **Parallelism**: 4 threads
- **Hash length**: 256 bits (32 bytes)
- **Salt length**: 128 bits (16 bytes)

### Password Storage Format

- **Argon2id**: `$argon2id$v=19$m=65536,t=2,p=4$...`
- **bcrypt**: `$2b$12$...` (legacy)
- **PBKDF2**: `<salt_hex>$<hash_hex>` (legacy)

### Migration Timeline

1. **Immediate**: All new passwords use Argon2id
2. **Gradual**: Existing passwords migrate on next login
3. **Monitor**: Track progress via `password_migration_stats`
4. **Complete**: When 100% of active users have logged in

### Backward Compatibility

- Old passwords continue to work during migration
- Verification is transparent to users
- No password resets required
- Migration happens automatically

## Testing / الاختبار

### Run Python Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/test_password_hasher.py -v

# Run with coverage
pytest tests/test_password_hasher.py --cov=shared.auth.password_hasher
```

### Run TypeScript Tests

```bash
# Install test dependencies
npm install --save-dev jest @types/jest ts-jest

# Run tests
npm test tests/test_password_hasher.test.ts

# Or with Jest
jest tests/test_password_hasher.test.ts
```

## Troubleshooting / استكشاف الأخطاء

### Issue: "argon2-cffi not available"

**Solution**:
```bash
pip install argon2-cffi
# or
npm install argon2
```

### Issue: Migration not happening

**Check**:
1. SQL migration was applied: `SELECT * FROM password_migration_stats;`
2. Code is using new password hasher
3. `password_needs_migration` column exists
4. User is successfully logging in

### Issue: Performance concerns

**Solution**: Adjust Argon2 parameters based on your server capacity:
```python
# Lower settings for resource-constrained environments
hasher = PasswordHasher(
    time_cost=1,        # Faster but less secure
    memory_cost=32768,  # 32 MB instead of 64 MB
    parallelism=2       # Fewer threads
)
```

## Performance Benchmarks / قياسات الأداء

Approximate hashing times on modern hardware:

| Algorithm | Time | Memory |
|-----------|------|--------|
| Argon2id (current) | ~100ms | 64 MB |
| bcrypt (rounds=12) | ~250ms | Minimal |
| PBKDF2 (100k iterations) | ~50ms | Minimal |

**Note**: Argon2id is intentionally slower to resist brute-force attacks.

## References / المراجع

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Argon2 RFC 9106](https://datatracker.ietf.org/doc/html/rfc9106)
- [Password Hashing Competition](https://www.password-hashing.net/)

## Support / الدعم

For questions or issues:
1. Check this README
2. Review test files for examples
3. Check `password_migration_helper.py` for integration examples

---

**Last Updated**: 2024-12-27
**Version**: 1.0.0
