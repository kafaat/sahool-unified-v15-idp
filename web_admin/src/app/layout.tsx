import type { Metadata } from 'next';
import { Tajawal } from 'next/font/google';
import './globals.css';

const tajawal = Tajawal({
  subsets: ['arabic', 'latin'],
  weight: ['400', '500', '700'],
  variable: '--font-tajawal',
});

export const metadata: Metadata = {
  title: 'لوحة تحكم سهول | Sahool Admin Dashboard',
  description: 'لوحة تحكم المشرفين لمنصة سهول الزراعية الذكية',
  keywords: ['سهول', 'زراعة', 'اليمن', 'sahool', 'agriculture', 'yemen'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl" className={tajawal.variable}>
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
        />
      </head>
      <body className={`${tajawal.className} bg-gray-50 min-h-screen`}>
        {children}
      </body>
    </html>
  );
}
