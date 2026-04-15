'use client';

/**
 * SAHOOL App Providers (Root)
 * مزودات التطبيق الأساسية
 *
 * Only includes providers needed by ALL pages (including auth).
 * QueryClientProvider is loaded in the (dashboard) layout to keep
 * auth pages (~react-query free) for a smaller initial bundle.
 */

import { useEffect } from 'react';
import { AuthProvider } from '@/stores/auth.store';
import { ToastProvider } from '@/components/ui/toast';
import { ThemeProvider } from '@/stores/theme.store';
import { initializeErrorTracking } from '@/lib/monitoring/error-tracking';
import { OfflineIndicator } from '@/components/pwa/ServiceWorkerRegistration';

function ErrorTrackingInitializer() {
  useEffect(() => {
    // Gap #23: initializeErrorTracking() was never called — wire it up once on mount
    initializeErrorTracking();
  }, []);
  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          {/* Gap #23: global error tracking initialization */}
          <ErrorTrackingInitializer />
          {/* Gap #24: OfflineIndicator lets users know when connectivity is lost */}
          <OfflineIndicator />
          {children}
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
