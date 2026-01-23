"use client";

/**
 * SAHOOL Admin Auth Guard
 * Component to protect routes that require authentication
 */

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/stores/auth.store";
import { Loader2, ShieldAlert, ArrowRight } from "lucide-react";
import Link from "next/link";

interface AuthGuardProps {
  children: React.ReactNode;
  requiredRole?: "admin" | "supervisor" | "viewer";
}

const roleHierarchy: Record<"admin" | "supervisor" | "viewer", number> = {
  admin: 3,
  supervisor: 2,
  viewer: 1,
};

const ROLE_NAMES: Record<"admin" | "supervisor" | "viewer", string> = {
  admin: "مدير",
  supervisor: "مشرف",
  viewer: "مشاهد",
};

export function AuthGuard({ children, requiredRole }: AuthGuardProps) {
  const { user, isLoading, isAuthenticated, checkAuth } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [showAccessDenied, setShowAccessDenied] = useState(false);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Redirect to login with return URL
      router.push(`/login?returnTo=${encodeURIComponent(pathname)}`);
    }
  }, [isLoading, isAuthenticated, router, pathname]);

  // Check role-based access
  useEffect(() => {
    if (!isLoading && isAuthenticated && user && requiredRole) {
      const userRoleLevel = roleHierarchy[user.role];
      const requiredRoleLevel = roleHierarchy[requiredRole];

      if (userRoleLevel < requiredRoleLevel) {
        // User doesn't have sufficient permissions - show access denied
        setShowAccessDenied(true);
      } else {
        setShowAccessDenied(false);
      }
    }
  }, [isLoading, isAuthenticated, user, requiredRole]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-green-600 mx-auto mb-4" />
          <p className="text-gray-600">جاري التحميل...</p>
        </div>
      </div>
    );
  }

  // Don't render children if not authenticated (redirect will happen)
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-green-600 mx-auto mb-4" />
          <p className="text-gray-600">جاري إعادة التوجيه...</p>
        </div>
      </div>
    );
  }

  // Show access denied if user doesn't have sufficient role
  if (showAccessDenied && requiredRole && user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <ShieldAlert className="w-8 h-8 text-red-500" />
          </div>

          <h2 className="text-xl font-bold text-gray-900 mb-2">
            الوصول مرفوض
          </h2>

          <p className="text-gray-600 mb-6">
            ليس لديك الصلاحيات الكافية للوصول إلى هذه الصفحة.
            <br />
            يتطلب الوصول صلاحية <span className="font-semibold text-gray-900">{ROLE_NAMES[requiredRole]}</span> أو أعلى.
          </p>

          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-500 mb-1">صلاحيتك الحالية</p>
            <p className="font-medium text-gray-900">{ROLE_NAMES[user.role]}</p>
          </div>

          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-6 py-3 bg-sahool-600 text-white rounded-lg font-medium hover:bg-sahool-700 transition-colors"
          >
            <ArrowRight className="w-5 h-5" />
            العودة للوحة التحكم
          </Link>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
