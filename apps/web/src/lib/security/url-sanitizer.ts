/**
 * SAHOOL URL Sanitizer
 * التحقق من الروابط
 *
 * Validates and sanitizes URLs to prevent XSS attacks via javascript: and other dangerous protocols.
 * This is a critical security control for any user-controlled URLs.
 */

/**
 * List of dangerous protocols that can execute code
 */
const DANGEROUS_PROTOCOLS = [
  "javascript:",
  "vbscript:",
  "data:",
  "blob:",
  "file:",
] as const;

/**
 * List of allowed protocols for external URLs
 */
const ALLOWED_PROTOCOLS = ["http:", "https:"] as const;

/**
 * Sanitize a URL by validating it against dangerous protocols
 *
 * @param url - The URL to sanitize (can be undefined or null)
 * @returns The original URL if safe, or null if dangerous/invalid
 *
 * @example
 * // Safe URLs are returned as-is
 * sanitizeUrl('https://example.com') // => 'https://example.com'
 * sanitizeUrl('/dashboard') // => '/dashboard'
 *
 * // Dangerous URLs return null
 * sanitizeUrl('javascript:alert(1)') // => null
 * sanitizeUrl('data:text/html,...') // => null
 */
export function sanitizeUrl(url: string | undefined | null): string | null {
  // Handle empty/null/undefined values
  if (!url || typeof url !== "string") {
    return null;
  }

  // Trim and normalize whitespace
  const trimmed = url.trim();
  if (trimmed.length === 0) {
    return null;
  }

  // Normalize to lowercase for protocol checking
  // Note: We preserve the original URL for the return value
  const normalized = trimmed.toLowerCase();

  // Block dangerous protocols (check with various bypass attempts)
  // Attackers may try: "javascript:", "  javascript:", "JAVASCRIPT:", etc.
  for (const protocol of DANGEROUS_PROTOCOLS) {
    if (normalized.startsWith(protocol)) {
      return null;
    }
    // Also check for whitespace-prefixed protocols (bypass attempt)
    if (normalized.replace(/^\s+/, "").startsWith(protocol)) {
      return null;
    }
  }

  // Block URLs that contain embedded dangerous protocols after URL encoding
  // e.g., "https://evil.com/redirect?url=javascript:alert(1)"
  // This is a defense-in-depth check
  for (const protocol of DANGEROUS_PROTOCOLS) {
    if (
      normalized.includes(encodeURIComponent(protocol)) ||
      normalized.includes(protocol)
    ) {
      // Check if it's in a query parameter or fragment
      const queryIndex = normalized.indexOf("?");
      const fragmentIndex = normalized.indexOf("#");
      const startIndex = Math.min(
        queryIndex >= 0 ? queryIndex : normalized.length,
        fragmentIndex >= 0 ? fragmentIndex : normalized.length
      );

      // Only block if dangerous protocol appears after the path (in query/fragment)
      // This avoids false positives on legitimate URLs
      if (startIndex > 0 && normalized.indexOf(protocol, startIndex) >= 0) {
        return null;
      }
    }
  }

  // Allow relative URLs (starting with / or ./)
  if (trimmed.startsWith("/") || trimmed.startsWith("./")) {
    return trimmed;
  }

  // Allow protocol-relative URLs
  if (trimmed.startsWith("//")) {
    return trimmed;
  }

  // Allow mailto: and tel: protocols for common use cases
  if (normalized.startsWith("mailto:") || normalized.startsWith("tel:")) {
    return trimmed;
  }

  // Check for allowed protocols
  for (const protocol of ALLOWED_PROTOCOLS) {
    if (normalized.startsWith(protocol)) {
      return trimmed;
    }
  }

  // If no protocol specified and doesn't start with /, assume it's a relative path
  // but be cautious - if it looks like a protocol (contains :/), reject it
  if (trimmed.includes("://") || trimmed.includes(":")) {
    // Unknown protocol - block it
    return null;
  }

  // Plain relative path without leading slash (e.g., "page.html", "path/to/page")
  return trimmed;
}

/**
 * Check if a URL is safe without modifying it
 *
 * @param url - The URL to check
 * @returns true if the URL is safe, false otherwise
 */
export function isUrlSafe(url: string | undefined | null): boolean {
  return sanitizeUrl(url) !== null;
}

/**
 * Sanitize a URL for use in window.open() or similar navigation
 * Returns a safe default if the URL is dangerous
 *
 * @param url - The URL to sanitize
 * @param fallback - Optional fallback URL (default: null)
 * @returns The sanitized URL or the fallback
 */
export function sanitizeUrlForNavigation(
  url: string | undefined | null,
  fallback: string | null = null
): string | null {
  return sanitizeUrl(url) ?? fallback;
}

export default {
  sanitizeUrl,
  isUrlSafe,
  sanitizeUrlForNavigation,
};
