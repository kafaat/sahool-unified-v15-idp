/**
 * CSRF Tests
 * اختبارات حماية CSRF
 */

import { describe, it, expect } from 'vitest';
import {
  CSRF_CONFIG,
  generateCsrfToken,
  createCsrfTokenPayload,
  hashToken,
  validateCsrfToken,
  extractCsrfTokenFromHeaders,
  extractCsrfTokenFromFormData,
  parseCsrfTokenPayload,
  serializeCsrfTokenPayload,
  requiresCsrfValidation,
  getCsrfCookieOptions,
} from '../csrf';

describe('CSRF Protection', () => {
  describe('CSRF_CONFIG', () => {
    it('has correct configuration values', () => {
      expect(CSRF_CONFIG.TOKEN_LENGTH).toBe(32);
      expect(CSRF_CONFIG.TOKEN_EXPIRATION).toBe(60 * 60 * 1000);
      expect(CSRF_CONFIG.COOKIE_NAME).toBe('sahool_csrf_token');
      expect(CSRF_CONFIG.HEADER_NAME).toBe('X-CSRF-Token');
      expect(CSRF_CONFIG.FIELD_NAME).toBe('_csrf');
    });
  });

  describe('generateCsrfToken', () => {
    it('generates a non-empty string token', () => {
      const token = generateCsrfToken();
      expect(token).toBeTruthy();
      expect(typeof token).toBe('string');
      expect(token.length).toBeGreaterThan(0);
    });

    it('generates unique tokens', () => {
      const token1 = generateCsrfToken();
      const token2 = generateCsrfToken();
      expect(token1).not.toBe(token2);
    });
  });

  describe('createCsrfTokenPayload', () => {
    it('creates payload with token and timestamps', () => {
      const payload = createCsrfTokenPayload();

      expect(payload.token).toBeTruthy();
      expect(payload.createdAt).toBeGreaterThan(0);
      expect(payload.expiresAt).toBeGreaterThan(payload.createdAt);
      expect(payload.expiresAt - payload.createdAt).toBe(CSRF_CONFIG.TOKEN_EXPIRATION);
    });
  });

  describe('hashToken', () => {
    it('returns consistent hash for same input', () => {
      const hash1 = hashToken('test-token');
      const hash2 = hashToken('test-token');
      expect(hash1).toBe(hash2);
    });

    it('returns different hashes for different inputs', () => {
      const hash1 = hashToken('token-1');
      const hash2 = hashToken('token-2');
      expect(hash1).not.toBe(hash2);
    });
  });

  describe('validateCsrfToken', () => {
    it('validates matching token', () => {
      const payload = createCsrfTokenPayload();
      const result = validateCsrfToken(payload.token, payload);

      expect(result.valid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('rejects mismatched token', () => {
      const payload = createCsrfTokenPayload();
      const result = validateCsrfToken('wrong-token-with-matching-length!!!', payload);

      expect(result.valid).toBe(false);
    });

    it('rejects when no stored payload', () => {
      const result = validateCsrfToken('some-token', null);

      expect(result.valid).toBe(false);
      expect(result.error).toContain('No CSRF token found');
    });

    it('rejects expired token', () => {
      const payload = createCsrfTokenPayload();
      // Manually expire it
      payload.expiresAt = Date.now() - 1000;

      const result = validateCsrfToken(payload.token, payload);

      expect(result.valid).toBe(false);
      expect(result.error).toContain('expired');
    });

    it('rejects empty provided token', () => {
      const payload = createCsrfTokenPayload();
      const result = validateCsrfToken('', payload);

      expect(result.valid).toBe(false);
      expect(result.error).toContain('No CSRF token provided');
    });

    it('rejects token with different length', () => {
      const payload = createCsrfTokenPayload();
      const result = validateCsrfToken('short', payload);

      expect(result.valid).toBe(false);
    });
  });

  describe('extractCsrfTokenFromHeaders', () => {
    it('extracts token from headers', () => {
      const headers = new Headers();
      headers.set('X-CSRF-Token', 'my-token');

      expect(extractCsrfTokenFromHeaders(headers)).toBe('my-token');
    });

    it('returns null when header not present', () => {
      const headers = new Headers();
      expect(extractCsrfTokenFromHeaders(headers)).toBeNull();
    });
  });

  describe('extractCsrfTokenFromFormData', () => {
    it('extracts token from form data', () => {
      const formData = new FormData();
      formData.set('_csrf', 'form-token');

      expect(extractCsrfTokenFromFormData(formData)).toBe('form-token');
    });

    it('returns null when field not present', () => {
      const formData = new FormData();
      expect(extractCsrfTokenFromFormData(formData)).toBeNull();
    });
  });

  describe('parseCsrfTokenPayload', () => {
    it('parses valid JSON payload', () => {
      const payload = createCsrfTokenPayload();
      const json = JSON.stringify(payload);

      const parsed = parseCsrfTokenPayload(json);
      expect(parsed).toEqual(payload);
    });

    it('returns null for undefined input', () => {
      expect(parseCsrfTokenPayload(undefined)).toBeNull();
    });

    it('returns null for invalid JSON', () => {
      expect(parseCsrfTokenPayload('not-json')).toBeNull();
    });

    it('returns null for JSON missing required fields', () => {
      expect(parseCsrfTokenPayload(JSON.stringify({ foo: 'bar' }))).toBeNull();
    });
  });

  describe('serializeCsrfTokenPayload', () => {
    it('serializes payload to JSON string', () => {
      const payload = createCsrfTokenPayload();
      const serialized = serializeCsrfTokenPayload(payload);

      expect(JSON.parse(serialized)).toEqual(payload);
    });
  });

  describe('requiresCsrfValidation', () => {
    it('returns true for unsafe methods', () => {
      expect(requiresCsrfValidation('POST')).toBe(true);
      expect(requiresCsrfValidation('PUT')).toBe(true);
      expect(requiresCsrfValidation('DELETE')).toBe(true);
      expect(requiresCsrfValidation('PATCH')).toBe(true);
    });

    it('returns false for safe methods', () => {
      expect(requiresCsrfValidation('GET')).toBe(false);
      expect(requiresCsrfValidation('HEAD')).toBe(false);
      expect(requiresCsrfValidation('OPTIONS')).toBe(false);
    });

    it('is case-insensitive', () => {
      expect(requiresCsrfValidation('post')).toBe(true);
      expect(requiresCsrfValidation('get')).toBe(false);
    });
  });

  describe('getCsrfCookieOptions', () => {
    it('returns correct cookie options', () => {
      const options = getCsrfCookieOptions();

      expect(options.httpOnly).toBe(false);
      expect(options.sameSite).toBe('strict');
      expect(options.path).toBe('/');
      expect(options.maxAge).toBe(CSRF_CONFIG.TOKEN_EXPIRATION / 1000);
    });
  });
});
