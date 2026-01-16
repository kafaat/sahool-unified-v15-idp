/**
 * Input Sanitization Utilities
 * أدوات تنظيف المدخلات
 *
 * @module shared/validation
 * @description Utilities for sanitizing user inputs to prevent XSS and injection attacks
 */

import { Transform, TransformFnParams } from "class-transformer";
import DOMPurify from "isomorphic-dompurify";

// ═══════════════════════════════════════════════════════════════════════════
// HTML Sanitization
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Sanitization options for different contexts
 */
export interface SanitizationOptions {
  /**
   * Allow HTML tags (default: false)
   */
  allowHtml?: boolean;

  /**
   * Allowed HTML tags (when allowHtml is true)
   */
  allowedTags?: string[];

  /**
   * Allowed HTML attributes (when allowHtml is true)
   */
  allowedAttributes?: string[];

  /**
   * Strip all HTML tags (default: true)
   */
  stripHtml?: boolean;

  /**
   * Normalize whitespace (default: true)
   */
  normalizeWhitespace?: boolean;

  /**
   * Trim leading/trailing whitespace (default: true)
   */
  trim?: boolean;

  /**
   * Remove null bytes (default: true)
   */
  removeNullBytes?: boolean;

  /**
   * Remove control characters (default: true)
   */
  removeControlChars?: boolean;
}

/**
 * Default sanitization options
 */
const DEFAULT_SANITIZATION_OPTIONS: SanitizationOptions = {
  allowHtml: false,
  stripHtml: true,
  normalizeWhitespace: true,
  trim: true,
  removeNullBytes: true,
  removeControlChars: true,
};

/**
 * Sanitize HTML to prevent XSS attacks
 *
 * @param input - Input string to sanitize
 * @param options - Sanitization options
 * @returns Sanitized string
 */
export function sanitizeHtml(
  input: string,
  options: SanitizationOptions = {},
): string {
  if (typeof input !== "string") {
    return input;
  }

  const opts = { ...DEFAULT_SANITIZATION_OPTIONS, ...options };
  let sanitized = input;

  // Remove null bytes
  if (opts.removeNullBytes) {
    sanitized = sanitized.replace(/\x00/g, "");
  }

  // Remove control characters (except newline and tab)
  if (opts.removeControlChars) {
    sanitized = sanitized.replace(
      // eslint-disable-next-line no-control-regex
      /[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]/g,
      "",
    );
  }

  // Sanitize HTML
  if (opts.allowHtml && opts.allowedTags) {
    // Use DOMPurify with allowed tags
    const config = {
      ALLOWED_TAGS: opts.allowedTags,
      ALLOWED_ATTR: opts.allowedAttributes || [],
      KEEP_CONTENT: true,
    };
    sanitized = DOMPurify.sanitize(sanitized, config);
  } else if (opts.stripHtml) {
    // Strip all HTML tags
    sanitized = DOMPurify.sanitize(sanitized, { ALLOWED_TAGS: [] });
  }

  // Normalize whitespace
  if (opts.normalizeWhitespace) {
    sanitized = sanitized.replace(/\s+/g, " ");
  }

  // Trim
  if (opts.trim) {
    sanitized = sanitized.trim();
  }

  return sanitized;
}

/**
 * Sanitize text for rich text editors
 * Allows safe HTML tags like <p>, <b>, <i>, <ul>, <li>, etc.
 *
 * @param input - Input string to sanitize
 * @returns Sanitized HTML string
 */
export function sanitizeRichText(input: string): string {
  const allowedTags = [
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "blockquote",
    "pre",
    "code",
    "a",
  ];

  const allowedAttributes = ["href", "title", "target"];

  return sanitizeHtml(input, {
    allowHtml: true,
    allowedTags,
    allowedAttributes,
    stripHtml: false,
    normalizeWhitespace: false,
  });
}

/**
 * Sanitize plain text (strip all HTML, normalize whitespace)
 *
 * @param input - Input string to sanitize
 * @returns Sanitized plain text
 */
export function sanitizePlainText(input: string): string {
  return sanitizeHtml(input, {
    stripHtml: true,
    normalizeWhitespace: true,
    trim: true,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SQL Injection Prevention
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Escape SQL identifiers (table/column names)
 * Note: This is a backup measure. Always use parameterized queries!
 *
 * @param identifier - SQL identifier to escape
 * @returns Escaped identifier
 */
export function escapeSqlIdentifier(identifier: string): string {
  if (typeof identifier !== "string") {
    throw new Error("SQL identifier must be a string");
  }

  // Remove any existing quotes and escape special characters
  return `"${identifier.replace(/"/g, '""')}"`;
}

/**
 * Validate SQL identifier (table/column name)
 * Only allows alphanumeric characters and underscores
 *
 * @param identifier - SQL identifier to validate
 * @returns True if valid
 */
export function isValidSqlIdentifier(identifier: string): boolean {
  if (typeof identifier !== "string") {
    return false;
  }

  // Only allow alphanumeric and underscores, must start with letter
  return /^[a-zA-Z][a-zA-Z0-9_]*$/.test(identifier);
}

// ═══════════════════════════════════════════════════════════════════════════
// NoSQL Injection Prevention
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Sanitize MongoDB query operators
 * Removes any properties starting with $ to prevent NoSQL injection
 *
 * @param obj - Object to sanitize
 * @returns Sanitized object
 */
export function sanitizeMongoQuery(obj: any): any {
  if (typeof obj !== "object" || obj === null) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => sanitizeMongoQuery(item));
  }

  const sanitized: any = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      // Remove keys starting with $ (MongoDB operators)
      if (!key.startsWith("$")) {
        sanitized[key] = sanitizeMongoQuery(obj[key]);
      }
    }
  }

  return sanitized;
}

