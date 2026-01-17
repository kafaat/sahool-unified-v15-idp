/**
 * SAHOOL CSP Nonce Utilities
 * أدوات nonce لـ CSP
 *
 * Utilities for working with CSP nonces in React components
 * أدوات للعمل مع nonces في مكونات React
 */

import { headers } from "next/headers";
import { logger } from "@/lib/logger";

// ═══════════════════════════════════════════════════════════════════════════
// Server-side Nonce Retrieval
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get the current CSP nonce from headers (server-side only)
 * الحصول على nonce الحالي من headers (من جانب الخادم فقط)
 *
 * Usage in Server Components:
 * const nonce = await getNonce();
 */
export async function getNonce(): Promise<string | null> {
  try {
    const headersList = await headers();
    return headersList.get("x-nonce");
  } catch {
    // Headers not available (e.g., in static generation)
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Nonce Props for Components
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get nonce props for script tags
 * الحصول على خصائص nonce لوسوم script
 *
 * Usage:
 * <script {...getNonceProps(nonce)}>...</script>
 */
export function getNonceProps(nonce: string | null): { nonce?: string } {
  if (!nonce) return {};
  return { nonce };
}

/**
 * Get nonce style attribute
 * الحصول على خاصية nonce للأنماط
 *
 * Usage:
 * <style {...getStyleNonceProps(nonce)}>...</style>
 */
export function getStyleNonceProps(nonce: string | null): { nonce?: string } {
  if (!nonce) return {};
  return { nonce };
}

// ═══════════════════════════════════════════════════════════════════════════
// CSP-Safe Inline Styles
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create CSP-safe inline styles using CSS variables
 * إنشاء أنماط مضمنة آمنة لـ CSP باستخدام متغيرات CSS
 *
 * Instead of inline styles, use CSS custom properties:
 *
 * Bad (blocked by CSP):
 * <div style={{ color: 'red' }}>...</div>
 *
 * Good (CSP-safe):
 * <div className="custom-color" style={cssVars({ '--color': 'red' })}>
 *   <style {...getStyleNonceProps(nonce)}>{`.custom-color { color: var(--color); }`}</style>
 * </div>
 */
export function cssVars(vars: Record<string, string>): Record<string, string> {
  return vars;
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if code is running on server
 * التحقق مما إذا كان الكود يعمل على الخادم
 */
export function isServer(): boolean {
  return typeof window === "undefined";
}

// ═══════════════════════════════════════════════════════════════════════════
// Script Validation & Security
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Dangerous patterns that should not appear in inline scripts
 * أنماط خطيرة يجب ألا تظهر في السكريبتات المضمنة
 */
const DANGEROUS_PATTERNS = [
  // Direct code execution
  /\beval\s*\(/gi,
  /\bFunction\s*\(/gi,
  /\bnew\s+Function\s*\(/gi,

  // Script injection attempts
  /<script[\s>]/gi,
  /<\/script>/gi,
  /javascript:/gi,

  // DOM manipulation that could execute code
  /\.innerHTML\s*=/gi,
  /\.outerHTML\s*=/gi,
  /document\.write\s*\(/gi,
  /document\.writeln\s*\(/gi,

  // Potential XSS vectors - Event handlers like onclick=, onerror=, etc.
  // Must start with word boundary to avoid matching "CONFIG=" etc.
  /\bon[a-z]+\s*=/gi,
  /<iframe[\s>]/gi,
  /<embed[\s>]/gi,
  /<object[\s>]/gi,

  // Data URIs and imports that could be dangerous
  /data:text\/html/gi,
  /import\s*\(/gi, // Dynamic imports could load untrusted code
];

/**
 * Patterns that are suspicious but might be legitimate
 * أنماط مشبوهة لكن قد تكون شرعية
 */
const SUSPICIOUS_PATTERNS = [
  /localStorage/gi,
  /sessionStorage/gi,
  /document\.cookie/gi,
  /window\.location/gi,
  /fetch\s*\(/gi,
  /XMLHttpRequest/gi,
  /\.postMessage\s*\(/gi,
];

/**
 * Validation result for inline script code
 * نتيجة التحقق من كود السكريبت المضمن
 */
interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

/**
 * Validate inline script code for security issues
 * التحقق من كود السكريبت المضمن بحثًا عن مشاكل أمنية
 *
 * @param code - The script code to validate
 * @returns Validation result with errors and warnings
 *
 * @example
 * ```typescript
 * const result = validateScriptCode('logger.log("hello")');
 * if (!result.isValid) {
 *   throw new Error(`Invalid script: ${result.errors.join(', ')}`);
 * }
 * ```
 */
export function validateScriptCode(code: string): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Check for empty or invalid input
  if (!code || typeof code !== "string") {
    errors.push("Script code must be a non-empty string");
    return { isValid: false, errors, warnings };
  }

  // Check for dangerous patterns
  for (const pattern of DANGEROUS_PATTERNS) {
    const match = code.match(pattern);
    if (match) {
      errors.push(
        `Dangerous pattern detected: "${match[0]}" - This could lead to code injection or XSS vulnerabilities`,
      );
    }
  }

  // Check for suspicious patterns
  for (const pattern of SUSPICIOUS_PATTERNS) {
    const match = code.match(pattern);
    if (match) {
      warnings.push(
        `Suspicious pattern detected: "${match[0]}" - Ensure this is intentional and from a trusted source`,
      );
    }
  }

  // Check for potential template injection
  if (code.includes("${") || code.includes("`")) {
    warnings.push(
      "Template literals detected - Ensure no user input is interpolated into this code",
    );
  }

  // Log warnings in development
  if (warnings.length > 0 && process.env.NODE_ENV !== "production") {
    logger.warn(
      "[Security Warning] Inline script validation warnings:",
      warnings,
    );
  }

  // Log errors
  if (errors.length > 0) {
    logger.error("[Security Error] Inline script validation failed:", errors);
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Sanitize script code by removing potentially dangerous content
 * تنظيف كود السكريبت من خلال إزالة المحتوى الخطير المحتمل
 *
 * @param code - The script code to sanitize
 * @returns Sanitized code with dangerous patterns removed
 *
 * @internal This is a basic sanitizer and should not be relied upon as the sole security measure
 */
function sanitizeScriptCode(code: string): string {
  let sanitized = code;

  // Remove HTML tags that might be injected
  sanitized = sanitized.replace(/<script[\s\S]*?<\/script>/gi, "");
  sanitized = sanitized.replace(/<iframe[\s\S]*?<\/iframe>/gi, "");
  sanitized = sanitized.replace(/<embed[\s\S]*?>/gi, "");
  sanitized = sanitized.replace(/<object[\s\S]*?<\/object>/gi, "");

  // Remove javascript: protocol
  sanitized = sanitized.replace(/javascript:/gi, "");

  // Remove data: URIs
  sanitized = sanitized.replace(/data:text\/html[^"'\s]*/gi, "");

  return sanitized;
}

/**
 * Safe way to add inline script with nonce and security validation
 * طريقة آمنة لإضافة script مضمن مع nonce والتحقق الأمني
 *
 * @param code - The JavaScript code to execute. MUST be from a trusted source only.
 * @param nonce - The CSP nonce from the server
 * @param options - Optional configuration
 * @param options.skipValidation - Skip validation (NOT RECOMMENDED - use only for trusted, static code)
 * @param options.allowSanitization - Attempt to sanitize code before validation
 *
 * @returns Props object with nonce and dangerouslySetInnerHTML
 *
 * @throws {Error} If code contains dangerous patterns and validation is not skipped
 *
 * @security
 * ⚠️ SECURITY WARNING ⚠️
 * - ONLY use this function with static, hardcoded JavaScript from trusted sources
 * - NEVER pass user input or dynamic content from untrusted sources
 * - This function uses dangerouslySetInnerHTML which can lead to XSS vulnerabilities
 * - The validation is a defense-in-depth measure but is NOT foolproof
 * - Always prefer external script files over inline scripts when possible
 *
 * @example
 * ```typescript
 * // ✅ SAFE: Static, trusted code
 * const nonce = await getNonce();
 * <script {...createInlineScript('logger.log("App initialized")', nonce)} />
 *
 * // ❌ UNSAFE: User input (NEVER DO THIS)
 * const userCode = req.body.code; // From user
 * <script {...createInlineScript(userCode, nonce)} /> // DANGEROUS!
 *
 * // ❌ UNSAFE: Dynamic untrusted content
 * const dynamicCode = await fetch(untrustedUrl).then(r => r.text());
 * <script {...createInlineScript(dynamicCode, nonce)} /> // DANGEROUS!
 * ```
 *
 * Usage in Server Components:
 * ```typescript
 * const nonce = await getNonce();
 * <script {...createInlineScript('window.__APP_CONFIG__ = {...}', nonce)} />
 * ```
 */
export function createInlineScript(
  code: string,
  nonce: string | null,
  options?: {
    skipValidation?: boolean;
    allowSanitization?: boolean;
  },
) {
  // Apply sanitization if requested
  const codeToValidate = options?.allowSanitization
    ? sanitizeScriptCode(code)
    : code;

  // Validate unless explicitly skipped
  if (!options?.skipValidation) {
    const validation = validateScriptCode(codeToValidate);

    if (!validation.isValid) {
      const errorMessage = `[Security] Inline script validation failed:\n${validation.errors.join("\n")}`;

      // In production, we should fail closed (reject the script)
      if (process.env.NODE_ENV === "production") {
        throw new Error(errorMessage);
      }

      // In development, log the error but allow it (for debugging)
      logger.error(errorMessage);
      logger.error("Script code:", code);
    }
  }

  return {
    ...getNonceProps(nonce),
    dangerouslySetInnerHTML: { __html: codeToValidate },
  };
}

/**
 * Safe way to add inline style with nonce
 * طريقة آمنة لإضافة style مضمن مع nonce
 *
 * Usage in Server Components:
 * const nonce = await getNonce();
 * <style {...createInlineStyle(css, nonce)} />
 */
export function createInlineStyle(css: string, nonce: string | null) {
  return {
    ...getStyleNonceProps(nonce),
    dangerouslySetInnerHTML: { __html: css },
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Export
// ═══════════════════════════════════════════════════════════════════════════

export const Nonce = {
  get: getNonce,
  getProps: getNonceProps,
  getStyleProps: getStyleNonceProps,
  cssVars,
  isServer,
  createInlineScript,
  createInlineStyle,
  validateScriptCode,
};

export default Nonce;
