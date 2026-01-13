# Field-Level Encryption Setup Guide

## دليل إعداد التشفير على مستوى الحقول

This guide provides step-by-step instructions for setting up field-level encryption in the SAHOOL platform.

## Table of Contents

1. [Overview](#overview)
2. [Generate Encryption Keys](#generate-encryption-keys)
3. [Configure Environment Variables](#configure-environment-variables)
4. [Integration Examples](#integration-examples)
5. [Key Management Best Practices](#key-management-best-practices)
6. [Key Rotation](#key-rotation)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The SAHOOL shared-crypto package provides:

- **AES-256-GCM Encryption**: Industry-standard encryption for sensitive data
- **Deterministic Encryption**: For fields that need to be searched (nationalId, phone)
- **Automatic Encryption/Decryption**: Via Prisma and SQLAlchemy middleware
- **PII Detection**: Automatic detection of personally identifiable information
- **Password Hashing**: bcrypt-based secure password hashing

---

## Generate Encryption Keys

### Step 1: Generate Keys

You need to generate three keys:

1. **Primary Encryption Key** (for standard encryption)
2. **Deterministic Encryption Key** (for searchable fields)
3. **HMAC Secret** (for data integrity)

#### Using Node.js

```bash
# Generate Primary Encryption Key
node -e "console.log('ENCRYPTION_KEY=' + require('crypto').randomBytes(32).toString('hex'))"

# Generate Deterministic Encryption Key
node -e "console.log('DETERMINISTIC_ENCRYPTION_KEY=' + require('crypto').randomBytes(32).toString('hex'))"

# Generate HMAC Secret
node -e "console.log('HMAC_SECRET=' + require('crypto').randomBytes(32).toString('hex'))"
```

#### Using Python

```bash
# Generate Primary Encryption Key
python3 -c "import os; print('ENCRYPTION_KEY=' + os.urandom(32).hex())"

# Generate Deterministic Encryption Key
python3 -c "import os; print('DETERMINISTIC_ENCRYPTION_KEY=' + os.urandom(32).hex())"

# Generate HMAC Secret
python3 -c "import os; print('HMAC_SECRET=' + os.urandom(32).hex())"
```

#### Using OpenSSL

```bash
# Generate keys
openssl rand -hex 32  # Run this three times for three keys
```

---

## Configure Environment Variables

### For NestJS Services (User Service)

Add to `/apps/services/user-service/.env`:

```env
# Field-Level Encryption
ENCRYPTION_KEY=your-64-character-hex-key-here
DETERMINISTIC_ENCRYPTION_KEY=your-64-character-hex-key-here
HMAC_SECRET=your-secret-here
CRYPTO_DEBUG=false
```

### For Python Services

Add to your Python service `.env`:

```env
# Field-Level Encryption
ENCRYPTION_KEY=your-64-character-hex-key-here
DETERMINISTIC_ENCRYPTION_KEY=your-64-character-hex-key-here
HMAC_SECRET=your-secret-here
```

---

## Integration Examples

### TypeScript/NestJS with Prisma

#### 1. Install the Package

The package is available as a local workspace package:

```bash
# No installation needed for local workspace
# Just import directly
```

#### 2. Update Prisma Service

```typescript
// src/prisma/prisma.service.ts
import { Injectable, OnModuleInit } from "@nestjs/common";
import { PrismaClient } from "@prisma/client";
import { createPrismaEncryptionMiddleware } from "@sahool/shared-crypto";

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  constructor() {
    super();

    // Configure encryption
    const encryptionConfig = {
      User: {
        phone: { type: "deterministic" }, // Searchable
      },
      UserProfile: {
        nationalId: { type: "deterministic" }, // Searchable
        dateOfBirth: { type: "standard" }, // Not searchable, more secure
      },
    };

    this.$use(
      createPrismaEncryptionMiddleware(encryptionConfig, {
        debug: process.env.CRYPTO_DEBUG === "true",
      }),
    );
  }

  async onModuleInit() {
    await this.$connect();
  }
}
```

#### 3. Use in Your Service

```typescript
// Data is automatically encrypted/decrypted
const user = await prisma.user.create({
  data: {
    email: "user@example.com",
    phone: "0551234567", // Will be encrypted
    profile: {
      create: {
        nationalId: "1234567890", // Will be encrypted
        dateOfBirth: new Date("1990-01-01"), // Will be encrypted
      },
    },
  },
});

// Searching works with deterministic encryption
const foundUser = await prisma.user.findFirst({
  where: {
    phone: "0551234567", // Will search encrypted value
  },
});
```

### Python with SQLAlchemy

#### 1. Install Dependencies

```bash
pip install cryptography bcrypt sqlalchemy
```

#### 2. Define Models with Encrypted Fields

```python
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from packages.shared_crypto.src.sqlalchemy_encryption import (
    EncryptedString,
    hash_password,
    verify_password
)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Encrypted fields
    phone = Column(EncryptedString(deterministic=True))  # Searchable
    national_id = Column(EncryptedString(deterministic=True))  # Searchable
    date_of_birth = Column(EncryptedString())  # Not searchable

# Usage
engine = create_engine('postgresql://user:pass@localhost/db')
Session = sessionmaker(bind=engine)
session = Session()

# Create user
user = User(
    email='user@example.com',
    password_hash=hash_password('user-password'),
    phone='0551234567',  # Will be encrypted automatically
    national_id='1234567890',  # Will be encrypted automatically
    date_of_birth='1990-01-01'  # Will be encrypted automatically
)
session.add(user)
session.commit()

# Search by encrypted field (works with deterministic encryption)
found_user = session.query(User).filter(
    User.national_id == '1234567890'  # Will search encrypted value
).first()
```

---

## Key Management Best Practices

### 1. Never Commit Keys to Version Control

Add to `.gitignore`:

```
.env
.env.local
.env.*.local
```

### 2. Use Secret Management Services

**Production Recommendations:**

- **AWS**: AWS Secrets Manager or AWS Systems Manager Parameter Store
- **Azure**: Azure Key Vault
- **GCP**: Google Cloud Secret Manager
- **Kubernetes**: Kubernetes Secrets with encryption at rest
- **HashiCorp Vault**: For on-premises or multi-cloud

### 3. Restrict Access to Keys

- Limit who can view/modify encryption keys
- Use IAM policies to restrict access
- Enable audit logging for key access
- Rotate keys regularly

### 4. Backup Keys Securely

- Store backups in encrypted form
- Use multiple secure locations
- Document key recovery procedures
- Test recovery procedures regularly

---

## Key Rotation

When you need to rotate encryption keys:

### Step 1: Generate New Keys

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Step 2: Update Environment Variables

```env
# New key
ENCRYPTION_KEY=new-key-here

# Old key (temporary, for decrypting existing data)
PREVIOUS_ENCRYPTION_KEY=old-key-here
```

### Step 3: Re-encrypt Data

The system will:

1. Decrypt data using `PREVIOUS_ENCRYPTION_KEY`
2. Encrypt data using `ENCRYPTION_KEY`

You can also use the provided rotation utility:

```typescript
import { rotateEncryption } from "@sahool/shared-crypto";

// Re-encrypt a single value
const newEncrypted = rotateEncryption(oldEncrypted);
```

### Step 4: Remove Old Key

After all data is re-encrypted, remove `PREVIOUS_ENCRYPTION_KEY` from environment.

---

## Troubleshooting

### Error: "ENCRYPTION_KEY environment variable is not set"

**Solution**: Ensure your `.env` file contains the encryption keys and is being loaded.

```bash
# Check if .env is being loaded
echo $ENCRYPTION_KEY

# For NestJS, install dotenv if not already:
npm install dotenv
```

### Error: "Decryption failed"

**Possible Causes:**

1. Using wrong encryption key
2. Data was not encrypted
3. Data was corrupted

**Solutions:**

1. Check that `ENCRYPTION_KEY` matches the key used to encrypt
2. Check if `PREVIOUS_ENCRYPTION_KEY` is needed
3. Enable debug mode: `CRYPTO_DEBUG=true`

### Searching Encrypted Fields Returns No Results

**Issue**: Searching deterministic encrypted fields doesn't work.

**Solution**: Ensure the field is configured with `type: 'deterministic'`:

```typescript
const encryptionConfig = {
  User: {
    phone: { type: "deterministic" }, // Must be deterministic for search
  },
};
```

### Performance Issues

**Issue**: Encryption/decryption is slow.

**Solutions:**

1. Only encrypt truly sensitive fields
2. Use deterministic encryption only for searchable fields
3. Consider caching decrypted values (carefully!)
4. Use database indexes on encrypted fields

---

## Security Considerations

### What to Encrypt

**Always Encrypt:**

- National IDs
- Passport numbers
- Social Security Numbers
- Bank account numbers
- Credit card numbers
- Health information

**Consider Encrypting:**

- Phone numbers (use deterministic for search)
- Email addresses (use deterministic for search)
- Dates of birth
- Addresses
- Salary information

**Don't Encrypt:**

- Non-sensitive reference data
- Already public information
- Data that needs complex queries
- High-volume data that doesn't need protection

### Encryption Types

**Standard Encryption** (Non-searchable, more secure):

- Use for highly sensitive data that doesn't need to be searched
- Each encryption produces different output
- Maximum security

**Deterministic Encryption** (Searchable, less secure):

- Use only for fields that must be searchable
- Same input always produces same output
- Allows equality searches but reveals patterns
- Less secure than standard encryption

---

## Support

For issues or questions:

- Open an issue in the project repository
- Contact the SAHOOL security team
- Review the API documentation in the package README

---

**Last Updated**: 2026-01-01
**Version**: 1.0.0
