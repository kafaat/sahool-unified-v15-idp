/**
 * SAHOOL Safe Sanitizer
 * Provides safe HTML sanitization that works on both client and server
 *
 * Uses regex-based sanitization to avoid jsdom issues with Next.js SSR
 * This approach is simpler and more reliable for SSR environments
 */

// Options type for sanitization
interface SanitizeOptions {
  ALLOWED_TAGS?: string[];
  ALLOWED_ATTR?: string[];
  KEEP_CONTENT?: boolean;
}

/**
 * Server-safe sanitizer using regex
 * Strips HTML tags and dangerous patterns
 */
function regexSanitize(input: string, options?: SanitizeOptions): string {
  if (!input || typeof input !== "string") return "";

  let result = input;

  // If ALLOWED_TAGS is empty array or undefined, strip all tags
  if (!options?.ALLOWED_TAGS || options.ALLOWED_TAGS.length === 0) {
    // Remove all HTML tags but keep content
    result = result.replace(/<[^>]*>/g, "");
  } else {
    // Remove tags not in allowed list
    const allowedTagsPattern = options.ALLOWED_TAGS.join("|");
    const disallowedTagRegex = new RegExp(
      `<(?!\\/?(${allowedTagsPattern})\\b)[^>]*>`,
      "gi"
    );
    result = result.replace(disallowedTagRegex, "");
  }

  // Remove dangerous patterns
  result = result
    .replace(/javascript:/gi, "")
    .replace(/vbscript:/gi, "")
    .replace(/data:/gi, "")
    .replace(/on\w+\s*=/gi, "");

  // Decode HTML entities to prevent double-encoding attacks
  result = result
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#x27;/g, "'")
    .replace(/&#39;/g, "'");

  // Strip again after decoding (iterative sanitization)
  if (!options?.ALLOWED_TAGS || options.ALLOWED_TAGS.length === 0) {
    result = result.replace(/<[^>]*>/g, "");
  }

  // Remove any remaining dangerous patterns after decoding
  result = result
    .replace(/javascript:/gi, "")
    .replace(/vbscript:/gi, "")
    .replace(/on\w+\s*=/gi, "");

  return result.trim();
}

/**
 * Sanitize input string - removes HTML and dangerous patterns
 * Works on both client and server
 *
 * @param input - The input string to sanitize
 * @param options - Sanitization options
 * @returns Sanitized string
 */
export function sanitize(input: string, options?: SanitizeOptions): string {
  return regexSanitize(input, options);
}

/**
 * Check if input is safe (no HTML/script)
 *
 * @param text - The text to check
 * @returns true if safe, false otherwise
 */
export function isSafeText(text: string): boolean {
  if (!text || typeof text !== "string") return false;

  const sanitized = sanitize(text, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
  });

  const hasDangerousPatterns = /javascript:|data:|vbscript:|on\w+=/i.test(text);

  return sanitized === text && !hasDangerousPatterns;
}

/**
 * Initialize sanitizer (no-op for regex-based implementation)
 * Kept for API compatibility
 */
export async function initSanitizer(): Promise<void> {
  // No initialization needed for regex-based sanitizer
}

// Export a default object for compatibility
const SafeDOMPurify = {
  sanitize,
  isSafeText,
  initSanitizer,
};

export default SafeDOMPurify;
