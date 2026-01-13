/**
 * SAHOOL Safe Sanitizer
 * Provides safe HTML sanitization that works on both client and server
 *
 * Uses iterative regex-based sanitization to avoid jsdom issues with Next.js SSR
 * Implements defense-in-depth with multiple passes to prevent bypass attacks
 */

// Options type for sanitization
interface SanitizeOptions {
  ALLOWED_TAGS?: string[];
  ALLOWED_ATTR?: string[];
  KEEP_CONTENT?: boolean;
}

// Maximum iterations to prevent infinite loops
const MAX_ITERATIONS = 10;

/**
 * Dangerous patterns that need to be removed
 * Combined into regex for efficiency
 */
const DANGEROUS_PROTOCOLS = /javascript:|vbscript:|data:/gi;
const EVENT_HANDLERS = /on\w+\s*=/gi;
const HTML_TAGS = /<[^>]*>/g;

/**
 * Apply a replacement iteratively until the string stabilizes
 * This prevents bypass attacks where intermediate transformations create new attack vectors
 */
function iterativeReplace(
  input: string,
  pattern: RegExp,
  replacement: string
): string {
  let result = input;
  let previous = "";
  let iterations = 0;

  while (result !== previous && iterations < MAX_ITERATIONS) {
    previous = result;
    // Create a new RegExp to reset lastIndex for global patterns
    const freshPattern = new RegExp(pattern.source, pattern.flags);
    result = result.replace(freshPattern, replacement);
    iterations++;
  }

  return result;
}

/**
 * Decode HTML entities in the correct order
 * IMPORTANT: Decode &amp; LAST to prevent double-unescaping attacks
 * e.g., &amp;lt; should not become < (it should become &lt;)
 */
function decodeHtmlEntities(input: string): string {
  let result = input;

  // First pass: decode named entities (except &amp;)
  result = result
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"')
    .replace(/&#x27;/gi, "'")
    .replace(/&#39;/gi, "'")
    .replace(/&#x2F;/gi, "/")
    .replace(/&#47;/gi, "/");

  // Decode numeric entities
  result = result.replace(/&#(\d+);/g, (_, num) => {
    const code = parseInt(num, 10);
    // Only decode safe characters (printable ASCII, excluding < > & " ')
    if (code >= 32 && code <= 126 && ![60, 62, 38, 34, 39].includes(code)) {
      return String.fromCharCode(code);
    }
    return "";
  });

  result = result.replace(/&#x([0-9a-f]+);/gi, (_, hex) => {
    const code = parseInt(hex, 16);
    // Only decode safe characters
    if (code >= 32 && code <= 126 && ![60, 62, 38, 34, 39].includes(code)) {
      return String.fromCharCode(code);
    }
    return "";
  });

  // LAST: decode &amp; to prevent double-unescaping
  // Only decode &amp; that is NOT followed by another entity pattern
  result = result.replace(/&amp;(?![a-z]+;|#\d+;|#x[0-9a-f]+;)/gi, "&");

  return result;
}

/**
 * Remove all dangerous patterns iteratively
 * This ensures that patterns created by intermediate transformations are also removed
 */
function removeDangerousPatterns(input: string): string {
  let result = input;
  let previous = "";
  let iterations = 0;

  while (result !== previous && iterations < MAX_ITERATIONS) {
    previous = result;

    // Remove dangerous protocols
    result = result.replace(DANGEROUS_PROTOCOLS, "");

    // Remove event handlers
    result = result.replace(EVENT_HANDLERS, "");

    // Remove null bytes and other control characters
    result = result.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "");

    iterations++;
  }

  return result;
}

/**
 * Server-safe sanitizer using iterative regex
 * Implements defense-in-depth with multiple passes
 */
function regexSanitize(input: string, options?: SanitizeOptions): string {
  if (!input || typeof input !== "string") return "";

  let result = input;

  // Step 1: Initial dangerous pattern removal
  result = removeDangerousPatterns(result);

  // Step 2: Remove HTML tags iteratively
  if (!options?.ALLOWED_TAGS || options.ALLOWED_TAGS.length === 0) {
    result = iterativeReplace(result, HTML_TAGS, "");
  } else {
    // Remove tags not in allowed list
    const allowedTagsPattern = options.ALLOWED_TAGS.join("|");
    const disallowedTagRegex = new RegExp(
      `<(?!\\/?(${allowedTagsPattern})\\b)[^>]*>`,
      "gi"
    );
    result = iterativeReplace(result, disallowedTagRegex, "");
  }

  // Step 3: Decode HTML entities (with proper ordering)
  result = decodeHtmlEntities(result);

  // Step 4: Remove dangerous patterns again (after decoding)
  result = removeDangerousPatterns(result);

  // Step 5: Final HTML tag removal (after entity decoding)
  if (!options?.ALLOWED_TAGS || options.ALLOWED_TAGS.length === 0) {
    result = iterativeReplace(result, HTML_TAGS, "");
  }

  // Step 6: Final cleanup pass
  result = removeDangerousPatterns(result);

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

  // Check for dangerous patterns in original text
  const hasDangerousPatterns =
    DANGEROUS_PROTOCOLS.test(text) ||
    EVENT_HANDLERS.test(text) ||
    HTML_TAGS.test(text);

  // Reset regex lastIndex after test
  DANGEROUS_PROTOCOLS.lastIndex = 0;
  EVENT_HANDLERS.lastIndex = 0;
  HTML_TAGS.lastIndex = 0;

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
