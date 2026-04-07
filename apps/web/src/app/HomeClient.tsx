'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Root page redirects to the authenticated dashboard.
 * Auth check is handled by middleware on /dashboard.
 * الصفحة الرئيسية تعيد التوجيه إلى لوحة التحكم المحمية.
 */
export default function HomeClient() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/dashboard');
  }, [router]);

  return (
    <main id="main-content" className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
        <p className="text-sm text-gray-500">جاري التحويل... | Redirecting...</p>
      </div>
    </main>
  );
}