// ═══════════════════════════════════════════════════════════════════════════
// Prompt Injection Prevention (for AI/LLM inputs)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Detect common prompt injection patterns
 *
 * @param input - Input string to check
 * @returns True if prompt injection is detected
 */
export function detectPromptInjection(input: string): boolean {
  if (typeof input !== "string") {
    return false;
  }

  const injectionPatterns = [
    /ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)/i,
    /disregard\s+(all\s+)?(previous|above|prior)/i,
    /forget\s+(everything|all|what)/i,
    /new\s+instructions?:/i,
    /system\s*:/i,
    /you\s+are\s+now/i,
    /act\s+as/i,
    /pretend\s+(to\s+be|you\s+are)/i,
    /roleplay/i,
    /simulate/i,
    /output\s+in\s+code\s+block/i,
    /```.*system/is,
  ];

  return injectionPatterns.some((pattern) => pattern.test(input));
}

/**
 * Sanitize AI/LLM prompt input
 * Removes potential prompt injection attempts
 *
 * @param input - Input string to sanitize
 * @returns Sanitized string
 */
export function sanitizePromptInput(input: string): string {
  if (typeof input !== "string") {
    return input;
  }

  let sanitized = input;

  // Remove potential system/instruction markers
  sanitized = sanitized.replace(/system\s*:/gi, "");
  sanitized = sanitized.replace(/instructions?\s*:/gi, "");
  sanitized = sanitized.replace(/```[^`]*system[^`]*```/gis, "");

  // Remove excessive newlines (potential delimiter injection)
  sanitized = sanitized.replace(/\n{3,}/g, "\n\n");

  // Basic sanitization
  sanitized = sanitizePlainText(sanitized);

  return sanitized;
}

// ═══════════════════════════════════════════════════════════════════════════
// Path Traversal Prevention
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Sanitize file path to prevent directory traversal
 *
 * @param path - File path to sanitize
 * @returns Sanitized path (filename only)
 */
export function sanitizeFilePath(path: string): string {
  if (typeof path !== "string") {
    return "";
  }

  // Remove any path traversal attempts
  let sanitized = path.replace(/\.\./g, "");
  sanitized = sanitized.replace(/[/\\]/g, "");

  // Remove any null bytes
  sanitized = sanitized.replace(/\x00/g, "");

  // Only keep the filename
  const parts = sanitized.split(/[/\\]/);
  sanitized = parts[parts.length - 1];

  return sanitized;
}

/**
 * Validate file extension against whitelist
 *
 * @param filename - Filename to validate
 * @param allowedExtensions - Array of allowed extensions (e.g., ['jpg', 'png'])
 * @returns True if extension is allowed
 */
export function isAllowedFileExtension(
  filename: string,
  allowedExtensions: string[],
): boolean {
  if (typeof filename !== "string") {
    return false;
  }

  const extension = filename.split(".").pop()?.toLowerCase();
  if (!extension) {
    return false;
  }

  return allowedExtensions.map((ext) => ext.toLowerCase()).includes(extension);
}

// ═══════════════════════════════════════════════════════════════════════════
// Class Transformer Decorators
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Decorator to sanitize HTML in DTO properties
 * @param options - Sanitization options
 */
export function SanitizeHtml(options: SanitizationOptions = {}) {
  return Transform((params: TransformFnParams) => {
    if (typeof params.value !== "string") {
      return params.value;
    }
    return sanitizeHtml(params.value, options);
  });
}

/**
 * Decorator to sanitize plain text in DTO properties
 */
export function SanitizePlainText() {
  return Transform((params: TransformFnParams) => {
    if (typeof params.value !== "string") {
      return params.value;
    }
    return sanitizePlainText(params.value);
  });
}

/**
 * Decorator to sanitize rich text in DTO properties
 */
export function SanitizeRichText() {
  return Transform((params: TransformFnParams) => {
    if (typeof params.value !== "string") {
      return params.value;
    }
    return sanitizeRichText(params.value);
  });
}

/**
 * Decorator to sanitize file paths in DTO properties
 */
export function SanitizeFilePath() {
  return Transform((params: TransformFnParams) => {
    if (typeof params.value !== "string") {
      return params.value;
    }
    return sanitizeFilePath(params.value);
  });
}

/**
 * Decorator to sanitize AI prompt inputs in DTO properties
 */
export function SanitizePrompt() {
  return Transform((params: TransformFnParams) => {
    if (typeof params.value !== "string") {
      return params.value;
    }
    return sanitizePromptInput(params.value);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Export all sanitization utilities
// ═══════════════════════════════════════════════════════════════════════════

export const SANITIZATION_UTILITIES = {
  sanitizeHtml,
  sanitizeRichText,
  sanitizePlainText,
  escapeSqlIdentifier,
  isValidSqlIdentifier,
  sanitizeMongoQuery,
  detectPromptInjection,
  sanitizePromptInput,
  sanitizeFilePath,
  isAllowedFileExtension,
  SanitizeHtml,
  SanitizePlainText,
  SanitizeRichText,
  SanitizeFilePath,
  SanitizePrompt,
};
