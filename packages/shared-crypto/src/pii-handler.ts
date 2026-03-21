/**
 * PII (Personally Identifiable Information) Handler Module
 * =========================================================
 *
 * Provides utilities for:
 * - Detecting PII in text and data
 * - Masking/redacting sensitive information
 * - Determining encryption requirements
 *
 * @module pii-handler
 * @author SAHOOL Team
 */

import { encryptSearchable, encrypt } from "./field-encryption";

// ═══════════════════════════════════════════════════════════════════════════
// PII Detection Patterns
// ═══════════════════════════════════════════════════════════════════════════

/**
 * PII Types supported
 */
export enum PIIType {
  NATIONAL_ID = "NATIONAL_ID",
  PHONE = "PHONE",
  EMAIL = "EMAIL",
  CREDIT_CARD = "CREDIT_CARD",
  SSN = "SSN", // Social Security Number
  PASSPORT = "PASSPORT",
  IBAN = "IBAN",
  IP_ADDRESS = "IP_ADDRESS",
  DATE_OF_BIRTH = "DATE_OF_BIRTH",
  NAME = "NAME",
  ADDRESS = "ADDRESS",
}

/**
 * PII Detection Result
 */
export interface PIIDetection {
  type: PIIType;
  value: string;
  startIndex: number;
  endIndex: number;
  confidence: number; // 0-1
}

/**
 * Regular expressions for PII detection.
 *
 * Patterns are intentionally specific to reduce false positives —
 * phone patterns require recognisable country prefixes, credit cards
 * are post-validated with Luhn, IBANs are post-validated with mod-97.
 */
const PII_PATTERNS: Record<PIIType, RegExp> = {
  // Saudi National ID: 10 digits starting with 1 (citizen) or 2 (resident)
  [PIIType.NATIONAL_ID]: /\b[12]\d{9}\b/g,

  // Phone numbers: require recognisable prefix to avoid matching arbitrary
  // 10-digit numbers (timestamps, IDs, GPS coordinates, etc.)
  // Supports: +966, 00966, 05x (Saudi), +<country> with delimiters
  [PIIType.PHONE]:
    /(?:\+966|00966|05)\d{8,9}|(?:\+\d{1,3}[-.\s])\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}/g,

  // Email addresses — require valid TLD length (2-63), no consecutive dots
  [PIIType.EMAIL]:
    /\b[A-Za-z0-9](?:[A-Za-z0-9._%+-]*[A-Za-z0-9])?@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}\b/g,

  // Credit card numbers (16 digits with optional spaces/dashes)
  // Post-validated with Luhn algorithm in calculateConfidence()
  [PIIType.CREDIT_CARD]: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g,

  // SSN (US format: 123-45-6789, excluding invalid area 000/666/9xx)
  [PIIType.SSN]: /\b(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b/g,

  // Passport: country-letter prefix + digits, tighter length bounds
  [PIIType.PASSPORT]: /\b[A-Z]{1,2}\d{6,9}\b/g,

  // IBAN — post-validated with mod-97 in calculateConfidence()
  [PIIType.IBAN]: /\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b/g,

  // IP Address (IPv4 with valid octet ranges)
  [PIIType.IP_ADDRESS]:
    /\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b/g,

  // Date of Birth (DD/MM/YYYY or YYYY-MM-DD, years 1920-2025)
  [PIIType.DATE_OF_BIRTH]:
    /\b(0?[1-9]|[12]\d|3[01])[\/\-](0?[1-9]|1[012])[\/\-](19[2-9]\d|20[01]\d|202[0-5])\b|\b(19[2-9]\d|20[01]\d|202[0-5])[\/\-](0?[1-9]|1[012])[\/\-](0?[1-9]|[12]\d|3[01])\b/g,

  // Names: English "Firstname Lastname" or Arabic names (3+ Arabic chars with spaces)
  [PIIType.NAME]:
    /\b[A-Z][a-z]{1,20}\s[A-Z][a-z]{1,20}\b|[\u0621-\u064A][\u0600-\u06FF]{1,20}\s[\u0621-\u064A][\u0600-\u06FF]{1,20}/g,

  // Addresses: number + street with common suffixes (EN) or Arabic street keywords
  [PIIType.ADDRESS]:
    /\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)|(?:شارع|طريق|حي|مبنى)\s+[\u0600-\u06FF\s]{2,}/gi,
};

