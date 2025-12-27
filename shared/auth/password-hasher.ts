/**
 * SAHOOL Password Hasher - Argon2id Migration
 * معالج كلمات المرور - الترحيل إلى Argon2id
 *
 * This module provides secure password hashing using Argon2id with backward compatibility
 * for bcrypt and PBKDF2 hashes. Supports automatic migration on successful login.
 *
 * يوفر هذا الوحدة تشفير آمن لكلمات المرور باستخدام Argon2id مع التوافق
 * للخلف مع bcrypt و PBKDF2. يدعم الترحيل التلقائي عند تسجيل الدخول الناجح.
 */

import * as crypto from 'crypto';
import { promisify } from 'util';

// Import password hashing libraries
let argon2: any;
let bcrypt: any;

try {
  argon2 = require('argon2');
} catch (e) {
  console.warn('argon2 not available. Please install: npm install argon2');
}

try {
  bcrypt = require('bcrypt');
} catch (e) {
  console.warn('bcrypt not available. Please install: npm install bcrypt');
}

const pbkdf2Async = promisify(crypto.pbkdf2);

/**
 * Supported password hashing algorithms
 */
export enum HashAlgorithm {
  ARGON2ID = 'argon2id',
  BCRYPT = 'bcrypt',
  PBKDF2_SHA256 = 'pbkdf2_sha256',
  UNKNOWN = 'unknown',
}

/**
 * Password verification result
 */
export interface VerificationResult {
  isValid: boolean;
  needsRehash: boolean;
}

/**
 * Password hasher configuration
 */
export interface PasswordHasherConfig {
  /** Argon2 time cost (number of iterations) */
  timeCost?: number;
  /** Argon2 memory cost in KiB */
  memoryCost?: number;
  /** Argon2 parallelism (number of threads) */
  parallelism?: number;
  /** Hash length in bytes */
  hashLength?: number;
  /** Salt length in bytes */
  saltLength?: number;
}

/**
 * Secure password hasher with migration support
 *
 * Features:
 * - Primary: Argon2id (recommended by OWASP)
 * - Legacy support: bcrypt, PBKDF2-SHA256
 * - Automatic migration on successful verification
 * - Constant-time comparison
 */
export class PasswordHasher {
  private readonly timeCost: number;
  private readonly memoryCost: number;
  private readonly parallelism: number;
  private readonly hashLength: number;
  private readonly saltLength: number;

  constructor(config: PasswordHasherConfig = {}) {
    this.timeCost = config.timeCost ?? 2; // OWASP minimum
    this.memoryCost = config.memoryCost ?? 65536; // 64 MB
    this.parallelism = config.parallelism ?? 4; // 4 threads
    this.hashLength = config.hashLength ?? 32; // 256 bits
    this.saltLength = config.saltLength ?? 16; // 128 bits

    if (!argon2) {
      console.warn('Argon2 not available, falling back to bcrypt/PBKDF2');
    }
  }

  /**
   * Hash a password using Argon2id (primary) or fallback algorithms
   *
   * @param password - Plain text password
   * @returns Hashed password with algorithm identifier
   */
  async hashPassword(password: string): Promise<string> {
    if (!password) {
      throw new Error('Password cannot be empty');
    }

    // Primary: Use Argon2id
    if (argon2) {
      try {
        return await argon2.hash(password, {
          type: argon2.argon2id,
          timeCost: this.timeCost,
          memoryCost: this.memoryCost,
          parallelism: this.parallelism,
          hashLength: this.hashLength,
          saltLength: this.saltLength,
        });
      } catch (error) {
        console.error('Argon2 hashing error:', error);
        // Fall through to bcrypt
      }
    }

    // Fallback 1: bcrypt
    if (bcrypt) {
      try {
        const saltRounds = 12;
        return await bcrypt.hash(password, saltRounds);
      } catch (error) {
        console.error('bcrypt hashing error:', error);
        // Fall through to PBKDF2
      }
    }

    // Fallback 2: PBKDF2-SHA256
    return this.hashPbkdf2(password);
  }

