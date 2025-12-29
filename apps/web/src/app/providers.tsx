'use client';

/**
 * SAHOOL App Providers
 * مزودات التطبيق
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React, { useState } from 'react';
import { AuthProvider } from '@/stores/auth.store';
import { ToastProvider } from '@/components/ui/toast';

interface ProvidersProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  children: any;
}

export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
            retry: 1, // Reduce retries for faster failure feedback (especially for E2E tests)
            retryDelay: 500, // Shorter delay between retries
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          {children}
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
