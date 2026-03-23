/**
 * Field-Level Encryption Module
 * ==============================
 *
 * Provides AES-256-GCM encryption for field-level data protection.
 * Supports both standard (non-searchable) and deterministic (searchable) encryption.
 *
 * @module field-encryption
 * @author SAHOOL Team
 */

import * as crypto from "crypto";

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Constant-time string comparison to prevent timing side-channel attacks.
 * Uses crypto.timingSafeEqual under the hood.
 */
function constantTimeEqual(a: string, b: string): boolean {
  const bufA = Buffer.from(a, "utf8");
  const bufB = Buffer.from(b, "utf8");
  if (bufA.length !== bufB.length) {
    // Pad shorter buffer to prevent length leak through timingSafeEqual
    const maxLen = Math.max(bufA.length, bufB.length);
    const paddedA = Buffer.alloc(maxLen);
    const paddedB = Buffer.alloc(maxLen);
    bufA.copy(paddedA);
    bufB.copy(paddedB);
    // Always run timingSafeEqual to avoid early return timing leak
    crypto.timingSafeEqual(paddedA, paddedB);
    return false;
  }
  return crypto.timingSafeEqual(bufA, bufB);
}

const ALGORITHM = "aes-256-gcm";
const IV_LENGTH = 16; // 128 bits
const AUTH_TAG_LENGTH = 16; // 128 bits
const SALT_LENGTH = 32; // 256 bits
const KEY_LENGTH = 32; // 256 bits
const PBKDF2_ITERATIONS = 100000;

// ═══════════════════════════════════════════════════════════════════════════
// Key Management
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get encryption key from environment variables
 */
function getEncryptionKey(): Buffer {
  const key = process.env.ENCRYPTION_KEY;
  if (!key) {
    throw new Error("ENCRYPTION_KEY environment variable is not set");
  }

  // Key should be 64 hex characters (32 bytes)
  if (key.length !== 64) {
    throw new Error("ENCRYPTION_KEY must be 64 hex characters (32 bytes)");
  }

  return Buffer.from(key, "hex");
}

/**
 * Get deterministic encryption key from environment variables
 */
function getDeterministicKey(): Buffer {
  const key = process.env.DETERMINISTIC_ENCRYPTION_KEY;
  if (!key) {
    throw new Error(
      "DETERMINISTIC_ENCRYPTION_KEY environment variable is not set",
    );
  }

  if (key.length !== 64) {
    throw new Error(
      "DETERMINISTIC_ENCRYPTION_KEY must be 64 hex characters (32 bytes)",
    );
  }

  return Buffer.from(key, "hex");
}

/**
 * Get previous encryption key for key rotation
 */
function getPreviousKey(): Buffer | null {
  const key = process.env.PREVIOUS_ENCRYPTION_KEY;
  if (!key) {
    return null;
  }

  if (key.length !== 64) {
    throw new Error(
      "PREVIOUS_ENCRYPTION_KEY must be 64 hex characters (32 bytes)",
    );
  }

  return Buffer.from(key, "hex");
}

/**
 * Generate a new encryption key (for setup/rotation)
 */
export function generateEncryptionKey(): string {
  return crypto.randomBytes(KEY_LENGTH).toString("hex");
}

// ═══════════════════════════════════════════════════════════════════════════
// Standard Encryption (Non-Searchable)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Encrypt data using AES-256-GCM (standard, non-searchable encryption)
 *
 * @param plaintext - The data to encrypt
 * @returns Encrypted data in format: iv:authTag:ciphertext (base64)
 *
 * @example
 * ```typescript
 * const encrypted = encrypt('sensitive data');
 * // Returns: "base64IV:base64AuthTag:base64Ciphertext"
 * ```
 */
export function encrypt(plaintext: string): string {
  if (!plaintext) {
    return plaintext;
  }

  try {
    const key = getEncryptionKey();
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ALGORITHM, key, iv);

    let encrypted = cipher.update(plaintext, "utf8", "base64");
    encrypted += cipher.final("base64");

    const authTag = cipher.getAuthTag();

    // Format: iv:authTag:ciphertext (all base64 encoded)
    return `${iv.toString("base64")}:${authTag.toString("base64")}:${encrypted}`;
  } catch (error) {
    throw new Error(
      `Encryption failed: ${error instanceof Error ? error.message : "Unknown error"}`,
    );
  }
}

