"use client";

/**
 * SAHOOL App Providers
 * مزودات التطبيق
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { AuthProvider } from "@/stores/auth.store";
import { ToastProvider } from "@/components/ui/toast";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
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

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>{children}</ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