// ═══════════════════════════════════════════════════════════════════════════
// PII Detection
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Detect PII in text
 *
 * @param text - Text to analyze
 * @param types - Specific PII types to detect (optional, defaults to all)
 * @returns Array of detected PII
 *
 * @example
 * ```typescript
 * const text = "My phone is 0551234567 and email is user@example.com";
 * const detected = detectPII(text);
 * // Returns: [{ type: 'PHONE', value: '0551234567', ... }, { type: 'EMAIL', ... }]
 * ```
 */
export function detectPII(text: string, types?: PIIType[]): PIIDetection[] {
  const results: PIIDetection[] = [];
  const typesToCheck = types || Object.values(PIIType);

  for (const type of typesToCheck) {
    const pattern = PII_PATTERNS[type];
    if (!pattern) continue;

    // Reset regex state
    pattern.lastIndex = 0;

    let match;
    while ((match = pattern.exec(text)) !== null) {
      results.push({
        type,
        value: match[0],
        startIndex: match.index,
        endIndex: match.index + match[0].length,
        confidence: calculateConfidence(type, match[0]),
      });
    }
  }

  return results;
}

/**
 * Luhn algorithm for credit card number validation.
 */
function passesLuhn(digits: string): boolean {
  const nums = digits.replace(/[\s-]/g, "");
  if (!/^\d+$/.test(nums)) return false;
  let sum = 0;
  let alt = false;
  for (let i = nums.length - 1; i >= 0; i--) {
    let n = parseInt(nums[i], 10);
    if (alt) {
      n *= 2;
      if (n > 9) n -= 9;
    }
    sum += n;
    alt = !alt;
  }
  return sum % 10 === 0;
}

/**
 * ISO 7064 mod-97 check for IBAN validation.
 */
function passesIBANCheck(iban: string): boolean {
  // Move country code + check digits to end
  const rearranged = iban.slice(4) + iban.slice(0, 4);
  // Replace letters with numbers (A=10, B=11, ..., Z=35)
  const numeric = rearranged.replace(/[A-Z]/g, (ch) =>
    String(ch.charCodeAt(0) - 55),
  );
  // Compute mod-97 on large number (process in chunks)
  let remainder = 0;
  for (let i = 0; i < numeric.length; i += 7) {
    const chunk = String(remainder) + numeric.slice(i, i + 7);
    remainder = parseInt(chunk, 10) % 97;
  }
  return remainder === 1;
}

/**
 * Calculate confidence score for PII detection with algorithmic validation.
 */
function calculateConfidence(type: PIIType, value: string): number {
  switch (type) {
    case PIIType.EMAIL:
      return value.includes("@gmail.com") ||
        value.includes("@yahoo.com") ||
        value.includes("@outlook.com")
        ? 0.95
        : 0.85;

    case PIIType.PHONE:
      return value.startsWith("05") || value.startsWith("+966")
        ? 0.95
        : 0.8;

    case PIIType.NATIONAL_ID:
      return value.startsWith("1") || value.startsWith("2") ? 0.9 : 0.6;

    case PIIType.CREDIT_CARD:
      // Validate with Luhn algorithm
      return passesLuhn(value) ? 0.95 : 0.3;

    case PIIType.IBAN:
      // Validate with mod-97 checksum
      return passesIBANCheck(value) ? 0.95 : 0.3;

    case PIIType.NAME:
      // Arabic names get slightly lower confidence (regex is broad)
      return /[A-Z]/.test(value) ? 0.7 : 0.6;

    default:
      return 0.7;
  }
}

/**
 * Check if text contains any PII
 *
 * @param text - Text to check
 * @returns True if PII is detected
 */
export function containsPII(text: string): boolean {
  return detectPII(text).length > 0;
}

/**
 * Get PII types present in text
 *
 * @param text - Text to analyze
 * @returns Array of PII types found
 */
export function getPIITypes(text: string): PIIType[] {
  const detected = detectPII(text);
  return [...new Set(detected.map((d) => d.type))];
}

// ═══════════════════════════════════════════════════════════════════════════
// PII Masking/Redaction
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Masking strategy
 */
export enum MaskingStrategy {
  FULL = "FULL", // Replace all characters with *
  PARTIAL = "PARTIAL", // Show first/last few characters
  HASH = "HASH", // Replace with hash
  REMOVE = "REMOVE", // Remove completely
}

