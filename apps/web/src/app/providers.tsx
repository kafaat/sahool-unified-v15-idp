"use client";

/**
 * SAHOOL App Providers (Root)
 * مزودات التطبيق الأساسية
 *
 * Only includes providers needed by ALL pages (including auth).
 * QueryClientProvider is loaded in the (dashboard) layout to keep
 * auth pages (~react-query free) for a smaller initial bundle.
 */

import { AuthProvider } from "@/stores/auth.store";
import { ToastProvider } from "@/components/ui/toast";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <ToastProvider>{children}</ToastProvider>
    </AuthProvider>
  );
}
