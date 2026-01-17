/**
 * Tests for Password Hasher - Argon2id Migration (TypeScript)
 * اختبارات معالج كلمات المرور - ترحيل Argon2id
 *
 * Tests cover:
 * - Argon2id hashing and verification
 * - Backward compatibility with bcrypt
 * - Backward compatibility with PBKDF2
 * - Migration detection
 * - Security properties
 */

import * as crypto from "crypto";
import { promisify } from "util";

// Import the password hasher
import {
  PasswordHasher,
  HashAlgorithm,
  getPasswordHasher,
  hashPassword,
  verifyPassword,
  needsRehash,
  generateOTP,
  generateSecureToken,
} from "../shared/auth/password-hasher";

const pbkdf2Async = promisify(crypto.pbkdf2);

// Check if optional dependencies are available
let argon2: any;
let bcrypt: any;

try {
  argon2 = require("argon2");
} catch (e) {
  console.warn("argon2 not available for tests");
}

try {
  bcrypt = require("bcrypt");
} catch (e) {
  console.warn("bcrypt not available for tests");
}

describe("PasswordHasher", () => {
  let hasher: PasswordHasher;
  const testPassword = "TestPassword123!@#";
  const testPasswords = [
    "SimplePass123",
    "Complex!Pass@2024#",
    "العربية123!", // Arabic password
    "P@ssw0rd",
    "VeryLongPasswordWithManyCharacters123!@#$%^&*()",
  ];

  beforeEach(() => {
    hasher = new PasswordHasher();
  });

  // ========== Argon2id Tests ==========

  describe("Argon2id Hashing", () => {
    const skipIfNoArgon2 = argon2 ? test : test.skip;

    skipIfNoArgon2("should hash password with Argon2id", async () => {
      const hashed = await hasher.hashPassword(testPassword);

      // Verify format
      expect(hashed).toMatch(/^\$argon2/);
      expect(hashed.length).toBeGreaterThan(50);
    });

    skipIfNoArgon2("should verify correct Argon2id password", async () => {
      const hashed = await hasher.hashPassword(testPassword);
      const result = await hasher.verifyPassword(testPassword, hashed);

      expect(result.isValid).toBe(true);
      expect(result.needsRehash).toBe(false); // New hash shouldn't need migration
    });

    skipIfNoArgon2("should reject incorrect Argon2id password", async () => {
      const hashed = await hasher.hashPassword(testPassword);
      const result = await hasher.verifyPassword("WrongPassword123!", hashed);

      expect(result.isValid).toBe(false);
      expect(result.needsRehash).toBe(false);
    });

    skipIfNoArgon2("should use unique salts", async () => {
      const hash1 = await hasher.hashPassword(testPassword);
      const hash2 = await hasher.hashPassword(testPassword);

      // Same password should produce different hashes (different salts)
      expect(hash1).not.toBe(hash2);

      // But both should verify correctly
      const result1 = await hasher.verifyPassword(testPassword, hash1);
      const result2 = await hasher.verifyPassword(testPassword, hash2);

      expect(result1.isValid).toBe(true);
      expect(result2.isValid).toBe(true);
    });
  });

  // ========== Bcrypt Compatibility Tests ==========

  describe("Bcrypt Backward Compatibility", () => {
    const skipIfNoBcrypt = bcrypt ? test : test.skip;

    skipIfNoBcrypt("should verify legacy bcrypt hashes", async () => {
      // Create a legacy bcrypt hash
      const legacyHash = await bcrypt.hash(testPassword, 12);

      // Verify it can be validated
      const result = await hasher.verifyPassword(testPassword, legacyHash);

      expect(result.isValid).toBe(true);
      expect(result.needsRehash).toBe(true); // Should need migration to Argon2id
    });

    skipIfNoBcrypt("should reject incorrect bcrypt password", async () => {
      const legacyHash = await bcrypt.hash(testPassword, 12);
      const result = await hasher.verifyPassword("WrongPassword", legacyHash);

      expect(result.isValid).toBe(false);
    });
  });

  // ========== PBKDF2 Compatibility Tests ==========

  describe("PBKDF2 Backward Compatibility", () => {
    test("should verify legacy PBKDF2 hashes", async () => {
      // Create a legacy PBKDF2 hash
      const salt = crypto.randomBytes(32);
      const hash = await pbkdf2Async(testPassword, salt, 100_000, 32, "sha256");
      const legacyHash = `${salt.toString("hex")}$${hash.toString("hex")}`;

      // Verify it can be validated
      const result = await hasher.verifyPassword(testPassword, legacyHash);

      expect(result.isValid).toBe(true);
      expect(result.needsRehash).toBe(true); // Should need migration to Argon2id
    });

    test("should reject incorrect PBKDF2 password", async () => {
      const salt = crypto.randomBytes(32);
      const hash = await pbkdf2Async(testPassword, salt, 100_000, 32, "sha256");
      const legacyHash = `${salt.toString("hex")}$${hash.toString("hex")}`;

      const result = await hasher.verifyPassword("WrongPassword", legacyHash);

      expect(result.isValid).toBe(false);
    });
  });

  // ========== Migration Detection Tests ==========

  describe("Migration Detection", () => {
    const skipIfNoArgon2 = argon2 ? test : test.skip;

    skipIfNoArgon2(
      "should not require rehash for new Argon2id hashes",
      async () => {
        const hashed = await hasher.hashPassword(testPassword);
        const needsMigration = await hasher.needsRehash(hashed);

        expect(needsMigration).toBe(false);
      },
    );

    const skipIfNoBcrypt = bcrypt ? test : test.skip;

    skipIfNoBcrypt("should require rehash for bcrypt hashes", async () => {
      const legacyHash = await bcrypt.hash(testPassword, 12);
      const needsMigration = await hasher.needsRehash(legacyHash);

      expect(needsMigration).toBe(true);
    });

    test("should require rehash for PBKDF2 hashes", async () => {
      const salt = crypto.randomBytes(32);
      const hash = await pbkdf2Async(testPassword, salt, 100_000, 32, "sha256");
      const legacyHash = `${salt.toString("hex")}$${hash.toString("hex")}`;

      const needsMigration = await hasher.needsRehash(legacyHash);

      expect(needsMigration).toBe(true);
    });
  });

  // ========== Security Tests ==========

  describe("Security Properties", () => {
    test("should reject empty password", async () => {
      await expect(hasher.hashPassword("")).rejects.toThrow(
        "Password cannot be empty",
      );
    });

    test("should return false for empty password/hash verification", async () => {
      const result1 = await hasher.verifyPassword("", "some_hash");
      const result2 = await hasher.verifyPassword("password", "");

      expect(result1.isValid).toBe(false);
      expect(result2.isValid).toBe(false);
    });

    const skipIfNoArgon2 = argon2 ? test : test.skip;

    skipIfNoArgon2("should verify multiple different passwords", async () => {
      for (const password of testPasswords) {
        const hashed = await hasher.hashPassword(password);
        const result = await hasher.verifyPassword(password, hashed);
        expect(result.isValid).toBe(true);

        // Wrong password should fail
        const wrongResult = await hasher.verifyPassword(
          password + "wrong",
          hashed,
        );
        expect(wrongResult.isValid).toBe(false);
      }
    });

    skipIfNoArgon2("should support Unicode passwords", async () => {
      const unicodePasswords = [
        "مرحبا123!", // Arabic
        "你好123!", // Chinese
        "Привет123!", // Russian
        "🔐Password123!", // Emoji
      ];

      for (const password of unicodePasswords) {
        const hashed = await hasher.hashPassword(password);
        const result = await hasher.verifyPassword(password, hashed);
        expect(result.isValid).toBe(true);
      }
    });
  });

  // ========== Global Function Tests ==========

  describe("Global Functions", () => {
    const skipIfNoArgon2 = argon2 ? test : test.skip;

    skipIfNoArgon2("should hash password with global function", async () => {
      const hashed = await hashPassword(testPassword);
      expect(hashed).toMatch(/^\$argon2/);
    });

    skipIfNoArgon2("should verify password with global function", async () => {
      const hashed = await hashPassword(testPassword);
      const result = await verifyPassword(testPassword, hashed);

      expect(result.isValid).toBe(true);
      expect(result.needsRehash).toBe(false);
    });

    test("should return same instance from getPasswordHasher", () => {
      const hasher1 = getPasswordHasher();
      const hasher2 = getPasswordHasher();

      expect(hasher1).toBe(hasher2); // Should be singleton
    });
  });

  // ========== Utility Function Tests ==========

  describe("Utility Functions", () => {
    test("should generate OTP with correct length", () => {
      const otp = generateOTP(6);

      expect(otp).toHaveLength(6);
      expect(otp).toMatch(/^\d+$/); // Only digits
    });

    test("should generate OTP with default length", () => {
      const otp = generateOTP();

      expect(otp).toHaveLength(4);
    });

    test("should generate unique OTPs", () => {
      const otps = Array.from({ length: 100 }, () => generateOTP(6));
      const uniqueOtps = new Set(otps);

      // Should have variety (at least 50% unique)
      expect(uniqueOtps.size).toBeGreaterThan(50);
    });

    test("should generate secure token with correct length", () => {
      const token = generateSecureToken(32);

      // Should be hex string of length 64 (32 bytes = 64 hex chars)
      expect(token).toHaveLength(64);
      expect(token).toMatch(/^[0-9a-f]+$/);
    });

    test("should generate unique secure tokens", () => {
      const token1 = generateSecureToken(32);
      const token2 = generateSecureToken(32);

      expect(token1).not.toBe(token2);
    });
  });

  // ========== Edge Cases ==========

  describe("Edge Cases", () => {
    test("should handle malformed hash formats", async () => {
      const malformedHashes = [
        "invalid",
        "$invalid$format",
        "no_dollar_sign",
        "$",
        "$$",
      ];

      for (const badHash of malformedHashes) {
        const result = await hasher.verifyPassword(testPassword, badHash);
        expect(result.isValid).toBe(false);
      }
    });
  });
});