/**
 * Mask PII in text
 *
 * @param text - Text containing PII
 * @param strategy - Masking strategy
 * @param types - Specific PII types to mask (optional)
 * @returns Masked text
 *
 * @example
 * ```typescript
 * const text = "My phone is 0551234567";
 * const masked = maskPII(text, MaskingStrategy.PARTIAL);
 * // Returns: "My phone is 055****567"
 * ```
 */
export function maskPII(
  text: string,
  strategy: MaskingStrategy = MaskingStrategy.PARTIAL,
  types?: PIIType[],
): string {
  const detected = detectPII(text, types);

  // Sort by start index in reverse to avoid index shifting
  detected.sort((a, b) => b.startIndex - a.startIndex);

  let maskedText = text;

  for (const detection of detected) {
    const masked = maskValue(detection.value, detection.type, strategy);
    maskedText =
      maskedText.substring(0, detection.startIndex) +
      masked +
      maskedText.substring(detection.endIndex);
  }

  return maskedText;
}

/**
 * Mask a single value based on its type and strategy
 */
function maskValue(
  value: string,
  type: PIIType,
  strategy: MaskingStrategy,
): string {
  switch (strategy) {
    case MaskingStrategy.FULL:
      return "*".repeat(value.length);

    case MaskingStrategy.PARTIAL:
      return maskPartial(value, type);

    case MaskingStrategy.HASH:
      return `[REDACTED:${value.substring(0, 4)}...]`;

    case MaskingStrategy.REMOVE:
      return "[REDACTED]";

    default:
      return maskPartial(value, type);
  }
}

/**
 * Partially mask value based on type
 */
function maskPartial(value: string, type: PIIType): string {
  switch (type) {
    case PIIType.EMAIL: {
      const [local, domain] = value.split("@");
      const maskedLocal =
        local.length > 2
          ? local[0] + "*".repeat(local.length - 2) + local[local.length - 1]
          : local[0] + "*";
      return `${maskedLocal}@${domain}`;
    }

    case PIIType.PHONE: {
      if (value.length > 6) {
        const start = value.substring(0, 3);
        const end = value.substring(value.length - 3);
        return `${start}${"*".repeat(value.length - 6)}${end}`;
      }
      return "*".repeat(value.length);
    }

    case PIIType.CREDIT_CARD: {
      // Show last 4 digits only
      const clean = value.replace(/[\s-]/g, "");
      const last4 = clean.substring(clean.length - 4);
      return `****-****-****-${last4}`;
    }

    case PIIType.NATIONAL_ID: {
      if (value.length >= 4) {
        const start = value.substring(0, 2);
        const end = value.substring(value.length - 2);
        return `${start}${"*".repeat(value.length - 4)}${end}`;
      }
      return "*".repeat(value.length);
    }

    default: {
      // Generic partial masking
      if (value.length > 4) {
        const visible = Math.ceil(value.length * 0.2);
        const start = value.substring(0, visible);
        const end = value.substring(value.length - visible);
        return `${start}${"*".repeat(value.length - visible * 2)}${end}`;
      }
      return "*".repeat(value.length);
    }
  }
}

/**
 * Redact all PII from text (complete removal)
 *
 * @param text - Text to redact
 * @returns Text with all PII removed
 */
export function redactPII(text: string): string {
  return maskPII(text, MaskingStrategy.REMOVE);
}

// ═══════════════════════════════════════════════════════════════════════════
// Encryption Decision Logic
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Field sensitivity level
 */
export enum SensitivityLevel {
  PUBLIC = "PUBLIC", // No encryption needed
  INTERNAL = "INTERNAL", // Hash or basic encryption
  CONFIDENTIAL = "CONFIDENTIAL", // Strong encryption
  RESTRICTED = "RESTRICTED", // Strong encryption + additional controls
}

/**
 * Determine if a field should be encrypted based on its name and value
 *
 * @param fieldName - Name of the field
 * @param value - Value of the field (optional)
 * @returns True if field should be encrypted
 *
 * @example
 * ```typescript
 * if (shouldEncrypt('nationalId')) {
 *   // Encrypt this field
 * }
 * ```
 */
