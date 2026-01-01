# Shared Crypto - Quick Reference Card
## مرجع سريع للتشفير

---

## 🔑 Generate Encryption Keys

```bash
# Generate all three keys at once
node -e "const crypto = require('crypto'); console.log('ENCRYPTION_KEY=' + crypto.randomBytes(32).toString('hex')); console.log('DETERMINISTIC_ENCRYPTION_KEY=' + crypto.randomBytes(32).toString('hex')); console.log('HMAC_SECRET=' + crypto.randomBytes(32).toString('hex'))"
```

---

## 🔐 Basic Encryption

```typescript
import { encrypt, decrypt, encryptSearchable } from '@sahool/shared-crypto';

// Standard (non-searchable)
const encrypted = encrypt('sensitive data');
const decrypted = decrypt(encrypted);

// Deterministic (searchable)
const encryptedId = encryptSearchable('1234567890');
```

---

## 🔒 Password Hashing

```typescript
import { hashPassword, verifyPassword } from '@sahool/shared-crypto';

const hash = await hashPassword('password123');
const isValid = await verifyPassword('password123', hash);
```

---

## 🛡️ PII Detection

```typescript
import { detectPII, maskPII, MaskingStrategy } from '@sahool/shared-crypto';

const detected = detectPII('My phone is 0551234567');
const masked = maskPII('Phone: 0551234567', MaskingStrategy.PARTIAL);
// Output: "Phone: 055****567"
```

---

## 🗄️ Prisma Integration

```typescript
import { createPrismaEncryptionMiddleware } from '@sahool/shared-crypto';

const config = {
  User: { phone: { type: 'deterministic' } },
  UserProfile: {
    nationalId: { type: 'deterministic' },
    dateOfBirth: { type: 'standard' },
  },
};

prisma.$use(createPrismaEncryptionMiddleware(config));
```

---

## 🐍 SQLAlchemy Integration

```python
from packages.shared_crypto.src.sqlalchemy_encryption import EncryptedString

class User(Base):
    national_id = Column(EncryptedString(deterministic=True))
    date_of_birth = Column(EncryptedString())
```

---

## 📝 Environment Variables

```env
ENCRYPTION_KEY=<64-hex-chars>
DETERMINISTIC_ENCRYPTION_KEY=<64-hex-chars>
HMAC_SECRET=<random-string>
CRYPTO_DEBUG=false
```

---

## 🔄 Key Rotation

```typescript
import { rotateEncryption } from '@sahool/shared-crypto';

// 1. Set PREVIOUS_ENCRYPTION_KEY in env
// 2. Set new ENCRYPTION_KEY in env
// 3. Re-encrypt data
const newEncrypted = rotateEncryption(oldEncrypted);
```

---

## 🎯 When to Use Each Type

| Type | Use For | Searchable | Security |
|------|---------|------------|----------|
| **Standard** | dateOfBirth, address | ❌ No | ⭐⭐⭐ High |
| **Deterministic** | nationalId, phone | ✅ Yes | ⭐⭐ Medium |

---

## ⚡ Common Operations

### Encrypt Object Fields

```typescript
import { encryptFields } from '@sahool/shared-crypto';

const data = { name: 'Ahmed', nationalId: '1234567890' };
const encrypted = encryptFields(data, ['nationalId'], true);
```

### HMAC Signature

```typescript
import { createHMAC, verifyHMAC } from '@sahool/shared-crypto';

const signature = createHMAC('data to protect');
const isValid = verifyHMAC('data to protect', signature);
```

### Check if Should Encrypt

```typescript
import { shouldEncrypt, shouldUseDeterministicEncryption } from '@sahool/shared-crypto';

if (shouldEncrypt('nationalId')) {
  // Encrypt this field
}

if (shouldUseDeterministicEncryption('nationalId')) {
  // Use deterministic encryption
}
```

---

## 🚨 Common Errors

| Error | Solution |
|-------|----------|
| `ENCRYPTION_KEY not set` | Add to `.env` file |
| `Decryption failed` | Check key, try `PREVIOUS_ENCRYPTION_KEY` |
| `Search returns nothing` | Use deterministic encryption |
| `Invalid key length` | Key must be 64 hex chars (32 bytes) |

---

## 📚 Documentation Links

- Setup Guide: `ENCRYPTION_SETUP.md`
- Usage Examples: `USAGE_EXAMPLES.md`
- Package README: `README.md`

---

**Version**: 1.0.0 | **Last Updated**: 2026-01-01
