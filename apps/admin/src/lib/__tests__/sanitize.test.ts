/**
 * Sanitize Tests
 * اختبارات التنظيف
 */

import { describe, it, expect } from 'vitest';
import { sanitizeInput, sanitizeHtml, sanitizeEmail, sanitizeUrl } from '../sanitize';

describe('sanitizeInput', () => {
  it('strips all HTML tags', () => {
    expect(sanitizeInput('<b>bold</b>')).not.toContain('<b>');
    expect(sanitizeInput('<b>bold</b>')).toContain('bold');
  });

  it('strips script tags and their content', () => {
    const result = sanitizeInput('<script>alert("xss")</script>Hello');
    expect(result).not.toContain('script');
    expect(result).toContain('Hello');
  });

  it('strips style tags and their content', () => {
    const result = sanitizeInput('<style>body{display:none}</style>Content');
    expect(result).toContain('Content');
    expect(result).not.toContain('style');
  });

  it('removes null bytes and control characters', () => {
    const result = sanitizeInput('Hello\x00World\x01!');
    expect(result).not.toContain('\x00');
    expect(result).not.toContain('\x01');
  });

  it('preserves normal text', () => {
    expect(sanitizeInput('Hello World')).toBe('Hello World');
    expect(sanitizeInput('مرحبا بالعالم')).toBe('مرحبا بالعالم');
  });

  it('handles non-string input gracefully', () => {
    expect(sanitizeInput(123 as unknown as string)).toBe(123);
    expect(sanitizeInput(null as unknown as string)).toBe(null);
  });

  it('trims whitespace', () => {
    expect(sanitizeInput('  hello  ')).toBe('hello');
  });
});

describe('sanitizeHtml', () => {
  it('strips all tags with no allowlist', () => {
    const result = sanitizeHtml('<p>Hello <b>World</b></p>');
    expect(result).not.toContain('<p>');
    expect(result).not.toContain('<b>');
  });

  it('allows specified tags', () => {
    const result = sanitizeHtml('<p>Hello <b>World</b></p>', ['p']);
    expect(result).toContain('<p>');
    expect(result).not.toContain('<b>');
  });

  it('strips script tags even when other tags are allowed', () => {
    const result = sanitizeHtml('<p>Hello</p><script>alert(1)</script>', ['p']);
    expect(result).not.toContain('script');
  });
});

describe('sanitizeEmail', () => {
  it('returns sanitized valid email', () => {
    expect(sanitizeEmail('Admin@Sahool.IO')).toBe('Admin@Sahool.IO');
  });

  it('returns null for invalid email', () => {
    expect(sanitizeEmail('not-an-email')).toBeNull();
    expect(sanitizeEmail('')).toBeNull();
  });

  it('returns null for non-string', () => {
    expect(sanitizeEmail(123 as unknown as string)).toBeNull();
  });

  it('strips HTML from email', () => {
    const result = sanitizeEmail('<script>x</script>admin@sahool.io');
    // After sanitization, should still be a valid email or null
    if (result) {
      expect(result).not.toContain('<script>');
    }
  });
});

describe('sanitizeUrl', () => {
  it('allows safe URLs', () => {
    expect(sanitizeUrl('https://sahool.io')).toBe('https://sahool.io');
    expect(sanitizeUrl('http://localhost:3000')).toBe('http://localhost:3000');
  });

  it('allows relative paths', () => {
    expect(sanitizeUrl('/dashboard')).toBe('/dashboard');
    expect(sanitizeUrl('/api/health')).toBe('/api/health');
  });

  it('blocks javascript: protocol', () => {
    expect(sanitizeUrl('javascript:alert(1)')).toBeNull();
  });

  it('blocks data: protocol', () => {
    expect(sanitizeUrl('data:text/html,<h1>Hello</h1>')).toBeNull();
  });

  it('blocks vbscript: protocol', () => {
    expect(sanitizeUrl('vbscript:msgbox')).toBeNull();
  });

  it('blocks file: protocol', () => {
    expect(sanitizeUrl('file:///etc/passwd')).toBeNull();
  });

  it('returns null for non-string input', () => {
    expect(sanitizeUrl(123 as unknown as string)).toBeNull();
  });

  it('rejects ftp and other protocols', () => {
    expect(sanitizeUrl('ftp://files.com')).toBeNull();
  });

  it('allows mailto and tel', () => {
    expect(sanitizeUrl('mailto:admin@sahool.io')).toBe('mailto:admin@sahool.io');
    expect(sanitizeUrl('tel:+967123456')).toBe('tel:+967123456');
  });
});
