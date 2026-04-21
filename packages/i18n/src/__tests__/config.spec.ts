/**
 * Tests for packages/i18n/src/config.ts
 *
 * Verifies next-intl v4 requestLocale handling:
 *   1. requestLocale is awaited (it is a Promise in v4)
 *   2. Fallback to defaultLocale for invalid/missing locales
 *   3. Returned config includes the resolved locale and messages
 */

import { vi, describe, it, expect, beforeAll } from 'vitest';
import { defaultLocale, locales } from '../index';

// Type matching the callback signature that getRequestConfig receives
type ConfigCallback = (ctx: {
  requestLocale: Promise<string | undefined>;
}) => Promise<{
  locale: string;
  messages: Record<string, unknown>;
  timeZone: string;
  now: Date;
}>;

let configCallback: ConfigCallback;

// Mock next-intl/server before config.ts is imported so we can capture the callback
vi.mock('next-intl/server', () => ({
  getRequestConfig: (cb: ConfigCallback) => {
    configCallback = cb;
    return cb;
  },
}));

// Mock locale JSON files that config.ts imports dynamically
vi.mock('../locales/ar.json', () => ({ default: { greeting: 'مرحبا', test: 'ar' } }));
vi.mock('../locales/en.json', () => ({ default: { greeting: 'Hello', test: 'en' } }));

beforeAll(async () => {
  // Importing config.ts triggers getRequestConfig, which sets configCallback via our mock
  await import('../config');
});

describe('i18n config.ts — next-intl v4 requestLocale handling', () => {
  it('awaits requestLocale (a Promise) to resolve the locale', async () => {
    // requestLocale is a Promise in next-intl v4; config.ts must await it
    const result = await configCallback({ requestLocale: Promise.resolve('en') });
    expect(result.locale).toBe('en');
  });

  it('falls back to defaultLocale when requestLocale resolves to an invalid locale', async () => {
    const result = await configCallback({ requestLocale: Promise.resolve('fr') });
    expect(result.locale).toBe(defaultLocale);
  });

  it('falls back to defaultLocale when requestLocale resolves to undefined', async () => {
    const result = await configCallback({ requestLocale: Promise.resolve(undefined) });
    expect(result.locale).toBe(defaultLocale);
  });

  it('returned config includes the resolved locale', async () => {
    const result = await configCallback({ requestLocale: Promise.resolve('ar') });
    expect(result.locale).toBe('ar');
  });

  it('returned config includes messages for the resolved locale', async () => {
    const result = await configCallback({ requestLocale: Promise.resolve('en') });
    expect(result.messages).toBeDefined();
    expect(typeof result.messages).toBe('object');
  });

  it('accepts all supported locales without falling back', async () => {
    for (const locale of locales) {
      const result = await configCallback({ requestLocale: Promise.resolve(locale) });
      expect(result.locale).toBe(locale);
    }
  });

  it('includes the Asia/Aden timeZone in the returned config', async () => {
    const result = await configCallback({ requestLocale: Promise.resolve(defaultLocale) });
    expect(result.timeZone).toBe('Asia/Aden');
  });

  it('includes a now Date in the returned config', async () => {
    const result = await configCallback({ requestLocale: Promise.resolve(defaultLocale) });
    expect(result.now).toBeInstanceOf(Date);
  });
});
