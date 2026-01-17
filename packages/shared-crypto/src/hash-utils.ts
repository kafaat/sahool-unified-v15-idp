/**
 * Hashing and HMAC Utilities Module
 * ==================================
 *
 * Provides secure hashing utilities including:
 * - bcrypt password hashing
 * - SHA-256 hashing
 * - HMAC for data integrity
 *
 * @module hash-utils
 * @author SAHOOL Team
 */

import * as crypto from "crypto";
import * as bcrypt from "bcryptjs";

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const DEFAULT_BCRYPT_ROUNDS = 12;
const DEFAULT_HMAC_ALGORITHM = "sha256";

// ═══════════════════════════════════════════════════════════════════════════
// Password Hashing (bcrypt)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hash a password using bcrypt
 *
 * @param password - Plain text password to hash
 * @param rounds - Number of salt rounds (default: 12)
 * @returns Hashed password
 *
 * @example
 * ```typescript
 * const hash = await hashPassword('user-password-123');
 * // Returns: "$2a$12$..." (bcrypt hash)
 * ```
 */
export async function hashPassword(
  password: string,
  rounds: number = DEFAULT_BCRYPT_ROUNDS,
): Promise<string> {
  if (!password) {
    throw new Error("Password cannot be empty");
  }

  try {
    const salt = await bcrypt.genSalt(rounds);
    return await bcrypt.hash(password, salt);
  } catch (error) {
    throw new Error(
      `Password hashing failed: ${error instanceof Error ? error.message : "Unknown error"}`,
    );
  }
}

/**
 * Verify a password against a bcrypt hash
 *
 * @param password - Plain text password to verify
 * @param hash - bcrypt hash to verify against
 * @returns True if password matches, false otherwise
 *
 * @example
 * ```typescript
 * const isValid = await verifyPassword('user-password-123', storedHash);
 * if (isValid) {
 *   console.log('Password is correct');
 * }
 * ```
 */
export async function verifyPassword(
  password: string,
  hash: string,
): Promise<boolean> {
  if (!password || !hash) {
    return false;
  }

  try {
    return await bcrypt.compare(password, hash);
  } catch (error) {
    console.error("Password verification error:", error);
    return false;
  }
}

/**
 * Synchronous password hashing (use only when async is not possible)
 *
 * @param password - Plain text password
 * @param rounds - Number of salt rounds
 * @returns Hashed password
 */
export function hashPasswordSync(
  password: string,
  rounds: number = DEFAULT_BCRYPT_ROUNDS,
): string {
  if (!password) {
    throw new Error("Password cannot be empty");
  }

  try {
    const salt = bcrypt.genSaltSync(rounds);
    return bcrypt.hashSync(password, salt);
  } catch (error) {
    throw new Error(
      `Password hashing failed: ${error instanceof Error ? error.message : "Unknown error"}`,
    );
  }
}

/**
 * Synchronous password verification
 *
 * @param password - Plain text password
 * @param hash - bcrypt hash
 * @returns True if password matches
 */
