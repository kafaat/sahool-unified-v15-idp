/**
 * URL Validation Utilities for Open Redirect Prevention
 * أدوات التحقق من صحة الروابط لمنع إعادة التوجيه المفتوح
 *
 * Prevents open redirect attacks by validating returnTo URLs
 * يمنع هجمات إعادة التوجيه المفتوح عن طريق التحقق من صحة روابط العودة
 */

/**
 * Whitelist of safe internal routes that can be used for returnTo redirects
 * قائمة المسارات الداخلية الآمنة التي يمكن استخدامها لإعادة التوجيه
 */
export const SAFE_RETURN_TO_ROUTES = [
  "/dashboard",
  "/analytics",
  "/farms",
  "/settings",
  "/fields",
  "/diseases",
  "/epidemic",
  "/irrigation",
  "/sensors",
  "/yield",
  "/alerts",
  "/lab",
  "/precision-agriculture",
  "/support",
] as const;

/**
 * Default redirect path when returnTo is invalid or missing
 */
export const DEFAULT_RETURN_PATH = "/dashboard";

/**
 * Validates a returnTo URL to prevent open redirect attacks
 *
 * Security checks:
 * 1. Must be a non-empty string
 * 2. Must start with a single forward slash (relative path)
 * 3. Must not contain protocol indicators (//)
 * 4. Must not contain URL-encoded sequences that could bypass checks
 * 5. Path must match or start with a whitelisted route
 *
 * @param url - The returnTo URL to validate
 * @returns true if the URL is safe to redirect to
 */
export function isValidReturnTo(url: string | null | undefined): boolean {
  // Must be a non-empty string
  if (!url || typeof url !== "string") {
    return false;
  }

  // Must start with exactly one forward slash (relative path)
  if (!url.startsWith("/")) {
    return false;
  }

  // Must not contain protocol indicators (prevents //evil.com)
  if (url.includes("//")) {
    return false;
  }

  // Must not contain backslashes (prevents \evil.com on some browsers)
  if (url.includes("\\")) {
    return false;
  }

  // Check for URL-encoded bypass attempts
  const decodedUrl = decodeURIComponent(url);
  if (decodedUrl.includes("//") || decodedUrl.includes("\\")) {
    return false;
  }

  // Parse the URL to extract just the pathname
  try {
    const parsed = new URL(url, "http://localhost");

    // Ensure the pathname matches the original url (no host manipulation)
    // This catches cases like /\evil.com or /@evil.com
    if (parsed.pathname !== url.split("?")[0].split("#")[0]) {
      // Allow query params and hash, but pathname must match
      const urlPathOnly = url.split("?")[0].split("#")[0];
      if (parsed.pathname !== urlPathOnly) {
        return false;
      }
    }

    // Check if the path starts with a whitelisted route
    const pathOnly = parsed.pathname;
    const isWhitelisted = SAFE_RETURN_TO_ROUTES.some(
      (route) => pathOnly === route || pathOnly.startsWith(`${route}/`),
    );

    return isWhitelisted;
  } catch {
    // If URL parsing fails, reject it
    return false;
  }
}

/**
 * Sanitizes a returnTo URL, returning a safe default if invalid
 *
 * @param url - The returnTo URL to sanitize
 * @returns A safe URL to redirect to
 */
export function sanitizeReturnTo(url: string | null | undefined): string {
  if (isValidReturnTo(url)) {
    return url as string;
  }
  return DEFAULT_RETURN_PATH;
}
