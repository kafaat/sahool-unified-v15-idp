/**
 * Logger Tests
 * Tests for the SAHOOL logging utility
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock environment variables before importing logger
const originalEnv = process.env;

beforeEach(() => {
  vi.resetModules();
  process.env = { ...originalEnv };
  vi.clearAllMocks();
});

afterEach(() => {
  process.env = originalEnv;
});

describe('Logger', () => {
  describe('Development Mode', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'development';
    });

    it('should log messages in development mode', async () => {
      const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      const { logger } = await import('../logger');

      logger.log('test message');

      expect(consoleLogSpy).toHaveBeenCalledWith('test message');
      consoleLogSpy.mockRestore();
    });

    it('should log errors in development mode', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { logger } = await import('../logger');

      logger.error('test error');

      expect(consoleErrorSpy).toHaveBeenCalledWith('test error');
      consoleErrorSpy.mockRestore();
    });

    it('should log warnings in development mode', async () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const { logger } = await import('../logger');

      logger.warn('test warning');

      expect(consoleWarnSpy).toHaveBeenCalledWith('test warning');
      consoleWarnSpy.mockRestore();
    });
  });

  describe('Production Mode', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'production';
      process.env.NEXT_PUBLIC_SENTRY_DSN = ''; // No Sentry DSN
    });

    it('should not log regular messages in production mode', async () => {
      const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      const { logger } = await import('../logger');

      logger.log('test message');

      expect(consoleLogSpy).not.toHaveBeenCalled();
      consoleLogSpy.mockRestore();
    });

    it('should log critical errors in production mode', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { logger } = await import('../logger');

      logger.critical('critical error');

      expect(consoleErrorSpy).toHaveBeenCalledWith('critical error');
      consoleErrorSpy.mockRestore();
    });

    it('should handle critical errors without Sentry when DSN is not configured', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      process.env.NEXT_PUBLIC_SENTRY_DSN = ''; // Explicitly no DSN
      const { logger } = await import('../logger');

      // Should not throw even without Sentry
      expect(() => {
        logger.critical('critical error');
      }).not.toThrow();

      expect(consoleErrorSpy).toHaveBeenCalledWith('critical error');
      consoleErrorSpy.mockRestore();
    });

    it('should handle Error objects in critical logging', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { logger } = await import('../logger');

      const testError = new Error('test error');
      logger.critical(testError);

      expect(consoleErrorSpy).toHaveBeenCalledWith(testError);
      consoleErrorSpy.mockRestore();
    });

    it('should handle multiple arguments in critical logging', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const { logger } = await import('../logger');

      logger.critical('error message', { detail: 'extra' }, 'more info');

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'error message',
        { detail: 'extra' },
        'more info'
      );
      consoleErrorSpy.mockRestore();
    });
  });

  describe('Type Safety', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'development';
    });

    it('should accept unknown[] types instead of any[]', async () => {
      const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      const { logger } = await import('../logger');

      // These should all work with unknown[] type
      logger.log('string');
      logger.log(123);
      logger.log({ key: 'value' });
      logger.log(null);
      logger.log(undefined);
      logger.log(['array']);

      expect(consoleLogSpy).toHaveBeenCalledTimes(6);
      consoleLogSpy.mockRestore();
    });
  });

  describe('Sentry Integration', () => {
    it('should not load Sentry when DSN is empty', async () => {
      process.env.NODE_ENV = 'production';
      process.env.NEXT_PUBLIC_SENTRY_DSN = '';

      const { logger } = await import('../logger');
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      // Should not attempt to load Sentry
      logger.critical('test error');

      // Just verify it doesn't throw
      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });

    it('should handle Sentry loading gracefully when configured', async () => {
      process.env.NODE_ENV = 'production';
      process.env.NEXT_PUBLIC_SENTRY_DSN = 'https://test@sentry.io/123';

      const { logger } = await import('../logger');
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      // Even with DSN configured, should not throw if Sentry fails to load
      expect(() => {
        logger.critical('test error');
      }).not.toThrow();

      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });
  });
});
