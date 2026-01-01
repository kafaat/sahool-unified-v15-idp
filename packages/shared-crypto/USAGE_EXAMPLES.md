# Shared Crypto Usage Examples
## أمثلة استخدام مكتبة التشفير

This document provides practical examples of using the @sahool/shared-crypto package.

---

## Table of Contents

1. [Basic Encryption/Decryption](#basic-encryptiondecryption)
2. [Password Hashing](#password-hashing)
3. [PII Detection and Masking](#pii-detection-and-masking)
4. [Prisma Integration](#prisma-integration)
5. [SQLAlchemy Integration](#sqlalchemy-integration)
6. [HMAC and Data Integrity](#hmac-and-data-integrity)
7. [Advanced Use Cases](#advanced-use-cases)

---

## Basic Encryption/Decryption

### Standard Encryption (Non-searchable)

```typescript
import { encrypt, decrypt } from '@sahool/shared-crypto';

// Encrypt sensitive data
const sensitiveData = 'User\'s private information';
const encrypted = encrypt(sensitiveData);
console.log('Encrypted:', encrypted);
// Output: "base64IV:base64AuthTag:base64Ciphertext"

// Decrypt data
const decrypted = decrypt(encrypted);
console.log('Decrypted:', decrypted);
// Output: "User's private information"
```

### Deterministic Encryption (Searchable)

```typescript
import { encryptSearchable } from '@sahool/shared-crypto';

// Encrypt data for searching
const nationalId = '1234567890';
const encrypted1 = encryptSearchable(nationalId);
const encrypted2 = encryptSearchable(nationalId);

// Same input produces same output (deterministic)
console.log(encrypted1 === encrypted2); // true

// Use for searching in database
const user = await prisma.user.findFirst({
  where: {
    nationalId: encryptSearchable('1234567890'),
  },
});
```

### Batch Field Encryption

```typescript
import { encryptFields, decryptFields } from '@sahool/shared-crypto';

const userData = {
  name: 'Ahmed',
  email: 'ahmed@example.com',
  phone: '0551234567',
  nationalId: '1234567890',
  dateOfBirth: '1990-01-01',
};

// Encrypt specific fields
const encrypted = encryptFields(
  userData,
  ['phone', 'nationalId', 'dateOfBirth'],
  true // Use deterministic for phone and nationalId
);

// Decrypt fields
const decrypted = decryptFields(
  encrypted,
  ['phone', 'nationalId', 'dateOfBirth']
);
```

---

## Password Hashing

### Hash Password

```typescript
import { hashPassword, verifyPassword } from '@sahool/shared-crypto';

// Hash password (async)
const password = 'user-secure-password';
const hashedPassword = await hashPassword(password);
console.log('Hashed:', hashedPassword);
// Output: "$2a$12$..."

// Verify password
const isValid = await verifyPassword(password, hashedPassword);
console.log('Password valid:', isValid); // true

// With custom rounds
const strongHash = await hashPassword(password, 14); // More secure, slower
```

### Synchronous Password Hashing

```typescript
import { hashPasswordSync, verifyPasswordSync } from '@sahool/shared-crypto';

// For synchronous operations (use async when possible)
const hashedPassword = hashPasswordSync('password123');
const isValid = verifyPasswordSync('password123', hashedPassword);
```

---

## PII Detection and Masking

### Detect PII

```typescript
import { detectPII, PIIType } from '@sahool/shared-crypto';

const text = 'My phone is 0551234567 and email is ahmed@example.com';
const detected = detectPII(text);

detected.forEach((pii) => {
  console.log(`Found ${pii.type}: ${pii.value} (confidence: ${pii.confidence})`);
});
// Output:
// Found PHONE: 0551234567 (confidence: 0.95)
// Found EMAIL: ahmed@example.com (confidence: 0.95)
```

### Mask PII

```typescript
import { maskPII, MaskingStrategy } from '@sahool/shared-crypto';

const text = 'Contact me at 0551234567 or ahmed@example.com';

// Partial masking (default)
const masked = maskPII(text, MaskingStrategy.PARTIAL);
console.log(masked);
// Output: "Contact me at 055****567 or a****d@example.com"

// Full masking
const fullyMasked = maskPII(text, MaskingStrategy.FULL);
console.log(fullyMasked);
// Output: "Contact me at ********** or *********************"

// Redact completely
const redacted = maskPII(text, MaskingStrategy.REMOVE);
console.log(redacted);
// Output: "Contact me at [REDACTED] or [REDACTED]"
```

### Auto-Detect and Encrypt

```typescript
import {
  shouldEncrypt,
  autoEncrypt,
  encryptSensitiveFields
} from '@sahool/shared-crypto';

// Check if field should be encrypted
if (shouldEncrypt('nationalId')) {
  console.log('This field should be encrypted');
}

// Auto-encrypt based on field name
const encrypted = autoEncrypt('nationalId', '1234567890');

// Encrypt all sensitive fields in object
const userData = {
  name: 'Ahmed',
  nationalId: '1234567890',
  phone: '0551234567',
  email: 'ahmed@example.com',
};

const encrypted = encryptSensitiveFields(userData);
// nationalId and phone are automatically encrypted
```

---

## Prisma Integration

### Setup Prisma Service

```typescript
// src/prisma/prisma.service.ts
import { Injectable, OnModuleInit } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { createPrismaEncryptionMiddleware } from '@sahool/shared-crypto';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  constructor() {
    super();

    // Configure which fields to encrypt
    const encryptionConfig = {
      User: {
        phone: { type: 'deterministic' },
        ssn: { type: 'standard' },
      },
      UserProfile: {
        nationalId: { type: 'deterministic' },
        dateOfBirth: { type: 'standard' },
        address: { type: 'standard' },
      },
      Payment: {
        creditCardNumber: { type: 'standard' },
        bankAccount: { type: 'standard' },
      },
    };

    // Apply middleware
    this.$use(
      createPrismaEncryptionMiddleware(encryptionConfig, {
        debug: process.env.CRYPTO_DEBUG === 'true',
        onError: (error, context) => {
          console.error(
            `Encryption error in ${context.model}.${context.field}:`,
            error.message
          );
        },
      })
    );
  }

  async onModuleInit() {
    await this.$connect();
  }
}
```

### Using Encrypted Fields

```typescript
// Create user with encrypted fields
const user = await prisma.user.create({
  data: {
    email: 'ahmed@example.com',
    phone: '0551234567', // Automatically encrypted
    passwordHash: await hashPassword('password'),
    firstName: 'Ahmed',
    lastName: 'Ali',
    profile: {
      create: {
        nationalId: '1234567890', // Automatically encrypted
        dateOfBirth: new Date('1990-01-01'), // Automatically encrypted
      },
    },
  },
});

// Data is automatically decrypted on read
console.log(user.phone); // "0551234567" (decrypted)

// Search by encrypted field (works with deterministic)
const foundUser = await prisma.user.findFirst({
  where: {
    phone: '0551234567', // Automatically encrypted for search
  },
});

// Update encrypted field
await prisma.user.update({
  where: { id: user.id },
  data: {
    phone: '0559876543', // Automatically encrypted
  },
});
```

---

## SQLAlchemy Integration

### Define Models

```python
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from packages.shared_crypto.src.sqlalchemy_encryption import (
    EncryptedString,
    EncryptedText,
    hash_password,
    verify_password
)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))

    # Encrypted fields
    phone = Column(EncryptedString(deterministic=True))
    national_id = Column(EncryptedString(deterministic=True))
    date_of_birth = Column(EncryptedString())
    address = Column(EncryptedText())  # Longer text field
```

### CRUD Operations

```python
from sqlalchemy.orm import sessionmaker

# Create session
engine = create_engine('postgresql://user:pass@localhost/db')
Session = sessionmaker(bind=engine)
session = Session()

# Create user
user = User(
    email='ahmed@example.com',
    password_hash=hash_password('user-password'),
    phone='0551234567',  # Auto-encrypted
    national_id='1234567890',  # Auto-encrypted
    date_of_birth='1990-01-01',  # Auto-encrypted
    address='123 Main St, Riyadh'  # Auto-encrypted
)
session.add(user)
session.commit()

# Read user (data auto-decrypted)
user = session.query(User).filter(User.email == 'ahmed@example.com').first()
print(user.phone)  # "0551234567" (decrypted)

# Search by encrypted field
user = session.query(User).filter(
    User.national_id == '1234567890'  # Auto-encrypted for search
).first()

# Update encrypted field
user.phone = '0559876543'  # Auto-encrypted on commit
session.commit()
```

---

## HMAC and Data Integrity

### Create and Verify HMAC

```typescript
import { createHMAC, verifyHMAC } from '@sahool/shared-crypto';

// Create HMAC signature
const data = 'Important message that must not be tampered with';
const signature = createHMAC(data);

// Verify data integrity
const isValid = verifyHMAC(data, signature);
console.log('Data integrity:', isValid); // true

// Tampered data
const tamperedData = 'Important message that was modified';
const isStillValid = verifyHMAC(tamperedData, signature);
console.log('Tampered data:', isStillValid); // false
```

### Checksum Verification

```typescript
import { createChecksum, verifyChecksum } from '@sahool/shared-crypto';

const fileContent = 'File contents here...';
const checksum = createChecksum(fileContent);

// Later, verify file hasn't changed
const isValid = verifyChecksum(fileContent, checksum);
console.log('File intact:', isValid);
```

---

## Advanced Use Cases

### Key Rotation

```typescript
import { rotateEncryption } from '@sahool/shared-crypto';

// Set PREVIOUS_ENCRYPTION_KEY in environment
// Then re-encrypt data
const oldEncrypted = 'existing-encrypted-data';
const newEncrypted = rotateEncryption(oldEncrypted);

// Batch rotation
const users = await prisma.user.findMany();
for (const user of users) {
  if (user.sensitiveField) {
    const newValue = rotateEncryption(user.sensitiveField);
    await prisma.user.update({
      where: { id: user.id },
      data: { sensitiveField: newValue },
    });
  }
}
```

### Custom Encryption Configuration

```typescript
import {
  createPrismaEncryptionMiddleware,
  mergeEncryptionConfigs
} from '@sahool/shared-crypto';

// Base config
const baseConfig = {
  User: {
    phone: { type: 'deterministic' },
  },
};

// Additional config
const additionalConfig = {
  User: {
    ssn: { type: 'standard' },
  },
  Payment: {
    creditCard: { type: 'standard' },
  },
};

// Merge configs
const fullConfig = mergeEncryptionConfigs(baseConfig, additionalConfig);

prisma.$use(createPrismaEncryptionMiddleware(fullConfig));
```

### Conditional Encryption

```typescript
import { shouldEncrypt, getSensitivityLevel, SensitivityLevel } from '@sahool/shared-crypto';

function handleUserData(fieldName: string, value: string) {
  const sensitivity = getSensitivityLevel(fieldName, value);

  switch (sensitivity) {
    case SensitivityLevel.RESTRICTED:
      // Maximum security + audit logging
      console.log(`Accessing restricted field: ${fieldName}`);
      return encrypt(value);

    case SensitivityLevel.CONFIDENTIAL:
      // Standard encryption
      return encrypt(value);

    case SensitivityLevel.INTERNAL:
      // Hash or light encryption
      return sha256(value);

    case SensitivityLevel.PUBLIC:
      // No encryption needed
      return value;
  }
}
```

### Multi-Field Search

```typescript
// Search by multiple encrypted fields
const searchCriteria = {
  phone: '0551234567',
  nationalId: '1234567890',
};

const user = await prisma.user.findFirst({
  where: {
    OR: [
      { phone: searchCriteria.phone },
      {
        profile: {
          nationalId: searchCriteria.nationalId
        }
      },
    ],
  },
  include: { profile: true },
});
```

---

## Testing Encryption

### Unit Tests

```typescript
import { encrypt, decrypt, encryptSearchable } from '@sahool/shared-crypto';

describe('Encryption', () => {
  it('should encrypt and decrypt data', () => {
    const original = 'sensitive data';
    const encrypted = encrypt(original);
    const decrypted = decrypt(encrypted);
    expect(decrypted).toBe(original);
  });

  it('should produce deterministic results', () => {
    const data = '1234567890';
    const encrypted1 = encryptSearchable(data);
    const encrypted2 = encryptSearchable(data);
    expect(encrypted1).toBe(encrypted2);
  });

  it('should detect PII', () => {
    const text = 'Phone: 0551234567';
    const detected = detectPII(text);
    expect(detected).toHaveLength(1);
    expect(detected[0].type).toBe(PIIType.PHONE);
  });
});
```

---

## Performance Optimization

### Caching Considerations

```typescript
// ⚠️ WARNING: Only cache decrypted data in secure memory
// Never cache to disk or shared storage

class SecureCache {
  private cache = new Map<string, { value: string; expires: number }>();

  set(key: string, encryptedValue: string, ttlSeconds: number = 300) {
    const decrypted = decrypt(encryptedValue);
    this.cache.set(key, {
      value: decrypted,
      expires: Date.now() + ttlSeconds * 1000,
    });
  }

  get(key: string): string | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() > entry.expires) {
      this.cache.delete(key);
      return null;
    }

    return entry.value;
  }
}
```

---

**Last Updated**: 2026-01-01
**Version**: 1.0.0
