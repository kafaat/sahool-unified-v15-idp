# @sahool/shared-crypto

## SAHOOL Shared Cryptography Library
### مكتبة التشفير المشتركة

A comprehensive cryptography library for the SAHOOL platform, providing field-level encryption, PII detection, and data protection utilities.

## Features

- **AES-256-GCM Encryption**: Industry-standard encryption for sensitive data
- **Deterministic Encryption**: For searchable encrypted fields
- **Field-Level Encryption**: Automatic encryption/decryption middleware for Prisma and SQLAlchemy
- **PII Detection**: Automatic detection and handling of Personally Identifiable Information
- **Password Hashing**: bcrypt-based secure password hashing
- **HMAC Utilities**: Data integrity verification
- **Key Management**: Environment-based key management

## Installation

```bash
npm install @sahool/shared-crypto
```

## Environment Variables

Required environment variables:

```env
# Primary encryption key (32 bytes hex - 64 characters)
ENCRYPTION_KEY=your-256-bit-key-in-hex-format

# Deterministic encryption key (for searchable fields)
DETERMINISTIC_ENCRYPTION_KEY=your-256-bit-key-in-hex-format

# HMAC secret key
HMAC_SECRET=your-hmac-secret-key

# Optional: Key rotation
PREVIOUS_ENCRYPTION_KEY=old-key-for-migration
```

## Usage

### Field Encryption

```typescript
import { encrypt, decrypt, encryptDeterministic, decryptDeterministic } from '@sahool/shared-crypto';

// Standard encryption (non-searchable)
const encrypted = encrypt('sensitive data');
const decrypted = decrypt(encrypted);

// Deterministic encryption (searchable)
const encryptedId = encryptDeterministic('national-id-123');
const decryptedId = decryptDeterministic(encryptedId);
```

### Prisma Middleware

```typescript
import { createPrismaEncryptionMiddleware } from '@sahool/shared-crypto';

const encryptionConfig = {
  User: {
    phone: { type: 'deterministic' },
    email: { type: 'deterministic' }
  },
  UserProfile: {
    nationalId: { type: 'deterministic' },
    dateOfBirth: { type: 'standard' }
  }
};

prisma.$use(createPrismaEncryptionMiddleware(encryptionConfig));
```

### PII Detection

```typescript
import { detectPII, maskPII, shouldEncrypt } from '@sahool/shared-crypto';

const text = 'My phone is 05512345678';
const detected = detectPII(text); // Returns detected PII patterns
const masked = maskPII(text); // Returns 'My phone is 055****5678'
```

### Password Hashing

```typescript
import { hashPassword, verifyPassword } from '@sahool/shared-crypto';

const hash = await hashPassword('user-password');
const isValid = await verifyPassword('user-password', hash);
```

## Security Best Practices

1. **Never commit encryption keys** to version control
2. **Rotate keys regularly** using the key rotation mechanism
3. **Use deterministic encryption only** for fields that need to be searched
4. **Store keys securely** using a secret management service (AWS Secrets Manager, Azure Key Vault, etc.)
5. **Monitor decryption operations** for anomalies

## License

MIT License - SAHOOL Team
