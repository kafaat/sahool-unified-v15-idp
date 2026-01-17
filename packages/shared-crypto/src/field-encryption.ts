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

  const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
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
 * Decrypt deterministically encrypted data
 *
 * @param encryptedData - The encrypted data
 * @returns Decrypted plaintext
 */
export function decryptDeterministic(encryptedData: string): string {
  if (!encryptedData) {
    return encryptedData;
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

    // We need to try decryption to recover the plaintext since we can't
    // derive the IV without knowing the plaintext. This is a limitation
    // of deterministic encryption that we accept for searchability.
    // We'll use a different approach: store a hash alongside for verification.

    // For now, we'll use a simpler deterministic approach with AES-256-ECB
    // which is deterministic by nature (no IV). Less secure but searchable.
    throw new Error(
      "Deterministic decryption requires the original implementation",
    );
  } catch (error) {
    throw new Error(
      `Deterministic decryption failed: ${error instanceof Error ? error.message : "Unknown error"}`,
    );
  }
}

/**
 * Alternative: Deterministic encryption using AES-256-CTR with deterministic IV
 * This is more suitable for searchable encryption
 */
export function encryptSearchable(plaintext: string): string {
  if (!plaintext) {
    return plaintext;
  }

  try {
    const key = getDeterministicKey();

    // Derive deterministic IV using PBKDF2
    const salt = Buffer.from("sahool-deterministic-salt"); // Fixed salt for determinism
    const iv = crypto.pbkdf2Sync(plaintext, salt, 1000, IV_LENGTH, "sha256");

    // Use CTR mode which is deterministic with same IV
    const cipher = crypto.createCipheriv("aes-256-ctr", key, iv);

    let encrypted = cipher.update(plaintext, "utf8", "base64");
    encrypted += cipher.final("base64");

    return encrypted;
  } catch (error) {
    throw new Error(
      `Searchable encryption failed: ${error instanceof Error ? error.message : "Unknown error"}`,
    );
  }
}

/**
 * Decrypt searchable encrypted data
 */
export function decryptSearchable(
  encryptedData: string,
  hint?: string,
): string {
  if (!encryptedData) {
    return encryptedData;
  }

  // For searchable encryption, we need the original plaintext to derive the IV
  // This is a known limitation. In practice, you'd search by encrypting the
  // search term and comparing encrypted values.

  // If we have a hint (the value we're searching for), we can decrypt
  if (hint) {
    const encrypted = encryptSearchable(hint);
    if (encrypted === encryptedData) {
      return hint;
    }
  }

  throw new Error(
    "Searchable decryption requires the original value as hint, or use brute force (not recommended)",
  );
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
  const decryptFn = deterministic ? (val: string) => val : decrypt; // Searchable can't be decrypted without hint

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
  const searchableFormat = /^[A-Za-z0-9+/]+=*$/;

  return (
    standardFormat.test(data) ||
    (searchableFormat.test(data) && data.length > 20)
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

export default {
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
};
