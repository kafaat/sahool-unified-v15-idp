"use client";

import Sidebar from "@/components/layout/Sidebar";
import { AuthGuard } from "@/components/auth/AuthGuard";
import Breadcrumbs from "@/components/ui/Breadcrumbs";

interface DashboardShellProps {
  children: React.ReactNode;
  requiredRole?: "admin" | "supervisor" | "viewer";
}

/**
 * Client-side dashboard shell with sidebar and auth guard.
 * Used by server-component layouts to enable metadata exports.
 */
export default function DashboardShell({
  children,
  requiredRole = "viewer",
}: DashboardShellProps) {
  return (
    <AuthGuard requiredRole={requiredRole}>
      {/* Skip to main content - accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:right-4 focus:z-50 focus:bg-sahool-600 focus:text-white focus:px-4 focus:py-2 focus:rounded-lg focus:shadow-lg"
      >
        تخطي إلى المحتوى الرئيسي
      </a>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Sidebar />
        <main
          id="main-content"
          className="ms-0 lg:ms-64 min-h-screen"
          aria-label="المحتوى الرئيسي"
        >
          <div className="px-6 pt-4">
            <Breadcrumbs className="mb-2" />
          </div>
          <div className="animate-page-enter">
            {children}
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
