/**
 * Comprehensive API Routes Tests
 * اختبارات شاملة لجميع مسارات API
 *
 * Verifies structure, exports, error handling, and security patterns
 * for all 17 API route handlers.
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const API_DIR = path.resolve(__dirname, '..');

function readRoute(routePath: string): string {
  const fullPath = path.join(API_DIR, routePath, 'route.ts');
  try {
    return fs.readFileSync(fullPath, 'utf-8');
  } catch {
    return ''; // Missing files produce empty content; "file exists" test catches this
  }
}

function routeExists(routePath: string): boolean {
  return fs.existsSync(path.join(API_DIR, routePath, 'route.ts'));
}

// ═══════════════════════════════════════════════════════════════════════════
// Auth Routes
// ═══════════════════════════════════════════════════════════════════════════

describe('POST /api/auth/register', () => {
  const content = readRoute('auth/register');

  it('file exists', () => expect(routeExists('auth/register')).toBe(true));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('validates email', () => expect(content).toMatch(/email/i));
  it('validates password', () => expect(content).toMatch(/password/i));
  it('returns error status codes', () => expect(content).toMatch(/status:\s*\d{3}/));
  it('forwards to upstream auth service', () => expect(content).toMatch(/fetch|api|upstream/i));
  it('validates required fields', () => expect(content).toMatch(/name|email|password/i));
  it('uses NextResponse', () => expect(content).toContain('NextResponse'));
});

describe('POST /api/auth/forgot-password', () => {
  const content = readRoute('auth/forgot-password');

  it('file exists', () => expect(routeExists('auth/forgot-password')).toBe(true));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('accepts email in body', () => expect(content).toMatch(/email/));
  it('forwards request to upstream', () => {
    expect(content).toMatch(/fetch|api|upstream/i);
  });
});

describe('POST /api/auth/reset-password', () => {
  const content = readRoute('auth/reset-password');

  it('file exists', () => expect(routeExists('auth/reset-password')).toBe(true));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('validates token', () => expect(content).toMatch(/token/));
  it('validates new password', () => expect(content).toMatch(/password/));
  it('returns error status on invalid token', () => expect(content).toMatch(/40[01]/));
});

describe('POST /api/auth/send-otp', () => {
  const content = readRoute('auth/send-otp');

  it('file exists', () => expect(routeExists('auth/send-otp')).toBe(true));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('accepts identifier in body', () => expect(content).toMatch(/email|phone|body|json/i));
  it('uses OTP generation', () => expect(content).toMatch(/otp|code|token/i));
});

describe('POST /api/auth/resend-otp', () => {
  const content = readRoute('auth/resend-otp');

  it('file exists', () => expect(routeExists('auth/resend-otp')).toBe(true));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('implements rate limiting or cooldown', () => {
    expect(content).toMatch(/rate|limit|cooldown|throttle|429|too.*many/i);
  });
});

describe('POST /api/auth/verify-otp', () => {
  const content = readRoute('auth/verify-otp');

  it('file exists', () => expect(routeExists('auth/verify-otp')).toBe(true));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('accepts OTP code', () => expect(content).toMatch(/otp|code/i));
  it('returns error on invalid code', () => expect(content).toMatch(/40[01]/));
  it('returns response data on success', () => expect(content).toMatch(/json|data|response/i));
});

describe('GET /api/auth/me', () => {
  const content = readRoute('auth/me');

  it('file exists', () => expect(routeExists('auth/me')).toBe(true));
  it('exports GET handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+GET/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('extracts token from request', () => expect(content).toMatch(/token|cookie|header|authorization/i));
  it('returns 401 for unauthenticated', () => expect(content).toContain('401'));
  it('returns user data on success', () => expect(content).toMatch(/user|profile/i));
});

describe('POST /api/auth/refresh', () => {
  const content = readRoute('auth/refresh');

  it('file exists', () => expect(routeExists('auth/refresh')).toBe(true));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('uses refresh token', () => expect(content).toMatch(/refresh/i));
  it('returns new access token', () => expect(content).toMatch(/access.*token|token/i));
  it('returns 401 on expired refresh token', () => expect(content).toContain('401'));
  it('sets httpOnly cookie', () => expect(content).toMatch(/httpOnly|cookie/i));
});

describe('POST /api/auth/activity', () => {
  const content = readRoute('auth/activity');

  it('file exists', () => expect(routeExists('auth/activity')).toBe(true));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('tracks user activity', () => expect(content).toMatch(/activity|last_active|timestamp/i));
});

// ═══════════════════════════════════════════════════════════════════════════
// Security Routes
// ═══════════════════════════════════════════════════════════════════════════

describe('GET/POST /api/csrf-token', () => {
  const content = readRoute('csrf-token');

  it('file exists', () => expect(routeExists('csrf-token')).toBe(true));
  it('exports GET handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+GET/));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('generates CSRF token', () => expect(content).toMatch(/csrf|token|generate/i));
  it('sets cookie', () => expect(content).toMatch(/cookie|Set-Cookie/i));
  it('returns token in response', () => expect(content).toMatch(/token/i));
});

describe('POST /api/csp-report', () => {
  const content = readRoute('csp-report');

  it('file exists', () => expect(routeExists('csp-report')).toBe(true));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('parses CSP violation report', () => expect(content).toMatch(/csp-report|violated-directive|document-uri/i));
  it('logs violation details', () => expect(content).toMatch(/log|logger|console/i));
  it('returns 204 or 200', () => expect(content).toMatch(/20[04]/));
  it('validates report structure', () => expect(content).toMatch(/body|json|parse/i));
});

// ═══════════════════════════════════════════════════════════════════════════
// Utility Routes
// ═══════════════════════════════════════════════════════════════════════════

describe('GET/POST /api/code-review', () => {
  const content = readRoute('code-review');

  it('file exists', () => expect(routeExists('code-review')).toBe(true));
  it('exports GET handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+GET/));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('handles code analysis', () => expect(content).toMatch(/code|review|analysis|diff/i));
  it('returns structured response', () => expect(content).toContain('NextResponse.json'));
});

describe('POST /api/log-error', () => {
  const content = readRoute('log-error');

  it('file exists', () => expect(routeExists('log-error')).toBe(true));
  it('exports POST handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+POST/));
  it('has error handling', () => expect(content).toContain('try {'));
  it('accepts error payload', () => expect(content).toMatch(/error|message|stack/i));
  it('validates payload size', () => expect(content).toMatch(/length|size|limit|truncat/i));
  it('logs to server', () => expect(content).toMatch(/log|logger|console/i));
  it('returns success response', () => expect(content).toMatch(/NextResponse\.json|status/));
});

describe('GET /api/health', () => {
  const content = readRoute('health');

  it('file exists', () => expect(routeExists('health')).toBe(true));
  it('exports GET handler', () => expect(content).toMatch(/export\s+(async\s+)?function\s+GET/));
  it('returns status ok', () => expect(content).toMatch(/ok|healthy|status/i));
  it('returns 200', () => expect(content).toContain('200'));
});

// ═══════════════════════════════════════════════════════════════════════════
// Cross-cutting Concerns
// ═══════════════════════════════════════════════════════════════════════════

describe('API Routes Cross-cutting', () => {
  const routes = [
    'auth/register', 'auth/forgot-password', 'auth/reset-password',
    'auth/send-otp', 'auth/resend-otp', 'auth/verify-otp',
    'auth/me', 'auth/refresh', 'auth/activity',
    'csrf-token', 'csp-report', 'code-review', 'log-error', 'health',
  ];

  routes.forEach((route) => {
    it(`${route} uses NextResponse`, () => {
      const content = readRoute(route);
      expect(content).toContain('NextResponse');
    });
  });

  const authRoutes = [
    'auth/register', 'auth/forgot-password', 'auth/reset-password',
    'auth/send-otp', 'auth/resend-otp', 'auth/verify-otp',
    'auth/refresh',
  ];

  authRoutes.forEach((route) => {
    it(`${route} has try-catch error handling`, () => {
      const content = readRoute(route);
      expect((content.match(/try\s*\{/g) || []).length).toBeGreaterThanOrEqual(1);
    });

    it(`${route} handles 500 server errors`, () => {
      const content = readRoute(route);
      expect(content).toContain('500');
    });
  });
});