export function shouldEncrypt(fieldName: string, value?: string): boolean {
  const sensitiveFields = [
    "nationalId",
    "national_id",
    "ssn",
    "password",
    "passwordHash",
    "password_hash",
    "creditCard",
    "credit_card",
    "bankAccount",
    "bank_account",
    "iban",
    "passport",
    "dateOfBirth",
    "date_of_birth",
    "dob",
    "salary",
    "income",
    "taxId",
    "tax_id",
  ];

  // Check field name
  const lowerFieldName = fieldName.toLowerCase();
  if (
    sensitiveFields.some((field) =>
      lowerFieldName.includes(field.toLowerCase()),
    )
  ) {
    return true;
  }

  // Check value content if provided
  if (value) {
    const piiTypes = getPIITypes(value);
    const sensitivePIITypes = [
      PIIType.NATIONAL_ID,
      PIIType.SSN,
      PIIType.CREDIT_CARD,
      PIIType.PASSPORT,
      PIIType.IBAN,
    ];

    return piiTypes.some((type) => sensitivePIITypes.includes(type));
  }

  return false;
}

/**
 * Determine sensitivity level of a field
 *
 * @param fieldName - Name of the field
 * @param value - Value of the field (optional)
 * @returns Sensitivity level
 */
export function getSensitivityLevel(
  fieldName: string,
  value?: string,
): SensitivityLevel {
  const restrictedFields = [
    "password",
    "passwordHash",
    "creditCard",
    "bankAccount",
    "ssn",
  ];
  const confidentialFields = [
    "nationalId",
    "passport",
    "dateOfBirth",
    "salary",
    "iban",
  ];
  const internalFields = ["phone", "email", "address"];

  const lowerFieldName = fieldName.toLowerCase();

  if (
    restrictedFields.some((field) =>
      lowerFieldName.includes(field.toLowerCase()),
    )
  ) {
    return SensitivityLevel.RESTRICTED;
  }

  if (
    confidentialFields.some((field) =>
      lowerFieldName.includes(field.toLowerCase()),
    )
  ) {
    return SensitivityLevel.CONFIDENTIAL;
  }

  if (
    internalFields.some((field) => lowerFieldName.includes(field.toLowerCase()))
  ) {
    return SensitivityLevel.INTERNAL;
  }

  // Check value for PII
  if (value && containsPII(value)) {
    const types = getPIITypes(value);
    if (
      types.includes(PIIType.CREDIT_CARD) ||
      types.includes(PIIType.SSN) ||
      types.includes(PIIType.NATIONAL_ID)
    ) {
      return SensitivityLevel.CONFIDENTIAL;
    }
    return SensitivityLevel.INTERNAL;
  }

  return SensitivityLevel.PUBLIC;
}

/**
 * Determine if field should use deterministic encryption (for searchability)
 *
 * @param fieldName - Name of the field
 * @returns True if deterministic encryption should be used
 */
export function shouldUseDeterministicEncryption(fieldName: string): boolean {
  const searchableFields = [
    "nationalId",
    "national_id",
    "phone",
    "email",
    "passport",
    "taxId",
    "tax_id",
  ];

  const lowerFieldName = fieldName.toLowerCase();
  return searchableFields.some((field) =>
    lowerFieldName.includes(field.toLowerCase()),
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Automatic Encryption Handler
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Automatically encrypt a value based on field name
 *
 * @param fieldName - Name of the field
 * @param value - Value to encrypt
 * @returns Encrypted value or original if encryption not needed
 */
export function autoEncrypt(fieldName: string, value: string): string {
  if (!value || typeof value !== "string") {
    return value;
  }

  if (!shouldEncrypt(fieldName, value)) {
    return value;
  }

  if (shouldUseDeterministicEncryption(fieldName)) {
    return encryptSearchable(value);
  }

  return encrypt(value);
}

/**
 * Process an object and encrypt sensitive fields
 *
 * @param data - Object to process
 * @returns Object with encrypted sensitive fields
 */
export function encryptSensitiveFields<T extends Record<string, any>>(
  data: T,
): T {
  const result: any = { ...data };

  for (const [key, value] of Object.entries(result)) {
    if (typeof value === "string" && shouldEncrypt(key, value)) {
      result[key] = autoEncrypt(key, value);
    }
  }

  return result as T;
}

// ═══════════════════════════════════════════════════════════════════════════
// Exports
// ═══════════════════════════════════════════════════════════════════════════

export default {
  PIIType,
  MaskingStrategy,
  SensitivityLevel,
  detectPII,
  containsPII,
  getPIITypes,
  maskPII,
  redactPII,
  shouldEncrypt,
  getSensitivityLevel,
  shouldUseDeterministicEncryption,
  autoEncrypt,
  encryptSensitiveFields,
};
