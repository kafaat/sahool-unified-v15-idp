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
   * @param text - The text to validate
   * @returns true if safe, false otherwise
   */
  safeText: (text: string): boolean => {
    if (!text || typeof text !== "string") return false;
    return !/<[^>]*>|javascript:|data:|on\w+=/i.test(text);
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
   * @param input - The input string to sanitize
   * @returns Sanitized string
   */
  html: (input: string): string => {
    if (!input || typeof input !== "string") return "";
    return input
      .replace(/<[^>]*>/g, "") // Remove HTML tags
      .replace(/javascript:/gi, "") // Remove javascript: protocol
      .replace(/on\w+=/gi, "") // Remove event handlers
      .replace(/data:/gi, "") // Remove data: protocol
      .replace(/vbscript:/gi, "") // Remove vbscript: protocol
      .replace(/file:/gi, "") // Remove file: protocol
      .trim();
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