/**
 * Decrypt data encrypted with AES-256-GCM
 *
 * @param encryptedData - The encrypted data in format: iv:authTag:ciphertext
 * @returns Decrypted plaintext
 *
 * @example
 * ```typescript
 * const decrypted = decrypt(encryptedData);
 * ```
 */
export function decrypt(encryptedData: string): string {
  if (!encryptedData) {
    return encryptedData;
  }

  try {
    // Try with current key
    return decryptWithKey(encryptedData, getEncryptionKey());
  } catch (error) {
    // Try with previous key (for key rotation)
    const previousKey = getPreviousKey();
    if (previousKey) {
      try {
        return decryptWithKey(encryptedData, previousKey);
      } catch {
        // Fall through to throw original error
      }
    }
    throw new Error(
      `Decryption failed: ${error instanceof Error ? error.message : "Unknown error"}`,
    );
  }
}

/**
 * Helper function to decrypt with a specific key
 */
function decryptWithKey(encryptedData: string, key: Buffer): string {
  const parts = encryptedData.split(":");
  if (parts.length !== 3) {
    throw new Error("Invalid encrypted data format");
  }

  const [ivBase64, authTagBase64, encryptedBase64] = parts;

  const iv = Buffer.from(ivBase64, "base64");
  const authTag = Buffer.from(authTagBase64, "base64");
  const encrypted = Buffer.from(encryptedBase64, "base64");

  const decipher = crypto.createDecipheriv(ALGORITHM, key, iv, {
    authTagLength: AUTH_TAG_LENGTH,
  });
  decipher.setAuthTag(authTag);

  let decrypted = decipher.update(encrypted);
  decrypted = Buffer.concat([decrypted, decipher.final()]);

  return decrypted.toString("utf8");
}

// ═══════════════════════════════════════════════════════════════════════════
// Deterministic Encryption (Searchable)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Deterministic encryption - same input always produces same output
 * This allows searching encrypted fields, but provides less security than standard encryption.
 * Use ONLY for fields that need to be searched (e.g., nationalId, phone)
 *
 * @param plaintext - The data to encrypt
 * @returns Deterministically encrypted data
 *
 * @example
 * ```typescript
 * const encrypted1 = encryptDeterministic('12345');
 * const encrypted2 = encryptDeterministic('12345');
 * // encrypted1 === encrypted2 (always)
 * ```
 */
export function encryptDeterministic(plaintext: string): string {
  if (!plaintext) {
    return plaintext;
  }

  try {
    const key = getDeterministicKey();

    // Use HMAC-SHA256 to derive a deterministic IV from the plaintext
    // This ensures same plaintext always gets same IV
    const deterministicIV = crypto
      .createHmac("sha256", key)
      .update(plaintext)
      .digest()
      .slice(0, IV_LENGTH);

    const cipher = crypto.createCipheriv(ALGORITHM, key, deterministicIV);

    let encrypted = cipher.update(plaintext, "utf8", "base64");
    encrypted += cipher.final("base64");

    const authTag = cipher.getAuthTag();

    // Format: authTag:ciphertext (IV is deterministic and not stored)
    return `${authTag.toString("base64")}:${encrypted}`;
  } catch (error) {
    throw new Error(
      `Deterministic encryption failed: ${error instanceof Error ? error.message : "Unknown error"}`,
    );
  }
}

/**
 * Decrypt deterministically encrypted data.
 *
 * Uses the hint (suspected plaintext) to re-derive the same HMAC-based IV
 * that was used during encryption, then decrypts with AES-256-GCM.
 * The GCM auth tag guarantees the hint is correct — a wrong hint will
 * cause an authentication failure.
 *
 * @param encryptedData - The encrypted data in format "authTag:ciphertext"
 * @param hint - The suspected original plaintext
 * @returns Decrypted plaintext
 */
