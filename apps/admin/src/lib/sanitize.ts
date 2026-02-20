/**
 * HTML Sanitization Utility
 * Uses isomorphic-dompurify for robust, SSR-safe HTML sanitization.
 *
 * This replaces hand-rolled regex sanitization which was flagged by CodeQL
 * for incomplete multi-character sanitization (e.g. partial <script tags
 * surviving regex-based stripping).
 */

import DOMPurify from "isomorphic-dompurify";

/**
 * Sanitize user input by removing ALL HTML tags and control characters.
 * Returns plain text safe for display.
 * @param input - The string to sanitize
 * @returns Sanitized plain text string with all HTML removed
 */
export function sanitizeInput(input: string): string {
    if (typeof input !== "string") return input;

    // Remove null bytes and control characters (except newlines and tabs)
    // eslint-disable-next-line no-control-regex -- Intentional: sanitizing dangerous control characters
    let sanitized = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "");

    // Use DOMPurify with no allowed tags/attributes to strip all HTML.
    // This properly handles incomplete tags, encoded entities, and nested markup
    // that regex-based stripping cannot reliably catch.
    sanitized = DOMPurify.sanitize(sanitized, {
        ALLOWED_TAGS: [],
        ALLOWED_ATTR: [],
    });

    return sanitized.trim();
}

/**
 * Sanitize HTML content with allowed tags
 * @param html - The HTML string to sanitize
 * @param allowedTags - Array of allowed HTML tags (default: none)
 * @returns Sanitized HTML string
 */
export function sanitizeHtml(
    html: string,
    allowedTags: string[] = []
): string {
    if (typeof html !== "string") return html;

    // DOMPurify handles tag allowlisting, attribute stripping, and all
    // edge cases (incomplete tags, encoded payloads, event handlers, etc.)
    return DOMPurify.sanitize(html, {
        ALLOWED_TAGS: allowedTags,
        ALLOWED_ATTR: [],
    }).trim();
}

/**
 * Validate and sanitize email address
 * @param email - Email address to validate
 * @returns Sanitized email or null if invalid
 */
export function sanitizeEmail(email: string): string | null {
    if (typeof email !== "string") return null;

    const sanitized = sanitizeInput(email);
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return emailRegex.test(sanitized) ? sanitized : null;
}

/**
 * Sanitize URL to prevent XSS via javascript: or data: protocols
 * @param url - URL to sanitize
 * @returns Sanitized URL or null if dangerous
 */
export function sanitizeUrl(url: string): string | null {
    if (typeof url !== "string") return null;

    const sanitized = sanitizeInput(url).trim();

    // Block dangerous protocols
    const dangerousProtocols = /^(javascript|data|vbscript|file):/i;
    if (dangerousProtocols.test(sanitized)) {
        return null;
    }

    // Allow only http, https, mailto, tel
    const safeProtocols = /^(https?|mailto|tel):/i;
    if (!safeProtocols.test(sanitized) && !sanitized.startsWith("/")) {
        return null;
    }

    return sanitized;
}