export function verifyPasswordSync(password: string, hash: string): boolean {
  if (!password || !hash) {
    return false;
  }

  try {
    return bcrypt.compareSync(password, hash);
  } catch (error) {
    console.error("Password verification error:", error);
    return false;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// SHA-256 Hashing
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create SHA-256 hash of data
 *
 * @param data - Data to hash
 * @returns Hex-encoded SHA-256 hash
 *
 * @example
 * ```typescript
 * const hash = sha256('my data');
 * // Returns: "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
 * ```
 */
export function sha256(data: string | Buffer): string {
  return crypto.createHash("sha256").update(data).digest("hex");
}

/**
 * Create SHA-256 hash and return as base64
 *
 * @param data - Data to hash
 * @returns Base64-encoded SHA-256 hash
 */
export function sha256Base64(data: string | Buffer): string {
  return crypto.createHash("sha256").update(data).digest("base64");
}

/**
 * Create SHA-512 hash of data
 *
 * @param data - Data to hash
 * @returns Hex-encoded SHA-512 hash
 */
export function sha512(data: string | Buffer): string {
  return crypto.createHash("sha512").update(data).digest("hex");
}

// ═══════════════════════════════════════════════════════════════════════════
// HMAC (Hash-based Message Authentication Code)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get HMAC secret from environment
 */
function getHmacSecret(): string {
  const secret = process.env.HMAC_SECRET;
  if (!secret) {
    throw new Error("HMAC_SECRET environment variable is not set");
  }
  return secret;
}

/**
 * Create HMAC signature for data integrity verification
 *
 * @param data - Data to sign
 * @param secret - Secret key (optional, uses env var if not provided)
 * @param algorithm - HMAC algorithm (default: sha256)
 * @returns Hex-encoded HMAC signature
 *
 * @example
 * ```typescript
 * const signature = createHMAC('important data');
 * // Later, verify:
 * const isValid = verifyHMAC('important data', signature);
 * ```
 */
export function createHMAC(
  data: string | Buffer,
  secret?: string,
  algorithm: string = DEFAULT_HMAC_ALGORITHM,
): string {
  const hmacSecret = secret || getHmacSecret();

  try {
    return crypto.createHmac(algorithm, hmacSecret).update(data).digest("hex");
  } catch (error) {
    throw new Error(
      `HMAC creation failed: ${error instanceof Error ? error.message : "Unknown error"}`,
    );
  }
}

/**
 * Verify HMAC signature
 *
 * @param data - Original data
 * @param signature - HMAC signature to verify
 * @param secret - Secret key (optional)
 * @param algorithm - HMAC algorithm
 * @returns True if signature is valid
 */
export function verifyHMAC(
  data: string | Buffer,
  signature: string,
  secret?: string,
  algorithm: string = DEFAULT_HMAC_ALGORITHM,
): boolean {
  try {
    const expectedSignature = createHMAC(data, secret, algorithm);
    return crypto.timingSafeEqual(
      Buffer.from(signature, "hex"),
      Buffer.from(expectedSignature, "hex"),
    );
  } catch (error) {
    console.error("HMAC verification error:", error);
    return false;
  }
}

/**
 * Create HMAC with base64 encoding
 */
export function createHMACBase64(
  data: string | Buffer,
  secret?: string,
  algorithm: string = DEFAULT_HMAC_ALGORITHM,
): string {
  const hmacSecret = secret || getHmacSecret();
  return crypto.createHmac(algorithm, hmacSecret).update(data).digest("base64");
}

// ═══════════════════════════════════════════════════════════════════════════
// Specialized Hashing Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create a deterministic hash for data deduplication
 * Uses SHA-256 for consistency
 *
 * @param data - Data to hash
 * @returns Deterministic hash
 */
export function createDeterministicHash(data: string): string {
  return sha256(data);
}

/**
 * Create a hash for sensitive data (with salt)
 *
 * @param data - Sensitive data
 * @param salt - Salt (optional, generated if not provided)
 * @returns Object with hash and salt
 */
export function hashSensitiveData(
  data: string,
  salt?: string,
): { hash: string; salt: string } {
  const dataSalt = salt || crypto.randomBytes(16).toString("hex");
  const hash = sha256(`${data}${dataSalt}`);

  return { hash, salt: dataSalt };
}

/**
 * Verify sensitive data hash
 *
 * @param data - Data to verify
 * @param hash - Hash to verify against
 * @param salt - Salt used in hashing
 * @returns True if data matches hash
 */
export function verifySensitiveDataHash(
  data: string,
  hash: string,
  salt: string,
): boolean {
  const computedHash = sha256(`${data}${salt}`);
  try {
    return crypto.timingSafeEqual(
      Buffer.from(hash, "hex"),
      Buffer.from(computedHash, "hex"),
    );
  } catch {
    return false;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Checksum and Integrity
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create checksum for data integrity verification
 *
 * @param data - Data to checksum
 * @returns Checksum string
 */
export function createChecksum(data: string | Buffer): string {
  return sha256(data);
}

/**
 * Verify data integrity using checksum
 *
 * @param data - Data to verify
 * @param checksum - Expected checksum
 * @returns True if data is intact
 */
export function verifyChecksum(
  data: string | Buffer,
  checksum: string,
): boolean {
  const computed = createChecksum(data);
  try {
    return crypto.timingSafeEqual(
      Buffer.from(checksum, "hex"),
      Buffer.from(computed, "hex"),
    );
  } catch {
    return false;
  }
}

/**
 * Create a file hash (useful for file integrity checks)
 *
 * @param filePath - Path to file
 * @returns Promise with file hash
 */
export async function hashFile(filePath: string): Promise<string> {
  const fs = await import("fs/promises");
  const data = await fs.readFile(filePath);
  return sha256(data);
}

// ═══════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Generate a cryptographically secure random token
 *
 * @param length - Length in bytes (default: 32)
 * @returns Hex-encoded random token
 */
export function generateToken(length: number = 32): string {
  return crypto.randomBytes(length).toString("hex");
}

/**
 * Generate a secure random string (URL-safe)
 *
 * @param length - Length in bytes
 * @returns Base64url-encoded random string
 */
export function generateSecureRandomString(length: number = 32): string {
  return crypto.randomBytes(length).toString("base64url");
}

/**
 * Create a hash-based unique ID from data
 *
 * @param data - Data to create ID from
 * @returns Unique ID (first 16 characters of SHA-256 hash)
 */
export function createHashId(data: string): string {
  return sha256(data).substring(0, 16);
}

// ═══════════════════════════════════════════════════════════════════════════
// Exports
// ═══════════════════════════════════════════════════════════════════════════

export default {
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
};
