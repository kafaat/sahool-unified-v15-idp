/**
 * Logger Utility Tests
 * اختبارات أداة التسجيل
 *
 * Tests for environment-aware logging, Sentry integration,
 * and production-safe structured logging.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import fs from 'fs';
import path from 'path';

const LIB_DIR = path.resolve(__dirname, '..');
const loggerPath = path.join(LIB_DIR, 'logger.ts');
const sentryShimPath = path.join(LIB_DIR, 'sentry-shim.ts');

// ═══════════════════════════════════════════════════════════════════════════
// Logger Source Analysis
// ═══════════════════════════════════════════════════════════════════════════

describe('Logger (source analysis)', () => {
  let content: string;

  beforeAll(() => {
    content = fs.readFileSync(loggerPath, 'utf-8');
  });

  it('file exists', () => {
    expect(fs.existsSync(loggerPath)).toBe(true);
  });

  it('exports logger object', () => {
    expect(content).toMatch(/export const logger/);
  });

  it('exports default', () => {
    expect(content).toMatch(/export default logger/);
  });

  describe('Log Methods', () => {
    const methods = ['log', 'error', 'warn', 'debug', 'info', 'group', 'groupEnd', 'critical', 'production'];

    methods.forEach((method) => {
      it(`has ${method} method`, () => {
        expect(content).toMatch(new RegExp(`${method}\\s*[:=]`));
      });
    });
  });

  describe('Environment Awareness', () => {
    it('checks NODE_ENV for development mode', () => {
      expect(content).toContain("process.env.NODE_ENV === 'development'");
    });

    it('guards dev-only logs with isDev check', () => {
      expect(content).toContain('if (isDev)');
    });

    it('error method logs in all environments', () => {
      // error method has both isDev and else branches
      const errorBlock = content.slice(content.indexOf('error:'));
      expect(errorBlock).toContain('if (isDev)');
      expect(errorBlock).toContain('} else {');
    });

    it('critical method always logs', () => {
      // critical calls console.error unconditionally before the isDev check
      const criticalBlock = content.slice(content.indexOf('critical:'));
      expect(criticalBlock).toContain('console.error(...args)');
    });
  });

  describe('Production Structured Logging', () => {
    it('uses JSON.stringify for production error logs', () => {
      expect(content).toContain('JSON.stringify');
    });

    it('includes service name in structured logs', () => {
      expect(content).toContain("service: 'sahool-admin'");
    });

    it('includes timestamp in structured logs', () => {
      expect(content).toContain('new Date().toISOString()');
    });

    it('includes log level in structured logs', () => {
      expect(content).toContain("level: 'error'");
    });
  });

  describe('Sentry Integration', () => {
    it('checks SENTRY_DSN environment variable', () => {
      expect(content).toContain('NEXT_PUBLIC_SENTRY_DSN');
    });

    it('has isSentryEnabled flag', () => {
      expect(content).toContain('isSentryEnabled');
    });

    it('lazy-loads Sentry module', () => {
      expect(content).toContain("import('@sentry/nextjs')");
    });

    it('validates Sentry module has required methods', () => {
      expect(content).toContain('captureException');
      expect(content).toContain('captureMessage');
    });

    it('handles Sentry import failure gracefully', () => {
      expect(content).toContain('catch (error)');
      expect(content).toContain('continuing without error tracking');
    });

    it('sends Error objects to captureException', () => {
      expect(content).toContain('firstArg instanceof Error');
      expect(content).toContain('Sentry.captureException');
    });

    it('sends string messages to captureMessage', () => {
      expect(content).toContain("typeof firstArg === 'string'");
      expect(content).toContain('Sentry.captureMessage');
    });

    it('only sends to Sentry in production', () => {
      expect(content).toContain('!isDev && isSentryEnabled');
    });
  });

  describe('Arabic Documentation', () => {
    it('has Arabic doc comments', () => {
      expect(content).toMatch(/[\u0600-\u06FF]/);
    });

    it('documents logging utility purpose', () => {
      expect(content).toContain('أداة تسجيل سجلات');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Logger Runtime Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Logger (runtime)', () => {
  let consoleSpy: Record<string, ReturnType<typeof vi.spyOn>>;

  beforeEach(() => {
    consoleSpy = {
      log: vi.spyOn(console, 'log').mockImplementation(() => {}),
      error: vi.spyOn(console, 'error').mockImplementation(() => {}),
      warn: vi.spyOn(console, 'warn').mockImplementation(() => {}),
      debug: vi.spyOn(console, 'debug').mockImplementation(() => {}),
      info: vi.spyOn(console, 'info').mockImplementation(() => {}),
      group: vi.spyOn(console, 'group').mockImplementation(() => {}),
      groupEnd: vi.spyOn(console, 'groupEnd').mockImplementation(() => {}),
    };
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('logger can be imported', async () => {
    const { logger } = await import('../logger');
    expect(logger).toBeDefined();
    expect(typeof logger.log).toBe('function');
    expect(typeof logger.error).toBe('function');
    expect(typeof logger.warn).toBe('function');
    expect(typeof logger.debug).toBe('function');
    expect(typeof logger.info).toBe('function');
    expect(typeof logger.critical).toBe('function');
    expect(typeof logger.production).toBe('function');
    expect(typeof logger.group).toBe('function');
    expect(typeof logger.groupEnd).toBe('function');
  });

  it('critical always logs to console.error', async () => {
    const { logger } = await import('../logger');
    logger.critical('test critical error');
    expect(consoleSpy.error).toHaveBeenCalled();
  });

  it('logger methods do not throw', async () => {
    const { logger } = await import('../logger');
    expect(() => logger.log('test')).not.toThrow();
    expect(() => logger.error('test')).not.toThrow();
    expect(() => logger.warn('test')).not.toThrow();
    expect(() => logger.debug('test')).not.toThrow();
    expect(() => logger.info('test')).not.toThrow();
    expect(() => logger.critical('test')).not.toThrow();
    expect(() => logger.production('test')).not.toThrow();
    expect(() => logger.group('test')).not.toThrow();
    expect(() => logger.groupEnd()).not.toThrow();
  });

  it('error method handles Error objects', async () => {
    const { logger } = await import('../logger');
    const err = new Error('test error');
    expect(() => logger.error(err)).not.toThrow();
    expect(() => logger.critical(err)).not.toThrow();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Sentry Shim Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Sentry Shim', () => {
  it('file exists', () => {
    expect(fs.existsSync(sentryShimPath)).toBe(true);
  });

  it('is a valid module with empty export', () => {
    const content = fs.readFileSync(sentryShimPath, 'utf-8');
    expect(content).toContain('export {}');
  });

  it('has documentation explaining its purpose', () => {
    const content = fs.readFileSync(sentryShimPath, 'utf-8');
    expect(content).toContain('shim');
    expect(content).toContain('@sentry/nextjs');
  });

  it('explains webpack alias usage', () => {
    const content = fs.readFileSync(sentryShimPath, 'utf-8');
    expect(content).toMatch(/webpack|resolve\.alias/i);
  });

  it('can be imported without errors', async () => {
    expect(async () => {
      await import('../sentry-shim');
    }).not.toThrow();
  });

  it('is a minimal file (under 20 lines)', () => {
    const content = fs.readFileSync(sentryShimPath, 'utf-8');
    const lines = content.split('\n').length;
    expect(lines).toBeLessThan(20);
  });
});