export function decryptDeterministic(
  encryptedData: string,
  hint?: string,
): string {
  if (!encryptedData) {
    return encryptedData;
  }

  if (!hint) {
    throw new Error(
      "Deterministic decryption requires the original value as hint",
    );
  }

  try {
    const key = getDeterministicKey();
    const parts = encryptedData.split(":");

    if (parts.length !== 2) {
      throw new Error("Invalid deterministic encrypted data format");
    }

    const [authTagBase64, encryptedBase64] = parts;
    const authTag = Buffer.from(authTagBase64, "base64");
    const encrypted = Buffer.from(encryptedBase64, "base64");

    // Re-derive the same deterministic IV from the hint
    const deterministicIV = crypto
      .createHmac("sha256", key)
      .update(hint)
      .digest()
      .slice(0, IV_LENGTH);

    const decipher = crypto.createDecipheriv(ALGORITHM, key, deterministicIV, {
      authTagLength: AUTH_TAG_LENGTH,
    });
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(encrypted);
    decrypted = Buffer.concat([decrypted, decipher.final()]);

    return decrypted.toString("utf8");
  } catch (error) {
    throw new Error(
      `Deterministic decryption failed: ${error instanceof Error ? error.message : "Unknown error"}`,
    );
  }
}

/**
 * Deterministic encryption using AES-256-CTR with HMAC-derived IV.
 * Same input always produces same output, enabling encrypted field search.
 *
 * The IV is derived from HMAC-SHA256(key, plaintext) — this is
 * deterministic AND per-deployment (tied to DETERMINISTIC_ENCRYPTION_KEY),
 * unlike the previous fixed-salt approach.
 *
 * Output format: "s2:<base64 ciphertext>" (versioned for migration).
 * Legacy format (no prefix) is still accepted by decryptSearchable.
 */
export function encryptSearchable(plaintext: string): string {
  if (!plaintext) {
    return plaintext;
  }

  try {
    const key = getDeterministicKey();

    // Derive deterministic IV using HMAC-SHA256(key, plaintext)
    // This is per-deployment (key-dependent) unlike the old fixed salt
    const iv = crypto
      .createHmac("sha256", key)
      .update(plaintext)
      .digest()
      .slice(0, IV_LENGTH);

    // Use CTR mode which is deterministic with same IV
    const cipher = crypto.createCipheriv("aes-256-ctr", key, iv);

    let encrypted = cipher.update(plaintext, "utf8", "base64");
    encrypted += cipher.final("base64");

    // Prefix with version tag so decryptSearchable knows the format
    return `s2:${encrypted}`;
  } catch (error) {
    throw new Error(
      `Searchable encryption failed: ${error instanceof Error ? error.message : "Unknown error"}`,
    );
  }
}

/**
 * Decrypt searchable encrypted data.
 *
 * For v2 ("s2:" prefix): derives the same HMAC-based IV from the hint
 * and decrypts with AES-256-CTR.  This works because the IV derivation
 * is deterministic given the key + plaintext.
 *
 * For legacy (no prefix): falls back to hint-comparison only.
 *
 * @param encryptedData - The encrypted string
 * @param hint - The suspected original plaintext (required for decryption)
 */
