/**
 * i18n Configuration for Next.js App Router
 */

import { getRequestConfig } from 'next-intl/server';
import { locales, defaultLocale, type Locale } from './index';

export default getRequestConfig(async ({ requestLocale }) => {
  // In next-intl v4, use requestLocale (a Promise) instead of the deprecated locale param
  const requested = await requestLocale;
  const validLocale = requested && locales.includes(requested as Locale) ? requested : defaultLocale;

  return {
    locale: validLocale,
    messages: (await import(`./locales/${validLocale}.json`)).default,
    timeZone: 'Asia/Aden',
    now: new Date(),
  };
});

export { locales, defaultLocale };
export type { Locale };
