/**
 * SAHOOL Input Validation and Sanitization Utilities
 * Comprehensive security utilities for input validation and sanitization
 */

// ═══════════════════════════════════════════════════════════════════════════
// Validators
// ═══════════════════════════════════════════════════════════════════════════

export const validators = {
  /**
   * 2FA code: exactly 6 digits
   * @param code - The 2FA code to validate
   * @returns true if valid, false otherwise
   */
  twoFactorCode: (code: string): boolean => {
    if (!code || typeof code !== "string") return false;
    return /^\d{6}$/.test(code.trim());
  },

  /**
   * Email validation (RFC 5322 compliant)
   * @param email - The email address to validate
   * @returns true if valid, false otherwise
   */
  email: (email: string): boolean => {
    if (!email || typeof email !== "string") return false;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email.trim()) && email.length <= 254;
  },

  /**
   * Phone validation (international format)
   * @param phone - The phone number to validate
   * @returns true if valid, false otherwise
   */
  phone: (phone: string): boolean => {
    if (!phone || typeof phone !== "string") return false;
    return /^\+?[\d\s-]{10,}$/.test(phone.trim());
  },

  /**
   * Safe text (no HTML/script)
   * Checks for: HTML tags, dangerous protocols, event handlers, encoded attacks
   * @param text - The text to validate
   * @returns true if safe, false otherwise
   */
  safeText: (text: string): boolean => {
    if (!text || typeof text !== "string") return false;

    // Comprehensive pattern for detecting dangerous content
    const dangerousPatterns = [
      /<[^>]*>/i, // HTML tags
      /javascript\s*:/i, // javascript: protocol
      /vbscript\s*:/i, // vbscript: protocol
      /livescript\s*:/i, // livescript: protocol
      /data\s*:/i, // data: protocol
      /file\s*:/i, // file: protocol
      /blob\s*:/i, // blob: protocol
      /on\w+\s*=/i, // Event handlers (onclick, onerror, etc.)
      /expression\s*\(/i, // CSS expression
      /-moz-binding\s*:/i, // Firefox binding
      /behavior\s*:/i, // IE behavior
      /&#x?[0-9a-f]+;/i, // Numeric/hex HTML entities (potential encoding bypass)
      /&(lt|gt|amp|quot|apos|nbsp|tab|newline);/i, // Named HTML entities
      /%[0-9a-f]{2}/i, // URL encoding
      /\\x[0-9a-f]{2}/i, // Hex escapes
      /\\u[0-9a-f]{4}/i, // Unicode escapes
      /[\x00\u200B\u200C\u200D\uFEFF]/i, // Null bytes and zero-width chars
      /@import/i, // CSS import
      /xlink:href/i, // SVG xlink
      /srcdoc\s*=/i, // iframe srcdoc
      /formaction\s*=/i, // form hijacking
    ];

    return !dangerousPatterns.some((pattern) => pattern.test(text));
  },

  /**
   * URL validation
   * @param url - The URL to validate
   * @returns true if valid, false otherwise
   */
  url: (url: string): boolean => {
    if (!url || typeof url !== "string") return false;
    try {
      const urlObj = new URL(url);
      return urlObj.protocol === "http:" || urlObj.protocol === "https:";
    } catch {
      return false;
    }
  },

  /**
   * Password strength validation
   * Requires: min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
   * @param password - The password to validate
   * @returns true if strong enough, false otherwise
   */
  password: (password: string): boolean => {
    if (!password || typeof password !== "string") return false;
    const minLength = password.length >= 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(
      password,
    );
    return (
      minLength && hasUpperCase && hasLowerCase && hasNumber && hasSpecialChar
    );
  },

  /**
   * Numeric validation
   * @param value - The value to validate
   * @returns true if valid number, false otherwise
   */
  number: (value: string | number): boolean => {
    if (typeof value === "number") return !isNaN(value) && isFinite(value);
    if (typeof value === "string") return /^-?\d+\.?\d*$/.test(value.trim());
    return false;
  },

  /**
   * Alphanumeric validation (letters and numbers only)
   * @param value - The value to validate
   * @returns true if alphanumeric, false otherwise
   */
  alphanumeric: (value: string): boolean => {
    if (!value || typeof value !== "string") return false;
    return /^[a-zA-Z0-9]+$/.test(value);
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Sanitizers
// ═══════════════════════════════════════════════════════════════════════════

export const sanitizers = {
  /**
   * Remove all HTML tags and dangerous patterns
   * Security: Uses iterative approach to handle encoded/nested attacks
   * Covers: script tags, event handlers, dangerous protocols, data URIs,
   *         encoded entities, null bytes, unicode escapes, and more
   * @param input - The input string to sanitize
   * @returns Sanitized string
   */
  html: (input: string): string => {
    if (!input || typeof input !== "string") return "";

    let sanitized = input;

    // Iteratively decode and strip to handle nested/encoded HTML
    const MAX_ITERATIONS = 10;
    for (let i = 0; i < MAX_ITERATIONS; i++) {
      const before = sanitized;

      // Remove null bytes and zero-width characters (bypass attempts)
      sanitized = sanitized.replace(
        /[\x00\u200B\u200C\u200D\uFEFF\u00AD]/g,
        "",
      );

      // Remove backslash escapes that could bypass filters (e.g., \x6a for 'j')
      sanitized = sanitized.replace(
        /\\x[0-9a-fA-F]{2}/g,
        "",
      );

      // Remove unicode escapes (e.g., \u006A for 'j')
      sanitized = sanitized.replace(
        /\\u[0-9a-fA-F]{4}/g,
        "",
      );

      // Decode URL-encoded characters (%XX)
      try {
        // Only decode if it looks like URL encoding to avoid errors
        if (/%[0-9a-fA-F]{2}/.test(sanitized)) {
          sanitized = decodeURIComponent(sanitized);
        }
      } catch {
        // If decoding fails, remove % sequences to prevent bypass
        sanitized = sanitized.replace(/%[0-9a-fA-F]{2}/g, "");
      }

      // Decode HTML entities - standard named entities
      sanitized = sanitized
        .replace(/&lt;/gi, "<")
        .replace(/&gt;/gi, ">")
        .replace(/&amp;/gi, "&")
        .replace(/&quot;/gi, '"')
        .replace(/&apos;/gi, "'")
        .replace(/&#x27;/gi, "'")
        .replace(/&#x22;/gi, '"')
        .replace(/&#x3d;/gi, "=")
        .replace(/&nbsp;/gi, " ")
        .replace(/&tab;/gi, " ")
        .replace(/&newline;/gi, " ");

      // Decode numeric HTML entities (decimal) - with variable zero padding
      sanitized = sanitized.replace(/&#0*60;/gi, "<");
      sanitized = sanitized.replace(/&#0*62;/gi, ">");
      sanitized = sanitized.replace(/&#0*34;/gi, '"');
      sanitized = sanitized.replace(/&#0*39;/gi, "'");
      sanitized = sanitized.replace(/&#0*61;/gi, "=");
      sanitized = sanitized.replace(/&#0*58;/gi, ":"); // colon

      // Decode hex HTML entities - with variable zero padding and case insensitivity
      sanitized = sanitized.replace(/&#x0*3c;/gi, "<");
      sanitized = sanitized.replace(/&#x0*3e;/gi, ">");
      sanitized = sanitized.replace(/&#x0*22;/gi, '"');
      sanitized = sanitized.replace(/&#x0*27;/gi, "'");
      sanitized = sanitized.replace(/&#x0*3d;/gi, "=");
      sanitized = sanitized.replace(/&#x0*3a;/gi, ":"); // colon

      // Remove dangerous patterns in a loop to handle nested attacks
      // e.g., <!--<!--- --> becomes <!-- --> after one pass, or <scr<scriptipt> becomes <script>
      let previousValue: string;
      do {
        previousValue = sanitized;

        // Remove HTML comments (can hide malicious content)
        sanitized = sanitized.replace(/<!--[\s\S]*?-->/g, "");

        // Remove CDATA sections
        sanitized = sanitized.replace(/<!\[CDATA\[[\s\S]*?\]\]>/gi, "");

        // Remove all HTML tags (including self-closing, malformed, and SVG)
        sanitized = sanitized.replace(/<\/?[a-z][^>]*>/gi, "");
        sanitized = sanitized.replace(/<[a-z]/gi, ""); // Catch unclosed tags

        // Remove dangerous protocols (with flexible whitespace/newline/tab matching)
        // These patterns handle obfuscation like "java\tscript:" or "java\nscript:"
        sanitized = sanitized.replace(/j[\s\u0000]*a[\s\u0000]*v[\s\u0000]*a[\s\u0000]*s[\s\u0000]*c[\s\u0000]*r[\s\u0000]*i[\s\u0000]*p[\s\u0000]*t[\s\u0000]*:/gi, "");
        sanitized = sanitized.replace(/v[\s\u0000]*b[\s\u0000]*s[\s\u0000]*c[\s\u0000]*r[\s\u0000]*i[\s\u0000]*p[\s\u0000]*t[\s\u0000]*:/gi, "");
        sanitized = sanitized.replace(/l[\s\u0000]*i[\s\u0000]*v[\s\u0000]*e[\s\u0000]*s[\s\u0000]*c[\s\u0000]*r[\s\u0000]*i[\s\u0000]*p[\s\u0000]*t[\s\u0000]*:/gi, "");
        sanitized = sanitized.replace(/d[\s\u0000]*a[\s\u0000]*t[\s\u0000]*a[\s\u0000]*:/gi, "");
        sanitized = sanitized.replace(/f[\s\u0000]*i[\s\u0000]*l[\s\u0000]*e[\s\u0000]*:/gi, "");

        // Remove additional dangerous protocols
        sanitized = sanitized.replace(/blob\s*:/gi, "");
        sanitized = sanitized.replace(/about\s*:/gi, "");
        sanitized = sanitized.replace(/ws\s*:/gi, "");
        sanitized = sanitized.replace(/wss\s*:/gi, "");

        // Remove event handlers (comprehensive list)
        // Matches: onclick, onerror, onload, onmouseover, onfocus, onbegin, etc.
        // Handles spaces/tabs/newlines between 'on' and handler name
        sanitized = sanitized.replace(/on[\s\u0000]*[a-z]+[\s\u0000]*=/gi, "");
      } while (sanitized !== previousValue);

      // Remove CSS expression (IE-specific XSS)
      sanitized = sanitized.replace(/expression[\s\u0000]*\(/gi, "");

      // Remove CSS url() which can contain javascript:
      sanitized = sanitized.replace(/url[\s\u0000]*\(/gi, "");

      // Remove -moz-binding (Firefox-specific)
      sanitized = sanitized.replace(/-moz-binding[\s\u0000]*:/gi, "");

      // Remove behavior (IE-specific)
      sanitized = sanitized.replace(/behavior[\s\u0000]*:/gi, "");

      // Remove FSCommand (Flash)
      sanitized = sanitized.replace(/fscommand/gi, "");

      // Remove base64 in suspicious contexts
      sanitized = sanitized.replace(/base64[\s\u0000]*,/gi, "");

      // Remove @import (CSS injection)
      sanitized = sanitized.replace(/@import/gi, "");

      // Remove srcdoc attribute content
      sanitized = sanitized.replace(/srcdoc[\s\u0000]*=/gi, "");

      // Remove formaction (form hijacking)
      sanitized = sanitized.replace(/formaction[\s\u0000]*=/gi, "");

      // Remove xlink:href (SVG)
      sanitized = sanitized.replace(/xlink:href[\s\u0000]*=/gi, "");

      // Remove xmlns (namespace injection)
      sanitized = sanitized.replace(/xmlns[\s\u0000]*=/gi, "");

      // If no changes, we're done
      if (sanitized === before) {
        break;
      }
    }

    // Final safety: remove any remaining angle brackets
    sanitized = sanitized.replace(/[<>]/g, "");

    // Remove any remaining equals signs followed by quotes (attribute patterns)
    sanitized = sanitized.replace(/=\s*["']/g, "");

    return sanitized.trim();
  },

  /**
   * Escape for HTML display (prevents XSS)
   * @param input - The input string to escape
   * @returns Escaped string safe for HTML display
   */
  escape: (input: string): string => {
    if (!input || typeof input !== "string") return "";
    if (typeof window === "undefined") {
      // Server-side fallback
      return input
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#x27;")
        .replace(/\//g, "&#x2F;");
    }
    // Client-side using DOM
    const div = document.createElement("div");
    div.textContent = input;
    return div.innerHTML;
  },

  /**
   * Sanitize email address
   * @param email - The email to sanitize
   * @returns Sanitized email
   */
  email: (email: string): string => {
    if (!email || typeof email !== "string") return "";
    return email
      .toLowerCase()
      .trim()
      .replace(/[^\w\s@.+-]/g, ""); // Keep only valid email characters
  },

  /**
   * Sanitize phone number (keep only digits, +, -, and spaces)
   * @param phone - The phone number to sanitize
   * @returns Sanitized phone number
   */
  phone: (phone: string): string => {
    if (!phone || typeof phone !== "string") return "";
    return phone.replace(/[^\d+\s-]/g, "").trim();
  },

  /**
   * Sanitize numeric input
   * @param value - The value to sanitize
   * @returns Sanitized numeric string
   */
  number: (value: string): string => {
    if (!value || typeof value !== "string") return "";
    return value.replace(/[^\d.-]/g, "").trim();
  },

  /**
   * Sanitize alphanumeric input
   * @param value - The value to sanitize
   * @returns Sanitized alphanumeric string
   */
  alphanumeric: (value: string): string => {
    if (!value || typeof value !== "string") return "";
    return value.replace(/[^a-zA-Z0-9]/g, "").trim();
  },

  /**
   * Sanitize filename (remove path traversal and special chars)
   * @param filename - The filename to sanitize
   * @returns Safe filename
   */
  filename: (filename: string): string => {
    if (!filename || typeof filename !== "string") return "";
    return filename
      .replace(/\.\./g, "") // Remove path traversal
      .replace(/[^a-zA-Z0-9._-]/g, "_") // Replace special chars with underscore
      .slice(0, 255); // Limit length
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages (Arabic)
// ═══════════════════════════════════════════════════════════════════════════

export const validationErrors: Record<
  keyof typeof validators | "required" | "tooLong" | "tooShort",
  string
> = {
  twoFactorCode: "الرجاء إدخال رمز صحيح مكون من 6 أرقام",
  email: "الرجاء إدخال بريد إلكتروني صحيح",
  phone: "الرجاء إدخال رقم هاتف صحيح",
  safeText: "النص يحتوي على محتوى غير آمن",
  url: "الرجاء إدخال رابط صحيح",
  password:
    "كلمة المرور يجب أن تحتوي على 8 أحرف على الأقل، حرف كبير، حرف صغير، رقم، ورمز خاص",
  number: "الرجاء إدخال رقم صحيح",
  alphanumeric: "يجب أن يحتوي على أحرف وأرقام فقط",
  required: "هذا الحقل مطلوب",
  tooLong: "النص طويل جداً",
  tooShort: "النص قصير جداً",
};

// ═══════════════════════════════════════════════════════════════════════════
// Combined Validation Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Validate and sanitize input with error message
 * @param value - The value to validate
 * @param type - The validation type
 * @returns Object with isValid, sanitized value, and error message
 */
export function validateInput(
  value: string,
  type: keyof typeof validators,
): { isValid: boolean; value: string; error?: string } {
  if (!value) {
    return {
      isValid: false,
      value: "",
      error: validationErrors.required,
    };
  }

  const isValid = validators[type](value);
  const sanitizedValue =
    type in sanitizers
      ? sanitizers[type as keyof typeof sanitizers](value)
      : value;

  return {
    isValid,
    value: sanitizedValue,
    error: isValid ? undefined : validationErrors[type] || "إدخال غير صحيح",
  };
}

/**
 * Batch validate multiple inputs
 * @param inputs - Object with field names and values to validate
 * @param rules - Object with field names and validation types
 * @returns Object with validation results for each field
 */
export function validateForm(
  inputs: Record<string, string>,
  rules: Record<string, keyof typeof validators>,
): Record<string, { isValid: boolean; value: string; error?: string }> {
  const results: Record<
    string,
    { isValid: boolean; value: string; error?: string }
  > = {};

  // ES5-compatible iteration
  for (const field in inputs) {
    if (inputs.hasOwnProperty(field)) {
      const value = inputs[field];
      const rule = rules[field];
      if (rule) {
        results[field] = validateInput(value, rule);
      }
    }
  }

  return results;
}

/**
 * Check if all form fields are valid
 * @param validationResults - Results from validateForm
 * @returns true if all fields are valid
 */
export function isFormValid(
  validationResults: Record<
    string,
    { isValid: boolean; value: string; error?: string }
  >,
): boolean {
  // ES5-compatible iteration
  for (const field in validationResults) {
    if (validationResults.hasOwnProperty(field)) {
      if (!validationResults[field].isValid) {
        return false;
      }
    }
  }
  return true;
}
