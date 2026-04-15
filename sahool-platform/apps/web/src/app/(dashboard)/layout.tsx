"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/stores/auth.store";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading, hydrate, logout } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-emerald-600 font-medium animate-pulse">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="bg-emerald-700 text-white px-6 py-4 flex items-center justify-between shadow">
        <Link href="/dashboard" className="text-xl font-bold tracking-tight">
          SAHOOL
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-sm opacity-80">
            {user?.name}{" "}
            <span className="inline-block bg-emerald-500 text-white text-xs px-2 py-0.5 rounded-full capitalize ml-1">
              {user?.role}
            </span>
          </span>
          <Link href="/profile" className="text-sm hover:underline">
            Profile
          </Link>
          {user?.role === "admin" && (
            <Link href="/admin" className="text-sm hover:underline">
              Admin
            </Link>
          )}
          <button
            onClick={() => logout()}
            className="text-sm bg-emerald-600 px-3 py-1 rounded hover:bg-emerald-500 transition-colors"
          >
            Sign out
          </button>
        </div>
      </nav>

      {/* Page content */}
      <main className="flex-1 p-6 max-w-5xl mx-auto w-full">{children}</main>
    </div>
  );
}
