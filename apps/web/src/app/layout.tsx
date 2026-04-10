import type { Metadata } from 'next';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, getLocale } from 'next-intl/server';
import './globals.css';
import { Providers } from './providers';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { getDirection, type Locale } from '@sahool/i18n';

// Use CSS variable for font family — Tajawal loaded non-blocking via <link> in <head>
const tajawal = { variable: '--font-tajawal' };

export const metadata: Metadata = {
  title: 'سهول | SAHOOL - Smart Agriculture Platform',
  description: 'منصة سهول الزراعية الذكية - SAHOOL Smart Agricultural Platform for Yemen',
  keywords: ['سهول', 'زراعة', 'اليمن', 'sahool', 'agriculture', 'yemen', 'smart farming'],
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
      { url: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { url: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
    apple: [{ url: '/apple-touch-icon.png', sizes: '180x180' }],
  },
  manifest: '/manifest.json',
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  // Get locale from next-intl (configured in i18n.ts)
  const locale = (await getLocale().catch(() => "en")) as Locale;
  const messages = await getMessages().catch(() => ({}));
  const direction = getDirection(locale);

  return (
    <html lang={locale} dir={direction} className={`${tajawal.variable} dark`} suppressHydrationWarning>
      <head>
        {/*
          Tajawal Arabic font is self-hosted via @font-face in globals.css
          with Google Fonts CDN as fallback source. No external stylesheet
          needed — this ensures offline-first font loading.
        */}
        {/* Leaflet CSS — loaded with precedence="low" so it does not block first paint */}
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin="anonymous"
          precedence="low"
        />
      </head>
      <body className="font-tajawal bg-gray-50 dark:bg-gray-900 min-h-screen transition-colors" suppressHydrationWarning>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:start-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg focus:shadow-lg"
        >
          {direction === 'rtl' ? 'انتقل إلى المحتوى الرئيسي' : 'Skip to main content'}
        </a>
        <ErrorBoundary>
          <NextIntlClientProvider messages={messages} locale={locale}>
            <Providers><main id="main-content">{children}</main></Providers>
          </NextIntlClientProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
