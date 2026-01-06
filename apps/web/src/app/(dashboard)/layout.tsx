'use client';
import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/layouts/sidebar';
import { Header } from '@/components/layouts/header';
import { useAuth } from '@/stores/auth.store';
import { Loading } from '@/components/ui/loading';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading, checkAuth } = useAuth();

  React.useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  React.useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" textAr="جاري التحميل..." text="Loading..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <ErrorBoundary
        fallback={
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg m-4">
            <p className="text-red-700 text-sm">فشل تحميل القائمة الجانبية</p>
          </div>
        }
      >
        <Sidebar />
      </ErrorBoundary>
      <div className="flex-1 flex flex-col overflow-hidden">
        <ErrorBoundary
          fallback={
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg m-4">
              <p className="text-red-700 text-sm">فشل تحميل رأس الصفحة</p>
            </div>
          }
        >
          <Header />
        </ErrorBoundary>
        <main id="main-content" className="flex-1 overflow-y-auto p-6">
          <ErrorBoundary>{children}</ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
