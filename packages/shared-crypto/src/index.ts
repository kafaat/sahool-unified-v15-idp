/**
 * @sahool/shared-crypto
 * ====================
 *
 * Main entry point for SAHOOL shared cryptography library
 *
 * @module @sahool/shared-crypto
 * @author SAHOOL Team
 */

// ═══════════════════════════════════════════════════════════════════════════
// Field Encryption
// ═══════════════════════════════════════════════════════════════════════════

export {
  encrypt,
  decrypt,
  encryptDeterministic,
  decryptDeterministic,
  encryptSearchable,
  decryptSearchable,
  encryptFields,
  decryptFields,
  generateEncryptionKey,
  isEncrypted,
  rotateEncryption,
  validateEncryptionKey,
} from "./field-encryption";

// ═══════════════════════════════════════════════════════════════════════════
// Hash Utilities
// ═══════════════════════════════════════════════════════════════════════════

export {
  // Password hashing
  hashPassword,
  verifyPassword,
  hashPasswordSync,
  verifyPasswordSync,

  // SHA hashing
  sha256,
  sha256Base64,
  sha512,

  // HMAC
  createHMAC,
  verifyHMAC,
  createHMACBase64,

  // Specialized hashing
  createDeterministicHash,
  hashSensitiveData,
  verifySensitiveDataHash,

  // Integrity
  createChecksum,
  verifyChecksum,
  hashFile,

  // Utilities
  generateToken,
  generateSecureRandomString,
  createHashId,
} from "./hash-utils";

// ═══════════════════════════════════════════════════════════════════════════
// PII Handler
// ═══════════════════════════════════════════════════════════════════════════

export {
  // Types and Enums
  PIIType,
  MaskingStrategy,
  SensitivityLevel,
  PIIDetection,

  // Detection
  detectPII,
  containsPII,
  getPIITypes,

  // Masking
  maskPII,
  redactPII,

  // Encryption Decision
  shouldEncrypt,
  getSensitivityLevel,
  shouldUseDeterministicEncryption,
  autoEncrypt,
  encryptSensitiveFields,
} from "./pii-handler";

// ═══════════════════════════════════════════════════════════════════════════
// Prisma Encryption Middleware
// ═══════════════════════════════════════════════════════════════════════════

export {
  createPrismaEncryptionMiddleware,
  EncryptionConfig,
  FieldEncryptionConfig,
  ModelEncryptionConfig,
} from "./prisma-encryption";

// ═══════════════════════════════════════════════════════════════════════════
// Default Export
// ═══════════════════════════════════════════════════════════════════════════

import * as fieldEncryption from "./field-encryption";
import * as hashUtils from "./hash-utils";
import * as piiHandler from "./pii-handler";

export default {
  ...fieldEncryption,
  ...hashUtils,
  ...piiHandler,
};
