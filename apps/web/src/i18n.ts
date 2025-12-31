/**
 * i18n Configuration for SAHOOL Web Application
 * Using next-intl with App Router
 */

import { getRequestConfig } from 'next-intl/server';
import { locales, defaultLocale, messages, type Locale } from '@sahool/i18n';

export default getRequestConfig(async ({ locale }) => {
  // Validate that the incoming locale parameter is valid
  const validLocale = (locales.includes(locale as Locale) ? locale : defaultLocale) as Locale;

  return {
    messages: messages[validLocale],
    timeZone: 'Asia/Aden',
    now: new Date(),
  };
});

export { locales, defaultLocale };
export type { Locale };
