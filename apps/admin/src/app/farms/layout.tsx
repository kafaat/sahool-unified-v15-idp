"use client";

import Sidebar from "@/components/layout/Sidebar";
import { AuthGuard } from "@/components/auth/AuthGuard";

export default function FarmsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard requiredRole="viewer">
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <main className="mr-64 min-h-screen">{children}</main>
      </div>
    </AuthGuard>
  );
}
