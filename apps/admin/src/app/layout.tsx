import type { Metadata } from 'next';
import { headers } from 'next/headers';
import './globals.css';
import { Providers } from './providers';
import { getDirection, getLocale } from '@/lib/i18n';

// Self-hosted Tajawal font via @font-face in globals.css (no external dependency)
const tajawal = { variable: '--font-tajawal' };

export const metadata: Metadata = {
  title: 'لوحة تحكم سهول | Sahool Admin Dashboard',
  description: 'لوحة تحكم المشرفين لمنصة سهول الزراعية الذكية',
  keywords: ['سهول', 'زراعة', 'اليمن', 'sahool', 'agriculture', 'yemen'],
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { url: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
    apple: [{ url: '/icon-192.png', sizes: '192x192' }],
  },
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  // Get nonce from headers for CSP (set by middleware)
  let nonce = '';
  try {
    const headersList = await headers();
    nonce = headersList.get('X-Nonce') || '';
  } catch (error) {
    // Rare edge case: headers() may throw at build-time. Fall back gracefully.
    console.error('[RootLayout] Failed to read headers(), falling back to default locale:', error);
  }

  const locale = getLocale();
  const direction = getDirection(locale);

  return (
    // suppressHydrationWarning prevents errors from browser extensions (e.g., Dark Reader)
    // that modify DOM attributes during hydration
    <html lang={locale} dir={direction} className={tajawal.variable} suppressHydrationWarning>
      <head suppressHydrationWarning>
        {/* Leaflet CSS - loaded normally to avoid onLoad handler issues in React */}
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
          nonce={nonce}
          suppressHydrationWarning
        />
        <noscript>
          <link
            rel="stylesheet"
            href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
            integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
            crossOrigin=""
          />
        </noscript>
      </head>
      <body className="font-tajawal bg-gray-50 min-h-screen" suppressHydrationWarning>
        <Providers>
          <main id="main-content">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