  /**
   * Verify a password against its hash
   *
   * @param password - Plain text password to verify
   * @param hashedPassword - Stored hash
   * @returns Verification result with rehash recommendation
   */
  async verifyPassword(
    password: string,
    hashedPassword: string
  ): Promise<VerificationResult> {
    if (!password || !hashedPassword) {
      return { isValid: false, needsRehash: false };
    }

    try {
      const algorithm = this.detectAlgorithm(hashedPassword);

      switch (algorithm) {
        case HashAlgorithm.ARGON2ID:
          return await this.verifyArgon2(password, hashedPassword);
        case HashAlgorithm.BCRYPT:
          return await this.verifyBcrypt(password, hashedPassword);
        case HashAlgorithm.PBKDF2_SHA256:
          return await this.verifyPbkdf2(password, hashedPassword);
        default:
          console.warn('Unknown hash algorithm for password');
          return { isValid: false, needsRehash: false };
      }
    } catch (error) {
      console.error('Password verification error:', error);
      return { isValid: false, needsRehash: false };
    }
  }

  /**
   * Detect the algorithm used for a hashed password
   *
   * @param hashedPassword - The hashed password string
   * @returns HashAlgorithm enum value
   */
  private detectAlgorithm(hashedPassword: string): HashAlgorithm {
    if (hashedPassword.startsWith('$argon2')) {
      return HashAlgorithm.ARGON2ID;
    } else if (
      hashedPassword.startsWith('$2a$') ||
      hashedPassword.startsWith('$2b$') ||
      hashedPassword.startsWith('$2y$')
    ) {
      return HashAlgorithm.BCRYPT;
    } else if (hashedPassword.includes('$') && hashedPassword.split('$').length >= 2) {
      // PBKDF2 format: salt$hash
      return HashAlgorithm.PBKDF2_SHA256;
    } else {
      return HashAlgorithm.UNKNOWN;
    }
  }

  /**
   * Verify Argon2id password
   */
  private async verifyArgon2(
    password: string,
    hashedPassword: string
  ): Promise<VerificationResult> {
    if (!argon2) {
      console.error('Argon2 not available but hash is Argon2 format');
      return { isValid: false, needsRehash: false };
    }

    try {
      const isValid = await argon2.verify(hashedPassword, password);

      // Check if rehash is needed (parameters changed)
      let needsRehash = false;
      if (isValid) {
        needsRehash = await argon2.needsRehash(hashedPassword, {
          type: argon2.argon2id,
          timeCost: this.timeCost,
          memoryCost: this.memoryCost,
          parallelism: this.parallelism,
        });
      }

      return { isValid, needsRehash };
    } catch (error) {
      // argon2.verify throws on mismatch
      return { isValid: false, needsRehash: false };
    }
  }

  /**
   * Verify bcrypt password - always needs migration to Argon2id
   */
  private async verifyBcrypt(
    password: string,
    hashedPassword: string
  ): Promise<VerificationResult> {
    if (!bcrypt) {
      console.error('bcrypt not available but hash is bcrypt format');
      return { isValid: false, needsRehash: false };
    }

    try {
      const isValid = await bcrypt.compare(password, hashedPassword);
      // Always migrate bcrypt to Argon2id
      return { isValid, needsRehash: isValid };
    } catch (error) {
      console.error('bcrypt verification error:', error);
      return { isValid: false, needsRehash: false };
    }
  }

