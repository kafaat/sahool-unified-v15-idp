"use client";

import Sidebar from "@/components/layout/Sidebar";
import { AuthGuard } from "@/components/auth/AuthGuard";

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
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <main
          className="mr-64 min-h-screen"
          role="main"
          aria-label="المحتوى الرئيسي"
        >
          {children}
        </main>
      </div>
    </AuthGuard>
  );
}
