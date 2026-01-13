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
 * Using multiple patterns to catch various bypass attempts
 */
const DANGEROUS_PROTOCOLS = /javascript\s*:|vbscript\s*:|data\s*:/gi;
// More comprehensive event handler patterns to prevent bypass
const EVENT_HANDLER_PATTERNS = [
  /\bon\w+\s*=/gi, // Standard: onclick=
  /\bon\s+\w+\s*=/gi, // With space: on click=
  /\bon[\s\S]*?=/gi, // With any chars: on/**/click=
  /\b(?:on(?:abort|blur|change|click|dblclick|error|focus|input|keydown|keypress|keyup|load|mousedown|mouseenter|mouseleave|mousemove|mouseout|mouseover|mouseup|reset|resize|scroll|select|submit|unload|wheel|copy|cut|paste|drag|dragend|dragenter|dragleave|dragover|dragstart|drop))\s*=/gi,
];
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

    // Remove event handlers using all patterns
    for (const pattern of EVENT_HANDLER_PATTERNS) {
      const freshPattern = new RegExp(pattern.source, pattern.flags);
      result = result.replace(freshPattern, "");
    }

    // Remove null bytes and other control characters
    result = result.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "");

    iterations++;
  }

  return result;
}

/**
 * Remove dangerous tag content entirely (script, style, etc.)
 * This removes both the tag and its contents
 * Note: Patterns handle optional whitespace before > to prevent bypass
 */
function removeDangerousTagContent(input: string): string {
  let result = input;
  let previous = "";
  let iterations = 0;

  // Dangerous tags whose content should be completely removed
  // Using \s* before > to handle variations like </script > or </script  >
  const DANGEROUS_TAGS = [
    /<script\b[^<]*(?:(?!<\/script\s*>)<[^<]*)*<\/script\s*>/gi,
    /<style\b[^<]*(?:(?!<\/style\s*>)<[^<]*)*<\/style\s*>/gi,
    /<noscript\b[^<]*(?:(?!<\/noscript\s*>)<[^<]*)*<\/noscript\s*>/gi,
    /<iframe\b[^<]*(?:(?!<\/iframe\s*>)<[^<]*)*<\/iframe\s*>/gi,
    /<object\b[^<]*(?:(?!<\/object\s*>)<[^<]*)*<\/object\s*>/gi,
    /<embed\b[^<]*(?:(?!<\/embed\s*>)<[^<]*)*<\/embed\s*>/gi,
    /<applet\b[^<]*(?:(?!<\/applet\s*>)<[^<]*)*<\/applet\s*>/gi,
  ];

  while (result !== previous && iterations < MAX_ITERATIONS) {
    previous = result;

    for (const pattern of DANGEROUS_TAGS) {
      const freshPattern = new RegExp(pattern.source, pattern.flags);
      result = result.replace(freshPattern, "");
    }

    // Also handle self-closing script tags (with optional whitespace)
    result = result.replace(/<script[^>]*\/\s*>/gi, "");

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

  // Step 1: Remove dangerous tag content FIRST (script, style, etc. with their contents)
  result = removeDangerousTagContent(result);

  // Step 2: Initial dangerous pattern removal
  result = removeDangerousPatterns(result);

  // Step 3: Decode HTML entities for checking
  const decodedForCheck = decodeHtmlEntities(result);

  // Step 4: Remove dangerous patterns from decoded content
  result = removeDangerousPatterns(decodedForCheck);

  // Step 5: Remove dangerous tag content again (after decoding might create new tags)
  result = removeDangerousTagContent(result);

  // Step 6: Remove HTML tags iteratively
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

  // Step 7: Final cleanup pass
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
  let hasDangerousPatterns =
    DANGEROUS_PROTOCOLS.test(text) || HTML_TAGS.test(text);

  // Reset regex lastIndex after test
  DANGEROUS_PROTOCOLS.lastIndex = 0;
  HTML_TAGS.lastIndex = 0;

  // Check all event handler patterns
  if (!hasDangerousPatterns) {
    for (const pattern of EVENT_HANDLER_PATTERNS) {
      const freshPattern = new RegExp(pattern.source, pattern.flags);
      if (freshPattern.test(text)) {
        hasDangerousPatterns = true;
        break;
      }
    }
  }

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