export function decryptSearchable(
  encryptedData: string,
  hint?: string,
): string {
  if (!encryptedData) {
    return encryptedData;
  }

  if (!hint) {
    throw new Error(
      "Searchable decryption requires the original value as hint",
    );
  }

  // v2 format: "s2:<base64 ciphertext>"
  if (encryptedData.startsWith("s2:")) {
    const ciphertextBase64 = encryptedData.slice(3);
    const key = getDeterministicKey();

    // Derive the same deterministic IV from the hint
    const iv = crypto
      .createHmac("sha256", key)
      .update(hint)
      .digest()
      .slice(0, IV_LENGTH);

    const decipher = crypto.createDecipheriv("aes-256-ctr", key, iv);
    let decrypted = decipher.update(ciphertextBase64, "base64", "utf8");
    decrypted += decipher.final("utf8");

    // Verify the decrypted text matches the hint (CTR mode will always
    // "decrypt" something — we need to confirm it's correct)
    // Use constant-time comparison to prevent timing side-channel attacks
    if (!constantTimeEqual(decrypted, hint)) {
      throw new Error("Searchable decryption: hint does not match");
    }

    return decrypted;
  }

  // Legacy format with random salt: "s1:<salt>:<ciphertext>"
  if (encryptedData.startsWith("s1:")) {
    const parts = encryptedData.split(":");
    if (parts.length !== 3) {
      throw new Error("Invalid s1 encrypted data format");
    }
    const key = getDeterministicKey();
    const salt = Buffer.from(parts[1], "base64");
    const iv = crypto.pbkdf2Sync(hint, salt, 1000, IV_LENGTH, "sha256");
    const decipher = crypto.createDecipheriv("aes-256-ctr", key, iv);
    let decrypted = decipher.update(parts[2], "base64", "utf8");
    decrypted += decipher.final("utf8");
    // Use constant-time comparison to prevent timing side-channel attacks
    if (!constantTimeEqual(decrypted, hint)) {
      throw new Error("Searchable decryption: hint does not match");
    }
    return decrypted;
  }

  // Legacy format (no prefix, fixed salt): compare encrypted values
  // Re-encrypt with fixed-salt legacy function and compare against stored data
  // Use constant-time comparison to prevent timing side-channel attacks
  if (constantTimeEqual(encryptedData, verifyFixedSaltLegacy(hint))) {
    return hint;
  }

  throw new Error(
    "Searchable decryption failed: hint does not match encrypted data",
  );
}

/**
 * Legacy searchable encryption (v1) using fixed salt.
 * @deprecated Use encryptSearchable() for new encryption operations.
 * This function now generates a random salt per operation and stores it
 * alongside the encrypted data. Format: "s1:<base64 salt>:<base64 ciphertext>"
 */
export function encryptLegacySearchable(plaintext: string): string {
  if (!plaintext) {
    return plaintext;
  }

  const key = getDeterministicKey();
  const salt = crypto.randomBytes(SALT_LENGTH);
  const iv = crypto.pbkdf2Sync(plaintext, salt, 1000, IV_LENGTH, "sha256");
  const cipher = crypto.createCipheriv("aes-256-ctr", key, iv);

  let encrypted = cipher.update(plaintext, "utf8", "base64");
  encrypted += cipher.final("base64");

  return `s1:${salt.toString("base64")}:${encrypted}`;
}

/**
 * Verify legacy v1 encrypted data that used the old fixed salt.
 * Used only for migration/verification of pre-existing encrypted data.
 * @internal
 */
function verifyFixedSaltLegacy(plaintext: string): string {
  const key = getDeterministicKey();
  const salt = Buffer.from("sahool-deterministic-salt");
  const iv = crypto.pbkdf2Sync(plaintext, salt, 1000, IV_LENGTH, "sha256");
  const cipher = crypto.createCipheriv("aes-256-ctr", key, iv);

  let encrypted = cipher.update(plaintext, "utf8", "base64");
  encrypted += cipher.final("base64");

  return encrypted;
}

// ═══════════════════════════════════════════════════════════════════════════
// Batch Operations
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Encrypt multiple fields in an object
 *
 * @param data - Object with fields to encrypt
 * @param fields - Array of field names to encrypt
 * @param deterministic - Use deterministic encryption for searchability
 * @returns Object with encrypted fields
 */
export function encryptFields<T extends Record<string, any>>(
  data: T,
  fields: (keyof T)[],
  deterministic = false,
): T {
  const result = { ...data };
  const encryptFn = deterministic ? encryptSearchable : encrypt;

  for (const field of fields) {
    if (result[field] && typeof result[field] === "string") {
      result[field] = encryptFn(result[field] as string) as any;
    }
  }

  return result;
}

/**
 * Decrypt multiple fields in an object
 *
 * @param data - Object with encrypted fields
 * @param fields - Array of field names to decrypt
 * @param deterministic - Use deterministic decryption
 * @returns Object with decrypted fields
 */
export function decryptFields<T extends Record<string, any>>(
  data: T,
  fields: (keyof T)[],
  deterministic = false,
): T {
  const result = { ...data };
  const decryptFn = deterministic ? (val: string) => val : decrypt; // Searchable needs hint — skip in batch

  for (const field of fields) {
    if (result[field] && typeof result[field] === "string") {
      try {
        result[field] = decryptFn(result[field] as string) as any;
      } catch (error) {
        // Log error but don't fail the entire operation
        console.error(`Failed to decrypt field ${String(field)}:`, error);
      }
    }
  }

  return result;
}

