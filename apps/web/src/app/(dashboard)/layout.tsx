'use client';
import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/layouts/sidebar';
import { Header } from '@/components/layouts/header';
import { useAuth } from '@/stores/auth.store';
import { Loading } from '@/components/ui/loading';

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
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