  /**
   * Verify PBKDF2-SHA256 password - always needs migration to Argon2id
   */
  private async verifyPbkdf2(
    password: string,
    hashedPassword: string
  ): Promise<VerificationResult> {
    try {
      const parts = hashedPassword.split('$');
      if (parts.length !== 2) {
        return { isValid: false, needsRehash: false };
      }

      const [saltHex, storedHashHex] = parts;
      const salt = Buffer.from(saltHex, 'hex');

      // Compute hash with same salt
      const computedHash = await pbkdf2Async(
        password,
        salt,
        100_000,
        32,
        'sha256'
      );

      // Constant-time comparison
      const isValid = crypto.timingSafeEqual(
        Buffer.from(storedHashHex, 'hex'),
        computedHash
      );

      // Always migrate PBKDF2 to Argon2id
      return { isValid, needsRehash: isValid };
    } catch (error) {
      console.error('PBKDF2 verification error:', error);
      return { isValid: false, needsRehash: false };
    }
  }

  /**
   * Hash password using PBKDF2-SHA256 (fallback only)
   *
   * @param password - Plain text password
   * @returns Hashed password in format: salt$hash (hex encoded)
   */
  private async hashPbkdf2(password: string): Promise<string> {
    const salt = crypto.randomBytes(32);
    const hash = await pbkdf2Async(password, salt, 100_000, 32, 'sha256');
    return `${salt.toString('hex')}$${hash.toString('hex')}`;
  }

  /**
   * Check if a password hash needs to be rehashed
   *
   * @param hashedPassword - The hashed password to check
   * @returns True if the password should be rehashed
   */
  async needsRehash(hashedPassword: string): Promise<boolean> {
    try {
      const algorithm = this.detectAlgorithm(hashedPassword);

      // Always rehash non-Argon2 hashes
      if (algorithm !== HashAlgorithm.ARGON2ID) {
        return true;
      }

      // Check if Argon2 parameters have changed
      if (argon2) {
        return await argon2.needsRehash(hashedPassword, {
          type: argon2.argon2id,
          timeCost: this.timeCost,
          memoryCost: this.memoryCost,
          parallelism: this.parallelism,
        });
      }

      return false;
    } catch (error) {
      return false;
    }
  }
}

// Global instance with recommended parameters
let defaultHasher: PasswordHasher | null = null;

/**
 * Get the default password hasher instance
 *
 * @returns PasswordHasher instance with recommended settings
 */
export function getPasswordHasher(): PasswordHasher {
  if (!defaultHasher) {
    defaultHasher = new PasswordHasher({
      timeCost: 2,        // OWASP recommended minimum
      memoryCost: 65536,  // 64 MB
      parallelism: 4,     // 4 parallel threads
      hashLength: 32,     // 256 bits
      saltLength: 16,     // 128 bits
    });
  }
  return defaultHasher;
}

/**
 * Hash a password using the default hasher
 *
 * @param password - Plain text password
 * @returns Hashed password
 */
export async function hashPassword(password: string): Promise<string> {
  return getPasswordHasher().hashPassword(password);
}

/**
 * Verify a password using the default hasher
 *
 * @param password - Plain text password
 * @param hashedPassword - Stored hash
 * @returns Verification result
 */
export async function verifyPassword(
  password: string,
  hashedPassword: string
): Promise<VerificationResult> {
  return getPasswordHasher().verifyPassword(password, hashedPassword);
}

/**
 * Check if a password needs rehashing
 *
 * @param hashedPassword - Stored hash
 * @returns True if rehashing is recommended
 */
export async function needsRehash(hashedPassword: string): Promise<boolean> {
  return getPasswordHasher().needsRehash(hashedPassword);
}

// Utility functions for backward compatibility

/**
 * Generate a numeric OTP code
 *
 * @param length - Number of digits (default 4)
 * @returns Numeric OTP string
 */
export function generateOTP(length: number = 4): string {
  const digits = '0123456789';
  let otp = '';
  for (let i = 0; i < length; i++) {
    const randomIndex = crypto.randomInt(0, digits.length);
    otp += digits[randomIndex];
  }
  return otp;
}

/**
 * Generate a secure random token
 *
 * @param length - Token length in bytes
 * @returns Hex-encoded token string
 */
export function generateSecureToken(length: number = 32): string {
  return crypto.randomBytes(length).toString('hex');
}