// ═══════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if data is encrypted (basic heuristic check)
 */
export function isEncrypted(data: string): boolean {
  if (!data || typeof data !== "string") {
    return false;
  }

  // Check for our encryption format patterns
  const standardFormat = /^[A-Za-z0-9+/]+=*:[A-Za-z0-9+/]+=*:[A-Za-z0-9+/]+=*$/;
  const searchableV2Format = /^s2:[A-Za-z0-9+/]+=*$/;
  const searchableLegacyFormat = /^[A-Za-z0-9+/]+=*$/;

  return (
    standardFormat.test(data) ||
    searchableV2Format.test(data) ||
    (searchableLegacyFormat.test(data) && data.length > 20)
  );
}

/**
 * Rotate encryption key - re-encrypt data with new key
 *
 * @param encryptedData - Data encrypted with old key
 * @returns Data encrypted with new key
 */
export function rotateEncryption(encryptedData: string): string {
  // Decrypt with old key (will try PREVIOUS_ENCRYPTION_KEY automatically)
  const plaintext = decrypt(encryptedData);

  // Encrypt with new key
  return encrypt(plaintext);
}

/**
 * Validate encryption key format
 */
export function validateEncryptionKey(key: string): boolean {
  return (
    typeof key === "string" && key.length === 64 && /^[0-9a-f]+$/i.test(key)
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Exports
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Migrate a legacy searchable-encrypted value (v1, fixed salt) to the
 * current format (v2, HMAC-derived IV).
 *
 * @param legacyCiphertext - Value encrypted with the old encryptSearchable
 * @param plaintext - The known original plaintext
 * @returns New v2-encrypted value, or null if the plaintext doesn't match
 */
export function migrateSearchableEncryption(
  legacyCiphertext: string,
  plaintext: string,
): string | null {
  if (!legacyCiphertext || !plaintext) {
    return null;
  }

  // Already migrated
  if (legacyCiphertext.startsWith("s2:")) {
    return legacyCiphertext;
  }

  // Handle s1: format (random-salt legacy) - verify by decrypting
  if (legacyCiphertext.startsWith("s1:")) {
    const parts = legacyCiphertext.split(":");
    if (parts.length === 3) {
      const salt = Buffer.from(parts[1]!, "base64");
      const key = getDeterministicKey();
      const iv = crypto.pbkdf2Sync(plaintext, salt, 1000, IV_LENGTH, "sha256");
      const cipher = crypto.createCipheriv("aes-256-ctr", key, iv);
      let encrypted = cipher.update(plaintext, "utf8", "base64");
      encrypted += cipher.final("base64");
      if (encrypted !== parts[2]) {
        return null; // plaintext doesn't match
      }
      return encryptSearchable(plaintext);
    }
    return null;
  }

  // Handle fixed-salt legacy format (raw base64, no prefix)
  const reEncrypted = verifyFixedSaltLegacy(plaintext);
  if (reEncrypted !== legacyCiphertext) {
    return null; // plaintext doesn't match
  }

  // Re-encrypt with v2 format
  return encryptSearchable(plaintext);
}

/**
 * Check if a searchable-encrypted value uses the legacy (v1) format.
 */
export function isLegacySearchable(encryptedData: string): boolean {
  if (!encryptedData || typeof encryptedData !== "string") {
    return false;
  }
  // v2 values start with "s2:", everything else is legacy (fixed-salt raw base64 or s1: random-salt)
  return !encryptedData.startsWith("s2:");
}

export default {
  encrypt,
  decrypt,
  encryptDeterministic,
  decryptDeterministic,
  encryptSearchable,
  decryptSearchable,
  encryptLegacySearchable,
  migrateSearchableEncryption,
  isLegacySearchable,
  encryptFields,
  decryptFields,
  generateEncryptionKey,
  isEncrypted,
  rotateEncryption,
  validateEncryptionKey,
};
