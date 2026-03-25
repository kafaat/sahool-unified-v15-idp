/**
 * HTML Sanitization Utility
 * Uses the xss library for robust, SSR-safe HTML sanitization.
 *
 * xss is a pure-JavaScript library with no native dependencies (unlike
 * isomorphic-dompurify which requires jsdom). This avoids CI build failures
 * caused by --ignore-scripts skipping jsdom's postinstall hooks.
 *
 * Replaces hand-rolled regex sanitization which was flagged by CodeQL for
 * incomplete multi-character sanitization (partial tags like <script without
 * closing > surviving regex-based stripping).
 */

import xss, { type IFilterXSSOptions } from 'xss';

// Plain-text mode: strip ALL tags and attributes, returning only text content
const PLAIN_TEXT_OPTIONS: IFilterXSSOptions = {
  whiteList: {}, // No tags allowed
  stripIgnoreTag: true, // Strip tags not in whitelist (all of them)
  stripIgnoreTagBody: ['script', 'style', 'noscript'], // Also strip body of these
};

/**
 * Sanitize user input by removing ALL HTML tags and control characters.
 * Returns plain text safe for display.
 * @param input - The string to sanitize
 * @returns Sanitized plain text string with all HTML removed
 */
export function sanitizeInput(input: string): string {
  if (typeof input !== 'string') return input;

  // Remove null bytes and control characters (except newlines and tabs)
  // eslint-disable-next-line no-control-regex -- Intentional: sanitizing dangerous control characters
  let sanitized = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');

  // Use xss library to strip all HTML tags and dangerous content.
  // Properly handles incomplete tags, encoded entities, event handlers,
  // and nested markup that regex cannot reliably catch.
  sanitized = xss(sanitized, PLAIN_TEXT_OPTIONS);

  return sanitized.trim();
}

/**
 * Sanitize HTML content with allowed tags
 * @param html - The HTML string to sanitize
 * @param allowedTags - Array of allowed HTML tags (default: none)
 * @returns Sanitized HTML string
 */
export function sanitizeHtml(html: string, allowedTags: string[] = []): string {
  if (typeof html !== 'string') return html;

  if (allowedTags.length === 0) {
    return sanitizeInput(html);
  }

  // Build whitelist object for xss library: { tagName: [] } (no attributes)
  const whiteList: Record<string, string[]> = {};
  for (const tag of allowedTags) {
    whiteList[tag] = [];
  }

  return xss(html, {
    whiteList,
    stripIgnoreTag: true,
    stripIgnoreTagBody: ['script', 'style', 'noscript'],
  }).trim();
}

/**
 * Validate and sanitize email address
 * @param email - Email address to validate
 * @returns Sanitized email or null if invalid
 */
export function sanitizeEmail(email: string): string | null {
  if (typeof email !== 'string') return null;

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
  if (typeof url !== 'string') return null;

  const sanitized = sanitizeInput(url).trim();

  // Block dangerous protocols
  const dangerousProtocols = /^(javascript|data|vbscript|file):/i;
  if (dangerousProtocols.test(sanitized)) {
    return null;
  }

  // Allow only http, https, mailto, tel
  const safeProtocols = /^(https?|mailto|tel):/i;
  if (!safeProtocols.test(sanitized) && !sanitized.startsWith('/')) {
    return null;
  }

  return sanitized;
}