// ========== Integration Tests ==========

describe("Password Migration Scenarios", () => {
  let hasher: PasswordHasher;
  const testPassword = "UserPassword123!";

  beforeEach(() => {
    hasher = new PasswordHasher();
  });

  const skipIfNoArgon2OrBcrypt = argon2 && bcrypt ? test : test.skip;

  skipIfNoArgon2OrBcrypt(
    "should complete full migration flow from bcrypt to Argon2id",
    async () => {
      // Step 1: User has old bcrypt password
      const oldHash = await bcrypt.hash(testPassword, 12);

      // Step 2: User logs in - verify old password
      let result = await hasher.verifyPassword(testPassword, oldHash);

      expect(result.isValid).toBe(true);
      expect(result.needsRehash).toBe(true);

      // Step 3: Generate new Argon2id hash
      const newHash = await hasher.hashPassword(testPassword);

      // Step 4: Verify new hash works
      result = await hasher.verifyPassword(testPassword, newHash);

      expect(result.isValid).toBe(true);
      expect(result.needsRehash).toBe(false);
    },
  );

  const skipIfNoArgon2 = argon2 ? test : test.skip;

  skipIfNoArgon2(
    "should complete full migration flow from PBKDF2 to Argon2id",
    async () => {
      // Step 1: User has old PBKDF2 password
      const salt = crypto.randomBytes(32);
      const hash = await pbkdf2Async(testPassword, salt, 100_000, 32, "sha256");
      const oldHash = `${salt.toString("hex")}$${hash.toString("hex")}`;

      // Step 2: User logs in - verify old password
      let result = await hasher.verifyPassword(testPassword, oldHash);

      expect(result.isValid).toBe(true);
      expect(result.needsRehash).toBe(true);

      // Step 3: Generate new Argon2id hash
      const newHash = await hasher.hashPassword(testPassword);

      // Step 4: Verify new hash works
      result = await hasher.verifyPassword(testPassword, newHash);

      expect(result.isValid).toBe(true);
      expect(result.needsRehash).toBe(false);
    },
  );
});
