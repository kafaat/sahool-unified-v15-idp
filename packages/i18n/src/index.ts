/**
 * SAHOOL i18n Package
 * Internationalization utilities for the SAHOOL platform
 */

// Re-export locale files
import arMessages from './locales/ar.json';
import enMessages from './locales/en.json';

export const messages = {
  ar: arMessages,
  en: enMessages,
} as const;

export type Locale = keyof typeof messages;
export type Messages = typeof arMessages;

export const locales: Locale[] = ['ar', 'en'];
export const defaultLocale: Locale = 'ar';

/**
 * Get messages for a specific locale
 */
export function getMessages(locale: Locale): Messages {
  return messages[locale] || messages[defaultLocale];
}

/**
 * Get locale display name
 */
export function getLocaleDisplayName(locale: Locale): string {
  const names: Record<Locale, string> = {
    ar: 'العربية',
    en: 'English',
  };
  return names[locale];
}

/**
 * Check if locale is RTL
 */
export function isRTL(locale: Locale): boolean {
  return locale === 'ar';
}

/**
 * Get text direction for locale
 */
export function getDirection(locale: Locale): 'rtl' | 'ltr' {
  return isRTL(locale) ? 'rtl' : 'ltr';
}

// Re-export next-intl utilities for convenience
export {
  useTranslations,
  useLocale,
  useMessages,
  useNow,
  useTimeZone,
  useFormatter,
  NextIntlClientProvider,
} from 'next-intl';

export type { AbstractIntlMessages } from 'next-intl';
