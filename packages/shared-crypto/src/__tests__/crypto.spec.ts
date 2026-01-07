/**
 * Unit Tests for Shared Cryptography Module
 * Tests encryption, hashing, and PII handling from @sahool/shared-crypto
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  // Field encryption
  encrypt,
  decrypt,
  encryptSearchable,
  decryptSearchable,
  encryptFields,
  decryptFields,
  generateEncryptionKey,
  isEncrypted,
  validateEncryptionKey,
  rotateEncryption,
  // Hash utilities
  hashPassword,
  verifyPassword,
  hashPasswordSync,
  verifyPasswordSync,
  sha256,
  sha256Base64,
  sha512,
  createHMAC,
  verifyHMAC,
  createDeterministicHash,
  hashSensitiveData,
  verifySensitiveDataHash,
  createChecksum,
  verifyChecksum,
  generateToken,
  generateSecureRandomString,
  createHashId,
} from '../index';

// Mock environment variables
beforeEach(() => {
  process.env.ENCRYPTION_KEY = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef';
  process.env.DETERMINISTIC_ENCRYPTION_KEY = 'fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210';
  process.env.HMAC_SECRET = 'test-hmac-secret-key';
});

afterEach(() => {
  delete process.env.ENCRYPTION_KEY;
  delete process.env.DETERMINISTIC_ENCRYPTION_KEY;
  delete process.env.HMAC_SECRET;
});

// ═══════════════════════════════════════════════════════════════════════════
// Password Hashing Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Password Hashing', () => {
  describe('hashPassword', () => {
    it('should hash password using bcrypt', async () => {
      const password = 'mySecurePassword123!';
      const hash = await hashPassword(password);

      expect(hash).toBeTruthy();
      expect(hash).toMatch(/^\$2[aby]\$\d+\$/); // bcrypt format
      expect(hash.length).toBeGreaterThan(50);
    });

    it('should generate different hashes for same password', async () => {
      const password = 'mySecurePassword123!';
      const hash1 = await hashPassword(password);
      const hash2 = await hashPassword(password);

      expect(hash1).not.toBe(hash2); // Different salts
    });

    it('should throw error for empty password', async () => {
      await expect(hashPassword('')).rejects.toThrow();
    });

    it('should accept custom rounds parameter', async () => {
      const password = 'mySecurePassword123!';
      const hash = await hashPassword(password, 10);

      expect(hash).toBeTruthy();
      expect(hash).toMatch(/^\$2[aby]\$10\$/); // 10 rounds
    });
  });

  describe('verifyPassword', () => {
    it('should verify correct password', async () => {
      const password = 'mySecurePassword123!';
      const hash = await hashPassword(password);
      const isValid = await verifyPassword(password, hash);

      expect(isValid).toBe(true);
    });

    it('should reject incorrect password', async () => {
      const password = 'mySecurePassword123!';
      const hash = await hashPassword(password);
      const isValid = await verifyPassword('wrongPassword', hash);

      expect(isValid).toBe(false);
    });

    it('should return false for empty password', async () => {
      const hash = await hashPassword('password');
      const isValid = await verifyPassword('', hash);

      expect(isValid).toBe(false);
    });

    it('should return false for empty hash', async () => {
      const isValid = await verifyPassword('password', '');

      expect(isValid).toBe(false);
    });
  });

  describe('hashPasswordSync', () => {
    it('should hash password synchronously', () => {
      const password = 'mySecurePassword123!';
      const hash = hashPasswordSync(password);

      expect(hash).toBeTruthy();
      expect(hash).toMatch(/^\$2[aby]\$\d+\$/);
    });

    it('should throw error for empty password', () => {
      expect(() => hashPasswordSync('')).toThrow();
    });
  });

  describe('verifyPasswordSync', () => {
    it('should verify password synchronously', () => {
      const password = 'mySecurePassword123!';
      const hash = hashPasswordSync(password);
      const isValid = verifyPasswordSync(password, hash);

      expect(isValid).toBe(true);
    });

    it('should reject incorrect password', () => {
      const password = 'mySecurePassword123!';
      const hash = hashPasswordSync(password);
      const isValid = verifyPasswordSync('wrongPassword', hash);

      expect(isValid).toBe(false);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// SHA Hashing Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('SHA Hashing', () => {
  describe('sha256', () => {
    it('should create SHA-256 hash', () => {
      const data = 'test data';
      const hash = sha256(data);

      expect(hash).toBeTruthy();
      expect(hash.length).toBe(64); // SHA-256 hex length
      expect(hash).toMatch(/^[0-9a-f]{64}$/);
    });

    it('should produce consistent hashes', () => {
      const data = 'test data';
      const hash1 = sha256(data);
      const hash2 = sha256(data);

      expect(hash1).toBe(hash2);
    });

    it('should produce different hashes for different data', () => {
      const hash1 = sha256('data1');
      const hash2 = sha256('data2');

      expect(hash1).not.toBe(hash2);
    });

    it('should handle Buffer input', () => {
      const buffer = Buffer.from('test data');
      const hash = sha256(buffer);

      expect(hash).toBeTruthy();
      expect(hash.length).toBe(64);
    });
  });

  describe('sha256Base64', () => {
    it('should create base64 encoded SHA-256 hash', () => {
      const data = 'test data';
      const hash = sha256Base64(data);

      expect(hash).toBeTruthy();
      expect(hash).toMatch(/^[A-Za-z0-9+/]+=*$/); // Base64 format
    });

    it('should produce consistent hashes', () => {
      const data = 'test data';
      const hash1 = sha256Base64(data);
      const hash2 = sha256Base64(data);

      expect(hash1).toBe(hash2);
    });
  });

  describe('sha512', () => {
    it('should create SHA-512 hash', () => {
      const data = 'test data';
      const hash = sha512(data);

      expect(hash).toBeTruthy();
      expect(hash.length).toBe(128); // SHA-512 hex length
      expect(hash).toMatch(/^[0-9a-f]{128}$/);
    });

    it('should produce consistent hashes', () => {
      const data = 'test data';
      const hash1 = sha512(data);
      const hash2 = sha512(data);

      expect(hash1).toBe(hash2);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// HMAC Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('HMAC', () => {
  describe('createHMAC', () => {
    it('should create HMAC signature', () => {
      const data = 'important data';
      const hmac = createHMAC(data);

      expect(hmac).toBeTruthy();
      expect(hmac.length).toBe(64); // SHA-256 HMAC hex length
      expect(hmac).toMatch(/^[0-9a-f]{64}$/);
    });

    it('should produce consistent signatures', () => {
      const data = 'important data';
      const hmac1 = createHMAC(data);
      const hmac2 = createHMAC(data);

      expect(hmac1).toBe(hmac2);
    });

    it('should produce different signatures for different data', () => {
      const hmac1 = createHMAC('data1');
      const hmac2 = createHMAC('data2');

      expect(hmac1).not.toBe(hmac2);
    });

    it('should accept custom secret', () => {
      const data = 'test data';
      const secret = 'custom-secret';
      const hmac = createHMAC(data, secret);

      expect(hmac).toBeTruthy();
    });
  });

  describe('verifyHMAC', () => {
    it('should verify valid HMAC', () => {
      const data = 'important data';
      const hmac = createHMAC(data);
      const isValid = verifyHMAC(data, hmac);

      expect(isValid).toBe(true);
    });

    it('should reject invalid HMAC', () => {
      const data = 'important data';
      const hmac = createHMAC(data);
      const isValid = verifyHMAC('tampered data', hmac);

      expect(isValid).toBe(false);
    });

    it('should reject malformed HMAC', () => {
      const data = 'important data';
      const isValid = verifyHMAC(data, 'invalid-hmac');

      expect(isValid).toBe(false);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Field Encryption Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Field Encryption', () => {
  describe('encrypt and decrypt', () => {
    it('should encrypt and decrypt data', () => {
      const plaintext = 'sensitive data';
      const encrypted = encrypt(plaintext);
      const decrypted = decrypt(encrypted);

      expect(encrypted).not.toBe(plaintext);
      expect(decrypted).toBe(plaintext);
    });

    it('should produce different ciphertexts for same plaintext', () => {
      const plaintext = 'sensitive data';
      const encrypted1 = encrypt(plaintext);
      const encrypted2 = encrypt(plaintext);

      expect(encrypted1).not.toBe(encrypted2); // Different IVs
    });

    it('should handle empty strings', () => {
      const encrypted = encrypt('');
      expect(encrypted).toBe('');

      const decrypted = decrypt('');
      expect(decrypted).toBe('');
    });

    it('should include IV and auth tag', () => {
      const plaintext = 'test data';
      const encrypted = encrypt(plaintext);

      // Format: iv:authTag:ciphertext
      const parts = encrypted.split(':');
      expect(parts.length).toBe(3);
    });
  });

  describe('encryptSearchable and decryptSearchable', () => {
    it('should create deterministic encryption', () => {
      const plaintext = 'searchable data';
      const encrypted1 = encryptSearchable(plaintext);
      const encrypted2 = encryptSearchable(plaintext);

      expect(encrypted1).toBe(encrypted2); // Deterministic
    });

    it('should decrypt with hint', () => {
      const plaintext = 'searchable data';
      const encrypted = encryptSearchable(plaintext);
      const decrypted = decryptSearchable(encrypted, plaintext);

      expect(decrypted).toBe(plaintext);
    });

    it('should fail to decrypt without hint', () => {
      const plaintext = 'searchable data';
      const encrypted = encryptSearchable(plaintext);

      expect(() => decryptSearchable(encrypted)).toThrow();
    });

    it('should handle empty strings', () => {
      const encrypted = encryptSearchable('');
      expect(encrypted).toBe('');
    });
  });

  describe('encryptFields and decryptFields', () => {
    it('should encrypt multiple fields', () => {
      const data = {
        name: 'John Doe',
        email: 'john@example.com',
        phone: '+967712345678',
        publicField: 'visible',
      };

      const encrypted = encryptFields(data, ['email', 'phone']);

      expect(encrypted.name).toBe('John Doe'); // Not encrypted
      expect(encrypted.email).not.toBe('john@example.com'); // Encrypted
      expect(encrypted.phone).not.toBe('+967712345678'); // Encrypted
      expect(encrypted.publicField).toBe('visible'); // Not encrypted
    });

    it('should decrypt multiple fields', () => {
      const data = {
        email: 'john@example.com',
        phone: '+967712345678',
      };

      const encrypted = encryptFields(data, ['email', 'phone']);
      const decrypted = decryptFields(encrypted, ['email', 'phone']);

      expect(decrypted.email).toBe('john@example.com');
      expect(decrypted.phone).toBe('+967712345678');
    });

    it('should use deterministic encryption when specified', () => {
      const data = {
        nationalId: '123456789',
        phone: '+967712345678',
      };

      const encrypted1 = encryptFields(data, ['nationalId', 'phone'], true);
      const encrypted2 = encryptFields(data, ['nationalId', 'phone'], true);

      expect(encrypted1.nationalId).toBe(encrypted2.nationalId);
      expect(encrypted1.phone).toBe(encrypted2.phone);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Encryption Key Management Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Encryption Key Management', () => {
  describe('generateEncryptionKey', () => {
    it('should generate valid encryption key', () => {
      const key = generateEncryptionKey();

      expect(key).toBeTruthy();
      expect(key.length).toBe(64); // 32 bytes in hex
      expect(key).toMatch(/^[0-9a-f]{64}$/);
    });

    it('should generate unique keys', () => {
      const key1 = generateEncryptionKey();
      const key2 = generateEncryptionKey();

      expect(key1).not.toBe(key2);
    });
  });

  describe('validateEncryptionKey', () => {
    it('should validate correct key format', () => {
      const key = generateEncryptionKey();
      expect(validateEncryptionKey(key)).toBe(true);
    });

    it('should reject invalid key length', () => {
      expect(validateEncryptionKey('too-short')).toBe(false);
    });

    it('should reject invalid characters', () => {
      const invalidKey = 'g'.repeat(64); // 'g' is not hex
      expect(validateEncryptionKey(invalidKey)).toBe(false);
    });

    it('should reject non-string keys', () => {
      expect(validateEncryptionKey(123 as any)).toBe(false);
    });
  });

  describe('isEncrypted', () => {
    it('should detect encrypted data', () => {
      const plaintext = 'test data';
      const encrypted = encrypt(plaintext);

      expect(isEncrypted(encrypted)).toBe(true);
      expect(isEncrypted(plaintext)).toBe(false);
    });

    it('should handle empty strings', () => {
      expect(isEncrypted('')).toBe(false);
    });

    it('should handle non-strings', () => {
      expect(isEncrypted(null as any)).toBe(false);
      expect(isEncrypted(undefined as any)).toBe(false);
    });
  });

  describe('rotateEncryption', () => {
    it('should re-encrypt with new key', () => {
      const plaintext = 'test data';
      const encrypted = encrypt(plaintext);

      // Set previous key
      process.env.PREVIOUS_ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;
      process.env.ENCRYPTION_KEY = generateEncryptionKey();

      const rotated = rotateEncryption(encrypted);
      const decrypted = decrypt(rotated);

      expect(decrypted).toBe(plaintext);
      expect(rotated).not.toBe(encrypted);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Specialized Hashing Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Specialized Hashing', () => {
  describe('createDeterministicHash', () => {
    it('should create deterministic hash', () => {
      const data = 'test data';
      const hash1 = createDeterministicHash(data);
      const hash2 = createDeterministicHash(data);

      expect(hash1).toBe(hash2);
    });

    it('should produce different hashes for different data', () => {
      const hash1 = createDeterministicHash('data1');
      const hash2 = createDeterministicHash('data2');

      expect(hash1).not.toBe(hash2);
    });
  });

  describe('hashSensitiveData', () => {
    it('should hash sensitive data with salt', () => {
      const data = 'sensitive';
      const result = hashSensitiveData(data);

      expect(result.hash).toBeTruthy();
      expect(result.salt).toBeTruthy();
      expect(result.hash.length).toBe(64);
    });

    it('should produce different hashes without specified salt', () => {
      const data = 'sensitive';
      const result1 = hashSensitiveData(data);
      const result2 = hashSensitiveData(data);

      expect(result1.hash).not.toBe(result2.hash); // Different salts
      expect(result1.salt).not.toBe(result2.salt);
    });

    it('should produce same hash with same salt', () => {
      const data = 'sensitive';
      const salt = 'fixed-salt';
      const result1 = hashSensitiveData(data, salt);
      const result2 = hashSensitiveData(data, salt);

      expect(result1.hash).toBe(result2.hash);
      expect(result1.salt).toBe(result2.salt);
    });
  });

  describe('verifySensitiveDataHash', () => {
    it('should verify correct sensitive data', () => {
      const data = 'sensitive';
      const { hash, salt } = hashSensitiveData(data);
      const isValid = verifySensitiveDataHash(data, hash, salt);

      expect(isValid).toBe(true);
    });

    it('should reject incorrect data', () => {
      const data = 'sensitive';
      const { hash, salt } = hashSensitiveData(data);
      const isValid = verifySensitiveDataHash('wrong', hash, salt);

      expect(isValid).toBe(false);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Checksum and Integrity Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Checksum and Integrity', () => {
  describe('createChecksum', () => {
    it('should create checksum for data', () => {
      const data = 'test data';
      const checksum = createChecksum(data);

      expect(checksum).toBeTruthy();
      expect(checksum.length).toBe(64);
    });

    it('should produce consistent checksums', () => {
      const data = 'test data';
      const checksum1 = createChecksum(data);
      const checksum2 = createChecksum(data);

      expect(checksum1).toBe(checksum2);
    });

    it('should handle Buffer input', () => {
      const buffer = Buffer.from('test data');
      const checksum = createChecksum(buffer);

      expect(checksum).toBeTruthy();
    });
  });

  describe('verifyChecksum', () => {
    it('should verify valid checksum', () => {
      const data = 'test data';
      const checksum = createChecksum(data);
      const isValid = verifyChecksum(data, checksum);

      expect(isValid).toBe(true);
    });

    it('should reject invalid checksum', () => {
      const data = 'test data';
      const checksum = createChecksum(data);
      const isValid = verifyChecksum('tampered data', checksum);

      expect(isValid).toBe(false);
    });

    it('should handle malformed checksums', () => {
      const data = 'test data';
      const isValid = verifyChecksum(data, 'invalid');

      expect(isValid).toBe(false);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Utility Functions Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Utility Functions', () => {
  describe('generateToken', () => {
    it('should generate secure token', () => {
      const token = generateToken();

      expect(token).toBeTruthy();
      expect(token.length).toBe(64); // 32 bytes in hex
      expect(token).toMatch(/^[0-9a-f]{64}$/);
    });

    it('should generate unique tokens', () => {
      const token1 = generateToken();
      const token2 = generateToken();

      expect(token1).not.toBe(token2);
    });

    it('should accept custom length', () => {
      const token = generateToken(16);

      expect(token.length).toBe(32); // 16 bytes in hex
    });
  });

  describe('generateSecureRandomString', () => {
    it('should generate URL-safe random string', () => {
      const str = generateSecureRandomString();

      expect(str).toBeTruthy();
      expect(str).toMatch(/^[A-Za-z0-9_-]+$/); // Base64url format
    });

    it('should generate unique strings', () => {
      const str1 = generateSecureRandomString();
      const str2 = generateSecureRandomString();

      expect(str1).not.toBe(str2);
    });

    it('should accept custom length', () => {
      const str = generateSecureRandomString(16);

      expect(str).toBeTruthy();
    });
  });

  describe('createHashId', () => {
    it('should create hash-based ID', () => {
      const data = 'test data';
      const id = createHashId(data);

      expect(id).toBeTruthy();
      expect(id.length).toBe(16);
      expect(id).toMatch(/^[0-9a-f]{16}$/);
    });

    it('should produce consistent IDs', () => {
      const data = 'test data';
      const id1 = createHashId(data);
      const id2 = createHashId(data);

      expect(id1).toBe(id2);
    });

    it('should produce different IDs for different data', () => {
      const id1 = createHashId('data1');
      const id2 = createHashId('data2');

      expect(id1).not.toBe(id2);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Integration Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Integration Tests', () => {
  describe('User Data Protection', () => {
    it('should protect user credentials', async () => {
      const userData = {
        email: 'user@example.com',
        password: 'SecurePass123!',
        nationalId: '123456789',
        phone: '+967712345678',
      };

      // Hash password
      const passwordHash = await hashPassword(userData.password);

      // Encrypt sensitive fields
      const encrypted = encryptFields(
        {
          email: userData.email,
          nationalId: userData.nationalId,
          phone: userData.phone,
        },
        ['nationalId', 'phone']
      );

      // Verify password
      const isValidPassword = await verifyPassword(userData.password, passwordHash);
      expect(isValidPassword).toBe(true);

      // Decrypt fields
      const decrypted = decryptFields(encrypted, ['nationalId', 'phone']);
      expect(decrypted.nationalId).toBe(userData.nationalId);
      expect(decrypted.phone).toBe(userData.phone);
    });
  });

  describe('Data Integrity Pipeline', () => {
    it('should ensure data integrity with HMAC', () => {
      const data = { userId: '123', action: 'login', timestamp: Date.now() };
      const jsonData = JSON.stringify(data);

      // Create checksum
      const checksum = createChecksum(jsonData);

      // Create HMAC
      const hmac = createHMAC(jsonData);

      // Verify integrity
      expect(verifyChecksum(jsonData, checksum)).toBe(true);
      expect(verifyHMAC(jsonData, hmac)).toBe(true);

      // Tamper with data
      const tamperedData = JSON.stringify({ ...data, action: 'admin' });
      expect(verifyChecksum(tamperedData, checksum)).toBe(false);
      expect(verifyHMAC(tamperedData, hmac)).toBe(false);
    });
  });

  describe('Searchable Encryption for Database', () => {
    it('should enable searching encrypted fields', () => {
      const users = [
        { name: 'John', nationalId: '123456789' },
        { name: 'Jane', nationalId: '987654321' },
        { name: 'Bob', nationalId: '555555555' },
      ];

      // Encrypt national IDs (searchable)
      const encryptedUsers = users.map((user) => ({
        name: user.name,
        nationalId: encryptSearchable(user.nationalId),
      }));

      // Search for specific national ID
      const searchId = '987654321';
      const encryptedSearchId = encryptSearchable(searchId);

      const found = encryptedUsers.find((user) => user.nationalId === encryptedSearchId);
      expect(found).toBeTruthy();
      expect(found?.name).toBe('Jane');
    });
  });

  describe('Complete Encryption Workflow', () => {
    it('should handle complete encryption workflow', () => {
      // 1. Generate keys
      const encryptionKey = generateEncryptionKey();
      expect(validateEncryptionKey(encryptionKey)).toBe(true);

      // 2. Encrypt data
      const sensitiveData = 'Patient medical record #12345';
      const encrypted = encrypt(sensitiveData);
      expect(isEncrypted(encrypted)).toBe(true);

      // 3. Create checksum
      const checksum = createChecksum(encrypted);

      // 4. Decrypt data
      const decrypted = decrypt(encrypted);
      expect(decrypted).toBe(sensitiveData);

      // 5. Verify integrity
      expect(verifyChecksum(encrypted, checksum)).toBe(true);
    });
  });
});
