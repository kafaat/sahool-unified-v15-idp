"use client";
import * as React from "react";
import { QueryClient } from "@tanstack/query-core";
import { QueryClientProvider } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layouts/sidebar";
import { Header } from "@/components/layouts/header";
import { useAuth } from "@/stores/auth.store";
import { Loading } from "@/components/ui/loading";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";

/**
 * QueryClientProvider is scoped to the dashboard route group so that auth
 * pages (login, register, forgot-password, etc.) do not pay the cost of
 * loading @tanstack/react-query in their initial bundle.
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAuthenticated, isLoading, checkAuth } = useAuth();
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = React.useState(false);

  const [queryClient] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute - data considered fresh
            gcTime: 5 * 60 * 1000, // 5 minutes - garbage collect inactive queries
            refetchOnWindowFocus: false, // Reduce bandwidth in low-connectivity areas
            refetchOnReconnect: true, // Re-fetch when connection restored (offline-first)
            retry: 1, // Single retry for failed queries (low-bandwidth friendly)
          },
        },
      }),
  );

  React.useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  React.useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
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
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden transition-colors">
        <ErrorBoundary
          fallback={
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg m-4">
              <p className="text-red-700 text-sm">فشل تحميل القائمة الجانبية</p>
            </div>
          }
        >
          <Sidebar
            isOpen={isMobileSidebarOpen}
            onClose={() => setIsMobileSidebarOpen(false)}
          />
        </ErrorBoundary>
        <div className="flex-1 flex flex-col overflow-hidden">
          <ErrorBoundary
            fallback={
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg m-4">
                <p className="text-red-700 text-sm">فشل تحميل رأس الصفحة</p>
              </div>
            }
          >
            <Header onMenuToggle={() => setIsMobileSidebarOpen(prev => !prev)} />
          </ErrorBoundary>
          <main id="main-content" className="flex-1 overflow-y-auto p-6">
            <ErrorBoundary>{children}</ErrorBoundary>
          </main>
        </div>
      </div>
    </QueryClientProvider>
  );
}
