/**
 * Lightweight HTML Sanitization Utility
 * SSR-safe alternative to isomorphic-dompurify for Next.js
 * 
 * This utility provides basic HTML sanitization without requiring DOM APIs,
 * making it safe to use in both server-side and client-side contexts.
 */

/**
 * Sanitize user input by removing HTML tags and control characters
 * @param input - The string to sanitize
 * @returns Sanitized string with HTML tags removed
 */
export function sanitizeInput(input: string): string {
    if (typeof input !== "string") return input;

    // Remove HTML tags using regex
    let sanitized = input.replace(/<[^>]*>/g, "");

    // Decode common HTML entities
    sanitized = sanitized
        .replace(/&lt;/g, "<")
        .replace(/&gt;/g, ">")
        .replace(/&amp;/g, "&")
        .replace(/&quot;/g, '"')
        .replace(/&#x27;/g, "'")
        .replace(/&#x2F;/g, "/");

    // Remove null bytes and control characters (except newlines and tabs)
    sanitized = sanitized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "");

    // Remove any script-like content
    sanitized = sanitized.replace(/javascript:/gi, "");
    sanitized = sanitized.replace(/on\w+\s*=/gi, "");

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

    if (allowedTags.length === 0) {
        // No tags allowed, strip everything
        return sanitizeInput(html);
    }

    // Build regex pattern for allowed tags
    const allowedPattern = allowedTags.join("|");
    const tagRegex = new RegExp(
        `<(?!\\/?(${allowedPattern})\\b)[^>]*>`,
        "gi"
    );

    // Remove disallowed tags
    let sanitized = html.replace(tagRegex, "");

    // Remove dangerous attributes from allowed tags
    sanitized = sanitized.replace(/\s+on\w+\s*=\s*["'][^"']*["']/gi, "");
    sanitized = sanitized.replace(/\s+javascript:\s*/gi, "");

    return sanitized.trim();
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
