import { Metadata } from 'next';
import { Suspense } from 'react';
import LoginClient from './LoginClient';

// Force dynamic rendering since this page uses next-intl which requires headers
export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'Login | SAHOOL - Smart Agriculture Platform',
  description: 'تسجيل الدخول إلى منصة سهول الزراعية - Login to SAHOOL Smart Agricultural Platform',
  keywords: ['login', 'تسجيل الدخول', 'sahool', 'agriculture'],
  openGraph: {
    title: 'Login | SAHOOL',
    description: 'Login to SAHOOL Smart Agricultural Platform',
    type: 'website',
  },
};

export default function LoginPage() {
  // LoginClient uses useSearchParams() which requires a Suspense boundary in Next.js 15
  return (
    <Suspense fallback={null}>
      <LoginClient />
    </Suspense>
  );
}
