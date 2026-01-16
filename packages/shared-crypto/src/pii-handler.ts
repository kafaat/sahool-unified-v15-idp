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
 * Regular expressions for PII detection
 */
const PII_PATTERNS: Record<PIIType, RegExp> = {
  // Saudi National ID: 1xxxxxxxxx (10 digits starting with 1 or 2)
  [PIIType.NATIONAL_ID]: /\b[12]\d{9}\b/g,

  // Phone numbers: Saudi format (05xxxxxxxx or +966xxxxxxxxx)
  // Also supports other formats: (555) 123-4567, 555-123-4567, etc.
  [PIIType.PHONE]:
    /(\+966|00966|05)\d{8,9}|\b\d{10}\b|(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g,

  // Email addresses
  [PIIType.EMAIL]: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,

  // Credit card numbers (basic pattern, 13-19 digits with optional spaces/dashes)
  [PIIType.CREDIT_CARD]: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4,7}\b/g,

  // SSN (US format: 123-45-6789)
  [PIIType.SSN]: /\b\d{3}-\d{2}-\d{4}\b/g,

  // Passport numbers (alphanumeric, typically 6-9 characters)
  [PIIType.PASSPORT]: /\b[A-Z]{1,2}\d{6,9}\b/g,

  // IBAN (International Bank Account Number)
  [PIIType.IBAN]: /\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b/g,

  // IP Address (IPv4)
  [PIIType.IP_ADDRESS]:
    /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g,

  // Date of Birth (various formats: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD)
  [PIIType.DATE_OF_BIRTH]:
    /\b(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-](19|20)\d\d\b|\b(19|20)\d\d[\/\-](0?[1-9]|1[012])[\/\-](0?[1-9]|[12][0-9]|3[01])\b/g,

  // Names are harder to detect with regex, this is a placeholder
  [PIIType.NAME]: /\b[A-Z][a-z]+ [A-Z][a-z]+\b/g,

  // Addresses (very basic pattern)
  [PIIType.ADDRESS]:
    /\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)/gi,
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
 * Calculate confidence score for PII detection
 */
function calculateConfidence(type: PIIType, value: string): number {
  // Basic confidence calculation
  // Could be enhanced with more sophisticated checks

  switch (type) {
    case PIIType.EMAIL:
      // Check for common email providers
      return value.includes("@gmail.com") ||
        value.includes("@yahoo.com") ||
        value.includes("@outlook.com")
        ? 0.95
        : 0.85;

    case PIIType.PHONE:
      // Saudi numbers starting with 05 or +966 are high confidence
      return value.startsWith("05") || value.startsWith("+966") ? 0.95 : 0.75;

    case PIIType.NATIONAL_ID:
      // Valid Saudi IDs start with 1 or 2
      return value.startsWith("1") || value.startsWith("2") ? 0.9 : 0.6;

    case PIIType.CREDIT_CARD:
      // Could add Luhn algorithm validation here
      return 0.8;

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
